# Tenacious-Bench — Week 11: Sales Agent Evaluation & Alignment

**Project:** Ground Truth — Building the Sales Evaluation Bench and Aligning the Conversion Engine  
**Author:** Kirubel Tewodros  
**Cohort:** 10 Academy TRP1  
**Status:** 🟢 Day 3 complete — 155 tasks authored, held_out sealed, LoRA training Day 4

---

## What This Is

A custom evaluation benchmark (Tenacious-Bench v0.1) for the Week 10 Conversion Engine AI sales agent, plus a LoRA adapter trained to fix the highest-ROI failure mode: **Signal Over-Claiming** (P-006–P-010).

**Target failure:** The agent uses assertive language about prospect signals when the underlying evidence is below the confidence threshold. Trigger rate: 0.55. Annual pipeline cost: ~$2.40M per 1,000 touches.

**Training path:** Path A — SFT on Qwen 3.5 (backbone TBD: 0.8B/2B/4B) with LoRA for the phrasing-gate generation component.

---

## Quick Start

**Requirements:** Python 3.9+

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Validate the schema + 3 dummy tasks
python scoring_evaluator.py --validate

# Score a single task
python scoring_evaluator.py --task tenacious_bench_v0.1/train/TB-0001.json --output agent_output.json

# Batch score a split
python scoring_evaluator.py --batch tenacious_bench_v0.1/train/ --outputs outputs/
```

**Key dependencies:** `sentence-transformers`, `transformers`, `peft`, `trl`, `datasets`,
`huggingface-hub`, `openai` (OpenRouter), `pytest`

---

## Repo Structure

```
seeds/                          # Read-only Week 10 inputs
    trace_log.jsonl             # 30 τ²-Bench run traces (seed for trace-derived tasks)
    probe_library.json/.md      # 33 adversarial probes across 10 categories
    failure_taxonomy.md         # 10 failure categories with trigger rates + costs
    target_failure_mode.md      # Signal Over-Claiming selection rationale

tenacious_bench_v0.1/
    train/                      # 50% of tasks (~120–150)
    dev/                        # 30% of tasks (~75–90)
    held_out/                   # 20% sealed (~50–60) — NEVER used in training

generation_scripts/             # Reproducible: model routes, judge prompts, dedup
training/                       # LoRA training script, hyperparameters, loss logs
ablations/                      # ablation_results.json, held_out_traces.jsonl, stats
synthesis_memos/                # One memo per required paper

schema.json                     # Machine-verifiable task schema + 3 examples
scoring_evaluator.py            # (task, agent_output) → float score
audit_memo.md                   # ≤600 words: what τ²-Bench misses for Tenacious
methodology.md                  # Path declaration, justification, partitioning
methodology_rationale.md        # Paper citations + ≥3 Week 10 trace IDs
datasheet.md                    # Gebru 7-section + Pushkarna layered detail
inter_rater_agreement.md        # 30-task hand-label, ≥80% agreement required
evidence_graph.json             # Every numeric memo claim → source
cost_log.md                     # Running cost log (target: ≤$10 total)
memo.pdf                        # 2-page executive memo (generated at submission)
```

---

## Deliverable Deadlines

| Deadline | UTC | What ships |
|---|---|---|
| Interim | Wednesday 21:00 | README, audit_memo, schema, scoring_evaluator, bench v0.1 skeleton, datasheet, methodology, generation_scripts, inter_rater_agreement, PDF report |
| Final | Saturday 21:00 | + training/, ablations/, model_card, evidence_graph, all synthesis memos, public HF artifacts |

---

## Key Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| [Audit Memo](./audit_memo.md) | `audit_memo.md` | What τ²-Bench misses and why Signal Over-Claiming is the target |
| [Datasheet](./datasheet.md) | `datasheet.md` | Gebru 7-section + Pushkarna layered dataset documentation |
| [Methodology](./methodology.md) | `methodology.md` | Path A declaration, partitioning, contamination protocol |
| [Synthesis Memos](./synthesis_memos/) | `synthesis_memos/` | Critical engagement memos for required reading papers |
| [Schema](./schema.json) | `schema.json` | Task schema + 3 example tasks |
| [Evidence Graph](./evidence_graph.json) | `evidence_graph.json` | Provenance for every numeric claim in memo and blog |
| [Cost Log](./cost_log.md) | `cost_log.md` | Running API cost log (hard cap: $10) |

---

## What's Next (Remaining Work)

| Deadline | Item |
|---|---|
| **Wednesday 21:00 UTC** | ~~README~~, ~~audit_memo~~, ~~schema~~, ~~scoring_evaluator~~, ~~dataset skeleton~~, ~~datasheet~~, ~~methodology~~, ~~generation_scripts~~, ~~inter_rater_agreement~~, memo.pdf |
| **Day 4** | Colab T4 — 5-task dummy LoRA pipeline test → real 125-task training run on Qwen 3.5 |
| **Day 4–5** | OpenRouter synthesis: 60 tasks (Qwen3-80B generates, DeepSeek V3.2 judges) to reach 250 total |
| **Day 5** | Delta A/B ablations on held_out; fill `ablations/ablation_results.json` + C-006/C-007 |
| **Day 5–6** | Write remaining 6 synthesis memos |
| **Saturday 21:00 UTC** | HuggingFace dataset + model push, model_card, blog post, τ²-Bench GitHub issue |

---

## Key Numbers (Week 10 Baseline)

| Metric | Value |
|---|---|
| τ²-Bench pass@1 | 0.8333 (p=0.009, from Week 10 report) |
| Signal Over-Claiming trigger rate | 0.55 (P-006–P-010) |
| Cost per qualified lead | $0.52 |
| Stall rate | 11.1% |
| Target failure annual cost | ~$2.40M/1,000 touches |

---

## Public Artifacts (populated at final submission)

- HuggingFace dataset: _TBD_
- HuggingFace model (LoRA adapter): _TBD_
- Blog post: _TBD_
- Community engagement: _TBD_

---

## Cost Log Summary

See [cost_log.md](cost_log.md) for running totals. Hard cap: **$10**.
