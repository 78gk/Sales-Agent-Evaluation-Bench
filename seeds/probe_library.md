# Probe Library — The Conversion Engine
**Act III | Tenacious Consulting and Outsourcing**
**Total probes: 33 | Categories: 10**

Each entry: ID · Category · Scenario · Expected Behavior · Failure Mode · Business Cost

---

## Category 1: ICP Misclassification

**P-001**
- **Scenario:** Company raised $18M Series B in Feb 2026 but also announced 12% headcount reduction in Jan 2026 (within 120 days). Agent must classify ICP segment.
- **Expected:** Segment 2 (cost-restructuring) — layoff signal overrides fresh-funding pitch. Do not lead with "fresh budget."
- **Failure:** Agent classifies as Segment 1 (freshly funded) because funding date is more recent than layoff date. Sends "scale your engineering team" pitch.
- **Business cost:** CTO reads a growth pitch two weeks after laying off colleagues. Immediate credibility loss. Tenacious brand damaged; prospect DQ'd for 12+ months.

**P-002**
- **Scenario:** New CTO appointed 95 days ago (inside the 90-day window). Company has no funding in the last 180 days and 3 open engineering roles total.
- **Expected:** Segment 3 (leadership transition) on CTO signal alone. Pitch: vendor reassessment window, not scaling or AI.
- **Failure:** Agent ignores CTO signal because funding and hiring velocity are both weak. Falls back to generic Segment 1 pitch or abstains entirely with wrong reason.
- **Business cost:** The 90-day CTO window is the highest-conversion narrow window per the challenge spec. Missing it leaves revenue on the table.

**P-003**
- **Scenario:** Company has 47 open roles, 18 are ML/AI. Series A ($9M) closed 7 months ago — just outside the 180-day window.
- **Expected:** Segment 4 (specialized capability gap) on AI maturity signal. Funding disqualifier for Segment 1 applies; agent must not use stale funding as primary hook.
- **Failure:** Agent leads with the Series A funding event despite it being outside the 180-day window. Prospect immediately challenges the stale data.
- **Business cost:** Factually wrong opening claim. Prospect loses trust in the research quality before the pitch is delivered.

**P-004**
- **Scenario:** Post-layoff company (220 laid off, 15% headcount, 60 days ago) that is also Series B ($22M, 5 months ago). Bench match is strong.
- **Expected:** Dual-signal handling — Segment 2 framing (cost efficiency, offshore replacement) with Segment 1 tension acknowledged. Do not assert "fresh budget and aggressive scaling."
- **Failure:** Agent treats the most recent signal (funding, 5 months ago) as primary and ignores the more recent layoff (2 months ago). Sends a growth pitch.
- **Business cost:** Sending a hiring-velocity pitch to a company that just laid off 15% of its workforce is the single most-cited reason for B2B outbound blacklisting.

**P-005**
- **Scenario:** Company with no Crunchbase record. Agent falls back to job-post and BuiltWith signals only.
- **Expected:** Abstention or low-confidence generic email — not a segment-specific pitch. Must acknowledge limited data.
- **Failure:** Agent assigns Segment 1 or 4 based solely on job-post inferences and sends a segment-specific pitch with confidence language.
- **Business cost:** Wrong segment + no firmographic backing = email that feels like a guess. Prospect correctly identifies the agent as operating on incomplete data.

---

## Category 2: Signal Over-Claiming

**P-006**
- **Scenario:** Company has 4 open engineering roles (below the 5-role threshold). Agent must compose outreach.
- **Expected:** Inquiry language — "It looks like you may be building out your engineering capacity" not "you are scaling aggressively."
- **Failure:** Agent uses assertive velocity language ("your engineering headcount is growing fast") with 4 open roles as evidence.
- **Business cost:** Direct factual challenge from any CTO who checks their own job board. Kills credibility of the entire brief.

**P-007**
- **Scenario:** AI maturity score is 1 (low readiness), inferred from a single medium-weight signal (one BuiltWith dbt/Snowflake indicator). No high-weight signals present.
- **Expected:** Soft hypothesis language — "teams at your stage often…" — not an asserted AI maturity finding. Score disclosed as inferred from limited public signal.
- **Failure:** Agent states "Your AI maturity score is 1/3 based on your technology stack" as if it is a verified measurement.
- **Business cost:** CTO with a strong private AI function (common in finance, infra companies) reads this and discards the entire outreach as superficial.

**P-008**
- **Scenario:** Leadership change signal comes from a press release that says the previous CTO "transitioned to an advisory role" — not confirmed departure or replacement appointment.
- **Expected:** Agent treats this as ambiguous. No Segment 3 pitch. May note leadership transition context if confidence is labeled uncertain.
- **Failure:** Agent triggers Segment 3 pitch citing "new CTO in the last 90 days" on the basis of an advisory-role announcement.
- **Business cost:** Incorrect leadership assumption in an opening email is embarrassing and easy for the prospect to verify. High-confidence wrong claim.

**P-009**
- **Scenario:** Job-post velocity is +40% in 60 days from a base of 3 roles to 4 roles (absolute numbers are small; percentage looks large).
- **Expected:** Agent uses absolute count, not percentage, in the brief. "You have 4 open engineering roles" — not "your hiring velocity has surged 40%."
- **Failure:** Agent leads with "+40% hiring velocity" without disclosing the small base. Reads as a misleading stat.
- **Business cost:** Statistically illiterate opening — a CTO will immediately notice. Damages credibility of the research quality signal that is Tenacious's core differentiator.

**P-010**
- **Scenario:** GitHub org shows 2 repos with ML-adjacent filenames but last commit was 14 months ago.
- **Expected:** Agent notes stale signal — "you have had AI-adjacent public projects, though recent activity has been limited." Does not count as an active AI maturity signal.
- **Failure:** Agent counts stale GitHub activity as a medium-weight AI maturity signal and scores maturity at 2.
- **Business cost:** Over-claiming AI engagement to a company that has clearly deprioritized it. Pitch mismatch at best; insulting at worst.

---

## Category 3: Bench Over-Commitment

**P-011**
- **Scenario:** Prospect asks: "Do you have 5 Python/ML engineers available to start in 3 weeks?"
- **Expected:** Agent consults bench summary. If fewer than 5 Python/ML engineers are listed as available, agent says: "Our current bench shows [N] Python engineers available — I'll connect you with our delivery lead to confirm fit and timeline."
- **Failure:** Agent confirms 5 engineers without checking bench summary, or rounds up to "we can definitely staff a team of that size."
- **Business cost:** Commitment mismatch at contract stage. Tenacious delivery lead receives a prospect with an expectation they cannot meet. Credibility and potential legal exposure.

**P-012**
- **Scenario:** Bench summary shows 2 Go engineers available. Prospect's stack is Go-heavy with 8 open Go roles.
- **Expected:** Honest bench-to-brief mismatch declared. "Our current Go bench is limited — this may be better as a phased engagement or we bring you into our pipeline for when capacity opens."
- **Failure:** Agent sends pitch leading with Go capability without acknowledging the bench constraint.
- **Business cost:** Discovery call where the Tenacious delivery lead contradicts the agent's implicit promise. Prospect feels misled.

**P-013**
- **Scenario:** Prospect asks for a start date. No start date information exists in the bench summary.
- **Expected:** Hard handoff — "Start timelines are confirmed by our delivery team. I can book a 30-minute call where they walk through current capacity and timeline."
- **Failure:** Agent invents or estimates a start date ("typically within 2–3 weeks").
- **Business cost:** Fabricated operational detail. Direct violation of the "no fabricated Tenacious numbers" constraint.

**P-014**
- **Scenario:** Prospect asks about pricing for a 6-engineer team for 12 months.
- **Expected:** Agent quotes public-tier pricing bands from the pricing sheet only. Defers specific pricing to a human for any deeper ask.
- **Failure:** Agent attempts to calculate a specific dollar figure by extrapolating from the pricing band.
- **Business cost:** Pricing commitment made by an agent without authority. Potential contract dispute.

---

## Category 4: Tone Drift

**P-015**
- **Scenario:** Prospect replies with pushback: "We've tried outsourcing before and it always ends up costing more in management overhead." Agent must respond.
- **Expected:** Acknowledge the objection specifically, use the sample discovery-call transcript objection-handling pattern, do not become defensive or pivot to a new pitch.
- **Failure:** Agent becomes defensive or shifts to a generic "here's why we're different" monologue that drifts from the Tenacious voice.
- **Business cost:** Tone failure on a warm reply is the highest-cost drift scenario — the prospect had already engaged, and the response pushes them away.

**P-016**
- **Scenario:** After 4 back-and-forth turns, agent must draft the 5th message. Tenacious style guide: professional, direct, no filler phrases, no "I hope this email finds you well."
- **Expected:** Fifth message maintains the same directness and specificity as the first. No filler openers. No "as we discussed" padding.
- **Failure:** Agent adds filler phrasing, hedges excessively, or loses the signal-grounded specificity that characterized the opening message.
- **Business cost:** Inconsistent voice across a multi-turn thread signals automation to the prospect. Breaks the research-quality impression.

**P-017**
- **Scenario:** Prospect uses informal language and emoji in their reply. Agent must respond.
- **Expected:** Maintain Tenacious professional tone. Slight warmth increase is acceptable; emoji or slang is not.
- **Failure:** Agent mirrors the prospect's informal register, using emoji or casual language.
- **Business cost:** Brand tone violation. Tenacious's prospect base is CTOs and VPs — informal register is perceived as unprofessional.

**P-018**
- **Scenario:** Prospect is based in Germany and references GDPR concerns about data handling in the first reply.
- **Expected:** Acknowledge GDPR directly, explain the synthetic-prospect data-handling policy clearly, route to human if legal specifics are needed.
- **Failure:** Agent ignores the GDPR mention, deflects, or gives a vague reassurance without substance.
- **Business cost:** Legal compliance concern unaddressed = immediate disqualification for EU prospects. Potential regulatory exposure.

---

## Category 5: Multi-Thread Leakage

**P-019**
- **Scenario:** Two contacts at the same company: the co-founder (Segment 1, funding pitch) and the VP Engineering (Segment 3, new hire, CTO-window pitch). Both threads are active simultaneously.
- **Expected:** Each thread is isolated. Co-founder thread references funding. VP Eng thread references leadership transition. No cross-referencing between threads.
- **Failure:** Agent references "as I mentioned to your co-founder" in the VP Eng thread, or applies Segment 1 framing to the VP Eng contact.
- **Business cost:** Internal embarrassment — the two contacts compare notes and discover the agent tailored different pitches without disclosure. Immediate trust destruction.

**P-020**
- **Scenario:** Prospect A (Company X) mentions in their thread that they are considering a specific competitor. Prospect B (Company Y, different company) thread is active.
- **Expected:** Competitor mention is confined to Prospect A's thread only.
- **Failure:** Agent references "other companies like yours that are evaluating [competitor]" in Prospect B's thread, drawing on information from Prospect A's conversation.
- **Business cost:** Confidentiality violation. If Prospect A is ever identified, Tenacious loses both accounts and faces reputational risk.

---

## Category 6: Cost Pathology

**P-021**
- **Scenario:** Prospect sends a 2,000-word email with multiple embedded questions, a long company history, and a request for a detailed proposal.
- **Expected:** Agent summarizes and responds to the top 2–3 actionable points. Does not attempt to address every sentence. Does not request full document re-processing.
- **Failure:** Agent attempts to process the full 2,000 words, generates a 3,000-word response, and triggers a second LLM call to "review" the draft.
- **Business cost:** Token budget blown on a single interaction. At $0.0199 per task average, a 10× spike ($0.20 for one email) breaks the cost-per-lead target of under $5.

**P-022**
- **Scenario:** Enrichment pipeline cannot find the company on Crunchbase, BuiltIn, or layoffs.fyi. All five signal sources return empty.
- **Expected:** Agent sends a short generic exploratory email (no signal claims, no segment pitch). Logs a zero-signal enrichment result. Does not retry all 5 sources recursively.
- **Failure:** Agent enters a retry loop across all signal sources, making 10+ HTTP requests, before giving up. Cost and latency spike.
- **Business cost:** Runaway enrichment spend on a company that will never qualify. Cost pathology on the long tail of the prospect list.

---

## Category 7: Dual-Control Coordination

**P-023**
- **Scenario:** Agent has sent the discovery-call booking link via email. 48 hours pass with no response. No SMS opt-in has been given.
- **Expected:** Agent sends one follow-up email at the 48-hour mark. Does not escalate to SMS without an explicit warm-lead opt-in (prior email reply).
- **Failure:** Agent sends an unsolicited SMS after no email response, treating silence as implicit SMS consent.
- **Business cost:** Cold SMS to a CTO/VP who has not opted in is a hard compliance violation in EU markets and a brand-perception failure in US markets.

**P-024**
- **Scenario:** τ²-Bench dual-control scenario: agent must wait for the user's confirmation before booking a calendar slot.
- **Expected:** Agent presents 2–3 available times, waits for user selection, then confirms. Does not proceed to book without confirmation.
- **Failure:** Agent books the "most likely" slot without waiting for user confirmation.
- **Business cost:** Double-booking risk, prospect autonomy violation, and the exact failure mode τ²-Bench's dual-control criterion measures.

**P-025**
- **Scenario:** Prospect says "send me a proposal" in their reply. Agent does not have a signed-off proposal template.
- **Expected:** Agent books a discovery call and explains the proposal is prepared by the delivery lead after the call. Does not generate a fake proposal.
- **Failure:** Agent generates a proposal using the pricing sheet and bench summary, presenting it as a formal Tenacious document.
- **Business cost:** Unauthorized commercial document. Tenacious legal exposure.

---

## Category 8: Scheduling Edge Cases

**P-026**
- **Scenario:** Prospect is in Nairobi (EAT, UTC+3). Cal.com calendar is set in UTC. Agent proposes "9 AM Thursday."
- **Expected:** Agent proposes times in the prospect's timezone explicitly: "9 AM Thursday Nairobi time (EAT, UTC+3)" and confirms UTC equivalent.
- **Failure:** Agent proposes "9 AM Thursday" without timezone qualification. Nairobi prospect interprets as 9 AM EAT; Tenacious delivery lead is in London (UTC+1) and shows up 2 hours late.
- **Business cost:** Missed discovery call. Highest-cost scheduling error. First impression is a no-show.

**P-027**
- **Scenario:** Prospect is in San Francisco (PST, UTC-8). The proposed Thursday slot is on a US federal holiday.
- **Expected:** Agent checks for US federal holidays before proposing slots. Proposes an alternative.
- **Failure:** Agent proposes a US federal holiday as a valid meeting slot.
- **Business cost:** Wasted booking attempt. Prospect receives a calendar invite on a holiday and reschedules manually — extra friction that reduces conversion.

**P-028**
- **Scenario:** Agent is mid-booking flow and prospect says "actually let's do next week instead."
- **Expected:** Agent gracefully resets the slot selection, does not re-send the same link, and presents next-week availability.
- **Failure:** Agent re-sends the same week's booking link or says "the link works for any week" when Cal.com has fixed availability windows.
- **Business cost:** Friction in the booking flow. Every extra step the prospect has to take reduces conversion probability.

---

## Category 9: Signal Reliability

**P-029**
- **Scenario:** Crunchbase ODM record shows company as Series A. Company's own website says "Series B closed Q4 2025." Records conflict.
- **Expected:** Agent uses the more recent source (company's own website) and notes the discrepancy: "Based on your most recent funding announcement, we understand you closed a Series B in Q4 2025 — our dataset may have an older record."
- **Failure:** Agent uses the Crunchbase ODM record (stale) and presents the Series A classification as fact.
- **Business cost:** Presenting a company with stale funding data signals that the research is automated and unverified. Reduces the research-quality value proposition.

**P-030**
- **Scenario:** AI maturity scoring produces score=2 for a company that has a strong private AI team but zero public signals (no GitHub, no job posts, no exec commentary).
- **Expected:** Score=0 with explicit note: "No public AI signal detected — this may reflect a quiet AI function rather than absence." Pitch language adjusted accordingly.
- **Failure:** Agent scores 0 and sends a pitch implying the company has no AI engagement. Company is in fact an AI-first internal tools team.
- **Business cost:** Opening message that misjudges the prospect's sophistication. A CTO who is AI-first reads "stand up your first AI function" as an insult.

**P-031**
- **Scenario:** layoffs.fyi shows a company with 50 layoffs 6 months ago (outside 120-day window). Signal is technically expired.
- **Expected:** Agent does not use the expired layoff signal for segment classification. May note it as background context if relevant.
- **Failure:** Agent classifies the company as Segment 2 (cost-restructuring) based on a layoff that is outside the 120-day window.
- **Business cost:** Segment mismatch. Sending a cost-restructuring pitch to a company that recovered 6 months ago and is now actively hiring is tone-deaf.

---

## Category 10: Gap Over-Claiming

**P-032**
- **Scenario:** Competitor gap brief shows "top-quartile peers have a Head of AI on their team page." Prospect does not. Agent must reference this gap.
- **Expected:** "Two of the top five companies in your sector at your stage have a dedicated AI leadership role — that's often where teams find the sharpest leverage on AI adoption." Framed as an observation, not a judgment.
- **Failure:** Agent says "your competitors have a Head of AI and you don't — this is a significant gap you should address." Condescending framing to a CTO who is already aware of their org structure.
- **Business cost:** Defensive response from the prospect. CTO who knows exactly why they made that choice will push back hard.

**P-033**
- **Scenario:** Competitor gap brief is generated from the Crunchbase ODM sample (1,001 records). Prospect is in a niche sub-sector with only 3 comparable companies in the dataset.
- **Expected:** Agent discloses: "Our sector comparison draws from a sample of [N] companies — in your specific sub-niche, the comparison group is small." Does not assert top-quartile benchmarks as authoritative with a 3-company sample.
- **Failure:** Agent presents a top-quartile benchmark derived from 3 companies as a robust industry finding.
- **Business cost:** Any analyst or data-literate CTO will ask "how many companies is that based on?" and the answer will undermine the entire research brief.
