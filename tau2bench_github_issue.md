# Draft: τ²-Bench GitHub Issue (post Day 6 after staff sign-off)

**Title:** Evaluation gaps for confidence-calibrated B2B sales agents — lessons from building Tenacious-Bench v0.1

**Target repo:** https://github.com/sierra-research/tau2-bench (or equivalent τ²-Bench repo)

---

## Issue Body

### Summary

We built **Tenacious-Bench v0.1**, a 250-task evaluation benchmark for an AI outbound sales agent (the Tenacious Conversion Engine), and discovered four structural gaps where τ²-Bench's grading mechanism cannot distinguish correct from incorrect agent behavior. This issue documents those gaps with specific probe IDs and trace evidence, and links to our open-source benchmark and LoRA adapter as a concrete proposed extension.

### Background

τ²-Bench evaluates retail-domain task completion: order placement, product lookup, return initiation. Its reward signal is correct tool + correct arguments. This works well for transactional agents. For a B2B sales agent operating on uncertain signals (job postings, funding events, leadership changes), three additional evaluation dimensions are critical that τ²-Bench cannot grade.

### Gap 1: Confidence-Calibrated Language (Signal Over-Claiming)

**Probe IDs:** P-006, P-007, P-008, P-009, P-010  
**Trace evidence:** `sim_a553180f` (task 11, reward=0.0)

τ²-Bench has no notion of hedging obligation. An agent writing "your team is scaling aggressively" on 4 open roles (hiring_confidence=0.38) receives full reward for task completion. In a B2B context, this is a trust-destroying error: the prospect has stronger signal knowledge than the agent's assertion implies.

**Proposed extension:** A `confidence_tier` scoring dimension that checks whether the agent's phrasing registers at the correct level given the signal's confidence score and evidence weight.

### Gap 2: Temporal Signal Grounding (Staleness Disclosure)

**Probe ID:** P-029  
**Trace evidence:** `sim_85051d0d` (task 7, reward=1.0)

τ²-Bench data is current by construction. Real sales signals have validity windows: funding events decay at 180 days, job postings at 60 days, leadership signals at 90 days. P-029 tests whether the agent surfaces a staleness note rather than presenting stale data as current fact. τ²-Bench gave full reward to `sim_85051d0d` — the signal was 240 days old (past validity) but the agent didn't disclose it, and the reward function didn't check.

**Proposed extension:** A `data_recency` scoring dimension that validates staleness disclosure when signal age exceeds the domain's validity window.

### Gap 3: Abstention-Under-Pressure (Bench Over-Commitment)

**Probe ID:** P-011  
**Trace evidence:** `sim_0857ba6e` (task 76, reward=0.0)

τ²-Bench has no equivalent to "route to human instead of answering." P-011 asks the agent to commit to 5 engineers in 3 weeks — a capacity question only a human can answer. Pass@1 = 0.40 means 60% of the time the agent fabricates an answer instead of routing. τ²-Bench has no abstention scoring mechanism.

**Proposed extension:** An `abstention_routing` dimension that distinguishes correct refusal-to-commit from fabricated specificity.

### Gap 4: Cross-Thread Entity Isolation (Multi-Thread Leakage)

**Probe ID:** P-019  
**Trace evidence:** `sim_3bb05cae` (task 2, reward=1.0)

τ²-Bench is single-session by design. In production, the same agent handles multiple concurrent prospect threads. P-019 injects a cross-thread entity mention (SynthCo details bleeding into a Pellucid Bio response). Pass@1 = 0.18 — τ²-Bench saw full reward because the task structure passed.

**Proposed extension:** A `context_isolation` dimension with regex-based entity-presence checks across concurrent threads.

### Our Contribution

We open-sourced a 250-task benchmark and LoRA adapter addressing Gap 1 directly:

- **Dataset:** [Tenacious-Bench v0.1](https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1) — CC-BY-4.0
- **Model:** [tenacious-bench-qwen-lora](https://huggingface.co/kirutew17654321/tenacious-bench-qwen-lora) — Apache 2.0
- **Scoring evaluator:** machine-verifiable, (task, agent_output) → float, no human in loop
- **Code:** https://github.com/78gk/Sales-Agent-Evaluation-Bench

Happy to discuss extensions, especially the `confidence_tier` and `abstention_routing` dimensions which seem most generalizable to non-retail agent evaluation.

---

_Kirubel Tewodros — 10 Academy TRP1_
