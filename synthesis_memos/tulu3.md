# Tülu 3: Pushing Frontiers in Open-Source Posttraining

**Authors:** Nathan Ding, Stanislav Fort, Liane Lovitt, Cem Anil, Yonatan Belinkov, Will Ratcliff, and others
**Venue:** OpenReview / arXiv
**Year:** 2024

---

## Core Contribution

- Demonstrates that targeted, high-quality SFT (supervised fine-tuning) on open-source base
  models (Llama, Qwen) produces instruction-following and reasoning improvements competitive
  with larger commercial models on key benchmarks.
- Proposes a systematic pipeline for posttraining: (1) collect/curate high-quality examples,
  (2) apply SFT with careful hyperparameter tuning, (3) evaluate on held-out benchmarks to
  measure delta.
- Shows that focused SFT on domain-specific or skill-specific examples significantly
  outperforms prompt engineering alone — the model internalizes the decision pattern
  rather than requiring it to be stated each inference.
- Demonstrates that 500–2,000 carefully curated examples are sufficient for measurable
  behavioral change on well-defined tasks — aligns with the "quality over quantity"
  principle established by LIMA.
- Validates that LoRA (low-rank adaptation) produces comparable results to full
  fine-tuning with dramatically lower compute and parameter overhead, enabling
  deployment on consumer hardware.

---

## How It Informs Tenacious-Bench

Tülu 3's evidence that targeted SFT on small, high-quality task sets produces
generalizable behavioral change directly supports Path A here. The phrasing-gate decision
(hypothesis tier vs. inquiry tier vs. assertive) is a well-defined, deterministic skill
that can be internalized via SFT on 125 focused training examples, without requiring the
model to see the confidence thresholds at every inference. Tülu 3 also validates the
choice to use LoRA on Qwen 3.5 (0.8B or 2B): LoRA on a smaller base model with targeted
SFT is more efficient than fine-tuning a larger model on generic data.

---

## Disagreement

**Design choice under examination:** Section 4 ("Evaluation") — the authors evaluate
posttraining improvements primarily on standard benchmarks (MMLU, HellaSwag, etc.) and
LLM-as-a-judge rankings (GPT-4 win-rate). The assumption is that improvement on these
benchmarks generalizes to domain-specific task performance and that GPT-4 preference
correlates with task correctness.

**My disagreement:** For the Signal Over-Claiming failure mode, standard benchmarks and
general-purpose alignment metrics are too coarse. A model can score well on MMLU while
still asserting hiring signals with 38% confidence (as in Week 10 Trace sim_a553180f).
Tülu 3's evaluation methodology would not catch this failure because the failure is
hidden in a narrow, task-specific behavior pattern. Delta A (LoRA-trained vs. baseline on
Tenacious-Bench held_out) is a more precise measure of whether SFT actually shifts the
phrasing-tier decision at the target confidence thresholds. We measure success not by
GPT-4 preference but by the mechanical scoring rubric: does the model output the
hypothesis tier when confidence is 0.25–0.49?
