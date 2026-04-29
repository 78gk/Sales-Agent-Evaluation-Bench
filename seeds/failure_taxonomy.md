# Failure Taxonomy - The Conversion Engine
**Act III | Tenacious Consulting and Outsourcing**

---

## Taxonomy Overview

Probes are grouped into 10 categories. Each category maps to a distinct business risk area for Tenacious. The taxonomy is ordered by aggregate observed trigger rate, computed as the mean of the probe-level `observed_trigger_rate` values in `probes/probe_library.json`.

| # | Category | Probes | Aggregate Trigger Rate | Peak Business Cost |
|---|---|---|---|---|
| 1 | ICP Misclassification | P-001-P-005 | 0.58 (avg of 5 probes) | Wrong pitch, DQ'd prospect |
| 2 | Signal Over-Claiming | P-006-P-010 | 0.55 (avg of 5 probes) | Brand credibility loss |
| 3 | Bench Over-Commitment | P-011-P-014 | 0.40 (avg of 4 probes) | Contract dispute, delivery failure |
| 4 | Tone Drift | P-015-P-018 | 0.40 (avg of 4 probes) | Warm-reply abandonment |
| 5 | Scheduling Edge Cases | P-026-P-028 | 0.40 (avg of 3 probes) | Missed discovery call |
| 6 | Signal Reliability with False-Positive Notes | P-029-P-031 | 0.40 (avg of 3 probes) | Research quality undermined |
| 7 | Gap Over-Claiming | P-032-P-033 | 0.40 (avg of 2 probes) | Defensive prospect, pushback |
| 8 | Dual-Control Coordination | P-023-P-025 | 0.25 (avg of 3 probes) | Booking failure, legal exposure |
| 9 | Multi-Thread Leakage | P-019-P-020 | 0.15 (avg of 2 probes) | Trust destruction |
| 10 | Cost Pathology | P-021-P-022 | 0.15 (avg of 2 probes) | Budget overrun |

---

## Category Detail

### 1. ICP Misclassification (P-001-P-005)
**Definition:** The agent assigns the wrong ICP segment, triggering a pitch that is misaligned with the prospect's actual buying context.

**Root cause:** The segment classifier uses a priority order that is not aligned with the signal weighting in the spec. The most recent signal date is used as a proxy for the most relevant signal, but a 60-day-old layoff outweighs a 5-month-old funding round for segment assignment.

**Tenacious-specific impact:** The four ICP segments exist because different buying contexts require different pitches. A Segment 1 pitch to a Segment 2 company reads as uninformed or tone-deaf on the very first touch.

**Trigger conditions:** Conflicting signals (funding plus layoff), signals near time-window boundaries, or missing Crunchbase ODM records.

**Aggregate trigger rate:** 0.58 across five probes.

---

### 2. Signal Over-Claiming (P-006-P-010)
**Definition:** The agent asserts facts about the prospect using certain language when the underlying signal is weak, ambiguous, or below the stated confidence threshold.

**Root cause:** The enrichment pipeline produces scores and signals without propagating confidence weights into the prompt. The agent uses the score value without calibrating its language to the evidence strength behind that score.

**Tenacious-specific impact:** Signal-grounded outreach is Tenacious's core differentiator. An over-claimed signal destroys the research-quality impression that makes signal-grounded email materially outperform generic outreach.

**Trigger conditions:** AI maturity inferred from two or fewer medium-weight inputs, job-post count below the 5-role threshold, or stale data outside validity windows.

**Aggregate trigger rate:** 0.55 across five probes.

---

### 3. Bench Over-Commitment (P-011-P-014)
**Definition:** The agent makes implicit or explicit commitments about Tenacious's delivery capacity that are not supported by the bench summary.

**Root cause:** The bench summary is loaded as context but is not enforced as a hard constraint at commitment-generation time.

**Tenacious-specific impact:** Bench utilization is Tenacious's primary operating metric. Over-committing capacity through an agent creates a mismatch that the delivery lead must unwind on the first call.

**Trigger conditions:** Prospect asks for specific headcount, stack, pricing, or start-date commitments and the agent does not route to human handoff.

**Aggregate trigger rate:** 0.40 across four probes.

---

### 4. Tone Drift from Style Guide (P-015-P-018)
**Definition:** The agent's language departs from the Tenacious style guide after one or more turns of prospect engagement.

**Root cause:** The style guide is applied to the first draft only. Follow-up messages are generated without re-checking the tone markers that make the opening message credible.

**Tenacious-specific impact:** If turns 2-4 read differently from the first message, the prospect infers automation and discounts the research-quality framing that made the first touch work.

**Trigger conditions:** Multi-turn threads, prospect objections, informal prospect language, or compliance concerns that require a careful tonal reset.

**Aggregate trigger rate:** 0.40 across four probes.

---

### 5. Scheduling Edge Cases (P-026-P-028)
**Definition:** The agent proposes or confirms calendar slots that are invalid due to timezone ambiguity, holidays, or prospect preference changes.

**Root cause:** Cal.com integration returns UTC times, but the agent does not consistently translate them into the prospect's local context or check edge constraints before proposing them.

**Tenacious-specific impact:** Tenacious's prospect pool spans EU, US, and East Africa. Timezone errors produce missed calls, the single highest-cost scheduling failure.

**Trigger conditions:** Cross-timezone bookings, regional holidays, or in-thread rescheduling after a first link has already been sent.

**Aggregate trigger rate:** 0.40 across three probes.

---

### 6. Signal Reliability with False-Positive Notes (P-029-P-031)
**Definition:** The agent uses signal data that is stale, conflicts with a more authoritative source, or is over-interpreted despite known false-positive risk.

**Root cause:** The enrichment pipeline does not compare cross-source consistency strongly enough and does not always surface reliability notes into the outbound prompt.

**Tenacious-specific impact:** When a prospect spots stale or contradictory research, the system loses the right to use "we did our homework" framing at all.

**Trigger conditions:** Company website contradicts Crunchbase, funding and leadership signals sit near expiry windows, or AI-maturity inference rests on stale GitHub or cached hiring data.

**Aggregate trigger rate:** 0.40 across three probes.

---

### 7. Gap Over-Claiming (P-032-P-033)
**Definition:** The agent presents competitor gap findings in a framing that is condescending, overstated given the sample size, or implies the prospect is behind in a way they will find insulting.

**Root cause:** The competitor-gap brief is produced as a factual artifact, but the delivery framing is not calibrated to the prospect's likely self-perception or the size and quality of the peer set.

**Tenacious-specific impact:** Competitor-gap outreach is only valuable if it lands as insight rather than condescension. Over-claiming here turns a differentiated research brief into a defensive reply or silent delete.

**Trigger conditions:** Small peer set, weak evidence URLs, or medium-confidence gap findings delivered with assertive language.

**Aggregate trigger rate:** 0.40 across two probes.

---

### 8. Dual-Control Coordination (P-023-P-025)
**Definition:** The agent proceeds with a booking, escalation, or commitment step without waiting for explicit prospect confirmation.

**Root cause:** The agent optimizes for task completion over respecting the dual-control protocol that requires user confirmation before the next irreversible step.

**Tenacious-specific impact:** The result is either an unsolicited channel escalation, an unauthorized booking, or an unsanctioned commercial artifact. All three are expensive relative to the tiny convenience gain.

**Trigger conditions:** Silent prospect after email send, ambiguous "sounds good" replies, missing signed-off proposal templates, or booking flows where a plausible slot is visible.

**Aggregate trigger rate:** 0.25 across three probes.

---

### 9. Multi-Thread Leakage (P-019-P-020)
**Definition:** Information from one prospect's conversation thread bleeds into a different prospect's thread.

**Root cause:** Thread isolation is not enforced strongly enough at the memory layer. If the agent's context includes multiple active accounts, signal leakage is possible.

**Tenacious-specific impact:** Leakage is low frequency but catastrophic when it happens. One cross-account confidentiality error can permanently disqualify multiple buyers inside the same referral network.

**Trigger conditions:** Two active contacts at the same account, shared-context memory buffers, or consecutive prospect handling without explicit thread reset.

**Aggregate trigger rate:** 0.15 across two probes.

---

### 10. Cost Pathology (P-021-P-022)
**Definition:** A prompt or interaction pattern that causes token usage or API call counts to spike beyond the per-lead cost target.

**Root cause:** There is no token-budget guard on individual interactions and no short-circuit on enrichment when all signal sources return empty.

**Tenacious-specific impact:** Cost pathologies rarely destroy a single account, but they quietly break the economics that justify using the agent at all.

**Trigger conditions:** Very long prospect replies, nested draft-review loops, or enrichment retries on companies with zero recoverable public signal.

**Aggregate trigger rate:** 0.15 across two probes.
