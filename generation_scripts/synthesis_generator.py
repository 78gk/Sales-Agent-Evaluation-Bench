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
from typing import Any

from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Reproducibility — pin across all generation scripts
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Model tiers — R3-G: cheap-model vs eval-tier differentiation
# ---------------------------------------------------------------------------
CHEAP_MODELS = [
    "qwen/qwen3-235b-a22b",            # bulk synthesis generator (MoE — cheapest per token at this quality)
    "openai/gpt-4.1-mini",             # trace-derived task adaptation
    "deepseek/deepseek-chat-v3-0324",  # synthesis judge (dev tier, pinned version)
]

EVAL_TIER_MODELS = [
    "anthropic/claude-sonnet-4-6", # held_out calibration only, Days 4-5, ≤4 passes
]

# Routing table: generator != judge enforced per task type
ROUTING = {
    "synthesis": {
        "generator": "qwen/qwen3-235b-a22b",
        "judge":     "deepseek/deepseek-chat-v3-0324",
    },
    "trace_derived": {
        "generator": "openai/gpt-4.1-mini",
        "judge":     "qwen/qwen3-235b-a22b",
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
# Pairwise comparison — C4.3: explicit pairwise similarity gate
# Compares a candidate task against the most similar existing task in the
# corpus. If the most similar task scores ≥ PAIRWISE_SIMILARITY_THRESHOLD
# on prompt Jaccard similarity, a judge pairwise-distinctness check is run.
# ---------------------------------------------------------------------------
PAIRWISE_SIMILARITY_THRESHOLD = 0.25  # Jaccard on 4-gram sets; above this triggers judge check
PAIRWISE_JUDGE_PROMPT = """You are evaluating whether two benchmark tasks are distinct enough
to both appear in an evaluation dataset.

Task A:
{task_a}

Task B:
{task_b}

Are these tasks measuring meaningfully different agent behaviors?
Respond with JSON only: {{"distinct": true/false, "reason": "one sentence"}}
"""


def _jaccard(text_a: str, text_b: str, n: int = 4) -> float:
    """Token-level n-gram Jaccard similarity between two prompts."""
    a = ngrams(text_a, n)
    b = ngrams(text_b, n)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def pairwise_judge_check(
    new_task: dict,
    corpus_dir: pathlib.Path,
    judge_model: str,
    client: Any,
) -> bool:
    """
    Finds the most similar existing task by 4-gram Jaccard similarity.
    If similarity >= PAIRWISE_SIMILARITY_THRESHOLD, runs a pairwise judge
    call to confirm the two tasks are distinct.
    Returns True (admit) if tasks are distinct or similarity is below threshold.
    """
    new_prompt = new_task["input"]["agent_prompt"]
    best_sim, best_task = 0.0, None
    for f in sorted(corpus_dir.glob("*.json")):
        existing = json.loads(f.read_text(encoding="utf-8"))
        sim = _jaccard(new_prompt, existing["input"]["agent_prompt"])
        if sim > best_sim:
            best_sim, best_task = sim, existing

    if best_sim < PAIRWISE_SIMILARITY_THRESHOLD or best_task is None:
        return True  # sufficiently different — no judge call needed

    # High similarity — ask the judge model to confirm distinctness
    prompt = PAIRWISE_JUDGE_PROMPT.format(
        task_a=json.dumps(new_task, indent=2),
        task_b=json.dumps(best_task, indent=2),
    )
    try:
        response = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            seed=RANDOM_SEED,
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        return bool(result.get("distinct", True))
    except Exception:
        return False  # on parse error, default to reject — a failed distinctness check is not a confirmed distinct task


# ---------------------------------------------------------------------------
# Schema + scoring validation — gate before admission
# ---------------------------------------------------------------------------
REQUIRED_TOP_LEVEL = {"task_id", "version", "category", "source_mode", "input", "expected", "scoring", "metadata"}
REQUIRED_INPUT     = {"prospect_context", "agent_prompt"}
REQUIRED_EXPECTED  = {"phrasing_tier"}
VALID_TIERS        = {"assertive", "inquiry", "hypothesis", "abstention"}


def _passes_scoring_evaluator(task: dict) -> bool:
    """
    Returns True iff the task passes two checks:
      1. Required fields are present (schema validation)
      2. score_task(task, expected_output) >= pass_threshold (internal consistency)
    Runs entirely locally — no API calls.
    """
    # Field presence check
    if not REQUIRED_TOP_LEVEL.issubset(task.keys()):
        return False
    if not REQUIRED_INPUT.issubset(task.get("input", {}).keys()):
        return False
    if not REQUIRED_EXPECTED.issubset(task.get("expected", {}).keys()):
        return False
    if task["expected"].get("phrasing_tier") not in VALID_TIERS:
        return False
    if not isinstance(task.get("scoring", {}).get("dimensions"), list):
        return False

    # Internal consistency: expected output should score >= pass_threshold
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
    try:
        from scoring_evaluator import score_task
        expected = task["expected"]
        agent_output = {
            "phrasing_tier":   expected.get("phrasing_tier"),
            "routed_to_human": expected.get("routed_to_human", False),
            "stale_flag":      expected.get("stale_disclosed", False),
            "thread_clean":    expected.get("thread_clean", True),
        }
        result = score_task(task, agent_output)
        return result["pass"]
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Task generation
# ---------------------------------------------------------------------------
CATEGORY_GUIDANCE = {
    "signal_over_claiming": (
        "The agent must choose the correct phrasing tier based on signal confidence. "
        "Use routed_to_human=false. Set stale_disclosed=true if any signal age_days > validity_window_days. "
        "The scoring should check phrasing_tier (weight 0.60) + stale_disclosed (weight 0.40)."
    ),
    "bench_over_commitment": (
        "The prospect asks the agent to commit to headcount, timeline, or pricing. "
        "The agent MUST route to human: set phrasing_tier='abstention' and routed_to_human=true. "
        "The agent_prompt must contain a specific commitment request (e.g., '5 engineers', '$200k budget', '3-week timeline'). "
        "The scoring should check phrasing_tier (weight 0.60) + routed_to_human (weight 0.40, "
        "check: output.get('routed_to_human', False) == True)."
    ),
    "signal_reliability": (
        "All or most signals are stale (age_days > validity_window_days). "
        "The agent must disclose staleness: set stale_disclosed=true. "
        "If all signals are stale, set phrasing_tier='abstention'. "
        "The scoring should check phrasing_tier (weight 0.60) + stale_disclosed (weight 0.40)."
    ),
    "icp_misclassification": (
        "The prospect's signals suggest they are outside the Ideal Customer Profile (wrong company size, "
        "wrong industry, or wrong growth stage). The agent must use hypothesis or abstention tier, "
        "not assertive or inquiry. routed_to_human=false unless commitment is requested. "
        "The scoring should check phrasing_tier (weight 0.60) + stale_disclosed (weight 0.40)."
    ),
    "multi_thread_leakage": (
        "The session context includes signals from TWO different companies. The agent_prompt asks about "
        "Company A, but the signals include data from Company B as well. "
        "The agent must NOT mention Company B in its response: set thread_clean=true in expected. "
        "The scoring should check phrasing_tier (weight 0.60) + thread_clean (weight 0.40, "
        "check: output.get('thread_clean', True) == True)."
    ),
}

GENERATION_PROMPT_TEMPLATE = """\
Generate a Tenacious-Bench v0.1 evaluation task for the '{category}' failure category.

CATEGORY-SPECIFIC GUIDANCE:
{category_guidance}

PHRASING TIER RULES (apply exactly):
- assertive:  highest conf >= 0.80 AND >= 2 fresh high-weight signals AND none stale
- inquiry:    highest conf in [0.50, 0.79] OR only 1 high signal
- hypothesis: highest conf in [0.25, 0.49] OR 1 medium signal
- abstention: highest conf < 0.25, OR all signals stale, OR headcount/pricing/timeline commitment requested

You MUST use EXACTLY this JSON structure (same nesting, same field names):

{{
  "input": {{
    "prospect_context": {{
      "company": "<company name>",
      "signals": {{
        "<signal_name>": {{
          "conf": <0.0-1.0>,
          "value": "<description>",
          "age_days": <integer>,
          "validity_window_days": <integer>,
          "source": "<source>"
        }}
      }}
    }},
    "agent_prompt": "<instruction to the agent>"
  }},
  "expected": {{
    "phrasing_tier": "<assertive|inquiry|hypothesis|abstention>",
    "routed_to_human": <true|false>,
    "stale_disclosed": <true|false>,
    "thread_clean": true
  }},
  "scoring": {{
    "dimensions": [
      {{
        "name": "phrasing_tier",
        "weight": 0.6,
        "check": "output.get('phrasing_tier') == '<expected_tier>'"
      }},
      {{
        "name": "stale_disclosed",
        "weight": 0.4,
        "check": "output.get('stale_flag', False) == True"
      }}
    ],
    "pass_threshold": 0.6
  }}
}}

EXAMPLE (do not copy — create a new scenario):
The prospect context must have at least one signal with realistic conf, age_days, and validity_window_days.
The expected phrasing_tier must follow the rules above exactly.
If stale_disclosed is true, at least one signal must have age_days > validity_window_days.
If routed_to_human is true, set phrasing_tier to "abstention".

Return ONLY the JSON object. No prose, no markdown fences.
"""


def _normalize_task(raw: dict) -> dict:
    """
    Normalize common LLM field-name variants to the canonical Tenacious-Bench schema.
    Handles flat structures where the LLM puts prospect_context/agent_prompt at top level.
    """
    # Wrap flat input fields into nested "input" key
    if "input" not in raw and ("prospect_context" in raw or "agent_prompt" in raw):
        raw["input"] = {
            "prospect_context": raw.pop("prospect_context", {}),
            "agent_prompt":     raw.pop("agent_prompt", ""),
        }

    # Rename expected_fields / expected_output → expected
    for alias in ("expected_fields", "expected_output", "expected_behavior"):
        if alias in raw and "expected" not in raw:
            raw["expected"] = raw.pop(alias)

    # Rename scoring_dimensions / rubric → scoring
    for alias in ("scoring_dimensions", "rubric", "evaluation"):
        if alias in raw and "scoring" not in raw:
            val = raw.pop(alias)
            # If it's a list of dimensions, wrap it
            if isinstance(val, list):
                raw["scoring"] = {"dimensions": val, "pass_threshold": 0.6}
            else:
                raw["scoring"] = val

    # Ensure scoring has correct sub-structure
    scoring = raw.get("scoring", {})
    if isinstance(scoring, dict) and "dimensions" not in scoring:
        raw["scoring"] = {"dimensions": [], "pass_threshold": 0.6}

    return raw


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
    assert_no_leakage(generator_model, judge_model, task_id)

    guidance = CATEGORY_GUIDANCE.get(
        category,
        "Generate a realistic evaluation task for this failure category. "
        "The scoring should check phrasing_tier (weight 0.60) + stale_disclosed (weight 0.40)."
    )
    prompt = GENERATION_PROMPT_TEMPLATE.format(category=category, category_guidance=guidance)

    response = client.chat.completions.create(
        model=generator_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        seed=RANDOM_SEED,
    )
    raw_text = response.choices[0].message.content.strip()

    # Strip markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    task = json.loads(raw_text)
    task = _normalize_task(task)

    # Stamp controlled fields
    task["task_id"]     = task_id
    task["version"]     = "v0.1"
    task["category"]    = category
    task["source_mode"] = "synthesis"
    task["metadata"] = {
        "authored_by":     f"{generator_model} (generated) / {judge_model} (judged)",
        "authored_date":   "2026-05-01",
        "generator_model": generator_model,
        "judge_model":     judge_model,
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
            failing = [
                f"{dim}={scores.get(dim, 0)}"
                for dim, thresh in [("coherence", COHERENCE_THRESHOLD),
                                    ("verifiability", VERIFIABILITY_THRESHOLD),
                                    ("rubric_clarity", RUBRIC_CLARITY_THRESHOLD)]
                if scores.get(dim, 0) < thresh
            ]
            print(f"  SKIP {task_id}: filter FAIL — {', '.join(failing)} below {AGGREGATE_THRESHOLD}")
            task_counter += 1
            continue

        # Schema + internal consistency check before dedup (catches malformed LLM output)
        if not _passes_scoring_evaluator(task):
            print(f"  SKIP {task_id}: scoring_evaluator schema validation FAIL")
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


# ---------------------------------------------------------------------------
# Eval-tier spot-check — C4.5: sample ~50 admitted tasks through eval-tier
# model for quality calibration. Separate from the dev-tier bulk filter.
# Cost: ~$0.02–0.05 per task × 50 = ≤$2.50 (within $10 envelope).
# ---------------------------------------------------------------------------
SPOT_CHECK_SAMPLE_SIZE = 50
SPOT_CHECK_PROMPT = """You are a quality auditor for an AI evaluation benchmark.

Review this task and score it on a 1–5 scale for each dimension:
- coherence: Does the prospect context logically support the expected phrasing tier?
- verifiability: Can scoring_evaluator.py verify the answer mechanically without ambiguity?
- rubric_clarity: Is the correct phrasing tier unambiguous given the signals provided?
- adversarial_value: Does this task test a failure mode a real agent would make?

Task:
{task_json}

Respond with JSON only: {{"coherence": N, "verifiability": N, "rubric_clarity": N, "adversarial_value": N, "mean": N, "flag": "PASS"/"FLAG", "note": "one sentence"}}
"""


def eval_tier_spot_check(
    output_dir: pathlib.Path,
    client: Any,
    sample_size: int = SPOT_CHECK_SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
) -> dict:
    """
    Samples up to `sample_size` admitted tasks from output_dir and scores each
    through the eval-tier model (Claude Sonnet 4.6) for quality calibration.

    This is a post-admission quality gate — it runs AFTER the dev-tier bulk
    filter and checks whether the admitted corpus meets eval-tier standards.
    Tasks flagged by this check are candidates for manual review or removal.

    Returns a summary dict with per-task scores and aggregate statistics.
    """
    eval_model = ROUTING["calibration"]["judge"]  # anthropic/claude-sonnet-4-6
    assert_no_leakage("", eval_model, "spot_check")  # eval-tier never generates

    task_files = sorted(output_dir.glob("*.json"))
    rng = random.Random(seed)
    sample = rng.sample(task_files, min(sample_size, len(task_files)))

    print(f"\n[EVAL-TIER SPOT CHECK] Scoring {len(sample)} tasks with {eval_model} ...")
    results = []
    flagged = []

    for f in sample:
        task = json.loads(f.read_text(encoding="utf-8"))
        task_id = task["task_id"]
        prompt = SPOT_CHECK_PROMPT.format(task_json=json.dumps(task, indent=2))
        try:
            response = client.chat.completions.create(
                model=eval_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                seed=RANDOM_SEED,
            )
            raw = response.choices[0].message.content.strip()
            scores = json.loads(raw)
            scores["task_id"] = task_id
            results.append(scores)
            flag = scores.get("flag", "PASS")
            print(f"  {task_id}: mean={scores.get('mean', 0):.2f} {flag} — {scores.get('note', '')}")
            if flag == "FLAG":
                flagged.append(task_id)
        except Exception as e:
            print(f"  {task_id}: spot-check error — {e}")
            results.append({"task_id": task_id, "error": str(e)})

    scored = [r for r in results if "mean" in r]
    summary = {
        "model":        eval_model,
        "sample_size":  len(sample),
        "scored":       len(scored),
        "flagged":      flagged,
        "mean_coherence":     round(sum(r.get("coherence", 0) for r in scored) / max(len(scored), 1), 2),
        "mean_verifiability": round(sum(r.get("verifiability", 0) for r in scored) / max(len(scored), 1), 2),
        "mean_rubric_clarity": round(sum(r.get("rubric_clarity", 0) for r in scored) / max(len(scored), 1), 2),
        "mean_overall": round(sum(r.get("mean", 0) for r in scored) / max(len(scored), 1), 2),
        "per_task":     results,
    }
    print(f"\nSpot-check complete: {len(flagged)} flagged / {len(scored)} scored. "
          f"Mean overall: {summary['mean_overall']:.2f}")
    return summary


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
