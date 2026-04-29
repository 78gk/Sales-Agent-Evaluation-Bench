# Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing

**Authors:** Zhangchen Xu, Fengqing Jiang, Luyao Niu, Yuntian Deng, Radha Poovendran,
Yejin Choi, Bill Yuchen Lin
**Venue:** ACL 2024 (findings)
**Year:** 2024

---

## Core Contribution

- Proposes a self-generation approach: prompt an instruction-tuned LLM with only the
  user-turn prefix (e.g., `<|start_header_id|>user<|end_header_id|>`), let the model
  complete both the instruction and the response, then filter for quality.
- Demonstrates that 300,000 self-generated instruction-response pairs match or exceed
  Alpaca, ShareGPT, and WizardLM datasets on standard benchmarks, with zero human
  annotation and zero seed instructions.
- Quality filter (Section 3.2) removes examples that are too short, unsafe, or
  incoherent — but evaluates instruction quality, not response-behaviour correctness.
- Shows that diversity emerges naturally from the model's pre-training distribution
  without explicit diversity constraints.
- Scales linearly: more queries produce more diverse instructions, with no quality
  degradation observed up to 1M examples.

---

## How It Informs Tenacious-Bench

Magpie's generator ≠ ground-truth assumption informs our decision to use a separate
judge model. `generation_scripts/router_config.json` enforces that Qwen3-80B generates
and DeepSeek V3.2 judges — the exact cross-model check Magpie lacks. Magpie's evidence
that model-generated data produces diverse instructions also confirms the value of the
synthesis source mode for Tenacious-Bench (Days 3–4, OpenRouter, 60 tasks planned).

---

## Disagreement

**Design choice under examination:** Section 3.2 ("Quality Filtering") — the authors
filter generated examples by instruction quality (length, coherence, safety). The filter
does not check whether the model's *response* reflects correct domain behaviour. The
assumption is that an aligned model generating data about a topic will produce
behaviourally aligned responses by construction: alignment transfers from the model's
pre-training distribution into its self-generated outputs.

**My disagreement:** For confidence-calibrated tasks, an aligned model generating its own
training data will produce the dominant assertive prior — not the threshold-correct hedge —
because "aligned" in the RLHF sense means "preferred by a general human judge," and
general human judges prefer confident, actionable text over hedged text. Magpie's filter
accepts "Your team is clearly scaling aggressively" as a high-quality response (fluent,
relevant, task-complete). Our `generation_scripts/judge_prompt.txt` would fail it on
`rubric_clarity` (score ≤ 2/5) because the expected tier is `hypothesis` given
`conf=0.35` and a single mid-weight signal — and the response does not reflect the
threshold decision.

This is not a pathological edge case. The 0.55 trigger rate for Signal Over-Claiming
(P-006–P-010, `seeds/failure_taxonomy.md`) means that in 55% of sampled interactions, a
model operating under natural aligned priors chose assertive phrasing when the evidence
required a hedge. A Magpie-style self-generation pass over our prompt templates would
encode this failure into the training data: the model would generate `assertive` outputs
as ground truth, and the quality filter — which checks instruction coherence, not tier
correctness — would pass them. We would train the model *to over-claim*, not to calibrate.

Our counter-design is the judge layer in `router_config.json`: DeepSeek V3.2 judges every
Qwen3-80B-generated synthesis task on three dimensions, including `rubric_clarity` (is the
expected tier clearly justified by the evidence?). A task where the model-generated
"expected" tier is `assertive` but the signals show `conf=0.42` would fail
`rubric_clarity` ≤ 2 and be discarded. Magpie's design has no analogue for this check.
The quality filter and the domain-correctness filter are not the same filter, and
conflating them is the paper's core architectural assumption we explicitly reject.
