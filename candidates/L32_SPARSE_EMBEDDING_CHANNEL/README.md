# L32 — Where Do 18 Embeddings Work?

**Status:** `E02 COMPLETE — HOLD / Findings. Not promoted to Main candidate.` (2026-09-13)  
**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main

## RQ

> **When only a handful of frequent token embeddings learn a translation task, where does their causal effect actually enter a decoder-only LM: through the task/source prefill, through generated-target feedback, or through both?**

## Mother phenomenon

NAACL 2025 KS-Lottery shows that for LLaMA-7B translation, tuning an ultra-small selected set of input-token embeddings can approach full/embedding tuning; in en→ca the strict set contains only 18 rows and achieves a very large gain. The selected rows are mostly high-frequency/function-like tokens.

Primary source: https://aclanthology.org/2025.naacl-long.458/

The parent owns **sparsity / winning-ticket selection / frequency**. L32 does **not** claim those as novelty.

## Missing inference

In a decoder-only LM, the same input embedding row may be read in different computational roles:

- instruction/template prefill;
- source-sentence prefill;
- generated-target autoregressive history.

Because LLaMA input embeddings are not tied to the LM head, the selected-row update cannot directly change output logits. The unresolved scientific question is therefore **which access route makes these few rows powerful**.

## Authorized E01

1. Reproduce the large parent en→ca sparse-tuning effect using the published 18 token IDs.
2. Keep one trained model and the same learned embedding deltas.
3. At inference selectively use base vs tuned rows by sequence segment:
   - BASE
   - ALL
   - INSTRUCTION
   - SOURCE
   - PREFILL = instruction + source
   - TARGET = generated/reference target history only
4. Evaluate both:
   - teacher-forced next-token log probability / accuracy on fixed target trajectories;
   - free-running Flores spBLEU.
5. Compare channel recovery relative to the ALL-vs-BASE sparse adaptation gain.

## First-stage gate

`spBLEU(ALL) - spBLEU(BASE) >= +15` on en→ca Flores devtest, same sign across 3 training seeds.

If this fails: **STOP.** No mechanism interpretation.

## Support gate

Before source-vs-target interpretation, verify the 18 selected IDs actually occur often enough in both source and reference-target spans. Require at least 250 Flores sentences with ≥1 selected-token occurrence on each side. Otherwise HOLD/redesign rather than interpreting no-opportunity as no causal role.

## Why not already owned

Closest components:

- Findings ACL 2024: embedding tuning / early layers activate multilinguality; vocabulary sharing matters.
- NAACL 2025 KS-Lottery: 18 frequent embedding rows suffice.
- Prefix Tuning: a few learned vectors can condition generation.
- decoder-only multilingual MT: source/target interaction matters.

But these do not identify whether KS-Lottery's sparse gain is carried by source reading, task-prefix conditioning, target-history feedback, or cross-phase reuse. KS-Lottery's own Prefix-Tuning baseline is substantially weaker than Partial Tuning, so “they are just 18 prompt vectors” is not an adequate existing answer.

## Strong-result meanings

- **TARGET dominant:** frequent tuned rows behave like recurrent control/state vectors re-injected during autoregressive generation.
- **SOURCE dominant:** a tiny set of context-anchor embeddings reconfigures source reading despite nearly all lexical rows being frozen.
- **INSTRUCTION dominant:** reinterpret the claimed multilingual ticket as primarily a task-conditioning interface.
- **Joint access required:** the update works through cross-phase reuse rather than a single static locus.

## Non-authorized

Do not yet do:

- 101-language sweeps;
- model-zoo expansion;
- new KS/PEFT method;
- generic probing / hidden-state atlas;
- “high frequency is causal” claims;
- full-paper C2/C3 experiments.

Full Selection record:

`search_rounds/2026-09-13_SPARSE_EMBEDDING_CHANNEL_SELECTION.md`


---

## E01 outcome (2026-09-13)

Gate `spBLEU(ALL) - spBLEU(BASE) >= +15`: **PASSED** at **+29.50**
[+28.59, +30.46], 3 seeds, Flores-101 devtest, reproducing the parent's en->ca
phenomenon. Full report: `notes/E01_REPORT.md`.

The channel question is answered decisively, and the answer rejects three of
Selection's four accounts:

| channel | recovery of the gain | 95% CI |
|---|---|---|
| INSTRUCTION | **1.00** | [0.98, 1.02] |
| SOURCE | **-0.00** | [-0.01, 0.01] |
| TARGET feedback | 0.05 | [-0.01, 0.09] |

Source occurrences are *more* frequent than instruction ones (7.73 vs 7.00 per
sentence) and recover nothing, so this is not an opportunity effect. A
norm-matched random delta on the same rows scores 0.05 spBLEU, and the gain does
not survive paraphrasing the instruction (+3.19 vs +29.18).

Two findings changed the paper identity:

1. **94% of the reproduced effect is termination, not translation.** Scoring
   only the first line of the continuation, the untuned model is at 33.99 and
   the tuned model at 35.71 -- `Delta_ALL` falls from +29.50 to +1.72
   [+1.03, +2.42]. The base model already translates and then does not stop.
   The pre-registered audit found base spBLEU spans **0.31-33.78** on this task
   as a function of prompt and post-processing alone.
2. **The ticket is a template key, not a capability locus.**

A follow-up probe of the selection procedure itself
(`notes/TICKET_SELECTION_PROBE.md`) is logged **EXPLORATORY**: its pre-declared
condition was mis-specified. At the parent's ticket size k=18, against a seed
noise floor of 18/18, rewording the prompt leaves 10/18 and switching language
leaves 10/18.

**Verdict:** E01 alone is a Findings-level correction. The Main-level path is
open but unproven and needs one pre-registered selection round
(`TICKET_SELECTION_PROBE.md` §6, under a GPU-day). C2 remains unauthorised.


---

## E02 outcome (2026-09-13) — `HOLD / Findings`

Preregistered in `notes/E02_PREREGISTRATION.md` before any run; full result in
`notes/E02_REPORT.md`. Question: *are multilingual winning tickets properties of
a language, or of the interface used to ask the model to translate?*

| layer | result |
|---|---|
| L1 cross-language evaluation audit | **PASS** 3/3 |
| L2 selection factorial + frequency control | **PASS** 18/18 |
| L3 functional cross-template transfer | **FAIL** (ratio 0.996) |

**L1.** Using the parent's own published Table 11 tickets, 94-107% of the
sparse-tuning gain is termination in all three pairs (ca 0.938, es 0.970, ro
1.070). For en->ro the translation content is *worse* after tuning while the raw
score rises 20 points.

**L2.** At the parent's ticket size, rewording the prompt destroys more of the
certified ticket (8.6/18 survive) than switching target language (11.6/18),
against a seed ceiling of 17.4/18 -- and the prompt arm is the controlled one.
Template tokens rank 7-11 while non-template tokens **matched on training count**
rank 84-372 (Wilcoxon p <= 1e-3, 18/18 cells). Frequency does not explain it.

**L3.** But tickets are functionally interchangeable across templates (0.996),
so the interface account does not extend from selection to function.

An added, non-preregistered control shows count-matched non-template rows
recover only 0.40-0.59, so ticket identity does matter; and across 8 runs,
whether the random ticket contained `<s>` separates 0.97-0.99 from 0.40-0.59
with no overlap. Not used to change the verdict.

**Conclusion:** a strong Findings paper -- the dissociation is that ticket
*selection* is an interface phenomenon while ticket *function* rests on a small
prompt-generic structural core. **Not** "multilingual tickets are prompt
artifacts", which L3 does not support.
