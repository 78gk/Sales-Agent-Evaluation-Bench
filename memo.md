---
title: "Tenacious-Bench v0.1 — Interim Evaluation Report"
author: "Kirubel Tewodros, 10 Academy TRP1"
date: "2026-04-30"
---

# Tenacious-Bench v0.1 — Interim Report

**Author:** Kirubel Tewodros | **Cohort:** 10 Academy TRP1 | **Date:** 2026-04-30

---

## 1. The Problem

The Week 10 Conversion Engine agent achieved τ²-Bench pass@1 = 0.8333 (p=0.009,
z=2.619) [C-001]. τ²-Bench measures retail task completion — whether the agent calls
the right tool with the right arguments. It cannot measure whether the agent spoke with
appropriate confidence about uncertain prospect signals, whether it handed off to a human
when it should have, or whether it leaked context between concurrent sales threads.

For the Tenacious Conversion Engine, those three gaps are the product. Signal
Over-Claiming alone — the agent using assertive phrasing when evidence only supports a
hedge — triggers in 55% of interactions [C-002] and costs an estimated $2.40M per 1,000
sales touches in trust erosion and lost pipeline [C-004].

---

## 2. What Tenacious-Bench v0.1 Adds

Tenacious-Bench fills four evaluation dimensions absent from τ²-Bench:

| Dimension | What it tests | Graded by |
|---|---|---|
| Phrasing tier correctness | Does the agent hedge proportionally to evidence confidence? | String match on `phrasing_tier` field |
| Abstention-when-required | Does the agent route to a human instead of committing to headcount, pricing, or legal terms? | Boolean `routed_to_human` field |
| Thread isolation | Does the agent keep each prospect's context clean in multi-thread sessions? | Regex on response text |
| Staleness disclosure | Does the agent flag signals whose age exceeds their validity window? | Boolean `stale_flag` field |

All four dimensions are scored by `scoring_evaluator.py` with no human in the loop.
The phrasing tier thresholds are deterministic: assertive (conf ≥ 0.80, ≥2 fresh signals),
inquiry (conf 0.50–0.79), hypothesis (conf 0.25–0.49), abstention (conf < 0.25 or all
stale or commitment requested).

---

## 3. Dataset Status

**155 tasks authored and verified** as of Day 3:

| Split | Tasks | Purpose |
|---|---|---|
| `train/` | 75 | LoRA fine-tuning (Day 4) |
| `dev/` | 30 | Validation loss + prompt iteration |
| `held_out/` | 50 | Sealed — Delta A/B measurement only |
| **Total** | **155** | 62% of 250-task target |

Category coverage:

| Category | Count | Notes |
|---|---|---|
| signal_over_claiming | 71 | Primary training target — highest frequency + cost |
| bench_over_commitment | 20 | Headcount / pricing / timeline commitment tasks |
| tone_drift | 10 | Professional register under pushback and informal input |
| dual_control | 8 | Autonomous booking and proposal generation failures |
| signal_reliability | 12 | Stale-signal disclosure |
| icp_misclassification | 11 | Conflicting signals, recency ordering |
| gap_over_claiming | 6 | Competitive benchmark over-assertion |
| multi_thread_leakage | 7 | Cross-thread entity isolation |
| scheduling_edge | 5 | Timezone / holiday / reschedule failures |
| cost_pathology | 5 | Runaway processing / retry loops |

All 155 tasks pass `scoring_evaluator.py --batch` at 100%. The held_out split is sealed
with SHA-256 hashes in `ablations/held_out_seal.txt` and gitignored from all training
scripts. An 8-gram contamination check across all three splits confirms zero cross-split
prompt overlap (`generation_scripts/contamination_report.md`).

Inter-rater reliability across 30 sampled train tasks: phrasing_tier 96.7%,
routed_to_human 100%, stale_disclosed 100%, thread_clean 100% — all exceed the 80%
threshold required for seal approval.

---

## 4. Training Plan

**Path A — SFT with LoRA on Qwen 3.5** (Day 4, Colab T4, 16 GB VRAM).

The failure mode is a first-token generation decision: the model ignores the confidence
field in the prompt and defaults to assertive phrasing. SFT on (input, correct_phrasing_tier)
pairs directly teaches the routing decision. LoRA keeps the adapter small (publishable to
HuggingFace) and enables clean ablation comparisons.

**Ablation plan:**
- **Delta A:** Trained LoRA vs Week 10 baseline on `held_out` — primary improvement
  measurement, p<0.05 required (paired bootstrap, n=1000)
- **Delta B:** Trained LoRA vs prompt-engineered Qwen 3.5 (no training, same backbone)
  — tests whether SFT adds value over prompt engineering alone; negative result is
  publishable
- **Delta C:** Informational comparison against τ²-Bench pass@1 = 0.8333 — no re-runs

**Budget:** $0.00 spent of $10.00 cap through Day 3. All 155 tasks generated
programmatically at zero API cost. OpenRouter synthesis budget (~$2–3) preserved for
Days 3–4 to extend the corpus to 250 tasks.

---

## 5. What Ships Saturday

- Full 250-task dataset on HuggingFace (CC-BY-4.0), held_out released post-leaderboard
- LoRA adapter on HuggingFace (Qwen 3.5, trained on 125 train tasks)
- Ablation results: Delta A and Delta B with confidence intervals
- 8 synthesis memos (Liu et al. COLM 2024, Gebru 2021, Tülu 3, LIMA, Magpie, and three others)
- Blog post and τ²-Bench GitHub community engagement

---

*All numeric claims in this memo resolve to rows in `evidence_graph.json`.
C-005 (cost/lead = $0.52) is marked unverified pending source confirmation and
is not cited in this report.*
