# L32 — Where Do 18 Embeddings Work?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
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
