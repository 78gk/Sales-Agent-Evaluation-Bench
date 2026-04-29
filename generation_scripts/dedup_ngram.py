"""
dedup_ngram.py — 8-gram fingerprint contamination check.
Asserts no cross-split overlap in agent_prompt text across train / dev / held_out.

Usage:
    python generation_scripts/dedup_ngram.py
Exit 0 if clean, 1 if overlaps found.
Output: generation_scripts/contamination_report.md
"""

import json
import sys
from pathlib import Path

N = 8
SPLITS = {
    "train":    list(Path("tenacious_bench_v0.1/train").glob("*.json")),
    "dev":      list(Path("tenacious_bench_v0.1/dev").glob("*.json")),
    "held_out": list(Path("tenacious_bench_v0.1/held_out").glob("*.json")),
}


def ngrams(text: str, n: int) -> set:
    words = text.lower().split()
    return {tuple(words[i: i + n]) for i in range(len(words) - n + 1)}


def run() -> tuple[list, dict]:
    index: dict[tuple, tuple[str, str]] = {}
    overlaps: list[tuple] = []
    stats: dict[str, int] = {}

    for split_name, files in SPLITS.items():
        stats[split_name] = len(files)
        for f in files:
            task = json.loads(f.read_text(encoding="utf-8"))
            tid = task["task_id"]
            prompt = task["input"]["agent_prompt"]
            for ng in ngrams(prompt, N):
                if ng in index:
                    other_tid, other_split = index[ng]
                    if other_split != split_name:
                        overlaps.append(
                            (tid, split_name, other_tid, other_split, " ".join(ng))
                        )
                else:
                    index[ng] = (tid, split_name)

    return overlaps, stats


def write_report(overlaps: list, stats: dict) -> None:
    total = sum(stats.values())
    status = "PASS" if not overlaps else "FAIL"
    lines = [
        "# Contamination Report — Tenacious-Bench v0.1",
        "",
        f"**Method:** 8-gram fingerprint overlap across train / dev / held_out  ",
        f"**Date:** 2026-04-30  ",
        f"**Status:** {status}",
        "",
        "## Split Sizes",
        "",
        f"| Split | Tasks |",
        f"|---|---|",
    ]
    for split, count in stats.items():
        lines.append(f"| {split} | {count} |")
    lines += [
        f"| **Total** | **{total}** |",
        "",
        "## Result",
        "",
    ]
    if not overlaps:
        lines += [
            f"No 8-gram overlaps detected across {total} tasks.",
            "",
            "Every `agent_prompt` in held_out is textually distinct from all train and dev prompts.",
        ]
    else:
        lines += [
            f"{len(overlaps)} cross-split overlaps detected. Tasks below must be revised before sealing.",
            "",
            "| Task | Split | Overlaps With | Split | Shared 8-gram |",
            "|---|---|---|---|---|",
        ]
        for o in overlaps:
            lines.append(f"| {o[0]} | {o[1]} | {o[2]} | {o[3]} | `{o[4]}` |")

    lines += [
        "",
        "## Embed Check",
        "",
        "Cosine-similarity check (all-MiniLM-L6-v2, threshold 0.85) — pending Day 4 Colab run.",
        "n-gram check is the primary gate for the Day 3 seal.",
    ]

    out = Path("generation_scripts/contamination_report.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {out}")


def main():
    overlaps, stats = run()
    total = sum(stats.values())

    if overlaps:
        print(f"FAIL: {len(overlaps)} cross-split 8-gram overlaps found:")
        for o in overlaps[:10]:
            print(f"  {o[0]} ({o[1]}) overlaps {o[2]} ({o[3]}): '{o[4]}'")
    else:
        print(f"PASS: No 8-gram overlaps across {total} tasks "
              f"(train={stats['train']}, dev={stats['dev']}, held_out={stats['held_out']}).")

    write_report(overlaps, stats)
    sys.exit(1 if overlaps else 0)


if __name__ == "__main__":
    main()
