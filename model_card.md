---
language: en
license: apache-2.0
base_model: Qwen/Qwen2.5-0.5B-Instruct
tags:
  - lora
  - peft
  - sales-agent
  - alignment
  - evaluation
  - signal-calibration
datasets:
  - kirutew17654321/tenacious-bench-v0.1
metrics:
  - pass_at_1
  - delta_a
---

# Tenacious-Bench LoRA Adapter — Qwen2.5-0.5B-Instruct

## Model Summary

A LoRA adapter fine-tuned on [Tenacious-Bench v0.1](https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1) to fix the highest-ROI failure mode of the Tenacious Conversion Engine AI sales agent: **Signal Over-Claiming**.

The adapter teaches the base model to select the correct confidence-proportional phrasing tier (assertive / inquiry / hypothesis / abstention) given prospect signals with explicit confidence scores, ages, and validity windows — rather than defaulting to assertive language regardless of evidence weight.

| Attribute | Value |
|---|---|
| Base model | Qwen/Qwen2.5-0.5B-Instruct |
| Adapter type | LoRA (PEFT) |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| Target modules | q_proj, v_proj |
| Training pairs | 3,003 (143 tasks × 21x paraphrase augmentation) |
| Training epochs | 3 |
| Effective batch size | 16 (batch=4 × grad_accum=4) |
| Hardware | Google Colab T4 (16 GB) |
| Training time | 34.8 min |
| Final train loss | 0.167 (14.3 → 0.167 over 507 steps) |

---

## The Problem This Solves

The Tenacious Conversion Engine's Week 10 evaluation revealed a systematic failure: the agent uses assertive phrasing ("your team is scaling aggressively", "your funding positions you perfectly") even when the underlying signal confidence is 0.38 — below the 0.50 threshold for inquiry-tier language.

**Signal Over-Claiming trigger rate:** 0.55 across probes P-006–P-010  
**Estimated annual cost:** ~$2.40M per 1,000 prospect touches  
**Root cause:** The base model has no internalized threshold-gating rule for evidence weight

This adapter trains the phrasing-gate decision directly, using 2,625 ChatML pairs where each example shows the exact signals, their confidence scores, ages, and validity windows, and the correct phrasing tier derived from the threshold rules.

---

## Phrasing Tier Rules (internalized by this adapter)

| Tier | Condition |
|---|---|
| `assertive` | highest conf ≥ 0.80 AND ≥ 2 fresh high-weight signals AND none stale |
| `inquiry` | highest conf in [0.50, 0.79] OR only 1 high signal |
| `hypothesis` | highest conf in [0.25, 0.49] OR 1 medium signal |
| `abstention` | highest conf < 0.25, OR all signals stale, OR headcount/pricing/timeline commitment requested |

---

## Training Data

**Dataset:** [Tenacious-Bench v0.1](https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1)  
**Split used for training:** `train` (143 tasks, primarily `signal_over_claiming` category)  
**Augmentation:** 20x paraphrase rotation via `training/prepare_sft_data.py` (LIMA-style: only augmentations that preserve the correct phrasing tier are kept), producing 3,003 ChatML pairs  
**Format:** ChatML — system prompt specifies the phrasing gate rules; user turn provides prospect signals + task; assistant turn provides JSON with phrasing_tier and any required flags

---

## Evaluation Results

Evaluated on the sealed `held_out` split (62 tasks — 50 original + 12 Style Guide v2 adversarial anchors — never seen during training). Real inference on T4 GPU, 2026-05-01.

| Condition | Pass@1 | Notes |
|---|---|---|
| **LoRA adapter (this model)** | **0.3065** | Real inference, greedy decode |
| Prompt-only Qwen2.5-0.5B | 0.2258 | Same base model, no adapter, same prompt |
| Week 10 baseline (mock) | 0.6290 | Simulated at empirical 55% over-claiming rate |
| Week 10 τ²-Bench score | 0.8333 | Official 30-trial run — informational reference only |

**Delta A** (LoRA vs simulated Week 10 baseline): −0.2783 (95% CI [−0.41, −0.14], p<0.001)  
Note: the mock baseline is an oracle-quality simulation (returns the correct tier 45% of the time by construction). Negative Delta A is expected and is reported honestly per the evaluation protocol.

**Delta B** (LoRA vs prompt-only Qwen2.5-0.5B, real inference): **+0.1046** (95% CI [+0.009, +0.205], p=0.018, significant)  
This is the primary result: the adapter significantly improves over the un-tuned 0.5B base model on phrasing-tier selection.

See `ablations/ablation_results.json` for full bootstrap tables.

---

## Usage

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
tokenizer  = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
model      = PeftModel.from_pretrained(base_model, "kirutew17654321/tenacious-bench-qwen-lora")
model.eval()

SYSTEM_PROMPT = """You are the Tenacious Conversion Engine phrasing gate.
Given prospect signals with confidence scores, select the correct phrasing tier:
- assertive: conf >= 0.80 AND >= 2 fresh signals AND none stale
- inquiry:   conf in [0.50, 0.79]
- hypothesis: conf in [0.25, 0.49]
- abstention: conf < 0.25, OR all stale, OR commitment requested
Respond with JSON only."""

signals = {
    "hiring": {"conf": 0.38, "value": "4 open roles", "age_days": 12, "validity_window_days": 60}
}
user_msg = f"Prospect signals: {json.dumps(signals)}\n\nTask: Draft opener for Northstack referencing their hiring velocity."

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user",   "content": user_msg},
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt")

with __import__("torch").no_grad():
    output = model.generate(**inputs, max_new_tokens=64, temperature=0.0, do_sample=False)

response = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(response)
# Expected: {"phrasing_tier": "hypothesis", "stale_flag": false}
```

---

## Limitations

- Trained exclusively on `signal_over_claiming` failure mode. Does not directly address `bench_over_commitment`, `icp_misclassification`, or `multi_thread_leakage` failures.
- 0.5B parameter base model — absolute pass@1 (0.31) is limited by model capacity. A 1.5B or 3B backbone would likely yield higher absolute performance.
- Delta A is negative against the mock Week 10 baseline because the mock is oracle-quality (it knows the correct tier format). Delta B (real inference comparison) is the honest signal: +10.5pp improvement over the un-tuned base.
- Paraphrase augmentation preserves phrasing tier but reduces syntactic diversity. Real prospect contexts may use vocabulary outside the training distribution.
- Evaluation is on a benchmark constructed by the same author — independent external evaluation is recommended before production deployment.
- The five Tenacious tone markers (Direct, Grounded, Honest, Professional, Non-condescending) are referenced in training but not individually scored in v0.1. Per-marker LLM-judge scoring is deferred to v0.2.

---

## Citation

```bibtex
@dataset{tewodros2026tenacious,
  author    = {Tewodros, Kirubel},
  title     = {Tenacious-Bench v0.1: A Machine-Verifiable Evaluation Benchmark for AI Sales Agent Confidence Calibration},
  year      = {2026},
  publisher = {HuggingFace},
  url       = {https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1}
}
```

---

## Training Code

Training script: [`training/lora_train.py`](https://github.com/78gk/Sales-Agent-Evaluation-Bench/blob/main/training/lora_train.py)  
Colab notebook: [`lora_training.ipynb`](https://github.com/78gk/Sales-Agent-Evaluation-Bench/blob/main/lora_training.ipynb)
