# Datasheets for Datasets

**Authors:** Timnit Gebru, Jamie Morgenstern, Briana Vecchione, Jennifer Wortman Vaughan,
Hanna Wallach, Hal Daumé III, Kate Crawford
**Venue:** Communications of the ACM, Vol. 64, No. 12, December 2021
**Year:** 2021

---

## Core Contribution

- Proposes a structured documentation standard for datasets modelled on datasheets used in
  electronics manufacturing: every dataset should ship with a "datasheet" specifying its
  motivation, composition, collection process, preprocessing, uses, distribution, and maintenance.
- Argues that the absence of standardized documentation is a root cause of reproducibility
  failures, undetected biases, and dataset misuse across ML research.
- The seven-section framework (Motivation, Composition, Collection, Preprocessing, Uses,
  Distribution, Maintenance) is designed to surface the assumptions and constraints that
  practitioners need to evaluate fitness-for-purpose before using a dataset.
- Provides guided questions for each section rather than prescribing a fixed format, allowing
  the framework to adapt across dataset types while preserving comparability.
- Demonstrates through examples that the same dataset (e.g., CelebA) looks very different
  under the datasheet lens: assumptions that were invisible in standard model cards become
  explicit obligations.

---

## How It Informs Tenacious-Bench

The Gebru framework directly structures `datasheet.md` in this repo. All seven sections are
present with substantive content, not stubs. The Composition section reports the four-way
source-mode breakdown and the 50/30/20 partition split. The Maintenance section names a
responsible party, versioning plan, and error-reporting channel. The framework's insistence
on explicit fitness-for-purpose boundaries is reflected in the "Are there tasks for which the
dataset should not be used?" answer: Tenacious-Bench explicitly documents it should not be
used as a general sales benchmark.

---

## Design Choice Under Examination

**Section 3, "Composition" (p. 87):** The authors instruct dataset creators to report "the
number of instances that constitute the dataset" and "the breakdown of instances by type."
The framing assumes a static, finalized dataset — all counts reported are final counts of
a shipped artifact, not in-progress counts of a dataset under active construction.

---

## My Disagreement

The Gebru framework is designed for post-hoc documentation of complete datasets. It provides
no guidance for documenting a dataset that is under construction at submission time — where
the reported counts are intentionally interim and will change before the final artifact ships.

This is not a corner case; it is the norm in competitive ML settings where interim
checkpoints are required deliverables. Tenacious-Bench v0.1 shipped a Day 3 interim with
155 tasks (75 train / 30 dev / 50 held_out) against a target of 250 (125 / 75 / 50). The
Gebru framework would have us report "155 tasks" as *the* composition — but the datasheet's
usefulness for anyone evaluating the final artifact depends on also knowing the target, the
growth plan, and which splits are sealed (held_out, SHA-256 committed) vs. still expanding.

My counter-design in `datasheet.md` explicitly reports both the interim composition and
the target composition, with a dated interim label and a gap table showing the Day 4–5
synthesis plan. This dual-state reporting is absent from the Gebru template but is essential
for datasets with staged authoring pipelines. The framework should be extended with a
"Dataset Version" section that distinguishes snapshot counts from target counts and provides
a versioning timestamp for each count reported — Week 10 Trace sim_a553180f illustrates why
snapshot-only documentation fails: the 0.8333 pass@1 figure from the official 30-trial Week
10 evaluation cannot be re-derived from the current `seeds/trace_log.jsonl`, which contains
150 entries from multiple run batches (72.7% pass rate). A static count with no versioning
context is not just unhelpful — it is actively misleading.
