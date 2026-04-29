# LIMA: Less Is More for Alignment

**Authors:** Chunting Zhou, Pengfei Liu, Puxin Xu, Srini Iyer, Jiao Sun, Yuning Mao,
Xuezhe Ma, Avia Efrat, Ping Yu, Lili Yu, Susan Zhang, Gargi Ghosh, Mike Lewis,
Luke Zettlemoyer, Omer Levy
**Venue:** NeurIPS 2023
**Year:** 2023

---

## Core Contribution

- Demonstrates that 1,000 carefully curated instruction-following examples, combined with
  SFT on a strong base model (LLaMA-65B), produces responses competitive with RLHF-trained
  models judged at significantly higher cost.
- Proposes the "superficial alignment hypothesis": the model's knowledge and capabilities
  are acquired during pre-training; alignment is learning the narrow format of helpful
  responses, not new knowledge.
- Curates training data from existing high-quality online sources (Stack Exchange, wikiHow,
  Reddit TIFU, StackOverflow) with strong diversity emphasis — no synthetic generation.
- Evaluates alignment via GPT-4 win-rate on 300 held-out prompts head-to-head against
  competing models.
- Shows that adding more data (up to 30,000 examples) does not improve win rate, and can
  degrade it — surface diversity of 1,000 examples is sufficient.

---

## How It Informs Tenacious-Bench

LIMA's result that SFT on 1,000 focused examples produces meaningful behavioral change
directly supports Path A here: 125 training tasks targeting Signal Over-Claiming is not
a data-volume problem, it is a label-quality problem. LIMA also confirms the cost
structure: high-quality curation is more efficient than bulk generation.

---

## Disagreement

**Design choice under examination:** Section 5 ("Human Evaluation") — the authors evaluate
alignment using GPT-4 as the preference judge. GPT-4 is asked to rate responses on a
1–7 scale for helpfulness, with the authors treating GPT-4 win-rate as the primary signal
that a model is "aligned." This commits LIMA to a definition of alignment as
*GPT-4 preference*, conflating surface helpfulness with domain correctness.

**My disagreement:** The "superficial alignment" hypothesis — that alignment is just learning
a response format — breaks down when the target format is *epistemically constrained* rather
than stylistically constrained. For Signal Over-Claiming, the correct response is not the
most helpful-sounding one. Hypothesis-tier phrasing ("Pellucid Bio may be scaling — I want
to verify signal strength before committing to that framing") is less preferred than assertive
phrasing ("Pellucid Bio is clearly scaling aggressively") because assertive language reads as
more confident and actionable. A GPT-4 preference judge would rate the assertive response
higher. Our `scoring_evaluator.py` rates it 0 (wrong tier, wrong dimension).

This is not a corner case. Trace `sim_a553180f` (task 11, `reward=0.0`) demonstrates exactly
this failure: the agent produced topically coherent, fluent, professionally confident text
that would win a GPT-4 preference vote. It failed because the evidence weight (4 open roles,
no funding confirmation, conf=0.48) mandates `hypothesis` phrasing, not `assertive`. The
Signal Over-Claiming trigger rate of 0.55 across five probes (P-006–P-010,
`seeds/failure_taxonomy.md`) means that the model's natural preference-maximising prior is
*the behaviour we are training against*.

LIMA's evaluation design would declare our Week 10 baseline well-aligned — GPT-4 would
prefer its confident assertive outputs over hedged alternatives. Our benchmark reveals it is
broken in the dimension that costs $2.40M/1,000 touches (`seeds/target_failure_mode.md`,
C-004 in `evidence_graph.json`). The lesson: preference-based evaluation is insufficient
when the correct behaviour is one that informed human principals want but naive AI judges
will systematically downrank.
