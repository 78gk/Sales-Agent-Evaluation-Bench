"""
synthesis_generator.py — Tenacious-Bench v0.1 multi-LLM synthesis pipeline.

Generates, judges, and deduplicates tasks via OpenRouter using the routing policy
documented in generation_scripts/routing_policy.md.

Usage:
    python generation_scripts/synthesis_generator.py --count 10
    python generation_scripts/synthesis_generator.py --dry-run  # print config, no API calls

Requires:
    OPENROUTER_API_KEY environment variable
    pip install openai
"""

import json
import os
import pathlib
import random
import sys
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Reproducibility — pin across all generation scripts
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Model tiers — R3-G: cheap-model vs eval-tier differentiation
# ---------------------------------------------------------------------------
CHEAP_MODELS = [
    "qwen/qwen3-80b",              # bulk synthesis generator (dev tier)
    "openai/gpt-4.1-mini",         # trace-derived task adaptation
    "deepseek/deepseek-chat-v3-2", # synthesis judge (dev tier)
]

EVAL_TIER_MODELS = [
    "anthropic/claude-sonnet-4-6", # held_out calibration only, Days 4-5, ≤4 passes
]

# Routing table: generator != judge enforced per task type
ROUTING = {
    "synthesis": {
        "generator": "qwen/qwen3-80b",
        "judge":     "deepseek/deepseek-chat-v3-2",
    },
    "trace_derived": {
        "generator": "openai/gpt-4.1-mini",
        "judge":     "qwen/qwen3-80b",
    },
    "calibration": {     # held_out calibration slice, eval-tier judge only
        "generator": None,
        "judge":     "anthropic/claude-sonnet-4-6",
    },
}

# ---------------------------------------------------------------------------
# Judge filter thresholds — R3-D, R3-E: named constants
# ---------------------------------------------------------------------------
COHERENCE_THRESHOLD     = 3.5   # prospect context logically supports expected tier
VERIFIABILITY_THRESHOLD = 3.5   # all expected fields machine-checkable
RUBRIC_CLARITY_THRESHOLD = 3.5  # correct tier unambiguous from signals
AGGREGATE_THRESHOLD     = 3.5   # mean(coherence, verifiability, rubric_clarity)

# ---------------------------------------------------------------------------
# Deduplication constants
# ---------------------------------------------------------------------------
NGRAM_N = 8
EMBED_SIMILARITY_THRESHOLD = 0.85

JUDGE_PROMPT_PATH = pathlib.Path(__file__).parent / "judge_prompt.txt"
DEFAULT_OUTPUT_DIR = pathlib.Path("tenacious_bench_v0.1/train")


# ---------------------------------------------------------------------------
# Preference leakage prevention — R3-C
# ---------------------------------------------------------------------------
def assert_no_leakage(generator_model: str, judge_model: str, task_id: str) -> None:
    """Raises ValueError if generator and judge are the same model."""
    if generator_model == judge_model:
        raise ValueError(
            f"Preference leakage: generator and judge are both '{generator_model}' "
            f"for task {task_id}. Rotate the judge model before continuing."
        )


# ---------------------------------------------------------------------------
# Judge prompt loading — R3-H: standalone file, not embedded in code
# ---------------------------------------------------------------------------
def load_judge_prompt() -> str:
    """Load judge prompt from standalone file."""
    if not JUDGE_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Judge prompt not found at {JUDGE_PROMPT_PATH}")
    return JUDGE_PROMPT_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------------------------
def get_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY environment variable is not set."
        )
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


# ---------------------------------------------------------------------------
# Judge filter — R3-D: 3 dimensions; R3-E: thresholds as named constants
# ---------------------------------------------------------------------------
def run_judge(task: dict, judge_model: str, client: Any) -> dict:
    """
    Score a candidate task on 3 dimensions.
    Returns dict: {coherence, verifiability, rubric_clarity, mean, pass, notes}.
    """
    judge_prompt = load_judge_prompt()
    filled = judge_prompt.replace("{{task_json}}", json.dumps(task, indent=2))

    response = client.chat.completions.create(
        model=judge_model,
        messages=[{"role": "user", "content": filled}],
        temperature=0.0,
        seed=RANDOM_SEED,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def passes_judge_filter(scores: dict) -> bool:
    """
    Returns True iff coherence, verifiability, rubric_clarity all meet their
    individual thresholds AND the aggregate mean meets AGGREGATE_THRESHOLD.
    """
    return (
        scores.get("coherence", 0)      >= COHERENCE_THRESHOLD
        and scores.get("verifiability", 0) >= VERIFIABILITY_THRESHOLD
        and scores.get("rubric_clarity", 0) >= RUBRIC_CLARITY_THRESHOLD
        and scores.get("mean", 0)         >= AGGREGATE_THRESHOLD
    )


# ---------------------------------------------------------------------------
# Deduplication — R3-F: pairwise n-gram check
# ---------------------------------------------------------------------------
def ngrams(text: str, n: int) -> set:
    words = text.lower().split()
    return {tuple(words[i: i + n]) for i in range(len(words) - n + 1)}


def dedup_check_ngram(new_task: dict, corpus_dir: pathlib.Path) -> bool:
    """Returns True if new_task has no 8-gram overlap with any task in corpus_dir."""
    new_grams = ngrams(new_task["input"]["agent_prompt"], NGRAM_N)
    for existing_file in sorted(corpus_dir.glob("*.json")):
        existing = json.loads(existing_file.read_text(encoding="utf-8"))
        existing_grams = ngrams(existing["input"]["agent_prompt"], NGRAM_N)
        if new_grams & existing_grams:
            return False
    return True


# ---------------------------------------------------------------------------
# Task generation
# ---------------------------------------------------------------------------
def generate_synthesis_task(
    task_type: str,
    category: str,
    client: Any,
    task_id: str,
) -> dict:
    """Generate a candidate synthesis task via the generator model."""
    route = ROUTING[task_type]
    generator_model = route["generator"]
    judge_model = route["judge"]
    assert_no_leakage(generator_model, judge_model, task_id)  # leakage guard

    generation_prompt = (
        f"Generate a Tenacious-Bench v0.1 evaluation task for the '{category}' failure "
        "category. Include: prospect_context with at least one signal (conf value, "
        "age_days, validity_window_days), agent_prompt, expected fields (phrasing_tier, "
        "routed_to_human, stale_disclosed, thread_clean), and scoring dimensions. "
        "Return JSON only, matching the Tenacious-Bench v0.1 schema."
    )

    response = client.chat.completions.create(
        model=generator_model,
        messages=[{"role": "user", "content": generation_prompt}],
        temperature=0.7,
        seed=RANDOM_SEED,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    task = json.loads(raw)
    task["task_id"]    = task_id
    task["version"]    = "v0.1"
    task["category"]   = category
    task["source_mode"] = "synthesis"
    task["metadata"] = {
        "authored_by":      f"{generator_model} (generated) / {judge_model} (judged)",
        "authored_date":    "2026-04-30",
        "generator_model":  generator_model,
        "judge_model":      judge_model,
    }
    return task


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_pipeline(
    count: int,
    output_dir: pathlib.Path,
    category: str = "signal_over_claiming",
    task_id_start: int = 256,
    dry_run: bool = False,
) -> list:
    """
    Generate → judge → dedup → write.
    Returns list of admitted task IDs.
    """
    if dry_run:
        print("=== DRY RUN — routing config ===")
        for task_type, route in ROUTING.items():
            print(f"  {task_type}: generator={route['generator']}, judge={route['judge']}")
        print(f"\n  Judge thresholds:")
        print(f"    coherence      >= {COHERENCE_THRESHOLD}")
        print(f"    verifiability  >= {VERIFIABILITY_THRESHOLD}")
        print(f"    rubric_clarity >= {RUBRIC_CLARITY_THRESHOLD}")
        print(f"    aggregate mean >= {AGGREGATE_THRESHOLD}")
        print(f"\n  RANDOM_SEED      = {RANDOM_SEED}")
        print(f"  CHEAP_MODELS     = {CHEAP_MODELS}")
        print(f"  EVAL_TIER_MODELS = {EVAL_TIER_MODELS}")
        return []

    client = get_client()
    output_dir.mkdir(parents=True, exist_ok=True)
    admitted = []
    task_counter = task_id_start

    for _ in range(count * 3):  # overshoot to account for filter failures
        if len(admitted) >= count:
            break

        task_id = f"TB-{task_counter:04d}"
        try:
            task = generate_synthesis_task("synthesis", category, client, task_id)
        except Exception as e:
            print(f"  SKIP {task_id}: generation error — {e}")
            task_counter += 1
            continue

        try:
            judge_model = ROUTING["synthesis"]["judge"]
            scores = run_judge(task, judge_model, client)
        except Exception as e:
            print(f"  SKIP {task_id}: judge error — {e}")
            task_counter += 1
            continue

        if not passes_judge_filter(scores):
            print(f"  SKIP {task_id}: filter FAIL "
                  f"(mean={scores.get('mean', 0):.2f} < {AGGREGATE_THRESHOLD})")
            task_counter += 1
            continue

        if not dedup_check_ngram(task, output_dir):
            print(f"  SKIP {task_id}: n-gram overlap — rewrite required")
            task_counter += 1
            continue

        out_path = output_dir / f"{task_id}.json"
        out_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
        admitted.append(task_id)
        print(f"  ADMIT {task_id}: mean={scores.get('mean', 0):.2f} "
              f"(c={scores.get('coherence')}, v={scores.get('verifiability')}, "
              f"r={scores.get('rubric_clarity')})")
        task_counter += 1

    print(f"\nPipeline complete: {len(admitted)}/{count} tasks admitted.")
    return admitted


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Tenacious-Bench v0.1 multi-LLM synthesis pipeline"
    )
    parser.add_argument("--count", type=int, default=10,
                        help="Number of tasks to generate (default: 10)")
    parser.add_argument("--output-dir", type=str,
                        default=str(DEFAULT_OUTPUT_DIR),
                        help="Output directory for task JSON files")
    parser.add_argument("--category", type=str, default="signal_over_claiming",
                        help="Failure category for generated tasks")
    parser.add_argument("--task-id-start", type=int, default=256,
                        help="Starting task ID number (default: 256)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print routing config and exit without API calls")
    args = parser.parse_args()

    run_pipeline(
        count=args.count,
        output_dir=pathlib.Path(args.output_dir),
        category=args.category,
        task_id_start=args.task_id_start,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
