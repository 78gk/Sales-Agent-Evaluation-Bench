# Tenacious-Bench v0.1
## A production-grade evaluation + alignment project for AI outbound sales agents

**Author:** Kirubel Tewodros  
**Repository:** [78gk/Sales-Agent-Evaluation-Bench](https://github.com/78gk/Sales-Agent-Evaluation-Bench)

---

## Why this project matters (real-world value)

Most AI sales agents are evaluated on task completion only (did it call the right tool?) and miss the highest-cost failure: **overconfident language on weak signals**.

Tenacious-Bench v0.1 was built to close that gap with machine-verifiable scoring and targeted LoRA alignment.

- **Target risk:** Signal Over-Claiming (trigger rate **0.55**)
- **Business impact:** estimated **~$2.40M annual pipeline risk per 1,000 touches**
- **Outcome:** LoRA adapter improves held-out pass@1 by **+0.1046** vs prompt-only baseline (**p=0.018**)

---

## Executive snapshot

| Area | Delivered |
|---|---|
| Benchmark | **260-task** dataset (train=143, dev=55, held_out=62) |
| Evaluation | Deterministic scorer (`scoring_evaluator.py`) with weighted rubric |
| Alignment | LoRA fine-tune on Qwen2.5-0.5B-Instruct |
| Training corpus | 3,003 SFT pairs |
| Validation | 0 n-gram contamination overlap across splits |
| Result | **Delta B +0.1046** on held_out |

---

## What recruiters and hiring teams can verify here

This repo demonstrates end-to-end applied LLM engineering:

- **Evaluation design:** translated product risk into measurable, testable benchmark tasks
- **Data engineering:** schema-first task generation, split discipline, contamination controls
- **Model alignment:** LoRA training pipeline for targeted behavioral correction
- **Experimentation rigor:** ablations, bootstrap confidence intervals, significance testing
- **Documentation maturity:** datasheet, methodology, evidence graph, model card, cost ledger
- **Shipping discipline:** public dataset + adapter + reproducible scripts + community write-up

---

## Core problem covered by the benchmark

Tenacious-Bench focuses on failure modes underrepresented in generic agent benchmarks:

1. **Signal Over-Claiming** (P-006–P-010)
2. **Bench Over-Commitment** (P-011)
3. **Thread Isolation Failure** (P-019)

Primary training objective in v0.1: confidence-proportional phrasing for Signal Over-Claiming.

---

## Quickstart

### 1) Environment setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Validate schema + scorer

```bash
python scoring_evaluator.py --validate
# Expected: 3x OK + 3x PASS
```

### 3) Score a single task

```bash
python scoring_evaluator.py \
  --task tenacious_bench_v0.1/train/TB-0001.json \
  --output agent_output.json
```

### 4) Batch score a split

```bash
python scoring_evaluator.py \
  --batch tenacious_bench_v0.1/dev/ \
  --outputs outputs/dev_responses/
```

---

## Reproduce the headline result (Delta B)

```bash
# 1) Install dependencies
pip install -r requirements.txt

# 2) Pull LoRA adapter
python -c "from huggingface_hub import snapshot_download; snapshot_download('kirutew17654321/tenacious-bench-qwen-lora', local_dir='training/checkpoint')"

# 3) Run ablation on held_out
python training/run_ablation.py \
  --held-out tenacious_bench_v0.1/held_out \
  --adapter training/checkpoint \
  --model qwen2.5-0.5b-instruct \
  --output ablations/ablation_results.json
```

Published benchmark number:
- **LoRA pass@1:** 0.3065
- **Prompt-only pass@1:** 0.2258
- **Delta B:** **+0.1046** (p=0.018)

---

## Public artifacts

- **Dataset:** [kirutew17654321/tenacious-bench-v0.1](https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1)
- **LoRA Adapter:** [kirutew17654321/tenacious-bench-qwen-lora](https://huggingface.co/kirutew17654321/tenacious-bench-qwen-lora)
- **Model Card:** [`model_card.md`](./model_card.md)
- **Methodology:** [`methodology.md`](./methodology.md)
- **Audit Memo:** [`audit_memo.md`](./audit_memo.md)
- **Evidence Graph:** [`evidence_graph.json`](./evidence_graph.json)
- **Cost Log:** [`cost_log.md`](./cost_log.md)

---

## Repository layout

```text
tenacious_bench_v0.1/      # dataset splits
generation_scripts/         # synthesis + dedup pipeline
training/                   # SFT prep, LoRA training, ablation
seeds/                      # week-10 traces, probe library, taxonomy
ablations/                  # experiment outputs
synthesis_memos/            # literature synthesis
```

---

## Tech stack

- Python, JSON schema validation
- Transformers, PEFT, TRL, Datasets
- OpenRouter-based data synthesis pipeline
- Hugging Face Hub (dataset + adapter publishing)

---

## License

- **Code:** [Apache 2.0](./LICENSE)
- **Dataset:** CC-BY-4.0
- **Adapter:** Apache 2.0

---

## Contact

**Kirubel Tewodros**  
GitHub: [@78gk](https://github.com/78gk)
