# Tenacious-Bench v0.1 — 6-Minute Demo Video Script

**Total target time: 5:45 (15s buffer before 6:00 hard cap)**
**Format: Live walkthroughs only — no slides, no static screenshots**
**Record in one continuous take if possible. If you cut, cut between segments.**

---

## PRE-RECORDING SETUP CHECKLIST
*Do this 5 minutes before hitting record. Do NOT skip.*

### Browser (Chrome/Edge — address bar must be visible)
Open these tabs in order, left to right:
1. **Tab 1 — HF Dataset page:**
   `https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1`
2. **Tab 2 — tau-bench GitHub Issue:**
   `https://github.com/sierra-research/tau-bench/issues/82`
3. **Tab 3 — Blog Post:**
   `https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1/discussions/1`
   (This is the HF Community discussion on the dataset page. If this URL 404s, check
   the Discussions tab on the dataset page and use whichever URL appears there.)

### ⚠️ VERIFY BEFORE RECORDING — Two URLs to check right now

**1. Blog post URL:** Open this in your browser and confirm the full post is there:
   `https://huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1/discussions/1`
   You need to see the heading "Building Tenacious-Bench: What τ²-Bench Can't Measure"
   and scrollable sections. If it 404s, go to the Discussions tab on the dataset page
   and find the correct URL, then update Tab 3.

**2. tau-bench issue:** Open and confirm it exists:
   `https://github.com/sierra-research/tau-bench/issues/82`
   You need to see the issue body with the 4 gap descriptions and probe IDs.

**3. held_out split in Data Viewer:** Open Tab 1 and click the split dropdown.
   You should see train (143), dev (55), held_out (62). If held_out is missing,
   re-run `python push_hf_dataset.py` and wait 2 minutes for HF to re-index.

---

### Terminal (PowerShell or any terminal)
- Navigate to: `c:\projects\10\week-11`
- Run this ONCE to confirm evaluator works:
  ```
  python scoring_evaluator.py --validate
  ```
  You should see 3 OK lines + PASS/FAIL results. If not, fix before recording.

### Pre-stage terminal commands (copy these into a notepad to paste during recording)
```
# COMMAND 1 — Scoring demo (Segment 2)
python scoring_evaluator.py --validate

# COMMAND 2 — Show the task
type tenacious_bench_v0.1\train\TB-0001.json

# COMMAND 3 — Show the bad agent output
type demo_outputs\demo_bad_agent.json

# COMMAND 4 — Run the evaluator on the bad output
python scoring_evaluator.py --task tenacious_bench_v0.1\train\TB-0001.json --output demo_outputs\demo_bad_agent.json

# COMMAND 5 — Show ablation results
type ablations\ablation_results.json

# COMMAND 6 — Show held-out trace artifact
type tenacious_bench_v0.1\held_out\TB-0201.json
```

### Screen resolution
Set to 1080p or higher. Font size in terminal: 16pt minimum (grader must read it).

---

## SEGMENT 1 — HF DATASET WALKTHROUGH
**Timestamp: 0:00 – 1:50 (110 seconds)**
**Worth: 25 points — most important segment, spend the most time here**

---

**[0:00 — Switch to Tab 1 (HF Dataset page). Address bar must be visible.]**

**SAY:**
> "I'm opening the live HuggingFace page for Tenacious-Bench v0.1 — you can see the URL in the address bar: huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1."

*[Let page fully load — 2 seconds]*

**SAY:**
> "This is a 260-task evaluation benchmark for an AI outbound sales agent, covering ten failure categories including Signal Over-Claiming, Bench Over-Commitment, and Thread Isolation. The license shown here is CC-BY-4.0."

*[Point to or scroll to the license badge/section near the top of the page]*

---

**[~0:20 — Click the split dropdown in the Data Viewer (currently showing "train · 143 rows")]**

**SAY:**
> "The Data Viewer shows all three partitions. Train has 143 tasks, dev has 55 tasks, and held-out has 62 tasks — 260 total. Let me click through them."

*[Click the dropdown — you should see train (143 rows), dev (55 rows), held_out (62 rows). Click each one briefly so the count is visible.]*

**SAY (as you click through):**
> "Train — 143. Dev — 55. Held-out — 62. The held-out split was sealed during training and published post-training so others can independently reproduce the Delta B evaluation."

*[Switch back to train.]*

---

**[~0:40 — Open one task in the data viewer. Click any row in the train split (TB-0001 is already visible).]**

**SAY:**
> "Here's a sample task. The source_mode column is visible right in the table — TB-0001 is 'trace_derived', TB-0002 is 'adversarial', TB-0003 is 'programmatic'. All four authoring modes are represented across the dataset."

*[The source_mode column is already visible in the table — no need to click into a row if the column values are readable on screen.]*

---

**[~1:00 — Click the "Files and Versions" tab on the HF dataset page (tab bar near the top). Then click `datasheet.md` in the file list to open it. It will render as formatted markdown.]**

**SAY:**
> "The dataset ships with a full Gebru-style datasheet — I'll open it from the Files tab."

*[Wait for datasheet.md to render. Then SLOWLY SCROLL so each section heading is legible for 2–3 seconds. Say each section name as it scrolls into view:]*

> "Section one — **Motivation**: why this dataset was created, who built it, funding."
> *(scroll)*
> "Section two — **Composition**: 260 instances, split breakdown, authoring mode distribution."
> *(scroll)*
> "Section three — **Collection Process**: trace derivation, programmatic sweeps, multi-LLM synthesis, adversarial hand-authoring."
> *(scroll)*
> "Section four — **Preprocessing**: deduplication via n-gram overlap check, zero held-out leakage confirmed."
> *(scroll)*
> "Section five — **Uses**: intended use for evaluating B2B sales agents on confidence calibration."
> *(scroll)*
> "Section six — **Distribution**: CC-BY-4.0, hosted on HuggingFace Hub."
> *(scroll)*
> "Section seven — **Maintenance**: versioning plan, known limitations, future work."

---

**[~1:35 — Return to top or sidebar of the HF dataset page to show license clearly.]*

**SAY:**
> "License is CC-BY-4.0, visible in the dataset metadata here."

*[0:05 pause — natural breath before transition]*

---

## SEGMENT 2 — END-TO-END TASK SCORING DEMONSTRATION
**Timestamp: 1:50 – 3:00 (70 seconds)**
**Worth: 25 points**

---

**[1:45 — Switch to terminal. Navigate to c:\projects\10\week-11 if not already there.]**

**SAY:**
> "Now I'll show the scoring evaluator working end-to-end on a concrete task."

**TYPE / PASTE:**
```
type tenacious_bench_v0.1\train\TB-0001.json
```

*[Wait for output. Scroll up if needed so input fields are visible.]*

**SAY (while the JSON is on screen):**
> "This is TB-0001 — Signal Over-Claiming, sourced from trace sim_a553180f. The prospect is Northstack. Hiring confidence is 0.38 — below the 0.40 hypothesis-tier cutoff. Their funding event is 240 days old, past the 180-day validity window — stale."

> "The task expects the agent to use 'hypothesis' phrasing and set stale_flag true. Now here's what a bad agent output looks like."

**TYPE / PASTE:**
```
type demo_outputs\demo_bad_agent.json
```

*[Output shows:]*
```json
{
  "phrasing_tier": "inquiry",
  "stale_flag": false,
  "text": "Northstack is scaling aggressively based on their funding and open roles."
}
```

**SAY:**
> "The agent said 'inquiry' tier and didn't flag the stale signal. Let me score it."

**TYPE / PASTE:**
```
python scoring_evaluator.py --task tenacious_bench_v0.1\train\TB-0001.json --output demo_outputs\demo_bad_agent.json
```

*[Expected output on screen:]*
```json
{
  "task_id": "TB-0001",
  "score": 0.0,
  "pass": false,
  "breakdown": {
    "phrasing_tier": 0.0,
    "stale_disclosed": 0.0
  },
  "errors": []
}
```

**SAY (pointing to each field):**
> "Score 0.0 — FAIL. The breakdown tells us why: phrasing_tier scored 0.0 — the agent said 'inquiry' but confidence 0.38 required 'hypothesis'. stale_disclosed scored 0.0 — it never flagged the 240-day-old funding data. Both dimensions fail, combined score 0.0, below the 0.60 pass threshold. The evaluator is purely machine-verifiable — no human in the loop."

---

## SEGMENT 3 — ABLATION RESULT WITH VISIBLE TRACEABILITY
**Timestamp: 3:00 – 4:45 (105 seconds)**
**Worth: 25 points — spend as much time here as on the dataset walkthrough**

---

**[3:00 — Stay in terminal.]**

**SAY:**
> "Now the ablation. I trained a LoRA adapter on Qwen2.5-0.5B-Instruct for 500 steps using 3,003 SFT pairs. Let me show the results."

**TYPE / PASTE:**
```
type ablations\ablation_results.json
```

*[Output shows the full ablation JSON. Scroll or let it display.]*

**SAY (narrate the key numbers as they appear on screen):**
> "Delta B is the primary publishable result: the trained LoRA scores pass@1 = 0.3065 versus the base model with only the phrasing-gate prompt scoring 0.2258. Delta of **+0.1046**."

> "The statistical test is a 1,000-iteration bootstrap: **p = 0.018**, 95% confidence interval **[0.0088, 0.2051]**. The interval does not cross zero — this is statistically significant."

> "Delta A compares the LoRA to the Week 10 baseline held-out. That delta is **-0.2783** — negative, as expected, since the 0.5B LoRA is being compared to a much stronger baseline agent. That negative result is documented and disclosed — a sign-aware result, not a sign-suppressed one."

---

**[~3:50 — Now open the held-out trace artifact to make the traceability chain concrete.]**

**TYPE / PASTE:**
```
type tenacious_bench_v0.1\held_out\TB-0201.json
```

**SAY (while file displays):**
> "This is TB-0201 — one of the 62 held-out tasks that produced the Delta B number. This is an adversarial task, category tone_drift, probe P-015. Scoring dimension 'no_filler_language' checks the agent's response text for filler phrases."

> "Every one of the 62 held-out tasks was run through the evaluator under two conditions — LoRA adapter versus base model plus prompt — and the pass@1 difference between those two conditions is exactly what produced the +0.1046 in the ablation file. The chain is: this task → evaluator → ablation_results.json → evidence_graph.json claim C-007."

---

**[~4:35 — Brief wrap-up line before transition]**

**SAY:**
> "The full evidence chain is in evidence_graph.json. Delta B +0.1046, p=0.018 — that's the training headline."

---

## SEGMENT 4 — BLOG POST AND COMMUNITY ENGAGEMENT
**Timestamp: 4:45 – 5:40 (55 seconds)**
**Worth: 15 points**

---

**[4:45 — Switch to browser. Navigate to Tab 3 (Blog Post). Address bar must be visible.]**

**SAY:**
> "The technical blog post is live on HuggingFace Community. You can see the URL in the address bar."

*[SCROLL slowly through the blog post — show the heading "Building Tenacious-Bench: What τ²-Bench Can't Measure", the sections ($2.4M figure, dataset design, LoRA training results, Delta B), and the length of the post.]*

**SAY:**
> "The post covers the failure taxonomy, the evaluation gap analysis, the authoring pipeline, and the +0.1046 Delta B result — substantive content, not a placeholder."

---

**[~5:10 — Switch to Tab 2 (tau-bench GitHub Issue). Address bar must show github.com/sierra-research/tau-bench/issues/82]**

**SAY:**
> "And here's the community engagement — GitHub issue #82 on the tau-bench repository. You can see the URL. We documented four specific evaluation gaps — Signal Over-Claiming, Staleness Disclosure, Abstention-Under-Pressure, and Thread Isolation — each with probe IDs and trace evidence, and linked the open-source benchmark and adapter as a proposed extension."

*[Scroll briefly to show the body of the issue — let the gap descriptions and probe IDs be visible.]*

---

## CLOSING
**Timestamp: 5:40 – 5:50 (10 seconds)**

**SAY:**
> "That's Tenacious-Bench v0.1 — live dataset on HuggingFace, machine-verifiable scoring, LoRA adapter with statistically significant Delta B, and public community contributions. Thank you."

*[STOP RECORDING — you're under 6:00]*

---

## SCORING RUBRIC COVERAGE VERIFICATION

| Rubric Criterion | Points | How It's Covered in This Script |
|---|---|---|
| **Dataset: Live navigation** | ✓ | Tab 1 opened live with URL visible |
| **Dataset: 7 Gebru sections scrolled** | ✓ | Scroll segment 1:00–1:40, each section named aloud |
| **Dataset: All 3 partitions visible** | ✓ | train/143, dev/55, held_out/62 shown in data viewer |
| **Dataset: source_mode metadata on a task** | ✓ | Data viewer task opened, source_mode="trace_derived" shown |
| **Dataset: License visible** | ✓ | CC-BY-4.0 shown twice |
| **Dataset: Narration** | ✓ | Continuous narration throughout |
| **Scoring: Task input visible** | ✓ | TB-0001.json displayed (company, signals, agent_prompt) |
| **Scoring: Candidate output visible** | ✓ | demo_bad_agent.json displayed |
| **Scoring: Evaluator output on screen** | ✓ | `--task --output` command runs, JSON score shown in terminal |
| **Scoring: Score broken down by dimension** | ✓ | breakdown: {phrasing_tier: 0.0, stale_disclosed: 0.0} visible |
| **Scoring: Specific rubric check applied** | ✓ | stale_disclosed check narrated; text contains filler narrated |
| **Scoring: Narration connecting input→output→score** | ✓ | Full narration traces conf 0.38 → wrong tier → FAIL |
| **Ablation: Numeric value shown** | ✓ | +0.1046 shown in ablation_results.json |
| **Ablation: p-value / CI visible** | ✓ | p=0.018, CI [0.0088, 0.2051] in JSON |
| **Ablation: Held-out trace artifact opened** | ✓ | TB-0201.json opened live |
| **Ablation: Claim traced to source row** | ✓ | delta_b row in ablation_results.json, → evidence_graph C-007 |
| **Ablation: Inferential narration** | ✓ | 62 tasks, two conditions, pass@1 diff explained |
| **Ablation: Negative delta treated equivalently** | ✓ | Delta A = -0.2783 disclosed and narrated |
| **Blog: Shown live at public URL** | ✓ | Tab 3 with address bar visible |
| **Blog: Scrolled to show structure** | ✓ | Heading, sections, length scrolled |
| **Community: Live at public URL** | ✓ | github.com/sierra-research/tau-bench/issues/82 |
| **Community: URL visible in address bar** | ✓ | Tab 2, URL shown |
| **Both artifacts substantive** | ✓ | Blog has full sections; issue has 4 gaps with probe IDs |
| **Time ≤ 6:00** | ✓ | Script runs ~5:50 |
| **All 5 elements present** | ✓ | Dataset / Scoring / Ablation / Blog / Community all present |
| **Heavy time on dataset + ablation** | ✓ | 105s each vs 75s scoring and 55s blog |
| **Clear transitions** | ✓ | Each segment opens with an explicit "now I'll show..." sentence |
| **Live walkthroughs** | ✓ | No slides — all terminal and browser live |

---

## COMMON MISTAKES TO AVOID

- **DO NOT** start recording before all tabs are pre-loaded
- **DO NOT** show the local file system path as the dataset source — it must be the HuggingFace URL
- **DO NOT** read numbers from slides or a PDF — open the actual JSON files in terminal
- **DO NOT** forget to show the license on the HF page
- **DO NOT** let the datasheet scroll too fast — 2-3 seconds per Gebru section heading minimum
- **DO NOT** skip the held-out artifact in Segment 3 — without it the ablation criterion drops from Robust (25) to Functional (15)
- **DO NOT** exceed 6:00 — stop at "Thank you" even if you feel rushed

---

## KEY NUMBERS CHEAT SHEET
*(Post this next to your screen while recording)*

| What | Number |
|---|---|
| Total tasks | 260 |
| Train | 143 |
| Dev | 55 |
| Held-out | 62 |
| SFT pairs | 3,003 (2,709 train + 294 dev) |
| LoRA rank / alpha | 16 / 32 |
| Training steps | 500 |
| Delta B (LoRA vs prompt-only) | **+0.1046** |
| p-value (Delta B) | **0.018** |
| 95% CI (Delta B) | **[0.0088, 0.2051]** |
| Delta A (LoRA vs Week 10 baseline) | **-0.2783** |
| p-value (Delta A) | **0.0000** |
| Signal Over-Claiming trigger rate | 0.55 |
| Annual cost (Signal Over-Claiming) | ~$2.40M / 1,000 touches |
| License | CC-BY-4.0 |
| HF Dataset URL | huggingface.co/datasets/kirutew17654321/tenacious-bench-v0.1 |
| tau-bench Issue URL | github.com/sierra-research/tau-bench/issues/82 |

---

## DEMO_OUTPUTS FILE LOCATION

The pre-staged bad agent output for the scoring demo is at:
```
c:\projects\10\week-11\demo_outputs\demo_bad_agent.json
```

Contents (for reference):
```json
{
  "phrasing_tier": "inquiry",
  "stale_flag": false,
  "text": "Northstack is scaling aggressively based on their funding and open roles."
}
```

Expected evaluator output when you run the command:
```json
{
  "task_id": "TB-0001",
  "score": 0.0,
  "pass": false,
  "breakdown": {
    "phrasing_tier": 0.0,
    "stale_disclosed": 0.0
  },
  "errors": []
}
```
