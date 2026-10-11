# L42 — E00 Locked Execution Decisions

**Date:** 2026-09-15  
**Parent:** `L42 — Does Scale Reward Syntax?`  
**Status:** `E00 PARTIALLY RESOLVED — FULL E01 SWEEP REMAINS ON EXECUTION HOLD UNTIL LOCAL DATA/DRY-RUN CHECKS PASS`

This file freezes the remaining pre-pilot choices that can be resolved from the paper/public code without consuming the full E01 sweep. It does not change the scientific question or expand the paper claim.

---

## 1. Reference protocol is now frozen: official public 60k code route

Use the official TreeReg public BLLIP-LG command as the local reference protocol, pinned to upstream commit:

`ananjan-nandi-9/tree_regularization@106ebd3bcc69ef5a642cfefee1af3237ccdb5dad`

Reference recipe:

- scratch Transformer LM;
- BLLIP-LG;
- `d_model=512`;
- 8 attention heads;
- 16 layers for the parent-scale endpoint;
- effective batch size 160 (`32 × 5` accumulation);
- 60,000 LM steps;
- start LR `1e-4`, end LR `6e-5`;
- TreeReg every 10 LM steps;
- TreeReg layer 12 at 16L;
- `sci_heads=0.25`;
- same-data TreeReg (`--treereg_same_data`).

The NAACL paper's ~8.2pp TRUE-vs-RANDOM point estimate remains context only. Phase A establishes the local reference effect under this exact public-code protocol. Do not switch to the paper's 100k description after seeing results.

---

## 2. Random structural-control target is frozen before training

Generate the RANDOM parse corpus once with a dedicated control seed:

`random_parse_seed = 314159`

Rules:

- use the parent's exact recursive random-split procedure;
- generate the corpus once after reconstructing the exact BLLIP-LG split;
- archive the generated parse file and its SHA256;
- reuse the identical RANDOM corpus for all depths and all training seeds;
- training seeds remain `10 / 20 / 30 / 40` and are independent of the RANDOM-control seed.

No regeneration after observing SG.

---

## 3. Gradient/clipping audit is integrated into E01 rather than added as a separate parent-scale sweep

For the first 16L seed (`seed=10`) in TRUE and RANDOM, record diagnostics at:

- initialization / first eligible update; and
- `step=1000` before continuing the run.

Record separately, before clipping:

- `||g_LM||`;
- `||g_TR||`;
- `||g_TR|| / ||g_LM||`;
- `cos(g_LM, g_TR)`;
- `||g_LM + g_TR||`;
- whether the combined update is clipped at norm 1.0;
- clip factor;
- raw TreeReg score/loss.

Use the same diagnostic at 4L TRUE/RANDOM for seed 10.

### Frozen pathology gate

Mark `HOLD — REGULARIZER SCALE PATHOLOGY` before interpreting SG if any of the following is observed between 4L and 16L for the same TRUE/RANDOM arm at the fixed diagnostic checkpoint:

1. the TreeReg-to-LM gradient-norm ratio differs by more than **4×**;
2. one depth is clipped on **>90%** of the fixed diagnostic update window while the other is clipped on **<10%**;
3. median clip factors differ by more than **4×**;
4. gradient cosine changes from materially aligned to materially opposed (or vice versa), using `|cos| >= 0.2` on both sides as the materiality threshold.

These thresholds are instrument safeguards, not hyperparameter-tuning targets. If triggered, do not tune TreeReg strength until the scientific interpretation looks good; return to Selection/instrument design.

---

## 4. 4L placement gate is bounded and costs only two extra full runs

The formal E01 4L endpoint remains the predeclared fractional-depth placement:

`4L@layer3`.

Before the full 4L seed sweep, use **seed 10 only** to test whether 4L is pathologically sensitive to placement:

- `4L@2 TRUE, seed10` — extra run;
- `4L@2 RANDOM, seed10` — extra run;
- `4L@3 TRUE, seed10` — already counts as the formal Phase-B seed10 run;
- `4L@3 RANDOM, seed10` — already counts as the formal Phase-B seed10 run.

Define

`A_4@k = SG_TRUE(4L@k) - SG_RANDOM(4L@k)`.

### Frozen placement gate

Mark `HOLD — LAYER-PLACEMENT SENSITIVE` if either:

- `A_4@2` and `A_4@3` have opposite signs; or
- `|A_4@2 - A_4@3| >= 5.0 pp`.

If neither happens, retain **layer 3** for the formal E01 endpoint regardless of which layer gives the numerically larger SG score. Do not choose the better layer post hoc.

This changes the maximum full-training budget from 24 to **26 full runs**. Only the two `4L@2` runs are additional; the `4L@3` seed10 runs are part of Phase B.

---

## 5. Exact execution order

### E00-A — local prerequisites, no full sweep

1. verify licensed `LDC2000T43` / exact Hu et al. BLLIP-LG reconstruction is available;
2. pin the upstream TreeReg commit above;
3. deterministically build TRUE and RANDOM datasets; archive hashes;
4. short dry-run to measure 4L/16L parameter counts, tokens/s, GPU memory, and realized FLOPs/token;
5. implement and unit-check pre-clipping gradient diagnostics.

If exact BLLIP-LG is unavailable: **HOLD. Do not substitute a corpus.**

### E01 Phase A — 16L parent-scale endpoint

Run `BASE / TRUE / RANDOM` for seeds `10/20/30/40`, but execute seed10 first. At seed10, collect the frozen diagnostic checkpoints before spending on the remaining seeds.

Proceed only if the existing Phase-A reproduction gates pass.

### E00-B / Phase-B entry — 4L placement robustness

After Phase A passes:

1. run formal `4L@3 TRUE/RANDOM seed10`;
2. run extra `4L@2 TRUE/RANDOM seed10`;
3. apply the frozen placement gate;
4. if it passes, complete formal 4L@3 BASE/TRUE/RANDOM for the remaining E01 seeds.

---

## 6. Scientific claim remains narrow

E01 tests only:

> **Does the matched-vs-random structural-constraint advantage show a material fixed-data depth-scale interaction?**

E01 does **not** establish:

- a universal parameter scaling law;
- a scaling exponent;
- that all linguistic inductive bias scales this way;
- that TreeReg soft regularization is equivalent to a hard syntactic architecture;
- that growing TRUE-vs-RANDOM separation necessarily means TRUE increasingly helps (mandatory TRUE-BASE / RANDOM-BASE decomposition remains required).

If `|I| < 5pp`, the CI includes zero, or the interaction is explained by placement/gradient pathology, the current scaling-paper identity stops. Do not rescue it by fitting a slope to noise, changing the regularizer, or switching to TG after seeing the failed result.

---

## 7. What is still genuinely unresolved before GPU execution

The only remaining pre-execution blockers require the local environment/data rather than more literature discussion:

- exact licensed BLLIP-LG availability and split reconstruction;
- deterministic preprocessing hashes;
- actual 4L/16L parameter count and throughput;
- verification that the added pre-clipping diagnostics are implemented correctly.

Until those pass, the **candidate remains PILOT-AUTHORIZED but the full E01 sweep is execution-HOLD**. The research-selection question itself is no longer the blocker.