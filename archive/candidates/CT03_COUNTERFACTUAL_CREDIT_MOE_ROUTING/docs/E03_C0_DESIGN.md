# CT03 Stage C0 (E03) — Counterfactual Credit Distillation, micro-training

**Status:** FROZEN 2026-09-20, before any training step.
**Predecessors:** E01 / E01.5 / E02 (`results/RESULTS*.md`).
**Scope:** one method, no benchmark. C0 answers whether the credit can *train a
router*, not whether it moves AIME.

---

## 1. The method (CCD), deliberately minimal

At a calibrated layer, for the routed set `S`, a selected expert `i in S` and a
boundary candidate `j not in S`:

```
dL_hat(i->j) = g^T ( h^{i->j} - h )          g = dL_seq/dh, one shared backward
y_ij         = -sign( dL_hat(i->j) )         +1 means "j should outrank i"
L_CF         = mean_ij  w_ij * log(1 + exp( -y_ij (s_j - s_i) ))
```

First version uses **uniform `w_ij`**. Magnitude weighting is not adopted until
it is shown to be necessary — the whole point of C0 is to learn whether the bare
signal trains anything.

Optional anchor, tested as a second arm only:
`L = L_CF + lambda * KL(p_router || p_router^0)`.
Its justification is the inductive bias, not the score: the pretrained router is
already fine on most tokens, and the blind spot is on fragile ones. **Repair
misrouting, do not relearn routing.** Exactly two arms: CF-only and CF+anchor.
No lambda sweep.

### Efficiency note that falls out of the renormalised algebra

```
dh_ij = (Z/Z' - 1) h + (p_j E_j - p_i E_i)/Z'
=> g^T dh_ij = (Z/Z' - 1)(g^T h) + ( p_j (g^T E_j) - p_i (g^T E_i) ) / Z'
```

So all `8 x 4 = 32` one-swaps at a token need only **12 expert forwards and 13
scalars** (`g^T h` plus `g^T E_e` for the 12 involved experts). The pairwise term
count never multiplies the expert cost.

## 2. What is trained

**Only the `gate` matrices at layers 28 / 36 / 44** of Qwen3-30B-A3B
(58% / 75% / 92% depth). Backbone, experts, attention, embeddings and LM head
are frozen. That is 3 x (2048 x 128) = 786k trainable parameters.

- **L47 is deliberately excluded.** The parent already demonstrates final-layer
  adaptation; the claim C0 must support is that *non-final* routers can be
  improved by counterfactual credit.
- **L20 is deliberately excluded.** Its Stage B calibration was 0.486, and the
  `<=60% depth` condition passed only marginally via L28 at 0.600. Adding layers
  by lowering the calibration bar would forfeit the one principle E02 established.

## 3. Everything else is held identical to E01/E02

Same token instrument (teacher-forced gold MATH solutions, hard = top-quartile
CE), same boundary-candidate construction, same `px_shared` proxy. The **only**
change from the diagnostic runs is that the credit now updates the router.
This is the design's main defence: a gain cannot be attributed to a new token
filter, a new candidate pool, or a new objective, because none of them changed.

`px_shared`, not `px_tok`: routing should improve the downstream consequence of
the whole continuation, not the current position. E01's cross-pairing settled it.

## 4. Data

`HuggingFaceH4/MATH-500`, shuffled at seed 0. The **first 16 problems that pass
the length filter are reserved as held-out** and never trained on; training draws
from the remainder. Held-out is fixed before training starts.

## 5. Pre-registered adjudication

Measured on held-out hard tokens at L28/36/44, base router vs trained router.

**A — credit alignment.** `corr(s_j - s_i, -dL_exact)` must rise materially above
its base value. Stage B measured the base router at **rho = 0.057** on Qwen; any
real learning should be visible as a clear move above that.

**B — actual route regret.** `R = L(S) - min_{S' in N(S)} L(S')` over the
one-swap neighbourhood, recomputed exactly on the *new* route. Must **fall**.

**C — no collapse.** Route overlap with base, per-expert load, routing entropy,
and held-out teacher-forced CE must not degrade materially.

**GO to C1 (benchmarks)** iff A and B and C hold. A+B are the load-bearing pair.

**KILL / reformulate** if `L_CF` fits (the router learns to satisfy the pairwise
labels) but **B does not improve**. That would mean the credit is learnable but
not useful, and the correct response is to rethink the formulation — **not** to
add losses until the metric moves.

A is not sufficient alone. A router can be taught to reproduce a proxy's
preferences without the underlying routing getting better; B is what
distinguishes those cases, which is why B cannot be traded away for a stronger A.

## 6. Numerics

fp32, sharded over 2 cards, as in E02. bf16 is rejected for the same reason: the
exact held-out regret in B reaches 1e-4 at deep layers, and bf16 can round two
near-identical routes to the same value. Training and evaluation share the
dtype so that B is comparable before and after.

---

# AMENDMENT 2026-09-20 — Stage C is an exploration tree, not a GO/KILL gate

**Recorded before any C0 result exists** (training at step ~150/300, no
checkpoint written, no evaluation run). The original §5 is kept above verbatim
as the frozen record; this amendment supersedes its *decision rule* only.

## What changed and why

§5 treated `L_CF` pairwise distillation as the method, so "it did not work"
would have read as "CT03 did not work". That conflates two different objects.
The central claim is:

> a pretrained MoE has exploitable counterfactual routing utility on hard
> tokens; that utility can be cheaply estimated, and converted into better
> router decisions.

E01/E01.5/E02 evidenced the first half. Stage C investigates the second, and
there is no reason to assume the first learning formulation is the right one.
**Method v0 failing is not CT03 failing.**

A further reason not to privilege pairwise loss: E01/E02 produce a *continuous*
quantity, `u_ij ~= -dL(i->j)`, and the pairwise reduction `u_j > u_i` discards
most of it. If v0 underperforms, the first question is whether the router should
learn a *preference* or a *utility landscape* — not which regulariser to add.

## Outcome → diagnosis → next step

| observation | scientific meaning | next |
|---|---|---|
| A↑ B↓ C stable | credit became routing improvement | benchmark (C1) |
| A↑ B≈ | credit learned but **not realised as action** | set-aware / executable-set objective |
| A↑ B↓ C bad | effective but destructive to the pretrained prior | selective update / trust region |
| A≈ B≈ | pairwise supervision did not write the information into the router | soft utility distillation, listwise |
| A erratic | optimisation / label scaling | analyse credit→logit mapping first |
| B↓ but benchmark flat | local routing gain ≠ end-task gain | which tokens/layers carry downstream value |

The anchor arm is reinterpreted accordingly: not a rescue loss, but the
configuration that the "effective but destructive" branch would recommend. It
was already running, so it costs nothing to read it that way.

## The crossing question, and the instrumentation it forces

Top-8 is a discrete boundary. The router's logits can reorder substantially
while no candidate actually crosses into the selected set, which would produce
**A rising with B lagging** — a coherent dynamic, not a failure. Distinguishing
that from "never learned" and from "crossed wrongly" needs more than A/B/C, so
evaluation additionally records, per token and layer:

- `margin_boundary` = `s[sel[-1]] - s[cand[0]]`, the gap at the selection boundary;
- `n_crossed` = experts the trained router puts in the top-8 that the base
  router would not, **at the same hidden state**;
- `frac_tokens_crossed`;
- `dL_revert` = exact loss change of reverting the realised route to the base
  router's choice. **Positive means the crossing helped.**

These separate three cases that A/B alone cannot:

1. not learned — A flat, `n_crossed` ~ 0;
2. learned, not realised — A up, `n_crossed` ~ 0, margin shrinking, B flat;
3. realised but wrong — `n_crossed` > 0, `dL_revert` <= 0, B flat or worse.

## Where the kill bar now sits

CT03 dies only on evidence against the central claim, not against v0:

1. even **exact oracle** counterfactual labels cannot train a router to lower
   held-out route regret;
2. exactly lower-regret routing yields no stable benefit in real free
   generation / benchmarks;
3. teacher-forced route utility does not correspond to generation-time utility,
   making the central object an artefact;
4. exploitable headroom exists only in the last 1–2 layers, leaving no room
   against EPO;
5. writing credit into the router requires touching backbone/experts or costs
   about as much as dense rerouting, destroying the efficiency claim.

Condition 3 is the one this project has not yet instrumented at all, and it is
the most dangerous: every result so far is teacher-forced.
