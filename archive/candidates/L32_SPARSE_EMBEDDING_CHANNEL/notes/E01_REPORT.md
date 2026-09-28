# L32 E01 — Pilot Report

**Date:** 2026-09-13.
**Verdict: first-stage gate PASSES; channel question ANSWERED decisively; the
answer is a claim mutation.**

Design frozen in `notes/E01_DESIGN.md` before any tuned arm was evaluated.
Nothing below departs from that pre-registration. Two additions to the frozen
plan are flagged explicitly in §5 and §6 and were run as instrument checks.

---

## 1. What ran

3 training seeds x LLaMA-7B (`huggyllama/llama-7b`) + 10k en→ca pairs, only the
18 published KS-Lottery en→ca embedding rows trainable (73,728 parameters; the
backbone reports zero trainable parameters), LR 1e-2, 5 epochs. Evaluation on
Flores-101 devtest (1012 sentences, original tarball), greedy, spBLEU via
`sacrebleu` `tokenize="flores101"`. 8 channel arms x 3 seeds, plus a
norm-matched random-delta control and a template-transfer check.

Every arm uses the **same** trained delta; only which positions may read the
tuned rows differs.

## 2. First-stage gate: PASSES

| | spBLEU | 95% CI |
|---|---|---|
| BASE (base rows everywhere) | 6.21 | [5.97, 6.45] |
| ALL (tuned rows wherever they occur) | 35.71 | [34.72, 36.77] |
| **`Δ_ALL`** | **+29.50** | **[+28.59, +30.46]** |

Gate was `≥ +15`, same sign in all 3 seeds. Passed: +29.50, seeds 36.00 / 35.66 /
35.46 against a seed-invariant base of 6.21. This reproduces the parent's en→ca
phenomenon (KS-Lottery reports 5.7 → 37.7).

## 3. Almost all of the reproduced effect is termination, not translation

The same runs, scored on the first line of the continuation instead of the whole
continuation — i.e. with the model's failure to stop neutralised:

| | raw | first line |
|---|---|---|
| BASE | 6.21 | **33.99** |
| ALL | 35.71 | 35.71 |
| `Δ_ALL` | **+29.50** [+28.59, +30.46] | **+1.72** [+1.03, +2.42] |

Termination behaviour, same runs:

| arm | EOS emitted | mean chars |
|---|---|---|
| BASE | 13% | 833 |
| ALL | 100% | 138 |

**The untuned model already produces the Catalan translation and then keeps
generating.** Of the +29.50 headline, +1.72 (5.8%) is translation quality and
+27.8 (94%) is the model learning to stop. `Δ_trunc` is small but real — its CI
excludes zero — so this is a decomposition, not a null.

This was anticipated by the pre-registered instrument audit (`E01_DESIGN.md` §2,
`results/prompt_probe.json`): on the untuned model the *same* base LLaMA-7B
scores anywhere in **0.31 – 33.78 spBLEU** on this task depending only on prompt
template and output post-processing. The parent's 5.7 is reproducible only under
whole-continuation scoring.

## 4. Where the update acts: the instruction span, and nothing else

Recovery `R_c = (M(c) − M(BASE)) / (M(ALL) − M(BASE))`, raw scoring, paired
bootstrap over sentences with training seeds resampled, 2000 draws:

| arm | spBLEU | `Δ` vs BASE | **recovery** | 95% CI | stop | chars |
|---|---|---|---|---|---|---|
| ALL | 35.71 | +29.50 | 1.00 | — | 1.00 | 138 |
| PREFILL | 35.75 | +29.55 | **1.00** | [0.99, 1.02] | 1.00 | 138 |
| INSTRUCTION | 35.68 | +29.48 | **1.00** | [0.98, 1.02] | 1.00 | 138 |
| INSTR_HEAD | 35.53 | +29.33 | **0.99** | [0.98, 1.01] | 1.00 | 139 |
| INSTR_TAIL | 20.03 | +13.92 | 0.47 | [0.28, 0.76] | 0.84 | 292 |
| SOURCE | 6.17 | −0.04 | **−0.00** | [−0.01, 0.01] | 0.16 | 842 |
| TARGET | 7.58 | +1.35 | **0.05** | [−0.01, 0.09] | 0.33 | 698 |

Same decomposition on the quality component alone (first-line scoring):
INSTRUCTION 1.00 [0.73, 1.40], INSTR_HEAD 0.92, SOURCE 0.12 [−0.21, 0.42],
TARGET −0.02 [−0.21, 0.14].

**Selection's accounts A (source interface), B (autoregressive feedback) and D
(joint access) are all rejected. Account C (task-prefix) is confirmed at
recovery 1.00.**

The critical control is the pre-registered support audit
(`results/support_audit.json`): the 18 selected ids occur **more** often in the
source span than in the instruction span — 7.73 vs 7.00 occurrences per
sentence, on all 1012 sentences — and they are 25% of all source tokens. Source
access recovers exactly nothing anyway. So this is not an opportunity effect.

## 5. The effect is specific to the learned direction (added control)

A random delta with row-by-row matched norms, applied at the same positions:

| | spBLEU | stop | chars |
|---|---|---|---|
| ALL, learned delta | 35.71 | 1.00 | 138 |
| ALL, norm-matched random delta | **0.05** | 0.00 | 1060 |
| INSTRUCTION, norm-matched random delta | 0.32 | 0.01 | 1138 |

So the result is not "perturbing 18 frequent rows changes behaviour". Matched
perturbation destroys the model.

## 6. The ticket is keyed to the template it was trained under (added check)

Swap the prompt template at inference; change nothing else
(`results/template_transfer_*.json`, 400 sentences, seeds 0 and 2):

| template | BASE raw | ALL raw | `Δ_raw` s0 | `Δ_raw` s2 |
|---|---|---|---|---|
| `explicit` (the trained one) | 6.23 | 35.67 / 35.22 | **+29.44** | **+28.99** |
| `reordered` (rewritten instruction, same `English:` / `Catalan:` labels) | 8.85 | 35.20 / 33.04 | +26.35 | +24.19 |
| `bare_pair` (labels only, no instruction sentence) | 9.19 | 19.51 / 18.11 | +10.33 | +8.92 |
| `paraphrase` (paraphrased instruction, `Source:` / `Target:` labels) | 2.51 | 9.91 / 2.09 | **+7.40** | **−0.42** |

The gain does not survive a paraphrase of the very same task instruction. This
distinguishes the two readings of §4: the rows do **not** carry a translation
capability injected at instruction positions; they carry a cue keyed to the
particular template.

## 7. What this means for the parent

KS-Lottery's en→ca headline — 18 embedding rows recovering full fine-tuning
translation performance, presented as evidence that multilingual transfer has an
ultra-low-dimensional locus in the embedding layer — decomposes as:

1. **94% of it is termination.** The untuned model translates; first-line
   scoring puts it at 33.99 against the tuned model's 35.71.
2. **100% of what is left is carried by occurrences inside the fixed instruction
   template**, with zero contribution from the source sentence despite more
   opportunity there, and ~5% from generated-target feedback.
3. **It does not survive a paraphrase of that template.**

The ticket is a prefill-time format/stop cue written into shared vocabulary rows,
not a multilingual capability locus. Note the parent's own selected tokens are
`\n`, `.`, `,`, `:`, `"`, `▁`, digits, and English function words — consistent
with this reading and with the parent's own observation that winning tickets are
high-frequency tokens. Frequency and template-occurrence are perfectly
confounded in the parent's setup.

Two caveats stated plainly. First, the parent's prompt is unpublished, so we
cannot prove their 5.7 was produced the way ours is — only that a base model's
score on this task spans 0.31–33.78 with the prompt and post-processing, and
that 5.7 sits inside the untruncated part of that range. Second, this is one
language pair and one model; the parent reports five pairs.

## 8. Status against the authorization

E01's question — *where does the sparse update act* — is **answered**, at a
resolution far above the noise floor (recovery CIs of width 0.04). The
first-stage gate passed. Nothing here is resolution-limited, which is the
failure mode L30 hit.

But the answer moves the paper identity: from *where does the multilingual ticket
act* to *the certified multilingual ticket is a template-keyed stop cue*. Under
`RESEARCH_EXECUTION.md` §8 that is a claim mutation and the authorization has
expired. See `notes/CLAIM_NOVELTY_DELTA.md`.

**C2 remains unauthorised, and E01 does not authorise it.**
