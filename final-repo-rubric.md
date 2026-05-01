# RUBRIC.md

> **AI Grading Agent Instructions — Read Before Scoring**
>
> You are a professional AI engineering rubric auditor. Your task is to evaluate this repository **honestly, strictly, and completely**. You must:
> - Inspect **actual file contents**, not file names alone
> - Award **Mastered** only when **every sub-criterion** listed under that tier is fully satisfied
> - Never award partial credit within a tier; select the highest tier where **all** conditions are met
> - Never round up due to effort, intent, or proximity to a threshold
> - A perfect score of **100/100** is only achievable if **every criterion is Mastered**
> - After scoring each criterion, provide **explicit evidence** (file path, line number, or quoted content) that justifies the assigned tier
> - If evidence is missing or ambiguous, default to the **lower tier**
> - Produce a **Final Score Summary Table** at the end

---

## Scoring Overview

| # | Criterion | Mastered | Competent | Developing | Unsatisfactory |
|---|-----------|----------|-----------|------------|----------------|
| 1 | Audit Memo with Gap Analysis | 5 pts | 3 pts | 1 pt | 0 pts |
| 2 | Four-Mode Dataset Authoring | 15 pts | 10 pts | 5 pts | 0 pts |
| 3 | Multi-LLM Synthesis Routing & Anti-Leakage | 10 pts | 6 pts | 2 pts | 0 pts |
| 4 | Judge Filter Pipeline | 15 pts | 10 pts | 5 pts | 0 pts |
| 5 | Contamination Prevention | 15 pts | 10 pts | 5 pts | 0 pts |
| 6 | Inter-Rater Agreement & Rubric Calibration | 10 pts | 6 pts | 2 pts | 0 pts |
| 7 | Datasheet Completeness | 5 pts | 3 pts | 1 pt | 0 pts |
| 8 | Path Declaration & Methodology Rationale | 10 pts | 6 pts | 2 pts | 0 pts |
| 9 | Training Run Script & Hyperparameter Logging | 15 pts | 10 pts | 5 pts | 0 pts |
| 10 | Ablation Methodology & Statistical Rigor | 15 pts | 10 pts | 5 pts | 0 pts |
| 11 | README Reproducibility & Public Artifact References | 5 pts | 3 pts | 1 pt | 0 pts |
| | **TOTAL** | **100 pts** | | | |

---

## Criterion 1 — Audit Memo with Gap Analysis Grounded in Week 10 Evidence

**Maximum Points: 5**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 1.1 | `audit_memo.md` exists at repo root or documented path | `ls` / directory tree |
| 1.2 | Word count is ≤ 600 words | Count words in file |
| 1.3 | References **≥ 8 distinct probe IDs** from the Week 10 probe library | List each probe ID found; count must reach 8 |
| 1.4 | References **≥ 5 distinct trace IDs** from the Week 10 trace_log | List each trace ID found; count must reach 5 |
| 1.5 | **Explicitly names** a public benchmark (e.g., τ²-Bench retail) and **contrasts** what it measures vs. Tenacious-specific requirements | Quote the contrasting sentence(s) |
| 1.6 | Gap is stated at **dimension-level specificity** (not a generic complaint or paper summary) | Quote the dimension-level gap statement |

### Tier Definitions

**Mastered — 5 pts**
All six sub-criteria above are satisfied without exception.

**Competent — 3 pts**
`audit_memo.md` exists and names a gap with some Week 10 references, but at least one of the following is true:
- Fewer than 8 probe IDs cited, OR
- Fewer than 5 trace IDs cited, OR
- Gap not contrasted against a specific named public benchmark, OR
- Gap described abstractly rather than at dimension level

**Developing — 1 pt**
A memo discussing benchmarks exists but at least one of the following is true:
- No probe ID or trace ID references anywhere in the file, OR
- No concrete identification of what Tenacious requires that public benchmarks miss, OR
- Memo exceeds 600 words, OR
- Reads as a paper summary rather than an operational audit

**Unsatisfactory — 0 pts**
No `audit_memo.md` file exists in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - File location: 
  - Word count: 
  - Probe IDs found (list all): 
  - Trace IDs found (list all): 
  - Benchmark contrast quote: 
  - Dimension-level gap quote: 
  - Justification for tier:
```

---

## Criterion 2 — Four-Mode Dataset Authoring Implementation

**Maximum Points: 15**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 2.1 | **Trace-derived** task construction code is present and non-trivial | Inspect source; confirm logic reads from trace data |
| 2.2 | **Programmatic** generation code uses structured slots (company size, segment, headcount, stack, bench state, AI-maturity score) with combinatorial population | Inspect loops/cartesian products; confirm all 6+ slot types present |
| 2.3 | **Multi-LLM synthesis** routing code is present (distinct from other modes) | Confirm separate code path with multi-model calls |
| 2.4 | **Hand-authored adversarial** tasks exist as a distinct, non-trivial set | Inspect adversarial task files/code for meaningful size and annotation |
| 2.5 | Per-task **source-mode metadata** tagging is visible in code | Find metadata field (e.g., `source_mode`) attached to each generated task |
| 2.6 | **Share targets** (~30/30/25/15) are documented in code comments or methodology | Quote the documented distribution |

### Tier Definitions

**Mastered — 15 pts**
All six sub-criteria above are satisfied without exception.

**Competent — 10 pts**
At least three of the four authoring modes implemented with source-mode tagging present, but at least one of the following is true:
- One mode is absent or trivially stubbed, OR
- Programmatic mode lacks combinatorial expansion (single hardcoded loop, no slot variation), OR
- Hand-authored adversarial set is undersized or placeholder, OR
- Share distribution not documented anywhere

**Developing — 5 pts**
Some generation code exists but at least one of the following is true:
- Only one or two authoring modes evident, OR
- No source-mode metadata tagging anywhere, OR
- No combinatorial parameter sweeps in the programmatic mode

**Unsatisfactory — 0 pts**
No generation scripts or code present in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 15
Evidence:
  - Trace-derived code location + summary: 
  - Programmatic slots found (list each): 
  - Combinatorial expansion confirmed (Y/N + line ref): 
  - Multi-LLM synthesis code location: 
  - Adversarial task file/code location + count: 
  - Source-mode metadata field name + example: 
  - Share targets quote + location: 
  - Justification for tier:
```

---

## Criterion 3 — Multi-LLM Synthesis Routing and Anti-Leakage Policy

**Maximum Points: 10**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 3.1 | Named model families assigned per role: **frontier seed author**, **dev-tier bulk generator**, **judge filter** — with distinct API calls or configurations for each | List model names and their assigned roles from code/docs |
| 3.2 | **Explicit rotation rule** is codified preventing the same model from both generating and judging the same task | Quote the rule from code or `methodology.md` |
| 3.3 | **Judge filter uses a different model family** from the synthesis source | Confirm family-level separation (e.g., GPT-4 judges vs. Claude generates) |
| 3.4 | **Li et al., 2025** preference leakage paper is cited in the rationale | Find citation with author name and year |

### Tier Definitions

**Mastered — 10 pts**
All four sub-criteria above are satisfied without exception.

**Competent — 6 pts**
Multiple LLMs used in synthesis with some role separation, but at least one of the following is true:
- Routing policy not explicitly documented, OR
- Anti-leakage rotation not codified (only loosely mentioned), OR
- Preference leakage risk not acknowledged, OR
- No citation to Li et al. or equivalent literature

**Developing — 2 pts**
Multi-LLM use is mentioned but at least one of the following is true:
- Single model family used for both generation and judging, OR
- No documented routing policy, OR
- No awareness of preference leakage risk demonstrated

**Unsatisfactory — 0 pts**
No multi-LLM synthesis present, or a single LLM used throughout with no role differentiation.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 10
Evidence:
  - Frontier seed author model name + file ref: 
  - Dev-tier bulk generator model name + file ref: 
  - Judge filter model name + file ref: 
  - Family separation confirmed (Y/N): 
  - Rotation rule quote + location: 
  - Li et al. 2025 citation quote + location: 
  - Justification for tier:
```

---

## Criterion 4 — Judge Filter Pipeline Implementation

**Maximum Points: 15**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 4.1 | **Pointwise scoring** on ≥ 3 dimensions (input coherence, ground-truth verifiability, rubric clarity, or equivalent) on a 1–5 or analogous scale | List each dimension and its scale from code |
| 4.2 | **Inclusion thresholds** documented for each scored dimension | Quote threshold values |
| 4.3 | **Pairwise comparison logic** for similar or duplicate tasks is present | Locate and describe the pairwise logic |
| 4.4 | **Dev-tier model** used for high-volume bulk filtering | Confirm in code |
| 4.5 | **Eval-tier model** used only for spot-check calibration on a sampled subset (~50 tasks) | Confirm sampling logic and subset size |
| 4.6 | **Judge prompts** committed to the repo | Locate prompt files or prompt strings |
| 4.7 | **Filter logging** records per-task pass/fail and reasons | Inspect logging code for per-task records |

### Tier Definitions

**Mastered — 15 pts**
All seven sub-criteria above are satisfied without exception.

**Competent — 10 pts**
Judge filter exists and applies pointwise scoring with some thresholds, but at least one of the following is true:
- Only one or two dimensions scored, OR
- Pairwise comparison absent, OR
- Dev-tier vs. eval-tier separation not enforced, OR
- Judge prompts not visible in the repo

**Developing — 5 pts**
Some filtering exists but at least one of the following is true:
- Ad hoc thresholds with no justification, OR
- Single-dimension scoring only, OR
- No documentation of what the judge checks

**Unsatisfactory — 0 pts**
No judge filter present; all generated tasks enter the dataset unfiltered.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 15
Evidence:
  - Scored dimensions (list all with scale): 
  - Inclusion thresholds (quote each): 
  - Pairwise logic location + description: 
  - Dev-tier model name + bulk filtering confirmation: 
  - Eval-tier model name + spot-check subset size + line ref: 
  - Judge prompt file path(s): 
  - Logging code location + example log field: 
  - Justification for tier:
```

---

## Criterion 5 — Contamination Prevention Implementation

**Maximum Points: 15**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 5.1 | **N-gram overlap check** implemented with threshold < 8-gram overlap on input fields | Locate n-gram code; confirm n value and threshold |
| 5.2 | **Embedding similarity check** uses a cheap embedding model with cosine threshold < 0.85 | Locate embedding code; confirm model name and threshold value |
| 5.3 | **Time-shift verification logic** present for tasks referencing public data with documented signal-window provenance | Locate time-shift logic; confirm provenance documentation |
| 5.4 | Script applies to **both** held-out vs. training AND held-out vs. dev partition pairs | Confirm both pair types are checked |
| 5.5 | **Report-emitting code** is present (the report file itself is not graded) | Confirm output/report generation logic exists |
| 5.6 | All thresholds match spec or **justified deviations** are documented | Quote justification if deviating |

### Tier Definitions

**Mastered — 15 pts**
All six sub-criteria above are satisfied without exception.

**Competent — 10 pts**
Two of the three checks (n-gram, embedding, time-shift) implemented with thresholds documented, but at least one of the following is true:
- One check absent (commonly time-shift verification), OR
- Thresholds present but not justified, OR
- Check applied only to a subset of partition pairs

**Developing — 5 pts**
Some contamination awareness in code but at least one of the following is true:
- Only one check implemented (e.g., string overlap with no embedding), OR
- Thresholds hardcoded without documentation, OR
- No embedding model used

**Unsatisfactory — 0 pts**
No contamination check script in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 15
Evidence:
  - N-gram code location + n value + threshold: 
  - Embedding model name + cosine threshold + file ref: 
  - Time-shift logic location + provenance documentation: 
  - Partition pairs covered (list both): 
  - Report-emitting code location: 
  - Threshold justifications (quote if deviating): 
  - Justification for tier:
```

---

## Criterion 6 — Inter-Rater Agreement and Rubric Calibration

**Maximum Points: 10**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 6.1 | `inter_rater_agreement.md` documents a **30-task subset** double-labeling protocol | Confirm task count |
| 6.2 | Protocol specifies **24-hour gap** between first and second pass | Quote the time-gap specification |
| 6.3 | Protocol specifies second pass is **blind to first-pass labels** | Quote the blinding specification |
| 6.4 | **Per-dimension** agreement matrix or equivalent breakdown is reported (not just aggregate) | List dimensions with their agreement percentages |
| 6.5 | **Evidence of rubric revision** where any dimension fell below 80% agreement (changelog, rubric diff, or methodology note) | Locate the revision evidence |
| 6.6 | **Final agreement reported per dimension** after revision | Quote final per-dimension numbers |

### Tier Definitions

**Mastered — 10 pts**
All six sub-criteria above are satisfied without exception.

**Competent — 6 pts**
Inter-rater agreement file exists with some agreement numbers and a described protocol, but at least one of the following is true:
- No per-dimension breakdown (only aggregate), OR
- No evidence of rubric revision when threshold was missed, OR
- 24-hour gap not documented, OR
- Subset size unclear or smaller than 30

**Developing — 2 pts**
Some mention of agreement or self-consistency but at least one of the following is true:
- No formal protocol described, OR
- No agreement numbers reported, OR
- No per-dimension analysis

**Unsatisfactory — 0 pts**
No inter-rater agreement document in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 10
Evidence:
  - File location: 
  - Task count stated: 
  - 24-hour gap quote: 
  - Blinding specification quote: 
  - Per-dimension agreement values (list all): 
  - Revision evidence location + summary: 
  - Final post-revision per-dimension values: 
  - Justification for tier:
```

---

## Criterion 7 — Datasheet Completeness (Gebru and Pushkarna)

**Maximum Points: 5**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 7.1 | All **seven Gebru sections** present with non-stub content: Motivation, Composition, Collection Process, Preprocessing/Cleaning/Labeling, Uses, Distribution, Maintenance | Verify each section exists and has substantive prose |
| 7.2 | **Pushkarna layered detail** visible at three levels: telescopic (high-level summary), periscopic (section-level overview), microscopic (field-level specifics) | Identify each layer in the document |
| 7.3 | **Limitations and known biases** acknowledged with specifics (not generic) | Quote the limitation/bias statements |
| 7.4 | **License stated** with rationale committed | Quote license name and rationale |
| 7.5 | Document length is **within 3 to 5 pages** | Estimate or measure page length |

### Tier Definitions

**Mastered — 5 pts**
All five sub-criteria above are satisfied without exception.

**Competent — 3 pts**
Datasheet exists with most Gebru sections and non-trivial content in major sections, but at least one of the following is true:
- One or two Gebru sections missing or stubbed (commonly Maintenance or Distribution), OR
- No layered detail (single flat depth throughout), OR
- Limitations section generic or absent

**Developing — 1 pt**
A datasheet file exists but at least one of the following is true:
- Only some Gebru sections covered, OR
- Content is stubby or template-like (fill-in-the-blank style), OR
- No acknowledgment of limitations, OR
- Does not follow Datasheets for Datasets convention

**Unsatisfactory — 0 pts**
No datasheet present in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - File location: 
  - Gebru sections present (check each): Motivation[ ] Composition[ ] Collection[ ] Preprocessing[ ] Uses[ ] Distribution[ ] Maintenance[ ]
  - Pushkarna layers identified: Telescopic[ ] Periscopic[ ] Microscopic[ ]
  - Limitations/bias quote: 
  - License name + rationale quote: 
  - Estimated page length: 
  - Justification for tier:
```

---

## Criterion 8 — Path Declaration and Methodology Rationale

**Maximum Points: 10**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 8.1 | **Explicit path choice** (A, B, or C) declared in `methodology.md` | Quote the declaration |
| 8.2 | `methodology_rationale.md` cites **≥ 3 Week 10 trace IDs** | List each trace ID found |
| 8.3 | **≥ 2 read papers cited** with specific section references (not just author/year) | List each citation with its section reference |
| 8.4 | Rationale ties the chosen path to the **matching failure mode**: Path A → generation quality; Path B → inconsistency; Path C → trajectory | Quote the failure-mode-to-path mapping |
| 8.5 | **Alternative paths considered and dismissed** with reasoning | Quote the dismissal reasoning |

### Tier Definitions

**Mastered — 10 pts**
All five sub-criteria above are satisfied without exception.

**Competent — 6 pts**
Path declared and rationale exists with some Week 10 evidence and paper citations, but at least one of the following is true:
- Fewer than three trace IDs cited, OR
- Only one paper cited, OR
- Rationale names a failure mode but does not ground it in trace evidence, OR
- Alternative paths not considered

**Developing — 2 pts**
Path is named but at least one of the following is true:
- Rationale is generic, OR
- No Week 10 trace citations, OR
- No paper citations, OR
- Failure-mode-to-path mapping absent or mismatched

**Unsatisfactory — 0 pts**
No path declaration or methodology rationale present in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 10
Evidence:
  - Path declared (A/B/C) + quote + file: 
  - Trace IDs cited (list all): 
  - Paper citations with section refs (list each): 
  - Failure-mode-to-path mapping quote: 
  - Alternative paths dismissal quote: 
  - Justification for tier:
```

---

## Criterion 9 — Training Run Script and Hyperparameter Logging

**Maximum Points: 15**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 9.1 | All required hyperparameters are **explicit** in script or config: learning rate, batch size, LoRA rank, LoRA alpha, epochs, warmup steps, scheduler | List each with its value and file location |
| 9.2 | **Random seed fixed and visible** in code | Quote the seed assignment |
| 9.3 | **Backbone version pinned** to a specific Qwen 3.5 size with commit hash or HuggingFace revision | Quote the pinned version string |
| 9.4 | **LoRA-only configuration confirmed** (no full fine-tune) | Confirm LoRA adapter config; no frozen-layer bypass |
| 9.5 | **Loss logging code present** for training and validation (W&B, Tensorboard, file writer, or print logging) | Locate logging calls |
| 9.6 | **Training framework** (Unsloth or TRL) called consistently with path's algorithmic requirements: SFTTrainer for Path A; DPOTrainer/SimPO/ORPO for Path B; reward-modeling or PRM trainer for Path C | Confirm framework-to-path alignment |
| 9.7 | Expected **wall-time within 30–90 minutes** OR a justified deviation is documented | Quote wall-time estimate or justification |

### Tier Definitions

**Mastered — 15 pts**
All seven sub-criteria above are satisfied without exception.

**Competent — 10 pts**
Training script exists and core hyperparameters defined, but at least one of the following is true:
- Seed not pinned or not visible, OR
- Some hyperparameters hardcoded ad hoc without documentation, OR
- Backbone pinning vague (no hash or revision), OR
- Loss logging mechanism unclear

**Developing — 5 pts**
A training script exists but at least one of the following is true:
- Hyperparameters mostly default or undocumented, OR
- No random seed set, OR
- LoRA configuration unclear or not used, OR
- Script is fragmentary or incomplete

**Unsatisfactory — 0 pts**
No training script in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 15
Evidence:
  - Learning rate value + file ref: 
  - Batch size value + file ref: 
  - LoRA rank value + file ref: 
  - LoRA alpha value + file ref: 
  - Epochs value + file ref: 
  - Warmup steps value + file ref: 
  - Scheduler name + file ref: 
  - Random seed value + line ref: 
  - Backbone version string (with hash/revision): 
  - LoRA-only confirmation: 
  - Loss logging code location + type (W&B/TB/file/print): 
  - Training framework name + path alignment confirmation: 
  - Wall-time estimate or justification: 
  - Justification for tier:
```

---

## Criterion 10 — Ablation Methodology and Statistical Rigor

**Maximum Points: 15**

> **Scope Note:** This criterion grades **script source code only**. JSON/JSONL output files produced by those scripts are not inspected.

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 10.1 | **Delta A** implemented: trained component vs. Week 10 baseline on Tenacious-Bench held-out | Locate Delta A comparison code |
| 10.2 | **Paired bootstrap or equivalent statistical test** code visible with 95% CI and p-value computation | Locate bootstrap loop or equivalent; confirm CI and p-value output |
| 10.3 | **Delta B** implemented: same backbone with prompt-engineered version of the same intervention only (no training) | Confirm Delta B code path with no training call |
| 10.4 | **Delta C** handles τ²-Bench reference **informationally** without re-running (cost-discipline compliance) | Confirm no re-run call; confirm informational reference only |
| 10.5 | **Cost-Pareto instrumentation** present: timing logic, token counters, and per-task cost computation | Locate timing code, token counter, and per-task cost field |
| 10.6 | **Harness is parameterized** to run all four comparisons from a shared interface | Confirm single entry point or unified CLI/config |
| 10.7 | **Failure handling** visible in harness code | Locate try/except or equivalent error handling |

### Tier Definitions

**Mastered — 15 pts**
All seven sub-criteria above are satisfied without exception.

**Competent — 10 pts**
Delta A implemented with at least one of Delta B or Cost-Pareto and some statistical reporting code, but at least one of the following is true:
- Statistical significance not properly computed (no bootstrap, no CI), OR
- Delta B absent, OR
- Cost-Pareto reduced to aggregate with no per-task breakdown, OR
- Delta C re-runs τ²-Bench (cost-discipline violation)

**Developing — 5 pts**
Some comparison code exists but at least one of the following is true:
- Only Delta A attempted, OR
- No statistical test, OR
- No cost or latency measurement, OR
- Comparison logic is qualitative only

**Unsatisfactory — 0 pts**
No ablation code in the repository.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 15
Evidence:
  - Delta A code location + description: 
  - Bootstrap/statistical test code location + CI/p-value output confirmed: 
  - Delta B code location + no-training confirmation: 
  - Delta C informational reference location (no re-run confirmed): 
  - Cost-Pareto timing code location: 
  - Token counter code location: 
  - Per-task cost field name + location: 
  - Shared harness interface description + file ref: 
  - Failure handling code location: 
  - Justification for tier:
```

---

## Criterion 11 — README Reproducibility and Public Artifact References

**Maximum Points: 5**

### Sub-Criteria Checklist (ALL must be satisfied for Mastered)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 11.1 | **README at repo root** with overview, status, setup, and reproduction steps | Confirm file is at `/README.md` |
| 11.2 | **Dependency pinning** present (requirements.txt or equivalent) | Confirm pinned versions |
| 11.3 | **Quickstart** that walks through reproducing the headline number with specific commands | Quote the quickstart command sequence |
| 11.4 | **HuggingFace dataset URL** referenced | Quote the URL |
| 11.5 | **HuggingFace model URL** referenced (required if Path A or C declared) | Quote the URL or confirm Path B exemption |
| 11.6 | **Blog post URL** referenced | Quote the URL |
| 11.7 | **Community engagement URL** referenced (GitHub issue, workshop submission, PR, or community board post) | Quote the URL |
| 11.8 | **License file** present at repo root matching the documented choice | Confirm file name and license match |
| 11.9 | **Attribution and credits section** present in README | Confirm section exists with content |

### Tier Definitions

**Mastered — 5 pts**
All nine sub-criteria above are satisfied without exception.

**Competent — 3 pts**
README exists with most setup information and some artifact URLs, but at least one of the following is true:
- One or two artifact URLs absent (commonly community engagement URL), OR
- Quickstart present but vague (no specific commands), OR
- License file missing or not aligned with documented choice, OR
- Environment dependencies underspecified

**Developing — 1 pt**
A README exists but at least one of the following is true:
- No quickstart or reproduction steps, OR
- Most artifact URLs absent, OR
- Setup instructions incomplete

**Unsatisfactory — 0 pts**
No README at repo root, or README is fundamentally empty.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - README confirmed at /README.md (Y/N): 
  - Dependency file name + pinning confirmed: 
  - Quickstart command(s) quoted: 
  - HuggingFace dataset URL: 
  - HuggingFace model URL (or Path B exemption noted): 
  - Blog post URL: 
  - Community engagement URL + type: 
  - License file name + match confirmed: 
  - Attribution section confirmed (Y/N): 
  - Justification for tier:
```

---

## Final Score Summary Table

> The AI grading agent must complete this table after evaluating all criteria. A perfect score of 100/100 requires every criterion to be awarded Mastered.

| # | Criterion | Max Pts | Tier Awarded | Points Earned |
|---|-----------|---------|--------------|---------------|
| 1 | Audit Memo with Gap Analysis | 5 | | |
| 2 | Four-Mode Dataset Authoring | 15 | | |
| 3 | Multi-LLM Synthesis Routing & Anti-Leakage | 10 | | |
| 4 | Judge Filter Pipeline | 15 | | |
| 5 | Contamination Prevention | 15 | | |
| 6 | Inter-Rater Agreement & Rubric Calibration | 10 | | |
| 7 | Datasheet Completeness | 5 | | |
| 8 | Path Declaration & Methodology Rationale | 10 | | |
| 9 | Training Run Script & Hyperparameter Logging | 15 | | |
| 10 | Ablation Methodology & Statistical Rigor | 15 | | |
| 11 | README Reproducibility & Public Artifact References | 5 | | |
| | **TOTAL** | **100** | | |

---

## Overall Assessment

```
TOTAL SCORE: [ ] / 100

Criteria at Mastered:     [ ] / 11
Criteria at Competent:    [ ] / 11
Criteria at Developing:   [ ] / 11
Criteria at Unsatisfactory: [ ] / 11

Critical Gaps (any criterion not at Mastered):
1. 
2. 
3. 

Agent Certification:
"I have inspected actual file contents for each criterion, cited specific
evidence for every tier assignment, and awarded Mastered only where every
sub-criterion is fully satisfied. No rounding up was applied."

[ ] CONFIRMED
```

---

*RUBRIC.md — Final Repository Submission Evaluation Standard*
*Total possible: 100 points | Mastered across all 11 criteria required for full marks*