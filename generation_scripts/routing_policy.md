# Generation Pipeline Routing Policy

**Project:** Tenacious-Bench v0.1
**Date:** 2026-04-30
**Enforces:** Generator ≠ judge for every (task_id, generation_run) pair.

---

## Model Tiers

### Dev Tier (bulk generation, Days 1–4)

| Role | Model | Provider | Max cost/task |
|---|---|---|---|
| Generator | `qwen/qwen3-80b` | OpenRouter | $0.02 |
| Judge | `deepseek/deepseek-chat-v3-2` | OpenRouter | $0.02 |

**Why these models:** Qwen3-80B has strong instruction-following and domain reasoning.
DeepSeek V3.2 uses a different training lineage, preventing self-preference leakage.
Neither model was used to develop the scoring rubric or phrasing-tier thresholds.

### Eval Tier (sealed held_out only, Days 4–5)

| Role | Model | Provider | Allowed days |
|---|---|---|---|
| Judge only | `anthropic/claude-sonnet-4-6` | OpenRouter | Days 4–5 |

**Why restricted:** Eval-tier models cost more and may have seen similar data.
Restricted to held_out calibration (≤4 passes) to contain cost within the $10 cap.
Never used as a generator.

### Trace-Derived Tier

| Role | Model | Provider |
|---|---|---|
| Generator | `openai/gpt-4.1-mini` | OpenRouter |
| Judge | `qwen/qwen3-80b` | OpenRouter |

**Why GPT-4.1-mini for trace tasks:** Lower cost for deterministic adaptation of existing
τ²-Bench traces. The task content is largely determined by the source trace; the model
only adapts phrasing and fills expected fields. Qwen3-80B judges to maintain cross-model
separation.

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

All synthesis and trace-derived tasks are scored by the judge on three dimensions
(prompt template: `generation_scripts/judge_prompt.txt`):

| Dimension | Threshold | What it checks |
|---|---|---|
| `coherence` | ≥ 3.5 / 5 | Prospect context logically supports the expected phrasing tier |
| `verifiability` | ≥ 3.5 / 5 | All expected fields are present and machine-checkable |
| `rubric_clarity` | ≥ 3.5 / 5 | The correct tier is unambiguous given the signals |

**Aggregate threshold:** `mean(coherence, verifiability, rubric_clarity) ≥ 3.5`

Tasks below threshold on the aggregate OR below 2/5 on any single dimension are discarded.

---

## Deduplication

Before any task is committed to a split, `generation_scripts/dedup_ngram.py` checks for
8-gram overlap with the existing corpus. Tasks sharing any 8-gram with a task in a
different split are rewritten or discarded. This enforces cross-split textual independence.

Embedding similarity check (`dedup_embed.py`, threshold cosine > 0.85) runs on Day 4
Colab to catch near-paraphrases that survive the n-gram filter.

---

## Reproducibility

`RANDOM_SEED = 42` is passed to all random operations in all generation scripts.
Sampling temperature and top-p are fixed per tier and documented in `router_config.json`.

---

## Budget Allocation

| Tier | Tasks | Estimated cost |
|---|---|---|
| Synthesis (dev tier) | ~60 tasks | ~$2.40 |
| Trace-derived (gpt-4.1-mini) | ~30 tasks | ~$0.50 |
| Eval-tier judge (held_out only) | ≤4 passes × 50 tasks | ~$2.00 |
| **Total** | | **≤$5.00** |

Remaining $5.00 of the $10 hard cap is held in reserve for retries and ablation scoring.
All costs logged in `cost_log.md` within 24 hours of each API call.
