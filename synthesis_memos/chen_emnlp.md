# ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate

**Authors:** Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang,
Jie Fu, Zhiyuan Liu
**Venue:** EMNLP 2023 / representative for Chen et al. in the evaluation debate space.
**Year:** 2023

---

**Note on citation:** The brief references "Chen et al. EMNLP 2025." At the time of
submission (2026-04-30), no verified EMNLP 2025 paper by Chen et al. on LLM evaluation
has been confirmed in public databases. This memo addresses the closest verified work —
Chan et al. / Chen et al. EMNLP 2023 (ChatEval) — and explicitly flags the citation gap.
The core argument applies across the evaluation-debate literature regardless of venue year.

---

## Core Contribution

- Proposes ChatEval: rather than using a single LLM judge to evaluate outputs, run a
  multi-agent debate among multiple LLM judges (e.g., GPT-4, Claude, Gemini) where each
  judge defends or revises its score after seeing other judges' reasoning.
- Demonstrates that multi-agent debate produces more consistent and calibrated scores than
  single-judge evaluation on open-ended tasks (summarization, dialogue quality).
- The debate mechanism surfaces and resolves judge disagreements: when two judges diverge,
  the forced reasoning exchange reduces the variance in final scores.
- Shows that the benefit of debate is larger when individual judges have high variance —
  i.e., when the task is ambiguous or requires nuanced judgment.
- Concludes that multi-judge ensemble plus debate is the most robust automated evaluation
  method for tasks without objective ground truth.

---

## How It Informs Tenacious-Bench

The ChatEval debate architecture is *not* used in Tenacious-Bench — and deliberately so.
The synthesis judge pipeline uses a single DeepSeek V3.2 judge per task (not an ensemble,
not a debate). The reasoning is documented in `generation_scripts/router_config.json`: the
judge is evaluating task *quality* (is this a well-formed evaluation task?), not output
*quality* (did the agent answer correctly?). For task-quality assessment, a single structured
rubric check on three named dimensions is more efficient and less prone to debate-induced
score inflation than a multi-agent ensemble. The primary scoring is handled by
`scoring_evaluator.py`'s deterministic checks — which require no judge at all.

---

## Design Choice Under Examination

**Section 3.3 ("Multi-Agent Debate Protocol"):** The authors run debate rounds until
judges reach consensus or a maximum round limit is hit. The consensus criterion is
agreement within 1 point on a 5-point scale. The paper treats consensus as a proxy for
correctness: if multiple independent LLMs agree, they are probably right.

---

## My Disagreement

Consensus among LLMs is not a reliable proxy for domain correctness when the judges share
a common pre-training prior that is misaligned with the correct behavior in the target
domain. For Signal Over-Claiming evaluation, a multi-agent debate among GPT-4, Claude, and
Gemini would rapidly reach consensus — not because they are correct, but because they all
share the same RLHF-trained preference for assertive, confident, actionable text. All three
judges would independently score `assertive`-tier phrasing higher than `hypothesis`-tier
phrasing on a cold email task, and they would agree with each other, producing low debate
variance and high apparent consensus. ChatEval would interpret this convergence as
reliability. It is actually correlated error.

The Week 11 evidence is direct: in the Day 4 pilot synthesis run, Qwen3-80B generated 5
tasks. 3 of 5 set `expected.phrasing_tier = assertive` on low-confidence signal contexts
(conf=0.40–0.48). If a ChatEval debate between Qwen3-80B and GPT-4 had been used to
validate these tasks, both models would likely have agreed the tasks were correct —
because both models' priors favor assertive outputs on sales tasks. Only the mechanical
`rubric_clarity` check (is the expected tier logically derivable from the stated confidence
values?) caught the error, because that check does not rely on judge preference at all.

The ChatEval paper's core claim — that multi-agent debate is the most robust evaluation
method — holds only when "robust" means "consistent across judges." For domain-specific
evaluation where the judges' shared prior is the source of error, consistency is a failure
mode, not a virtue. The correct fix is not more debate but a deterministic ground-truth
check that bypasses judge preference entirely.
