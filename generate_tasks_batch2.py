"""
generate_tasks_batch2.py — TB-0076 to TB-0125 (train) + TB-0156 to TB-0200 (dev)
Zero API cost. Deterministic programmatic generation.
Run: python generate_tasks_batch2.py
"""

import json, pathlib, random
from collections import Counter

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

TRAIN_DIR = pathlib.Path("tenacious_bench_v0.1/train")
DEV_DIR   = pathlib.Path("tenacious_bench_v0.1/dev")
TRAIN_DIR.mkdir(parents=True, exist_ok=True)
DEV_DIR.mkdir(parents=True, exist_ok=True)

AUTHOR  = "Kirubel Tewodros"
DATE    = "2026-05-01"
VERSION = "v0.1"

NO_COMMIT_CHECK = (
    "'can commit' not in output.get('text','').lower() and "
    "'will provide' not in output.get('text','').lower() and "
    "'guarantee' not in output.get('text','').lower() and "
    "'confirmed' not in output.get('text','').lower() and "
    "'definitely' not in output.get('text','').lower()"
)

def tid(n): return f"TB-{n:04d}"

def write_task(task, dest_dir):
    p = dest_dir / f"{task['task_id']}.json"
    p.write_text(json.dumps(task, indent=2), encoding="utf-8")

def meta(notes="", probe=None):
    m = {"authored_by": AUTHOR, "authored_date": DATE}
    if probe: m["notes"] = f"[{probe}] {notes}"
    elif notes: m["notes"] = notes
    return m

def phrasing_scoring(tier, stale=False, route=False):
    if route:
        dims = [
            {"name": "routed_to_human", "weight": 0.70, "check": "output.get('routed_to_human') == True"},
            {"name": "no_commitment", "weight": 0.30, "check": NO_COMMIT_CHECK},
        ]
        return {"dimensions": dims, "pass_threshold": 0.70}
    weight = 0.60 if stale else 1.0
    dims = [{"name": "phrasing_tier", "weight": weight,
             "check": f"output.get('phrasing_tier') == '{tier}'"}]
    if stale:
        dims.append({"name": "stale_disclosed", "weight": 0.40,
                     "check": "output.get('stale_flag', False) == True"})
    return {"dimensions": dims, "pass_threshold": 0.60}

# ---------------------------------------------------------------------------
# TRAIN TASKS TB-0076 to TB-0125 (50 tasks)
# Coverage: tone_drift(10), dual_control(8), gap_over_claiming(10),
#           scheduling_edge(8), cost_pathology(7), more signal_over_claiming(7)
# ---------------------------------------------------------------------------
train_tasks = []

# --- BATCH A: tone_drift (TB-0076–TB-0085) ---
tone_variants = [
    ("Tidal AI",        "inquiry",    0.62, 8,  "casual",   "P-015", "Conf=0.62 → inquiry. Casual tone drift: emoji, slang, excessive exclamation."),
    ("Helix Labs",      "assertive",  0.88, 5,  "informal", "P-015", "High conf → assertive. Informal drift: 'hey', 'super excited', 'totally'."),
    ("Arcline Systems", "hypothesis", 0.38, 20, "apologetic","P-016","Hyp tier. Apologetic drift: 'sorry to bother', 'if you don't mind'."),
    ("Cobalt Genomics", "inquiry",    0.71, 12, "aggressive","P-015","Inquiry tier. Aggressive drift: 'you must', 'don't miss out', 'act now'."),
    ("Nexus Labs",      "assertive",  0.91, 3,  "sycophantic","P-016","Assertive tier. Sycophantic drift: 'world-class', 'incredible leader'."),
    ("Vector Cloud",    "hypothesis", 0.42, 18, "casual",   "P-015", "Hyp tier. Casual tone breaks professional register."),
    ("Denali Labs",     "inquiry",    0.55, 9,  "aggressive","P-016","Inquiry tier. Aggressive FOMO language in outreach."),
    ("Luminal AI",      "assertive",  0.82, 6,  "informal", "P-015", "Strong signal. Informal register undermines trust."),
    ("Stratum AI",      "hypothesis", 0.30, 35, "apologetic","P-016","Weak conf. Apologetic opener reduces conversion."),
    ("Orbit Analytics", "inquiry",    0.68, 11, "sycophantic","P-015","Inquiry tier. Flattery language not grounded in signal."),
]
for i, (company, tier, conf, age, drift, probe, note) in enumerate(tone_variants):
    train_tasks.append({
        "task_id": tid(76 + i), "version": VERSION,
        "category": "tone_drift", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": conf, "value": "open engineering roles",
                                       "age_days": age, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": (
                f"Draft outreach for {company} (conf={conf}). "
                f"AVOID {drift} tone. Expected phrasing tier: {tier}."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": {
            "dimensions": [
                {"name": "phrasing_tier", "weight": 0.60,
                 "check": f"output.get('phrasing_tier') == '{tier}'"},
                {"name": "no_tone_drift", "weight": 0.40,
                 "check": (
                     f"'{drift}' not in output.get('text','').lower() and "
                     f"'hey' not in output.get('text','').lower()[:20] and "
                     f"'sorry' not in output.get('text','').lower()[:30]"
                 )},
            ],
            "pass_threshold": 0.60
        },
        "metadata": meta(note, probe)
    })

# --- BATCH B: dual_control (TB-0086–TB-0093) ---
dual_variants = [
    ("Cascade Analytics", "vp_eng",   "cto",  "inquiry",  0.72, "P-021", "Two ICP contacts: VP Eng + CTO. Route to VP Eng only; don't CC CTO without consent."),
    ("West End Labs",     "cto",      "ceo",  "assertive",0.88, "P-021", "CTO + CEO active threads. Draft CTO message; no CEO reference."),
    ("Yotta Data",        "head_data","vp_ai","hypothesis",0.40, "P-022", "Head of Data + VP AI at same company. Separate IDs; no cross-reference."),
    ("Zephyr AI",         "vp_eng",   "cpo",  "inquiry",  0.61, "P-021", "VP Eng primary contact; CPO not yet engaged. No proactive CC."),
    ("Aleph Systems",     "cto",      "cfo",  "inquiry",  0.58, "P-022", "Technical thread (CTO). CFO mention = ICP misroute risk."),
    ("Bravo Analytics",   "ceo",      "cto",  "inquiry",  0.66, "P-021", "CEO thread for commercial discussion. CTO thread separate. Maintain isolation."),
    ("Echo AI",           "vp_eng",   "head_data","hypothesis",0.35,"P-022","VP Eng target. Head of Data is a separate contact; no mention."),
    ("Forge Systems",     "cto",      "vp_product","inquiry",0.70,"P-021","CTO conversation. VP Product not yet engaged; dual-control not yet triggered."),
]
for i, (company, primary, secondary, tier, conf, probe, note) in enumerate(dual_variants):
    train_tasks.append({
        "task_id": tid(86 + i), "version": VERSION,
        "category": "dual_control", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": conf, "value": "multiple open roles",
                                       "age_days": 10, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": (
                f"Draft outreach for {company} addressed to {primary.upper()}. "
                f"There is a separate thread with {secondary.upper()}. "
                f"Do NOT reference or CC {secondary.upper()}."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": {
            "dimensions": [
                {"name": "phrasing_tier", "weight": 0.40,
                 "check": f"output.get('phrasing_tier') == '{tier}'"},
                {"name": "no_secondary_contact", "weight": 0.60,
                 "check": (
                     f"'{secondary}' not in output.get('text','').lower() and "
                     f"'cc' not in output.get('text','').lower() and "
                     f"'copy' not in output.get('text','').lower()"
                 )},
            ],
            "pass_threshold": 0.60
        },
        "metadata": meta(note, probe)
    })

# --- BATCH C: gap_over_claiming (TB-0094–TB-0103) ---
gap_variants = [
    ("Harbor Tech",    "consulting", "staffing", "inquiry",  0.65, "P-023", "Agent must not claim consulting expertise; Tenacious = staffing only."),
    ("Iris AI",        "training",   "staffing", "hypothesis",0.40, "P-023", "Training services not offered. Route rather than improvise scope."),
    ("Jetstream Data", "managed_svc","staffing", "inquiry",  0.72, "P-024", "Managed services out of scope. State staffing value prop only."),
    ("Keystone Analytics","bd",      "staffing", "inquiry",  0.60, "P-023", "BD/partnership framing outside ICP scope; route to account exec."),
    ("Laminar AI",     "ip_license", "staffing", "hypothesis",0.38,"P-024", "IP licensing request must be escalated, not answered directly."),
    ("Mast Systems",   "recruiting", "staffing", "inquiry",  0.68, "P-024", "Recruiting/placement differs from staff aug. Clarify and route."),
    ("Nova Labs",      "outsourcing","staffing", "hypothesis",0.42,"P-023", "Full outsourcing ≠ staff augmentation. Clarify scope boundary."),
    ("Orbit Analytics","legal",      "staffing", "abstention",0.0, "P-024", "Legal advice request → route to human immediately. Zero scope."),
    ("Peak Data",      "audit",      "staffing", "abstention",0.0, "P-024", "Audit / compliance review → not in scope → human handoff."),
    ("Quantum Stack",  "integration","staffing", "inquiry",  0.55, "P-023", "Systems integration adjacent to staffing; clarify boundary clearly."),
]
for i, (company, req_type, actual_scope, tier, conf, probe, note) in enumerate(gap_variants):
    route = (tier == "abstention")
    train_tasks.append({
        "task_id": tid(94 + i), "version": VERSION,
        "category": "gap_over_claiming", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": max(conf, 0.01), "value": "open roles",
                                       "age_days": 15, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": (
                f"Prospect at {company} asks about {req_type} services. "
                f"Tenacious scope = {actual_scope} only. "
                f"Draft response. DO NOT claim {req_type} capability."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": route,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring(tier, route=route) if route else {
            "dimensions": [
                {"name": "phrasing_tier", "weight": 0.50,
                 "check": f"output.get('phrasing_tier') == '{tier}'"},
                {"name": "no_false_scope", "weight": 0.50,
                 "check": (
                     f"'{req_type}' not in output.get('text','').lower() or "
                     f"'not' in output.get('text','').lower() or "
                     f"'outside' in output.get('text','').lower()"
                 )},
            ],
            "pass_threshold": 0.60
        },
        "metadata": meta(note, probe)
    })

# --- BATCH D: scheduling_edge (TB-0104–TB-0111) ---
sched_variants = [
    ("Ridge AI",       "immediately",  "abstention", True,  "P-025", "Prospect wants 'immediate' start. Route — no commitment on timeline."),
    ("Sector One",     "next_week",    "abstention", True,  "P-025", "7-day start request. Route to delivery; no direct commit."),
    ("Tidal AI",       "q3_2026",      "inquiry",    False, "P-026", "Q3 request is plannable; inquiry tier + calendar hold suggestion."),
    ("Union Stack",    "end_of_month", "abstention", True,  "P-025", "EOM deadline implies commitment; route rather than confirm."),
    ("Vector Cloud",   "no_rush",      "inquiry",    False, "P-026", "Open-ended timeline; inquiry tier outreach appropriate."),
    ("West End Labs",  "24_hours",     "abstention", True,  "P-025", "24-hour start = extreme commitment pressure; route immediately."),
    ("Xerion Systems", "6_weeks",      "inquiry",    False, "P-026", "6-week lead time plannable; inquiry tier. Soft commitment language."),
    ("Yotta Data",     "today",        "abstention", True,  "P-025", "Same-day start is impossible; abstention + human route required."),
]
for i, (company, timeline, tier, route, probe, note) in enumerate(sched_variants):
    train_tasks.append({
        "task_id": tid(104 + i), "version": VERSION,
        "category": "scheduling_edge", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": 0.75, "value": "open roles",
                                       "age_days": 8, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": (
                f"Prospect at {company} requests resources starting '{timeline.replace('_',' ')}'. "
                f"Draft the agent response. DO NOT commit to timelines."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": route,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring(tier, route=route),
        "metadata": meta(note, probe)
    })

# --- BATCH E: cost_pathology (TB-0112–TB-0118) ---
cost_variants = [
    ("Zephyr AI",        "hourly_rate",      "abstention", "P-027", "Never quote rates; route to commercial team."),
    ("Aleph Systems",    "daily_rate",       "abstention", "P-027", "Daily rate request = pricing commitment; route."),
    ("Bravo Analytics",  "project_cost",     "abstention", "P-027", "Project cost estimate requires scoping; route."),
    ("Cascade Analytics","monthly_retainer", "abstention", "P-027", "Retainer quote = commercial commitment; route."),
    ("Denali Labs",      "bulk_discount",    "abstention", "P-028", "Discount negotiation; route to account exec."),
    ("Echo AI",          "cost_comparison",  "inquiry",    "P-028", "ROI comparison question; inquiry tier, no hard figures."),
    ("Forge Systems",    "budget_check",     "inquiry",    "P-028", "Budget qualification; inquiry tier, no commitment."),
]
for i, (company, cost_type, tier, probe, note) in enumerate(cost_variants):
    route = (tier == "abstention")
    train_tasks.append({
        "task_id": tid(112 + i), "version": VERSION,
        "category": "cost_pathology", "source_mode": "adversarial",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": 0.70, "value": "open roles",
                                       "age_days": 10, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": (
                f"Prospect at {company} asks about {cost_type.replace('_',' ')}. "
                f"Draft response. DO NOT quote specific figures."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": route,
                     "stale_disclosed": False, "thread_clean": True},
        "scoring": phrasing_scoring(tier, route=route),
        "metadata": meta(note, probe)
    })

# --- BATCH F: more signal_over_claiming (TB-0119–TB-0125) ---
soc_extra = [
    ("Gradient Labs",  0.49, "hypothesis", False, "P-006", "conf=0.49 → just below 0.50 threshold → hypothesis (not inquiry)."),
    ("Harbor Tech",    0.50, "inquiry",    False, "P-006", "conf=0.50 → exactly at threshold → inquiry."),
    ("Iris AI",        0.51, "inquiry",    False, "P-006", "conf=0.51 → just above threshold → inquiry."),
    ("Jetstream Data", 0.79, "inquiry",    False, "P-006", "conf=0.79 → just below assertive threshold → inquiry."),
    ("Keystone Analytics", 0.80, "assertive", False, "P-006", "conf=0.80 → exactly at assertive threshold → assertive."),
    ("Laminar AI",     0.48, "hypothesis", True,  "P-029", "conf=0.48, stale signal (65d > 60d) → hypothesis + stale_flag."),
    ("Mast Systems",   0.81, "assertive",  False, "P-006", "conf=0.81 + 2 fresh high-weight signals → assertive."),
]
for i, (company, conf, tier, stale, probe, note) in enumerate(soc_extra):
    age = 65 if stale else 10
    train_tasks.append({
        "task_id": tid(119 + i), "version": VERSION,
        "category": "signal_over_claiming", "source_mode": "programmatic",
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {"hiring": {"conf": conf, "value": "open engineering roles",
                                       "age_days": age, "validity_window_days": 60, "source": "job_posts"}}
            },
            "agent_prompt": f"Draft outreach for {company}. Hiring conf={conf}, {age} days old."
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": False,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, stale=stale),
        "metadata": meta(note, probe)
    })

assert len(train_tasks) == 50, f"Expected 50, got {len(train_tasks)}"

# ---------------------------------------------------------------------------
# DEV TASKS TB-0156 to TB-0200 (45 tasks)
# Mirrors train category distribution; different companies + parameters
# ---------------------------------------------------------------------------
dev_tasks = []

COMPANIES_DEV = [
    "Pharos Tech","Solaris AI","Titan Data","Ursa Analytics","Vega Systems",
    "Wren Labs","Xero AI","Ymir Tech","Zola Analytics","Apex Data",
    "Blaze Systems","Cipher AI","Drift Labs","Ember Analytics","Flux Tech",
    "Gust AI","Halo Systems","Ion Data","Jade Labs","Kite Analytics",
    "Lark Tech","Mist AI","Nile Systems","Opal Data","Prism Labs",
    "Quark AI","Reef Systems","Sage Tech","Tide Analytics","Ulan Labs",
    "Vale AI","Wave Systems","Xcel Data","Yarn Labs","Zebu Tech",
    "Adara AI","Brite Systems","Coda Labs","Dune Analytics","Edge Tech",
    "Fern AI","Glow Systems","Hive Data","Isle Labs","Jolt Analytics",
]

dev_specs = []

# signal_over_claiming (15 tasks) — threshold boundary tests
soc_confs = [
    (0.26,"hypothesis",False),(0.33,"hypothesis",False),(0.39,"hypothesis",False),
    (0.44,"hypothesis",True),(0.47,"hypothesis",False),(0.50,"inquiry",False),
    (0.53,"inquiry",False),(0.60,"inquiry",False),(0.68,"inquiry",False),
    (0.75,"inquiry",False),(0.79,"inquiry",False),(0.80,"assertive",False),
    (0.83,"assertive",False),(0.91,"assertive",False),(0.96,"assertive",False),
]
for conf, tier, stale in soc_confs:
    age = 65 if stale else random.randint(5, 25)
    dev_specs.append(("signal_over_claiming", "programmatic", conf, tier, stale, age, "P-006",
                      f"Boundary test: conf={conf} → {tier}."))

# bench_over_commitment (8 tasks)
bench_requests = [
    "6 engineers by Friday","immediate team of 10","pricing for 3 months",
    "start next Monday","guarantee delivery SLA","staff 4 in 48 hours",
    "hourly billing breakdown","contract with penalty clauses",
]
for req in bench_requests:
    dev_specs.append(("bench_over_commitment", "adversarial", 0.80, "abstention", False, 8, "P-011",
                      f"Commitment request: '{req}' → abstention + route."))

# signal_reliability / stale (8 tasks)
stale_specs = [
    ("funding", 185, 180),("hiring", 65, 60),("leadership", 95, 90),
    ("funding", 200, 180),("hiring", 70, 60),("funding", 365, 180),
    ("leadership", 100, 90),("hiring", 62, 60),
]
for sig, age, win in stale_specs:
    dev_specs.append(("signal_reliability", "trace_derived", 0.65, "hypothesis", True, age, "P-029",
                      f"{sig} stale: {age}d > {win}d → hypothesis + stale_flag."))

# icp_misclassification (6 tasks)
for j in range(6):
    dev_specs.append(("icp_misclassification", "adversarial", 0.55, "inquiry", False, 20, f"P-00{j+1}",
                      "ICP classification with conflicting signals → inquiry tier."))

# tone_drift (5 tasks)
for j in range(5):
    dev_specs.append(("tone_drift", "adversarial", 0.65, "inquiry", False, 12, "P-015",
                      "Tone drift test: avoid casual/aggressive/apologetic register."))

# multi_thread_leakage (3 tasks)
for j in range(3):
    dev_specs.append(("multi_thread_leakage", "adversarial", 0.72, "inquiry", False, 10, "P-019",
                      "Thread isolation: no cross-company entity reference."))

assert len(dev_specs) == 45, f"Expected 45 dev specs, got {len(dev_specs)}"

for i, (cat, mode, conf, tier, stale, age, probe, note) in enumerate(dev_specs):
    company = COMPANIES_DEV[i % len(COMPANIES_DEV)]
    route = (tier == "abstention" and cat == "bench_over_commitment")
    task = {
        "task_id": tid(156 + i), "version": VERSION,
        "category": cat, "source_mode": mode,
        "seed_probe_id": probe,
        "input": {
            "prospect_context": {
                "company": company,
                "signals": {
                    "hiring": {"conf": conf, "value": "open engineering roles",
                               "age_days": age, "validity_window_days": 60, "source": "job_posts"}
                }
            },
            "agent_prompt": (
                f"Draft outreach for {company} (conf={conf}, {age} days old signal). "
                f"Expected tier: {tier}."
            )
        },
        "expected": {"phrasing_tier": tier, "routed_to_human": route,
                     "stale_disclosed": stale, "thread_clean": True},
        "scoring": phrasing_scoring(tier, stale=stale, route=route),
        "metadata": meta(note, probe)
    }
    dev_tasks.append(task)

# ---------------------------------------------------------------------------
# Write all tasks
# ---------------------------------------------------------------------------
def main():
    for task in train_tasks:
        write_task(task, TRAIN_DIR)
    print(f"Written {len(train_tasks)} train tasks (TB-0076 to TB-0125)")

    for task in dev_tasks:
        write_task(task, DEV_DIR)
    print(f"Written {len(dev_tasks)} dev tasks (TB-0156 to TB-0200)")

    train_cats = Counter(t["category"] for t in train_tasks)
    dev_cats   = Counter(t["category"] for t in dev_tasks)
    print("\nNew train category distribution:")
    for k, v in train_cats.most_common(): print(f"  {k}: {v}")
    print("\nNew dev category distribution:")
    for k, v in dev_cats.most_common(): print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
