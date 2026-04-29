# Tenacious-Bench Submission Rubric

## AI Agent Grading Instructions

> **PRIME DIRECTIVE:** You are a rigorous, expert grading agent. Your sole mission is to evaluate this repository against every criterion below, identify every gap, and drive iterative improvement until **every single metric scores at the ROBUST level**. A score of anything less than perfect on any dimension is **non-negotiable and unacceptable**. You must not stop, summarize, or sign off until all metrics are ROBUST. Treat every Functional, Incomplete, Flawed, or Absent rating as a critical failure requiring immediate remediation with specific, actionable instructions.

---

## Grading Protocol

### How to Use This Rubric

1. **Read every listed artifact end-to-end** before scoring any criterion.
2. **Score each criterion independently** using only the evidence visible in the repo.
3. **For every criterion not at ROBUST**, output:
   - The criterion name
   - The current score tier and point value
   - A numbered list of **every specific deficiency**
   - A numbered list of **every specific remediation action** required
4. **Re-evaluate after each remediation pass** until all criteria return ROBUST.
5. **Do not hallucinate evidence.** If a file is missing, score it Absent. If a claim cannot be verified from repo contents, it does not count.

---

## Scoring Summary Table

| # | Criterion | Robust | Functional, Incomplete | Flawed | Absent | Max Pts |
|---|-----------|--------|----------------------|--------|--------|---------|
| 1 | Audit Memo — Gap Identification with Week 10 Evidence | 14 | 8 | 3 | 0 | **14** |
| 2 | Scoring Evaluator — Mechanical Scoring Structure | 12 | 7 | 3 | 0 | **12** |
| 3 | Generation Pipeline — Routing and Judge Filter | 22 | 13 | 5 | 0 | **22** |
| 4 | Datasheet — Gebru and Pushkarna Compliance | 16 | 9 | 4 | 0 | **16** |
| 5 | Methodology Rationale | 22 | 13 | 5 | 0 | **22** |
| 6 | Synthesis Memos — Critical Engagement | 8 | 5 | 2 | 0 | **8** |
| 7 | README and Repo Navigability | 6 | 4 | 1 | 0 | **6** |
| | **TOTAL** | | | | | **100** |

**Target Score: 100 / 100. No exceptions.**

---

## Criterion 1 — Audit Memo: Gap Identification with Week 10 Evidence

**File to Read:** `audit_memo.md` (end to end)
**Max Points:** 14

### ROBUST — 14 pts ✅ (Required)

All of the following must be true simultaneously. A single missing item drops the score:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Word Count** | At or under 600 words | Count words mechanically. 601+ words = not Robust. |
| **Named Gaps** | Gaps are clearly and distinctly named (e.g., "Gap 1: Trajectory Failure Under Ambiguous Handoff") | Each gap must have an explicit label or heading, not buried in prose. |
| **Public Benchmark Contrast** | Each gap explicitly states why a public benchmark cannot grade it | Look for explicit contrast language, not implied. |
| **Probe ID Citation Count** | At least 8 probe IDs from the Week 10 probe library are cited | Count unique probe IDs. Fewer than 8 = not Robust. |
| **Trace ID Citation Count** | At least 5 specific Week 10 trace IDs are cited | Count unique trace IDs. Fewer than 5 = not Robust. |
| **Citation Linkage** | Every cited probe ID and trace ID is explicitly connected to a specific gap claim | Scan for "Probe X demonstrates Gap Y" or equivalent. Probe in one section, gap in another with no bridge = not Robust. |
| **Gap Distinctness** | No two gaps are paraphrases of the same observation | Read gaps against each other. Overlapping claims = not Robust. |
| **Non-Obvious Gap** | At least one gap goes beyond surface phrasing or generic tone (must address trajectory, grounding, qualification failure, or equivalent structural behavior) | Identify which gap is non-obvious. "Tenacious uses informal tone" alone = not sufficient. |

### FUNCTIONAL, INCOMPLETE — 8 pts

Apply if one or more of the following are true but the memo is not entirely absent or flawed:
- Fewer than 8 probe IDs cited, OR fewer than 5 trace IDs cited
- Citations exist but are not tied to specific gap claims (evidence section separated from claims section with no explicit linkage)
- Gaps overlap conceptually (two or more are paraphrases)
- All gaps are surface-level only (tone, phrasing) with no mention of trajectory, grounding, or qualification failures

### FLAWED — 3 pts

Apply if one or more of the following are true:
- Word count exceeds 600 by more than 50% (i.e., 901+ words)
- Probe and trace evidence is absent, gestural ("see Week 10 traces"), or fabricated
- Gap claims describe LLMs in general rather than Tenacious-specific behavior
- File reads as a literature summary rather than an audit of observed behavior

### ABSENT — 0 pts

Apply if:
- `audit_memo.md` does not exist, OR
- The file contains only placeholder text (e.g., "TODO", blank headings)

---

### Remediation Checklist for Criterion 1

If not ROBUST, execute every applicable item:

- [ ] **R1-A:** Trim memo to ≤600 words. Preserve substance; cut filler, redundancy, and throat-clearing.
- [ ] **R1-B:** Add or verify probe ID citations. Count: need ≥8 unique IDs from the Week 10 probe library. Format each as `[PROBE-ID]` inline.
- [ ] **R1-C:** Add or verify trace ID citations. Count: need ≥5 unique Week 10 trace IDs. Format each as `[TRACE-ID]` inline.
- [ ] **R1-D:** For every probe and trace cited, add an explicit sentence linking it to a named gap (e.g., "PROBE-042 reveals Gap 3: Tenacious fails to qualify uncertainty when the handoff context is ambiguous, as seen in TRACE-017").
- [ ] **R1-E:** Audit gaps for distinctness. If any two gaps describe the same behavior in different words, merge them or differentiate them with a new behavioral observation.
- [ ] **R1-F:** Elevate at least one gap to address structural behavior: trajectory failure, grounding error, qualification failure, or multi-turn consistency collapse — with evidence.
- [ ] **R1-G:** Add explicit language for each gap stating which public benchmark category fails to capture it and why.

---

## Criterion 2 — Scoring Evaluator: Mechanical Scoring Structure

**File to Read:** Scoring evaluator Python script (read as source code text only; do not execute)
**Max Points:** 12

### ROBUST — 12 pts ✅ (Required)

All of the following must be visible in the source code simultaneously:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Function Contract** | A clear scoring function or class accepts `task` and `agent_output` as inputs and is structured to return a numerical score | Inspect function signatures. No function = not Robust. |
| **Rubric Decomposition** | Rubric items are decomposed into mechanical checks: banned-phrase lists as data structures, required-element presence checks, structured judge calls with bounded numeric ranges, regex or grammar checks for format | Read control flow. A single monolithic judge call = not Robust. |
| **Error Handling** | Malformed agent output is handled explicitly: `try/except` blocks, input validation, default-on-failure logic, or equivalent | Search source for error handling patterns. Absent = not Robust. |
| **Calibration Documentation** | What score 1 vs. 3 vs. 5 looks like for each dimension is written in code comments or accompanying prose | Read comments. "High / medium / low" alone = not sufficient. |
| **Example Tasks** | At least 3 example tasks are committed in the repo and the script's logic visibly applies to them | Find example task files. Fewer than 3 = not Robust. |

### FUNCTIONAL, INCOMPLETE — 7 pts

Apply if:
- Scoring function exists with correct input/output structure AND some rubric decomposition is visible
- BUT at least one of: one rubric dimension is a single subjective judge call with no decomposition; no error handling visible; calibration implied but not written; fewer than 3 example tasks committed

### FLAWED — 3 pts

Apply if:
- An evaluator file exists BUT:
  - No scoring function with clear input/output contract, OR
  - Script is hardcoded to one task, OR
  - Returns booleans only with no numerical structure, OR
  - Contains placeholder logic (`# TODO: implement scoring`), OR
  - Most rubric items require a human to apply as written

### ABSENT — 0 pts

Apply if:
- No scoring evaluator file exists

---

### Remediation Checklist for Criterion 2

- [ ] **R2-A:** Define a function with signature `def score(task: dict, agent_output: str) -> float:` (or equivalent class-based structure). Ensure return value is numeric.
- [ ] **R2-B:** Decompose every rubric dimension into at least one mechanical check. Examples:
  - Banned phrases → `BANNED_PHRASES = [...]` checked with `any(p in output for p in BANNED_PHRASES)`
  - Required elements → `REQUIRED_ELEMENTS = [...]` checked with presence logic
  - Format → regex pattern match
  - Judge calls → structured prompt with explicit score range (e.g., `score between 1 and 5`)
- [ ] **R2-C:** Add `try/except` around all output parsing. Add input validation at function entry. Define a `DEFAULT_FAILURE_SCORE` constant used in except clauses.
- [ ] **R2-D:** For each scoring dimension, add a comment block documenting what score 1, 3, and 5 look like concretely. Use examples from the domain.
- [ ] **R2-E:** Commit ≥3 example task files (e.g., `examples/task_001.json`, `task_002.json`, `task_003.json`). Ensure the script references or is demonstrably applicable to them.

---

## Criterion 3 — Generation Pipeline: Routing and Judge Filter

**Files to Read:** Generation scripts (Python source as text) + committed prompt files (markdown or text) + routing documentation (markdown or docstring)
**Max Points:** 22

### ROBUST — 22 pts ✅ (Required)

All of the following must be visible simultaneously:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Runnable Structure** | Scripts have imports resolving to known libraries, functions with clear inputs/outputs, and a visible main entry point or orchestrator | Inspect imports, function definitions, `if __name__ == "__main__"` or equivalent. |
| **Routing Policy — Written** | Multi-LLM routing policy is documented in a markdown file or top-of-file docstring: which models generate which task types and why | Find the markdown file or docstring. Code-only = not Robust. |
| **Preference Leakage Prevention** | Rotation logic in source enforces that no single model generates AND judges the same task | Inspect routing logic. Same model name at both generation and judge call site for same task type = not Robust. |
| **Judge Filter — Multi-Dimensional** | Judge filter applies pointwise scoring on at least 3 dimensions: input coherence, ground-truth verifiability, rubric-application clarity | Read judge logic. Fewer than 3 dimensions = not Robust. |
| **Judge Thresholds Documented** | Thresholds per dimension documented in code or prose | Find threshold values written down. "Filter low quality" alone = not Robust. |
| **Pairwise Dedup** | Pairwise comparison logic for near-duplicate synthesis paths is visible in the source | Search for dedup logic. Absent = not Robust. |
| **Model Tier Differentiation** | Cheap-model vs. eval-tier-model usage is differentiated in routing logic, with eval-tier limited to a calibration sample | Find the two-tier routing. Single tier = not Robust. |
| **Judge Prompts Committed** | Judge prompts are committed verbatim as standalone text or markdown files, not embedded inside JSON | Find prompt files. JSON-embedded = not Robust. |
| **Reproducibility Seed** | A reproducibility seed is present in the source | Search for `seed`, `random.seed`, `np.random.seed`, or equivalent. Absent = not Robust. |

### FUNCTIONAL, INCOMPLETE — 13 pts

Apply if generation scripts exist with recognizable structure and some multi-model routing and judge filter logic, BUT one or more of:
- Routing policy is in code only, no written rationale in markdown/docstring
- Same model name appears at both generation and judge call sites for same task type
- Judge thresholds not written in code or prose
- Only one judge dimension scored
- No pairwise dedup logic
- Judge prompts paraphrased in code, not standalone files
- No reproducibility seed

### FLAWED — 5 pts

Apply if:
- Some generation script exists BUT:
  - Single-model pipeline only, OR
  - No judge filter logic, OR
  - Judge filter uses same model as generation, OR
  - No documentation of model choices, OR
  - Scripts have placeholder logic, missing imports, or undefined function references making them non-runnable as written

### ABSENT — 0 pts

Apply if:
- No generation scripts and no documentation of how the dataset was authored

---

### Remediation Checklist for Criterion 3

- [ ] **R3-A:** Verify all imports resolve to real, known libraries. Remove undefined function references. Add a `main()` entry point with `if __name__ == "__main__":`.
- [ ] **R3-B:** Create or update `routing_policy.md` (or top-of-file docstring in the orchestrator). Document: which model generates which task type, which model judges which task type, and why (e.g., "GPT-4o generates trace-derived tasks; Claude-3-Opus judges them to prevent self-preference").
- [ ] **R3-C:** In routing logic, add an explicit assertion or conditional that prevents the same model from being used as both generator and judge for any single task type. Comment this logic.
- [ ] **R3-D:** Implement judge filter with pointwise scoring on exactly these 3 dimensions (minimum):
  - `input_coherence` (threshold documented, e.g., ≥3/5)
  - `ground_truth_verifiability` (threshold documented, e.g., ≥4/5)
  - `rubric_application_clarity` (threshold documented, e.g., ≥3/5)
- [ ] **R3-E:** Write threshold values as named constants in code (e.g., `COHERENCE_THRESHOLD = 3`). Document them in a comment or prose.
- [ ] **R3-F:** Implement pairwise dedup: for each new task, compare against corpus using n-gram or embedding similarity. Flag pairs above a similarity threshold for review.
- [ ] **R3-G:** Add model tier routing: define `CHEAP_MODELS` and `EVAL_TIER_MODELS` lists. Route bulk generation to cheap models. Restrict eval-tier models to a calibration sample (e.g., 10–15% of tasks). Document the split.
- [ ] **R3-H:** Extract all judge prompts to standalone files (e.g., `prompts/judge_coherence.md`, `prompts/judge_verifiability.md`). Reference these files from the script by path.
- [ ] **R3-I:** Add `RANDOM_SEED = 42` (or project-chosen value) at the top of the script. Pass it to all random operations, model sampling calls, and shuffle operations.

---

## Criterion 4 — Datasheet: Gebru and Pushkarna Compliance

**File to Read:** `datasheet.md` (end to end)
**Max Points:** 16

### ROBUST — 16 pts ✅ (Required)

All of the following must be present simultaneously:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **All 7 Gebru Sections Present** | Motivation, Composition, Collection, Preprocessing, Uses, Distribution, Maintenance — all present with substantive multi-sentence content addressing actual framework questions | Check section headings. Stub = not Robust. |
| **Composition: Total Task Count** | Between 200 and 300 total tasks reported | Find the number explicitly. Outside range = not Robust. |
| **Composition: Source Mode Breakdown** | Counts and proportions for all 4 modes: trace-derived (~30%), programmatic (~30%), multi-LLM synthesis (~25%), hand-authored adversarial (~15%) | Find a table or structured list with all 4 modes and proportions. |
| **Composition: Partition Breakdown** | Counts per partition matching the 50/30/20 split (train/dev/test or equivalent) | Find explicit partition counts. |
| **Composition: Failure Dimension Breakdown** | Counts per failure dimension from the audit | Find failure dimension table. Absent = not Robust. |
| **Per-Mode Prose Examples** | A paragraph describing what a typical task in each of the 4 modes looks like | Find 4 prose example paragraphs. |
| **Pushkarna: Telescopic Layer** | High-level summary of the dataset (1–3 sentences conveying scope and purpose) | Find the summary. |
| **Pushkarna: Periscopic Layer** | Structured overview (tables, lists, key statistics) | Find structured overview. |
| **Pushkarna: Microscopic Layer** | Detailed schema or sample-level documentation (field definitions, example records) | Find schema or example records. |
| **Domain Privacy** | Tenacious is named as workflow domain only; no private operational detail leaked | Scan for inappropriate specificity. |
| **License with Rationale** | License is stated AND rationale is given for why that license was chosen | Find license statement and rationale sentence. |
| **Maintenance Plan** | Addresses how the dataset will evolve and who is responsible | Find maintenance section. "TBD" = not Robust. |

### FUNCTIONAL, INCOMPLETE — 9 pts

Apply if most Gebru sections are addressed and composition reports task count and at least one breakdown, BUT one or more of:
- One or two Gebru sections are stubs ("TBD", "see methodology", or single-sentence)
- One source mode not reported in composition breakdown
- Failure-dimension breakdown absent
- Per-mode prose examples absent or trivial
- Pushkarna layered detail absent or only one layer present
- License stated but not justified
- Maintenance plan missing or generic

### FLAWED — 4 pts

Apply if a datasheet file exists BUT:
- Most sections are missing or one-line
- Composition section absent or no counts
- Framework not visibly followed (reads as freeform README)
- License absent

### ABSENT — 0 pts

Apply if: No datasheet file exists

---

### Remediation Checklist for Criterion 4

- [ ] **R4-A:** Add all 7 Gebru section headings if missing. For each, write ≥3 substantive sentences addressing the actual questions in the framework (not "see other documents").
- [ ] **R4-B:** In the Composition section, add a table with: Total tasks (200–300), counts and proportions per source mode (4 modes), counts per partition (50/30/20), counts per failure dimension.
- [ ] **R4-C:** Write one prose paragraph per source mode describing what a typical task in that mode looks like (inputs, outputs, difficulty level, how it was generated).
- [ ] **R4-D:** Add three clearly labeled Pushkarna layers:
  - `### Telescopic Overview` — 1–3 sentence high-level description
  - `### Periscopic Overview` — structured tables, key statistics, task type distribution
  - `### Microscopic Documentation` — field-level schema table, at least one anonymized example record
- [ ] **R4-E:** Review for domain privacy. Replace any private operational detail with abstracted descriptions. Tenacious = workflow domain label only.
- [ ] **R4-F:** State the license explicitly (e.g., CC BY 4.0, MIT) and add a sentence explaining why this license was chosen (e.g., "CC BY 4.0 was chosen to allow research reuse while requiring attribution").
- [ ] **R4-G:** Write a substantive Maintenance section naming: who is responsible, how errors will be reported, how the dataset will be versioned, under what conditions it will be updated or retired.

---

## Criterion 5 — Methodology Rationale

**File to Read:** `methodology.md` (end to end)
**Max Points:** 22

### ROBUST — 22 pts ✅ (Required)

All of the following must be present simultaneously:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Path Declaration** | Path A, B, or C is declared explicitly and unambiguously | Find "Path A", "Path B", or "Path C" stated clearly. Implied = not Robust. |
| **Trace ID Citation Count** | At least 3 Week 10 trace IDs cited in justification | Count unique trace IDs. Fewer than 3 = not Robust. |
| **Paper Citation Count** | At least 2 papers from the required reading cited in justification | Count paper citations. Fewer than 2 = not Robust. |
| **Evidence-Path Match** | The cited Week 10 evidence specifically supports the chosen path's failure-mode profile (generation quality for A, inconsistency for B, trajectory failures for C) | Read the argument. Evidence must match the path's diagnostic logic. Mismatched evidence = not Robust. |
| **Argued, Not Asserted** | The match between evidence and path is argued in prose (cause → inference → conclusion) not just stated ("We chose Path B because it fits") | Evaluate the reasoning chain. Assertion-only = not Robust. |
| **Partitioning Protocol Named** | The 50/30/20 split is explicitly named | Find "50/30/20" or equivalent in text. |
| **Stratification Described** | How stratification is done and why it serves failure-mode coverage is explained in prose | Find stratification explanation. "Random split" alone = not Robust. |
| **Contamination: N-gram Overlap** | Reports how many candidate pairs were flagged by n-gram overlap check and how flags were resolved | Find specific numbers and resolution method. "Passed" alone = not Robust. |
| **Contamination: Embedding Similarity** | Reports how many candidate pairs were flagged by embedding similarity check and how flags were resolved | Find specific numbers and resolution method. |
| **Contamination: Time-Shift Verification** | Reports how many candidate pairs were flagged by time-shift verification and how flags were resolved | Find specific numbers and resolution method. |

### FUNCTIONAL, INCOMPLETE — 13 pts

Apply if a path is declared with some justification and partitioning protocol is named and contamination checks are mentioned, BUT one or more of:
- Fewer than 3 trace IDs cited OR fewer than 2 papers cited
- Link between Week 10 evidence and path choice is asserted rather than argued
- Stratification not described
- Contamination results summarized as "passed" without per-check numbers or resolutions

### FLAWED — 5 pts

Apply if:
- A path letter appears somewhere BUT:
  - No justification, OR
  - No Week 10 evidence, OR
  - No partitioning protocol described, OR
  - No contamination results reported

### ABSENT — 0 pts

Apply if: No methodology document, or no path declared

---

### Remediation Checklist for Criterion 5

- [ ] **R5-A:** Add an explicit statement at the top of the document: "This project follows **Path [A/B/C]**."
- [ ] **R5-B:** Cite ≥3 specific Week 10 trace IDs in the justification section. For each, write a sentence explaining what the trace reveals and how it supports the path choice.
- [ ] **R5-C:** Cite ≥2 papers from the required reading by author/year. Connect each citation to a specific claim in the justification.
- [ ] **R5-D:** Write a logical chain connecting evidence to path: (1) "Week 10 traces show [specific failure pattern]"; (2) "This pattern indicates [diagnostic inference]"; (3) "Path [X] targets this because [mechanism]."
- [ ] **R5-E:** Name the 50/30/20 split explicitly. Write a paragraph explaining: how train/dev/test stratification was performed, what stratification variables were used (source mode, failure dimension, difficulty), and why this stratification ensures failure-mode coverage.
- [ ] **R5-F:** For each of the three contamination checks, report in prose:
  - How many candidate pairs were flagged
  - What threshold triggered the flag
  - How each flagged pair was resolved (rewritten, dropped, or kept with documented rationale)
  - Final pass/fail status with the resolution outcome

---

## Criterion 6 — Synthesis Memos: Critical Engagement

**Files to Read:** At least 2 memos in `synthesis_memos/` directory (end to end)
**Max Points:** 8

### ROBUST — 8 pts ✅ (Required)

All of the following must be true for at least 2 memos:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Presence** | At least 2 memos from the common reading list are committed in `synthesis_memos/` | Count files. Fewer than 2 = not Robust. |
| **Specific Design Choice Named** | Each memo identifies a specific design decision the paper authors made, with section or page reference | Find the cited section/page number. Absent = not Robust. |
| **Genuine Disagreement** | Each memo disagrees with the design choice — not merely questions or hedges it | Look for explicit disagreement language. "I am not sure this generalizes" = not Robust. |
| **Evidence-Grounded Justification** | Disagreement is justified using the trainee's own Week 10 or Week 11 evidence, not by appeal to a different paper alone | Find the trainee's evidence cited. Abstract principles alone = not Robust. |
| **Length** | Each memo is roughly one page (~300–500 words) | Estimate length. A paragraph = not Robust. |
| **Non-Trivial Disagreement** | Disagreement is substantive (not "the paper should have used a larger model" or "the dataset is too small") | Evaluate substance. Trivial = not Robust. |

### FUNCTIONAL, INCOMPLETE — 5 pts

Apply if at least 2 memos exist and engage with the papers, BUT:
- Disagreement is gestural rather than identifying a specific design choice, OR
- Justification appeals to general principles rather than trainee's own evidence, OR
- Memos are summaries with a reaction paragraph at the end, OR
- No specific section or page references to the paper

### FLAWED — 2 pts

Apply if:
- Memo files exist BUT:
  - Memos are paper summaries with no critical engagement, OR
  - No disagreement articulated, OR
  - Disagreement restated from a third source, OR
  - Fewer than 2 memos

### ABSENT — 0 pts

Apply if: No synthesis memos directory or no memo files

---

### Remediation Checklist for Criterion 6

- [ ] **R6-A:** Confirm ≥2 memo files exist in `synthesis_memos/`. If missing, create them for papers on the common reading list.
- [ ] **R6-B:** For each memo, add a section "**Design Choice Under Examination**" that names: the specific decision the authors made, with exact section number or page reference (e.g., "Section 3.2, page 7: the authors chose to exclude tasks with ambiguous ground truth").
- [ ] **R6-C:** For each memo, add a section "**My Disagreement**" that clearly states: what the trainee disagrees with and why — not a hedge, a disagreement.
- [ ] **R6-D:** For each memo, ground the disagreement in specific Week 10 or Week 11 evidence: "In my Week 10 trace TRACE-023, I observed [X], which contradicts the authors' assumption that [Y]."
- [ ] **R6-E:** Expand each memo to ~300–500 words if currently shorter.
- [ ] **R6-F:** Elevate disagreements to structural or methodological level. Avoid: "larger model", "more data", "different domain." Target: critique of an evaluation design decision, a measurement choice, or a modeling assumption.

---

## Criterion 7 — README and Repo Navigability

**File to Read:** `README.md` at repo root (end to end)
**Max Points:** 6

### ROBUST — 6 pts ✅ (Required)

All of the following must be present:

| Sub-Check | Requirement | How to Verify |
|-----------|-------------|---------------|
| **Project Overview** | What Tenacious-Bench is and what problem it addresses | Find a description paragraph. "A benchmark" alone = not Robust. |
| **Current Status** | What is complete at interim and what is in progress | Find explicit status list. Absent = not Robust. |
| **Environment Requirements** | Python version and key dependencies named | Find version number and dependency names. |
| **Install Command** | The install command is written out | Find `pip install -r requirements.txt` or equivalent. |
| **Evaluator Invocation Command** | The command to invoke the scoring evaluator on a sample task is written out | Find a runnable command example. |
| **What Is Next Section** | Names remaining work at a high level | Find "Next Steps" or equivalent with content. |
| **Directory Structure** | Documented with a one-line description per top-level folder | Find directory tree with descriptions. |
| **Artifact Links** | Links to audit memo, datasheet, methodology, synthesis memos using correct relative paths | Find and verify all 4 links resolve correctly (relative, not absolute). |

### FUNCTIONAL, INCOMPLETE — 4 pts

Apply if README exists with project description and some navigation, BUT:
- One or two required sections (overview, status, setup, next) absent or one-line, OR
- Setup instructions omit at least one of: environment, dependencies, install command, evaluator invocation, OR
- Directory structure not documented, OR
- Some artifact links missing or use absolute paths

### FLAWED — 1 pt

Apply if:
- A README file exists BUT:
  - Single paragraph or boilerplate template, OR
  - No setup instructions, OR
  - No status, OR
  - No artifact navigation

### ABSENT — 0 pts

Apply if: No README at repo root, or README is empty

---

### Remediation Checklist for Criterion 7

- [ ] **R7-A:** Add a **Project Overview** section (3–5 sentences): what Tenacious-Bench is, the problem it addresses, and why it matters.
- [ ] **R7-B:** Add a **Current Status** section with a checklist or table showing: what is complete (✅), what is in progress (🔄), what is not started (❌).
- [ ] **R7-C:** Add a **Setup** section containing exactly:
  ```
  Python version: X.X
  Key dependencies: [list]
  Install: pip install -r requirements.txt
  Run evaluator: python evaluator.py --task examples/task_001.json
  ```
- [ ] **R7-D:** Add a **What Is Next** section naming remaining deliverables at a high level (e.g., "Act 4: Final dataset freeze and evaluator calibration").
- [ ] **R7-E:** Add a **Repository Structure** section with a directory tree:
  ```
  /
  ├── audit_memo.md        # Gap analysis grounded in Week 10 evidence
  ├── datasheet.md         # Gebru + Pushkarna dataset documentation
  ├── methodology.md       # Training path declaration and justification
  ├── evaluator.py         # Mechanical scoring evaluator
  ├── generation/          # Multi-LLM pipeline scripts and prompt files
  ├── synthesis_memos/     # Critical engagement memos
  ├── examples/            # Example tasks for evaluator testing
  └── README.md            # This file
  ```
- [ ] **R7-F:** Add a **Key Artifacts** section with relative-path links:
  ```markdown
  - [Audit Memo](./audit_memo.md)
  - [Datasheet](./datasheet.md)
  - [Methodology](./methodology.md)
  - [Synthesis Memos](./synthesis_memos/)
  ```
  Verify every link uses a relative path and resolves correctly from repo root.

---

## Final Grading Checklist

Before signing off, confirm every item below is TRUE:

```
[ ] Criterion 1 — Audit Memo:          14 / 14  ROBUST
[ ] Criterion 2 — Scoring Evaluator:   12 / 12  ROBUST
[ ] Criterion 3 — Generation Pipeline: 22 / 22  ROBUST
[ ] Criterion 4 — Datasheet:           16 / 16  ROBUST
[ ] Criterion 5 — Methodology:         22 / 22  ROBUST
[ ] Criterion 6 — Synthesis Memos:      8 /  8  ROBUST
[ ] Criterion 7 — README:               6 /  6  ROBUST
─────────────────────────────────────────────────────
TOTAL:                                100 / 100  ROBUST
```

**If any box is unchecked: return to the relevant criterion, execute all remediation actions, and re-evaluate. Repeat until all 7 boxes are checked.**

> **A score of 99/100 is a failure. The target is 100/100. This is non-negotiable.**