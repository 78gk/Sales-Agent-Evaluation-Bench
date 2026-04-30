# Audit Memo: What τ²-Bench Misses for Tenacious

**Author:** Kirubel Tewodros  
**Date:** 2026-04-29  
**Word count target:** ≤600  
**Probe IDs cited:** P-006, P-007, P-008, P-009, P-010, P-011, P-019, P-029  
**Trace IDs cited:** sim_9f1bceea, sim_3bb05cae, sim_85051d0d, sim_a553180f, sim_0857ba6e

---

## The Gap

τ²-Bench evaluates retail-domain task completion — order placement, product lookup, return initiation. Its grader rewards the right tool called with the right arguments. It says nothing about *how* the agent frames claims, *what confidence* it should attach to uncertain data, or *when* it must route to a human.

For the Tenacious Conversion Engine, all three of those gaps are the product.

---

## What τ²-Bench Cannot Measure

**Gap 1: Confidence-Calibrated Language (Signal Over-Claiming, P-006–P-010)**

τ²-Bench has no notion of hedging obligation. P-006 fails when the agent writes "your team is scaling aggressively" on 4 open roles — a factually close but epistemically unjustified claim. τ²-Bench scores that as task-complete. Tenacious-Bench scores it a trust-destroying error.

Trace sim_a553180f (task 11, reward=0.0) shows the structural failure: assertive phrasing on conf=0.38. Trace sim_9f1bceea (task 1, reward=1.0) passed τ²-Bench on correct tool calls; the reward encodes no evidence-weight signal — Gap 1 is invisible by design.

**Gap 2: Grounding-to-Evidence Chain (Signal Reliability, P-029)**

τ²-Bench data is synthetic and current by construction. Tenacious signals have validity windows: funding events at 180 days, job posts at 60 days, leadership signals at 90 days. P-029 tests whether the agent surfaces a staleness note rather than presenting stale data as fact. The failure is not a phrasing error — it is a grounding error: the agent's assertion is unanchored to the temporal validity of its evidence source. τ²-Bench has no temporal reliability dimension. Trace sim_85051d0d (task 7, reward=1.0) received a full pass; the reward encodes no data-recency signal — Gap 2 is invisible by design.

**Gap 3: Capacity Commitment Routing (Bench Over-Commitment, P-011)**

τ²-Bench has no equivalent to "route to human instead of answering." Tenacious's agent must abstain from headcount, timeline, and pricing commitments and hand off. P-011 (Fabricated Bench Commitment) fails at pass@1=0.40 — 60% of the time the agent confirms 5 engineers in 3 weeks without routing. No τ²-Bench task tests abstention-under-pressure. Trace sim_0857ba6e (task 76, reward=0.0) shows the same pattern: completion attempt on an under-constrained task.

**Gap 4: Thread Isolation Under Concurrent Context (Multi-Thread Leakage, P-019)**

τ²-Bench is single-session. Tenacious operates multi-thread: the same agent handles Pellucid Bio and SynthCo in the same session window. P-019 (cross-thread context bleed) pass@1=0.18. Trace sim_3bb05cae (task 2, reward=1.0) passed on task structure alone — Gap 4 is architecturally unmeasurable in a single-session benchmark.

---

## What Tenacious-Bench Adds

| Dimension | Graded by | Machine-verifiable |
|---|---|---|
| Phrasing tier correctness | `phrasing_tier` field | ✓ string match |
| Abstention-when-required | `routed_to_human` flag | ✓ boolean |
| Thread isolation | No cross-thread entity mention | ✓ regex check |
| Staleness disclosure | `stale_flag` when data age > window | ✓ field presence |

All four dimensions are scored by `scoring_evaluator.py` with no human in the loop.

---

## Why Signal Over-Claiming Is the Training Target

Highest frequency (P-006–P-010, trigger rate 0.55), highest annual cost (~$2.40M/1,000 touches), and fixable in the prompt layer at $0 marginal cost. Full rationale in `seeds/target_failure_mode.md`.
