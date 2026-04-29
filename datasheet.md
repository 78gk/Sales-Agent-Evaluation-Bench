# Datasheet for Tenacious-Bench v0.1

*Following Gebru et al. 2021 (Datasheets for Datasets) + Pushkarna & Zaldivar 2022 (Data Cards)*

---

## 1. Motivation

**Why was this dataset created?**  
τ²-Bench (retail domain) does not evaluate confidence-calibrated phrasing, abstention-under-pressure, or cross-thread isolation — the three highest-cost failure modes for Tenacious Consulting's AI outbound sales agent. Tenacious-Bench v0.1 fills that gap with 200–300 machine-verifiable evaluation tasks derived from real agent traces, programmatic signal sweeps, multi-LLM synthesis, and hand-authored adversarial cases.

**Who created it and on whose behalf?**  
Kirubel Tewodros, 10 Academy TRP1 cohort. Created as a course deliverable; not funded by or on behalf of Tenacious Consulting (a fictitious company for the challenge).

**Was there funding?**  
No external funding. LLM API costs capped at $10 (see cost_log.md).

---

## 2. Composition

**What do the instances represent?**  
Each instance is an evaluation task: a prospect context (company signals with confidence scores and age), an agent prompt, expected output fields (phrasing_tier, routed_to_human, stale_disclosed, thread_clean), and a machine-verifiable scoring rubric.

**How many instances?**  
Target: 250 tasks. Split: 125 train / 75 dev / 50 held_out (sealed).

**Authoring mode distribution:**  
- trace_derived: ~30% (derived from Week 10 τ²-Bench run traces)
- programmatic: ~30% (confidence × signal type parameter sweeps)
- synthesis: ~25% (multi-LLM generated, cross-model judged)
- adversarial: ~15% (hand-authored edge cases)

**Failure category distribution (target):**  

| Category | Count |
|---|---|
| signal_over_claiming | ~100 (primary training target) |
| bench_over_commitment | ~40 |
| icp_misclassification | ~30 |
| tone_drift | ~20 |
| other categories | ~60 |

**Are there labels?**  
Yes. Each task has machine-verifiable labels: phrasing_tier (4-class), routed_to_human (bool), stale_disclosed (bool), thread_clean (bool).

**Is there information that might be considered sensitive?**  
No. All company names are fictitious (Tenacious, Northstack, Pellucid Bio, SynthCo). No real personal data.

---

## 3. Collection Process

**How was data collected?**  
- trace_derived: adapted from `seeds/trace_log.jsonl` (30 τ²-Bench retail simulation traces)
- programmatic: Python scripts sweep signal confidence (0.1–0.9), signal type, staleness, and evidence count
- synthesis: OpenRouter multi-LLM generation (Qwen3-80B) with cross-model judgment (DeepSeek V3.2)
- adversarial: hand-authored by Kirubel Tewodros against probe IDs P-006–P-014, P-019–P-020, P-029–P-031

**Who collected the data?**  
Kirubel Tewodros (hand-authored + programmatic). LLM synthesis via OpenRouter APIs.

**Over what timeframe?**  
Days 1–3 of Week 11 (2026-04-29 to 2026-05-01).

**Were workers paid?**  
N/A — solo project.

---

## 4. Preprocessing / Cleaning / Labeling

**Was any preprocessing done?**  
- LLM-as-a-judge filter: all synthesis tasks scored 1–5 on coherence, verifiability, rubric clarity; tasks below threshold (TBD, ~3.5) discarded
- Deduplication: n-gram (8-gram) + embedding cosine (<0.85) checks before sealing held_out
- Contamination: time-shift verification (held_out authored Day 2+, train Day 1)

**Was the raw data saved?**  
Yes. `generation_scripts/` contains all generation logs, judge scores, and dedup results.

**Is the software used available?**  
Yes. `generation_scripts/` + `requirements.txt`.

---

## 5. Uses

**What tasks has the dataset been used for?**  
- LoRA SFT on Qwen 3.5 for phrasing-tier generation (Path A)
- Pass@1 evaluation of the Week 10 baseline agent
- Ablation testing (Delta A, B, C)

**Is there anything about the composition that might affect future uses?**  
Tasks assume the Tenacious Consulting B2B sales context (fictitious). Do not use to evaluate general-purpose customer service agents — the phrasing gate thresholds are domain-specific.

**Are there tasks for which the dataset should not be used?**  
Do not use as a general sales LLM benchmark — it tests one specific failure mode under one company's signal architecture.

---

## 6. Distribution

**How will the dataset be distributed?**  
HuggingFace Hub under CC-BY-4.0. Held-out partition released only after leaderboard publication and program staff sign-off.

**Is the dataset self-contained?**  
Yes. All signal data is synthetic/derived. No external data sources required to run the evaluator.

**What license?**  
CC-BY-4.0. This license was chosen to allow open research reuse and derivative benchmarks
while requiring attribution — appropriate for an academic evaluation dataset where citation
credit matters but broad adoption is desired.

**Have any third-party IP restrictions been identified?**  
No. All company/signal data is fictitious.

---

## 7. Maintenance

**Who maintains the dataset?**  
Kirubel Tewodros. Contact via 10 Academy cohort channels.

**Will the dataset be updated?**  
v0.1 is the submission artifact. Future versions (v0.2+) may expand coverage to additional failure categories.

**Is there a mechanism for others to contribute?**  
GitHub issues on the repo. PRs accepted for additional adversarial tasks after held_out is released.

---

## Pushkarna & Zaldivar — Layered Detail

*Following Pushkarna & Zaldivar, FAccT 2022 — Data Cards: Purposeful and Transparent Dataset
Documentation for Responsible AI*

### Telescopic Overview

Tenacious-Bench v0.1 is a 250-task, machine-verifiable evaluation benchmark for AI outbound
sales agents, targeting confidence-calibrated phrasing decisions. It fills four gaps in
τ²-Bench (retail domain) that are directly responsible for the highest-cost failure modes
observed in the Week 10 Tenacious Conversion Engine: Signal Over-Claiming, Bench
Over-Commitment, Multi-Thread Leakage, and Stale-Signal Disclosure.

### Periscopic Overview

| Attribute | Value |
|---|---|
| Total tasks (target) | 250 |
| Train / Dev / Held_out split | 50% / 30% / 20% |
| Authoring modes | Trace-derived (~30%), Programmatic (~30%), Multi-LLM synthesis (~25%), Adversarial (~15%) |
| Primary failure category | Signal Over-Claiming (~40% of tasks) |
| Scoring dimensions | 4 (phrasing_tier, routed_to_human, stale_disclosed, thread_clean) |
| Pass threshold | ≥0.60 weighted score |
| Intended use | LoRA SFT training + A/B ablation on held_out split |
| Out of scope | General customer service, retail Q&A, non-B2B sales domains |
| Known limitations | Tasks are synthetic/derived; single-author adversarial slice may miss failure modes not anticipated by the author; real prospect diversity not captured |
| Risks | Held_out partition could game leaderboard if released early |
| Mitigation | 3-layer contamination check; held_out gitignored; SHA-256 seal committed before training |

### Microscopic Documentation

**Schema fields (per task):**

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Unique ID, format TB-NNNN |
| `version` | string | Schema version, e.g. "v0.1" |
| `category` | string | Failure category from `seeds/failure_taxonomy.md` |
| `source_mode` | string | trace_derived / programmatic / synthesis / adversarial |
| `seed_trace_id` | string | Source trace from `seeds/trace_log.jsonl` (trace_derived only) |
| `input.prospect_context` | object | Company signals with confidence scores and age_days |
| `input.agent_prompt` | string | The prompt presented to the agent |
| `expected.phrasing_tier` | string | assertive / inquiry / hypothesis / abstention |
| `expected.routed_to_human` | boolean | Whether human handoff is required |
| `expected.stale_disclosed` | boolean | Whether staleness must be surfaced |
| `scoring.dimensions` | array | Per-dimension weight + machine-verifiable check expression |
| `scoring.pass_threshold` | float | Minimum weighted score to pass (default 0.60) |
| `metadata.authored_by` | string | Author name |
| `metadata.authored_date` | string | ISO date of authoring |

**Example record (abbreviated):**
```json
{
  "task_id": "TB-0001",
  "category": "signal_over_claiming",
  "source_mode": "trace_derived",
  "expected": { "phrasing_tier": "hypothesis", "stale_disclosed": true },
  "scoring": { "pass_threshold": 0.60 }
}
```
