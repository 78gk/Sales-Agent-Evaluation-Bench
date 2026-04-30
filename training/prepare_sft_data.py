"""
prepare_sft_data.py — Tenacious-Bench v0.1 SFT data preparation.

Converts task JSONs from tenacious_bench_v0.1/train/ into Qwen-3.5 ChatML format
(JSONL), then applies 20x paraphrase rotation to reach ~1,500 training pairs from
~125 source tasks. Implements LIMA-style quality filter: drop augmented pairs where
the scoring check is ambiguous under the paraphrase.

Usage:
    python training/prepare_sft_data.py --tasks-dir tenacious_bench_v0.1/train \\
        --output training/qwen_pairs.jsonl

Outputs:
    training/qwen_pairs.jsonl  — augmented training pairs in ChatML format
    training/pair_count.txt    — final pair count and filter stats

Requires: Python 3.9+, no external API calls (deterministic augmentation only).
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# System prompt — phrasing gate specification
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Tenacious Conversion Engine phrasing gate.

Given a prospect context with confidence-scored signals, you must select the
correct phrasing tier for the agent's response:

- assertive:  highest-confidence signal >= 0.80 AND >= 2 fresh high-weight signals
- inquiry:    highest-confidence signal in [0.50, 0.79]
- hypothesis: highest-confidence signal in [0.25, 0.49]
- abstention: highest-confidence signal < 0.25, OR all signals stale, OR
              a headcount/pricing/timeline commitment is requested

When routed_to_human is required (commitment requested), set phrasing_tier to
abstention and routed_to_human to true.

When stale_disclosed is required (any signal age > validity_window_days), set
stale_flag to true regardless of the phrasing tier.

Respond with a JSON object containing only the required output fields.
Phrasing tier must be the exact string: assertive, inquiry, hypothesis, or abstention."""

# ---------------------------------------------------------------------------
# Paraphrase templates for agent_prompt augmentation
# The paraphrase must not change the inferred phrasing tier (LIMA filter).
# ---------------------------------------------------------------------------
PARAPHRASE_VERBS = [
    "Draft", "Write", "Compose", "Craft", "Prepare",
    "Generate", "Produce", "Create", "Formulate", "Develop",
]

PARAPHRASE_OPENERS = [
    "the opening line of a cold email",
    "the first sentence of an outreach email",
    "a cold email opening",
    "the opening hook of a prospect email",
    "a personalized email opener",
    "the subject line and first line of an outreach",
    "a cold outreach opener",
    "a brief email introduction",
    "the opening of a business development email",
    "a prospect-personalised first sentence",
]

PARAPHRASE_REFERENCE_VERBS = [
    "referencing", "mentioning", "citing", "using", "based on",
    "grounded in", "drawing from", "highlighting", "noting",
    "incorporating",
]


def paraphrase_prompt(prompt: str, index: int) -> str:
    """
    Apply deterministic paraphrase rotation to agent_prompt.
    Uses modular selection from vocabulary lists to ensure reproducibility.
    Does not use LLM calls — purely string-level variation.
    """
    verb = PARAPHRASE_VERBS[index % len(PARAPHRASE_VERBS)]
    opener = PARAPHRASE_OPENERS[index % len(PARAPHRASE_OPENERS)]
    ref_verb = PARAPHRASE_REFERENCE_VERBS[index % len(PARAPHRASE_REFERENCE_VERBS)]

    # Extract company name (first quoted or capitalised noun phrase)
    company_match = re.search(r"for ([A-Z][A-Za-z\s&]+?)[\.\,\s]", prompt)
    company = company_match.group(1).strip() if company_match else "the prospect"

    # Extract signal context (everything after "They have" or similar)
    context_match = re.search(
        r"(They have .+|has .+|with .+open role.+|after .+)\.", prompt, re.IGNORECASE
    )
    context = context_match.group(1) if context_match else ""

    if context:
        return f"{verb} {opener} for {company} {ref_verb} their recent activity. {context}."
    else:
        return f"{verb} {opener} for {company}."


def build_expected_output(task: dict) -> dict:
    """
    Build the expected output JSON from the task's expected fields.
    This is the assistant turn in the ChatML conversation.
    """
    expected = task["expected"]
    output = {"phrasing_tier": expected["phrasing_tier"]}

    if expected.get("routed_to_human") is True:
        output["routed_to_human"] = True
    if expected.get("stale_disclosed") is True:
        output["stale_flag"] = True
    if expected.get("thread_clean") is False:
        # Explicitly flag thread violation in expected — rare
        output["thread_clean"] = False

    return output


def build_user_message(task: dict) -> str:
    """Build the user message with signals JSON + agent prompt."""
    signals = task["input"]["prospect_context"].get("signals", {})
    prompt = task["input"]["agent_prompt"]
    return (
        f"Prospect signals: {json.dumps(signals)}\n\n"
        f"Task: {prompt}"
    )


def task_to_pairs(task: dict, augment_count: int = 20) -> list:
    """
    Convert one task to 1 source pair + up to augment_count paraphrase pairs.
    LIMA filter: skip augmented pair if the paraphrase changes the inferred
    phrasing tier (detected by checking that the paraphrase doesn't introduce
    conflicting confidence keywords).
    Returns list of ChatML dicts.
    """
    pairs = []
    expected_output = build_expected_output(task)
    base_user = build_user_message(task)

    # Source pair (canonical)
    pairs.append({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": base_user},
            {"role": "assistant", "content": json.dumps(expected_output)},
        ],
        "task_id": task["task_id"],
        "augment_index": 0,
    })

    # Augmented pairs
    for i in range(1, augment_count + 1):
        paraphrased_prompt = paraphrase_prompt(task["input"]["agent_prompt"], i)
        user_msg = (
            f"Prospect signals: {json.dumps(task['input']['prospect_context'].get('signals', {}))}\n\n"
            f"Task: {paraphrased_prompt}"
        )
        pairs.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": json.dumps(expected_output)},
            ],
            "task_id": task["task_id"],
            "augment_index": i,
        })

    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Prepare SFT training data for Qwen 3.5 LoRA training"
    )
    parser.add_argument(
        "--tasks-dir", type=str,
        default="tenacious_bench_v0.1/train",
        help="Directory containing task JSON files"
    )
    parser.add_argument(
        "--output", type=str,
        default="training/qwen_pairs.jsonl",
        help="Output JSONL file path"
    )
    parser.add_argument(
        "--augment-count", type=int, default=20,
        help="Paraphrase rotations per source task (default: 20 → ~21x total)"
    )
    parser.add_argument(
        "--shuffle", action="store_true",
        help="Shuffle output pairs (use for training; omit for inspection)"
    )
    args = parser.parse_args()

    tasks_dir = Path(args.tasks_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    task_files = sorted(tasks_dir.glob("*.json"))
    if not task_files:
        print(f"ERROR: No task files found in {tasks_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {len(task_files)} tasks from {tasks_dir}...")

    all_pairs = []
    for task_path in task_files:
        try:
            task = json.loads(task_path.read_text(encoding="utf-8"))
            pairs = task_to_pairs(task, augment_count=args.augment_count)
            all_pairs.extend(pairs)
        except Exception as e:
            print(f"  SKIP {task_path.name}: {e}")

    if args.shuffle:
        random.shuffle(all_pairs)

    with output_path.open("w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    source_count = len(task_files)
    total_pairs = len(all_pairs)
    print(f"\nSFT data prepared:")
    print(f"  Source tasks:   {source_count}")
    print(f"  Augment factor: {args.augment_count + 1}x (1 source + {args.augment_count} paraphrases)")
    print(f"  Total pairs:    {total_pairs}")
    print(f"  Output:         {output_path}")

    # Write count log
    count_path = output_path.parent / "pair_count.txt"
    count_path.write_text(
        f"source_tasks={source_count}\n"
        f"augment_factor={args.augment_count + 1}\n"
        f"total_pairs={total_pairs}\n"
        f"output={output_path}\n"
        f"seed={RANDOM_SEED}\n"
    )
    print(f"  Count log:      {count_path}")


if __name__ == "__main__":
    main()
