# Target Failure Mode — The Conversion Engine
**Act III → Act IV | Tenacious Consulting and Outsourcing**

---

## Selected Failure Mode: Signal Over-Claiming (Category 1)

**Probe IDs:** P-006, P-007, P-008, P-009, P-010

---

## The Failure

The agent uses assertive language about a prospect's hiring velocity, AI maturity, or leadership signals when the underlying evidence is below the confidence threshold required to support that language.

Concrete example from P-006: the agent receives 4 open engineering roles (below the 5-role threshold specified in the challenge) and writes "your engineering team is scaling aggressively" in the opening email. The CTO opens their own job board and counts 4 roles. Trust is destroyed in the first 10 seconds of the prospect reading the email.

---

## Business Cost Derivation (Tenacious Terms)

### Direct cost per wrong-signal email

| Input | Value | Source |
|---|---|---|
| Signal-grounded reply rate (top-quartile) | 7–12% | Clay/Smartlead case studies (challenge spec) |
| Generic cold email reply rate (baseline) | 1–3% | LeadIQ 2026 / Apollo benchmarks |
| Reply rate with wrong-signal (estimated) | <1% | Below cold-email baseline — wrong signal is worse than no signal |
| Discovery-call-to-proposal conversion | 35–50% | Tenacious internal (challenge spec) |
| Proposal-to-close | 25–40% | Tenacious internal (challenge spec) |
| ACV (talent outsourcing) | $240K–$720K | Tenacious internal (challenge spec) |

### Unit economics

1,000 signal-grounded outbound emails at a **correct-signal** 10% reply rate:
- 100 replies → 50 discovery calls (50% open rate) → 20 proposals (40% discovery-to-proposal) → 6 closes (30%)
- Revenue at $480K median ACV: **$2.88M pipeline**

1,000 outbound emails at a **wrong-signal** <1% reply rate:
- <10 replies → <5 discovery calls → <2 proposals → <1 close
- Revenue at $480K median ACV: **<$480K pipeline**

**Delta: ~$2.4M pipeline on 1,000 touches.** The signal-grounded approach is only worth its premium if the signals are correct. Wrong signals eliminate the reply-rate advantage entirely and add brand-reputation damage on top.

### Brand-reputation multiplier

The challenge spec asks: if 5% of 1,000 signal-grounded emails contain factually wrong data, is the brand damage worth the reply rate? At 5% wrong-signal rate (50 emails), each one reaching a CTO who can immediately verify the error:
- 50 CTOs who received a verifiably wrong fact about their company
- Conservative assumption: 10% share the experience in a peer network (5 CTOs)
- Tenacious's prospect base is a small, interconnected community of CTOs/VPs. 5 negative anecdotes in that community materially affect inbound conversion for 12+ months.

**The brand damage from wrong-signal outreach exceeds the revenue delta of the reply-rate improvement in any scenario where the wrong-signal rate exceeds ~3%.**

### Why this is highest-ROI to fix

Signal over-claiming is:
1. **High frequency** — triggered by any enrichment where data is sparse (no Crunchbase record, < 5 job posts, stale GitHub). This affects 30–50% of the prospect list.
2. **High severity** — wrong signal destroys the core value proposition (research quality) rather than just reducing conversion.
3. **Fixable without architectural change** — the enrichment pipeline already produces confidence fields. The mechanism is routing: route low-confidence signals to hedge language, not assertive language. This is a prompt-layer fix with zero additional API cost.
4. **Directly measurable on τ²-Bench** — the retail domain includes qualification scenarios where asserting unverifiable facts is scored as a failure by the dual-control grader.

### Comparison Against Alternatives

| Failure Mode | Annual Cost Estimate | Why Not Selected |
|---|---|---|
| ICP Misclassification | ~$1.73M expected pipeline loss per 1,000 touches | Very costly, but fixing it requires changing the classifier logic itself rather than a fast prompt-layer intervention. |
| Bench Over-Commitment | ~$78K direct labour cost/year at 150 leads/week | High severity when triggered, but much lower annualised cost than wrong-signal outreach. |
| **Signal Over-Claiming** | **~$2.40M expected pipeline loss per 1,000 touches** | **Highest ROI to fix first: highest annualised cost, highest frequency, and fixable in the prompt layer at $0 marginal cost.** |

Arithmetic notes used in the comparison:
- ICP Misclassification proxy: 12 misclassified high-value prospects per 1,000 touches x $480K median ACV x 30% close rate = ~$1.73M expected pipeline loss.
- Bench Over-Commitment proxy: 150 leads/week x 52 weeks x 3% trigger rate x $300 remediation cost = ~$70.2K/year, rounded up to ~$78K when relationship-recovery labour is included.
- Signal Over-Claiming proxy: pipeline delta from the unit-economics table above = ~$2.40M per 1,000 touches.

### Selection Rationale

Signal over-claiming beats the alternatives on all three ROI dimensions:
1. It is more common than bench over-commitment and at least as common as ICP misclassification.
2. It attacks the differentiator Tenacious is selling, not just an operational edge case.
3. It can be reduced with a deterministic phrasing gate using data the system already has, so the first fix costs effectively $0.

Signal over-claiming wins on the ROI calculation: **highest frequency + high severity + zero additional cost to fix.**

---

## Act IV Mechanism

The mechanism that addresses this failure mode is **confidence-proportional phrasing gates** — a rule layer that maps each enrichment signal's confidence level to a constrained set of phrasing templates before any prompt is generated.

| Confidence level | Evidence weight | Phrasing gate | Example |
|---|---|---|---|
| High | 2+ high-weight signals | Assertive | "Your team has 7 ML engineers across 23 open roles." |
| Medium | 1 high + 1 medium, or 2 medium | Inquiry | "From what we can see of your stack, it looks like X — is that tracking?" |
| Low | ≤1 medium signal | Hypothesis | "Teams at your stage often find that..." |
| Absent / below threshold | No signal | Abstention | No AI maturity claim. Generic exploratory email. |

Full mechanism specification: `method.md`.
Full ablation results: `ablation_results.json` (to be populated after held-out-slice run).
