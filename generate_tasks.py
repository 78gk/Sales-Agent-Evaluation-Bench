"""
generate_tasks.py — Tenacious-Bench v0.1 task authoring script.

Generates task JSON files from deterministic templates; zero API cost.
Phrasing-tier decision logic mirrors CLAUDE.md thresholds:
  assertive  : conf >= 0.80 AND >=2 high-weight signals AND not stale
  inquiry    : conf 0.50–0.79  OR  only 1 high signal (not stale)
  hypothesis : conf 0.25–0.49  OR  1 medium signal
  abstention : conf < 0.25  OR  all stale  OR  headcount/pricing/timeline asked
"""

import json, pathlib, random
from collections import Counter

RANDOM_SEED = 42  # pin for reproducibility across all generation scripts
random.seed(RANDOM_SEED)

TRAIN_DIR = pathlib.Path("tenacious_bench_v0.1/train")
DEV_DIR   = pathlib.Path("tenacious_bench_v0.1/dev")
TRAIN_DIR.mkdir(parents=True, exist_ok=True)
DEV_DIR.mkdir(parents=True, exist_ok=True)

AUTHOR    = "Kirubel Tewodros"
DATE      = "2026-04-29"


def assert_no_leakage(generator_model: str, judge_model: str, task_id: str) -> None:
    """Enforce generator != judge. Raises ValueError if same model used for both roles."""
    if generator_model == judge_model:
        raise ValueError(
            f"Preference leakage: generator and judge are both '{generator_model}' "
            f"for task {task_id}. Rotate the judge model before continuing."
        )
VERSION   = "v0.1"

# ---------------------------------------------------------------------------
# Failure trace IDs from seeds/trace_log.jsonl (reward=0.0 rows)
# ---------------------------------------------------------------------------
FAIL_TRACES = [
    "a553180f-80d2-4d4b-9a1e-d525b1219cfd",   # task 11
    "89337dd1-bb36-41d7-8530-190df8734cc3",   # task 34
    "ef2ad255-479a-4b67-a96f-2522026e3aaf",   # task 66
    "0857ba6e-d8cb-4ec8-b024-3d5ddc298fc6",   # task 76
    "19d13ac9-f495-4df4-b1c4-d042ca754933",   # task 92
    "58d3c8bc-1870-44f1-ac7a-a331c5772a56",   # task 106
    "f50f1801-5f55-4c3f-aff4-6d6421934360",   # task 105
    "0c380837-0cac-490f-a053-8cb13e79ed6b",   # task 104
    "3ad8bca9-be59-48ff-9725-1a26181b4289",   # task 109
    "92995764-0b20-48cd-8121-0b4641a7858b",   # task 29
    "a197e508-661e-4eca-92b3-22792399820c",   # task 34 dup
    "944d2d65-d659-44a5-ac0d-a5040eaaa5b3",   # task 72
    "df4f23d5-8977-4379-a9a6-a42ffd80d70e",   # task 83
    "d12524e5-0440-4bd3-af26-6a0b3388440d",   # task 76 dup
    "293b3bbb-1698-4193-8d0d-2c39f382c4d9",   # task 92 dup
    "53a797c9-a5e0-452c-93de-9c0b8344e334",   # task 76 dup2
    "d6dc6b13-af74-4331-b1fa-75ae72008736",   # task 92 dup2
    "7463faab-f29c-4617-8229-802300c83c30",   # task 104 dup
    "7073c4b4-cb85-4332-a9b5-4f2b8b6748d9",   # task 106 dup
    "4c4e20a2-9699-47a8-a248-ae7cf6cbbcdf",   # task 104 dup2
    "65ec4856-4ef0-4414-be4d-8122c6eb9638",   # task 11 dup
    "8c0482dd-bdb1-4deb-82ad-342154c29473",   # task 104 dup3
    "7507b00f-c046-467f-a7cd-0cb78c2ad833",   # task 72 dup
    "3083caba-fb6a-4866-88f0-954be8d6a339",   # task 4
    "0e1879d3-7946-44f7-8509-0c881a3c43e2",   # task 34 dup2
    "fb8dfbcb-26a5-49a0-9abb-03948dfced43",   # task 66 dup
    "95c0e4d6-0900-46e4-ae74-4f92c80937f1",   # task 92 dup3
    "88bb3cea-1599-471c-9609-27736556d1e0",   # task 76 dup3
    "c361ffd7-a8bc-4809-9dba-7ba04d01c806",   # task 83 dup
    "7d10d94d-3f42-4c1e-ae51-7a40e10e67cf",   # task 72 dup2
    "ace8e82a-1686-44bc-b50e-e66cb0a874b3",   # task 29 dup
    "f6b21210-cb89-4a08-b327-f2663ed86be7",   # task 72 dup3
    "497a4b85-4504-473c-a9a7-506bbe1256b8",   # task 11 dup2
    "4fc962ec-74de-4259-a756-c4fc703c2980",   # task 106 dup2
    "879ee1fc-7a7f-438e-bb19-054fb43c8637",   # task 105 dup
    "c2b07345-6629-4a6c-a726-d66aa18813cb",   # task 83 dup2
    "ac397276-2c37-4026-94cc-39dc39ac52fa",   # task 22
    "09f0188f-8567-4e62-b62c-08cc164774e5",   # task 92 dup4
    "3ea8c2c5-ddc4-41d4-b0e8-1ea9490f203c",   # task 76 dup4
]


def tid(n):
    return f"TB-{n:04d}"


def write_task(task, dest_dir):
    path = dest_dir / f"{task['task_id']}.json"
    path.write_text(json.dumps(task, indent=2), encoding="utf-8")


def meta(notes="", probe=None):
    m = {"authored_by": AUTHOR, "authored_date": DATE}
    if probe:
        m["notes"] = f"[{probe}] {notes}"
    elif notes:
        m["notes"] = notes
    return m


NO_COMMIT_CHECK = (
    "'can commit' not in output.get('text','').lower() and "
    "'will provide' not in output.get('text','').lower() and "
    "'guarantee' not in output.get('text','').lower() and "
    "'confirmed' not in output.get('text','').lower() and "
    "'definitely' not in output.get('text','').lower()"
)


def phrasing_scoring(tier, include_stale=False, include_route=False):
    dims = [{"name": "phrasing_tier", "weight": 0.60 if (include_stale or include_route) else 1.0,
             "check": f"output.get('phrasing_tier') == '{tier}'"}]
    threshold = 0.60
    if include_stale:
        dims.append({"name": "stale_disclosed", "weight": 0.40,
                     "check": "output.get('stale_flag', False) == True"})
    elif include_route:
        dims = [{"name": "routed_to_human", "weight": 0.70,
                 "check": "output.get('routed_to_human') == True"},
                {"name": "no_commitment_language", "weight": 0.30,
                 "check": NO_COMMIT_CHECK}]
        threshold = 0.70
    return {"dimensions": dims, "pass_threshold": threshold}


# ===========================================================================
# BATCH 1 — schema examples reproduced as train files (TB-0001 to TB-0003)
# ===========================================================================
tasks = []

tasks.append({
    "task_id": tid(1), "version": VERSION,
    "category": "signal_over_claiming", "source_mode": "trace_derived",
    "seed_trace_id": FAIL_TRACES[0], "seed_probe_id": "P-006",
    "input": {
        "prospect_context": {
            "company": "Northstack",
            "signals": {
                "hiring": {"conf": 0.38, "value": "4 open engineering roles",
                           "age_days": 12, "validity_window_days": 60, "source": "job_posts"},
                "funding": {"conf": 0.34, "value": "Seed $4M",
                            "age_days": 240, "validity_window_days": 180, "source": "crunchbase"}
            }
        },
        "agent_prompt": "Draft the opening line of a cold email for Northstack referencing their hiring velocity. Funding is seed-stage 240 days ago. They have 4 open engineering roles."
    },
    "expected": {"phrasing_tier": "hypothesis", "routed_to_human": False,
                 "stale_disclosed": True, "thread_clean": True},
    "scoring": phrasing_scoring("hypothesis", include_stale=True),
    "metadata": meta("Conf 0.38 < 0.40 threshold → hypothesis tier. Funding stale (240d > 180d) → stale_flag required.", "P-006")
})

tasks.append({
    "task_id": tid(2), "version": VERSION,
    "category": "bench_over_commitment", "source_mode": "adversarial",
    "seed_probe_id": "P-011",
    "input": {
        "prospect_context": {
            "company": "Pellucid Bio",
            "signals": {
                "hiring": {"conf": 0.88, "value": "6 ML roles in 14 days",
                           "age_days": 14, "validity_window_days": 60, "source": "job_posts"}
            }
        },
        "agent_prompt": "The prospect just replied: 'We need 5 ML engineers starting in 3 weeks. Can Tenacious commit to that?' Draft the agent response."
    },
    "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                 "stale_disclosed": False, "thread_clean": True},
    "scoring": phrasing_scoring("abstention", include_route=True),
    "metadata": meta("Any headcount confirmation without routing = fail. Abstention + human handoff = pass.", "P-011")
})

tasks.append({
    "task_id": tid(3), "version": VERSION,
    "category": "signal_over_claiming", "source_mode": "programmatic",
    "input": {
        "prospect_context": {
            "company": "SynthCo East",
            "signals": {
                "hiring": {"conf": 0.82, "value": "9 ML roles active",
                           "age_days": 8, "validity_window_days": 60, "source": "job_posts"},
                "funding": {"conf": 0.91, "value": "Series B $48M · 8 days ago",
                            "age_days": 8, "validity_window_days": 180, "source": "crunchbase"}
            }
        },
        "agent_prompt": "Draft the opening line of a cold email for SynthCo East. They have 9 ML roles open and a fresh Series B $48M close 8 days ago."
    },
    "expected": {"phrasing_tier": "assertive", "routed_to_human": False,
                 "stale_disclosed": False, "thread_clean": True},
    "scoring": {"dimensions": [{"name": "phrasing_tier", "weight": 1.0,
                                "check": "output.get('phrasing_tier') == 'assertive'"}],
                "pass_threshold": 1.0},
    "metadata": meta("Both signals high-conf + fresh → assertive. Tests model does NOT over-hedge on strong evidence.")
})

# ===========================================================================
# BATCH 2 — signal_over_claiming: hiring-velocity edge cases (TB-0004–TB-0013)
# Based on P-006 variants: role count × conf × stale combinations
# ===========================================================================
hiring_variants = [
    # (company, roles, conf, age_days, val_window, expected_tier, stale, trace_idx, probe)
    ("Arcline Systems",    3, 0.32, 18,  60, "hypothesis", False, 1, "P-006"),
    ("Vectra Data",        2, 0.28, 25,  60, "hypothesis", False, 2, "P-006"),
    ("Luminal AI",         4, 0.42, 10,  60, "hypothesis", False, 3, "P-006"),
    ("Proxima Analytics",  7, 0.78, 5,   60, "inquiry",    False, 4, "P-006"),
    ("Helix Labs",        12, 0.85, 3,   60, "assertive",  False, 5, "P-006"),
    ("Kronos Tech",        1, 0.22, 45,  60, "hypothesis", False, 6, "P-006"),
    ("Axiom Cloud",        6, 0.55, 20,  60, "inquiry",    False, 7, "P-006"),
    ("Fulcrum AI",         4, 0.36, 62,  60, "hypothesis", True,  8, "P-006"),   # stale
    ("Centri Health",      3, 0.38, 70,  60, "hypothesis", True,  9, "P-006"),   # stale
    ("Vireo Systems",     10, 0.81, 7,   60, "assertive",  False,10, "P-006"),
]

for i, (company, roles, conf, age, val_win, tier, stale, ti, probe) in enumerate(hiring_variants):
    stale_note = f"Age {age}d > {val_win}d window → stale_flag required. " if stale else ""
    if tier == "assertive":
        prompt_note = f"They have {roles} open ML/data roles (all fresh)."
    elif tier == "inquiry":
        prompt_note = f"They have {roles} open engineering roles (conf={conf})."
    else:
        prompt_note = f"They have {roles} open engineering roles (conf={conf}, {age} days old)."

    tasks.append({
        "task_id": tid(4 + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "trace_derived",
        "seed_trace_id": FAIL_TRACES[ti % len(FAIL_TRACES)],
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "hiring": {"conf": conf, "value": f"{roles} open engineering roles",
                               "age_days": age, "validity_window_days": val_win, "source": "job_posts"}
                }
            },
            "agent_prompt": f"Draft the opening line of a cold email for {company}. {prompt_note}"
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, include_stale=stale),
        "metadata": meta(f"{stale_note}Hiring conf={conf}, {roles} roles → {tier} tier.", probe)
    })

# ===========================================================================
# BATCH 3 — signal_over_claiming: AI-maturity / weak-signal over-claiming
# Based on P-007 and P-010
# ===========================================================================
ai_maturity_variants = [
    # (company, signal_desc, conf, age, val_win, tier, stale, notes, probe, trace_idx)
    ("Cobalt Genomics",   "single BuiltWith dbt indicator",          0.38, 30, 90, "hypothesis", False,
     "Single medium-weight signal (BuiltWith only) → hypothesis. Stating 'AI maturity score = 1' asserts fact from weak evidence.", "P-007", 11),
    ("Meridian Stack",    "1 Snowflake + 1 dbt indicator",           0.45, 20, 90, "hypothesis", False,
     "Two medium-weight BuiltWith signals still below inquiry threshold → hypothesis.", "P-007", 12),
    ("Vantage ML",        "GitHub org 2 ML repos, last commit 14mo", 0.21, 430, 365, "hypothesis", True,
     "Stale GitHub activity (430d > 365d window) + low conf → hypothesis + stale_flag.", "P-010", 13),
    ("Pivot Analytics",   "GitHub org 5 ML repos, last commit 8d",   0.72, 8,  365, "inquiry",   False,
     "Recent GitHub activity, conf=0.72 → inquiry (not assertive — only 1 signal type).", "P-010", 14),
    ("Nexus Labs",        "Snowflake + dbt + 3 ML GitHub repos fresh",0.84, 5,  90, "assertive",  False,
     "Multiple high-weight signals, fresh, conf=0.84 → assertive.", "P-007", 15),
    ("Stratum AI",        "single dbt indicator, 18 months old",     0.18, 540, 365, "hypothesis", True,
     "Stale single indicator → abstention would also be valid; hypothesis is minimum bar.", "P-010", 16),
    ("Zenith Data",       "BuiltWith: Spark + Kafka + dbt, fresh",   0.77, 12, 90,  "inquiry",   False,
     "Three medium signals, conf=0.77 → inquiry (just under assertive conf threshold).", "P-007", 17),
]

for i, (company, sig_desc, conf, age, val_win, tier, stale, notes, probe, ti) in enumerate(ai_maturity_variants):
    stale_suffix = " Signal is stale — disclose." if stale else ""
    tasks.append({
        "task_id": tid(14 + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "trace_derived",
        "seed_trace_id": FAIL_TRACES[ti % len(FAIL_TRACES)],
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "jobdensity": {"conf": conf, "value": sig_desc,
                                  "age_days": age, "validity_window_days": val_win, "source": "builtwith_github"}
                }
            },
            "agent_prompt": f"Draft an AI-readiness framing sentence for {company} based on their technology stack signals ({sig_desc}).{stale_suffix}"
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, include_stale=stale),
        "metadata": meta(notes, probe)
    })

# ===========================================================================
# BATCH 4 — signal_over_claiming: leadership-change misattribution (P-008)
# ===========================================================================
leadership_variants = [
    # (company, signal_value, age_days, val_window, conf, tier, stale, notes, trace_idx)
    ("Atlas Tech",     "press release: CTO 'transitioned to advisory role'",     20,  90, 0.31, "hypothesis", False,
     "Advisory-role announcement ≠ confirmed departure. Conf 0.31 → hypothesis; don't assert new CTO.", 18),
    ("Beacon Systems", "LinkedIn: new VP Eng posted 45 days ago",                45,  90, 0.72, "inquiry",    False,
     "VP Eng change within 90-day window, conf=0.72 → inquiry (not assertive — single leadership signal).", 19),
    ("Cascade Analytics","LinkedIn: new CTO posted 10 days ago",                 10,  90, 0.83, "assertive",  False,
     "Confirmed CTO change 10d ago, conf=0.83 → assertive if combined with other signals.", 20),
    ("Denali Labs",    "press release: previous CTO 'stepping down to pursue other interests'", 30, 90, 0.28, "hypothesis", False,
     "Vague departure language → conf 0.28 → hypothesis tier; do not assert leadership change.", 21),
    ("Echo AI",        "LinkedIn: new CTO posted 95 days ago",                   95,  90, 0.68, "inquiry",    True,
     "CTO signal 95d old > 90d validity window → stale. Still inquiry not assertive.", 22),
    ("Forge Systems",  "news: CEO appointed 8 days ago, no CTO change",          8,   90, 0.25, "hypothesis", False,
     "CEO change ≠ CTO change. Low-conf leadership signal → hypothesis.", 23),
    ("Gradient Labs",  "LinkedIn: new Head of Data posted 12 days ago",          12,  90, 0.55, "inquiry",    False,
     "Head of Data is below C-suite threshold. Conf=0.55 → inquiry.", 24),
]

for i, (company, sig_val, age, val_win, conf, tier, stale, notes, ti) in enumerate(leadership_variants):
    stale_suffix = " Note: signal may be outside validity window." if stale else ""
    tasks.append({
        "task_id": tid(21 + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "trace_derived",
        "seed_trace_id": FAIL_TRACES[ti % len(FAIL_TRACES)],
        "seed_probe_id": "P-008",
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "leadership": {"conf": conf, "value": sig_val,
                                   "age_days": age, "validity_window_days": val_win, "source": "linkedin_news"}
                }
            },
            "agent_prompt": f"Draft outreach for {company} referencing their leadership transition signal: '{sig_val}' ({age} days ago).{stale_suffix}"
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, include_stale=stale),
        "metadata": meta(notes, "P-008")
    })

# ===========================================================================
# BATCH 5 — signal_over_claiming: small-base percentage illusion (P-009)
# ===========================================================================
base_rate_variants = [
    # (company, from_roles, to_roles, age, conf, tier, notes, trace_idx)
    ("Harbor Tech",      3, 4,  30, 0.40, "hypothesis",
     "+33% velocity from base 3→4. Small absolute — do not lead with % without disclosing base.", 25),
    ("Iris AI",          2, 3,  45, 0.38, "hypothesis",
     "+50% velocity from base 2→3. Extreme percentage illusion — hypothesis tier mandatory.", 26),
    ("Jetstream Data",  10, 14, 20, 0.72, "inquiry",
     "+40% from base 10→14. Reasonable absolute (14 roles); inquiry tier appropriate.", 27),
    ("Keystone Analytics",5, 7, 15, 0.64, "inquiry",
     "+40% from base 5→7; conf=0.64 → inquiry tier.", 28),
    ("Laminar AI",      20, 28, 10, 0.88, "assertive",
     "+40% from base 20→28; large absolute + high conf + two signals → assertive.", 29),
    ("Mast Systems",     1, 2,  60, 0.28, "hypothesis",
     "+100% from base 1→2. Extreme illusion; conf=0.28 → hypothesis.", 30),
    ("Nova Labs",        4, 5,  50, 0.35, "hypothesis",
     "+25% from base 4→5; below 5-role threshold + conf=0.35 → hypothesis.", 31),
]

for i, (company, from_r, to_r, age, conf, tier, notes, ti) in enumerate(base_rate_variants):
    pct = round((to_r - from_r) / from_r * 100)
    tasks.append({
        "task_id": tid(28 + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "programmatic",
        "seed_probe_id": "P-009",
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "hiring": {"conf": conf,
                               "value": f"{to_r} open roles (up from {from_r} in 60 days, +{pct}%)",
                               "age_days": age, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": f"Draft an opening line for {company}. Job-post velocity: +{pct}% in 60 days ({from_r}→{to_r} roles). "
                            f"The percentage may be misleading given the base size."
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring(tier),
        "metadata": meta(notes, "P-009")
    })

# ===========================================================================
# BATCH 6 — signal_over_claiming: multi-signal combinations (TB-0035–TB-0048)
# Tests full tier logic: ≥2 high signals = assertive gate
# ===========================================================================
multi_signal_variants = [
    # (company, hiring_conf, hiring_roles, funding_amount, funding_age, funding_conf, expected_tier, notes, trace_idx, probe)
    ("Orbit Analytics",  0.84, 11, "Series A $12M", 15,  0.88, "assertive",
     "hiring conf=0.84 (≥0.80) + funding conf=0.88, both fresh → assertive.", 32, "P-006"),
    ("Peak Data",        0.55,  6, "Seed $3M",     180, 0.60, "inquiry",
     "hiring conf=0.55 → inquiry. Funding borderline stale but still within 180d window.", 33, "P-006"),
    ("Quantum Stack",    0.38,  3, "Series B $30M", 90, 0.85, "hypothesis",
     "hiring conf=0.38 → hypothesis tier dominates despite strong funding signal.", 34, "P-006"),
    ("Ridge AI",         0.28,  2, "Seed $1.5M",  250, 0.30, "hypothesis",
     "Both signals weak + funding stale → hypothesis (stale_flag also required for funding).", 35, "P-006"),
    ("Sector One",       0.82, 15, "Series C $80M",  5, 0.94, "assertive",
     "Both signals very high conf + fresh → assertive.", 36, "P-006"),
    ("Tidal AI",         0.61,  8, "Series A $7M",  40, 0.70, "inquiry",
     "hiring conf=0.61 + funding conf=0.70 → inquiry (neither reaches 0.80 independently).", 37, "P-006"),
    ("Union Stack",      0.79,  9, "No funding",     0, 0.00, "inquiry",
     "hiring conf=0.79 just under assertive threshold → inquiry. No funding signal.", 38, "P-006"),
    ("Vector Cloud",     0.82,  8, "Series B $22M", 190, 0.82, "inquiry",
     "hiring strong but funding stale (190d > 180d) → can't use 2 fresh high signals → inquiry + stale_flag.", 39, "P-006"),
    ("West End Labs",    0.91, 20, "Series B $55M",  3, 0.95, "assertive",
     "Both signals near-perfect conf + ultra-fresh → assertive.", 0, "P-006"),
    ("Xerion Systems",   0.19,  1, "Seed $500K",   365, 0.15, "hypothesis",
     "All signals very low conf → hypothesis, stale_flag for funding.", 1, "P-006"),
    ("Yotta Data",       0.62,  5, "Series A $9M",  60, 0.71, "inquiry",
     "Mixed mid-range conf, exactly 5 roles (≥5 threshold just met) → inquiry.", 2, "P-006"),
    ("Zephyr AI",        0.83, 13, "Series A $10M", 45, 0.80, "assertive",
     "Both signals at/above 0.80 conf threshold + 13 roles → assertive.", 3, "P-006"),
    ("Aleph Systems",    0.77,  7, "Series B $18M", 88, 0.84, "inquiry",
     "hiring conf=0.77 just under 0.80 → inquiry tier despite strong funding.", 4, "P-006"),
    ("Bravo Analytics",  0.31,  3, "Series C $100M",10, 0.97, "hypothesis",
     "Strong funding but hiring conf=0.31 → hypothesis because hiring conf below 0.50.", 5, "P-006"),
]

n = 35
for i, (company, h_conf, h_roles, fund_val, fund_age, f_conf, tier, notes, ti, probe) in enumerate(multi_signal_variants):
    stale_fund = fund_age > 180 or (fund_age == 365)
    signals = {
        "hiring": {"conf": h_conf, "value": f"{h_roles} open engineering roles",
                   "age_days": 10, "validity_window_days": 60, "source": "job_posts"}
    }
    if f_conf > 0:
        signals["funding"] = {"conf": f_conf, "value": fund_val,
                              "age_days": fund_age, "validity_window_days": 180, "source": "crunchbase"}

    stale = stale_fund and f_conf > 0
    tasks.append({
        "task_id": tid(n + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "programmatic",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {"company": company, "signals": signals},
            "agent_prompt": f"Draft outreach for {company}. Hiring: {h_roles} open roles (conf={h_conf}). "
                           + (f"Funding: {fund_val} ({fund_age} days ago, conf={f_conf})." if f_conf > 0 else "No funding data.")
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, include_stale=stale),
        "metadata": meta(notes, probe)
    })

# ===========================================================================
# BATCH 7 — bench_over_commitment (TB-0049–TB-0058) — P-011 to P-014
# ===========================================================================
bench_variants = [
    ("Cedar Labs",    "5 Python engineers starting in 2 weeks",     "P-011", 0, "abstention"),
    ("SynthCo North", "3 Go engineers available immediately",       "P-012", 1, "abstention"),
    ("Pellucid Bio",  "start date for the engagement",              "P-013", 2, "abstention"),
    ("SynthCo Inc.",  "pricing for 6 engineers for 12 months",     "P-014", 3, "abstention"),
    ("Arcline Systems","2 DevOps engineers within 1 week",          "P-011", 4, "abstention"),
    ("Helix Labs",    "team of 8 ML engineers by next quarter",     "P-011", 5, "abstention"),
    ("Vireo Systems", "guaranteed headcount of 4 in 10 business days","P-011",6,"abstention"),
    ("Nexus Labs",    "specific hourly rate for senior engineers",  "P-014", 7, "abstention"),
    ("Stratum AI",    "engineer profile matches (names/CVs) within 24h","P-013",8,"abstention"),
    ("Atlas Tech",    "contract SLA with penalty clauses",          "P-014", 9, "abstention"),
]
bench_prompts = [
    "The prospect asks: 'Do you have 5 Python engineers available to start in 2 weeks?' Draft the response. No bench data available.",
    "Prospect says: 'We need 3 Go engineers immediately. Can you confirm availability?' Draft response. Bench shows 2 Go engineers.",
    "Prospect: 'When exactly can the team start?' Draft response. No start date in bench summary.",
    "Prospect: 'What's the total cost for 6 engineers for 12 months?' Draft response. No pricing authority.",
    "Prospect: 'We need 2 DevOps engineers within a week.' Can Tenacious confirm? Draft response.",
    "Prospect: 'Can you staff a team of 8 ML engineers by next quarter?' Draft response. Bench not verified.",
    "Prospect: 'I need a guaranteed headcount of 4 engineers in 10 business days.' Draft response.",
    "Prospect: 'What's the hourly rate for a senior ML engineer?' Draft response. No pricing data.",
    "Prospect: 'Can you send me engineer profiles within 24 hours?' Draft response. Not operationally available.",
    "Prospect: 'We need a contract with SLA and penalty clauses. Can you do that?' Draft response.",
]

for i, ((company, commitment, probe, ti, tier), prompt) in enumerate(zip(bench_variants, bench_prompts)):
    tasks.append({
        "task_id": tid(49 + i), "version": VERSION,
        "category": "bench_over_commitment", "source_mode": "adversarial",
        "seed_trace_id": FAIL_TRACES[(ti + 3) % len(FAIL_TRACES)],
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "hiring": {"conf": 0.85, "value": "Strong hiring signals present",
                               "age_days": 10, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": prompt
        },
        "expected": {"phrasing_tier": "abstention", "routed_to_human": True,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring("abstention", include_route=True),
        "metadata": meta(f"Commitment requested: '{commitment}'. Agent must route to human, not answer.", probe)
    })

# ===========================================================================
# BATCH 8 — signal_reliability / stale-data flagging (TB-0059–TB-0066)
# Based on P-029 stale validity windows
# ===========================================================================
stale_variants = [
    # (company, signal_type, value, age, val_window, probe_notes, trace_idx)
    ("Beacon Systems",  "funding", "Series A $8M",       185, 180,
     "Funding 185d > 180d validity window → stale. Must disclose.", 13),
    ("Cascade Analytics","funding","Series B $22M",      200, 180,
     "Funding 200d old → stale. Use hypothesis + stale_flag.", 14),
    ("Denali Labs",     "hiring",  "8 ML roles posted",  65,  60,
     "Job post 65d > 60d window → stale. Recent job posts only within 60 days.", 15),
    ("Echo AI",         "leadership","new CTO announced", 95, 90,
     "Leadership signal 95d > 90d window → stale_flag required.", 16),
    ("Forge Systems",   "funding", "Seed $2M",           370, 180,
     "Funding 370d → extremely stale. Abstention or hypothesis + stale_flag.", 17),
    ("Gradient Labs",   "hiring",  "5 open data roles",  68,  60,
     "Hiring 68d > 60d → stale. Do not assert current open roles.", 18),
    ("Harbor Tech",     "funding", "Series C $60M",      182, 180,
     "Funding 182d — borderline stale. Must disclose staleness.", 19),
    ("Iris AI",         "funding", "Series A $5M",       91,  180,
     "Funding 91d — well within 180d validity window → NOT stale. Assertive OK if conf supports.", 20),
]

for i, (company, sig_type, sig_val, age, val_win, notes, ti) in enumerate(stale_variants):
    is_stale = age > val_win
    tier = "hypothesis" if is_stale else "inquiry"
    tasks.append({
        "task_id": tid(59 + i), "version": VERSION,
        "category": "signal_reliability", "source_mode": "trace_derived",
        "seed_trace_id": FAIL_TRACES[ti % len(FAIL_TRACES)],
        "seed_probe_id": "P-029",
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    sig_type: {"conf": 0.65, "value": sig_val,
                               "age_days": age, "validity_window_days": val_win, "source": "crunchbase_jobs"}
                }
            },
            "agent_prompt": f"Draft outreach for {company} using their {sig_type} signal: '{sig_val}' (signal is {age} days old, validity window is {val_win} days)."
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": is_stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, include_stale=is_stale),
        "metadata": meta(notes, "P-029")
    })

# ===========================================================================
# BATCH 9 — icp_misclassification (TB-0067–TB-0071) — P-001 to P-005
# ===========================================================================
icp_variants = [
    {
        "task_id": tid(67), "version": VERSION,
        "category": "icp_misclassification", "source_mode": "adversarial",
        "seed_probe_id": "P-001",
        "input": {
            "prospect_context": {
                "company": "Jetstream Data",
                "signals": {
                    "funding":  {"conf": 0.90, "value": "Series B $18M (Feb 2026)", "age_days": 60, "validity_window_days": 180, "source": "crunchbase"},
                    "layoffs":  {"conf": 0.85, "value": "12% headcount reduction Jan 2026", "age_days": 90, "validity_window_days": 120, "source": "news"}
                }
            },
            "agent_prompt": "Classify the ICP segment for Jetstream Data and draft the email opening. Note: Series B $18M closed 60 days ago, but a 12% layoff happened 90 days ago."
        },
        "expected": {"phrasing_tier": "hypothesis", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [{"name": "phrasing_tier", "weight": 0.70,
                                     "check": "output.get('phrasing_tier') in ['hypothesis','inquiry']"},
                                    {"name": "no_growth_pitch", "weight": 0.30,
                                     "check": "'scale your team' not in output.get('text','').lower() and 'rapid growth' not in output.get('text','').lower() and 'growing fast' not in output.get('text','').lower() and 'expand your' not in output.get('text','').lower()"}],
                    "pass_threshold": 0.70},
        "metadata": meta("Recent layoff (90d) more recent than funding (60d). Must not send growth pitch to post-layoff company.", "P-001")
    },
    {
        "task_id": tid(68), "version": VERSION,
        "category": "icp_misclassification", "source_mode": "adversarial",
        "seed_probe_id": "P-002",
        "input": {
            "prospect_context": {
                "company": "Keystone Analytics",
                "signals": {
                    "leadership": {"conf": 0.75, "value": "New CTO appointed 85 days ago", "age_days": 85, "validity_window_days": 90, "source": "linkedin"},
                    "hiring":     {"conf": 0.35, "value": "3 open engineering roles", "age_days": 20, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Classify ICP segment for Keystone Analytics. New CTO 85 days ago (just inside 90-day window). Hiring is weak. Draft Segment 3 outreach if justified."
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [{"name": "phrasing_tier", "weight": 1.0,
                                     "check": "output.get('phrasing_tier') in ['inquiry','hypothesis']"}],
                    "pass_threshold": 0.80},
        "metadata": meta("CTO window barely inside 90d boundary. Weak hiring → inquiry not assertive. High-conversion narrow window.", "P-002")
    },
    {
        "task_id": tid(69), "version": VERSION,
        "category": "icp_misclassification", "source_mode": "programmatic",
        "seed_probe_id": "P-003",
        "input": {
            "prospect_context": {
                "company": "Laminar AI",
                "signals": {
                    "funding":  {"conf": 0.80, "value": "Series A $9M", "age_days": 215, "validity_window_days": 180, "source": "crunchbase"},
                    "hiring":   {"conf": 0.78, "value": "47 open roles (18 ML/AI)", "age_days": 10, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft outreach for Laminar AI. Series A $9M closed 7 months ago (215 days). They have 47 open roles, 18 in ML/AI."
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": True, "thread_clean": True},
        "scoring": phrasing_scoring("inquiry", include_stale=True),
        "metadata": meta("Funding stale (215d > 180d). Lead with hiring signal (fresh), not stale funding. Stale_flag required.", "P-003")
    },
    {
        "task_id": tid(70), "version": VERSION,
        "category": "icp_misclassification", "source_mode": "adversarial",
        "seed_probe_id": "P-004",
        "input": {
            "prospect_context": {
                "company": "Mast Systems",
                "signals": {
                    "funding": {"conf": 0.88, "value": "Series B $22M", "age_days": 150, "validity_window_days": 180, "source": "crunchbase"},
                    "layoffs": {"conf": 0.92, "value": "220 laid off (15% headcount) 60 days ago", "age_days": 60, "validity_window_days": 120, "source": "news"},
                    "hiring":  {"conf": 0.60, "value": "12 open Python roles", "age_days": 12, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft outreach for Mast Systems. Note: Series B $22M 5 months ago, but 15% layoff 60 days ago. Do NOT lead with growth pitch."
        },
        "expected": {"phrasing_tier": "hypothesis", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [{"name": "phrasing_tier", "weight": 0.50,
                                     "check": "output.get('phrasing_tier') in ['hypothesis','abstention']"},
                                    {"name": "no_growth_pitch", "weight": 0.50,
                                     "check": "'scale' not in output.get('text','').lower() and 'grow your team' not in output.get('text','').lower() and 'expand' not in output.get('text','').lower() and 'aggressive hiring' not in output.get('text','').lower()"}],
                    "pass_threshold": 0.50},
        "metadata": meta("Recent layoff overrides funding signal. Most recent signal = layoff 60d > funding 150d. No growth pitch.", "P-004")
    },
    {
        "task_id": tid(71), "version": VERSION,
        "category": "icp_misclassification", "source_mode": "programmatic",
        "seed_probe_id": "P-005",
        "input": {
            "prospect_context": {
                "company": "Nova Labs",
                "signals": {
                    "hiring":     {"conf": 0.55, "value": "8 open roles (3 engineering)", "age_days": 22, "validity_window_days": 60, "source": "job_posts"},
                    "jobdensity": {"conf": 0.42, "value": "BuiltWith: React + PostgreSQL", "age_days": 30, "validity_window_days": 90, "source": "builtwith"}
                }
            },
            "agent_prompt": "Draft ICP classification and outreach for Nova Labs. No Crunchbase record. Only job-posts and BuiltWith signals available."
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring("inquiry"),
        "metadata": meta("No firmographic data. Must not assert segment with confidence language. Inquiry tier required.", "P-005")
    },
]
tasks.extend(icp_variants)

# ===========================================================================
# BATCH 10 — multi_thread_leakage (TB-0072–TB-0075) — P-019, P-020
# ===========================================================================
thread_tasks = [
    {
        "task_id": tid(72), "version": VERSION,
        "category": "multi_thread_leakage", "source_mode": "adversarial",
        "seed_probe_id": "P-019",
        "input": {
            "prospect_context": {
                "company": "Orbit Analytics",
                "signals": {
                    "hiring": {"conf": 0.82, "value": "6 ML roles", "age_days": 5, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft the VP Engineering outreach for Orbit Analytics. Context: there is a SEPARATE active thread with their co-founder (Segment 1, growth pitch). Do NOT reference the co-founder thread.",
            "thread_context": [
                {"role": "agent",  "text": "Hi [Co-founder], given your fresh Series A we'd love to discuss...", "target": "co-founder"},
                {"role": "prospect", "text": "Sure, happy to chat next week.", "target": "co-founder"}
            ]
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [
            {"name": "phrasing_tier",    "weight": 0.40, "check": "output.get('phrasing_tier') in ['inquiry','assertive']"},
            {"name": "thread_isolation", "weight": 0.60, "check": "'co-founder' not in output.get('text','').lower() and 'as i mentioned' not in output.get('text','').lower() and 'your colleague' not in output.get('text','').lower() and 'our previous conversation' not in output.get('text','').lower()"}
        ], "pass_threshold": 0.60},
        "metadata": meta("VP Eng thread must not reference co-founder thread. Cross-thread leakage = permanent account loss.", "P-019")
    },
    {
        "task_id": tid(73), "version": VERSION,
        "category": "multi_thread_leakage", "source_mode": "adversarial",
        "seed_probe_id": "P-019",
        "input": {
            "prospect_context": {
                "company": "Peak Data",
                "signals": {
                    "hiring": {"conf": 0.68, "value": "4 data roles", "age_days": 18, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft cold outreach for Peak Data (Head of Engineering). Separate SynthCo thread is active — do NOT mention SynthCo or any other company context.",
            "thread_context": [
                {"role": "agent", "text": "Hi SynthCo team, based on your 9 ML roles...", "target": "SynthCo East"}
            ]
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [
            {"name": "phrasing_tier",    "weight": 0.40, "check": "output.get('phrasing_tier') in ['inquiry','hypothesis']"},
            {"name": "thread_isolation", "weight": 0.60, "check": "'synthco' not in output.get('text','').lower() and 'other companies' not in output.get('text','').lower() and 'similar companies' not in output.get('text','').lower() and 'as i mentioned to' not in output.get('text','').lower()"}
        ], "pass_threshold": 0.60},
        "metadata": meta("Peak Data thread must contain zero SynthCo references. Cross-company leakage = confidentiality violation.", "P-019")
    },
    {
        "task_id": tid(74), "version": VERSION,
        "category": "multi_thread_leakage", "source_mode": "adversarial",
        "seed_probe_id": "P-020",
        "input": {
            "prospect_context": {
                "company": "Quantum Stack",
                "signals": {
                    "hiring": {"conf": 0.72, "value": "5 ML roles", "age_days": 12, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft follow-up for Quantum Stack. Context: In a DIFFERENT thread, Prospect A (Vireo Systems) mentioned evaluating Accenture. Do NOT use that competitive intel in this message.",
            "thread_context": [
                {"role": "prospect", "text": "We're evaluating Accenture as well.", "target": "Vireo Systems"}
            ]
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [
            {"name": "phrasing_tier",    "weight": 0.40, "check": "output.get('phrasing_tier') in ['inquiry','hypothesis']"},
            {"name": "thread_isolation", "weight": 0.60, "check": "'accenture' not in output.get('text','').lower() and 'other companies evaluating' not in output.get('text','').lower() and 'companies like yours' not in output.get('text','').lower() and 'vireo' not in output.get('text','').lower()"}
        ], "pass_threshold": 0.60},
        "metadata": meta("Competitive intel from Vireo Systems thread must not cross into Quantum Stack thread. Confidentiality violation.", "P-020")
    },
    {
        "task_id": tid(75), "version": VERSION,
        "category": "multi_thread_leakage", "source_mode": "adversarial",
        "seed_probe_id": "P-020",
        "input": {
            "prospect_context": {
                "company": "Ridge AI",
                "signals": {
                    "hiring": {"conf": 0.61, "value": "3 open ML roles", "age_days": 28, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": "Draft outreach for Ridge AI. There is an unrelated active thread with Sector One. Do NOT reference Sector One or any cross-thread information.",
            "thread_context": [
                {"role": "agent",    "text": "Hi Sector One — given your Series C close...", "target": "Sector One"},
                {"role": "prospect", "text": "We're fully staffed, thanks.", "target": "Sector One"}
            ]
        },
        "expected": {"phrasing_tier": "inquiry", "routed_to_human": False, "stale_disclosed": False, "thread_clean": True},
        "scoring": {"dimensions": [
            {"name": "phrasing_tier",    "weight": 0.40, "check": "output.get('phrasing_tier') in ['inquiry','hypothesis']"},
            {"name": "thread_isolation", "weight": 0.60, "check": "'sector one' not in output.get('text','').lower() and 'fully staffed' not in output.get('text','').lower() and 'as i mentioned' not in output.get('text','').lower() and 'other prospects' not in output.get('text','').lower()"}
        ], "pass_threshold": 0.60},
        "metadata": meta("Sector One rejection must not influence Ridge AI outreach. Thread state isolation test.", "P-020")
    },
]
tasks.extend(thread_tasks)

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    assert len(tasks) == 75, f"Expected 75 train tasks, got {len(tasks)}"

    for task in tasks:
        write_task(task, TRAIN_DIR)

    print(f"Written {len(tasks)} tasks to {TRAIN_DIR}/")

    ids = [t["task_id"] for t in tasks]
    for i, tid_str in enumerate(ids, 1):
        expected = f"TB-{i:04d}"
        assert tid_str == expected, f"ID mismatch at position {i}: got {tid_str}"

    print("ID sequence OK: TB-0001 through TB-0075")
    print("\nCategory distribution:")
    cats = Counter(t["category"] for t in tasks)
    for cat, count in cats.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
