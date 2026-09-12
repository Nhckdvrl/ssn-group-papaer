# 2026-09-13 — Live Search After K191

**Purpose:** persistent rolling log for the current search round so network interruption does not cause repeated rediscovery. Any seriously investigated dead route is recorded here immediately.

**Rule:** only `PILOT-AUTHORIZED` candidates are surfaced as actionable topics. `MAYBE` / `SERIOUS` / blocked ideas stay internal and are either killed or fully selected before user-facing promotion.

---

## Hook A — Final-layer hidden-state angular jump

**Status:** `DROP / OWNER COLLISION — DO NOT REDISCOVER THIS ROUND`  
**Origin:** Shibata et al., Findings EACL 2026, *Suppressing Final Layer Hidden State Jumps in Transformer Pretraining*.

Observed mother phenomenon:
- many open-weight Transformer LMs show small angular displacement through middle layers but a disproportionately large jump at/near the final layer;
- the jump grows over pretraining/checkpoints;
- jump-suppressing regularization (JREG) reduces the phenomenon and modestly improves downstream performance;
- the parent interprets the jump as possible over-reliance on final layers / under-utilization of middle layers, but does not directly establish why this late reconfiguration emerges.

Primary source: https://aclanthology.org/2026.findings-eacl.64/

### Owner assassination result

The natural mechanism question — why computation remains relatively quiet/off-readout in the body and changes abruptly near the end — is no longer open enough.

1. **Oskin 2026, *Off-Axis, On Purpose: Where a Transformer Computes Concepts and Why it Does So*** directly studies why intermediate computation is held away from the vocabulary readout and why the answer arrives late. In a controlled 12-layer Transformer, attention writes remain strongly off the unembedding/readout direction through depth; forcing attention onto the readout is 64–84x more damaging than matched random rotations, specifically through cross-token mixing. In the late phase, the FFN writes the answer on-axis by addition. This supplies a direct functional account for late representational commitment rather than merely observing late-layer specialization.
   - https://arxiv.org/abs/2608.10251
2. **Queipo-de-Llano et al., ICLR 2026, *Attention Sinks and Compression Valleys in LLMs are Two Sides of the Same Coin*** already proposes a causal/theoretical `Mix → Compress → Refine` depth organization, with late layers performing selective refinement after a compressed middle phase.
   - https://proceedings.iclr.cc/paper_files/paper/2026/hash/1734b19d9afe7d2c7f1154954eaf0d5a-Abstract-Conference.html
3. **Bhattacharya & Kolli 2026, *An Analysis of Residual-Stream Geometry Across Transformer Depth*** independently reproduces a quiet-middle / strong-late transition across six instruction-tuned models and finds Procrustes residual peaking at the final transition. It explicitly remains descriptive, but it makes the geometry itself a current named object.
   - https://arxiv.org/abs/2607.18348
4. **Guda 2026, *Geometric and Behavioral Stratification in Transformer Residual Streams*** identifies the unembedding prediction direction as a narrow privileged readout interface across 18 models and causally separates prediction-proximal from prediction-distal residual structure.
   - https://arxiv.org/abs/2608.12447

### Strongest reviewer compression

> `Shibata: final angular jump + Oskin: functional off-axis workspace / late on-axis answer writing + ICLR Mix-Compress-Refine + 2026 residual-stream geometry = your explanation.`

The exact numerical identity between Shibata's angular-jump metric and Oskin's late on-axis write is not directly proven, but establishing that bridge would mostly align two already-owned descriptions rather than create a sufficiently new model-science inference. A study that only decomposes JREG/jump into readout-aligned vs orthogonal components is therefore too close to successor mechanism work.

### Verdict

**DROP.** Do not promote `why does the final layer jump?`, `jump = late readout commitment`, or `is JREG smoothing delayed commitment?` as a new candidate unless a qualitatively different contradiction emerges. Current space is too owned for the Main bar.
