# L31 — What Selects a Factual-Recall Route?

**Status:** **KILL — K191 — SELECTION RECHECK FAILED (2026-09-13)**  
**Target:** ACL / EMNLP / NAACL Main

## Final disposition

L31 was briefly marked `PILOT-AUTHORIZED — E01 ONLY`, but that authorization is **revoked before compute** after a stricter successful-result and identification recheck.

> **Do not run E01. Do not reactivate this route by changing the geometry transform, localization metric, model family, or synthetic setup.**

## Original question

> What load-bearing condition determines whether a Transformer learns an Attention-centered or MLP-centered factual-recall computation?

The mother phenomenon was real: Choe et al. (EMNLP 2025 Main) showed substantial cross-model differences in factual-recall Attention/MLP causal organization, while Hochman et al. (ACL 2026 Main) showed that factual retrieval is distributed, redundant and non-contiguous.

The proposed causal axis was embedding geometry / MLP usability, motivated by work showing that Attention and MLP can both act as factual associative memories and that embedding geometry strongly changes MLP fact-storage capacity/usability.

## Why the pilot authorization was wrong

### 1. The geometry intervention is not selective

The proposed manipulation changes the same representation geometry seen by Attention, MLPs, the residual stream and final readout. Therefore even a clean route shift would not identify the intended chain:

`geometry -> MLP usability -> route selection`.

Attention learnability/retrieval geometry is altered by the treatment as well. A positive result would therefore not isolate MLP usability as the cause of route switching.

### 2. Making the intervention selective makes the result close to predetermined

One could insert an artificial transform only on the MLP path, but then the scientific result becomes roughly:

> make one known-capable memory substrate harder to use -> optimization relies more on another known-capable substrate.

Nichani et al. already establish that Attention and MLP can trade off as factual associative memories. Dugan/Garcia-style work establishes how geometry changes MLP usability. Combining the two into a synthetic substitution experiment is not a sufficiently new Main-level inference.

### 3. `Attention-centered vs MLP-centered` is too coarse / protocol-sensitive

Choe already reports intervention-dependent differences between restoration and severing/knockout. Hochman et al. show multiple functionally equivalent factual-retrieval paths. Thus a scalar module-level reliance contrast is not obviously a stable intrinsic computational regime.

Later geometric-memory work further expands the mechanism space beyond an Attention-vs-MLP binary: facts may be represented in embedding geometry while modules implement routing/selection. The proposed object is therefore too coarse to bear the intended causal law.

### 4. Strongest successful E01 is below the Main bar

Even the ideal result would largely say:

> when one available factual-memory substrate becomes harder to use, a Transformer shifts burden to another available substrate.

That conclusion is too predictable from the closest components and is vulnerable to the reviewer compression:

> `Attention/MLP are substitutable fact memories + geometry changes MLP usability = observed substitution`.

The missing exact experiment is not enough; the answer is already substantially implied by the neighboring work.

### 5. Synthetic E01 does not explain the natural mother

The natural anomaly is cross-family factual-recall organization in pretrained LLMs. A small synthetic geometry intervention would only show route flexibility in a controlled toy regime. Bridging that result back to Qwen/LLaMA-style natural differences would still require a large and confounded research program.

## Final failure codes

- **IDENTIFICATION FAILURE** — treatment changes more than the proposed MLP first stage.
- **CONSTRUCT FAILURE** — Attention-vs-MLP reliance is not clearly a stable intrinsic regime under redundant paths.
- **SUCCESSFUL-RESULT / PAPER-SCALE FAILURE** — ideal positive result is largely implied by closest components.
- **GROWTH-PATH FAILURE** — synthetic causal result is too far from explaining the natural mother phenomenon.

## Anti-resurrection

Do not revive as:

- `geometry chooses Attention vs MLP` with a different transform;
- selectively degrading one module and measuring compensation;
- another factual-memory localization metric study;
- another model-family Attention/MLP comparison;
- another synthetic `which substrate wins?` experiment;
- generic factual-memory route switching.

A future idea about factual memory must introduce a qualitatively different scientific object and survive selection from scratch.

## Durable lesson

Before pilot authorization, apply one additional reviewer-compression test:

> **If the bounded E01 succeeds perfectly, is the conclusion still substantially non-obvious after combining the closest component papers?**

`No one has run this exact intervention` is insufficient when the successful answer is already a natural consequence of known components.
