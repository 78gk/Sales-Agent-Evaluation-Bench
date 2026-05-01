"""
Push model_card.md as README.md to the HuggingFace model repo.

Usage: python push_hf_model_card.py
Requires: HF_TOKEN in .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import HfApi

load_dotenv()
token = os.getenv("HF_TOKEN")
if not token:
    raise SystemExit("HF_TOKEN not found in .env")

REPO_ID = "kirutew17654321/tenacious-bench-qwen-lora"
MODEL_CARD = Path(__file__).parent / "model_card.md"

api = HfApi(token=token)
print(f"Uploading model_card.md as README.md to {REPO_ID} ...")
api.upload_file(
    path_or_fileobj=str(MODEL_CARD),
    path_in_repo="README.md",
    repo_id=REPO_ID,
    repo_type="model",
    commit_message="Update model card: fix training data counts (143 tasks, 3003 pairs)",
)
print("Model card push complete.")
print(f"  https://huggingface.co/kirutew17654321/tenacious-bench-qwen-lora")
