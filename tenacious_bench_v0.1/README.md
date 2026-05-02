---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-classification
  - question-answering
tags:
  - evaluation
  - sales-agent
  - signal-calibration
  - lora
  - alignment
pretty_name: Tenacious-Bench v0.1
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: dev
        path: dev.jsonl
      - split: held_out
        path: held_out.jsonl
---

# Tenacious-Bench v0.1

**260-task, machine-verifiable evaluation benchmark** for the Tenacious Conversion Engine AI outbound sales agent.
Purpose-built to measure the failure modes that τ²-Bench cannot grade: confidence-calibrated phrasing, staleness disclosure, abstention routing, and thread isolation.

| Split | Tasks | Use |
|---|---|---|
| train | 143 | LoRA fine-tuning corpus |
| dev | 55 | Validation / prompt iteration |
| held_out | 62 | Released post-training for independent Delta B verification |

## Task schema

Each record contains:
- `task_id` — unique ID (TB-0001 … TB-G024)
- `category` — failure mode (e.g. `signal_over_claiming`)
- `source_mode` — `trace_derived`, `programmatic`, `synthesis`, or `adversarial`
- `input.prospect_context` — company signals with confidence scores and ages
- `input.agent_prompt` — the task the agent must complete
- `expected` — ground-truth `phrasing_tier`, `routed_to_human`, `stale_disclosed`
- `scoring` — weighted dimensions and pass threshold

## Evaluation

```python
# pip install -r requirements.txt
python scoring_evaluator.py --validate
python scoring_evaluator.py --task tenacious_bench_v0.1/train/TB-0001.json --output agent_out.json
```

## LoRA Adapter

Trained on the `train` split (3,003 SFT pairs, 143 tasks × 21x augmentation).
**Delta B: +0.1046 (p=0.018)** vs prompt-only Qwen2.5-0.5B on sealed held-out.

- Adapter: [kirutew17654321/tenacious-bench-qwen-lora](https://huggingface.co/kirutew17654321/tenacious-bench-qwen-lora)
- Code: [github.com/78gk/Sales-Agent-Evaluation-Bench](https://github.com/78gk/Sales-Agent-Evaluation-Bench)

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

License: CC-BY-4.0
