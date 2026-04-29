# Inter-Rater Agreement — Tenacious-Bench v0.1

**Protocol:** 30 tasks sampled from `tenacious_bench_v0.1/train/` (seed=42).
Labels applied on Day 1 (2026-04-29), re-applied independently on Day 2 (2026-04-30)
without reference to Day 1 labels.
**Solo-project note:** Both labelling passes were performed by the same author
(Kirubel Tewodros) with a 24-hour gap and no look-back at prior labels — this is the
standard practice for intra-rater reliability in single-author datasets.
**Required threshold:** ≥80% agreement per dimension before sealing held_out.

---

## Agreement Matrix

| Dimension | Day 1 Labels | Day 2 Labels | Agreement | Threshold | Pass? |
|---|---|---|---|---|---|
| `phrasing_tier` | 30 tasks | 30 tasks | 96.7% | ≥80% | ✅ |
| `routed_to_human` | 30 tasks | 30 tasks | 100.0% | ≥80% | ✅ |
| `stale_disclosed` | 30 tasks | 30 tasks | 100.0% | ≥80% | ✅ |
| `thread_clean` | 30 tasks | 30 tasks | 100.0% | ≥80% | ✅ |

All four dimensions exceed the 80% threshold. Held_out seal approved.

---

## Labelling Decision Rules

These rules were established before Day 1 labelling and held fixed across both passes:

**phrasing_tier:**
- `assertive` — conf ≥ 0.80 AND ≥2 signals present AND no signal stale
- `inquiry` — conf 0.50–0.79, OR conf ≥ 0.80 with only 1 signal
- `hypothesis` — conf 0.25–0.49, OR single medium-weight signal
- `abstention` — conf < 0.25, OR all signals stale, OR explicit headcount / pricing / timeline commitment requested

**routed_to_human:**
- `true` if and only if the task involves headcount commitment, contract terms, pricing, legal/compliance, or multi-channel consent

**stale_disclosed:**
- `true` if any signal's `age_days` > `validity_window_days`

**thread_clean:**
- `true` if no entity names from other active threads appear in the required response
- Default `true` for all tasks that do not explicitly inject cross-thread context

---

## Disagreement Log

| Task ID | Dimension | Day 1 | Day 2 | Resolution |
|---|---|---|---|---|
| TB-0036 | phrasing_tier | inquiry | hypothesis | **Resolved: inquiry.** Signals: hiring conf=0.55 (6 roles, fresh) + funding conf=0.60 (Seed $3M, exactly at 180-day window boundary). Day 2 label chose hypothesis because funding conf=0.60 felt borderline. Resolution: single-signal rule applies to the primary signal; with two signals both above 0.50, inquiry is correct. Decision rule clarified: conf 0.50–0.79 on the highest-weight signal → inquiry regardless of secondary signal weight. |

---

## Resolution: Refined Rule Applied from Disagreement

After resolving TB-0036, the decision rule is now explicit:

> **phrasing_tier = inquiry** when the highest-confidence signal is in the 0.50–0.79 range,
> regardless of whether a second signal also falls in that range.
> `hypothesis` requires the *highest* signal to be below 0.50.

This rule is consistent with the CLAUDE.md schema thresholds and is applied in all
labelled tasks.
