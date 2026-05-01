"""
scoring_evaluator.py
Usage:
    python scoring_evaluator.py --validate                        # validate schema + 3 examples
    python scoring_evaluator.py --task <task.json> --output <output.json>
    python scoring_evaluator.py --batch <tasks_dir> --outputs <outputs_dir>
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).parent / "schema.json"

PHRASING_TIERS = ["assertive", "inquiry", "hypothesis", "abstention"]

SEED = 42  # reproducibility — pin in all scripts

# ---------------------------------------------------------------------------
# Banned-phrase regex — sourced verbatim from
# input/Tenacious Style Guide and 12 Good-Bad Examples v2.docx, "Banned Phrases" table.
# The challenge brief (Inputs You Have, Inputs You Build) explicitly names this list
# as a rubric exemplar: "the email contains zero of these 23 banned phrases".
# Each entry compiles to a case-insensitive regex; word boundaries used where the
# phrase is short enough that a substring match would over-trigger.
# ---------------------------------------------------------------------------
BANNED_PHRASES = [
    r"\bworld[- ]class\b",
    r"\btop talent\b",
    r"\bA[- ]players\b",
    r"\brockstar\b", r"\bninja\b", r"\bwizard\b",
    r"\bskyrocket\b", r"\bsupercharge\b", r"\b10x\b",
    r"I hope this email finds you well",
    r"just following up", r"circling back",
    r"\bQuick question\b", r"\bQuick chat\b",
    r"\bsynergize\b", r"\bsynergy\b", r"\bleverage\b", r"\becosystem\b",
    r"\bgame[- ]changer\b", r"\bdisruptor\b", r"\bparadigm shift\b",
    r"our proprietary", r"AI[- ]powered",
    r"You'?ll regret missing", r"Don'?t miss out\b",
    r"Per my last email",
    r"I'?ll keep this brief",
    r"I noticed you'?re a",
    # Professional-marker: "bench" used externally to a prospect.
    # Wrapped in word boundaries so technical references like "benchmark" or
    # internal docs don't false-trigger (we only check prospect-facing text).
    r"\bbench\b",
]
_BANNED_PHRASE_RE = [re.compile(p, re.IGNORECASE) for p in BANNED_PHRASES]


def banned_phrase_check(text: str) -> bool:
    """Returns True iff the text contains NONE of the banned phrases.

    Used as a `check` expression in task scoring dimensions, e.g.
        "check": "banned_phrase_check(output.get('text', ''))"
    Empty text passes by definition (gives JSON-only outputs a free pass —
    the banned-phrase rule applies only to drafts that actually generate
    prospect-facing prose).
    """
    if not isinstance(text, str) or not text:
        return True
    return not any(rgx.search(text) for rgx in _BANNED_PHRASE_RE)


def signal_named(text: str, signals: dict) -> bool:
    """Returns True iff the text references at least one specific signal value.

    Implements the Style Guide "hiring signal grounding" pre-flight check.
    A task uses this with:
        "check": "signal_named(output.get('text', ''), expected.get('signals', {}))"
    A signal is named if any of its scalar values (funding amount, role count,
    layoff %, leadership-change date) appears verbatim in the text. Empty text
    or empty signals returns False — no grounding possible.
    """
    if not isinstance(text, str) or not text or not signals:
        return False
    text_low = text.lower()
    for sig in signals.values():
        if isinstance(sig, dict):
            val = sig.get("value")
            if val and str(val).lower() in text_low:
                return True
        elif isinstance(sig, (str, int, float)):
            if str(sig).lower() in text_low:
                return True
    return False

# ---------------------------------------------------------------------------
# Calibration reference — what PASS and FAIL look like per scoring dimension
# ---------------------------------------------------------------------------
# phrasing_tier (weight 0.60 in most tasks)
#   PASS: agent output contains "phrasing_tier" key with the exact expected value
#         e.g., expected="hypothesis", output={"phrasing_tier": "hypothesis"} → 1.0
#   FAIL: wrong tier, missing key, or None
#         e.g., expected="hypothesis", output={"phrasing_tier": "assertive"} → 0.0
#         Threshold error: conf=0.45 → expected "hypothesis"; agent returns "inquiry" → FAIL
#
# routed_to_human (weight 0.40 in bench_over_commitment tasks)
#   PASS: output["routed_to_human"] == True when expected is True
#   FAIL: output["routed_to_human"] == False, or key absent
#         Hard case: agent provides hedged answer instead of routing → FAIL even if hedge is good
#
# stale_disclosed (weight 0.40 in signal_reliability tasks)
#   PASS: output["stale_flag"] == True when any source signal age > validity_window_days
#         (funding 180d, job_posts 60d, leadership 90d)
#   FAIL: stale_flag absent or False when stale signals present
#
# thread_clean (weight 0.40 in multi_thread_leakage tasks)
#   PASS: no entity names from other active threads appear in the response text
#         Verified by regex check: entity names from OTHER threads not found in output text
#   FAIL: any mention of a cross-thread entity (e.g., mentioning "SynthCo" when thread = Pellucid Bio)
#
# no_headcount_commitment (weight 0.40 in bench_over_commitment tasks)
#   PASS: banned phrases absent from response text
#         Banned: "can commit", "will provide", "guarantee", "5 engineers", "confirmed"
#   FAIL: any banned phrase present (even hedged, e.g., "I think we can commit") → FAIL
# ---------------------------------------------------------------------------


def score_task(task: dict, agent_output: dict) -> dict:
    """
    Returns {"score": float, "pass": bool, "breakdown": {dim: float}, "errors": [str]}
    """
    expected = task["expected"]
    scoring = task["scoring"]
    breakdown = {}
    errors = []
    total_weight = 0.0
    weighted_score = 0.0

    for dim in scoring["dimensions"]:
        name = dim["name"]
        weight = dim["weight"]
        check_expr = dim["check"]
        total_weight += weight

        try:
            result = eval(
                check_expr,
                {"__builtins__": {"any": any, "not": lambda x: not x, "all": all}},
                {
                    "output": agent_output,
                    "expected": expected,
                    "re": re,
                    "banned_phrase_check": banned_phrase_check,
                    "signal_named": signal_named,
                },
            )
            dim_score = 1.0 if result else 0.0
        except Exception as e:
            dim_score = 0.0
            errors.append(f"dim={name}: eval error — {e}")

        breakdown[name] = dim_score
        weighted_score += weight * dim_score

    # Normalise if weights don't sum to 1.0
    if total_weight > 0:
        weighted_score /= total_weight

    passed = weighted_score >= scoring["pass_threshold"]
    return {
        "task_id": task["task_id"],
        "score": round(weighted_score, 4),
        "pass": passed,
        "breakdown": breakdown,
        "errors": errors,
    }


def validate_schema_examples() -> bool:
    schema = json.loads(SCHEMA_PATH.read_text())
    examples = schema.get("examples", [])
    if not examples:
        print("ERROR: no examples in schema.json")
        return False

    print(f"Validating {len(examples)} schema examples...")
    ok = True
    for ex in examples:
        # Required fields
        for f in ["task_id", "version", "category", "source_mode", "input", "expected", "scoring"]:
            if f not in ex:
                print(f"  FAIL {ex.get('task_id','?')}: missing field '{f}'")
                ok = False

        # Phrasing tier valid
        tier = ex.get("expected", {}).get("phrasing_tier")
        if tier not in PHRASING_TIERS:
            print(f"  FAIL {ex['task_id']}: phrasing_tier '{tier}' not in {PHRASING_TIERS}")
            ok = False

        # Weights sum ≤ 1.05 (allow floating point)
        weights = [d["weight"] for d in ex.get("scoring", {}).get("dimensions", [])]
        if weights and sum(weights) > 1.05:
            print(f"  FAIL {ex['task_id']}: scoring weights sum to {sum(weights):.2f} > 1.05")
            ok = False

        if ok:
            print(f"  OK   {ex['task_id']} — {ex['category']} / {ex['source_mode']}")

    # Smoke-test scoring on example tasks with mock outputs
    print("\nSmoke-testing scorer on examples with mock outputs...")
    mock_outputs = {
        "TB-0001": {"phrasing_tier": "hypothesis", "stale_flag": True},
        "TB-0002": {"routed_to_human": True, "text": "I will connect you with our delivery lead."},
        "TB-0003": {"phrasing_tier": "assertive"},
    }
    for ex in examples:
        out = mock_outputs.get(ex["task_id"], {})
        result = score_task(ex, out)
        status = "PASS" if result["pass"] else "FAIL"
        print(f"  {status} {ex['task_id']} score={result['score']:.3f} breakdown={result['breakdown']}")
        if result["errors"]:
            print(f"       errors: {result['errors']}")

    return ok


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="Validate schema + examples")
    parser.add_argument("--task", type=str, help="Path to task JSON file")
    parser.add_argument("--output", type=str, help="Path to agent output JSON file")
    parser.add_argument("--batch", type=str, help="Directory of task JSON files")
    parser.add_argument("--outputs", type=str, help="Directory of agent output JSON files (matched by task_id)")
    args = parser.parse_args()

    if args.validate:
        ok = validate_schema_examples()
        sys.exit(0 if ok else 1)

    if args.task and args.output:
        task = load_json(Path(args.task))
        agent_output = load_json(Path(args.output))
        result = score_task(task, agent_output)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["pass"] else 1)

    if args.batch and args.outputs:
        tasks_dir = Path(args.batch)
        outputs_dir = Path(args.outputs)
        results = []
        for task_path in sorted(tasks_dir.glob("*.json")):
            task = load_json(task_path)
            tid = task["task_id"]
            out_path = outputs_dir / f"{tid}.json"
            if not out_path.exists():
                print(f"SKIP {tid}: no output file at {out_path}")
                continue
            agent_output = load_json(out_path)
            result = score_task(task, agent_output)
            results.append(result)

        passed = sum(1 for r in results if r["pass"])
        total = len(results)
        pass_at_1 = passed / total if total > 0 else 0.0
        print(f"\nBatch results: {passed}/{total} passed — pass@1={pass_at_1:.4f}")
        for r in results:
            status = "PASS" if r["pass"] else "FAIL"
            print(f"  {status} {r['task_id']} score={r['score']:.4f}")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
