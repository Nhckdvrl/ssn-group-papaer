# L42 — E00 Pre-Pilot Instrument Audit

**Status:** mandatory before any E01 GPU sweep.  
**Parent candidate:** `L42 — Does Scale Reward Syntax?`  
**Purpose:** remove avoidable replication / construct / scale-axis ambiguity before spending the authorized E01 budget.

L42 is already `PILOT-AUTHORIZED — E01 ONLY`. This file does **not** reopen Selection and does not authorize any additional experiment. It records blockers discovered after registration that must be resolved before interpreting E01 scientifically.

---

## E00.1 — Resolve the published-paper vs public-code training recipe

There is a real provenance mismatch.

The NAACL 2025 paper Appendix F describes the BLLIP-LG scratch setting as approximately:

- 16 layers;
- batch size 160;
- learning rate `1e-4`;
- 100,000 training steps;
- warm-up followed by cosine decay to zero.

The authors' public GitHub README says that the provided BLLIP-LG command was used for training and specifies:

- 16 layers;
- effective batch size 160 (`32 × 5` accumulation);
- `max_train_steps=60000`;
- `start_lr=1e-4`;
- `end_lr=6e-5`;
- TreeReg every 10 LM steps;
- layer 12;
- 25% of attention heads.

The 60k command is present in the repository's first public README commit; it is not a recent third-party modification.

### Rule

Do **not** call the 60k public command and the 100k paper recipe the same `parent setup`.

Before Phase A, choose and freeze one **reference protocol**:

- **Paper-reference route:** reconstruct the paper's 100k schedule closely enough to claim paper replication; or
- **Code-reference route:** reproduce the official public 60k command and treat the resulting 16L TRUE/RANDOM/BASE contrast as the local reference effect.

If using the code-reference route, the published `~8.2 pp` TRUE-vs-RANDOM point estimate is context, **not a frozen replication target** until the 60k recipe itself reproduces a comparable effect.

No post-result switching between 60k and 100k to rescue the phenomenon.

---

## E00.2 — Resolve BLLIP-LG access and exact split identity

The TreeReg public code hard-codes Stanford internal paths for:

- BLLIP-LG trees;
- the vocabulary object.

The MIT `cpllab/syntactic-generalization` repository explicitly states that BLLIP training data cannot be redistributed because of copyright. It gives exact instructions for reconstructing the Hu et al. 2020 BLLIP-LG train/dev/test splits from `LDC2000T43`.

### Rule

Before launching E01, verify that the licensed BLLIP corpus is actually available and reconstruct the exact Hu et al. split.

If exact BLLIP-LG cannot be obtained, **HOLD E01**. Do not silently replace it with WikiText, PTB, another WSJ subset, or an auto-parsed public corpus and continue calling the run a parent replication.

A substitute corpus would require a fresh Selection audit because both the parent effect and the scientific scale interaction could change.

---

## E00.3 — Tighten what RANDOM identifies

The NAACL parent generates randomized parses recursively by choosing random split points for each sentence span.

This preserves sentence length but does **not** guarantee matching of:

- tree depth distribution;
- branching balance;
- constituent-span length distribution;
- regularizer difficulty.

Therefore

`A(d) = SG_TRUE(d) - SG_RANDOM(d)`

should initially be described as:

> **matched-vs-random structural-constraint advantage**

rather than as a fully isolated `linguistic alignment` estimand.

### Interpretation rule

Always decompose

- `B(d)=TRUE-BASE`,
- `C(d)=RANDOM-BASE`.

If `A(d)` grows mainly because `B(d)` grows while `C(d)` stays near zero, that directly supports the strong `scale rewards matched syntax` interpretation.

If `A(d)` grows mainly because `C(d)` becomes increasingly negative while `B(d)` is stable, the safe conclusion is only:

> **larger models are more sensitive to a random structural constraint.**

That result is scientifically interesting but is insufficient by itself for the title-level `scale rewards syntax` claim.

### Required follow-up if RANDOM-harm dominates

Before promotion to a general alignment claim, add a stronger misalignment control in a new Selection round. The most natural candidate is **length-matched parse shuffling**: assign each sentence a real parse-tree shape from another sentence of the same word length. This preserves the empirical tree-shape distribution while breaking sentence-specific syntactic alignment.

This is an unlock condition for E02, **not additional E01 authorization**.

---

## E00.4 — Define the scale axis correctly

E01 changes **depth only** while holding hidden size, attention-head count, data, and update count fixed.

This is a clean first test of:

> **fixed-data depth scaling**

It is **not** yet:

- compute-optimal scaling;
- a universal parameter-scaling law;
- a fitted scaling exponent;
- a claim about arbitrary width/depth trade-offs.

Larger depth also implies larger training FLOPs at the same token count. Therefore a positive or negative interaction may still depend on the data/compute regime.

### Rule

E01 language should be `depth-scale interaction at fixed data`, not `the scaling law of linguistic inductive bias`.

If E01 passes, C1 must add enough scale points and eventually separate at least parameter/data/compute axes before any exponent-level claim.

---

## E00.5 — Check regularizer strength for mechanical scale dependence

The model uses `d_model=512`, 8 heads, and a feed-forward width equal to `8 × d_model`. TreeReg is applied to hidden states at a selected intermediate layer and to 25% of heads.

Moving from 4L to 16L while applying TreeReg at roughly 75% relative depth changes the number of upstream layers through which the TreeReg gradient propagates. The same nominal TreeReg schedule therefore does not guarantee the same effective optimization pressure.

### Mandatory diagnostics

At initialization and one fixed early checkpoint, record for TRUE and RANDOM at both depths:

- LM-only gradient norm before clipping;
- TreeReg-only gradient norm before clipping;
- `||g_TR|| / ||g_LM||`;
- cosine similarity `cos(g_LM, g_TR)`;
- norm of the combined gradient `||g_LM + g_TR||`;
- whether global clipping is triggered and the resulting clip factor;
- raw TreeReg loss/score;
- parameter count and realized training FLOPs/token for each depth.

The public TreeReg loop accumulates LM and TreeReg gradients into the **same optimizer update** and then applies global gradient clipping at norm `1.0`. A scale-dependent clipping rate can therefore create a nonlinear change in the effective relative strength of TreeReg even when nominal hyperparameters are identical.

Do not infer these quantities from the repository's existing `grad_norm` log: the current code computes/logs it after clipping. Instrument pre-clipping gradients explicitly.

Do not tune TreeReg separately by scale after seeing SG.

If the primary interaction coincides with a gross change in gradient ratio, gradient cosine, or clipping regime, treat the scientific interpretation as **HOLD** until that implementation effect is understood.

---

## E00.6 — Two-endpoint discipline

E01 uses 4L and 16L endpoints only. Therefore even a clean `|I| >= 5 pp` result establishes an **interaction**, not a scaling curve.

It cannot distinguish among:

- smooth monotone scaling;
- a one-time crossover;
- an intermediate optimum;
- saturation;
- a threshold effect.

### Promotion rule

A successful E01 authorizes a new Selection audit for an actual scale curve. It does **not** authorize wording such as `syntax changes the scaling exponent` by itself.

This is exactly the distinction between:

> **E01:** is there enough scale interaction to justify a paper-scale study?

and

> **paper:** what conditional scaling law actually describes the interaction?

---

## E00.7 — Layer placement is part of the instrument

The 16L TreeReg parent explicitly sweeps TreeReg placement across layers `[2,4,6,8,10,12,14]` and finds layer 12 best on aggregate SyntaxGym and PTB perplexity. The parent therefore does **not** establish that TreeReg's effect is invariant to placement.

Separately, the paper's 4-layer grokking experiments apply TreeReg at layer 2. L42 currently proposes layer 3 for 4L by matching the 16L parent's approximate fractional depth (`12/16 = 3/4`). That rule is principled, but it is not parent-validated at 4L.

This creates a dangerous alternative explanation for `A(16) > A(4)`:

> the 4L model may simply be regularized at a less effective layer.

### Rule

Do **not** tune 4L placement by choosing whichever layer gives the nicest final SG interaction.

Before the full 4L seed sweep, perform a bounded **placement robustness gate** using predeclared layer 2 and layer 3 settings. The purpose is not to select the better SG result; it is to determine whether the low-scale instrument is pathologically placement-sensitive.

Preferred implementation:

- use the same small predeclared seed subset for `4L@2` and `4L@3`;
- run TRUE and RANDOM under both placements;
- inspect the alignment contrast plus the pre-clipping gradient diagnostics from E00.5;
- if the qualitative contrast flips or changes by an amount comparable to the entire planned `5 pp` scale interaction, mark **HOLD — LAYER-PLACEMENT SENSITIVE**;
- if placement is reasonably stable, keep the predeclared fractional-depth rule (`4L@3`) for the formal E01 endpoint.

Do not use this gate to cherry-pick layer 2 or 3 after observing final SG.

This robustness work must be costed explicitly before execution because it is additional to the original 24-run cap; if the extra runs are not authorized, the conservative alternative is to keep E01 at HOLD until a cheaper independent placement criterion is justified.

---

## E00.8 — Do not replace depth scaling with width scaling casually

Keeping depth fixed and scaling hidden width would eliminate the layer-location problem, but it creates a worse TreeReg-specific construct shift.

TreeReg's SCIN computation normalizes the context direction but ultimately uses the **L2 norm of an orthogonal component of the hidden state**. With layer-normalized hidden states, this magnitude can change mechanically with hidden dimension. These SCIN values feed directly into TreeReg's scoring/loss.

Therefore width scaling can change the effective TreeReg temperature/strength even before any linguistic effect occurs.

For E01, depth-only scaling remains the safer first axis.

---

# E00 final gate

Proceed to the full E01 sweep only when all are true:

1. one reference training protocol is frozen and its provenance is explicit;
2. exact BLLIP-LG access/splits are available;
3. TRUE/RANDOM/BASE data and parse-generation pipelines are deterministic and archived;
4. actual 4L and 16L parameter counts and throughput are measured by a short dry-run;
5. primary wording is fixed to **fixed-data depth-scale interaction**;
6. interpretation is predeclared so that RANDOM-harm-only cannot be relabeled post hoc as `syntax benefit`;
7. pre-clipping gradient/clipping diagnostics show no gross scale-dependent implementation pathology;
8. the 4L placement robustness issue is resolved without selecting the nicest SG result post hoc.

If these conditions are not met, L42 remains a valid registered candidate but the **full E01 seed sweep should remain on execution HOLD**.
