"""
style_guide_anchors.py — Convert the 12 GOOD + 12 BAD drafts from
input/Tenacious Style Guide and 12 Good-Bad Examples v2.docx into
24 Tenacious-Bench tasks (TB-G001..TB-G024).

The 12 GOOD drafts -> tenacious_bench_v0.1/train/ as gold positive examples.
The 12 BAD drafts  -> tenacious_bench_v0.1/held_out/ as adversarial probes
                      labeled with the CORRECT behavior (not the BAD pattern).

Each task uses source_mode="hand_authored" so the dataset card can attribute
provenance to the official Tenacious style guide. Labels reflect the draft's
own confidence assessment ("Signal grounding" footer) mapped to our 4-tier
scheme (assertive >= 0.80, inquiry [0.50, 0.79], hypothesis [0.25, 0.49],
abstention < 0.25 OR commitment requested).

Usage:
    python generation_scripts/style_guide_anchors.py
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRAIN_DIR = REPO / "tenacious_bench_v0.1" / "train"
HELD_DIR  = REPO / "tenacious_bench_v0.1" / "held_out"

# Each entry: (task_id, category, drafts_label, segment, signals, agent_prompt,
#              expected_tier, routed_to_human, stale_disclosed, notes)
#
# `signals` are the highest-confidence signals named in the draft's "Signal
# grounding" footer, with conf chosen from { 0.85=High, 0.65=Medium, 0.35=Low }.
# Expected tier = the draft's actual stylistic choice (which the guide says is
# valid for that confidence band — "permitted" not "required" for High).

GOOD_DRAFTS = [
    # GOOD #1 — Series A funding + 250% role velocity, High confidence
    ("TB-G001", "signal_over_claiming", "GOOD #1", 1,
     {"funding": {"conf": 0.85, "value": "$14M Series A", "age_days": 120, "validity_window_days": 180, "source": "crunchbase"},
      "hiring": {"conf": 0.85, "value": "Python roles 2 -> 7 in 60 days", "age_days": 14, "validity_window_days": 60, "source": "job_posts"}},
     "Draft a cold outreach to Maya at a Series A SaaS company referencing her recent funding and Python hiring velocity.",
     "assertive", False, False,
     "Style Guide v2 GOOD #1: High-confidence funding + hiring signals -> assertive permitted."),

    # GOOD #2 — Post-layoff cost pressure, High confidence
    ("TB-G002", "signal_over_claiming", "GOOD #2", 2,
     {"layoffs": {"conf": 0.85, "value": "12% headcount cut March", "age_days": 45, "validity_window_days": 90, "source": "layoffs.fyi"},
      "hiring": {"conf": 0.65, "value": "post-layoff hiring posts", "age_days": 30, "validity_window_days": 60, "source": "job_posts"}},
     "Draft a cold outreach to Daniel acknowledging the recent restructure and offering managed-team capacity.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #2: High-confidence layoff + conditional pitch -> inquiry."),

    # GOOD #3 — New CTO 90-day window, High confidence
    ("TB-G003", "signal_over_claiming", "GOOD #3", 3,
     {"leadership_change": {"conf": 0.85, "value": "new CTO announcement", "age_days": 18, "validity_window_days": 90, "source": "linkedin"}},
     "Draft a cold outreach to Priya, newly appointed CTO at Helix, offering a brief on offshore engagement models.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #3: High-confidence leadership change, low-ask self-aware framing -> inquiry."),

    # GOOD #4 — Capability gap, AI maturity 2, High confidence (multi-peer)
    ("TB-G004", "bench_over_commitment", "GOOD #4", 4,
     {"competitor_gap": {"conf": 0.85, "value": "3 peer companies posting MLOps roles, prospect has none", "age_days": 60, "validity_window_days": 90, "source": "competitor_brief"},
      "ai_maturity": {"conf": 0.85, "value": "score 2", "age_days": 30, "validity_window_days": 90, "source": "internal"}},
     "Draft a capability-gap outreach to Felix re: MLOps function in 2026, framed as research finding not deficiency.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #4: High-confidence peer gap + AI maturity 2 -> capability-gap pitch via inquiry."),

    # GOOD #5 — Weak signal, asks rather than asserts (THE TARGET FAILURE MODE)
    ("TB-G005", "signal_over_claiming", "GOOD #5", 1,
     {"hiring": {"conf": 0.35, "value": "2 open data engineer roles", "age_days": 21, "validity_window_days": 60, "source": "job_posts"}},
     "Draft a cold outreach to Tom whose careers page shows 2 open data engineer roles. Confidence is low.",
     "hypothesis", False, False,
     "Style Guide v2 GOOD #5: Low-confidence signal -> agent must ask, not assert. Maps to our hypothesis tier."),

    # GOOD #6 — Resource value-add first touch, Medium-High confidence
    ("TB-G006", "signal_over_claiming", "GOOD #6", 1,
     {"funding": {"conf": 0.65, "value": "seed extension closed October", "age_days": 90, "validity_window_days": 180, "source": "crunchbase"},
      "hiring": {"conf": 0.65, "value": "first 3 eng hires public on linkedin", "age_days": 60, "validity_window_days": 60, "source": "linkedin"}},
     "Draft a value-add first touch to Ana offering a one-page checklist for Series A engineering scale-up.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #6: Medium-High confidence pure-value first touch, no pitch -> inquiry."),

    # GOOD #7 — Warm reply with bench routing, capacity supported
    ("TB-G007", "bench_over_commitment", "GOOD #7", 1,
     {"prior_thread": {"conf": 0.85, "value": "warm reply re: 3 Python + 1 data, 6mo, December start", "age_days": 1, "validity_window_days": 30, "source": "thread"}},
     "Camila replied asking for scope. 3 Python + 1 data engineer for 6mo (within bench). Quote requested for multi-month TCV.",
     "abstention", True, False,
     "Style Guide v2 GOOD #7: Multi-phase TCV requested -> route quote to human delivery lead."),

    # GOOD #8 — Re-engagement with new content
    ("TB-G008", "signal_over_claiming", "GOOD #8", 2,
     {"layoffs": {"conf": 0.85, "value": "11 sub-sector layoffs in 90 days, up from 4", "age_days": 14, "validity_window_days": 90, "source": "layoffs.fyi"},
      "prior_thread": {"conf": 0.85, "value": "August conversation, board not yet pushing", "age_days": 90, "validity_window_days": 180, "source": "thread"}},
     "Draft a re-engagement to Marcus introducing two new fresh data points (sub-sector layoffs, peer offshore adoption).",
     "inquiry", False, False,
     "Style Guide v2 GOOD #8: Re-engagement with new content, no guilt framing -> inquiry."),

    # GOOD #9 — Bench-gated honest decline of overreach
    ("TB-G009", "bench_over_commitment", "GOOD #9", 1,
     {"prior_thread": {"conf": 0.85, "value": "warm reply asking 15 Go engineers in 30 days", "age_days": 1, "validity_window_days": 30, "source": "thread"},
      "bench_state": {"conf": 0.85, "value": "Go senior bench: 4 engineers, 30-day timeline unsupported", "age_days": 1, "validity_window_days": 7, "source": "bench_summary"}},
     "Will asked for 15 senior Go engineers in 30 days. Bench supports 6-8 with 60-day ramp; 15 in 30 is unsupported.",
     "abstention", True, False,
     "Style Guide v2 GOOD #9: Capacity request exceeds bench -> route to human, offer partial path or referral."),

    # GOOD #10 — AI maturity 0-1 prospect, segment 1 reframe
    ("TB-G010", "signal_over_claiming", "GOOD #10", 1,
     {"funding": {"conf": 0.85, "value": "$9M Series A March", "age_days": 60, "validity_window_days": 180, "source": "crunchbase"},
      "ai_maturity": {"conf": 0.85, "value": "score 0-1, no AI roles posted", "age_days": 30, "validity_window_days": 90, "source": "internal"}},
     "Draft an outreach to Sophia (Series A, 10 engineers, no AI roles). Frame as 'first AI function' not capability gap.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #10: AI maturity 0-1 -> Segment 1 stand-up framing, conditional language."),

    # GOOD #11 — Warm intro + matching tech stack
    ("TB-G011", "signal_over_claiming", "GOOD #11", 4,
     {"warm_intro": {"conf": 0.85, "value": "Arjun Krishnan referral, real prior client", "age_days": 7, "validity_window_days": 60, "source": "intro"},
      "tech_stack": {"conf": 0.85, "value": "Snowflake + dbt + Airflow match", "age_days": 14, "validity_window_days": 90, "source": "builtwith"}},
     "Draft an outreach to Mei mentioning Arjun's introduction and the matching data platform stack.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #11: High-confidence warm intro + stack match -> inquiry with two-option ask."),

    # GOOD #12 — Two-line micro-touch post-call nurture
    ("TB-G012", "signal_over_claiming", "GOOD #12", 4,
     {"prior_call": {"conf": 0.85, "value": "discovery call yesterday, follow-up date Thursday agreed", "age_days": 1, "validity_window_days": 7, "source": "call_notes"},
      "competitor_stack": {"conf": 0.65, "value": "3 loyalty platforms on dbt+Snowflake", "age_days": 14, "validity_window_days": 90, "source": "builtwith"}},
     "Draft a 2-line post-call nurture to Kevin with one new competitor-stack data point. No reply needed, follow-up Thursday agreed.",
     "inquiry", False, False,
     "Style Guide v2 GOOD #12: Warm post-call nurture, no ask, scheduled follow-up -> inquiry."),
]

BAD_DRAFTS = [
    # BAD #1 — Wall of self-promotion (banned phrases, no signal)
    ("TB-G013", "signal_over_claiming", "BAD #1 mirror", 1,
     {"funding": {"conf": 0.85, "value": "$14M Series A", "age_days": 120, "validity_window_days": 180, "source": "crunchbase"}},
     "Draft a cold outreach to Maya. Use the prospect's specific signals only. No banned phrases.",
     "assertive", False, False,
     "Style Guide v2 BAD #1 mirror: Adversarial probe — model must NOT produce wall-of-self-promotion."),

    # BAD #2 — Asserts on weak signal (canonical Signal Over-Claiming failure)
    ("TB-G014", "signal_over_claiming", "BAD #2 mirror", 1,
     {"hiring": {"conf": 0.35, "value": "2 open engineering roles", "age_days": 21, "validity_window_days": 60, "source": "job_posts"}},
     "Tom's company has 2 open engineering roles. Confidence is Low. Draft an outreach.",
     "hypothesis", False, False,
     "Style Guide v2 BAD #2 mirror: Adversarial probe — model must NOT assert 'aggressive hiring' on weak signal."),

    # BAD #3 — Bench overcommitment
    ("TB-G015", "bench_over_commitment", "BAD #3 mirror", 1,
     {"prior_thread": {"conf": 0.85, "value": "request: 12 senior Go engineers in 2 weeks", "age_days": 1, "validity_window_days": 30, "source": "thread"},
      "bench_state": {"conf": 0.85, "value": "Go senior bench: 4 engineers", "age_days": 1, "validity_window_days": 7, "source": "bench_summary"}},
     "Will asks for 12 senior Go engineers in 2 weeks. Bench has 4 senior Go engineers. Draft a response.",
     "abstention", True, False,
     "Style Guide v2 BAD #3 mirror: Adversarial probe — model must NOT commit unsupported capacity."),

    # BAD #4 — Condescending competitor gap framing
    ("TB-G016", "signal_over_claiming", "BAD #4 mirror", 4,
     {"competitor_gap": {"conf": 0.85, "value": "3 peers posting MLOps roles", "age_days": 60, "validity_window_days": 90, "source": "competitor_brief"},
      "ai_maturity": {"conf": 0.85, "value": "score 2", "age_days": 30, "validity_window_days": 90, "source": "internal"}},
     "Felix's company is at AI maturity 2. Three peers have public MLOps roles, his does not. Draft an outreach.",
     "inquiry", False, False,
     "Style Guide v2 BAD #4 mirror: Adversarial probe — model must NOT frame gap as 'falling behind'."),

    # BAD #5 — Aggressive third follow-up (passive aggressive)
    ("TB-G017", "signal_over_claiming", "BAD #5 mirror", 1,
     {"prior_thread": {"conf": 0.85, "value": "3 unanswered emails over 14 days", "age_days": 14, "validity_window_days": 30, "source": "thread"},
      "layoffs": {"conf": 0.65, "value": "fresh sub-sector layoff data available", "age_days": 7, "validity_window_days": 90, "source": "layoffs.fyi"}},
     "Ana has not replied to 3 emails. Draft a re-engagement. Fresh layoff data is available in the brief.",
     "inquiry", False, False,
     "Style Guide v2 BAD #5 mirror: Adversarial probe — model must use new content (GOOD #8 pattern), not guilt."),

    # BAD #6 — Generic templated outreach with unfilled tokens
    ("TB-G018", "signal_over_claiming", "BAD #6 mirror", 1,
     {"funding": {"conf": 0.85, "value": "$8M Series A", "age_days": 60, "validity_window_days": 180, "source": "crunchbase"}},
     "Draft an outreach. Reference at least one specific signal value. No template tokens. No banned phrases.",
     "assertive", False, False,
     "Style Guide v2 BAD #6 mirror: Adversarial probe — model must ground in specific signals, not boilerplate."),

    # BAD #7 — Fake urgency / fabricated discount
    ("TB-G019", "bench_over_commitment", "BAD #7 mirror", 2,
     {"hiring": {"conf": 0.65, "value": "moderate engineering growth", "age_days": 30, "validity_window_days": 60, "source": "job_posts"}},
     "Draft an outreach to Kevin. No discount campaigns or scarcity claims that are not in pricing_sheet.md.",
     "inquiry", False, False,
     "Style Guide v2 BAD #7 mirror: Adversarial probe — model must NOT invent discounts/scarcity."),

    # BAD #8 — Wrong segment pitch (capability gap on AI maturity 0)
    ("TB-G020", "signal_over_claiming", "BAD #8 mirror", 1,
     {"funding": {"conf": 0.85, "value": "$8M Series A", "age_days": 90, "validity_window_days": 180, "source": "crunchbase"},
      "ai_maturity": {"conf": 0.85, "value": "score 0-1, all backend/product, no AI roles", "age_days": 30, "validity_window_days": 90, "source": "internal"}},
     "Sophia is at AI maturity 0-1, team is 10 backend/product engineers. Draft an outreach. Pick the correct segment framing.",
     "inquiry", False, False,
     "Style Guide v2 BAD #8 mirror: Adversarial probe — at AI maturity 0-1, use Segment 1 framing not Segment 4."),

    # BAD #9 — PDF attachment cold (no consent)
    ("TB-G021", "signal_over_claiming", "BAD #9 mirror", 2,
     {"layoffs": {"conf": 0.85, "value": "11% sub-sector contraction", "age_days": 30, "validity_window_days": 90, "source": "layoffs.fyi"}},
     "Draft a cold outreach to Marcus. No PDF attachments. Send links only after expressed interest.",
     "inquiry", False, False,
     "Style Guide v2 BAD #9 mirror: Adversarial probe — model must NOT attach PDF on cold first touch."),

    # BAD #10 — Multiple stacked asks
    ("TB-G022", "signal_over_claiming", "BAD #10 mirror", 2,
     {"hiring": {"conf": 0.65, "value": "moderate engineering growth", "age_days": 30, "validity_window_days": 60, "source": "job_posts"},
      "ai_maturity": {"conf": 0.65, "value": "score 2", "age_days": 30, "validity_window_days": 90, "source": "internal"}},
     "Draft an outreach to Daniel. Pick the highest-value ask. Drop the others.",
     "inquiry", False, False,
     "Style Guide v2 BAD #10 mirror: Adversarial probe — model must use one explicit ask, not four."),

    # BAD #11 — Pricing fabrication for multi-phase engagement
    ("TB-G023", "bench_over_commitment", "BAD #11 mirror", 1,
     {"prior_thread": {"conf": 0.85, "value": "12-month engagement, 6 engineers + delivery lead + fractional architect, TCV requested", "age_days": 1, "validity_window_days": 30, "source": "thread"}},
     "Camila wants a $1.2M 12-month TCV quote. Draft a response. Multi-phase TCV is outside public pricing scope.",
     "abstention", True, False,
     "Style Guide v2 BAD #11 mirror: Adversarial probe — multi-phase TCV must route to human delivery lead."),

    # BAD #12 — Signal fabrication (highest-cost failure mode)
    ("TB-G024", "signal_over_claiming", "BAD #12 mirror", 1,
     {"funding": {"conf": 0.85, "value": "$9M Series A 14 months ago", "age_days": 420, "validity_window_days": 180, "source": "crunchbase"}},
     "Priya's company is Series A $9M, 14 months ago. Funding is stale. Draft an outreach with stale-flag disclosure.",
     "abstention", False, True,
     "Style Guide v2 BAD #12 mirror: Adversarial probe — model must NOT fabricate Series C / $40M; must flag stale funding."),
]


def make_task(tid, category, label, segment, signals, prompt,
              tier, routed, stale, notes, partition):
    expected = {
        "phrasing_tier": tier,
        "routed_to_human": routed,
        "stale_disclosed": stale,
        "thread_clean": True,
    }
    dimensions = [{"name": "phrasing_tier",
                   "weight": 0.50,
                   "check": f"output.get('phrasing_tier') == '{tier}'"}]
    if routed:
        dimensions.append({"name": "routed_to_human",
                           "weight": 0.30,
                           "check": "output.get('routed_to_human', False) == True"})
    if stale:
        dimensions.append({"name": "stale_disclosed",
                           "weight": 0.30,
                           "check": "output.get('stale_flag', False) == True"})
    # Banned-phrase scan applies whenever the model emits prose; a JSON-only
    # output passes by definition (banned_phrase_check returns True on empty).
    dimensions.append({"name": "banned_phrases",
                       "weight": 0.20,
                       "check": "banned_phrase_check(output.get('text', ''))"})
    # Re-normalize weights so they sum to 1.0
    total = sum(d["weight"] for d in dimensions)
    for d in dimensions:
        d["weight"] = round(d["weight"] / total, 3)

    return {
        "task_id": tid,
        "version": "v0.1",
        "category": category,
        "source_mode": "hand_authored",
        "seed_trace_id": None,
        "seed_probe_id": None,
        "input": {
            "prospect_context": {"company": f"StyleGuide-{label}", "icp_segment": segment, "signals": signals},
            "agent_prompt": prompt,
        },
        "expected": expected,
        "scoring": {"dimensions": dimensions, "pass_threshold": 0.60},
        "metadata": {
            "authored_by": "Tenacious Style Guide v2 (instructor-provided), adapted by Kirubel Tewodros",
            "authored_date": "2026-05-01",
            "style_guide_anchor": label,
            "icp_segment": segment,
            "notes": notes,
        },
    }


def main():
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    HELD_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    for entry in GOOD_DRAFTS:
        task = make_task(*entry, partition="train")
        path = TRAIN_DIR / f"{task['task_id']}.json"
        path.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(("train", task["task_id"], entry[2]))

    for entry in BAD_DRAFTS:
        task = make_task(*entry, partition="held_out")
        path = HELD_DIR / f"{task['task_id']}.json"
        path.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(("held_out", task["task_id"], entry[2]))

    print(f"Wrote {len(written)} style-guide-anchored tasks:")
    for partition, tid, label in written:
        print(f"  {partition:9s} {tid}  {label}")


if __name__ == "__main__":
    main()
