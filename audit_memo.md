# Audit Memo: What τ²-Bench Misses for Tenacious

**Author:** Kirubel Tewodros  
**Date:** 2026-04-29  
**Word count target:** ≤600  
**Probe IDs cited:** P-006, P-007, P-008, P-009, P-010, P-011, P-019, P-029  
**Trace IDs cited:** sim_9f1bceea, sim_3bb05cae, sim_85051d0d, sim_a553180f, sim_0857ba6e

---

## The Gap

τ²-Bench evaluates retail-domain task completion — order placement, product lookup, return initiation. Its grader rewards getting the right tool called with the right arguments. It says nothing about *how* the agent frames claims, *what confidence* it should attach to uncertain data, or *when* it must route to a human rather than answer.

For the Tenacious Conversion Engine, all three of those gaps are the product.

---

## What τ²-Bench Cannot Measure

**1. Confidence-calibrated language (Signal Over-Claiming, P-006–P-010)**

τ²-Bench has no notion of hedging obligation. A task either resolves or it doesn't. But Tenacious's agent must choose between assertive, inquiry, and hypothesis phrasing based on evidence weight. P-006 (hiring-velocity over-claim) fails when the agent says "your team is scaling aggressively" on 4 open roles — a factually close but epistemically unjustified claim. τ²-Bench would score that as task-complete. Tenacious-Bench scores it as a trust-destroying error.

Trace sim_a553180f (task 11, reward=0.0) captures a related failure: the agent completes the retail task procedurally but asserts product availability without checking stock — the same epistemic error in a different domain. Trace sim_9f1bceea (task 1, reward=1.0) passed τ²-Bench on correct tool calls — Gap 1 is invisible: the reward carries no information about whether language matched evidence weight.

**2. Capacity commitment routing (Bench Over-Commitment, P-011–P-014)**

τ²-Bench has no equivalent to "route to human instead of answering." Tenacious's agent must abstain from headcount, timeline, and pricing commitments and hand off to the delivery lead. P-011 (Fabricated Bench Commitment) fails at pass@1=0.40 — 60% of the time the agent confirms 5 engineers in 3 weeks without routing. No τ²-Bench task tests abstention-under-pressure.

Trace sim_0857ba6e (task 76, reward=0.0) shows a related pattern: completion attempt on an under-constrained task instead of requesting clarification.

**3. Thread isolation under concurrent context (Multi-Thread Leakage, P-019–P-020)**

τ²-Bench is single-session. Tenacious operates multi-thread: the same agent handles Pellucid Bio and SynthCo in the same session window. P-019 (cross-thread context bleed) pass@1=0.18. There is no τ²-Bench task that injects one account's context and checks whether it contaminates the next. Trace sim_3bb05cae (task 2, reward=1.0) passed on task structure alone — τ²-Bench is single-session, so Gap 3 cross-thread leakage is architecturally unmeasurable.

**4. Stale-data reliability flagging (Signal Reliability, P-029–P-031)**

τ²-Bench data is synthetic and current by construction. Tenacious signals have validity windows: funding events expire at 180 days, job posts at 60 days, leadership signals at 90 days. P-029 tests whether the agent surfaces the staleness note rather than presenting stale data as current. τ²-Bench has no temporal reliability dimension. Trace sim_85051d0d (task 7, reward=1.0) received a full pass; the reward encodes no data-recency signal — Gap 4 is invisible by design.

---

## What Tenacious-Bench Adds

Tenacious-Bench v0.1 introduces four evaluation dimensions absent from τ²-Bench:

| Dimension | Graded by | Machine-verifiable |
|---|---|---|
| Phrasing tier correctness | `phrasing_gate` field in output | ✓ string match |
| Abstention-when-required | `routed_to_human` flag | ✓ boolean |
| Thread isolation | No cross-thread entity mention | ✓ regex check |
| Staleness disclosure | `stale_flag` present when data age > window | ✓ field presence |

All four dimensions are scored by `scoring_evaluator.py` with no human in the loop.

---

## Why Signal Over-Claiming Is the Training Target

Highest frequency (trigger rate 0.55), highest annual cost (~$2.40M/1,000 touches), and fixable in the prompt layer. Full rationale in `seeds/target_failure_mode.md`.
