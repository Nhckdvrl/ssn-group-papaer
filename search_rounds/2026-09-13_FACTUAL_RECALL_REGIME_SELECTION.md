# 2026-09-13 — Factual-Recall Route-Selection Selection Audit

**Candidate:** `L31 — What Selects a Factual-Recall Route?`  
**Final status:** **PILOT-AUTHORIZED — E01 ONLY**  
**Package:** `candidates/L31_FACTUAL_RECALL_ROUTE_SELECTION/`

## Research question

> **What load-bearing condition determines whether a Transformer learns an Attention-centered or MLP-centered factual-recall computation?**

The paper identity is computational-regime selection, not localization.

## Mother phenomenon

Choe et al. (EMNLP 2025 Main) establish cross-model Attention-vs-MLP factual-recall diversity across 17 autoregressive Transformers and rule out several obvious one-factor explanations. Hochman et al. (ACL 2026 Main) independently establish distributed, redundant and non-contiguous factual-retrieval paths, making protocol robustness a required construct-validity gate.

Mother verdict: **PASS**. The project does not depend on first discovering mechanism diversity.

## Pre-specified causal axis

The selected axis is embedding geometry / MLP usability.

Nichani et al. (ICLR 2025) prove that Attention and MLPs can both implement associative factual memory and trade capacity. Dugan et al. (2025) and Garcia et al. (2026) show that embedding geometry / decoding margin strongly controls MLP storage capacity and Transformer usability.

The causal hypothesis is therefore pre-result:

> degrading the usability of the MLP memory substrate should move factual-recall causal burden toward Attention when both routes are free to learn; improving MLP usability should move burden toward MLP.

This avoids the forbidden `try architecture knobs until one works` strategy.

## Ownership / reviewer compression

Strongest compression:

> `Choe factual-route diversity + Nichani Attention/MLP memory tradeoff + Dugan/Garcia MLP geometry/usability = L31`.

The compression does not establish the central missing inference: none of the closest work allows both routes to compete freely while causally manipulating the usability of one substrate and measuring whether the learned route changes.

The constructive-MLP work deliberately freezes/constrains alternative attention storage to isolate MLP usability. Thus it cannot answer route selection.

Direct owner search through 2026-09-13 found no paper owning the exact `geometry/usability → freely learned Attention-vs-MLP route` causal test.

**Novelty:** `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

## Identification

E01 uses matched small factual-recall Transformers with identical task/data/architecture/training budget and changes only a predeclared embedding-geometry intervention grounded in prior work.

Required first stage:

1. geometry manipulation must materially move the intended MLP-usability quantity in the predicted direction;
2. otherwise stop before route comparison.

Required route construct:

- two orthogonal causal measurements must agree directionally;
- direct factual behavior is the endpoint;
- probes/activation magnitude alone do not count.

This directly incorporates the L29/K190 first-stage lesson and Hochman et al.'s redundant-path warning.

**Identification:** `PASS FOR PILOT`.

## Outcome map

- usability changes + route shifts predicted direction: supports causal route-selection account; return to SELECT for C2/C3.
- usability changes + route does not shift: kill determinant hypothesis; no factor fishing.
- usability first stage fails: instrument failure; bounded repair only.
- causal route metrics disagree: construct unstable; kill/hold before natural-model expansion.

No result authorizes changing the paper identity after the fact.

## Resolution / feasibility

E01 is shallow synthetic factual-recall training, not billion-parameter pretraining. Multiple seeds and several geometry conditions are feasible. Prior work reports large capacity/usability changes under the selected geometry manipulation, so the first-stage signal is expected to be well above the L19-style resolution floor.

**Resolution:** `PASS FOR PILOT`.

## Main-level path

E01 alone is not Main-scale. If it passes, the coherent growth path is:

1. controlled causal route switch;
2. predict natural pretrained-model route differences from the same scientific quantity;
3. controlled training manipulation that moves the quantity and switches regime;
4. one consequential implication for factual localization/editing assumptions.

The target final statement is a conditional law:

> **Transformers have multiple viable factual-memory computations, and substrate usability/geometry helps select which one training converges to.**

C2/C3 require re-selection.

## Final authorization

> **PILOT-AUTHORIZED — E01 ONLY**

Authorized: small matched factual-recall training experiment, predeclared embedding-geometry manipulation, first-stage MLP-usability check, multiple seeds, two causal route measurements.

Not authorized: natural-model zoo, broad factor sweeps, knowledge editing, full paper program, or post-hoc alternative determinants.
