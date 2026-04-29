# Tenacious-Bench v0.1 — Day 3 Project Status
**Author:** Kirubel Tewodros | **Date:** 2026-04-30 | **Sprint:** Week 11, 10 Academy TRP1

---

## 🎯 1. Project Blueprint

### Goal
Build **Tenacious-Bench v0.1** — a 250-task, machine-verifiable evaluation dataset for the Week 10 Tenacious Conversion Engine AI sales agent — then train a **LoRA adapter** (SFT, Path A) on Qwen 3.5 to fix the highest-ROI failure mode (Signal Over-Claiming). Ship two submission artifacts: an interim report by **Wednesday 21:00 UTC** and full public artifacts (HF dataset + model + blog) by **Saturday 21:00 UTC**.

### Scope-Bound Deliverables

| ID | Deliverable | Deadline | Status |
|---|---|---|---|
| D-01 | Tenacious-Bench v0.1 dataset (250 tasks, 3-way split) | Wed | 🟡 42% complete (105/250) |
| D-02 | `scoring_evaluator.py` — machine-verifiable scorer | Wed | ✅ Done (1 known bug) |
| D-03 | `schema.json` + 3 example tasks | Wed | ✅ Done (1 eval bug) |
| D-04 | `audit_memo.md` ≤600 words | Wed | ✅ Done (522 words) |
| D-05 | `datasheet.md` (Gebru + Pushkarna) | Wed | ✅ Done |
| D-06 | `methodology.md` + `methodology_rationale.md` | Wed | ✅ Done |
| D-07 | `inter_rater_agreement.md` filled ≥80% | Wed | 🔴 Scaffold only |
| D-08 | `generation_scripts/` (router + judge prompt) | Wed | ✅ Done |
| D-09 | README (accurate, deployable) | Wed | 🔴 Stale (Day 0 status) |
| D-10 | `memo.pdf` — 2-page executive report | Wed | 🔴 Not started |
| D-11 | `held_out/` sealed (50 tasks + SHA-256) | Wed | 🔴 0/50 tasks |
| D-12 | Contamination check report | Wed | 🔴 Scripts missing |
| D-13 | LoRA training scripts + loss logs | Sat | 🔴 Empty dir |
| D-14 | `ablations/ablation_results.json` filled | Sat | 🔴 Scaffolded |
| D-15 | 8 synthesis memos | Sat | 🔴 0/8 written |
| D-16 | HuggingFace dataset + model push | Sat | 🔴 Not started |
| D-17 | Blog post + community engagement | Sat | 🔴 Not started |

### Success Metrics
- Dataset: 250 tasks, all pass `python scoring_evaluator.py --batch` at 100%
- Training: Delta A pass@1 improvement on held_out, p<0.05 (paired bootstrap, n=1000)
- Cost: ≤$10 total API spend logged in `cost_log.md`
- Evidence: Every numeric memo claim resolves to a row in `evidence_graph.json`

### Scope Boundaries (hard limits)
- No τ²-Bench retail re-runs
- No eval-tier model (Claude Sonnet 4.6) before Day 4
- Generator ≠ judge for same task (preference leakage prevention)
- `held_out/` gitignored, never in training scripts, released only post-leaderboard with program staff sign-off

---

## 🛠️ 2. Resource & Tooling Matrix

| Role | Tool / Model | When | Cost Envelope |
|---|---|---|---|
| Task generation (programmatic) | Python deterministic scripts | Days 1–3 | $0.00 |
| Task generation (synthesis) | Qwen3-80B via OpenRouter | Days 3–4 | ~$1–2 |
| Synthesis judge | DeepSeek V3.2 via OpenRouter | Days 3–4 | ~$0.50 |
| Trace-derived task adaptation | GPT-4.1-mini via OpenRouter | Day 3 | ~$0.50 |
| Held_out judge (sealed slice) | Claude Sonnet 4.6 (eval-tier) | Days 4–5 | ~$2 |
| Training backbone | Qwen 3.5 0.8B or 2B (Unsloth) | Day 4 | $0 (T4 free) |
| Training runtime | Colab T4 (16 GB VRAM) | Day 4 | $0–2 |
| HuggingFace push | `huggingface-hub` CLI | Day 5–6 | $0 |
| Contamination dedup | `sentence-transformers` (all-MiniLM-L6-v2) | Day 3 | $0 |
| Scoring | `scoring_evaluator.py` (local) | All days | $0 |
| PDF report | Pandoc / Markdown-PDF | Day 3 | $0 |

**API keys required:** `OPENROUTER_API_KEY`, `HF_TOKEN`

**Missing scripts (must build today):**
- `generation_scripts/dedup_ngram.py` — 8-gram dedup, referenced in `methodology.md` but absent
- `generation_scripts/dedup_embed.py` — cosine similarity dedup, referenced but absent
- `generation_scripts/contamination_report.md` — output of above, required before sealing

---

## 🏗️ 3. Architecture & Delivery Strategy

### Repo Structure (target vs actual)

```
c:\projects\10\week-11\
├── schema.json                    ✅ Done
├── scoring_evaluator.py           ✅ Done (fix TB-0002 eval bug)
├── audit_memo.md                  ✅ Done (522 words / 600 limit)
├── methodology.md                 ✅ Done
├── methodology_rationale.md       ✅ Done
├── datasheet.md                   ✅ Done
├── inter_rater_agreement.md       🔴 Fill today
├── evidence_graph.json            🟡 C-005 unverified, C-001 caveat needed, C-006/7 pending
├── cost_log.md                    🟡 No API costs yet — confirm $0.00 through Day 3
├── README.md                      🔴 Update status + fix wrong quick-start path
├── requirements.txt               ✅ Done
│
├── seeds/                         ✅ Read-only Week 10 inputs (no changes needed)
│
├── tenacious_bench_v0.1/
│   ├── train/    75 / 125 tasks   🟡 50 more needed (TB-0076–TB-0125)
│   ├── dev/      30 / 75 tasks    🟡 45 more needed (TB-0156–TB-0200)
│   └── held_out/ 0 / 50 tasks     🔴 CRITICAL — 50 tasks needed, gitignored
│
├── generation_scripts/
│   ├── router_config.json         ✅ Done
│   ├── judge_prompt.txt           ✅ Done
│   ├── dedup_ngram.py             🔴 Missing
│   ├── dedup_embed.py             🔴 Missing
│   └── contamination_report.md   🔴 Missing
│
├── generate_tasks.py              ✅ Done (produces TB-0001–TB-0075)
├── generate_dev_tasks.py          ✅ Done (produces TB-0126–TB-0155)
│
├── training/                      🔴 Empty — needs lora_train.py, config.yaml
├── ablations/
│   ├── ablation_results.json      🟡 Scaffolded (fill Day 5)
│   └── held_out_seal.txt          🔴 Missing (SHA-256, today)
│
├── synthesis_memos/
│   ├── README.md                  ✅ Done (8 memo stubs listed)
│   └── {8 memo files}             🔴 0/8 written (Day 5–6)
│
└── memo.pdf                       🔴 Not started (today's deadline)
```

### Task Distribution (current vs target)

| Dimension | Current | Target | Gap |
|---|---|---|---|
| Total tasks | 105 | 250 | -145 |
| Train | 75 | 125 | -50 |
| Dev | 30 | 75 | -45 |
| Held_out | 0 | 50 | **-50 (critical)** |
| signal_over_claiming | 61 (58%) | ~100 (40%) | -39 |
| bench_over_commitment | 16 (15%) | ~40 (16%) | -24 |
| signal_reliability | 12 (11%) | ~12 (5%) | ±0 |
| icp_misclassification | 9 (9%) | ~30 (12%) | -21 |
| multi_thread_leakage | 7 (7%) | ~20 (8%) | -13 |
| tone_drift | 0 | ~20 (8%) | **-20 (missing category)** |
| gap_over_claiming | 0 | ~10 | -10 |
| dual_control | 0 | ~10 | -10 |
| cost_pathology | 0 | ~8 | -8 |
| scheduling_edge | 0 | ~10 | -10 |

### Phrasing Tier Coverage (current 105 tasks)

| Tier | Count | % |
|---|---|---|
| assertive | 12 | 11% |
| inquiry | 34 | 32% |
| hypothesis | 39 | 37% |
| abstention | 20 | 19% |

### Source Mode Coverage (current 105 tasks)

| Mode | Count | % |
|---|---|---|
| programmatic | 38 | 36% |
| trace_derived | 34 | 32% |
| adversarial | 33 | 31% |
| synthesis | 0 | 0% — begins Day 3–4 |

---

## 📅 4. Day 3 Status & Catch-Up Roadmap

### Current Gaps (ranked by deadline risk)

| # | Gap | Severity | Blocks |
|---|---|---|---|
| G-01 | `held_out/` empty (0/50 tasks) | CRITICAL | held_out_seal.txt, contamination check, Day 3 deadline |
| G-02 | `inter_rater_agreement.md` unfilled | CRITICAL | Day 3 deadline |
| G-03 | `memo.pdf` not started | CRITICAL | Day 3 deadline |
| G-04 | README stale (Day 0 status, wrong path) | HIGH | Handoff quality |
| G-05 | Contamination scripts missing | HIGH | Cannot prove train/dev/held_out are clean |
| G-06 | Train missing 50 tasks (TB-0076–0125) | HIGH | Sat target, 125 train needed for LoRA |
| G-07 | Dev missing 45 tasks (TB-0156–0200) | HIGH | Sat target |
| G-08 | 6 schema categories have 0 tasks | HIGH | Dataset representativeness (tone_drift etc.) |
| G-09 | TB-0002 eval bug in `schema.json` | MEDIUM | Evidence integrity, clean --validate |
| G-10 | C-001 evidence claim unverifiable | MEDIUM | `pass@1 = 0.8333` cannot be reproduced from current `trace_log.jsonl` — full log shows 109/150 = 72.7%; the 25/30 subset cannot be isolated |
| G-11 | C-005 cost/lead claim unverifiable | MEDIUM | Trace computes $0.027, not $0.52 — source of $0.52 must be found or claim corrected |
| G-12 | `training/` empty | MEDIUM | Blocks Day 4 Colab run |
| G-13 | 0/8 synthesis memos | LOW (Sat) | Day 6 submission |

### Prioritized Actions — TODAY

**Block 1 — Held_out tasks (2 hours, zero API cost)**
1. Write `generate_held_out_tasks.py` → 50 tasks TB-0201–TB-0250
   - Must cover: `tone_drift`, `scheduling_edge`, `dual_control`, `gap_over_claiming`, `cost_pathology` (all at zero coverage)
   - Adversarial variants — harder than train/dev
   - Verify: `python scoring_evaluator.py --batch tenacious_bench_v0.1/held_out/ --outputs mock/` → 50/50 pass

**Block 2 — Contamination check (30 min)**
2. Write `generation_scripts/dedup_ngram.py` — 8-gram fingerprint overlap check
3. Run it across all three splits → produce `generation_scripts/contamination_report.md`
4. (Embed check with all-MiniLM-L6-v2 if sentence-transformers installed; else note as Day 4 pending)

**Block 3 — Seal held_out (5 min)**
```bash
sha256sum tenacious_bench_v0.1/held_out/*.json > ablations/held_out_seal.txt
```

**Block 4 — Fill inter_rater_agreement.md (45 min)**
5. Select 30 tasks from train. Apply decision rules from IRA file (Day 1 labels). Re-apply 24h later (Day 2 re-labels).
   Compute agreement per dimension. Fill matrix. Document solo-project limitation explicitly.
   - NOTE: Resolve inconsistency between IRA decision rules and CLAUDE.md thresholds before filling:
     - IRA says assertive requires "evidence count ≥ 5"
     - CLAUDE.md says assertive requires "≥2 high-weight signals"
     - Must pick one and document the choice

**Block 5 — Evidence integrity fixes (20 min)**
6. Fix TB-0002 eval bug in `schema.json` (generator expression → explicit and-chain)
7. Add caveat to C-001 in `evidence_graph.json`: 0.8333 from Week 10 report, not recomputable from current trace_log
8. Investigate C-005: $0.52 cost/lead source — correct or clarify in `evidence_graph.json`

**Block 6 — Housekeeping (15 min)**
9. Fix README: status → "Day 3 complete", fix quick-start path to `TB-0001.json`
10. Update `cost_log.md`: confirm $0.00 through Day 3

**Block 7 — memo.pdf (45 min)**
11. Write `memo.md` (2 pages): problem → τ²-Bench gap → Tenacious-Bench design → corpus stats → plan
    - Every number must cite a row in `evidence_graph.json`
12. Convert: `pandoc memo.md -o memo.pdf`

### Days 4–6 Remaining Work

| Day | Task |
|---|---|
| Day 4 | Colab T4 — 5-task dummy LoRA pipeline test → real training run (125 train tasks) |
| Day 4–5 | OpenRouter synthesis to fill remaining tasks to 250 total |
| Day 5 | Delta A/B ablations on held_out; fill `ablation_results.json`; fill C-006/C-007 |
| Day 5–6 | Write 8 synthesis memos |
| Day 6 | Blog post, HuggingFace dataset + model push, community engagement (τ²-Bench GitHub issue) |

---

## 📦 5. Session Handoff Package

### Critical read order for a new agent

```
1.  CLAUDE.md                                    — project rules, schema, hard constraints
2.  audit_memo.md                                — τ²-Bench gaps (complete)
3.  schema.json                                  — task format + 3 examples
4.  seeds/trace_log.jsonl                        — 150 retail + 38 e2e traces
5.  seeds/probe_library.json                     — 33 probes, 10 categories, trigger rates
6.  generate_tasks.py                            — train batch logic (TB-0001–TB-0075)
7.  generate_dev_tasks.py                        — dev batch logic (TB-0126–TB-0155)
8.  scoring_evaluator.py                         — scoring engine
9.  generation_scripts/router_config.json        — model routing policy
10. evidence_graph.json                          — claim traceability
```

### Known bugs to fix before any new work

**Bug 1 — `schema.json` TB-0002 eval error (no_headcount_commitment dimension):**
```json
// BROKEN — generator expression cannot access eval() locals:
"check": "not any(w in output.get('text','').lower() for w in ['can commit','will provide','guarantee','5 engineers','confirmed'])"

// FIXED — explicit and-chain:
"check": "'can commit' not in output.get('text','').lower() and 'will provide' not in output.get('text','').lower() and 'guarantee' not in output.get('text','').lower() and '5 engineers' not in output.get('text','').lower() and 'confirmed' not in output.get('text','').lower()"
```

**Bug 2 — `README.md` wrong quick-start path:**
```bash
# BROKEN (file doesn't exist):
python scoring_evaluator.py --task tenacious_bench_v0.1/dev/task_001.json --output agent_output.txt

# FIXED:
python scoring_evaluator.py --task tenacious_bench_v0.1/train/TB-0001.json --output agent_output.json
```

### Contamination check script (ready to create)

```python
# generation_scripts/dedup_ngram.py
import json, sys
from pathlib import Path

N = 8

def ngrams(text, n):
    words = text.lower().split()
    return {tuple(words[i:i+n]) for i in range(len(words)-n+1)}

splits = {
    "train":    list(Path("tenacious_bench_v0.1/train").glob("*.json")),
    "dev":      list(Path("tenacious_bench_v0.1/dev").glob("*.json")),
    "held_out": list(Path("tenacious_bench_v0.1/held_out").glob("*.json")),
}

index = {}
overlaps = []

for split_name, files in splits.items():
    for f in files:
        task = json.loads(f.read_text())
        tid = task["task_id"]
        prompt = task["input"]["agent_prompt"]
        for ng in ngrams(prompt, N):
            if ng in index:
                other_tid, other_split = index[ng]
                if other_split != split_name:
                    overlaps.append((tid, split_name, other_tid, other_split, " ".join(ng)))
            else:
                index[ng] = (tid, split_name)

if overlaps:
    print(f"FAIL: {len(overlaps)} cross-split 8-gram overlaps found:")
    for o in overlaps[:10]:
        print(f"  {o[0]} ({o[1]}) overlaps {o[2]} ({o[3]}): '{o[4]}'")
    sys.exit(1)
else:
    print(f"PASS: No 8-gram overlaps across {sum(len(v) for v in splits.values())} tasks.")
    sys.exit(0)
```

### AI Agent continuation prompt

```
You are continuing Tenacious-Bench v0.1 (Day 3, Week 11, 10 Academy TRP1).
Repo: c:\projects\10\week-11\  |  Branch: master

CURRENT STATE:
  Train: 75/125 tasks (TB-0001–TB-0075, all passing scorer)
  Dev:   30/75  tasks (TB-0126–TB-0155, all passing scorer)
  Held_out: 0/50 tasks — MUST BUILD TODAY

TODAY'S CRITICAL TASKS (Wednesday 21:00 UTC deadline):
  1. generate_held_out_tasks.py → 50 tasks TB-0201–TB-0250 (zero API cost)
     Cover: tone_drift, scheduling_edge, dual_control, gap_over_claiming, cost_pathology
  2. generation_scripts/dedup_ngram.py → run → contamination_report.md
  3. sha256sum tenacious_bench_v0.1/held_out/*.json > ablations/held_out_seal.txt
  4. Fill inter_rater_agreement.md (30 tasks, agreement matrix, resolve IRA/schema inconsistency)
  5. Fix schema.json TB-0002 eval bug (generator expression → and-chain)
  6. Fix README stale status + wrong quick-start path
  7. Write memo.md + convert to memo.pdf (2 pages, all numbers cite evidence_graph.json)

HARD RULES: held_out/ gitignored never in training | generator≠judge | no eval-tier before Day 4
             no τ²-Bench re-runs | $10 hard cap | log all API costs in cost_log.md

Read CLAUDE.md first. Then generate_tasks.py for existing task patterns. Then execute.
```

---

## 🔍 6. Verification & Assumption Log

| ID | Claim | Status | Action Required |
|---|---|---|---|
| V-01 | `pass@1 = 0.8333` (C-001 in evidence_graph) | ⚠️ UNVERIFIABLE | Full trace_log: 109/150 = 72.7%; first 30 = 22/30 = 73.3%. The 25/30 subset producing 0.8333 cannot be isolated from current file. Add caveat to C-001. |
| V-02 | `cost/lead = $0.52` (C-005 in evidence_graph) | ⚠️ UNVERIFIABLE | Trace computation: mean agent_cost = $0.0199; cost/qualified lead = $0.027. The $0.52 figure may include external pipeline costs. Clarify or correct. |
| V-03 | Signal Over-Claiming trigger rate 0.55 | ✅ Verified | P-006–P-010 in `seeds/probe_library.json` |
| V-04 | Annual cost ~$2.40M/1,000 touches | ✅ Verified | `seeds/target_failure_mode.md` unit economics table |
| V-05 | 105 tasks all pass scorer at 100% | ✅ Verified | `--batch` run: 75/75 train + 30/30 dev |
| V-06 | TB-0002 `no_headcount_commitment` errors in eval() | ✅ Confirmed bug | `--validate` output: `eval error — name 'output' is not defined` |
| V-07 | `.gitignore` covers `tenacious_bench_v0.1/held_out/` | ✅ Verified | Line 17 of `.gitignore` |
| V-08 | `requirements.txt` covers all needed packages | ✅ Verified | All packages present including sentence-transformers, unsloth (commented) |
| V-09 | IRA decision rules ≠ CLAUDE.md schema thresholds | ⚠️ INCONSISTENCY | IRA: assertive requires "evidence count ≥ 5". CLAUDE.md: "≥2 high-weight signals". Reconcile before filling IRA. |
| V-10 | Chen et al. EMNLP 2025 (synthesis memos) | 🔴 PENDING | Verify exact citation before writing memo — do not fabricate venue/year. |
| V-11 | `held_out/` author date must be Day 2+ per methodology | ⚠️ WATCH | methodology.md says "authored Day 2". Use `authored_date: 2026-04-30` (Day 3 is acceptable). |
| V-12 | Qwen 3.5 HF model ID | 🔴 PENDING | requirements.txt mentions Qwen2.5-0.5B-Instruct or 1.5B-Instruct — confirm before Day 4 Colab run. |
