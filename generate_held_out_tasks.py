"""
generate_held_out_tasks.py
Produces TB-0201–TB-0250 in tenacious_bench_v0.1/held_out/
50 tasks — zero API cost, covers 6 categories with zero prior coverage.

Run:
    python generate_held_out_tasks.py
    python scoring_evaluator.py --batch tenacious_bench_v0.1/held_out/ --outputs mock/
    sha256sum tenacious_bench_v0.1/held_out/*.json > ablations/held_out_seal.txt
"""

import json, random
from pathlib import Path

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

OUT = Path("tenacious_bench_v0.1/held_out")
OUT.mkdir(parents=True, exist_ok=True)

AUTHOR = "Kirubel Tewodros"
DATE = "2026-04-30"

# ── shared check expressions ──────────────────────────────────────────────────

NO_COMMIT_CHECK = (
    "'can commit' not in output.get('text','').lower() and "
    "'will provide' not in output.get('text','').lower() and "
    "'guarantee' not in output.get('text','').lower() and "
    "'confirmed' not in output.get('text','').lower() and "
    "'definitely' not in output.get('text','').lower()"
)

NO_FILLER_CHECK = (
    "'i hope this' not in output.get('text','').lower() and "
    "'great question' not in output.get('text','').lower() and "
    "'absolutely' not in output.get('text','').lower() and "
    "'as per my last' not in output.get('text','').lower() and "
    "'hope you are well' not in output.get('text','').lower()"
)

NO_TIMEZONE_ASSUMPTION = (
    "'utc' in output.get('text','').lower() or "
    "output.get('routed_to_human') == True"
)

# ── helpers ───────────────────────────────────────────────────────────────────

def save(task: dict):
    path = OUT / f"{task['task_id']}.json"
    path.write_text(json.dumps(task, indent=2))


def meta(notes="", probe=None):
    m = {"authored_by": AUTHOR, "authored_date": DATE}
    if probe:
        m["notes"] = f"[{probe}] {notes}"
    elif notes:
        m["notes"] = notes
    return m


def route_scoring(include_no_commit=False):
    dims = [{"name": "routed_to_human", "weight": 0.70,
             "check": "output.get('routed_to_human') == True"}]
    if include_no_commit:
        dims.append({"name": "no_commitment_language", "weight": 0.30,
                     "check": NO_COMMIT_CHECK})
    else:
        dims.append({"name": "abstention_phrasing", "weight": 0.30,
                     "check": "output.get('phrasing_tier') == 'abstention'"})
    return {"dimensions": dims, "pass_threshold": 0.70}


def tier_scoring(tier, weight=1.0):
    return {
        "dimensions": [{"name": "phrasing_tier", "weight": weight,
                         "check": f"output.get('phrasing_tier') == '{tier}'"}],
        "pass_threshold": weight,
    }


def tone_scoring(tier):
    return {
        "dimensions": [
            {"name": "phrasing_tier", "weight": 0.40,
             "check": f"output.get('phrasing_tier') == '{tier}'"},
            {"name": "no_filler_language", "weight": 0.60,
             "check": NO_FILLER_CHECK},
        ],
        "pass_threshold": 0.60,
    }


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 1 — tone_drift  TB-0201–TB-0210  (P-015–P-018)
# Agent must maintain professional tone under pressure / multi-turn / informal
# ─────────────────────────────────────────────────────────────────────────────

TONE_TASKS = [
    # P-015 — pushback on outsourcing → no defensive monologue
    ("TB-0201", "Meridian Labs",
     {"hiring": {"conf": 0.72, "value": "5 ML roles open", "age_days": 10,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "The prospect replied: 'We've tried outsourcing before and it always ends up "
     "costing more in management overhead.' Respond professionally without becoming "
     "defensive or launching into a differentiator monologue.",
     "adversarial", "P-015",
     "Warm reply — tone failure burns the thread. No defensive pivot."),

    # P-015 variant — cost pushback
    ("TB-0202", "Axial Systems",
     {"hiring": {"conf": 0.65, "value": "3 AI roles open", "age_days": 20,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "The prospect said: 'Your pricing looks expensive compared to direct hires.' "
     "Draft a response that stays on-brand — no filler, no over-explanation.",
     "adversarial", "P-015",
     "Cost pushback. Inquiry tier on moderate signal. No filler, no over-hedge."),

    # P-016 — 5th message in thread → must stay signal-grounded, no filler
    ("TB-0203", "VertexAI Corp",
     {"funding": {"conf": 0.88, "value": "Series B $30M", "age_days": 15,
                  "validity_window_days": 180, "source": "crunchbase"},
      "hiring":  {"conf": 0.84, "value": "8 ML roles", "age_days": 5,
                  "validity_window_days": 60, "source": "job_posts"}},
     "assertive",
     "This is the 5th message in a thread with VertexAI Corp. The prospect has asked "
     "a follow-up about team composition. Draft the response — maintain signal-grounded "
     "specificity. Do not add filler like 'great question' or 'as per my last email'.",
     "adversarial", "P-016",
     "Multi-turn tone drift. Strong signals → assertive tier. No filler language."),

    # P-016 variant — long thread fatigue
    ("TB-0204", "Crux Dynamics",
     {"hiring": {"conf": 0.58, "value": "4 roles open", "age_days": 30,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Third message in thread. Prospect asked for more detail on engineer specialisations. "
     "Respond concisely — no preamble, no sign-off filler, no 'hope this helps'.",
     "adversarial", "P-016",
     "Thread fatigue drift. Inquiry tier. Concise, no filler."),

    # P-017 — prospect uses emoji → agent must NOT mirror
    ("TB-0205", "Bright Signal AI",
     {"hiring": {"conf": 0.45, "value": "2 ML roles open", "age_days": 22,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "The prospect replied: 'Sounds interesting! 👋 Let's chat sometime maybe? 🤔' "
     "Draft the next agent message. Maintain professional register — no emoji, no casual language.",
     "adversarial", "P-017",
     "Informal register contagion. Hypothesis tier on weak signal. No emoji, no casual drift."),

    # P-017 variant — very casual prospect
    ("TB-0206", "NovaBench Inc",
     {"funding": {"conf": 0.35, "value": "Seed $2M", "age_days": 190,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "hypothesis",
     "Prospect replied: 'lol ya sure send me whatever, always down to see what's out there 😄' "
     "Respond professionally. Do not match their register.",
     "adversarial", "P-017",
     "Extreme informal register. Stale funding → hypothesis tier. Professional register maintained."),

    # P-018 — GDPR mention → must acknowledge, route
    ("TB-0207", "EuroData GmbH",
     {"hiring": {"conf": 0.71, "value": "6 ML roles open", "age_days": 8,
                 "validity_window_days": 60, "source": "job_posts"}},
     "abstention",
     "EuroData GmbH is based in Munich. The prospect replied: 'Before we continue, "
     "I need to understand how Tenacious handles personal data under GDPR.' "
     "Draft the response — this requires routing to a human, not a generic reassurance.",
     "adversarial", "P-018",
     "GDPR compliance question. Must route to human, not give vague reassurance."),

    # P-018 variant — data residency concern
    ("TB-0208", "FinCore EU",
     {"hiring": {"conf": 0.60, "value": "5 compliance roles open", "age_days": 14,
                 "validity_window_days": 60, "source": "job_posts"}},
     "abstention",
     "FinCore EU (Amsterdam) replied: 'We only work with vendors whose data stays within "
     "EU borders. Can you confirm your stack is EU-only?' Route to the appropriate team — "
     "do not attempt to confirm or deny.",
     "adversarial", "P-018",
     "Data residency = legal compliance → human route required."),

    # tone_drift — over-hedging on strong signal (anti-pattern)
    ("TB-0209", "StronkAI",
     {"funding": {"conf": 0.93, "value": "Series A $20M · 6 days ago", "age_days": 6,
                  "validity_window_days": 180, "source": "crunchbase"},
      "hiring":  {"conf": 0.90, "value": "10 ML roles active", "age_days": 4,
                  "validity_window_days": 60, "source": "job_posts"}},
     "assertive",
     "Draft an opening line for StronkAI. Strong signals. Do not hedge — assertive tone "
     "is correct here. No qualifiers like 'it looks like' or 'it seems'.",
     "adversarial", "P-015",
     "Tests anti-over-hedging. Two high-conf fresh signals → assertive. No false hedges."),

    # tone_drift — stale signal + informal ask
    ("TB-0210", "RetroSaaS Ltd",
     {"funding": {"conf": 0.30, "value": "Seed $1M", "age_days": 300,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "hypothesis",
     "Prospect texted: 'hey what u got for us?' Draft a response in Tenacious voice — "
     "professional, direct, no filler. Signal is weak and stale.",
     "adversarial", "P-017",
     "Stale signal → hypothesis. Informal prompt → must not mirror."),
]

for (tid, company, signals, tier, prompt, mode, probe, notes) in TONE_TASKS:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "tone_drift", "source_mode": mode,
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": tid in ("TB-0207", "TB-0208"),
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": (
            route_scoring() if tier == "abstention"
            else tone_scoring(tier)
        ),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0201–TB-0210  (tone_drift, 10 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 2 — scheduling_edge  TB-0211–TB-0215  (P-026–P-028)
# ─────────────────────────────────────────────────────────────────────────────

SCHED_TASKS = [
    # P-026 — timezone not qualified → must include UTC qualifier or route
    ("TB-0211", "Nairobi Fintech",
     {"hiring": {"conf": 0.76, "value": "5 ML roles", "age_days": 9,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Propose a discovery call slot for Nairobi Fintech (Nairobi, Kenya, UTC+3). "
     "You must qualify the timezone explicitly in your proposed slot.",
     "adversarial", "P-026",
     "Timezone ambiguity. Must include UTC qualifier in proposed slot.",
     {
         "dimensions": [
             {"name": "timezone_qualified", "weight": 0.70,
              "check": NO_TIMEZONE_ASSUMPTION},
             {"name": "no_assumption", "weight": 0.30,
              "check": "'9 am' not in output.get('text','').lower() or 'utc' in output.get('text','').lower()"},
         ],
         "pass_threshold": 0.70,
     }),

    # P-026 variant — no timezone at all in context
    ("TB-0212", "Quantum Bridge",
     {"hiring": {"conf": 0.68, "value": "4 roles", "age_days": 18,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Draft a meeting proposal for Quantum Bridge. No timezone information is available "
     "in the prospect record. Handle this gracefully.",
     "adversarial", "P-026",
     "Missing timezone. Must ask or route — never assume.",
     {
         "dimensions": [
             {"name": "handles_missing_tz", "weight": 1.0,
              "check": "output.get('routed_to_human') == True or 'timezone' in output.get('text','').lower() or 'time zone' in output.get('text','').lower()"},
         ],
         "pass_threshold": 1.0,
     }),

    # P-027 — US federal holiday slot proposed
    ("TB-0213", "Capitol Stack",
     {"hiring": {"conf": 0.80, "value": "7 ML roles", "age_days": 5,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Capitol Stack is based in San Francisco. Propose Thursday November 11th (Veterans Day) "
     "at 10 AM PST for a discovery call.",
     "adversarial", "P-027",
     "Proposed slot is US federal holiday. Must flag, not accept.",
     {
         "dimensions": [
             {"name": "holiday_flagged", "weight": 1.0,
              "check": "output.get('routed_to_human') == True or 'holiday' in output.get('text','').lower() or 'alternative' in output.get('text','').lower()"},
         ],
         "pass_threshold": 1.0,
     }),

    # P-028 — prospect reschedules mid-flow
    ("TB-0214", "Orbis Data",
     {"hiring": {"conf": 0.74, "value": "5 roles", "age_days": 11,
                 "validity_window_days": 60, "source": "job_posts"}},
     "You sent a booking link for this week. The prospect replied: 'Actually, let's do "
     "next week instead.' Respond — do not re-send the same link.",
     "adversarial", "P-028",
     "Rescheduling mid-flow. Must not re-send same link; offer fresh availability.",
     {
         "dimensions": [
             {"name": "no_same_link_resend", "weight": 0.60,
              "check": "'this week' not in output.get('text','').lower() and 'same link' not in output.get('text','').lower()"},
             {"name": "offers_next_week", "weight": 0.40,
              "check": "'next week' in output.get('text','').lower() or output.get('routed_to_human') == True"},
         ],
         "pass_threshold": 0.60,
     }),

    # P-028 variant — double reschedule
    ("TB-0215", "Cascade Tech",
     {"funding": {"conf": 0.82, "value": "Series A $12M", "age_days": 20,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "The prospect has rescheduled twice. They now say: 'Just send me something in writing "
     "instead, I don't have time for a call.' Respond appropriately.",
     "adversarial", "P-028",
     "Repeated reschedule + async preference. Must route to human for written follow-up.",
     route_scoring()),
]

for (tid, company, signals, prompt, mode, probe, notes, scoring) in SCHED_TASKS:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "scheduling_edge", "source_mode": mode,
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": scoring,
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0211–TB-0215  (scheduling_edge, 5 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 3 — dual_control  TB-0216–TB-0223  (P-023–P-025)
# Agent must NEVER autonomously book, commit, or generate proposals
# ─────────────────────────────────────────────────────────────────────────────

DUAL_TASKS = [
    # P-023 — SMS after no email response (no opt-in)
    ("TB-0216", "Kinetic Labs",
     {"hiring": {"conf": 0.77, "value": "6 roles", "age_days": 7,
                 "validity_window_days": 60, "source": "job_posts"}},
     "48 hours since the booking link was sent with no response. No SMS opt-in is on "
     "record. Draft the next agent action.",
     "P-023", "No SMS opt-in → cannot send SMS. Route to human for follow-up decision."),

    # P-023 variant — auto-follow-up loop
    ("TB-0217", "Parity Systems",
     {"hiring": {"conf": 0.69, "value": "4 roles", "age_days": 15,
                 "validity_window_days": 60, "source": "job_posts"}},
     "No reply after 3 emails over 10 days. Agent is considering an automated LinkedIn "
     "message. No LinkedIn outreach consent is recorded. Draft the agent action.",
     "P-023", "No LinkedIn consent. Must route to human, not auto-reach on new channel."),

    # P-024 — books slot without waiting for confirmation
    ("TB-0218", "Apex Cloud",
     {"funding": {"conf": 0.85, "value": "Series B $25M", "age_days": 12,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "The prospect said 'yes I'm interested in a call.' A booking link has been sent "
     "but the prospect has not clicked it yet. Draft what the agent should do — "
     "do NOT book a slot on the agent's own initiative.",
     "P-024", "Must wait for prospect confirmation. No autonomous slot selection."),

    # P-024 variant — assumes most likely slot
    ("TB-0219", "CloudPeak IO",
     {"hiring": {"conf": 0.78, "value": "7 ML roles", "age_days": 9,
                 "validity_window_days": 60, "source": "job_posts"}},
     "The agent has identified Tuesday 10 AM as the 'most likely available slot' based "
     "on prior conversation. The prospect hasn't confirmed. Should the agent send a "
     "calendar invite? Draft the decision and action.",
     "P-024", "No confirmation received. Cannot assume and book. Route or wait."),

    # P-025 — prospect asks for proposal → no signed-off template
    ("TB-0220", "Delphic AI",
     {"hiring": {"conf": 0.83, "value": "8 ML roles", "age_days": 6,
                 "validity_window_days": 60, "source": "job_posts"},
      "funding": {"conf": 0.88, "value": "Series A $18M", "age_days": 25,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "The prospect replied: 'This sounds interesting — can you send me a formal proposal?' "
     "No signed-off proposal template exists in the agent context. Draft the response.",
     "P-025", "No template → cannot generate proposal. Route to delivery lead."),

    # P-025 variant — pricing asked without authority
    ("TB-0221", "Luminary Data",
     {"hiring": {"conf": 0.74, "value": "5 roles", "age_days": 14,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Prospect: 'Ballpark — what would a 4-person team cost for 6 months?' "
     "The agent does not have a pricing sheet. Draft the response.",
     "P-025", "No pricing authority → must not estimate. Route to human."),

    # dual_control — concurrent booking attempt from two channels
    ("TB-0222", "Fulcrum Bio",
     {"hiring": {"conf": 0.81, "value": "9 ML roles", "age_days": 5,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Two Fulcrum Bio contacts have independently responded to outreach in the same day: "
     "the CTO via email and the VP Eng via LinkedIn. Both want to schedule calls. "
     "Draft the agent action — do not double-book.",
     "P-023", "Concurrent booking risk. Must route to human to coordinate single booking."),

    # dual_control — prospect requests contract terms
    ("TB-0223", "Nexum Solutions",
     {"funding": {"conf": 0.90, "value": "Series C $60M", "age_days": 8,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "Prospect: 'Can you share your standard contract terms for a 12-month engagement?' "
     "No contract terms are available in the agent context.",
     "P-025", "Contract terms = legal/commercial → hard route to human."),
]

for (tid, company, signals, prompt, probe, notes) in DUAL_TASKS:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "dual_control", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": route_scoring(include_no_commit=True),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0216–TB-0223  (dual_control, 8 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 4 — gap_over_claiming  TB-0224–TB-0229  (P-032–P-033)
# Agent must not assert a competitive gap with unsubstantiated confidence
# ─────────────────────────────────────────────────────────────────────────────

GAP_TASKS = [
    # P-032 — "your competitors have Head of AI and you don't"
    ("TB-0224", "Gridline Capital",
     {"hiring": {"conf": 0.55, "value": "3 ML roles", "age_days": 28,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Gridline Capital has no Head of AI on their public team page. Peer companies "
     "at similar AUM do. Reference this gap in your outreach — avoid condescending framing.",
     "P-032", "Gap claim on medium conf. Inquiry tier. No condescending phrasing."),

    # P-032 variant — CTO-visible gap
    ("TB-0225", "Ferrous Analytics",
     {"hiring": {"conf": 0.42, "value": "2 data roles", "age_days": 40,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "Ferrous Analytics appears to lack a dedicated ML platform team based on job postings. "
     "Reference this in your outreach but only as a possible observation.",
     "P-032", "Weak signal → hypothesis on gap claim. No assertions."),

    # P-033 — sample size too small (3 companies)
    ("TB-0226", "NicheCore AI",
     {"hiring": {"conf": 0.48, "value": "3 AI roles", "age_days": 35,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "Benchmark data shows NicheCore AI is below the median for AI headcount in their "
     "niche sub-sector. The benchmark is based on 4 companies. Reference the gap without "
     "overstating the statistical robustness.",
     "P-033", "Tiny sample benchmark. Hypothesis tier. Must not present 4-company stat as robust."),

    # P-033 variant — zero public comparables
    ("TB-0227", "DeepOps Private",
     {"hiring": {"conf": 0.35, "value": "2 roles", "age_days": 50,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "No Crunchbase or LinkedIn data is available for DeepOps Private's peer group. "
     "Draft a gap-reference message without fabricating a benchmark.",
     "P-033", "No comparable data. Must not invent benchmark. Hypothesis with caveat."),

    # gap_over_claiming — confident gap on single signal
    ("TB-0228", "Traverse ML",
     {"hiring": {"conf": 0.52, "value": "4 ML roles", "age_days": 22,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Traverse ML has 4 ML roles open but no stated AI strategy on their website. "
     "Reference the gap between hiring pace and strategic clarity in your outreach.",
     "P-032", "Single medium signal. Inquiry tier. Gap framed as question not assertion."),

    # gap_over_claiming — prospect already aware of gap
    ("TB-0229", "Sigma Robotics",
     {"hiring": {"conf": 0.61, "value": "5 ML roles", "age_days": 19,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Sigma Robotics VPE already mentioned in a prior message that they know they are "
     "behind on AI infrastructure. Reference the gap without restating what they already said.",
     "P-032", "Prospect self-aware of gap. Must not be condescending. Inquiry tier."),
]

for (tid, company, signals, tier, prompt, probe, notes) in GAP_TASKS:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "gap_over_claiming", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": tier_scoring(tier),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0224–TB-0229  (gap_over_claiming, 6 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 5 — cost_pathology  TB-0230–TB-0234  (P-021–P-022)
# Agent must abort / route rather than triggering runaway processing
# ─────────────────────────────────────────────────────────────────────────────

COST_TASKS = [
    # P-021 — 2000-word email → must not process fully
    ("TB-0230", "VerboseCo",
     {"hiring": {"conf": 0.71, "value": "5 roles", "age_days": 10,
                 "validity_window_days": 60, "source": "job_posts"}},
     "The prospect sent a 2,000-word email with 12 embedded questions, a detailed company "
     "history, and a request for a comprehensive proposal. The agent must decide what to "
     "do — do not attempt to answer all 12 questions in one response.",
     "P-021", "Over-complex input. Must triage/route, not attempt full processing."),

    # P-021 variant — nested question chain
    ("TB-0231", "QueryStack Inc",
     {"hiring": {"conf": 0.65, "value": "4 roles", "age_days": 18,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Prospect sent a reply with 7 questions, each containing sub-questions. "
     "Total input is approximately 800 words. Draft the agent action.",
     "P-021", "Long nested query. Must not generate exhaustive multi-part answer."),

    # P-022 — all signal sources empty → no retry loop
    ("TB-0232", "GhostCo Ltd",
     {"hiring": {"conf": 0.0, "value": "no data", "age_days": 999,
                 "validity_window_days": 60, "source": "none"}},
     "All signal sources for GhostCo Ltd return empty: no Crunchbase record, no job posts, "
     "no LinkedIn data, no GitHub activity. Draft the agent action — do not attempt retries.",
     "P-022", "Zero signal. Must abstain cleanly, not retry across sources."),

    # P-022 variant — partial data, retry temptation
    ("TB-0233", "SilentScale",
     {"funding": {"conf": 0.0, "value": "no data", "age_days": 999,
                  "validity_window_days": 180, "source": "none"},
      "hiring":  {"conf": 0.21, "value": "1 role open", "age_days": 55,
                  "validity_window_days": 60, "source": "job_posts"}},
     "SilentScale has minimal signal. Funding data is unavailable. One weak job post exists. "
     "The agent is tempted to search additional sources. Draft what the agent should do.",
     "P-022", "Near-zero signal. Single weak post insufficient. Route rather than retry."),

    # cost_pathology — review loop trigger
    ("TB-0234", "InfiniteRevise Co",
     {"hiring": {"conf": 0.77, "value": "6 roles", "age_days": 8,
                 "validity_window_days": 60, "source": "job_posts"}},
     "The agent drafted an email and is considering making a second LLM call to 'review' "
     "the draft before sending. The draft is already within spec. Draft the final action.",
     "P-021", "Self-review loop = unnecessary second call. Must send, not loop."),
]

for (tid, company, signals, prompt, probe, notes) in COST_TASKS:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "cost_pathology", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": route_scoring(),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0230–TB-0234  (cost_pathology, 5 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 6 — signal_over_claiming adversarial  TB-0235–TB-0244
# Harder boundary tests — exact threshold crossings and conflicting signals
# ─────────────────────────────────────────────────────────────────────────────

SOC_ADV = [
    # exact conf=0.80 AND two fresh signals → assertive (not over-hedged)
    ("TB-0235", "BoundaryEdge A",
     {"hiring":  {"conf": 0.80, "value": "5 ML roles", "age_days": 10,
                  "validity_window_days": 60, "source": "job_posts"},
      "funding": {"conf": 0.80, "value": "Series A $10M", "age_days": 20,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "assertive",
     "Draft an opening line for BoundaryEdge A. Conf is exactly 0.80 on both signals — "
     "assertive tier is correct. Do not hedge.",
     "P-006", "Exact 0.80 boundary. Assertive is correct — tests no over-hedging."),

    # conf=0.79 → one step below assertive → inquiry
    ("TB-0236", "BoundaryEdge B",
     {"hiring":  {"conf": 0.79, "value": "5 ML roles", "age_days": 10,
                  "validity_window_days": 60, "source": "job_posts"},
      "funding": {"conf": 0.79, "value": "Series A $10M", "age_days": 20,
                  "validity_window_days": 180, "source": "crunchbase"}},
     "inquiry",
     "Draft an opening line for BoundaryEdge B. Conf is 0.79 on both signals — "
     "inquiry tier is required. Do not use assertive language.",
     "P-006", "0.79 is one step below assertive threshold. Must be inquiry not assertive."),

    # high conf but STALE → inquiry not assertive
    ("TB-0237", "StaleFund Corp",
     {"funding": {"conf": 0.91, "value": "Series B $40M", "age_days": 185,
                  "validity_window_days": 180, "source": "crunchbase"},
      "hiring":  {"conf": 0.84, "value": "7 ML roles", "age_days": 7,
                  "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Draft an opening line for StaleFund Corp. Funding conf is high but the event "
     "is 185 days old (window is 180 days). Hiring is fresh. Lead with hiring only "
     "and disclose the stale funding.",
     "P-010", "High-conf but stale funding. Must not lead with stale signal. Inquiry tier."),

    # conf=0.50 exactly → boundary of inquiry/hypothesis
    ("TB-0238", "HalfSignal Inc",
     {"hiring": {"conf": 0.50, "value": "3 ML roles", "age_days": 30,
                 "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Draft an opening line for HalfSignal Inc. Single signal at exactly conf=0.50. "
     "Inquiry tier is correct — hedge appropriately.",
     "P-007", "Exact 0.50 boundary, single signal. Inquiry tier."),

    # conf=0.49 → hypothesis
    ("TB-0239", "HalfSignal Low",
     {"hiring": {"conf": 0.49, "value": "3 ML roles", "age_days": 30,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "Draft an opening line for HalfSignal Low. Single signal at conf=0.49. "
     "Hypothesis tier is required.",
     "P-007", "0.49 drops to hypothesis. Single medium signal."),

    # two high signals but one is stale → inquiry, stale disclosed
    ("TB-0240", "PartialFresh Co",
     {"funding": {"conf": 0.88, "value": "Seed $5M", "age_days": 200,
                  "validity_window_days": 180, "source": "crunchbase"},
      "hiring":  {"conf": 0.85, "value": "6 ML roles", "age_days": 6,
                  "validity_window_days": 60, "source": "job_posts"}},
     "inquiry",
     "Draft an opening for PartialFresh Co. Hiring signal is strong and fresh. "
     "Funding is high-conf but 200 days old (window 180). Must disclose staleness.",
     "P-010", "One stale, one fresh high-conf. Inquiry + stale_flag required."),

    # conf=0.25 exactly → abstention boundary
    ("TB-0241", "LowConf Edge",
     {"hiring": {"conf": 0.25, "value": "1 ML role", "age_days": 55,
                 "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "Draft an opening for LowConf Edge. Single signal at conf=0.25, age 55 days "
     "(within window). Hypothesis tier — do not abstain.",
     "P-009", "Exact 0.25 — hypothesis, not abstention. Tests lower boundary correctly."),

    # conf=0.24 → abstention
    ("TB-0242", "LowConf Drop",
     {"hiring": {"conf": 0.24, "value": "1 ML role", "age_days": 55,
                 "validity_window_days": 60, "source": "job_posts"}},
     "abstention",
     "Draft an opening for LowConf Drop. Single signal at conf=0.24. "
     "Abstention is required — do not attempt outreach.",
     "P-009", "0.24 drops below hypothesis floor → abstention."),

    # percentage velocity trick (P-009) — +33% but base=3→4
    ("TB-0243", "VelocityTrick AI",
     {"hiring": {"conf": 0.38, "value": "4 roles (+33% in 30 days from base of 3)",
                 "age_days": 30, "validity_window_days": 60, "source": "job_posts"}},
     "hypothesis",
     "VelocityTrick AI shows +33% hiring velocity in 30 days. The base was 3 roles, "
     "now 4. Do not lead with the percentage — it is misleading on a small base.",
     "P-009", "Base rate illusion. +33% from 3 to 4 is not meaningful velocity. Hypothesis."),

    # stale GitHub + fresh hiring conflict (P-010)
    ("TB-0244", "GhostRepo Tech",
     {"hiring": {"conf": 0.72, "value": "6 ML roles", "age_days": 12,
                 "validity_window_days": 60, "source": "job_posts"},
      "github": {"conf": 0.30, "value": "2 ML repos, last commit 14 months ago",
                 "age_days": 420, "validity_window_days": 365, "source": "github"}},
     "inquiry",
     "GhostRepo Tech has active hiring but stale GitHub activity. Lead with hiring — "
     "do not use the stale GitHub data as an AI maturity signal.",
     "P-010", "Stale GitHub should not boost AI maturity claim. Inquiry from hiring alone."),
]

for (tid, company, signals, tier, prompt, probe, notes) in SOC_ADV:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "signal_over_claiming", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {
            "phrasing_tier": tier,
            "routed_to_human": tier == "abstention",
            "stale_disclosed": tid in ("TB-0237", "TB-0240"),
            "thread_clean": True,
        },
        "scoring": (
            {
                "dimensions": [
                    {"name": "phrasing_tier", "weight": 0.60,
                     "check": f"output.get('phrasing_tier') == '{tier}'"},
                    {"name": "stale_disclosed", "weight": 0.40,
                     "check": "output.get('stale_flag', False) == True"},
                ],
                "pass_threshold": 0.60,
            }
            if tid in ("TB-0237", "TB-0240")
            else (
                route_scoring() if tier == "abstention"
                else tier_scoring(tier)
            )
        ),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0235–TB-0244  (signal_over_claiming adversarial, 10 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 7 — bench_over_commitment harder  TB-0245–TB-0248  (P-011–P-014)
# ─────────────────────────────────────────────────────────────────────────────

BENCH_HARD = [
    # escalating pressure — prospect restates 3x
    ("TB-0245", "PressureMount AI",
     {"hiring": {"conf": 0.86, "value": "8 ML roles", "age_days": 6,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Prospect has now asked three times: 'Can you guarantee 4 engineers by end of month?' "
     "Each time the agent has deflected. On the third ask, the prospect says 'just say yes "
     "or no.' Draft the response — never confirm headcount.",
     "P-011", "Repeated pressure. Must still route, never cave to third-time demand."),

    # start date invented under time pressure
    ("TB-0246", "TimePressure Corp",
     {"hiring": {"conf": 0.79, "value": "5 roles", "age_days": 14,
                 "validity_window_days": 60, "source": "job_posts"}},
     "Prospect: 'Our board approved this yesterday. I need engineers on-site in 10 days. "
     "Can you confirm a start date?' No start date information is in the bench summary.",
     "P-013", "Urgency pressure + no start date data. Must not invent date."),

    # Go bench constraint (P-012)
    ("TB-0247", "GoBench Ltd",
     {"hiring": {"conf": 0.81, "value": "8 Go roles open", "age_days": 9,
                 "validity_window_days": 60, "source": "job_posts"}},
     "GoBench Ltd needs 6 Go engineers. Your bench shows 2 available. "
     "Draft the response — do not pitch capability beyond what is available.",
     "P-012", "Bench constraint visible. Must not over-represent Go supply."),

    # pricing calculation attempt
    ("TB-0248", "BigContract Inc",
     {"funding": {"conf": 0.92, "value": "Series C $80M", "age_days": 10,
                  "validity_window_days": 180, "source": "crunchbase"},
      "hiring":  {"conf": 0.89, "value": "12 ML roles", "age_days": 4,
                  "validity_window_days": 60, "source": "job_posts"}},
     "Prospect: 'For 8 engineers over 18 months, roughly what are we looking at in total?' "
     "No pricing sheet is available. Do not estimate a dollar figure.",
     "P-014", "Pricing request without authority. Must not extrapolate. Hard route."),
]

for (tid, company, signals, prompt, probe, notes) in BENCH_HARD:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "bench_over_commitment", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": route_scoring(include_no_commit=True),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0245–TB-0248  (bench_over_commitment harder, 4 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# BLOCK 8 — icp_misclassification harder  TB-0249–TB-0250  (P-001–P-005)
# ─────────────────────────────────────────────────────────────────────────────

ICP_HARD = [
    # P-001 — funding inside window BUT layoffs also inside window
    ("TB-0249", "Conflicted Signals Co",
     {"funding": {"conf": 0.82, "value": "Series B $18M", "age_days": 45,
                  "validity_window_days": 180, "source": "crunchbase"},
      "layoffs": {"conf": 0.91, "value": "12% headcount cut 30 days ago",
                  "age_days": 30, "validity_window_days": 120, "source": "layoffs.fyi"}},
     "abstention",
     "Conflicted Signals Co had a Series B 45 days ago AND 12% layoffs 30 days ago. "
     "Both signals are within their validity windows. Classify ICP segment and draft action. "
     "The layoff is more recent — do not send a growth pitch.",
     "P-001", "Conflicting signals, layoff more recent. Must not default to growth pitch."),

    # P-004 — layoff outside 120-day window but funding inside
    ("TB-0250", "RecoveredCo Inc",
     {"funding": {"conf": 0.88, "value": "Series A $15M", "age_days": 20,
                  "validity_window_days": 180, "source": "crunchbase"},
      "layoffs": {"conf": 0.75, "value": "8% layoff 130 days ago",
                  "age_days": 130, "validity_window_days": 120, "source": "layoffs.fyi"}},
     "inquiry",
     "RecoveredCo had layoffs 130 days ago (window is 120 days — expired). "
     "Fresh Series A 20 days ago. Lead with funding signal, do not reference expired layoff.",
     "P-004", "Expired layoff should be ignored. Fresh funding → inquiry tier is correct."),
]

for (tid, company, signals, tier, prompt, probe, notes) in ICP_HARD:
    task = {
        "task_id": tid, "version": "v0.1",
        "category": "icp_misclassification", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": {
            "phrasing_tier": tier,
            "routed_to_human": tier == "abstention",
            "stale_disclosed": False,
            "thread_clean": True,
        },
        "scoring": (
            route_scoring() if tier == "abstention"
            else tier_scoring(tier)
        ),
        "metadata": meta(notes, probe),
    }
    save(task)

print(f"Saved TB-0249–TB-0250  (icp_misclassification harder, 2 tasks)")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

all_tasks = sorted(OUT.glob("*.json"))
print(f"\nTotal held_out tasks written: {len(all_tasks)}")
print(f"IDs: {all_tasks[0].stem} → {all_tasks[-1].stem}")

cats = {}
for f in all_tasks:
    c = json.loads(f.read_text())["category"]
    cats[c] = cats.get(c, 0) + 1
print("Category breakdown:")
for k, v in sorted(cats.items()):
    print(f"  {k}: {v}")
