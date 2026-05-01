"""
lora_train.py — Tenacious-Bench v0.1 LoRA training script.

Uses standard HuggingFace PEFT + TRL (no Unsloth dependency).
Compatible with Colab T4 (16 GB VRAM) at float16.

Usage:
    python training/lora_train.py \
        --pairs training/qwen_pairs.jsonl \
        --model qwen2.5-0.5b-instruct \
        --output training/checkpoint \
        --hub-repo kirutew17654321/tenacious-bench-qwen-lora

Hyperparameters (Path A spec):
    rank=16, alpha=32, target=q_proj+v_proj, dtype=float16
    lr=2e-4, batch=4, grad_accum=4, epochs=3
    Wall-clock budget: 30 minutes on T4
"""

import json
import os
import sys
import time
from pathlib import Path

MODEL_OPTIONS = {
    "qwen2.5-0.5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b-instruct":   "Qwen/Qwen2.5-3B-Instruct",
}
# Pinned HuggingFace revision — ensures reproducibility across HF model updates.
# SHA retrieved 2026-05-02 via model_info("Qwen/Qwen2.5-0.5B-Instruct").sha.
# Training was run on 2026-05-01 against this revision.
MODEL_REVISION = "7ae557604adf67be50417f59c2c2f167def9a775"

LORA_RANK          = 16
LORA_ALPHA         = 32
LORA_TARGET_MODS   = ["q_proj", "v_proj"]
LEARNING_RATE      = 2e-4
BATCH_SIZE         = 4
GRAD_ACCUM         = 4
NUM_EPOCHS         = 3
MAX_SEQ_LENGTH     = 2048
WARMUP_STEPS       = 20
WALL_CLOCK_MINUTES = 30
DEV_SPLIT_RATIO    = 0.1
RANDOM_SEED        = 42


def load_pairs(pairs_path: Path) -> list:
    pairs = []
    with pairs_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


def split_train_dev(pairs: list, dev_ratio: float, seed: int) -> tuple:
    import random
    random.seed(seed)
    groups = {}
    for pair in pairs:
        tid = pair.get("task_id", "unknown")
        groups.setdefault(tid, []).append(pair)
    task_ids = sorted(groups.keys())
    random.shuffle(task_ids)
    dev_count = max(1, int(len(task_ids) * dev_ratio))
    dev_tids = set(task_ids[:dev_count])
    train_tids = set(task_ids[dev_count:])
    train_pairs = [p for tid in train_tids for p in groups[tid]]
    dev_pairs   = [p for tid in dev_tids   for p in groups[tid]]
    return train_pairs, dev_pairs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tenacious-Bench LoRA training")
    parser.add_argument("--pairs",    type=str, default="training/qwen_pairs.jsonl")
    parser.add_argument("--model",    type=str, default="qwen2.5-0.5b-instruct",
                        choices=list(MODEL_OPTIONS.keys()))
    parser.add_argument("--output",   type=str, default="training/checkpoint")
    parser.add_argument("--hub-repo", type=str, default="kirutew17654321/tenacious-bench-qwen-lora")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    pairs_path = Path(args.pairs)
    output_dir = Path(args.output)
    model_id   = MODEL_OPTIONS[args.model]

    if not pairs_path.exists():
        print(f"ERROR: pairs file not found: {pairs_path}", file=sys.stderr)
        sys.exit(1)

    pairs = load_pairs(pairs_path)
    train_pairs, dev_pairs = split_train_dev(pairs, DEV_SPLIT_RATIO, RANDOM_SEED)

    print("=== Tenacious-Bench LoRA Training ===")
    print(f"  Model:          {model_id}")
    print(f"  Train pairs:    {len(train_pairs)}")
    print(f"  Dev pairs:      {len(dev_pairs)}")
    print(f"  LoRA rank:      {LORA_RANK}, alpha={LORA_ALPHA}")
    print(f"  Target modules: {LORA_TARGET_MODS}")
    print(f"  LR:             {LEARNING_RATE}")
    print(f"  Batch:          {BATCH_SIZE} × {GRAD_ACCUM} grad_accum = {BATCH_SIZE * GRAD_ACCUM} eff")
    print(f"  Epochs:         {NUM_EPOCHS}")
    print(f"  Wall-clock cap: {WALL_CLOCK_MINUTES} min")
    print(f"  Output:         {output_dir}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without training.")
        return

    import inspect
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset

    try:
        from trl import SFTTrainer, SFTConfig as _SFTConfig
        _USE_SFT_CONFIG = True
    except ImportError:
        from trl import SFTTrainer
        _SFTConfig = None
        _USE_SFT_CONFIG = False

    print("\nLoading base model...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=MODEL_REVISION, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # transformers >= 4.50 deprecated `torch_dtype` in favor of `dtype`.
    from_pretrained_kwargs = dict(device_map="auto", trust_remote_code=True)
    auto_params = inspect.signature(AutoModelForCausalLM.from_pretrained).parameters
    if "dtype" in auto_params:
        from_pretrained_kwargs["dtype"] = torch.float16
    else:
        from_pretrained_kwargs["torch_dtype"] = torch.float16
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=MODEL_REVISION, **from_pretrained_kwargs)
    model.enable_input_require_grads()

    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=LORA_TARGET_MODS,
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    def format_messages(example):
        text = tokenizer.apply_chat_template(
            example["conversations"],
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}

    train_ds = Dataset.from_list([{"conversations": p["messages"]} for p in train_pairs]).map(format_messages)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Evaluation during training is disabled: the T4's 14.56 GiB VRAM is fully
    # consumed by the 0.5B model + fp16 optimizer states + LoRA activations,
    # leaving insufficient headroom for an eval forward pass. Real evaluation
    # is performed by run_ablation.py on the sealed held_out split after training.
    shared_args = dict(
        output_dir=str(output_dir),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_steps=WARMUP_STEPS,
        fp16=True,
        gradient_checkpointing=True,
        logging_steps=10,
        eval_strategy="no",
        save_strategy="epoch",
        seed=RANDOM_SEED,
        report_to="none",
    )

    def _filter_kwargs(target_cls, kwargs):
        sig = inspect.signature(target_cls.__init__).parameters
        accepted, dropped = {}, []
        for k, v in kwargs.items():
            if k in sig:
                accepted[k] = v
            else:
                dropped.append(k)
        return accepted, dropped

    if _USE_SFT_CONFIG:
        cfg_params = inspect.signature(_SFTConfig.__init__).parameters
        cfg_kwargs = dict(shared_args)
        # `eval_strategy` was renamed in some transformers versions; keep both names available.
        if "eval_strategy" not in cfg_params and "evaluation_strategy" in cfg_params:
            cfg_kwargs["evaluation_strategy"] = cfg_kwargs.pop("eval_strategy")
        # `max_seq_length` (trl <0.21) → `max_length` (trl >=0.21).
        if "max_seq_length" in cfg_params:
            cfg_kwargs["max_seq_length"] = MAX_SEQ_LENGTH
        elif "max_length" in cfg_params:
            cfg_kwargs["max_length"] = MAX_SEQ_LENGTH
        if "dataset_text_field" in cfg_params:
            cfg_kwargs["dataset_text_field"] = "text"
        cfg_kwargs, dropped = _filter_kwargs(_SFTConfig, cfg_kwargs)
        if dropped:
            print(f"  [info] dropped unsupported SFTConfig kwargs: {dropped}")
        trainer_args = _SFTConfig(**cfg_kwargs)

        # trl >=0.13 renamed SFTTrainer's `tokenizer` arg to `processing_class`.
        trainer_init = inspect.signature(SFTTrainer.__init__).parameters
        trainer_kwargs = dict(
            model=model,
            train_dataset=train_ds,
            args=trainer_args,
        )
        if "processing_class" in trainer_init:
            trainer_kwargs["processing_class"] = tokenizer
        elif "tokenizer" in trainer_init:
            trainer_kwargs["tokenizer"] = tokenizer
        trainer = SFTTrainer(**trainer_kwargs)
    else:
        try:
            training_args = TrainingArguments(**shared_args)
        except TypeError:
            shared_args["evaluation_strategy"] = shared_args.pop("eval_strategy")
            training_args = TrainingArguments(**shared_args)
        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=train_ds,
            dataset_text_field="text",
            max_seq_length=MAX_SEQ_LENGTH,
            args=training_args,
        )

    start_time = time.time()
    wall_clock_limit = WALL_CLOCK_MINUTES * 60

    print(f"\nStarting training (wall-clock limit: {WALL_CLOCK_MINUTES} min)...")
    try:
        trainer.train()
    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")

    elapsed = time.time() - start_time
    print(f"\nTraining complete. Elapsed: {elapsed/60:.1f} min")
    if elapsed > wall_clock_limit:
        print("WARNING: Wall-clock limit exceeded — pivot to prompt-only baseline if needed.")

    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"Adapter saved to {output_dir}")

    loss_log = {
        "model_id": model_id,
        "elapsed_minutes": round(elapsed / 60, 2),
        "train_pairs": len(train_pairs),
        "dev_pairs": len(dev_pairs),
        "lora_rank": LORA_RANK,
        "lora_alpha": LORA_ALPHA,
        "learning_rate": LEARNING_RATE,
        "training_history": [
            {"step": log["step"], "loss": log.get("loss"), "eval_loss": log.get("eval_loss")}
            for log in trainer.state.log_history
            if "loss" in log or "eval_loss" in log
        ],
    }
    loss_log_path = output_dir / "loss_log.json"
    loss_log_path.write_text(json.dumps(loss_log, indent=2))
    print(f"Loss log saved to {loss_log_path}")

    if args.hub_repo:
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            try:
                from huggingface_hub import HfApi
                hf_token = HfApi().token
            except Exception:
                pass
        if not hf_token:
            print("WARNING: HF_TOKEN not set — skipping Hub push.")
        else:
            print(f"Pushing adapter to HuggingFace Hub: {args.hub_repo}...")
            model.push_to_hub(args.hub_repo, token=hf_token)
            tokenizer.push_to_hub(args.hub_repo, token=hf_token)
            print(f"Adapter pushed to https://huggingface.co/{args.hub_repo}")


if __name__ == "__main__":
    main()
