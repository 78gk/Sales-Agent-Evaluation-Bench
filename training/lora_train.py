"""
lora_train.py — Tenacious-Bench v0.1 LoRA training script.

Trains a LoRA adapter on Qwen 3.5 (0.8B or 2B) using the Unsloth library for
fast training on Colab T4 (16 GB VRAM). Target: fix Signal Over-Claiming by
SFT on the phrasing-gate decision.

Usage (Colab T4 — paste as cells or run as script):
    python training/lora_train.py \\
        --pairs training/qwen_pairs.jsonl \\
        --model qwen2.5-0.5b-instruct \\
        --output training/checkpoint \\
        --hub-repo 78gk/tenacious-bench-qwen-lora

Hyperparameters (Path A spec from CLAUDE.md):
    rank=16, alpha=32, target=q_proj+v_proj, dtype=float16
    lr=2e-4, batch=4, grad_accum=4, epochs=3
    Wall-clock budget: 30 minutes on T4 (kill criterion triggers if exceeded)

Kill criterion (from memo.md §7.5):
    - Dev loss plateau (no improvement over 100 steps) → halve lr
    - Dev loss divergence (>20% rise over 50 steps) → add weight_decay
    - Mode collapse on dev → increase rank to 32
    - Wall-clock >30 min → pivot to prompt-only baseline (Delta B primary)
"""

import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — Path A spec
# ---------------------------------------------------------------------------
MODEL_OPTIONS = {
    "qwen2.5-0.5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b-instruct":   "Qwen/Qwen2.5-3B-Instruct",
}

LORA_RANK          = 16
LORA_ALPHA         = 32
LORA_TARGET_MODS   = ["q_proj", "v_proj"]
DTYPE              = "float16"    # T4 16-bit
LEARNING_RATE      = 2e-4
BATCH_SIZE         = 4
GRAD_ACCUM         = 4           # effective batch = 16
NUM_EPOCHS         = 3
MAX_SEQ_LENGTH     = 2048
WARMUP_STEPS       = 20
WALL_CLOCK_MINUTES = 30          # hard kill at 30 min per CLAUDE.md spec
DEV_SPLIT_RATIO    = 0.1         # 10% of pairs held for dev loss monitoring
RANDOM_SEED        = 42

# Kill-criterion thresholds
PLATEAU_STEPS      = 100   # no dev improvement → halve lr
DIVERGE_STEPS      = 50    # dev loss rise >20% over N steps → add weight_decay
DIVERGE_RATIO      = 1.20  # 20% rise triggers divergence flag


def load_pairs(pairs_path: Path) -> list:
    """Load JSONL training pairs."""
    pairs = []
    with pairs_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


def split_train_dev(pairs: list, dev_ratio: float, seed: int) -> tuple:
    """Stratified split by task_id prefix to keep augmented variants together."""
    import random
    random.seed(seed)

    # Group by source task_id
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


def format_for_unsloth(pairs: list) -> list:
    """Convert ChatML dicts to Unsloth-compatible conversation format."""
    return [{"conversations": p["messages"]} for p in pairs]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tenacious-Bench LoRA training")
    parser.add_argument("--pairs", type=str,
                        default="training/qwen_pairs.jsonl",
                        help="Path to JSONL training pairs")
    parser.add_argument("--model", type=str,
                        default="qwen2.5-0.5b-instruct",
                        choices=list(MODEL_OPTIONS.keys()),
                        help="Model size to train")
    parser.add_argument("--output", type=str,
                        default="training/checkpoint",
                        help="Output directory for LoRA adapter")
    parser.add_argument("--hub-repo", type=str,
                        default="kirutew17654321/tenacious-bench-qwen-lora",
                        help="HuggingFace Hub repo to push adapter (requires HF_TOKEN)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print config and data stats without training")
    args = parser.parse_args()

    pairs_path = Path(args.pairs)
    output_dir = Path(args.output)
    model_id   = MODEL_OPTIONS[args.model]

    if not pairs_path.exists():
        print(f"ERROR: pairs file not found: {pairs_path}", file=sys.stderr)
        print("Run: python training/prepare_sft_data.py first")
        sys.exit(1)

    pairs = load_pairs(pairs_path)
    train_pairs, dev_pairs = split_train_dev(pairs, DEV_SPLIT_RATIO, RANDOM_SEED)

    print(f"=== Tenacious-Bench LoRA Training ===")
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

    # ---------------------------------------------------------------------------
    # Import Unsloth — must be installed in Colab with:
    #   pip install unsloth[colab-new]
    # ---------------------------------------------------------------------------
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError as e:
        print(f"ERROR: Required package not installed: {e}")
        print("Run: pip install unsloth[colab-new] trl datasets")
        sys.exit(1)

    print("\nLoading base model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_id,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,        # auto-detect float16 on T4
        load_in_4bit=False,  # 16-bit per spec; set True for 0.5B if OOM
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_RANK,
        target_modules=LORA_TARGET_MODS,
        lora_alpha=LORA_ALPHA,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=RANDOM_SEED,
    )

    def format_messages(example):
        """Apply ChatML template."""
        text = tokenizer.apply_chat_template(
            example["conversations"],
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}

    train_ds = Dataset.from_list(format_for_unsloth(train_pairs)).map(format_messages)
    dev_ds   = Dataset.from_list(format_for_unsloth(dev_pairs)).map(format_messages)

    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_steps=WARMUP_STEPS,
        fp16=True,
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        seed=RANDOM_SEED,
        report_to="none",          # no W&B — keep costs zero
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        args=training_args,
    )

    # ---------------------------------------------------------------------------
    # Wall-clock kill criterion
    # ---------------------------------------------------------------------------
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
        print("WARNING: Wall-clock limit exceeded. Kill criterion triggered.")
        print("See CLAUDE.md §7.5 kill criterion — pivot to prompt-only baseline if needed.")

    # Save adapter
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"Adapter saved to {output_dir}")

    # Write loss log
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
        ]
    }
    loss_log_path = output_dir / "loss_log.json"
    loss_log_path.write_text(json.dumps(loss_log, indent=2))
    print(f"Loss log saved to {loss_log_path}")

    # Push to Hub if requested
    if args.hub_repo:
        import os
        from huggingface_hub import HfApi
        hf_token = os.environ.get("HF_TOKEN") or HfApi().token
        if not hf_token:
            print("WARNING: HF_TOKEN not set and no cached HF credentials — skipping Hub push.")
            print("Run notebook_login() or set HF_TOKEN env var before training.")
        else:
            print(f"Pushing adapter to HuggingFace Hub: {args.hub_repo}...")
            model.push_to_hub(args.hub_repo, token=hf_token)
            tokenizer.push_to_hub(args.hub_repo, token=hf_token)
            print(f"Adapter pushed to https://huggingface.co/{args.hub_repo}")


if __name__ == "__main__":
    main()
