"""
Push tenacious_bench_v0.1 train + dev + held_out partitions to HuggingFace.

The held_out split is published post-training so the evaluation is reproducible.
Training is complete and the Delta B result (ablation_results.json) was computed
on the sealed 62-task held_out before publication, so publishing the labels here
does not compromise the validity of the reported numbers.

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

print(f"Uploading train/ dev/ held_out/ from {LOCAL_DIR} to {REPO_ID} ...")
api.upload_folder(
    folder_path=str(LOCAL_DIR),
    repo_id=REPO_ID,
    repo_type="dataset",
    commit_message="Add held_out split (62 tasks) for independent Delta B verification",
)

# Upload datasheet.md from project root so it is accessible on the HF Files tab
datasheet_path = Path(__file__).parent / "datasheet.md"
print(f"Uploading datasheet.md ...")
api.upload_file(
    path_or_fileobj=str(datasheet_path),
    path_in_repo="datasheet.md",
    repo_id=REPO_ID,
    repo_type="dataset",
    commit_message="Add Gebru-style datasheet (7 sections)",
)

print("Dataset push complete.")
print(f"  https://huggingface.co/datasets/{REPO_ID}")
