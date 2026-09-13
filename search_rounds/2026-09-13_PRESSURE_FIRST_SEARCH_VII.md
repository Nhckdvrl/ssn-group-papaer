# 2026-09-13 — Pressure-First Search VII

Continuation after `PRESSURE_FIRST_SEARCH_VI.md`. The purpose of this round is still to find a **second scientific object independent of L32/L33**, not to manufacture breadth. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

Search doctrine remains:

> **scientific pressure first → decisive matched/stress test → phenomenon second**

This log records routes that looked plausible enough to deserve owner assassination, but did not survive Selection-level scrutiny.

---

## Hook P26 — Lexical ambiguity: context rewrites the ambiguous token, or preserves multiple meanings until readout?

**Status:** `DROP / CAUSAL REPRESENTATION PROGRAM ALREADY ACTIVE`

### Pressure

A classic semantic-processing distinction asks whether context resolves an ambiguous word by changing the word representation itself or whether multiple candidate meanings remain available and downstream computation selects among them.

This initially looked like a good Type-D question: a mature linguistic distinction plus a modern same-checkpoint causal graph.

### Why it dies

By 2026, lexical/idiomatic ambiguity work already combines layerwise representation analysis with activation patching / causal tracing to distinguish competing literal and non-literal interpretations. The remaining proposal would be reviewer-compressible as another ambiguity phenotype plugged into an existing causal-representation program, rather than a new computational parent.

### Anti-resurrection

Do not reopen generic `context rewrites word sense vs late readout`, `does the model retain both senses`, or `patch the ambiguous-token representation` without a new estimand beyond causal sense representation.

---

## Hook P27 — Implicit causality: focusing or integration inside an autoregressive LM?

**Status:** `DROP / OLD THEORY + ALREADY-MEASURED ANTICIPATION + CAUSAL NEURON WORK`

### Pressure

Human psycholinguistics has long contrasted accounts in which implicit-causality verbs proactively focus an expected referent against accounts in which the bias mainly enters during later integration.

### Why it dies

GPT-2-era work already established anticipatory implicit-causality effects in next-token surprisal, and 2025 causal-neuron work directly manipulates implicit-causality-related internal units. A new path cut would refine localization, but the strongest result is too close to `old phenomenon + existing causal instrument`.

### Anti-resurrection

Do not reopen as `does implicit causality act before the pronoun`, `focus vs integrate with patching`, or another IC-neuron localization study.

---

## Hook P28 — Why can RMSNorm omit mean-centering?

**Status:** `DROP / DIRECT 2026 GEOMETRIC OWNER`

### Pressure

LayerNorm explicitly removes the mean along the uniform-vector direction, whereas RMSNorm does not. Modern LLMs nevertheless overwhelmingly use RMSNorm. A clean structural question was whether trained representations make the missing mean-removal operation redundant.

### Why it dies

EACL 2026 Findings, *Geometric Interpretation of Layer Normalization and a Comparative Analysis with RMSNorm*, explicitly makes this geometric decomposition and finds that trained LN/RMSNorm models naturally operate close to the subspace orthogonal to the uniform direction. The proposed `remove the uniform component and test the same checkpoint` experiment would only reconfirm its mechanistic conclusion.

### Anti-resurrection

Do not reopen `why RMSNorm works without centering`, `uniform-vector component is unused`, or `centering is redundant in modern LMs`.

---

## Hook P29 — Why does SwiGLU / gated MLP outperform an ordinary FFN?

**Status:** `DROP / DIRECT THEORY AND MODERN GATED-MLP OWNERS`

### Pressure

SwiGLU became a near-default modern LLM choice despite its original adoption being primarily empirical. This is exactly the kind of structural default that should be questioned.

### Why it dies

2026 work now directly studies why GLU-style structures outperform non-GLU alternatives through optimization / conditioning analyses, while other 2026 work develops explicit mathematical interpretations of gated MLPs and tools for analyzing the two multiplicative branches. Generic `why SwiGLU works`, `gate vs up pathway`, or `gating creates better memories` is therefore no longer an open parent.

### Anti-resurrection

A future gated-MLP candidate must name a different causal quantity not implied by GLU optimization theory or modern gate/up analyses.

---

## Hook P30 — Does the classic “FFN = key–value memory” law survive SwiGLU?

**Status:** `DROP / OLD-LAW UPDATE ALREADY OWNED`

### Pressure

The influential key–value-memory interpretation of Transformer FFNs was developed for ordinary two-layer MLPs, while LLaMA/Qwen/Gemma use multiplicative gated MLPs. This initially looked like an ideal `old law → changed architecture` route.

### Why it dies

Recent work explicitly analyzes gated MLPs as fact-storing / associative-memory structures and develops formal constructions for SwiGLU/ReGLU fact storage. Additional 2026 work interprets gated MLPs as bilinear-attention-like computation. Thus the architecture change has already been incorporated into the memory/mechanism literature.

### Anti-resurrection

Do not reopen generic `does FFN-as-memory still apply to SwiGLU`, `which branch is key/value`, or `gate vs up factual storage`.

---

## Hook P31 — Why is QK-Norm needed in modern LLMs?

**Status:** `DROP / CORE STABILITY MECHANISM ALREADY OWNED`

### Pressure

QK-Norm has become a common stability choice. A structural-default question was whether it does more than control the scale of dot-product logits.

### Why it dies

The original QK-normalization motivation already targets uncontrolled attention-logit / softmax saturation, and 2025–2026 work directly connects Q/K weight growth, attention-logit drift and stability. Generic `why QK-Norm works` is therefore already mechanistically constrained enough that another same-checkpoint intervention would be a refinement, not a fresh scientific parent.

### Anti-resurrection

Do not reopen as `QK-Norm prevents saturation`, `Q/K norms cause training instability`, or generic attention-temperature stabilization.

---

## Hook P32 — Ellipsis: copy/reconstruct the missing phrase, or keep a pointer to the antecedent?

**Status:** `DROP / BEAUTIFUL THEORY, BAD FIRST STAGE + NO SELECTIVE OPERATION`

### Pressure

Human VP-ellipsis processing has a classic and intuitive dispute. In a sentence like `Alice praised Bob and Carol did too`, copy/reconstruction accounts posit local reconstruction of the omitted predicate, whereas direct-access accounts posit a pointer-like retrieval of the antecedent representation. Human speed–accuracy / antecedent-complexity evidence strongly motivated direct-access accounts.

This is exactly the kind of long-standing A/B we want in principle.

### Why it dies

Two blockers are fatal for a bounded E01:

1. Existing LM ellipsis work reports weak and uneven performance outside the simplest ellipsis cases, so the mother is not sufficiently guaranteed on a pre-specified open model.
2. In a causal Transformer, `local state contains a compressed reconstruction` and `local state contains a retrieval pointer that is later used` cannot be cleanly separated by a simple mask/patch: blocking later antecedent access changes the computation needed by both plausible implementations, while patching an antecedent-derived state risks injecting the answer.

This would require inventing the phenotype and the identifying instrument simultaneously.

### Anti-resurrection

Do not reopen as `does an LLM copy the VP`, `ellipsis uses a pointer`, or `mask antecedent access after the ellipsis site` unless a genuinely selective operation appears.

---

## Hook P33 — GQA: what are extra KV groups actually buying?

**Status:** `DROP / CLEAN INTERVENTION, BUT SCIENTIFIC OWNERSHIP COMPRESSED BY GQA GROUPING LITERATURE`

### Pressure

Grouped-query attention preserves many query heads while heavily sharing keys and values. The tempting scientific question is whether each extra KV group contributes a distinct address space (K), a distinct payload (V), or merely redundant capacity. A native GQA checkpoint admits clean `K-swap / V-swap / KV-swap` group interventions.

### Why it dies

The 2024–2026 GQA literature is already dense around exactly the load-bearing premise: which query heads should share which KV projections and how much Q/K/V homogeneity exists. Asymmetric GQA, quality-aware grouping, weighted GQA, key-driven grouping and 2026 graph-based query clustering all exploit or directly analyze non-uniform head/group similarity; the 2026 clustering work explicitly investigates homogeneities among queries, keys and values.

Therefore even a clean K-vs-V decomposition is reviewer-compressible as a more detailed explanation of a redundancy structure that current GQA compression work already operationalizes. The strongest successful result is unlikely to establish a new Main-level model-science law.

### Anti-resurrection

Do not reopen generic `why GQA works`, `KV heads are redundant`, `query diversity matters more than KV diversity`, or `which Q should pair with which KV`.

---

## Hook P34 — Does self-attention need the diagonal when the residual stream already carries the current token?

**Status:** `DROP / DIRECT REMOVE-DIAGONAL OWNER + METHOD FRAMING`

### Pressure

A causal decoder lets token *t* attend to itself even though the residual connection already carries its current representation. That makes the attention diagonal look like a potentially redundant structural default.

### Why it dies

2025 *You Might Not Need Attention Diagonals* directly studies discarding self-attention diagonal entries and frames diagonal self-attention as over-self-confidence. More importantly, the obvious next step becomes an architecture/masking recipe rather than an unresolved high-leverage model-science question.

### Anti-resurrection

Do not reopen generic `residual makes self-attention diagonal redundant`, `remove self-loop`, or `what does diagonal attention do`.

---

## Hook P35 — Is a “Super Weight” a property of the function, or of the coordinate system?

**Status:** `DROP / FUNCTION-PRESERVING ROTATION LITERATURE ALREADY ESTABLISHES COORDINATE-DEPENDENT PARAMETER IMPORTANCE`

### Pressure

The Super Weight result is unusually strong: pruning one scalar can catastrophically destroy generation. A 2026 follow-up adds a useful contradiction: parameters that are extraordinarily important under pruning are nevertheless poor targets for selective training.

A deeper candidate question was:

> **Is `this scalar is uniquely super` an invariant property of the learned function, or only a privileged coordinate representation of a lower-dimensional functional bottleneck?**

Modern pre-norm Transformers admit function-preserving orthogonal reparameterizations, so this looked amenable to a decisive same-function test rather than another correlation study.

### Why it dies

The 2025 DenoiseRotator line already exploits exactly the relevant fact: it inserts/merges orthogonal transformations using Transformer computational invariance and **redistributes parameter importance across coordinates while preserving model outputs**, explicitly to make pruning easier. This does not use the Super Weight terminology, but it collapses the proposed strongest claim.

Reviewer compression is immediate:

> `Super Weight establishes catastrophic scalar pruning sensitivity + DenoiseRotator already shows function-preserving rotations can redistribute parameter importance = scalar-level “superness” is not a coordinate-invariant scientific object.`

An experiment rotating away a super weight would be a striking demonstration, but the answer is already implied by the two owners and by the symmetry itself.

### Anti-resurrection

Do not reopen as `rotate away the super weight`, `super weight is coordinate artifact`, or `find the invariant direction behind a super weight` unless a new invariant causal quantity is identified that DenoiseRotator-style reparameterization does not already imply.

---

## Pressure only — Scalar implicature as online alternative construction vs learned enriched mapping

**Status:** `PRESSURE ONLY — NOT SELECTION / NO COMPUTE`

Question:

> **When `some` is interpreted as `not all`, does the model online construct and exclude the stronger alternative `all`, or has the enriched mapping effectively become a learned/default interpretation?**

Why the pressure is real:

- the default/literal-first/constraint-based debate is old and theoretically meaningful;
- human work continues to find context-sensitive stronger-alternative activation;
- LLM work has behavioral evidence and activation steering, but this is not yet the same as identifying online alternative construction.

Why it is **not** a candidate:

No selective E01 has been found. Erasing/patching an `all`-like direction removes semantic content and does not specifically block the *operation of generating an alternative*. Nonce-scale or contextual-alternative manipulations can establish contextual sensitivity but do not distinguish online exhaustification from a context-conditioned learned mapping. Until the operation identifies the theory, this stays outside Selection.

Do not promote it merely because the theory question is attractive.

---

## Additional route rejected before full card — Complement coercion / logical metonymy

`John began the book` raises a good semantic question: is a covert event compositionally constructed or retrieved from lexical/world associations? Recent LLM work exists, but CoNLL 2025 reports that tested models struggle to retrieve plausible covert events and fail to exploit the compositional properties of coercion sentences reliably. That makes the mother itself a bet. Under the current doctrine, do not launch a mechanism paper that first needs the competence phenomenon to appear.

---

# Round state

**New survivor in this continuation: 0.**

Current portfolio therefore remains:

- L32 — `PILOT-AUTHORIZED — E01 ONLY`;
- L33 — `PILOT-AUTHORIZED — E01 ONLY`;
- L17 — existing speech project;
- Mainline — **NONE**.

The strongest lesson from this continuation is not to confuse a clean causal operation with an open scientific question. RMSNorm, SwiGLU, GQA and Super Weight all produced unusually clean interventions, but owner compression still killed them. Conversely, scalar implicature and VP ellipsis produced genuinely live theoretical pressure, but no selective identifying operation. Both failure modes are reasons to withhold authorization.
