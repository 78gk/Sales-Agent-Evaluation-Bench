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
260 tasks (Day 5 final, v0.1.1 with Style-Guide anchors added 2026-05-01); target 200–300 achieved.
Current split: 143 train / 55 dev / 62 held_out (sealed).

**Authoring mode distribution (final):**  

| Mode | Count | % | Notes |
|---|---|---|---|
| adversarial | 83 | 32% | Hand-authored high-risk boundary cases (18 train + 15 dev + 50 held_out) |
| synthesis | 81 | 31% | Multi-LLM synthesis, Qwen/Qwen3-235b-a22b → DeepSeek/deepseek-chat-v3-0324 (train + dev) |
| programmatic | 38 | 15% | Parameter sweeps (24 train + 14 dev) |
| trace_derived | 34 | 13% | Derived from seeds/trace_log.jsonl (33 train + 1 dev) |
| **hand_authored (Style Guide v2 anchors)** | **24** | **9%** | **TB-G001–TB-G024 — 12 GOOD drafts (train) + 12 BAD drafts (held_out, labels = correct behavior). Added v0.1.1 on 2026-05-01 after instructor-provided `Tenacious Style Guide v2.docx` arrived. Provenance: `metadata.style_guide_anchor` names the source draft.** |
| **Total** | **260** | **100%** | |

**v0.1.1 Amendment Note (2026-05-01):** The Tenacious Style Guide v2 document, named in the challenge brief as canonical Tenacious-rubric input, arrived at the end of Day 5. To preserve traceability rather than retro-relabel the existing corpus, the 24 hand-labeled drafts in the guide were added as a self-contained supplement (TB-G001–TB-G024), and the scoring evaluator was extended with a banned-phrase regex check (`banned_phrase_check()` in `scoring_evaluator.py`) covering the 23 phrases enumerated in the guide. The existing 236 tasks remain unchanged; a v0.2 full re-audit against the 5-tone-marker framework is documented as future work in the model card limitations section.

**Per-Authoring-Mode Descriptions:**

*Trace-derived tasks* are adapted from specific Week 10 τ²-Bench simulation runs in `seeds/trace_log.jsonl`. Each task maps one failed or passed trial to a Tenacious-Bench evaluation task, preserving the signal context and agent challenge but reframing the evaluation around phrasing-tier correctness. Example: Trace sim_a553180f (Week 10 task 11, reward=0.0) becomes Tenacious-Bench TB-0011: given a company with hiring_confidence=0.38, the task requires the agent to use hypothesis-tier phrasing (not assertive), demonstrating signal-respect rather than task-completion accuracy.

*Programmatic tasks* are generated via parameter sweeps: for each combination of (signal_type ∈ {funding, hiring, layoffs, leadership}, confidence ∈ {0.1, 0.3, 0.5, 0.7, 0.9}, evidence_count ∈ {1, 2, 3}), a task template is instantiated with randomized company names and prospect contexts. These tasks are deterministic and reproducible. Example: (signal_type=hiring, confidence=0.45, evidence_count=2) generates a task where the agent sees one hiring signal and one funding signal, both at 0.45 confidence — testing the inquiry vs. hypothesis tier boundary.

*Synthesis tasks* are generated on-the-fly via multi-LLM synthesis: Qwen/Qwen3-235b-a22b generates candidate tasks given a failure category and schema constraints; DeepSeek/deepseek-chat-v3-0324 (a separate model) evaluates each candidate on three dimensions (coherence, verifiability, rubric_clarity) using `generation_scripts/judge_prompt.txt`; tasks scoring ≥3.5 on all dimensions are deduped via 8-gram overlap check and committed. Generator ≠ judge is enforced by assertion in the pipeline. These tasks exhibit higher diversity and more natural language variation than programmatic tasks. Example: a synthesis task might describe a prospect with conflicting signals (positive hiring trend but recent layoff announcement, 3 days old) requiring the agent to reconcile and express appropriate uncertainty.

*Adversarial tasks* are hand-authored against specific probes from `seeds/probe_library.json` to stress-test edge cases: near-threshold confidence values (0.49 vs. 0.51, crossing the inquiry/hypothesis boundary), stale-signal mixtures (two signals valid, one expired), cross-thread entity mentions, and capacity-commitment requests that should trigger abstention. These are authored by the dataset creator (Kirubel Tewodros) with full domain knowledge and represent the most challenging evaluation scenarios.

**Failure category distribution (final):**  

| Category | Count |
|---|---|
| signal_over_claiming | 139 (primary training target) |
| bench_over_commitment | 27 |
| signal_reliability | 15 |
| icp_misclassification | 13 |
| tone_drift | 10 |
| multi_thread_leakage | 8 |
| dual_control | 8 |
| gap_over_claiming | 6 |
| scheduling_edge | 5 |
| cost_pathology | 5 |

**Are there labels?**  
Yes. Each task has machine-verifiable labels: phrasing_tier (4-class), routed_to_human (bool), stale_disclosed (bool), thread_clean (bool).

**Is there information that might be considered sensitive?**  
No. All company names are fictitious (Tenacious, Northstack, Pellucid Bio, SynthCo). No real personal data.

---

## 3. Collection Process

**How was data collected?**  
- trace_derived: adapted from `seeds/trace_log.jsonl` (30 τ²-Bench retail simulation traces)
- programmatic: Python scripts sweep signal confidence (0.1–0.9), signal type, staleness, and evidence count
- synthesis: OpenRouter multi-LLM generation (Qwen/Qwen3-235b-a22b) with cross-model judgment (DeepSeek/deepseek-chat-v3-0324)
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

Tenacious-Bench v0.1 is a 260-task, machine-verifiable evaluation benchmark for AI outbound
sales agents, targeting confidence-calibrated phrasing decisions. It fills four gaps in
τ²-Bench (retail domain) that are directly responsible for the highest-cost failure modes
observed in the Week 10 Tenacious Conversion Engine: Signal Over-Claiming, Bench
Over-Commitment, Multi-Thread Leakage, and Stale-Signal Disclosure. The Tenacious Style Guide v2
(named as canonical Tenacious rubric in the challenge brief) is implemented through (a) a 23-phrase
banned-phrase regex in the scoring evaluator and (b) 24 hand-labeled anchor tasks (TB-G001–TB-G024,
v0.1.1 supplement, 2026-05-01).

### Periscopic Overview

| Attribute | Value |
|---|---|
| Total tasks (final) | 260 (v0.1.1, includes 24 Style-Guide anchor tasks added 2026-05-01) |
| Train / Dev / Held_out split | 143 / 55 / 62 (55% / 21% / 24%); target was 50/30/20 — dev is short of 30% target because synthesis admission rate (≈55% of candidates) yielded fewer tasks than projected; held_out grew from 50 → 62 with v0.1.1 BAD-draft anchor probes |
| Authoring modes | Adversarial (32%), Multi-LLM synthesis (31%), Programmatic (15%), Trace-derived (13%), Hand-authored Style Guide anchors (9%); original planned target was 30/30/25/15 — adversarial is over-represented because the original 50 held_out tasks were all adversarial (by design); v0.1.1 adds 24 Style Guide anchors as a separate hand_authored category |
| Primary failure category | Signal Over-Claiming (139/260 = 53% of tasks) |
| Scoring dimensions | 5 (phrasing_tier, routed_to_human, stale_disclosed, thread_clean, banned_phrases) |
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
