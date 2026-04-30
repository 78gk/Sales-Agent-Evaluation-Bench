# Cost Log — Tenacious-Bench v0.1

**Hard cap: $10.00**  
**Rule: No τ²-Bench retail re-runs. No eval-tier model before Day 4.**

| Date | Day | Activity | Model | Notes | Cost ($) | Running Total ($) |
|---|---|---|---|---|---|---|
| 2026-04-29 | 1 | Repo setup, schema design, 3 example tasks | — | Zero-cost local work | 0.00 | 0.00 |
| 2026-04-29 | 1–2 | Trace-derived + adversarial task authoring (75 train, 30 dev) | — | Zero-cost local work | 0.00 | 0.00 |
| 2026-04-30 | 3 | Held-out task sealing, contamination checks, inter-rater labelling | — | Zero-cost local work | 0.00 | 0.00 |
| 2026-04-30 | 4 | SFT data prep, LoRA train script, ablation dry-run, 8 synthesis memos | — | Zero-cost local work | 0.00 | 0.00 |
| 2026-05-01 | 5 | Synthesis generation: 125 train tasks (incl. smoke test 2) via OpenRouter | Qwen/Qwen3-235b-a22b (generator), DeepSeek/deepseek-chat-v3-0324 (judge) | ~90 admitted + ~180 rejected candidates; actual balance draw confirmed $6.46 | 6.46 | 6.46 |
| 2026-05-01 | 5 | Synthesis generation: 45 dev tasks (categorically diverse) via OpenRouter | Qwen/Qwen3-235b-a22b (generator), DeepSeek/deepseek-chat-v3-0324 (judge) | Est. ~$0.50–1.00; running | ~0.75 | ~7.21 |

---

## Budget Summary (Day 5)

| Category | Budget | Spent | Remaining |
|---|---|---|---|
| Dataset synthesis (dev-tier LLM, OpenRouter) | $3–5 | ~$7.21 | ~$2.79 |
| Training (Colab T4) | $0 | $0.00 | — |
| Held-out eval / calibration (eval-tier) | $2–3 | $0.00 | ~$2.79 reserved |
| **Total** | **$10.00** | **~$7.21** | **~$2.79** |

**Status:** Within cap. Remaining $2.79 allocated to eval-tier calibration slice (Day 6, if needed).

---

## Model Tiers

| Tier | Models | When allowed |
|---|---|---|
| Dev-tier | Qwen/Qwen3-235b-a22b, DeepSeek/deepseek-chat-v3-0324 (via OpenRouter) | Days 1–5 for generation + judging |
| Eval-tier | anthropic/claude-sonnet-4-6 (via OpenRouter) | Days 4–6 only, calibration slice ≤4 passes |
| Training | Qwen2.5-0.5B-Instruct via Unsloth on T4 | Day 5 (Colab, zero marginal cost) |

---

## Notes

- All synthesis API calls routed through OpenRouter. Generator ≠ judge enforced by assertion in `synthesis_generator.py`.
- Colab T4 training is free tier — no cost logged.
- If running over $9.00 before Day 6 calibration: skip eval-tier and use dev-tier judge for calibration slice.
- Log every API call within 24 hours of making it.
