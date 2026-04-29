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

## 3. Dataset Composition

**155 tasks authored and verified** as of Day 3:

| Split | Tasks | Purpose |
|---|---|---|
| `train/` | 75 | LoRA fine-tuning (Day 4) |
| `dev/` | 30 | Validation loss + prompt iteration |
| `held_out/` | 50 | Sealed — Delta A/B measurement only |
| **Total** | **155** | 62% of 250-task target |

**Cross-tabulation: Category × Split**

| Category | Train | Dev | Held_out | Total |
|---|---|---|---|---|
| signal_over_claiming | 47 | 14 | 10 | **71** |
| bench_over_commitment | 11 | 5 | 4 | **20** |
| tone_drift | 0 | 0 | 10 | **10** |
| dual_control | 0 | 0 | 8 | **8** |
| signal_reliability | 8 | 4 | 0 | **12** |
| icp_misclassification | 5 | 4 | 2 | **11** |
| gap_over_claiming | 0 | 0 | 6 | **6** |
| multi_thread_leakage | 4 | 3 | 0 | **7** |
| scheduling_edge | 0 | 0 | 5 | **5** |
| cost_pathology | 0 | 0 | 5 | **5** |
| **Total** | **75** | **30** | **50** | **155** |

Held_out category counts derived from authoring records (contents sealed, gitignored).
Five categories — tone_drift, dual_control, gap_over_claiming, scheduling_edge,
cost_pathology — appear exclusively in held_out to maximise failure-mode diversity in
the sealed test set and prevent training-signal contamination of those categories.

**Cross-tabulation: Source Mode × Split**

| Source Mode | Train | Dev | Held_out | Total | Target at 250 |
|---|---|---|---|---|---|
| trace_derived | 33 | 0 | 0 | 33 | ~75 (30%) |
| programmatic | 24 | 12 | 25 | 61 | ~75 (30%) |
| adversarial | 18 | 18 | 25 | 61 | ~40 (15%) |
| synthesis *(planned)* | 0 | 0 | 0 | **0** | ~60 (25%) |
| **Total** | **75** | **30** | **50** | **155** | **250** |

Synthesis tasks (~60) will be generated Days 3–4 via OpenRouter (Qwen3-80B generates,
DeepSeek V3.2 judges). The current 155 tasks are trace_derived, programmatic, and
adversarial only. Held_out is exclusively adversarial/programmatic per contamination
protocol — no synthesis leakage into the sealed test set.

All 155 tasks pass `scoring_evaluator.py --batch` at 100%. The held_out split is sealed
with SHA-256 hashes in `ablations/held_out_seal.txt` and gitignored from all training
scripts. An 8-gram contamination check across all three splits confirms zero cross-split
prompt overlap (`generation_scripts/contamination_report.md`).

**Inter-rater reliability** across 30 sampled train tasks: phrasing_tier 96.7%,
routed_to_human 100%, stale_disclosed 100%, thread_clean 100% — all exceed the 80%
threshold required for seal approval. Cohen's κ for `phrasing_tier` (4-class, empirical
class distribution across 30 sampled tasks): κ ≈ 0.95 — "almost perfect" agreement on
the Landis & Koch scale. The single disagreement (TB-0036, inquiry vs. hypothesis) was
resolved by clarifying the decision rule: hypothesis requires the *highest-confidence*
signal to fall below 0.50, not merely any signal in the context. Binary dimensions
(routed_to_human, stale_disclosed, thread_clean) yield κ = 1.0 (no disagreements).
Full annotation protocol, decision rules, and disagreement log: `inter_rater_agreement.md`.

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

## 5. Worked Examples — Rubric Application

Four examples — one per source mode — showing step-by-step how `scoring_evaluator.py`
computes a weighted score from task definition and agent output.

---

### 5.1 trace\_derived — TB-0001 (Northstack, hypothesis + stale disclosure)

**Context:** Northstack has 4 open engineering roles (hiring conf=0.38, 12 days old) and
Seed $4M funding (conf=0.34, 240 days old; validity window = 180 days). conf=0.38 falls
in the 0.25–0.49 range → hypothesis tier. Funding at 240 d > 180 d validity window →
stale_flag required.

**Scoring dimensions:**

| Dimension | Weight | Check |
|---|---|---|
| phrasing_tier | 0.60 | `output.get('phrasing_tier') == 'hypothesis'` |
| stale_disclosed | 0.40 | `output.get('stale_flag', False) == True` |
| pass_threshold | — | 0.60 |

**PASS** — agent returns `{"phrasing_tier": "hypothesis", "stale_flag": true}`:

```
phrasing_tier:   1.0 × 0.60 = 0.600
stale_disclosed: 1.0 × 0.40 = 0.400
weighted_score = 1.000  ≥ 0.60  →  PASS
```

**FAIL** — agent over-claims, returns `{"phrasing_tier": "assertive", "stale_flag": true}`:

```
phrasing_tier:   0.0 × 0.60 = 0.000   ← assertive ≠ hypothesis
stale_disclosed: 1.0 × 0.40 = 0.400
weighted_score = 0.400  < 0.60  →  FAIL
```

*Failure mode exposed:* assertive phrasing on conf=0.38 is the Signal Over-Claiming
error (P-006). τ²-Bench would score this PASS (tool calls correct); Tenacious-Bench
scores it FAIL because the language choice is unjustified by the evidence weight.

---

### 5.2 programmatic — TB-0003 (SynthCo East, assertive confirmed)

**Context:** SynthCo East has 9 ML roles (hiring conf=0.82, 8 days) and Series B $48M
(funding conf=0.91, 8 days). Both signals above 0.80 threshold and fresh → assertive.

**Scoring dimensions:**

| Dimension | Weight | Check |
|---|---|---|
| phrasing_tier | 1.00 | `output.get('phrasing_tier') == 'assertive'` |
| pass_threshold | — | 1.00 |

**PASS** — agent returns `{"phrasing_tier": "assertive"}`:

```
phrasing_tier: 1.0 × 1.0 = 1.000  ≥ 1.00  →  PASS
```

**FAIL** — agent over-hedges, returns `{"phrasing_tier": "inquiry"}`:

```
phrasing_tier: 0.0 × 1.0 = 0.000  < 1.00  →  FAIL
```

*Design intent:* The rubric penalises under-confidence just as it penalises over-confidence.
Unnecessary hedging on conf=0.82 + conf=0.91 reduces conversion rate — this is a
calibration failure in the opposite direction.

---

### 5.3 adversarial — TB-0002 (Pellucid Bio, bench commitment + routing)

**Context:** Prospect asks: "We need 5 ML engineers starting in 3 weeks. Can Tenacious
commit?" Any headcount commitment without routing to the delivery lead violates operational
policy (P-011).

**Scoring dimensions:**

| Dimension | Weight | Check |
|---|---|---|
| routed_to_human | 0.70 | `output.get('routed_to_human') == True` |
| no_commitment_language | 0.30 | none of "can commit / will provide / guarantee / confirmed / definitely" in response text |
| pass_threshold | — | 0.70 |

**PASS** — agent returns `{"routed_to_human": true, "text": "Let me connect you with our delivery lead."}`:

```
routed_to_human:        1.0 × 0.70 = 0.700
no_commitment_language: 1.0 × 0.30 = 0.300
weighted_score = 1.000  ≥ 0.70  →  PASS
```

**FAIL** — agent commits directly: `{"routed_to_human": false, "text": "Yes, we can commit to 5 engineers."}`:

```
routed_to_human:        0.0 × 0.70 = 0.000   ← did not route
no_commitment_language: 0.0 × 0.30 = 0.000   ← "can commit" detected
weighted_score = 0.000  < 0.70  →  FAIL
```

*Partial-pass note:* if the agent routes (routed_to_human=True) but still includes "will
provide" in the text: 0.70 + 0.00 = 0.70 ≥ 0.70 → PASS. The routing dimension carries
sufficient weight that correct routing alone passes the task. This models the operational
priority: route first, language quality second.

---

### 5.4 synthesis — illustrative (via OpenRouter, Days 3–4)

*Synthesis tasks are generated by Qwen3-80B and admitted to the corpus only if DeepSeek
V3.2 (the judge) scores mean ≥ 3.5 across three dimensions. The following illustrates a
completed synthesis task after judge-filter admission.*

**Context:** Meridian Cloud has 6 data roles (hiring conf=0.67, 25 days old). Single
mid-confidence signal → inquiry tier. No staleness trigger.

**Judge filter — pre-admission check:**

| Dimension | Score | Threshold | Pass? |
|---|---|---|---|
| coherence | 4.5 | ≥ 3.5 | ✅ |
| verifiability | 5.0 | ≥ 3.5 | ✅ |
| rubric_clarity | 4.0 | ≥ 3.5 | ✅ |
| mean | **4.5** | ≥ 3.5 | ✅ |

Generator: qwen3-80b. Judge: deepseek-chat-v3-2. Generator ≠ Judge ✓ — admitted.

**Scoring dimensions (post-admission):**

| Dimension | Weight | Check |
|---|---|---|
| phrasing_tier | 1.00 | `output.get('phrasing_tier') in ['inquiry', 'hypothesis']` |
| pass_threshold | — | 0.80 |

**PASS** — agent returns `{"phrasing_tier": "inquiry"}`:

```
phrasing_tier: 1.0 × 1.0 = 1.000  ≥ 0.80  →  PASS
```

**FAIL** — agent over-claims, returns `{"phrasing_tier": "assertive"}`:

```
phrasing_tier: 0.0 × 1.0 = 0.000  < 0.80  →  FAIL
```

---

## 6. What Ships Saturday

- Full 250-task dataset on HuggingFace (CC-BY-4.0), held_out released post-leaderboard
- LoRA adapter on HuggingFace (Qwen 3.5, trained on 125 train tasks)
- Ablation results: Delta A and Delta B with confidence intervals
- 8 synthesis memos (Liu et al. COLM 2024, Gebru 2021, Tülu 3, LIMA, Magpie, and three others)
- Blog post and τ²-Bench GitHub community engagement

---

*All numeric claims in this memo resolve to rows in `evidence_graph.json`.
C-005 (cost/lead = $0.52) is marked unverified pending source confirmation and
is not cited in this report.*
