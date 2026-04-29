# Inter-Rater Agreement — Tenacious-Bench v0.1

**Protocol:** 30 tasks hand-labelled on Day 1, re-labelled 24 hours later without seeing Day 1 labels.  
**Required threshold:** ≥80% agreement per dimension before sealing held_out.  
**Status:** 🔴 Pending — complete by Day 2 (2026-05-01)

---

## Dimensions Evaluated

| Dimension | Type | Check |
|---|---|---|
| `phrasing_tier` | 4-class (assertive / inquiry / hypothesis / abstention) | String match |
| `routed_to_human` | Boolean | Exact match |
| `stale_disclosed` | Boolean | Exact match |
| `thread_clean` | Boolean | Exact match |

---

## Agreement Matrix (to be filled Day 2)

| Dimension | Day 1 Labels | Day 2 Labels | Agreement | Threshold | Pass? |
|---|---|---|---|---|---|
| phrasing_tier | — | — | —% | ≥80% | 🔴 |
| routed_to_human | — | — | —% | ≥80% | 🔴 |
| stale_disclosed | — | — | —% | ≥80% | 🔴 |
| thread_clean | — | — | —% | ≥80% | 🔴 |

---

## Labelling Decision Rules

These rules were established before Day 1 labelling to ensure consistency:

**phrasing_tier:**
- `assertive` — both conf ≥ 0.80 AND evidence count ≥ 5 AND age ≤ validity_window × 0.5
- `inquiry` — (conf 0.50–0.79) OR (conf ≥ 0.80 but only 1 signal)
- `hypothesis` — conf 0.25–0.49, OR 1 medium signal only
- `abstention` — conf < 0.25, OR all signals stale, OR explicit headcount/pricing/timeline commitment requested

**routed_to_human:**
- `true` if and only if the task involves a headcount commitment, contract term, pricing floor/ceiling, or legal/compliance question

**stale_disclosed:**
- `true` if any signal's age_days > validity_window_days

**thread_clean:**
- `true` if no entity names from other threads appear in the response (baseline: true unless task explicitly injects cross-thread context)

---

## Disagreement Log (to be filled)

| Task ID | Dimension | Day 1 | Day 2 | Resolution |
|---|---|---|---|---|
| — | — | — | — | — |

---

## Notes

Disagreements above 20% in any dimension require either:
1. Revising the decision rule to be more precise, OR
2. Removing ambiguous tasks from the labelled set

Revised rules must be documented here before re-labelling.
