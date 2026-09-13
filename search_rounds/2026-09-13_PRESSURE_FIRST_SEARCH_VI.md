# 2026-09-13 — Pressure-First Search VI

Continuation after L33 selection. This round deliberately searches for a **second scientific object independent of agreement attraction**, rather than manufacturing portfolio breadth with neighboring linguistic interference phenomena.

Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## Hook P21 — Moses illusion: anomaly not detected, or detected but overridden by schema completion?

**Status:** `DROP / NEW PHENOTYPE + EXISTING TRUTH-STATE INSTRUMENT`

### Pressure

Semantic-illusion work gives a stable failure: a model can answer the stereotypical question while accepting a locally incorrect entity/premise. The classic human debate distinguishes incomplete/partial matching from detecting the anomaly but failing to suppress the dominant schema.

### Why it dies

By 2026, causal contextual-truth work already distinguishes surface agreement/accommodation from internal proposition truth state and provides steering/intervention tools. Applying that instrument to Moses-style items would be another `new behavioral phenotype + existing truth-state instrument` paper rather than a fresh computational parent.

### Anti-resurrection

Do not reopen as `does the model secretly know Moses is wrong`, `semantic illusion is late override`, or `hidden truth vs stereotyped answer` without a new estimand beyond contextual truth-state use.

---

## Hook P22 — Why do generated-token hidden states form a better prompt representation than prompt tokens?

**Status:** `DROP / PARENT ALREADY RULES OUT SIMPLE DENOISING AND MAPS REPRESENTATIONAL PHASES`

### Pressure

ICML 2026 reports that averaging hidden states from tokens generated after a prompt can encode the input semantics better than any single prompt-token state, across language, vision and proteins. A tempting explanation contrast is true iterative semantic reconstruction versus averaging multiple noisy copies.

### Why it dies

The parent already performs segment, trajectory, sampling-seed and mixing analyses showing that different generated regions carry complementary information rather than merely redundant noisy copies. It also studies injection/representation phases. The remaining `self-generated content vs extra computation` distinction is a narrow refinement inside the parent's own mechanism program.

### Anti-resurrection

Do not reopen as `generation is just semantic denoising`, `mean pooling generated states works because of redundancy`, or a generic generated-state embedding mechanism paper.

---

## Hook P23 — Attention sinks: meaningless no-op mass or functional global broadcast?

**Status:** `DROP / DIRECT CONDITIONAL-LAW OWNER`

### Pressure

A widely repeated explanation treats sink attention as excess mass parked on a token to approximate a no-op. A competing account is that sink positions can aggregate/broadcast useful global state.

### Why it dies

2026 *A Unifying View of Attention Sinks: Two Algorithms, Two Solutions* directly distinguishes the same visible attention pattern into two mechanisms — adaptive no-op and broadcast/global-information aggregation — and gives diagnostics/interventions based on value/output structure. The attractive premise has already been converted into a conditional law.

### Anti-resurrection

Do not reopen generic `what do attention sinks do`, `sink = garbage vs global state`, or `high attention sink may be useful`.

---

## Hook P24 — Is token-average versus example-average SFT a hidden explanation for long-reasoning supervision?

**Status:** `DROP / CONFOUND NOT CLEAN ENOUGH + RECIPE RISK`

### Pressure

Standard losses can weight variable-length samples differently, suggesting a possible hidden supervision-mass confound behind claims that long chains teach more than short ones.

### Why it dies

The simplistic form does not survive implementation scrutiny: in separate long/short training arms, ordinary CE is already normalized over valid tokens in each batch, so longer sequences do not simply receive proportionally larger whole-step weight. The meaningful token-vs-example distinction applies to relative weighting inside heterogeneous mixtures. Existing long-CoT work already analyzes token budget, capacity, error accumulation and token-level reweighting. Without a sharper scientific law this becomes a loss-normalization recipe.

### Anti-resurrection

Do not reopen as `long CoT only works because it has more loss tokens` or generic sequence-average vs token-average SFT.

---

## Hook P25 — Why do high-norm semantic vectors work in frozen decoders?

**Status:** `DROP / DIRECT MECHANISM COMPRESSION BY ICLR-2026 PRE-NORM INERTIA`

### Pressure

ACL 2026 *Frozen LLMs are Native Decoders for High-Norm Semantic Vectors* finds that learned continuous semantic vectors can have L2 norms roughly two orders of magnitude above ordinary embeddings, and shrinking the norm destroys frozen-LLM reconstruction. The parent explicitly leaves ambiguity between attention dominance, low-norm suppression, or both.

A particularly attractive observation is that in pre-RMSNorm decoders, raw residual magnitude is normalized before each attention/MLP branch. The parent's own layer statistics show enormous raw landmark hidden-state norm at layer 0 without a corresponding first-layer Q/K/V norm explosion; attention dominance emerges later.

This suggested the account:

> **high norm does not act as a directly visible attention beacon; it reduces the relative size of each normalized residual-block update, preserving the semantic vector direction through depth.**

An exact scale-equivariant intervention was available: initialize the semantic state at `αv` and scale every residual write at that position by `α`. Under ideal pre-RMSNorm homogeneity this preserves the normalized trajectory while keeping raw norm low, cleanly separating raw magnitude from residual-update dynamics.

### Why it dies

ICLR 2026 *The Unseen Bias: How Norm Discrepancy in Pre-Norm MLLMs Leads to Visual Information Loss* already formalizes the same mechanism under a different continuous-token source. Its central theory is an **asymmetric update dynamic / representational inertia**:

- pre-norm branch updates are comparatively insensitive to the incoming raw token norm;
- angular/semantic update rate scales inversely with token norm;
- high-norm continuous tokens therefore change direction much more slowly through depth;
- the paper validates this across mainstream MLLMs and causally intervenes via norm alignment.

Its theory can be summarized as `angular velocity ∝ update magnitude / token norm`, which directly predicts the proposed semantic-vector persistence account.

Therefore the strongest reviewer compression succeeds:

> `ACL-2026 establishes that high-norm semantic vectors are necessary + ICLR-2026 already proves high norm in pre-norm residual streams causes representational inertia = L34's explanation.`

The proposed scale-equivariant residual-write experiment would be a very clean confirmation/application of an already-owned general mechanism, not an independent Main-level scientific answer. Its near-algebraic character further weakens uncertainty: once pre-norm scale invariance is stated, the rescue is close to constructively implied.

### Anti-resurrection

Do not reopen as:

- `why does norm matter after RMSNorm?`;
- `high-norm semantic vector = protected state`;
- `semantic vectors work through smaller effective residual step size`;
- `scale semantic vector and scale residual updates`;
- `attention beacon vs representational inertia`.

A future norm-based candidate would need a **different causal quantity that the ICLR-2026 representational-inertia theory does not predict**.

---

# Round state

L33 remains the only new survivor from this search round so far. Mainline remains NONE. Open-ended search continues; do not treat one bounded pilot as a reason to stop.