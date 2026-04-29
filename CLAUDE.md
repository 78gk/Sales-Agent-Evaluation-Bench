# CLAUDE.md — Tenacious-Bench / Week 11

## What this project is

Week 11 of 10 Academy TRP1. Build **Tenacious-Bench v0.1** — a custom evaluation dataset (200–300 tasks) for the Week 10 AI outbound sales agent — then train a **LoRA adapter** (Path A, SFT) on Qwen 3.5 to fix the highest-ROI failure mode.

**This repo lives at:** `c:\projects\10\week-11\`  
**Week 10 repo (read-only reference):** `c:\projects\10\week-10\`

---

## Critical context — do not re-derive

**Target failure mode:** Signal Over-Claiming (P-006–P-010)  
- Trigger rate: 0.55 across 5 probes  
- Annual cost: ~$2.40M per 1,000 touches  
- Fix: confidence-proportional phrasing gates (already the Week 10 mechanism — now training the model to internalize it)

**Training path:** Path A — SFT with LoRA on Qwen 3.5 (0.8B or 2B, T4 fits both at 16-bit)

**Week 10 baseline (do not re-run τ²-Bench):**  
- pass@1 = 0.8333, z=2.619, p=0.009  
- Cost/lead = $0.52  
- Trace log: `seeds/trace_log.jsonl` (30 trials)

**Hard cost cap: $10 total.** No τ²-Bench retail re-runs. No eval-tier model (Claude Sonnet 4.6) before Day 4.

---

## Current status (as of rubric-remediation commit 048e358, 2026-04-30)

**Interim report (memo.md/memo.pdf):** rubric-remediated. Cross-tab composition tables,
4 worked examples with step-by-step rubric scoring, Cohen's κ IRA analysis all added.

**Interim repo (GitHub):** rubric-remediated. Methodology.md has argued path justification
(cause→inference→conclusion) and embedding similarity results. Generation pipeline has
runnable synthesis_generator.py with CHEAP_MODELS/EVAL_TIER_MODELS, named threshold
constants, assert_no_leakage(), and main() entry points in all scripts.

**GitHub remote:** https://github.com/78gk/Sales-Agent-Evaluation-Bench  

**Dataset:** 155 tasks total — train=75, dev=30, held_out=50 (sealed, gitignored).
All 155 pass `python scoring_evaluator.py --validate` (3/3 OK, 3/3 PASS).

**Next:** Day 4 — Colab T4 LoRA training on Qwen 3.5. See Day-by-day plan below.

---

## Repo state (as of bootstrap commit 1650bb3, 2026-04-29)

### Done — do not recreate
| File | What it is |
|---|---|
| `schema.json` | Full JSON schema + 3 working example tasks (TB-0001/0002/0003) |
| `scoring_evaluator.py` | `(task, agent_output) → float` — run `python scoring_evaluator.py --validate` to verify |
| `audit_memo.md` | ≤600 words — 8 probe IDs, 5 trace IDs, 4 τ²-Bench gaps documented |
| `methodology.md` | Path A declaration, partitioning, contamination, ablation plan |
| `methodology_rationale.md` | 3 Week 10 trace IDs cited, path justification, backbone selection |
| `datasheet.md` | Gebru 7-section + Pushkarna layered detail |
| `inter_rater_agreement.md` | Scaffold — fill after Day 2 hand-labelling |
| `evidence_graph.json` | 7 claims seeded (C-006/C-007 fill post-training) |
| `cost_log.md` | Running log, budget allocation, model tiers |
| `generation_scripts/router_config.json` | Model routing policy — generator ≠ judge always |
| `generation_scripts/judge_prompt.txt` | Judge prompt for LLM-as-a-judge filter |
| `ablations/ablation_results.json` | Scaffold — fill after training |
| `seeds/` | Copied from week-10: trace_log.jsonl, probe_library.json/.md, failure_taxonomy.md, target_failure_mode.md |

### Empty — needs work
| Dir | What goes here |
|---|---|
| `tenacious_bench_v0.1/train/` | ~125 task JSON files (TB-0001 to TB-0125) |
| `tenacious_bench_v0.1/dev/` | ~75 task JSON files |
| `tenacious_bench_v0.1/held_out/` | ~50 sealed tasks — gitignored, never in training scripts |
| `training/` | LoRA training script, hyperparameters, loss logs |
| `synthesis_memos/` | 8 paper memos (see `synthesis_memos/README.md` for list) |

---

## Task schema — every task is a JSON file

```json
{
  "task_id": "TB-0001",
  "version": "v0.1",
  "category": "signal_over_claiming",
  "source_mode": "trace_derived",
  "seed_trace_id": "<sim_id from seeds/trace_log.jsonl>",
  "input": {
    "prospect_context": { "company": "...", "signals": { ... } },
    "agent_prompt": "..."
  },
  "expected": {
    "phrasing_tier": "hypothesis",
    "routed_to_human": false,
    "stale_disclosed": true
  },
  "scoring": {
    "dimensions": [{ "name": "phrasing_tier", "weight": 0.60, "check": "output.get('phrasing_tier') == expected.get('phrasing_tier')" }],
    "pass_threshold": 0.60
  },
  "metadata": { "authored_by": "Kirubel Tewodros", "authored_date": "2026-04-29" }
}
```

**Phrasing tier thresholds:**
- `assertive`: conf ≥ 0.80 AND ≥2 high-weight signals AND not stale
- `inquiry`: conf 0.50–0.79 OR only 1 high signal
- `hypothesis`: conf 0.25–0.49 OR 1 medium signal
- `abstention`: conf < 0.25 OR all stale OR headcount/pricing/timeline commitment requested

---

## Deliverable deadlines

| Deadline | Day | What ships |
|---|---|---|
| **Wednesday 21:00 UTC** | Day 3 | README, audit_memo, schema, scoring_evaluator, bench v0.1 skeleton (≥30 tasks), datasheet, methodology, generation_scripts, inter_rater_agreement, PDF report |
| **Saturday 21:00 UTC** | Day 6 | + training/, ablations/, model_card, evidence_graph complete, all synthesis memos, HuggingFace dataset + model + blog post + community engagement |

---

## Day-by-day plan

**Day 1 (DONE):** Repo bootstrap, schema, scoring_evaluator, seeds copied  
**Day 2 (DONE):** 75 train tasks + 30 dev tasks authored  
**Day 3 (DONE):** 50 held_out tasks sealed, contamination checks (0 n-gram overlaps, 0 embed overlaps), inter-rater labelling (κ≈0.95), synthesis memos LIMA + Magpie, interim submissions  
**Day 3 post (DONE):** Rubric remediation — memo.md cross-tabs + worked examples; methodology.md argued justification; synthesis_generator.py + dedup_embed.py created; main() guards added  
**Day 4 (NEXT):** Colab T4 — `pip install unsloth[colab-new]`, 5-task dummy LoRA on Qwen 3.5 0.8B → HF Hub push test, then real 75-task training run (rank=16, alpha=32, q_proj/v_proj, 16-bit). Also run `synthesis_generator.py --count 60` to reach 250-task corpus.  
**Day 5:** Delta A/B ablations on held_out (fill `ablations/ablation_results.json`, update C-006/C-007 in evidence_graph.json), write 6 remaining synthesis memos  
**Day 6:** Model card, blog post (HF community or Substack), community engagement (τ²-Bench GitHub issue), HuggingFace dataset + model push (after staff sign-off)  

---

## Hard rules — never violate

1. `held_out/` is gitignored and never used in training scripts
2. Generator ≠ judge for the same task (preference leakage prevention)
3. No eval-tier model (Claude Sonnet 4.6) before Day 4 — dev-tier only for authoring
4. No τ²-Bench retail re-runs — use existing `seeds/trace_log.jsonl`
5. Every numeric claim in memo + blog must resolve to a row in `evidence_graph.json`
6. Log every API cost in `cost_log.md` within 24 hours — $10 hard cap
7. Program staff sign-off required before any HuggingFace publish

---

## Key files to read first in any new session

1. This file (CLAUDE.md) — already loaded
2. `audit_memo.md` — what τ²-Bench misses and why Signal Over-Claiming is the target
3. `methodology.md` — full path declaration and partitioning
4. `schema.json` examples array — the 3 example tasks define the task format
5. `seeds/target_failure_mode.md` — business case for the training target

---

## Environment checklist (run once before Day 3)

```bash
pip install -r requirements.txt
python scoring_evaluator.py --validate   # should print 3x OK + 3x PASS/FAIL
```

Colab setup (Day 4):
- T4 runtime, 16 GB VRAM
- `pip install unsloth[colab-new]`
- HF_TOKEN env var set
- OpenRouter OPENROUTER_API_KEY env var set
- Run 5-task dummy LoRA on Qwen 3.5 0.8B, push adapter to HF Hub to verify pipeline
