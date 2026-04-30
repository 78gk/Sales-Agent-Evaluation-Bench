# Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI

**Authors:** Mahima Pushkarna, Andrew Zaldivar
**Venue:** ACM FAccT 2022 (Conference on Fairness, Accountability, and Transparency)
**Year:** 2022

---

## Core Contribution

- Proposes Data Cards as a structured, layered documentation format for ML datasets,
  extending Gebru et al. 2021 with an explicit multi-resolution design (telescopic,
  periscopic, microscopic layers).
- The telescopic layer (1–3 sentences) is designed for non-technical stakeholders who need
  to understand scope and purpose without dataset internals.
- The periscopic layer (structured tables, key statistics) serves practitioners evaluating
  fitness-for-purpose before committing to a dataset.
- The microscopic layer (field-level schema, example records) serves engineers implementing
  training or evaluation pipelines on the dataset.
- Emphasizes that documentation should be purposeful — written with the audience and use
  case in mind — not exhaustive by default.
- Demonstrates that layered documentation reduces misuse by making the intended scope of a
  dataset legible at the level of abstraction the reader operates at.

---

## How It Informs Tenacious-Bench

The Pushkarna three-layer structure is implemented in `datasheet.md` under the "Pushkarna
& Zaldivar — Layered Detail" section. The Telescopic Overview (2 sentences, scope and
purpose) targets program staff reviewing the submission. The Periscopic Overview (attribute
table with 12 key dimensions) targets evaluators assessing rubric compliance. The Microscopic
Documentation (field-level schema table + abbreviated JSON example) targets anyone running
`scoring_evaluator.py` for the first time. All three layers are present with substantive
content.

---

## Design Choice Under Examination

**Section 4 ("Purposeful Documentation"), paragraph 3:** The authors argue that Data Cards
should be written for "the most important audience" and that "a single card cannot serve all
audiences simultaneously." Their solution is the three-layer structure, where each layer
addresses one audience. The implicit assumption is that the three audiences (executive,
practitioner, engineer) are sequential and non-overlapping — a practitioner reads the
periscopic layer and stops; an engineer reads through to the microscopic layer.

---

## My Disagreement

The three-layer model treats documentation as a one-way communication artifact from creator
to consumer. It does not account for the evaluation scenario where the *same person* moves
between audience roles within a single session — for example, a rubric grader who first
needs the telescopic summary to orient themselves, then the periscopic attribute table to
score the Composition criterion, then the microscopic schema to verify that the field names
in `datasheet.md` match the actual field names in `schema.json`.

In that scenario, the layered structure creates friction rather than reducing it: the grader
must navigate three separate sections of the document to answer one composite question. A
more useful design for evaluation contexts is a single integrated table that serves all three
resolutions simultaneously — columns for "what it is" (telescopic), "key statistics"
(periscopic), and "implementation detail" (microscopic). 

My Week 11 evidence: during rubric self-evaluation against `interim-report-rubric.md`, I
found myself re-reading all three Pushkarna layers in sequence to answer the single question
"does the Composition section report counts and proportions for all 4 source modes?" The
answer required: (1) knowing that the composition table exists (telescopic), (2) finding the
four-mode breakdown table (periscopic), and (3) verifying that the `source_mode` field in
the schema actually accepts those four values (microscopic). A single data dictionary row
per field — name, count, schema validation, and human-readable description — would have
answered all three in one place. The three-layer structure is elegant in principle but
imposes navigation overhead in practice that the Pushkarna paper does not acknowledge.
