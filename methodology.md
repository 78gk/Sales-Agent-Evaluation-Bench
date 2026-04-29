# Methodology — Tenacious-Bench v0.1

**Path declaration:** Path A — Supervised Fine-Tuning (SFT)  
**Backbone:** Qwen 3.5 (version pinned in requirements.txt — 0.8B or 2B based on T4 VRAM fit)  
**Date declared:** 2026-04-29

---

## Path Justification

Signal Over-Claiming is a generation quality failure: the model chooses assertive phrasing when the evidence weight mandates hedge phrasing. This is not an inconsistency failure (Path B) or a trajectory failure (Path C) — it is a first-token generation decision driven by the prompt's confidence field being ignored.

Week 10 trace evidence:
- `sim_a553180f` (task 11): agent asserts facts without checking evidence threshold → reward=0.0
- `sim_0857ba6e` (task 76): agent completes without requesting required constraint → reward=0.0  
- `sim_f50f1801` (task 105): over-confident resolution on partial signal → reward=0.0

SFT on (input, correct_phrasing_tier) pairs directly teaches the model to route to the right tier. The training signal is clean and the evaluation is machine-verifiable.

---

## Dataset Composition (target: 200–300 tasks)

| Authoring mode | Target % | Count | Notes |
|---|---|---|---|
| Trace-derived | ~30% | 75 | Derived from seeds/trace_log.jsonl — adapt τ²-Bench tasks to Tenacious context with phrasing gate labels |
| Programmatic + parameter sweeps | ~30% | 75 | Sweep confidence levels (0.1–0.9) × signal types (funding/hiring/layoffs/leadership) × evidence counts |
| Multi-LLM synthesis | ~25% | 60 | OpenRouter: Qwen3-80B generates, DeepSeek V3.2 judges (never same model for both) |
| Hand-authored adversarial | ~15% | 40 | Edge cases: conflicting signals, near-threshold confidence, stale+fresh signal clash |
| **Total** | **100%** | **250** | Target |

---

## Partitioning

| Split | % | Count | Notes |
|---|---|---|---|
| train | 50% | ~125 | Used for LoRA fine-tuning |
| dev | 30% | ~75 | Used for validation loss + prompt iteration |
| held_out | 20% | ~50 | Sealed. Not committed to training scripts. Released only post-leaderboard. |

Held-out is gitignored from all training scripts. Sealed with SHA-256 hash committed to `ablations/held_out_seal.txt` on Day 2.

---

## Generation Router

| Task type | Generator | Judge | Notes |
|---|---|---|---|
| Synthesis tasks | Qwen3-80B (OpenRouter) | DeepSeek V3.2 (OpenRouter) | Never same model |
| Trace-derived | GPT-4.1-mini | Qwen3-80B | Lower cost for deterministic adaptation |
| Adversarial | Hand-authored | Claude Sonnet 4.6 (sealed slice only) | Eval-tier only on held_out |

**Preference leakage prevention:** Generator and judge are never the same model for the same task. Rotation policy documented in `generation_scripts/router_config.json`.

---

## Contamination Protocol

Three checks before sealing held_out (Day 2):

1. **n-gram overlap:** No 8-gram overlap between held_out and train/dev. Script: `generation_scripts/dedup_ngram.py`
2. **Embedding cosine similarity:** No pair with cosine > 0.85 (using `all-MiniLM-L6-v2`). Script: `generation_scripts/dedup_embed.py`
3. **Time-shift verification:** Held_out tasks authored on Day 2; train tasks authored on Day 1. Log timestamps committed.

Contamination report: `generation_scripts/contamination_report.md` (committed after Day 2 seal).

---

## Inter-Rater Agreement

- 30 tasks hand-labelled on Day 1
- Same 30 tasks re-labelled 24 hours later (Day 2) without seeing Day 1 labels
- Agreement matrix per dimension (phrasing_tier, routed_to_human, stale_flag) in `inter_rater_agreement.md`
- Threshold: ≥80% agreement per dimension required before sealing

---

## Scoring Design Constraints

All scoring dimensions must be **machine-verifiable** — `scoring_evaluator.py` returns a float with no human in the loop.

| Dimension | Check method |
|---|---|
| `phrasing_tier` | Exact string match: "assertive" / "inquiry" / "hypothesis" / "abstention" |
| `routed_to_human` | Boolean field in agent output JSON |
| `stale_disclosed` | Presence of `stale_flag: true` when source age > validity_window |
| `thread_clean` | Regex: no entity names from other active threads in response |

---

## Ablation Plan

| Delta | Comparison | Expected |
|---|---|---|
| Delta A | Trained (LoRA) vs Week 10 baseline on held_out | Positive, p<0.05 paired bootstrap |
| Delta B | Trained vs prompt-engineered version (same backbone, no training) | Publish honestly — negative result acceptable |
| Delta C | Trained vs Week 10 τ²-Bench score | Informational only — no τ²-Bench re-runs |
