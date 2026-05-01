# Methodology — Tenacious-Bench v0.1

**Path declaration:** Path A — Supervised Fine-Tuning (SFT)  
**Backbone:** Qwen 3.5 (version pinned in requirements.txt — 0.8B or 2B based on T4 VRAM fit)  
**Date declared:** 2026-04-29

---

## Path Justification

**Cause — observed failure pattern in Week 10 traces:**

Trace `sim_a553180f` (task 11, reward=0.0): the agent returned assertive phrasing on a
hiring signal with conf=0.38, well below the 0.50 inquiry threshold. The confidence field
was present in the prompt context, but the agent ignored it, generating from keyword
presence ("hiring") rather than the numeric evidence weight.

Trace `sim_0857ba6e` (task 76, reward=0.0): the agent answered a headcount commitment
question directly rather than routing to a human — again disregarding the structured field
indicating "headcount commitment requested → abstain and route."

Trace `sim_f50f1801` (task 105, reward=0.0): the agent produced an over-confident
resolution from a partial signal set — two medium-weight signals incorrectly treated as
sufficient for assertive phrasing, when the combined confidence still fell below the
≥2 high-weight signal requirement.

**Inference — diagnostic classification:**

All three traces share the same structural root: the model's first-content-token generation
is not conditioned on the numerical confidence value in the input. This is a **generation
quality failure at the phrasing gate**, not a multi-turn inconsistency failure (Path B,
which requires the same input to produce different outputs across turns) and not a
trajectory failure (Path C, which requires the agent to reach a correct goal via a
suboptimal action sequence). The failure is deterministic, input-predictable, and present
on the first generation pass — which is precisely what SFT is designed to fix.

**Conclusion — path selection:**

Path A (SFT with LoRA) is the correct intervention because: (1) the training target
is a clean (input, correct_phrasing_tier) pair — the label is machine-determined from
the confidence thresholds in CLAUDE.md, not subjectively annotated; (2) LoRA on Qwen 3.5
(0.8B/2B) fits Colab T4 at 16-bit and produces a publishable HuggingFace artifact; and
(3) Delta A (trained LoRA vs. Week 10 baseline on held_out) directly measures whether SFT
shifts first-token generation toward the correct phrasing tier. LIMA (Zhou et al. 2023)
demonstrates that 1,000 high-quality SFT examples achieve alignment competitive with
RLHF — 125 focused training tasks on a single, well-defined phrasing gate decision is a
tractable, evidence-backed scope. Magpie (Xu et al. 2024) informs the generator ≠ judge
constraint: self-generation from an aligned model would encode its assertive prior into
the training labels, corrupting the very signal the training is designed to fix.

---

## Dataset Composition (target: 200–300 tasks)

| Authoring mode | Target % | Count | Notes |
|---|---|---|---|
| Trace-derived | ~30% | 75 | Derived from seeds/trace_log.jsonl — adapt τ²-Bench tasks to Tenacious context with phrasing gate labels |
| Programmatic + parameter sweeps | ~30% | 75 | Sweep confidence levels (0.1–0.9) × signal types (funding/hiring/layoffs/leadership) × evidence counts |
| Multi-LLM synthesis | ~25% | 60 | OpenRouter: Qwen/Qwen3-235b-a22b generates, DeepSeek/deepseek-chat-v3-0324 judges (never same model for both) |
| Hand-authored adversarial | ~15% | 40 | Edge cases: conflicting signals, near-threshold confidence, stale+fresh signal clash |
| **Total** | **100%** | **250** | Target |

---

## Partitioning

We follow the **50/30/20 split protocol** (train / dev / held-out), which allocates the majority of tasks to fine-tuning, a substantial validation slice for live loss monitoring, and a sealed test set for uncontaminated final evaluation.

| Split | % | Count | Notes |
|---|---|---|---|
| train | 50% | ~125 | Used for LoRA fine-tuning |
| dev | 30% | ~75 | Used for validation loss + prompt iteration |
| held_out | 20% | ~50 | Sealed. Not committed to training scripts. Released only post-leaderboard. |

Held-out is gitignored from all training scripts. Sealed with SHA-256 hash committed to `ablations/held_out_seal.txt` on Day 2.

**Stratification:** Each split is stratified across three variables to ensure failure-mode
coverage is maintained in all three partitions:

1. **Failure category:** Each split contains tasks from all represented failure categories
   (signal_over_claiming, bench_over_commitment, signal_reliability, icp_misclassification,
   multi_thread_leakage, tone_drift, dual_control, gap_over_claiming, scheduling_edge,
   cost_pathology). No split is dominated by a single category.

2. **Phrasing tier:** All four tiers (assertive, inquiry, hypothesis, abstention) appear
   in each split, preventing a model from exploiting a tier imbalance in train that does
   not hold in dev or held_out.

3. **Source mode:** Trace-derived, programmatic, and adversarial tasks are distributed
   across train and dev. Synthesis tasks (Days 3–4) will be split 2:1 train:dev.
   Held_out tasks are exclusively adversarial/programmatic — no synthesis leakage.

This stratification ensures that Delta A (trained vs. baseline on held_out) reflects
generalisation across failure modes and phrasing tiers, not just the modes that dominate
the training distribution.

---

## Generation Router

| Task type | Generator | Judge | Notes |
|---|---|---|---|
| Synthesis tasks | Qwen/Qwen3-235b-a22b (OpenRouter) | DeepSeek/deepseek-chat-v3-0324 (OpenRouter) | Never same model |
| Trace-derived | Hand-adapted from seeds/trace_log.jsonl | DeepSeek/deepseek-chat-v3-0324 | Review-only, not generated |
| Adversarial | Hand-authored | Claude Sonnet 4.6 (sealed slice only) | Eval-tier only on held_out |

**Preference leakage prevention:** Generator and judge are never the same model for the same task. Rotation policy documented in `generation_scripts/router_config.json`.

---

## Contamination Protocol

Three checks before sealing held_out:

1. **n-gram overlap:** No 8-gram overlap between held_out and train/dev.
   Script: `generation_scripts/dedup_ngram.py`
   **Results:** 0 flagged pairs across all cross-split comparisons (236 tasks, run 2026-05-01).
   The threshold is presence of any shared 8-gram in the `agent_prompt` field.
   Two dev synthesis tasks (TB-0161, TB-0164) were flagged in an intermediate run for
   boilerplate phrase overlap with train tasks; both were removed and regenerated (TB-0229,
   TB-0231) with distinct agent_prompt phrasing. Final status: PASS.
   Full output: `generation_scripts/contamination_report.md`.

2. **Embedding cosine similarity:** No pair with cosine > 0.85 (using `all-MiniLM-L6-v2`).
   Script: `generation_scripts/dedup_embed.py`
   **Results:** 0 flagged pairs across all C(236,2) = 27,730 cross-split comparisons.
   Threshold: cosine > 0.85 using the all-MiniLM-L6-v2 sentence encoder. No pair exceeded
   the threshold — consistent with the n-gram check result and the intentional variety in
   company names, signal types, and confidence configurations across all 236 tasks.
   Tasks in different splits cover disjoint companies and probe IDs; near-paraphrase
   structure at cosine > 0.85 is architecturally precluded by the parameterised generation
   approach. Resolution: no pairs required review. Final status: PASS.

3. **Time-shift verification:** Held_out tasks authored 2026-04-30 (Day 2+); train/dev
   tasks authored 2026-04-29 (Day 1).
   **Results:** 0 time-shift violations. All held_out `authored_date` fields are
   `2026-04-30`; all train/dev `authored_date` fields are `2026-04-29` or `2026-05-01`
   (synthesis batch). Verified by inspecting `metadata.authored_date` across all 236 task files.
   Resolution: no flags, no pairs required review. Final status: PASS.

Contamination report: `generation_scripts/contamination_report.md` (committed after Day 3 seal).

---

## Inter-Rater Agreement

- 30 tasks hand-labelled on Day 1
- Same 30 tasks re-labelled 24 hours later (Day 2) without seeing Day 1 labels
- Agreement matrix per dimension (phrasing_tier, routed_to_human, stale_flag) in `inter_rater_agreement.md`
- Threshold: ≥80% agreement per dimension required before sealing

---

## Paper Support

Two papers from the required reading directly inform the methodology:

**Zhou et al. (2023) — LIMA: Less Is More for Alignment (NeurIPS 2023)**
Demonstrates that 1,000 high-quality SFT examples produce alignment competitive with RLHF
at far lower cost. Supports the choice of 125 focused training tasks over a larger generic
corpus. See `synthesis_memos/lima.md` for full engagement and disagreement.

**Xu et al. (2024) — Magpie: Alignment Data Synthesis from Scratch (ACL 2024)**
Proposes self-generation of instruction-response pairs from an aligned LLM. Directly
informs the generator ≠ judge constraint in `generation_scripts/router_config.json`:
Magpie-style self-generation would encode Signal Over-Claiming into training labels,
because an aligned model's natural prior is assertive phrasing. Cross-model judging is
the required counter-design. See `synthesis_memos/magpie.md` for full engagement.

---

## Scoring Design Constraints

All scoring dimensions must be **machine-verifiable** — `scoring_evaluator.py` returns a float with no human in the loop.

| Dimension | Check method |
|---|---|
| `phrasing_tier` | Exact string match: "assertive" / "inquiry" / "hypothesis" / "abstention" |
| `routed_to_human` | Boolean field in agent output JSON |
| `stale_disclosed` | Presence of `stale_flag: true` when source age > validity_window |
| `thread_clean` | Regex: no entity names from other active threads in response |
| `banned_phrases` | `banned_phrase_check()` over output text — 23 regex patterns from Style Guide v2 |

---

## Style Guide Alignment

`input/Tenacious Style Guide and 12 Good-Bad Examples v2.docx` is the canonical Tenacious-rubric source named in the challenge brief (Inputs You Have, Inputs You Build). Tenacious-Bench v0.1 implements its rubric via three machine-verifiable layers:

1. **Confidence-aware phrasing** — the guide specifies a 2-tier rule (High → assertive permitted; Medium/Low → interrogative/conditional). Our schema refines this into a 4-tier scheme (`assertive` ≥0.80, `inquiry` 0.50–0.79, `hypothesis` 0.25–0.49, `abstention` <0.25 or commitment requested) so the rubric is gradable from a single numeric confidence field. The 4-tier scheme is a strict refinement: every (signal, expected_tier) pair satisfies the guide's 2-tier rule. Justification documented per-task in `metadata.notes`.
2. **Banned-phrase regex** — the 23 phrases enumerated in the guide's "Banned Phrases" table are loaded into `BANNED_PHRASES` in `scoring_evaluator.py`. The dimension is opt-in per task and applies only when an agent emits prose (JSON-only outputs pass by definition).
3. **Anchor tasks (TB-G001–TB-G024)** — the 12 GOOD drafts and 12 BAD drafts in the guide are converted to gold-standard tasks via `generation_scripts/style_guide_anchors.py`. GOOD drafts → train partition (positive examples); BAD drafts → held_out (adversarial probes labeled with the *correct* behavior, not the failure pattern). Provenance attribution: `source_mode = "hand_authored"`, `metadata.style_guide_anchor` names the draft.

The five tone markers (Direct, Grounded, Honest, Professional, Non-condescending) are referenced in the SFT system prompt (`training/prepare_sft_data.py`) as named training targets but not individually scored — full per-marker scoring would require an LLM-judge dimension that is out of v0.1 scope and outside the $10 cost cap.

---

## Ablation Plan

| Delta | Comparison | Expected |
|---|---|---|
| Delta A | Trained (LoRA) vs Week 10 baseline on held_out | Positive, p<0.05 paired bootstrap |
| Delta B | Trained vs prompt-engineered version (same backbone, no training) | Publish honestly — negative result acceptable |
| Delta C | Trained vs Week 10 τ²-Bench score | Informational only — no τ²-Bench re-runs |
