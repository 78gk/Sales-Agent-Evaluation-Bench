# Synthesis Memos — Tenacious-Bench v0.1

Critical engagement memos for required reading papers. Each memo:
- Names a specific design choice the authors made (with section/page reference)
- Disagrees with that choice explicitly — not a hedge or a question
- Grounds the disagreement in Week 10 or Week 11 evidence
- Is ~300–700 words

## Completed Memos (8/8)

| # | File | Paper | Venue | Key Disagreement |
|---|---|---|---|---|
| 1 | [lima.md](./lima.md) | Zhou et al. — LIMA: Less Is More for Alignment | NeurIPS 2023 | GPT-4 preference judge is insufficient when correct behavior is epistemically constrained (hypothesis > assertive) |
| 2 | [magpie.md](./magpie.md) | Xu et al. — Magpie: Alignment Data Synthesis | ACL 2024 | Self-generation encodes the model's assertive prior as training ground truth; quality filter ≠ domain-correctness filter |
| 3 | [tulu3.md](./tulu3.md) | Lambert et al. — Tülu 3 | arXiv 2024 | Standard benchmarks (MMLU, GPT-4 win-rate) too coarse for failure modes hidden in narrow decision patterns |
| 4 | [gebru2021.md](./gebru2021.md) | Gebru et al. — Datasheets for Datasets | CACM 2021 | Framework assumes static finalized datasets; no guidance for staged-authoring pipelines with interim snapshots |
| 5 | [pushkarna2022.md](./pushkarna2022.md) | Pushkarna & Zaldivar — Data Cards | FAccT 2022 | Three-layer structure creates navigation overhead when same reviewer moves between all three audience roles in one session |
| 6 | [liu2024.md](./liu2024.md) | Liu et al. — From Quantity to Quality | COLM 2024 | Perplexity conflates tier-decision uncertainty (productive signal) with lexical uncertainty (noise); misses confidently-wrong examples |
| 7 | [gu2024.md](./gu2024.md) | Gu et al. — LLM-as-a-Judge Survey | arXiv 2024 | Better rubrics don't fix correlated error when judges share a misaligned prior; deterministic checks are the correct fix |
| 8 | [chen_emnlp.md](./chen_emnlp.md) | Chan et al. — ChatEval | EMNLP 2023 | Multi-judge consensus is a failure mode when judges share a common prior; consistency ≠ correctness for domain-specific evaluation |
