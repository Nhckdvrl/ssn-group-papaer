# L08 — E12 preregistration: answer provenance, manipulated within item

**Written 2026-09-14, before any E12 run.** Authorizes one bounded confirmatory
package and nothing else. Registers the analysis and the kill rules in advance.

Linked claim: `C2` in [`MAINLINE.md`](MAINLINE.md) §2.
Motivating audit: [`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md).

---

## 1. What E12 has to fix

The depth-by-provenance law currently rests on a **between-dataset** contrast: MMLU is
prompt-recoverable, GSM8K is trajectory-carried. Three things are confounded with
provenance and every one of them is a reviewer's first question.

| confound | why it is live | removed by |
|---|---|---|
| **domain** — general knowledge vs arithmetic | nothing separates "prompt-recoverable" from "not arithmetic" | arm B on the *same items* |
| **answer format** — 4-way MC vs open numeric | the flat MMLU slope could be a chance floor | the open-ended knowledge cell, arm D |
| **difficulty** — longer chains are harder items | `L` is observational, not randomised | depth randomised by construction in arms B and D |

E12 is a 2x2 that orthogonalises **capability** and **answer provenance** on fixed
items, at matched depth.

## 2. Design

Factor 1, **capability**: knowledge content vs reasoning content.
Factor 2, **answer provenance**, manipulated within item:

- **trajectory-carried** — the answer exists only in tokens the model has emitted;
- **prompt-recoverable** — the information that determines the answer is present in
  the prompt at the moment of emission, but the model still generates a passage of
  matched length before answering.

| arm | items | capability | provenance | construction |
|---|---|---|---|---|
| **A** | GSM8K | reasoning | trajectory-carried | standard 5-shot CoT, as E01 |
| **B** | **the same GSM8K items** | reasoning | prompt-recoverable | the correct solution chain is supplied in the prompt; the model is instructed to restate and verify it, then answer. The answer is readable from the prompt throughout |
| **C** | MMLU | knowledge | prompt-recoverable | standard 5-shot CoT, as E01 |
| **D** | **the same MMLU items** | knowledge | trajectory-carried | the model must first derive an intermediate result that is *not* in the prompt and that the final answer depends on, then answer from its own derivation |

**Prediction.** The slope of retention on depth is steep in A and D, flat in B and C.
If the law is about provenance, the A/B gap and the C/D gap both open, and the
capability main effect is small. If the law is really about capability, A and C keep
their slopes when provenance is swapped and B/D change nothing.

**Depth is randomised, not observed.** In arms B and D the generated passage is padded
to a preassigned target length drawn from a fixed grid
(`L ∈ {16, 32, 64, 128, 256}` tokens, assigned to items by a seed independent of the
item), so depth is exogenous and uncorrelated with difficulty. Arms A and C keep their
natural depth and are the link back to the observational result.

**Arm D is the one that can fail for a boring reason** and it is designed first: the
derivation must be genuinely load-bearing, verified by an ablation in which the
derived quantity is corrupted and accuracy must fall for the full-precision model.
If the full model is insensitive to its own derivation in arm D, arm D is not
trajectory-carried and the arm is void — reported as such, not reinterpreted.

## 3. Interventions

The existing magnitude prune + RTN quantization cannot carry a claim about
compression; UniComp's headline uses Wanda, SparseGPT, AWQ and GPTQ, and a reviewer
will call our interventions artifacts. E12 uses, per model:

| locus | method | setting |
|---|---|---|
| parameter | **Wanda** | 50% unstructured |
| parameter | **SparseGPT** | 50% unstructured |
| parameter | **AWQ** or **GPTQ** | 4-bit weight-only |
| readout | readout truncation, first half | as E01, the inherited intervention |
| — | full precision | the denominator |

Severity is fixed in advance at the settings UniComp uses, so the comparison to the
published headline needs no severity argument. Calibration data for Wanda/SparseGPT/
GPTQ is fixed to one corpus across all arms and is **not** task-matched, because
task-matched calibration is a different paper (cf. Reasoning-Aware Compression,
arXiv 2509.12464, which owns the calibration-shift story and must be cited).

## 4. Models

Two families, not five. Breadth is already established by the inherited runs; E12 buys
identification, not breadth.

- `Llama-3.1-8B-Instruct` — the parent's model and UniComp's headline model
- `Qwen2.5-7B-Instruct` — the second parent model, different tokenizer and pretraining

## 5. Analysis, fixed in advance

Primary estimand, per (model, intervention):

```
slope difference  =  b(trajectory-carried)  -  b(prompt-recoverable)
```

where `b` is the coefficient on `log2(1 + L)` in a logistic regression of per-item
retention, retention defined among items the full-precision model answers correctly.
Estimated separately within capability, so the A/B gap and the C/D gap are two
independent tests of the same prediction. Paired bootstrap over items, B = 10000,
95% intervals. `scripts/analyze_depth.py` is the single source of truth and is not
modified after this file is committed except to add the new arms.

Secondary: the capability main effect at matched provenance and matched depth —
A vs D, and B vs C.

A cell whose full-precision baseline is below 0.05, or whose retention is below 0.02,
is `n/e`. Floor effects are never reported as large ratios.

## 6. Kill rules

L08's Main route is killed, and the package returns to ARCHIVED, if:

1. the A/B gap and the C/D gap are both null — provenance manipulated within item does
   not reproduce the observational dissociation;
2. the dissociation holds for readout truncation but for **none** of Wanda, SparseGPT,
   AWQ/GPTQ — the law would then be a property of our toy intervention;
3. arm D (open-ended, trajectory-carried knowledge) decays like arm A, i.e. the flat
   MMLU slope in the inherited data was the multiple-choice chance floor;
4. randomising depth removes the slope difference — it was item difficulty.

**Rescues that are forbidden in advance.** On a kill, the package may not retreat to
(a) "multiple choice and open generation still differ" — owned by Wen et al. and Song
et al.; (b) the `C3.2` no-crossing count — demoted by the 2026-09-14 audit; (c) a
benchmark-auditing or evaluation-recommendation paper. Any of these is a Findings-scale
result at best and the project stops instead.

## 7. C3, and why it is not a new benchmark

Only on a pass. Take a small, fixed set of load-bearing published comparisons —
UniComp's `knowledge bias` headline rows, Takeshita et al.'s Table 3 — and re-estimate
them with provenance and depth matched. Preregistered reading:

- if the published ordering survives matched re-estimation, L08's significance drops
  to a methodological note and the paper is Findings-scale;
- if it shrinks substantially, disappears, or inverts for a defined class of
  intervention, C3 stands and the contribution is a correction to what the field
  currently believes it has measured.

No new benchmark is built. No leaderboard is published.

## 8. Compute

Local environment only: `/home/xiang/miniconda3/envs/verl-clean/bin/python`. No new
environment, no package install or upgrade.

GPUs from idle cards on `fvcrc10`, `fvcrc11`, `fvcrc12`, `fvcrc13`, `fvcrc15`.
**At most four cards at a time for L08.** Idle cards are checked before launch and the
host/card assignment is recorded in the launch log.

Budget: 2 models x 5 intervention settings x 4 arms, 400-500 items per cell, greedy,
fixed token budgets identical across interventions within an arm. Arm D's validity
ablation runs at full precision only.

## 9. Order of work

1. Build arm D and run its full-precision validity ablation. **If arm D is void, stop
   and re-plan** — the 2x2 is not recoverable without it.
2. Build arm B; verify the full-precision model is at ceiling there (it should be near
   ceiling, since the answer is in the prompt), and that padding to target length does
   not itself change full-precision accuracy.
3. Run the full 2x2 under full precision + readout truncation on one model. This is the
   cheap replication of the inherited law under the new design.
4. Only then add Wanda / SparseGPT / AWQ-GPTQ and the second model.

Steps 1 and 2 are validity checks with a real chance of returning "the design does not
work". They come first deliberately.
