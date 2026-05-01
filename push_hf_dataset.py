"""
Push tenacious_bench_v0.1 train + dev partitions to HuggingFace.
NEVER uploads held_out/ — it is sealed and gitignored.

Usage: python push_hf_dataset.py
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

REPO_ID = "kirutew17654321/tenacious-bench-v0.1"
LOCAL_DIR = Path(__file__).parent / "tenacious_bench_v0.1"

api = HfApi(token=token)
api.create_repo(REPO_ID, repo_type="dataset", exist_ok=True, private=False)

print(f"Uploading train/ and dev/ from {LOCAL_DIR} to {REPO_ID} ...")
api.upload_folder(
    folder_path=str(LOCAL_DIR),
    repo_id=REPO_ID,
    repo_type="dataset",
    ignore_patterns=["held_out/*", "held_out/**"],
    commit_message="Add tenacious_bench_v0.1 train+dev (260 tasks, CC-BY-4.0)",
)
print("Dataset push complete.")
print(f"  https://huggingface.co/datasets/{REPO_ID}")
