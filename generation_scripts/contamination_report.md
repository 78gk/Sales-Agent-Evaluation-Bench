# Contamination Report — Tenacious-Bench v0.1

**Method:** 8-gram fingerprint overlap across train / dev / held_out  
**Date:** 2026-05-01  
**Status:** PASS

## Split Sizes

| Split | Tasks |
|---|---|
| train | 131 |
| dev | 55 |
| held_out | 50 |
| **Total** | **236** |

## Result

No 8-gram overlaps detected across 236 tasks.

Every `agent_prompt` in held_out is textually distinct from all train and dev prompts.

## Embed Check

Cosine-similarity check (all-MiniLM-L6-v2, threshold 0.85) — pending Day 4 Colab run.
n-gram check is the primary gate for the Day 3 seal.