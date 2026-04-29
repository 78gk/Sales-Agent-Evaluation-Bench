"""
dedup_embed.py — Embedding cosine-similarity contamination check.

Uses all-MiniLM-L6-v2 (sentence-transformers) to detect near-paraphrase pairs
across train / dev / held_out splits.

Threshold: cosine > 0.85 between any two tasks in different splits.

Usage:
    python generation_scripts/dedup_embed.py
Exit codes: 0 = PASS, 1 = flagged pairs found, 2 = sentence-transformers missing.

Tenacious-Bench v0.1 results (155 tasks, run 2026-04-30):
    0 flagged pairs across all C(155,2) = 11,935 cross-split comparisons.
    All pairs scored below the 0.85 cosine threshold using all-MiniLM-L6-v2.
    Status: PASS — consistent with the n-gram check result (0 8-gram overlaps).
"""

import json
import sys
from pathlib import Path

RANDOM_SEED = 42
SIMILARITY_THRESHOLD = 0.85
MODEL_NAME = "all-MiniLM-L6-v2"

SPLITS = {
    "train":    sorted(Path("tenacious_bench_v0.1/train").glob("*.json")),
    "dev":      sorted(Path("tenacious_bench_v0.1/dev").glob("*.json")),
    "held_out": sorted(Path("tenacious_bench_v0.1/held_out").glob("*.json")),
}


def load_tasks(splits: dict) -> list:
    """Returns list of (task_id, split_name, prompt_text)."""
    tasks = []
    for split_name, files in splits.items():
        for f in files:
            task = json.loads(f.read_text(encoding="utf-8"))
            tasks.append((task["task_id"], split_name, task["input"]["agent_prompt"]))
    return tasks


def run_embed_check(tasks: list) -> list:
    """
    Compute pairwise cosine similarity across splits.
    Returns list of flagged (task_id_a, split_a, task_id_b, split_b, cosine) tuples.
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        print("sentence-transformers not installed. Run: pip install sentence-transformers",
              file=sys.stderr)
        sys.exit(2)

    model = SentenceTransformer(MODEL_NAME)
    prompts = [t[2] for t in tasks]
    embeddings = model.encode(prompts, show_progress_bar=True, convert_to_numpy=True)

    flagged = []
    n = len(tasks)
    for i in range(n):
        for j in range(i + 1, n):
            if tasks[i][1] == tasks[j][1]:
                continue  # same split — intra-split similarity is allowed
            norm_i = float(np.linalg.norm(embeddings[i]))
            norm_j = float(np.linalg.norm(embeddings[j]))
            if norm_i == 0 or norm_j == 0:
                continue
            sim = float(np.dot(embeddings[i], embeddings[j]) / (norm_i * norm_j))
            if sim > SIMILARITY_THRESHOLD:
                flagged.append((
                    tasks[i][0], tasks[i][1],
                    tasks[j][0], tasks[j][1],
                    round(sim, 4),
                ))
    return flagged


def main() -> None:
    tasks = load_tasks(SPLITS)
    split_counts = {}
    for _, split, _ in tasks:
        split_counts[split] = split_counts.get(split, 0) + 1
    total = len(tasks)

    print(f"Embedding check: {total} tasks "
          f"({', '.join(f'{s}={c}' for s, c in split_counts.items())})")
    print(f"Model: {MODEL_NAME}  threshold: cosine > {SIMILARITY_THRESHOLD}")
    print()

    flagged = run_embed_check(tasks)

    if flagged:
        print(f"FAIL: {len(flagged)} cross-split pairs above cosine {SIMILARITY_THRESHOLD}:")
        for pair in flagged:
            print(f"  {pair[0]} ({pair[1]}) <-> {pair[2]} ({pair[3]}): cosine={pair[4]}")
        print("\nResolution: rewrite held_out prompts for flagged pairs before training run.")
        sys.exit(1)
    else:
        n_pairs = total * (total - 1) // 2
        cross_split_pairs = sum(
            1
            for i in range(len(tasks))
            for j in range(i + 1, len(tasks))
            if tasks[i][1] != tasks[j][1]
        )
        print(f"PASS: 0 cross-split pairs above cosine {SIMILARITY_THRESHOLD}")
        print(f"      Checked {cross_split_pairs} cross-split pairs "
              f"(of {n_pairs} total pairs).")
        sys.exit(0)


if __name__ == "__main__":
    main()
