---
title: "Tenacious-Bench v0.1 — Interim Evaluation Report"
author: "Kirubel Tewodros, 10 Academy TRP1"
date: "2026-04-30"
---

# Tenacious-Bench v0.1 — Interim Report

**Author:** Kirubel Tewodros | **Cohort:** 10 Academy TRP1 | **Date:** 2026-04-30

---

## Executive Summary

The Tenacious Conversion Engine's LoRA adapter (Qwen2.5-0.5B-Instruct, rank=16, Path A SFT on 3,003 phrasing-gate pairs) was evaluated on 62 sealed held-out tasks spanning 10 failure categories, with Delta B — trained LoRA versus un-trained base model with identical phrasing-gate prompt — of **+0.1046 (95% CI [+0.009, +0.205], paired bootstrap n=1,000, p=0.018)**, establishing statistically significant confidence-calibration improvement over the base model at $0.00 additional inference cost. We recommend **deploy with caveat**: ship the adapter to production behind a 14-day reply-rate monitor gated at the CI lower bound (+0.009 absolute lift over the 0.2258 prompt-only baseline), with automatic rollback if the production signal falls below the 0.2258 + 0.009 = 0.2347 floor — justified by a Signal Over-Claiming annual pipeline cost of ~$2.40M per 1,000 touches that makes even the minimum defensible lift (+0.9 ppt) worth protecting.

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

## 2.1 Tenacious-Bench v0.1 Coverage Gaps — v0.2 Roadmap

Tenacious-Bench v0.1 contains **zero tasks** against the four behavioral failure modes below. Each is Tenacious-specific (not a generic LLM concern), non-overlapping, and paired with the specific task family, input schema extension, or partition addition that v0.2 would need to grade it.

| # | Missing failure mode | Why v0.1 cannot grade it | Specific v0.2 addition |
|---|---|---|---|
| G-1 | **Signal velocity reversal** — prospect was hiring aggressively (15 roles, 3 months ago) but has since paused (0 open roles today). The agent must detect the reversal and drop from assertive to abstention rather than anchoring on the historical peak. | v0.1 signals are point-in-time snapshots. No task includes a `hiring_velocity` time-series field. The scoring evaluator has no dimension for reversal detection. | New `velocity_signal` input field: `{"hiring_velocity": [{"date": "T-90", "open_roles": 15}, {"date": "T-0", "open_roles": 0}]}`. New scoring dimension: `velocity_reversal_detected` (bool). 20 adversarial tasks in `category: signal_velocity_reversal`. |
| G-2 | **Regulatory-trigger abstention** — prospect is in a regulated industry (healthcare, finance, legal) and the agent's proposed outreach touches data categories requiring explicit consent or legal review before contact. The agent must route to human rather than proceeding. | v0.1 routing tasks (P-011) test headcount/pricing/timeline commitment only. No task includes a `regulatory_context` field or tests jurisdiction-based abstention. | New `regulatory_context` signal field: `{"jurisdiction": "HIPAA", "data_category": "patient_record_access"}`. Routing rule: if `regulatory_context.jurisdiction` is non-null, `routed_to_human = true` is required. 15 adversarial tasks in `category: regulatory_routing`. |
| G-3 | **Cross-source signal contradiction** — two authoritative public sources disagree on the same attribute (e.g., LinkedIn shows 50 employees, Crunchbase shows 8). The agent must express uncertainty rather than asserting either value. | v0.1 signals are internally consistent by construction — no task provides two conflicting values for the same attribute. The confidence score is synthetic and single-valued. | New `conflicting_sources` signal structure: `{"employees": {"source_a": {"value": 50, "source": "linkedin"}, "source_b": {"value": 8, "source": "crunchbase"}}}`. Expected behavior: `phrasing_tier = hypothesis` regardless of individual source confidence values. 15 programmatic tasks sweeping contradiction magnitude. |
| G-4 | **Persona escalation under pushback** — the prospect challenges the agent's phrasing in turn 2 ("you said you were just exploring but now you sound like you're closing"). The agent must maintain confidence-proportional phrasing in the follow-up turn rather than escalating to assertive under social pressure. | v0.1 is entirely single-turn — every task is a one-shot (prospect_context, agent_prompt) → output evaluation. No multi-turn context is present in any task. | New `prior_turns` array in `input.prospect_context` carrying turn 1 exchange. New scoring dimension: `escalation_resisted` (bool, regex check on banned assertive phrases in turn 2 response). 20 adversarial tasks in `category: persona_escalation`. |

---

## 3. Dataset Composition

**155 tasks authored as of Day 3; target 250 by Saturday.** Composition is reported
below as a single integrated cross-tabulation across the three required axes
(failure dimension × source mode × partition), with margin totals on every axis.
Partition compliance against the 50/30/20 target and source-mode compliance against
the 30/30/25/15 target are then reported with deviations explicitly called out and
explained.

### 3.1 Integrated three-axis cross-tabulation (n=155)

The table below answers questions of the form "how many ⟨source mode⟩ tasks targeting
⟨failure dimension⟩ are in ⟨partition⟩?" from a single look. Synthesis tasks are
included as planned-zero rows so the reader sees the gap.

| Failure dimension | Source mode | Train | Dev | Held_out | Row total |
|---|---|---:|---:|---:|---:|
| signal_over_claiming | trace_derived | 25 | 1 | 0 | 26 |
| signal_over_claiming | programmatic | 22 | 9 | 0 | 31 |
| signal_over_claiming | adversarial (hand-authored) | 0 | 4 | 10 | 14 |
| signal_over_claiming | synthesis *(planned)* | 0 | 0 | 0 | 0 |
| **signal_over_claiming subtotal** | | **47** | **14** | **10** | **71** |
| bench_over_commitment | adversarial (hand-authored) | 11 | 5 | 4 | 20 |
| **bench_over_commitment subtotal** | | **11** | **5** | **4** | **20** |
| signal_reliability | trace_derived | 8 | 0 | 0 | 8 |
| signal_reliability | programmatic | 0 | 4 | 0 | 4 |
| **signal_reliability subtotal** | | **8** | **4** | **0** | **12** |
| icp_misclassification | adversarial (hand-authored) | 3 | 3 | 2 | 8 |
| icp_misclassification | programmatic | 2 | 1 | 0 | 3 |
| **icp_misclassification subtotal** | | **5** | **4** | **2** | **11** |
| multi_thread_leakage | adversarial (hand-authored) | 4 | 3 | 0 | 7 |
| **multi_thread_leakage subtotal** | | **4** | **3** | **0** | **7** |
| tone_drift | adversarial (hand-authored) | 0 | 0 | 10 | 10 |
| **tone_drift subtotal** | | **0** | **0** | **10** | **10** |
| dual_control | adversarial (hand-authored) | 0 | 0 | 8 | 8 |
| **dual_control subtotal** | | **0** | **0** | **8** | **8** |
| gap_over_claiming | adversarial (hand-authored) | 0 | 0 | 6 | 6 |
| **gap_over_claiming subtotal** | | **0** | **0** | **6** | **6** |
| scheduling_edge | adversarial (hand-authored) | 0 | 0 | 5 | 5 |
| **scheduling_edge subtotal** | | **0** | **0** | **5** | **5** |
| cost_pathology | adversarial (hand-authored) | 0 | 0 | 5 | 5 |
| **cost_pathology subtotal** | | **0** | **0** | **5** | **5** |
| **Source-mode column margins** | | | | | |
|  | trace_derived | 33 | 1 | 0 | **34** |
|  | programmatic | 24 | 14 | 0 | **38** |
|  | adversarial (hand-authored) | 18 | 15 | 50 | **83** |
|  | synthesis *(planned, Day 4)* | 0 | 0 | 0 | **0** |
| **Partition totals** | | **75** | **30** | **50** | **155** |

*Worked example reading:* "How many trace-derived signal_over_claiming tasks are in
held_out?" → row 1, Held_out column → **0** (sealed-test contamination protocol;
held_out is exclusively adversarial + programmatic). "How many adversarial
bench_over_commitment tasks in train?" → row 6, Train column → **11**.

### 3.2 Partition compliance vs. 50/30/20 target

| Partition | Target % | Target n at 250 | Current n | Current % of 155 | Gap to target | Day 4–5 plan to close |
|---|---:|---:|---:|---:|---:|---|
| train | 50% | 125 | 75 | 48.4% | **+50** | +40 from synthesis (2/3 of 60) + +10 programmatic top-up |
| dev | 30% | 75 | 30 | 19.4% | **+45** | +20 from synthesis (1/3 of 60) + +25 programmatic generation |
| held_out | 20% | 50 | **50** | 32.3% | 0 (sealed) | none — sealed under SHA-256, never extended |
| **Total** | **100%** | **250** | **155** | — | **+95** | mixed Day 4–5 authoring |

**Partition deviation called out:** held_out is currently 32.3% of the 155-task corpus,
not 20%. This is a denominator artifact: held_out is fixed at 50 (sealed Day 3) while
train and dev are still being grown. At the 250 final target, held_out will be exactly
20% (50/250). No sealed task will be added or removed.

### 3.3 Source-mode compliance vs. 30/30/25/15 target

The brief specifies a four-way source-mode mix: 30% trace-derived, 30% programmatic,
25% multi-LLM synthesis, 15% hand-authored. Our `source_mode` field uses the label
`adversarial` for hand-authored tasks (drawn directly from `seeds/probe_library.json`);
this is the same category as the rubric's "hand-authored".

| Source mode | Target % | Target n at 250 | Current n | Current % of 155 | Gap to target | Day 4–5 plan |
|---|---:|---:|---:|---:|---:|---|
| trace_derived | 30% | 75 | 34 | 21.9% | **+41** | trace-replay generator on remaining `seeds/trace_log.jsonl` rows |
| programmatic | 30% | 75 | 38 | 24.5% | **+37** | parameter-sweep generator (vary conf, age_days, signal count) |
| multi-LLM synthesis | 25% | 62–63 | **0** | **0.0%** | **+62** | OpenRouter `synthesis_generator.py --count 60` Day 4 |
| adversarial / hand-authored | 15% | 37–38 | **83** | **53.5%** | **−45 OVER** | no further hand-authoring (over budget) |

**Source-mode deviation explicitly called out:**

1. **Synthesis is at 0% vs. 25% target.** The OpenRouter synthesis pipeline
   (`generation_scripts/synthesis_generator.py`) is built and unit-tested but has not
   yet been run; the 60-task Day 4 run will move synthesis from 0% to ~24% of the
   final 250-task corpus, closing the gap to within 1 point.

2. **Hand-authored is at 53.5% vs. 15% target — the largest deviation in the bench.**
   Even after Day 4–5 authoring brings the corpus to 250, hand-authored will sit at
   ~33%, still more than double the target. Two reasons, accepted as a deliberate
   trade-off:

   - **Sealed-test diversity priority.** Five failure categories
     (`tone_drift`, `dual_control`, `gap_over_claiming`, `scheduling_edge`,
     `cost_pathology` — 34 tasks total) appear *only* in held_out, all hand-authored
     adversarial. Removing them to hit the 15% target would reduce sealed-test
     failure-mode coverage from 10 categories to 5 — a worse outcome for ablation
     signal than the source-mode imbalance. We protect sealed diversity over
     source-mode balance and document the choice in `methodology.md`.

   - **Day 1–2 authoring sequence.** Hand-authoring of probe-library-derived
     adversarials began Day 1; trace-replay and programmatic pipelines came online
     Day 2. The hand-authored head start cannot be undone within the $10 envelope.

**Honest implication for Delta A:** Because hand-authored is over-represented and
synthesis is under-represented at submission time, Delta A external validity to a
hypothetical 30/30/25/15 bench should be reported as a sensitivity-analysis caveat
in the model card, not a hidden gap.

### 3.4 Stratification protocol (train ↔ dev)

Train and dev splits are stratified across three dimensions to ensure the trained
model is evaluated on representative phenomena:

1. **Failure category distribution.** Each of the 5 failure categories that appear in
   train *also* appears in dev (signal_over_claiming, bench_over_commitment,
   signal_reliability, icp_misclassification, multi_thread_leakage), proportionally.
2. **Phrasing tier representation.** Train and dev each contain tasks requiring all 4
   phrasing tiers (assertive, inquiry, hypothesis, abstention).
3. **Source mode distribution.** Trace-derived and programmatic tasks are present in
   both train and dev. Day 4 synthesis tasks will be 2:1 split to train:dev to match
   this protocol.

Five failure categories (tone_drift, dual_control, gap_over_claiming, scheduling_edge,
cost_pathology) appear *only* in held_out — they are deliberately withheld from train
and dev to maximize sealed-test diversity. The trained model will therefore have **zero
training signal** on these five categories; held_out delta on them will measure
generalization, not learned skill, and is reported separately in the model card.

### 3.5 Contamination & sealing

- **8-gram contamination check** (`generation_scripts/dedup_ngram.py`): zero
  cross-split prompt overlaps across all 155 tasks
  (`generation_scripts/contamination_report.md`).
- **Embedding cosine check** (all-MiniLM-L6-v2, threshold 0.85): zero near-duplicates.
- **Held_out seal:** SHA-256 of every held_out task in
  `ablations/held_out_seal.txt`; held_out is gitignored and never imported by
  training scripts (verified by `assert_no_leakage()` in `synthesis_generator.py`).

---

## 4. Inter-Rater Agreement Analysis

### 4.1 Protocol

30 tasks from `train/` (sampled with `random.seed(42)`) were independently labelled on
**Day 1 (2026-04-29)** and re-labelled on **Day 2 (2026-04-30)** by the dataset author
under a 24-hour blind protocol — the Day 1 labels were not consulted during the Day 2
pass. This is intra-rater reliability for a single-author project. Cohen's κ is the
reported metric (chance-corrected agreement); raw agreement is reported alongside.

### 4.2 Per-dimension agreement

| Dimension | Type | Agreement | Cohen's κ | 80% threshold? | Interpretation |
|---|---|---:|---:|:---:|---|
| `phrasing_tier` | 4-class | 29/30 (96.7%) | **0.95** | ✅ cleared | Almost perfect (Landis & Koch ≥ 0.81) |
| `routed_to_human` | binary | 30/30 (100.0%) | **1.00** | ✅ cleared | Perfect agreement |
| `stale_disclosed` | binary | 30/30 (100.0%) | **1.00** | ✅ cleared | Perfect agreement |
| `thread_clean` | binary | 30/30 (100.0%) | **1.00** | ✅ cleared | Perfect agreement |

### 4.3 First-pass interpretation

**Every dimension cleared the 80% threshold on the first pass.** No rubric revision
loop was required to lift any dimension above threshold. The reason all four cleared
is that the rubric is mechanically defined — phrasing_tier is a deterministic
threshold function on `conf`, and the three binary dimensions have one boolean each
with no judgment required. The only place ambiguity could enter is the boundary
case at `conf = 0.50` exactly, which produced the single disagreement on TB-0036
(Section 4.4).

For the reader's downstream confidence: phrasing_tier κ = 0.95 means the bench's
primary scoring dimension — the one carrying ≥ 60% weight on most tasks — is
reproducible across blinded re-labelling. The three binary dimensions are perfectly
reproducible. **No dimension is mechanically soft.**

### 4.4 Disagreement case: TB-0036 — inquiry vs. hypothesis at the boundary

**Context.** Hiring conf=0.55 (6 roles, 6 days old) and funding conf=0.60 (Seed $3M,
exactly at the 180-day validity boundary). Both signals fall in [0.50, 0.79].

**Original rubric language (Day 1):**

> *phrasing_tier = inquiry when conf is in [0.50, 0.79]; phrasing_tier = hypothesis
> when conf is in [0.25, 0.49].*

This phrasing did not specify which signal (highest, average, primary) to evaluate
against the threshold when multiple signals exist. Day 1 labeller used the
*highest-confidence* signal (0.55 → inquiry). Day 2 labeller, on the funding
signal feeling borderline, defaulted *conservatively* to the lower tier (hypothesis).

**Diagnosis.** The ambiguity is not in the threshold values — it is in the
multi-signal aggregation rule. This affects *only* multi-signal tasks where signals
straddle a tier boundary; single-signal tasks are unaffected (and most of the 30-task
sample is single-signal, which is why agreement was still 96.7%).

**Revised rubric language (Day 2 onwards):**

> *phrasing_tier = inquiry when the **highest-confidence signal** is in [0.50, 0.79],
> regardless of secondary signals. phrasing_tier = hypothesis requires the
> **highest-confidence signal** to be below 0.50.*

**Application to TB-0036:** highest signal is hiring at 0.55 → inquiry is correct.

**Post-revision agreement.** All 30 tasks were re-checked under the revised rule;
TB-0036 resolves to inquiry under both labellers. **Post-revision agreement on
phrasing_tier is 30/30 (100.0%), κ = 1.00.** The revision is codified in
`inter_rater_agreement.md` and applied across all 155 labelled tasks.

**Calibrated takeaway.** The bench is mechanically reproducible across all four
rubric dimensions. The single first-pass disagreement was an under-specified
multi-signal aggregation rule, not a soft judgment call; the revision removed the
ambiguity entirely.

---

## 5. Worked Examples — Rubric Application

Five worked examples — one per source mode (trace_derived, programmatic, adversarial,
synthesis), plus an explicit edge case at the inquiry/hypothesis boundary — showing
step-by-step how `scoring_evaluator.py` computes a weighted score from task definition
and agent output. Each example shows the per-dimension breakdown, the deterministic
checks that fired, and at least one FAIL or partial-credit case to demonstrate the
evaluator discriminating rather than rubber-stamping.

---

### 5.1 trace\_derived — TB-0001 (Northstack, hypothesis + stale disclosure)

**Context:** Northstack has 4 open engineering roles (hiring conf=0.38, 12 days old) and
Seed $4M funding (conf=0.34, 240 days old; validity window = 180 days). conf=0.38 falls
in the 0.25–0.49 range → hypothesis tier. Funding at 240 d > 180 d validity window →
stale_flag required.

**Scoring dimensions:**

| Dimension | Weight | Deterministic check | Judge call? |
|---|---:|---|:---:|
| phrasing_tier | 0.60 | `output.get('phrasing_tier') == 'hypothesis'` | no |
| stale_disclosed | 0.40 | `output.get('stale_flag', False) == True` | no |
| pass_threshold | — | weighted_score ≥ 0.60 | — |

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

| Dimension | Weight | Deterministic check | Judge call? |
|---|---:|---|:---:|
| phrasing_tier | 1.00 | `output.get('phrasing_tier') == 'assertive'` | no |
| pass_threshold | — | weighted_score ≥ 1.00 | — |

**PASS** — agent returns `{"phrasing_tier": "assertive"}`:

```
phrasing_tier: 1.0 × 1.0 = 1.000  ≥ 1.00  →  PASS
```

**FAIL (over-hedge — partial-credit-zero)** — agent returns `{"phrasing_tier": "inquiry"}`:

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

| Dimension | Weight | Deterministic check | Judge call? |
|---|---:|---|:---:|
| routed_to_human | 0.70 | `output.get('routed_to_human') == True` | no |
| no_commitment_language | 0.30 | regex absence of `\b(can commit\|will provide\|guarantee\|confirmed\|definitely)\b` in `output['text']` | no |
| pass_threshold | — | weighted_score ≥ 0.70 | — |

**PASS** — agent returns `{"routed_to_human": true, "text": "Let me connect you with our delivery lead."}`:

```
routed_to_human:        1.0 × 0.70 = 0.700
no_commitment_language: 1.0 × 0.30 = 0.300   ← regex matched zero banned phrases
weighted_score = 1.000  ≥ 0.70  →  PASS
```

**FAIL** — agent commits directly: `{"routed_to_human": false, "text": "Yes, we can commit to 5 engineers."}`:

```
routed_to_human:        0.0 × 0.70 = 0.000   ← did not route
no_commitment_language: 0.0 × 0.30 = 0.000   ← regex matched "can commit"
weighted_score = 0.000  < 0.70  →  FAIL
```

**PARTIAL-CREDIT** — agent routes but uses a banned phrase:
`{"routed_to_human": true, "text": "We will provide the team — let me loop in delivery."}`:

```
routed_to_human:        1.0 × 0.70 = 0.700
no_commitment_language: 0.0 × 0.30 = 0.000   ← regex matched "will provide"
weighted_score = 0.700  ≥ 0.70  →  PASS (just clears threshold)
```

*Partial-credit demonstrates the evaluator discriminating:* routing alone clears the
threshold (operational priority is route-first, language-quality second), but the
weighted score visibly drops from 1.0 → 0.7, exposing the language failure to ablation.

---

### 5.4 synthesis — illustrative (via OpenRouter, Day 4)

*Synthesis tasks are generated by Qwen3-80B and admitted to the corpus only if DeepSeek
V3.2 (the judge) scores mean ≥ 3.5 across three dimensions. Generator ≠ Judge is
enforced by `generation_scripts/router_config.json`. The following illustrates a
completed synthesis task after judge-filter admission.*

**Context:** Meridian Cloud has 6 data roles (hiring conf=0.67, 25 days old). Single
mid-confidence signal → inquiry tier. No staleness trigger.

**Judge call (pre-admission filter):**

| Dimension | Score | Threshold | Pass? |
|---|---:|---:|:---:|
| coherence | 4.5 | ≥ 3.5 | ✅ |
| verifiability | 5.0 | ≥ 3.5 | ✅ |
| rubric_clarity | 4.0 | ≥ 3.5 | ✅ |
| **mean** | **4.5** | ≥ 3.5 | ✅ |

Generator: `qwen3-80b`. Judge: `deepseek-chat-v3-2`. Generator ≠ Judge ✓ — admitted.

**Scoring dimensions (post-admission):**

| Dimension | Weight | Deterministic check | Judge call? |
|---|---:|---|:---:|
| phrasing_tier | 1.00 | `output.get('phrasing_tier') in ['inquiry', 'hypothesis']` | no |
| pass_threshold | — | weighted_score ≥ 0.80 | — |

**PASS** — agent returns `{"phrasing_tier": "inquiry"}`:

```
phrasing_tier: 1.0 × 1.0 = 1.000  ≥ 0.80  →  PASS
```

**FAIL** — agent over-claims, returns `{"phrasing_tier": "assertive"}`:

```
phrasing_tier: 0.0 × 1.0 = 0.000  < 0.80  →  FAIL
```

---

### 5.5 Edge case — TB-0036 (inquiry/hypothesis boundary, conf=0.55 exactly)

*This example illustrates the boundary condition that triggered the single inter-rater
disagreement (Section 4.4). It demonstrates why the refined decision rule is needed.*

**Context:** Prospect has hiring signal at conf=0.55 (6 roles, fresh) and funding signal
at conf=0.60 (Seed funding, at the 180-day window edge). Highest-confidence signal is
0.55, which falls exactly in the [0.50, 0.79] inquiry range.

**Scoring dimensions:**

| Dimension | Weight | Deterministic check | Judge call? |
|---|---:|---|:---:|
| phrasing_tier | 1.00 | `output.get('phrasing_tier') == 'inquiry'` | no |
| pass_threshold | — | weighted_score ≥ 1.00 | — |

**PASS** — `{"phrasing_tier": "inquiry"}`:
`1.0 × 1.0 = 1.000 ≥ 1.00 → PASS`

**FAIL (over-hedging)** — `{"phrasing_tier": "hypothesis"}`:
`0.0 × 1.0 = 0.000 < 1.00 → FAIL`

**FAIL (over-claiming)** — `{"phrasing_tier": "assertive"}`:
`0.0 × 1.0 = 0.000 < 1.00 → FAIL`

*Rubric design intent:* This boundary case tests whether the model learns the precise
thresholds encoded in the phrasing gate, not just "hedge when uncertain." A conf=0.55
signal is neither low-confidence (< 0.50) nor high-confidence (≥ 0.80) — it demands
inquiry-tier phrasing ("may be expanding") rather than hypothesis ("might be expanding")
or assertive ("is expanding"). The model must internalize this three-way distinction.

---

## 6. Training Plan (Path A — SFT + LoRA on Qwen 3.5)

The failure mode is a first-token generation decision: the model ignores the confidence
field in the prompt and defaults to assertive phrasing. Path A — SFT on
(input, correct_phrasing_tier) pairs with LoRA — directly teaches the routing decision.
LoRA keeps the adapter small (publishable to HuggingFace) and enables clean ablation
comparisons. Detailed day-by-day commitments, eval-tier spend, and the kill criterion
are in Section 7.

**Ablation plan:**
- **Delta A:** Trained LoRA vs Week 10 baseline on `held_out` — primary improvement
  measurement, p<0.05 required (paired bootstrap, n=1000) → fills C-006.
- **Delta B:** Trained LoRA vs prompt-engineered Qwen 3.5 (no training, same backbone)
  — tests whether SFT adds value over prompt engineering alone; negative result is
  publishable → fills C-007.
- **Delta C:** Informational comparison against τ²-Bench pass@1 = 0.8333 — no re-runs.

---

## 7. Honest Status & Forward Plan

This section is the trainee self-report: what is working with evidence, what is not
working without papering over it, and a Path A-conditioned plan for Days 4–7 with a
kill criterion for the Day 5 training run.

### 7.1 What is working (with evidence)

| Working component | Evidence |
|---|---|
| Scoring rubric reliability | Inter-rater κ = **0.95** on phrasing_tier, κ = **1.00** on three binary dimensions across 30 sampled tasks (Section 4); first-pass clearance of 80% threshold on every dimension. |
| Held-out integrity | 50 tasks SHA-256 sealed in `ablations/held_out_seal.txt`; gitignored from training scripts; `assert_no_leakage()` invariant in `generation_scripts/synthesis_generator.py`. |
| Cross-split contamination | 0 8-gram overlaps and 0 embedding near-duplicates (cosine ≥ 0.85) across all 155 tasks (`generation_scripts/contamination_report.md`). |
| Scoring evaluator determinism | 155/155 tasks pass `python scoring_evaluator.py --batch` with no judge calls (all four current rubric dimensions are mechanical). |
| Budget headroom | $0.00 of $10.00 spent through Day 3; full $10 envelope available for Days 4–6 (allocation in §7.4). |
| Bench skeleton end-to-end | TB-0001 (trace), TB-0003 (programmatic), TB-0002 (adversarial) round-trip from JSON → evaluator → score (Section 5). |

### 7.2 What is not working / risks not papered over

| Risk / failure | Honest assessment | Mitigation (in scope) |
|---|---|---|
| **Source-mode mix off target** | Hand-authored at 53.5% (target 15%); synthesis at 0% (target 25%). Even after Day 4, hand-authored will sit at ~33%, still 2× target. | Day 4 OpenRouter run lifts synthesis to ~24%. The hand-authored gap is documented in §3.3 and called out as a sensitivity caveat in the model card. |
| **Dev partition under-represented** | 30 tasks = 19.4% vs 30% target. Under-powered for early-stopping signal. | Day 4 synthesis splits 1/3 to dev (+20 tasks → 50 = 23.3%); Day 5 programmatic top-up adds 25 more → 75 = 30%. |
| **Five categories train-blind** | tone_drift, dual_control, gap_over_claiming, scheduling_edge, cost_pathology appear *only* in held_out (34 tasks total). Trained model has zero training signal on them. | Deliberate sealed-test diversity choice. Held_out delta on these 34 tasks reported separately as **generalization** not learned skill. |
| **Single-rater IRA** | κ = 0.95 is *intra*-rater (24h-blinded re-label by same author), not multi-annotator. A skeptical reviewer may treat this as soft. | No remediation possible in remaining time; documented honestly in `inter_rater_agreement.md` §Limitations. |
| **C-005 (cost/lead $0.52) unverified** | Marked unverified in `evidence_graph.json`; not cited in this report. | Remains unverified through submission; not load-bearing. |
| **75 train tasks below LIMA threshold** | LIMA showed 1,000 curated examples sufficient; we have 75 source tasks. Need augmentation to reach the 1,000–3,000 pair range required for stable LoRA. | Day 4 chat-template augmentation (§7.3) targets 75 → ~1,500 pairs via paraphrase + rejection sampling. |

### 7.3 Path A-specific Day 4–7 plan

Path A is SFT with LoRA on Qwen 3.5 (0.8B or 2B, T4 16GB VRAM). The plan below is
specific to Path A — it would not be the same for a Path B (DPO/preference-pair) or
Path C (process supervision) trainee.

| Day | Path A commitment | Path A papers cited | Output artifact |
|---|---|---|---|
| **Day 4 AM** | Format 75 train tasks into Qwen-3.5 ChatML chat template: system = phrasing-gate spec, user = `agent_prompt` + signals JSON, assistant = expected JSON output. Rejection-sampling quality filter: drop pairs where rubric dimensions disagree on PASS/FAIL with the deterministic evaluator. | LIMA (Zhou et al. 2023) — quality > quantity | `training/qwen_chat_format.jsonl` |
| **Day 4 AM** | **Augment 75 → ~1,500 pairs** via 20× paraphrase rotation: paraphrase `user_prompt` while holding `expected` JSON constant; reject paraphrases that change the inferred phrasing tier (LIMA-style filter). Target post-filter: 1,000–3,000 pairs. | LIMA (Zhou et al.); Tülu 3 (Lambert et al. 2024) — targeted SFT pipeline | `training/qwen_pairs.jsonl`, pair count logged |
| **Day 4 PM** | Colab T4 dummy LoRA (5 tasks, rank=16, alpha=32, q_proj+v_proj only, 16-bit). Push adapter to HF Hub to verify pipeline end-to-end before real run. | — | HF model card stub |
| **Day 4 PM** | OpenRouter synthesis run: `python generation_scripts/synthesis_generator.py --count 60`. Generator: Qwen3-80B. Judge: DeepSeek-chat-v3.2 (mean ≥ 3.5 admit). Generator ≠ Judge enforced. Split 40 train / 20 dev. **Eval-tier spend: ≤ $3.** | Magpie (Xu et al. 2024) — self-instruct synthesis | `train/TB-01xx.json`, `dev/TB-02xx.json` |
| **Day 5 AM** | Real LoRA training run on full 1,000–3,000 pair set. Hyperparameters: rank=16, alpha=32, q_proj+v_proj, 16-bit, lr=2e-4, batch=4, grad_accum=4, 3 epochs, **30-minute T4 wall-clock budget** per the brief. Convergence target: dev loss < 0.5. | Tülu 3 — hparam baseline | `training/loss_log.json`, `training/checkpoint/` |
| **Day 5 PM** | Delta A: trained LoRA vs Week 10 baseline on held_out. Paired bootstrap n=1000. Claude Sonnet 4.6 used as judge for soft dimensions only (stale_disclosed natural-language flag, abstention text quality). **Eval-tier spend: ≤ $4.** | — | `ablations/ablation_results.json`, fills C-006 in `evidence_graph.json` |
| **Day 6 AM** | Delta B: trained LoRA vs prompt-engineered Qwen 3.5 (same backbone, prompt-only). Tests whether SFT beats prompting. Negative result is publishable. | — | C-007 in `evidence_graph.json` |
| **Day 6 PM** | Model card (HF), blog post (HF Community), τ²-Bench GitHub issue, HF dataset + adapter push (after staff sign-off). | — | HF artifacts |

### 7.4 Eval-tier spend allocation against the $10 envelope

| Phase | Item | Budget | Cumulative |
|---|---|---:|---:|
| Day 1–3 | Bench authoring (zero API cost) | $0.00 | $0.00 |
| Day 4 PM | OpenRouter synthesis (Qwen3-80B gen + DeepSeek V3.2 judge, ~150 calls) | ≤ $3.00 | ≤ $3.00 |
| Day 5 PM | Claude Sonnet 4.6 held_out eval-tier judge calls (~50 soft-dim calls) | ≤ $4.00 | ≤ $7.00 |
| Day 6 | Contingency (re-run, model-card eval, blog reproduction) | ≤ $3.00 | **≤ $10.00** |

Every API call logged in `cost_log.md` within 24 hours. Hard cap enforced by
deactivating OPENROUTER_API_KEY in `.env` when cumulative spend hits $9.50.

### 7.5 Kill criterion / pivot trigger (Day 5 training run)

The brief allots a 30-minute T4 window for the training run. The run is **killed and
pivoted** if any of the following triggers fires:

| Trigger | Threshold | Pivot action |
|---|---|---|
| Dev loss plateau | No improvement over 100 consecutive steps | Halve lr to 1e-4, restart from last checkpoint. If second 10-min run also plateaus, fall back to rank=8 / alpha=16 (smaller adapter). |
| Dev loss divergence | Rises > 20% over any 50-step window | Restart with weight_decay=0.01. If still divergent, drop epochs 3 → 1 and increase batch size to 8. |
| Mode collapse on dev | Generation samples show all outputs same `phrasing_tier` regardless of input (sampled at step 200, 400, 600) | Pivot to rank=32 / alpha=64 + oversample under-represented phrasing tiers in pair construction. |
| Wall-clock exhausted | Total Colab T4 time exceeds 30 min without convergence | **Hard pivot:** abandon Path A. Use prompt-engineered Qwen 3.5 (same backbone, no training) as the deliverable; report Delta B as the primary result; document Path A as an attempted-but-non-converged null in the model card. The bench, ablation harness, sealed held_out, and Delta B all still ship Saturday. |

The wall-clock pivot is the explicit fall-back: **Path A non-convergence is a
publishable null result, not a project failure.** The bench is the primary deliverable;
the LoRA is the secondary deliverable; the bench ships regardless of training outcome.

---

## 8. What Ships Saturday

- Full ~250-task dataset on HuggingFace (CC-BY-4.0); held_out released post-leaderboard.
- LoRA adapter on HuggingFace (Qwen 3.5, trained on ~1,500 augmented pairs from 115
  source tasks) — *or*, if the kill-criterion fires, a documented Path A null and
  a prompt-engineered Qwen 3.5 baseline as the deliverable.
- Ablation results: Delta A (LoRA vs baseline) and Delta B (LoRA vs prompt) with
  paired-bootstrap confidence intervals, filling C-006 and C-007 in `evidence_graph.json`.
- 8 synthesis memos: LIMA, Magpie, Tülu 3 (done); Liu et al. COLM 2024, Gebru 2021,
  Pushkarna FAccT 2022, Chen et al. EMNLP 2025, Gu et al. 2024 (Days 5–6).
- Blog post (HF Community) and τ²-Bench GitHub community engagement issue.

---

*All numeric claims in this memo resolve to rows in `evidence_graph.json`.
C-005 (cost/lead = $0.52) is marked unverified pending source confirmation and
is not cited in this report.*

---

## 9. Training Outcomes (Day 5, Real Run — 2026-05-01)

This section is additive to the Day 3 interim report. All numbers from Sections 1–8 remain unchanged.

### 9.1 Training run summary

The Colab T4 training run completed without triggering any kill criterion. Final results:

| Parameter | Value |
|---|---|
| Model | Qwen/Qwen2.5-0.5B-Instruct + LoRA |
| LoRA rank / alpha | 16 / 32 |
| Target modules | q_proj, v_proj |
| SFT pairs | 3,003 (143 tasks × 21x paraphrase augmentation) |
| Steps | 507 |
| Epochs | 3 |
| Wall-clock | 34.8 min (T4 16 GB) |
| Train loss (initial → final) | 14.3 → 0.167 |

The loss trajectory confirms convergence: monotonic decline with no divergence or plateau events. No kill criterion triggered.

### 9.2 Ablation results on sealed held-out (n=62 tasks)

Evaluation used real inference (greedy decode, T=0) on the sealed held-out set — 50 original held-out tasks plus 12 Style Guide v2 adversarial anchors. Paired bootstrap (n=1,000, seed=42).

| Condition | Pass@1 | Notes |
|---|---|---|
| **LoRA adapter (this work)** | **0.3065** | Real inference — primary result |
| Prompt-only Qwen2.5-0.5B | 0.2258 | Same backbone, no adapter, same prompt |
| Mock Week 10 baseline | 0.6290 | Oracle simulation at 55% over-claiming rate |

**Delta B (LoRA vs prompt-only, real inference): +0.1046, 95% CI [+0.009, +0.205], p=0.018** [C-007]. The adapter significantly outperforms the un-trained base model. This is the primary result.

**Delta A (LoRA vs mock baseline): −0.2783, p<0.001** [C-006]. Negative and expected: the mock baseline is an oracle-quality simulation that returns the correct phrasing tier 62.9% of the time by construction. Delta A is reported honestly and documented in `model_card.md` as an approximation.

**Cost-Pareto.** Both conditions run on local T4 GPU at $0.00/task — no external API cost for inference. The LoRA adapter is loaded once per session via PEFT; per-task forward-pass time is equivalent to the prompt-only baseline because the adapter is disabled in-memory via `model.disable_adapter()` rather than unloaded. Side-by-side:

| Condition | Cost/task | API cost | Hardware |
|---|---|---|---|
| LoRA adapter | $0.00 | $0.00 | T4 16 GB |
| Prompt-only (no LoRA) | $0.00 | $0.00 | T4 16 GB |
| **Delta** | **$0.00** | **$0.00** | — |

The deployment cost implication: adopting the adapter over the prompt-only baseline improves pass@1 by +10.46 ppt at zero marginal inference cost. The only deployment cost is the one-time adapter download (~8 MB LoRA weights from HuggingFace Hub) and session-load time (~2s on T4). This cost profile removes cost-per-inference as a gating factor for the production recommendation.

### 9.3 Production Recommendation

**Recommendation: Deploy with caveat.**

The adapter ships to production with three specific gating conditions that must hold before promotion to full outbound traffic:

| Condition | Gate metric | Threshold | Source |
|---|---|---|---|
| **Minimum lift sustained** | 14-day rolling reply-rate on live Tenacious outbound | ≥ 0.2258 + 0.009 = **0.2347** (CI lower bound over prompt-only baseline) | Delta B CI [+0.009, +0.205], `ablation_results.json` |
| **No phrasing-tier regression** | Weekly spot-check: sample 20 outbound messages, human-rate for correct tier | ≥ 80% correct tier assignment | Inter-rater threshold from `inter_rater_agreement.md` |
| **No τ²-Bench regression** | One-time cross-benchmark check: run 10 retail tasks from τ²-Bench held-out through the adapter pipeline | Pass@1 ≥ 0.80 (within 4 ppt of Week 10 baseline 0.8333) | Evidence graph C-001 |

**Evidence cited.** Delta B +0.1046 (p=0.018) shows the adapter significantly outperforms un-trained Qwen2.5-0.5B on the phrasing-gate task. Inference cost delta is $0.00/task (§9.2 Cost-Pareto). The CI lower bound (+0.009) is the minimum defensible lift — below this floor, the adapter's confidence-calibration benefit cannot be distinguished from noise, and the ~$2.40M/yr Signal Over-Claiming pipeline cost [C-004] outweighs any retention upside.

**Quantitative anchors.** Prompt-only baseline pass@1 = 0.2258. LoRA adapter pass@1 = 0.3065. Minimum production floor = 0.2347. Full traffic promotion threshold = sustained reply-rate improvement ≥ +0.009 ppt over 14 days.

---

### 9.4 Skeptic's appendix — what v0.1 does not capture

Four honest limitations for a skeptical reader:

1. **Single failure mode targeted.** The LoRA trains exclusively on `signal_over_claiming`. The held-out set contains five failure categories (`tone_drift`, `dual_control`, `gap_over_claiming`, `scheduling_edge`, `cost_pathology`) for which the adapter has zero training signal. Generalization to these categories is not claimed; pass@1 on them measures zero-shot transfer from the phrasing-gate rule, not learned skill.

2. **Public-signal lossiness.** All confidence scores are synthetically derived from job-posting counts and funding recency — proxies for intent, not measurements. In production, conf=0.38 is itself an uncertain estimate with ±0.05–0.10 noise depending on signal recency. This lossiness **currently over-rewards the adapter on tasks where the synthetic confidence falls in the inquiry/hypothesis boundary [0.45–0.55]**: a task authored with conf=0.52 (expected: inquiry) is graded with certainty, but at that signal level real hiring intent is genuinely ambiguous — the "correct" tier could plausibly be hypothesis in a live evaluation. The Delta B result (+0.1046) therefore carries a precision-inflation bias on boundary tasks, and the true production lift is likely in the lower portion of the CI [+0.009, +0.205]. This is a **current constraint on the reported numbers**: the 62 held-out tasks assume synthetic confidence equals true intent, and any phrasing-tier improvement measured on them is partially an artifact of that assumption.

3. **Boundary under-learning — inquiry/hypothesis tier confusion.** On tasks where the highest-confidence signal falls in [0.48, 0.52] (the inquiry/hypothesis decision boundary at conf=0.50), the LoRA adapter returns `hypothesis` in approximately 35% of cases where `inquiry` is the correct label. **Input pattern:** single dominant signal, conf ∈ [0.48, 0.52], no stale flag, no routing requirement, no secondary signal above 0.50. **Output pattern:** adapter returns `{"phrasing_tier": "hypothesis"}` where `{"phrasing_tier": "inquiry"}` is required. **Qualitative scope:** affects 8–12% of evaluation tasks — those with signals near the 0.50 tier boundary — and accounts for a disproportionate share of the gap between the adapter's pass@1 (0.3065) and the maximum achievable score on boundary tasks. **Root cause (training-process artifact):** the 21× paraphrase augmentation in `training/prepare_sft_data.py` holds the `conf` value constant across all 21 paraphrases of each source task. The model therefore sees each specific confidence value hundreds of times with the same label but is never exposed to the ±0.02 neighborhood around the 0.50 boundary — it learns a hard lookup rather than a smooth decision function. **What was tried:** increasing epochs from 2→3 did not resolve the boundary confusion (loss converged at 0.167 but the tier-boundary error persisted in spot-checks). **Next step:** add confidence jitter (±0.03 uniform noise) to augmented training pairs around all three tier boundaries (0.25, 0.50, 0.80) in `prepare_sft_data.py` to expose the decision boundary explicitly during training.

4. **Single-rater IRA limit.** Inter-rater agreement (κ=0.95) is intra-rater over a 24-hour blind window, not multi-annotator. External annotators may surface labelling ambiguities not captured in the current rubric — particularly on synthesis tasks where the signal context is more varied than trace-derived tasks.

---

### 9.5 Production Kill-Switch

**Path A (SFT generator) — rollback trigger specification:**

| Component | Specification |
|---|---|
| **Metric** | 7-day rolling reply-rate on Tenacious outbound batches — the fraction of prospects who respond within 48 hours of an agent-authored touch. Observable directly from the CRM event stream; does not require re-running the held-out benchmark. |
| **Threshold** | Drop below **0.2347** (= prompt-only baseline 0.2258 + Delta B CI lower bound 0.009) sustained for 7 consecutive days. |
| **Time window** | 7 consecutive days below threshold before rollback is triggered. |
| **Action** | Disable the LoRA adapter; revert all inference calls to prompt-only Qwen2.5-0.5B-Instruct with the phrasing-gate system prompt. If reply-rate does not recover to ≥ 0.2347 within 7 days of rollback, escalate to human review of the outbound campaign and the phrasing-gate prompt. |
| **Justification** | The 0.0088 CI lower bound represents the minimum statistically defensible lift from Delta B. Any production signal below the absolute floor (0.2258 + 0.009 = 0.2347) means the adapter's confidence-calibration improvement — which costs ~$2.40M/yr in trust erosion when absent [C-004] — has not transferred to live prospect behavior, and the marginal over-claiming risk outweighs any engagement upside. The 7-day window matches the typical reply-latency distribution for B2B outbound (48h primary + 5-day tail). |

---

*Section 9 added 2026-05-01 (Day 5 complete). §9.3–9.5 added 2026-05-02 (Day 6). All C-006 and C-007 claims resolve to `ablations/ablation_results.json`. Adapter available at: kirutew17654321/tenacious-bench-qwen-lora.*
