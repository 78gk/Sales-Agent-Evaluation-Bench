# Cost Log — Tenacious-Bench v0.1

**Hard cap: $10.00**  
**Rule: No τ²-Bench retail re-runs. No eval-tier model on Days 2–3.**

| Date | Day | Activity | Model | Tokens / Units | Cost ($) | Running Total ($) |
|---|---|---|---|---|---|---|
| 2026-04-29 | 0 | Repo setup, schema design, 3 example tasks | — | — | 0.00 | 0.00 |

---

## Budget Allocation

| Category | Budget | Spent | Remaining |
|---|---|---|---|
| Dataset authoring (dev-tier LLM) | $3–5 | $0.00 | — |
| Training (Colab T4 or RunPod) | $0–5 | $0.00 | — |
| Held-out eval (eval-tier, 3–4 passes max) | $2–3 | $0.00 | — |
| Reserve | $1–2 | $0.00 | — |
| **Total** | **$10.00** | **$0.00** | **$10.00** |

---

## Model Tiers

| Tier | Models | When allowed |
|---|---|---|
| Dev-tier | Qwen3-80B, DeepSeek V3.2 (via OpenRouter) | Days 1–5 for generation + dev judging |
| Eval-tier | Claude Sonnet 4.6 or GPT-5 class (OpenRouter) | Days 4–5 only, sealed held_out scoring |
| Training | Qwen 3.5 0.8B/2B/4B via Unsloth on T4 | Days 3–4 |

---

## Notes

- Log every API call that costs money within 24 hours of making it
- Wasteful re-runs are a graded artifact — document any re-run and why it was necessary
- If running over $8 before training: stop synthesis generation, complete with hand-authored tasks
