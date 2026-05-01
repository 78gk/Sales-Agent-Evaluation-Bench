# Generation Pipeline Routing Policy

**Project:** Tenacious-Bench v0.1
**Date:** 2026-05-01 (updated)
**Enforces:** Generator ≠ judge for every (task_id, generation_run) pair.

---

## Model Tiers

### Dev Tier (bulk generation, Days 1–5)

| Role | Model | Provider | Max cost/task |
|---|---|---|---|
| Generator | `qwen/qwen3-235b-a22b` | OpenRouter | ~$0.04 |
| Judge | `deepseek/deepseek-chat-v3-0324` | OpenRouter | ~$0.005 |

**Why these models:** Qwen3-235b-a22b is a 235B MoE model with strong instruction-following and domain reasoning.
DeepSeek V3 (0324) uses a different training lineage, preventing self-preference leakage.
Neither model was used to develop the scoring rubric or phrasing-tier thresholds.

**Anti-leakage rationale:** Li et al. (2025), "Preference Contamination in LLM-as-a-Judge Pipelines," show that when the same model family is used for both generation and judging, scores inflate by 8–15% due to in-group preference. This policy enforces model-family separation at the generator/judge boundary to prevent that bias from entering the corpus.

### Eval Tier (sealed held_out only, Days 4–6)

| Role | Model | Provider | Allowed days |
|---|---|---|---|
| Judge only | `anthropic/claude-sonnet-4-6` | OpenRouter | Days 4–6 |

**Why restricted:** Eval-tier models cost more and may have seen similar data.
Restricted to held_out calibration (≤4 passes) to contain cost within the $10 cap.
Never used as a generator.

---

## Preference Leakage Prevention

**Rule:** For any single `(task_id, generation_run)` pair, the `generator_model` field
and the `judge_model` field must never hold the same model identifier.

**Enforcement in code (synthesis_generator.py):**

```python
RANDOM_SEED = 42

def assert_no_leakage(generator_model: str, judge_model: str, task_id: str) -> None:
    if generator_model == judge_model:
        raise ValueError(
            f"Preference leakage: generator and judge are both '{generator_model}' "
            f"for task {task_id}. Rotate the judge model before continuing."
        )
```

This assertion runs before any task is written to disk. A task that triggers it is
discarded, not committed.

---

## Judge Filter — Three Dimensions

All synthesis tasks are scored by the judge on three dimensions
(prompt template: `generation_scripts/judge_prompt.txt`):

| Dimension | Threshold | What it checks |
|---|---|---|
| `coherence` | ≥ 3.5 / 5 | Prospect context logically supports the expected phrasing tier |
| `verifiability` | ≥ 3.5 / 5 | All expected fields are present and machine-checkable |
| `rubric_clarity` | ≥ 3.5 / 5 | The correct tier is unambiguous given the signals |

**Aggregate threshold:** every dimension must score ≥ 3.5 individually (no averaging shortcut).

Tasks failing any single dimension are discarded. Rejection rate is logged to console during synthesis runs.

---

## Deduplication

Before any task is committed to a split, `generation_scripts/dedup_ngram.py` checks for
8-gram overlap with the existing corpus. Tasks sharing any 8-gram with a task in a
different split are rewritten or discarded. This enforces cross-split textual independence.

Embedding similarity check (`dedup_embed.py`, threshold cosine > 0.85) runs on Colab
to catch near-paraphrases that survive the n-gram filter.

---

## Reproducibility

`RANDOM_SEED = 42` is passed to all random operations in all generation scripts.
Sampling temperature and top-p are fixed per tier and documented in `router_config.json`.

---

## Budget Allocation (actual)

| Tier | Tasks | Actual cost |
|---|---|---|
| Synthesis (dev tier, train+dev) | ~170 admitted (~340 generated) | ~$7.50 |
| Eval-tier judge (held_out only) | ≤4 passes × 50 tasks | ~$2.50 reserved |
| **Total** | | **≤$10.00** |

All costs logged in `cost_log.md` within 24 hours of each API call.
