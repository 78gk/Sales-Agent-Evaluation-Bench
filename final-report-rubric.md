# RUBRIC.md — Final Report Submission Evaluation Standard

> **AI Grading Agent Instructions — Read Before Scoring**
>
> You are a professional AI engineering rubric auditor evaluating a **final report submission memo**. Your task is to evaluate this document **honestly, strictly, and completely**. You must:
> - Inspect **actual written content**, not section headings alone
> - Award **Mastery** only when **every sub-criterion** listed under that tier is fully satisfied
> - Never award partial credit within a tier; select the highest tier where **all** conditions are met
> - Never round up due to effort, proximity to threshold, or rhetorical quality
> - A perfect score of **40/40** is only achievable if **every criterion is Mastered**
> - After scoring each criterion, provide **explicit evidence** (page reference, paragraph number, or direct quotation) that justifies the assigned tier
> - If evidence is missing, ambiguous, or hedged, default to the **lower tier**
> - Produce a **Final Score Summary Table** at the end

---

## Scoring Overview

| # | Criterion | Mastery | Functional but Incomplete | Fundamentally Flawed | Absent |
|---|-----------|---------|--------------------------|----------------------|--------|
| 1 | Executive Summary & Headline Delta A Reporting | 5 pts | 3 pts | 1 pt | 0 pts |
| 2 | Delta B Honesty (Prompt-Engineered Baseline) | 5 pts | 3 pts | 1 pt | 0 pts |
| 3 | Cost per Task Delta with Production Implication | 5 pts | 3 pts | 1 pt | 0 pts |
| 4 | Production Recommendation with Specific Conditions | 5 pts | 3 pts | 1 pt | 0 pts |
| 5 | Tenacious-Bench v0.2 Coverage Gap Identification | 5 pts | 3 pts | 1 pt | 0 pts |
| 6 | Ground Truth Faithfulness Self-Critique | 5 pts | 3 pts | 1 pt | 0 pts |
| 7 | Unresolved Training Failure Acknowledgment | 5 pts | 3 pts | 1 pt | 0 pts |
| 8 | Kill-Switch Trigger Condition | 5 pts | 3 pts | 1 pt | 0 pts |
| | **TOTAL** | **40 pts** | | | |

---

## Criterion 1 — Executive Summary and Headline Delta A Reporting

**Maximum Points: 5**

> **Scope:** Whether Page 1 opens with a tight three-sentence executive summary and reports the Tenacious-Bench held-out lift with statistical rigor that a non-technical executive reader can interpret. Numerical claims are evaluated as communicated in the memo (precision, uncertainty framing, honesty signals). Whether the underlying number is correct is the repo grader's responsibility, not this criterion's.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 1.1 | Executive summary is **exactly three sentences** — not more, not fewer | Count sentences; reject if summary "runs longer than three sentences and buries the headline below scaffolding" |
| 1.2 | Summary is **self-contained**: a reader can extract what happened without reading further | Confirm the three sentences alone convey the result, intervention, and implication |
| 1.3 | Headline Delta A **point estimate** is reported | Quote the numeric value |
| 1.4 | **95% confidence interval with explicit bounds** is reported (e.g., [+2.1%, +6.4%]) | Quote the interval; reject if stated without bounds |
| 1.5 | **Statistical test is named** (paired bootstrap, p-value, or equivalent) | Quote the test name |

### Tier Definitions

**Mastery — 5 pts**
All five sub-criteria above are satisfied without exception. Three-sentence summary is present and self-contained. Headline Delta A is reported with point estimate, 95% confidence interval with bounds, and the paired statistical test named. The reader can extract what happened from the summary alone without reading further.

**Functional but Incomplete — 3 pts**
A summary and headline number are reported and lift direction is clear, but at least one of the following is true:
- Confidence interval is absent or stated without explicit bounds, OR
- The statistical test is not named, OR
- The summary runs longer than three sentences and buries the headline below scaffolding

**Fundamentally Flawed — 1 pt**
A summary section exists but at least one of the following is true:
- No quantitative headline number, OR
- The number is reported without any uncertainty framing, OR
- The summary is generic and avoids committing to a specific result

**Absent — 0 pts**
No executive summary on Page 1, or no Delta A reported on Page 1.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of executive summary:
  - Sentence count of summary:
  - Self-contained confirmation (Y/N + explanation):
  - Point estimate quoted:
  - 95% CI with explicit bounds quoted:
  - Statistical test name quoted:
  - Justification for tier:
```

---

## Criterion 2 — Delta B Honesty (Prompt-Engineered Baseline)

**Maximum Points: 5**

> **Scope:** Whether the memo reports the prompt-engineered baseline comparison on the same backbone with the same intervention shape, and reports the result honestly even when unfavorable to the trained component. The challenge document explicitly names a negative result here as a legitimate, publishable finding that must be reported honestly.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 2.1 | The prompt-engineered baseline comparison is reported with its **own point estimate** | Quote the numeric value for the prompt baseline |
| 2.2 | Framing makes clear the prompt baseline used the **same backbone and same intervention shape** (not just "we also tried prompting") | Quote the framing sentence confirming backbone and shape parity |
| 2.3 | If the result is **negative or null**, it is stated plainly **without rhetorical hedging** | Scan for softening language; flag phrases like "also performed reasonably" |
| 2.4 | If the result is **positive**, the memo **acknowledges what this implies** for the training claim | Confirm the implication is addressed, not buried |

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. The prompt-engineered baseline comparison is reported with its own point estimate. The comparison framing makes clear the prompt baseline used the same backbone and same intervention shape. If negative or null, stated plainly without rhetorical hedging. If positive, the memo acknowledges what this implies for the training claim.

**Functional but Incomplete — 3 pts**
The prompt baseline comparison is mentioned and a result is given, but at least one of the following is true:
- Framing is vague — no clarity on whether the prompt baseline used the same backbone, OR
- A negative result is softened with hedging language (e.g., "the prompt baseline also performed reasonably") that obscures the finding

**Fundamentally Flawed — 1 pt**
Some mention of prompting or an alternative approach exists but at least one of the following is true:
- No real comparison reported, OR
- The prompt baseline is reported only when favorable, OR
- The prompt baseline is conflated with the Week 10 agent baseline

**Absent — 0 pts**
No prompt-engineered baseline comparison appears in the memo.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of Delta B section:
  - Point estimate for prompt baseline quoted:
  - Backbone + intervention shape confirmation quoted:
  - Result direction (positive / negative / null):
  - Hedging language detected (Y/N — quote any flagged phrases):
  - Implication for training claim addressed (Y/N + quote):
  - Justification for tier:
```

---

## Criterion 3 — Cost per Task Delta with Production Implication

**Maximum Points: 5**

> **Scope:** Whether Page 1 reports per-task cost (and ideally latency) with and without the trained component, framed in terms an executive can use for a deployment decision.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 3.1 | Per-task cost is reported as a **delta or side-by-side pair** (with and without trained component) | Quote both cost values |
| 3.2 | The unit is **concrete**: dollars per task, cents per task, or tokens per task with a price anchor | Quote the unit and verify a monetary anchor is provided if tokens are used |
| 3.3 | **Latency is reported**, OR its omission is **explicitly justified** in the text | Quote latency figure or justification for omission |
| 3.4 | The cost figure is **connected to the production recommendation** rather than presented as a standalone number | Quote the connecting sentence |

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. Per-task cost is reported as a delta or side-by-side pair. The unit is concrete with a monetary anchor. Latency is also reported or its omission explicitly justified. The cost figure is connected to the production recommendation.

**Functional but Incomplete — 3 pts**
A cost number is reported with and without the trained component, but at least one of the following is true:
- Latency is omitted with no acknowledgment, OR
- Cost is reported only in raw token counts with no monetary translation, OR
- The cost figure sits disconnected from any decision implication

**Fundamentally Flawed — 1 pt**
Some mention of cost exists but at least one of the following is true:
- Only one side of the comparison is given, OR
- Cost is described only qualitatively ("similar," "manageable," "not significantly higher") with no numbers

**Absent — 0 pts**
No cost-per-task reporting on Page 1.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of cost section:
  - Cost WITH trained component (quoted):
  - Cost WITHOUT trained component (quoted):
  - Unit type ($/task, ¢/task, tokens+price anchor):
  - Latency reported (Y/N) OR omission justification quoted:
  - Connection to production recommendation quoted:
  - Justification for tier:
```

---

## Criterion 4 — Production Recommendation with Specific Conditions

**Maximum Points: 5**

> **Scope:** Whether the memo commits to one of the three named recommendation categories (deploy / deploy with caveat / do not deploy), and, if anything other than unconditional deploy, names what would need to change. This tests decision-making clarity and grounding in evidence, not description.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 4.1 | The recommendation is stated **unambiguously** using one of the three categories: **deploy**, **deploy with caveat**, or **do not deploy** | Quote the exact recommendation category statement |
| 4.2 | If **deploy with caveat** or **do not deploy**: **specific conditions** are named that gate the next state (specific lift threshold on a specific slice, specific cost ceiling, specific monitoring requirement, or specific data-collection prerequisite) | Quote each named condition with its quantitative anchor |
| 4.3 | The recommendation **cites the specific evidence** on which it rests | Quote the evidence citation |
| 4.4 | **Quantitative anchors are carried forward** into the recommendation paragraph itself — not left implicit or referenced only in earlier sections | Confirm numbers appear inline within the recommendation paragraph |

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. The recommendation is stated unambiguously using one of the three categories. If deploy with caveat or do not deploy, the memo names specific gating conditions with quantitative anchors. The recommendation cites the specific evidence on which it rests, with quantitative anchors carried forward into the recommendation paragraph itself.

**Functional but Incomplete — 3 pts**
A recommendation is given, but at least one of the following is true:
- Conditions for deploy with caveat are vague (e.g., "monitor closely" with no thresholds), OR
- The recommendation is stated without any quantitative grounding, OR
- The recommendation hedges across multiple categories without committing

**Fundamentally Flawed — 1 pt**
Some closing statement on Page 1 exists but at least one of the following is true:
- No clear recommendation category stated, OR
- The recommendation reduces to "needs further investigation" with no committed direction or trigger for that investigation

**Absent — 0 pts**
No production recommendation appears on Page 1.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of recommendation:
  - Recommendation category stated (deploy / deploy with caveat / do not deploy — quoted):
  - Gating conditions listed (quote each with quantitative anchor):
  - Evidence citation in recommendation paragraph quoted:
  - Quantitative anchors confirmed inline in recommendation paragraph (Y/N):
  - Hedging language detected (Y/N — quote any flagged phrases):
  - Justification for tier:
```

---

## Criterion 5 — Tenacious-Bench v0.2 Coverage Gap Identification

**Maximum Points: 5**

> **Scope:** Whether Page 2 names four specific behavioral failure modes that Tenacious-Bench v0.1 contains **zero tasks** against, each paired with a specific v0.2 addition to capture it. This criterion is bounded to **missing task coverage only**. Faithfulness of the rubric on tasks the benchmark already includes is out of scope and is not graded here.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 5.1 | **Exactly four** distinct missing-coverage failure modes are listed | Count and list each |
| 5.2 | Each gap is **Tenacious-specific** — not a generic LLM concern (hallucination, prompt injection, etc.) | Verify each gap names a behavior specific to Tenacious sales motion context |
| 5.3 | Each gap is paired with a **specific v0.2 addition**: a new task type, new input category, new data source, new partition, or new probe family | Quote the v0.2 addition for each gap |
| 5.4 | The four gaps are **non-overlapping** — each describes a distinct behavior the current bench cannot grade | Confirm no two gaps restate the same underlying issue |
| 5.5 | Each gap describes **missing task coverage** — not rubric faithfulness on existing tasks | Reject any gap that is actually a scoring-accuracy complaint on included tasks |

### Tier Definitions

**Mastery — 5 pts**
All five sub-criteria above are satisfied without exception. Four distinct Tenacious-specific missing-coverage failure modes are listed, each paired with a specific v0.2 addition, non-overlapping, and each describing behavior the current bench cannot grade because no task targets it.

**Functional but Incomplete — 3 pts**
Four gaps are listed, but at least one of the following is true:
- One or more gaps are generic LLM concerns rather than Tenacious-specific, OR
- The v0.2 addition is missing for one or more gaps, OR
- Two of the four gaps restate the same underlying issue, OR
- One or more gaps describe rubric faithfulness on existing tasks rather than missing task coverage (out of scope for this criterion)

**Fundamentally Flawed — 1 pt**
Some discussion of benchmark limitations exists but at least one of the following is true:
- Fewer than four gaps named, OR
- No v0.2 additions specified for any gap, OR
- The section is framed as benchmark strengths rather than honest limitations

**Absent — 0 pts**
No v0.2 gap section present in the memo.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of v0.2 gap section:
  - Gap 1 — failure mode quoted + Tenacious-specific (Y/N) + v0.2 addition quoted:
  - Gap 2 — failure mode quoted + Tenacious-specific (Y/N) + v0.2 addition quoted:
  - Gap 3 — failure mode quoted + Tenacious-specific (Y/N) + v0.2 addition quoted:
  - Gap 4 — failure mode quoted + Tenacious-specific (Y/N) + v0.2 addition quoted:
  - Overlap detected between any two gaps (Y/N — specify if yes):
  - Any gap misclassified as rubric-faithfulness complaint (Y/N — specify if yes):
  - Justification for tier:
```

---

## Criterion 6 — Ground Truth Faithfulness Self-Critique

**Maximum Points: 5**

> **Scope:** Whether the memo acknowledges that the rubric and ground truth on tasks the benchmark **already includes** are derived from public signals (hiring data, layoffs data, redacted case studies) and therefore measure those tasks imperfectly relative to a real Tenacious sales motion. This criterion is bounded to **measurement faithfulness on existing tasks**. Whether additional behaviors should be added as new task types is out of scope and is not graded here.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 6.1 | A **specific lossiness mechanism on existing tasks** is named — not a generic disclaimer | Quote the specific mechanism (e.g., "hiring signals lag actual stack decisions so grounding-quality scores reward stale signal") |
| 6.2 | The memo states **what kind of agent behavior** this lossiness **systematically over-rewards or under-rewards** on the headline result | Quote the over/under-reward statement |
| 6.3 | The lossiness is framed as a **current constraint on the reported numbers** — not as future work or a generic caveat | Confirm present-tense constraint framing; reject future-work framing |
| 6.4 | The discussion concerns **mis-scoring on included tasks** — not missing task types | Reject if the section actually describes new task types that should be added (that belongs in Criterion 5) |

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. A specific lossiness mechanism on existing tasks is named. The memo states what kind of agent behavior this lossiness systematically over-rewards or under-rewards on the headline result. Framed as a current constraint on the reported numbers, not as generic disclaimer or future work.

**Functional but Incomplete — 3 pts**
A lossiness acknowledgment is made, but at least one of the following is true:
- The mechanism is generic ("public data has limitations") with no specific failure pathway named, OR
- The impact on the headline result is not stated, OR
- The discussion describes missing task types rather than mis-scoring on included tasks (out of scope for this criterion)

**Fundamentally Flawed — 1 pt**
A disclaimer about data quality exists but at least one of the following is true:
- No mechanism named, OR
- The lossiness is treated only as future work rather than as a current constraint on the reported result

**Absent — 0 pts**
No ground truth faithfulness discussion present in the memo.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of faithfulness section:
  - Specific lossiness mechanism quoted:
  - Over-reward or under-reward behavior quoted:
  - Framed as current constraint (Y/N) — quote framing sentence:
  - Confirmed as mis-scoring on included tasks, not missing task types (Y/N):
  - Future-work framing detected (Y/N — quote if yes):
  - Justification for tier:
```

---

## Criterion 7 — Unresolved Training Failure Acknowledgment

**Maximum Points: 5**

> **Scope:** Whether the memo names **exactly one** honest unresolved failure from the training process, with enough specificity that the reader understands the failure mode. The failure **must** be a training-process failure (a model behavior issue, a hyperparameter outcome, a convergence issue, an alignment regression) — **not** a benchmark coverage gap or a ground truth limitation.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 7.1 | **Exactly one** specific failure is named (not multiple, not zero) | Count failures named |
| 7.2 | The failure has a **concrete description**: input pattern, output pattern, and frequency or qualitative scope | Quote the input pattern, output pattern, and scope |
| 7.3 | The memo states **what was tried and did not resolve it**, OR **what would be tried next** | Quote the attempted remediation or next-step statement |
| 7.4 | The failure is clearly a **training-process artifact** — not a benchmark gap or data limitation reframed | Confirm the failure type; reject if it belongs in Criterion 5 or 6 |

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. One specific training-process failure is named with concrete description of input pattern, output pattern, and frequency or qualitative scope. The memo states what was tried and did not resolve it, or what would be tried next. Clearly a training-process artifact, not a benchmark or data issue.

**Functional but Incomplete — 3 pts**
A training failure is described, but at least one of the following is true:
- The description is vague (e.g., "the model sometimes drifted in tone" with no frequency or trigger pattern), OR
- No remediation attempt or next step is mentioned

**Fundamentally Flawed — 1 pt**
Some statement that the training was not perfect exists but at least one of the following is true:
- No specific failure named, OR
- The failure is actually a benchmark gap or data limitation reframed as a training failure

**Absent — 0 pts**
No unresolved training failure section present in the memo.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of training failure section:
  - Number of failures named (must be exactly 1):
  - Input pattern quoted:
  - Output pattern quoted:
  - Frequency or qualitative scope quoted:
  - Remediation attempted OR next step quoted:
  - Confirmed as training-process failure, not benchmark/data issue (Y/N):
  - Justification for tier:
```

---

## Criterion 8 — Kill-Switch Trigger Condition

**Maximum Points: 5**

> **Scope:** Whether the memo specifies a concrete production trigger that would cause the trained component to be rolled back or disabled, expressed as a **measurable condition** rather than a sentiment, and calibrated against the production economics the memo itself reports. This criterion is **path-agnostic** and applies identically to Path A (SFT generator), Path B (preference-tuned judge or critic), and Path C (process reward model) submissions.

### Sub-Criteria Checklist (ALL must be satisfied for Mastery)

| # | Sub-Criterion | Verification Method |
|---|---------------|---------------------|
| 8.1 | The trigger is stated as a **measurable condition**: a metric, a threshold, and a time window | Quote the metric, threshold, and time window |
| 8.2 | The metric is **observable in production** without re-running a held-out benchmark | Confirm the metric can be read from a live system |
| 8.3 | A **clear action** is specified: disable the trained component and revert, fall back to non-trained alternative, or escalate to human review | Quote the action statement |
| 8.4 | The **threshold value is justified** — not asserted — with reference to the lift size or cost figures established earlier in the memo | Quote the justification tying the threshold to earlier reported numbers |

### Qualifying metric examples by path type (for agent reference):
- **Path A (SFT generator):** reply-rate drop, complaint-rate spike
- **Path B (judge/critic):** send-volume drop, false-approval rate
- **Path C (PRM):** trajectory-completion-rate drop, human-escalation-rate spike
- **Any path:** cost-per-conversion threshold

### Tier Definitions

**Mastery — 5 pts**
All four sub-criteria above are satisfied without exception. The trigger is stated as a measurable condition (metric + threshold + time window). The metric is observable in production without a held-out re-run. A clear rollback or escalation action is specified. The threshold value is justified with reference to lift size or cost figures established earlier in the memo.

**Functional but Incomplete — 3 pts**
A trigger is described, but at least one of the following is true:
- The threshold is unspecified (e.g., "if quality drops" without defining production quality), OR
- The action is vague ("review the system"), OR
- The trigger relies on a measurement that cannot be made in production without a held-out re-run, OR
- The threshold is asserted without justification

**Fundamentally Flawed — 1 pt**
Some mention of monitoring or rollback exists but at least one of the following is true:
- No specific metric named, OR
- No threshold stated, OR
- No action defined — reads as a generic safety statement

**Absent — 0 pts**
No kill-switch condition section present in the memo.

### Agent: Record Your Finding Here

```
Assigned Tier: [ ]
Points Awarded: [ ] / 5
Evidence:
  - Page/paragraph location of kill-switch section:
  - Path type (A / B / C):
  - Metric named (quoted):
  - Threshold value (quoted):
  - Time window (quoted):
  - Observable in production without held-out re-run (Y/N + explanation):
  - Action statement quoted:
  - Threshold justification tied to earlier memo numbers (quoted):
  - Justification for tier:
```

---

## Final Score Summary Table

> The AI grading agent must complete this table after evaluating all criteria. A perfect score of 40/40 requires every criterion to be awarded Mastery. No criterion may be left blank.

| # | Criterion | Max Pts | Tier Awarded | Points Earned |
|---|-----------|---------|--------------|---------------|
| 1 | Executive Summary & Headline Delta A Reporting | 5 | | |
| 2 | Delta B Honesty (Prompt-Engineered Baseline) | 5 | | |
| 3 | Cost per Task Delta with Production Implication | 5 | | |
| 4 | Production Recommendation with Specific Conditions | 5 | | |
| 5 | Tenacious-Bench v0.2 Coverage Gap Identification | 5 | | |
| 6 | Ground Truth Faithfulness Self-Critique | 5 | | |
| 7 | Unresolved Training Failure Acknowledgment | 5 | | |
| 8 | Kill-Switch Trigger Condition | 5 | | |
| | **TOTAL** | **40** | | |

---

## Overall Assessment

```
TOTAL SCORE: [ ] / 40

Criteria at Mastery:                  [ ] / 8
Criteria at Functional but Incomplete: [ ] / 8
Criteria at Fundamentally Flawed:     [ ] / 8
Criteria at Absent:                   [ ] / 8

Critical Gaps (any criterion not at Mastery — list all):
1.
2.
3.
4.
5.
6.
7.
8.

Cross-Criterion Scope Violations Detected:
  - Any Criterion 5 gap misclassified as Criterion 6 content (Y/N):
  - Any Criterion 6 content misclassified as Criterion 5 content (Y/N):
  - Any Criterion 7 failure misclassified as benchmark/data issue (Y/N):

Agent Certification:
"I have inspected actual written content for each criterion, cited specific
evidence for every tier assignment, awarded Mastery only where every
sub-criterion is fully and unambiguously satisfied, flagged all hedging
language and scope violations, and applied no rounding up for effort,
intent, or proximity to threshold."

[ ] CONFIRMED
```

---

*RUBRIC.md — Final Report Submission Evaluation Standard*
*Total possible: 40 points | Mastery across all 8 criteria required for full marks*