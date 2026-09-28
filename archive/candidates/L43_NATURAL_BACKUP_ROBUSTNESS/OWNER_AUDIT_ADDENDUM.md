# L43 Owner Audit Addendum — Nainani / CoAx overlap

**Date:** 2026-09-15  
**Status impact:** L43 remains `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.

This addendum records the strongest reviewer compression found after the initial selection document was committed.

## Strongest adjacent result

Nainani et al., *Adaptive Circuit Behavior and Generalization in Mechanistic Interpretability* (arXiv:2411.16105) already tests the exact `DoubleIO` / `TripleIO` stress families proposed for L43 E01.

Their full-model circuit rediscovery finds:

- canonical IOI Name Mover heads remain causally important on DoubleIO / TripleIO;
- no other individual head has a sufficiently large direct causal effect to justify adding a new Name Mover head;
- the new circuits reuse all base IOI nodes and add input edges for duplicated IO tokens;
- the paper also discovers `S2 Hacking`, a mechanism that appears in the knockout circuit but **not** in the intact full model, demonstrating that an intervention can manufacture an apparently adaptive mechanism.

This is substantially closer to L43 than a generic `circuit generalization` citation.

## Why this does not yet own L43

Nainani's negative statement about additional Name Movers is based on **individual / first-order direct causal effects** during circuit rediscovery.

The central empirical fact motivating CoAx is precisely that redundant backups can be invisible to intact-state first-order saliency: the published IOI backup heads score poorly individually on the intact canonical model and become visible only conditionally after the primary set is removed. CoAx's 2026 headline is a change from about `0.33` to `0.91` backup ROC-AUC when replacing ordinary single-ablation scoring with conditional co-ablation.

Therefore Nainani establishes a strong prior:

> **If natural backup recruitment exists on DoubleIO / TripleIO, it is not obvious as a new individually dominant Name Mover.**

But it does not test the L43 estimand:

> **whether the already-defined CoAx backup set becomes jointly / selectively necessary in the intact model under answer-preserving input stress, relative to BASE and to matched ordinary late heads.**

L43 E01's preregistered set-level ablation and matched-control interaction are specifically designed to test a redundancy signal that a greedy first-order circuit finder can miss.

## CoAx template-robustness result

CoAx itself reports that backup-recovery AUC remains high when the *conditional primary-ablation experiment* is rerun on alternative IOI surface templates (reported approximately `0.96` and `0.88`, versus `0.91` on the headline template).

This is **not** natural recruitment. The primary circuit is still internally ablated before backup importance is measured. It establishes that the *counterfactual backup relationship* is not tied to one surface wording.

## Updated dangerous reviewer compression

> `Nainani already discovers DoubleIO/TripleIO circuits and sees no new Name Movers; CoAx already shows the backup set is stable across prompt templates. What remains?`

Answer:

> **Those two results constrain opposite sides of the same missing bridge. Nainani says no new head is individually salient in the intact stressed model; CoAx says a known backup set is invisible to first-order intact saliency but wakes under artificial internal failure. Neither measures whether that same redundancy becomes jointly load-bearing in an intact stressed model.**

That bridge is the L43 scientific claim.

## Updated risk assessment

L43 is **not low-risk novelty**.

The project should be killed after E01 if the only result is:

- canonical heads remain important;
- backup-head attention changes descriptively;
- another prompt-specific circuit diagram;
- or a weak set-ablation effect that cannot beat the BASE-matched control.

The candidate survives only because its central quantity is a **set-level natural recruitment interaction for a previously intervention-defined backup set**. Losing that distinction collapses the work into Nainani + CoAx.