# Methodology Rationale — Path A (SFT)

**Status:** Rationale complete with full trace and paper citations.  
**Scope:** Path A — Supervised Fine-Tuning on Qwen 3.5 (0.8B or 2B)

---

## Path Selection: SFT (Path A)

Signal Over-Claiming is a generation quality failure, not a consistency or trajectory failure. The agent produces assertive phrasing when the evidence weight mandates hedging — this is a first-token generation decision that SFT directly addresses.

### Week 10 Trace Evidence

Three traces from `seeds/trace_log.jsonl` directly motivate this choice:

**Trace sim_a553180f (task 11, reward=0.0)**  
The agent completes the task but asserts product availability without verifying stock — structurally identical to asserting hiring velocity without checking the 5-role threshold. The failure is in the generation step: the model outputs a confident assertion when the evidence is ambiguous.

**Trace sim_0857ba6e (task 76, reward=0.0)**  
The agent attempts to complete an under-constrained task instead of routing to clarification. Analogous to confirming headcount without routing to the delivery lead. SFT on (constrained_prompt → abstention_output) pairs directly teaches this routing decision.

**Trace sim_f50f1801 (task 105, reward=0.0)**  
Over-confident resolution on a partial signal set. The model does not hedge despite missing required evidence. This is the Signal Over-Claiming failure mode in a retail proxy: asserting a conclusion when the inputs do not support it.

### Why Not Path B (DPO/SimPO)?

Path B addresses inconsistency — the model gets it right most of the time but can't detect when it's wrong. Signal Over-Claiming is not inconsistency: the model is *consistently wrong* in predictable conditions (low-confidence signals, stale data). SFT on labeled (input, correct_tier) pairs is cleaner and lower cost for a deterministic routing failure.

### Why Not Path C (PRM)?

Path C addresses trajectory failures — locally reasonable steps that lead to bad endings. Signal Over-Claiming happens in a single generation step, not across a multi-step trajectory. PRM overhead is not justified.

---

## Paper Support — Path-Specific Publications

**1. Ding et al. (2024). Tülu 3: Pushing Frontiers in Open-Source Posttraining.**  
Available at arXiv / OpenReview. Core finding: targeted SFT on 500–2,000 curated examples
produces measurable behavioral change. LoRA on open-source base models (Qwen, Llama)
achieves performance comparable to full fine-tuning with minimal compute overhead.
Directly supports Path A scope: 125 training tasks on Qwen 3.5 with LoRA is sufficient
to internalize the phrasing-gate decision.

**2. Zhou et al. (2023). LIMA: Less Is More for Alignment. *NeurIPS 2023*.**  
The "superficial alignment hypothesis": 1,000 carefully curated instruction-following
examples on a strong base model (LLaMA-65B) produce outputs competitive with RLHF-trained
models. Supports the 125-task training split — quality over volume, not data-volume
problems.

**3. Xu et al. (2024). Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing. *ACL 2024 (Findings)*.**  
Demonstrates multi-LLM synthesis: prompt an instruction-tuned model to generate both
instruction and response, then filter. Shows diversity emerges naturally without seed
instructions. Directly informs `generation_scripts/router_design`: the critical insight
is that generator ≠ judge is necessary. Magpie's design lacks this cross-model check;
our router_config.json enforces it.

---

## Backbone Selection

**Qwen 3.5 (0.8B or 2B — final choice by Day 3 based on T4 VRAM fit)**

- 0.8B: fits T4 (16 GB) comfortably; faster iteration; lower cost; less capacity for nuanced phrasing tier decisions
- 2B: fits T4 at 16-bit with Unsloth; better capacity for the 4-class phrasing gate; ~2× training time

Decision rule: attempt 2B first; fall back to 0.8B if training loss does not converge within 30 minutes.

**LoRA configuration (from Unsloth Qwen 3.5 guide):**
- rank: 16
- alpha: 32
- target modules: q_proj, v_proj
- 16-bit (not QLoRA 4-bit)
- Publish adapter only — do not merge into base weights
