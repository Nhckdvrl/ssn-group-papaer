# CT03 E01 — Is local counterfactual credit faithful to exact route regret?

**Status:** FROZEN 2026-09-20, before any run.
**Topic authority:** `chasing trends/topics/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING.md` §6.
**Rule:** this is the decisive pilot. No router is trained until E01 is adjudicated.

---

## 1. The one uncertainty E01 resolves

CT03's entire method rests on one approximation:

> the loss effect of swapping a routed expert for an unexecuted one can be
> predicted from a **local** expert-output perturbation dotted with a
> **shared** downstream gradient, without rerunning the downstream network.

E01 measures the faithfulness of that approximation against the exact quantity
it claims to replace. Nothing else. If it is unfaithful, CT03 dies here and no
amount of router-training engineering rescues it.

## 2. Quantities

One MoE layer `l`, one token position `t`. The layer's MoE block outputs
`h = h_{l,t}` into the residual stream. The router assigns softmax weights `w`
over all `E` experts and executes the top-`k`.

An **equal-compute replacement** `i -> j` (`i` selected, `j` unselected) gives

```
h^{i->j} = h - w_i E_i(x) + w_j E_j(x)
Δh       = w_j E_j(x) - w_i E_i(x)
```

OLMoE has `norm_topk_prob=false`, so the selected weights are raw softmax
probabilities and the swap needs no renormalisation. This is a deliberate model
choice: it removes a confound from the first measurement.

**Exact** (what the parent buys with full downstream execution):

- `dL_tok`  = CE at position `t` after patching, minus CE before.
- `dL_seq`  = total scored CE over the whole sequence after patching, minus before.
  (`dL_seq` differs from `dL_tok` because position `t`'s residual also feeds
  every later position through attention.)

**Proxy** (what CT03 proposes to use instead):

- `px_tok`    = `g_tok^T Δh`,    `g_tok = ∂CE_t / ∂h`        — per-token backward.
- `px_shared` = `g_shared^T Δh`, `g_shared = ∂L_seq / ∂h`    — ONE backward per sequence.

`px_shared` is the one the method actually needs; `px_tok` is the clean
first-order upper bound that tells us whether a failure is a Taylor failure or
a gradient-sharing failure. Both are measured.

## 3. Baselines the proxy must beat

A correlation alone is worthless if something free predicts as well. Measured
on the identical candidate set:

| baseline | rationale |
|---|---|
| `router_gap = w_j - w_i` | the router's own opinion; kill condition §10 |
| `-|Δh|` | expert outputs that move the residual more just matter more |
| `|Δh|` | sign-flipped control for the above |
| random | floor |

## 4. Candidate pools (reported separately, never pooled)

For each sampled `(t, l)`, `i` is fixed to the **lowest-weight selected expert**
(router rank `k`) — the one a Top-K router is closest to dropping.

- **boundary pool**: `j` = router ranks `k+1 .. k+m` (`m=8`). The realistic
  method pool, and the pool where `router_gap` has least leverage.
- **random pool**: `j` = `m` uniformly sampled unselected experts outside the
  boundary pool. Tests whether the proxy still works when `router_gap` is
  informative, and whether large beneficial swaps exist outside the top-(k+m).

## 5. Strata

- **layer**: `{1, 4, 7, 10, 13, 15}` of 16. Kill condition §10 includes
  "works only at the final MoE layer".
- **token difficulty**: per-token CE quartiles over scored tokens.
  `hard` = Q4, `easy` = Q1. The parent's claim is that routing regret
  concentrates on fragile tokens, so the proxy must work *there*.

## 6. Primary observables

Per (stratum × layer × pool):

1. Spearman rho(proxy, exact) — over candidates, pooled across tokens, and
   also the median of per-token rho (the method ranks *within* a token).
2. sign accuracy on `exact < 0` (beneficial swap) — and the base rate, since
   a degenerate all-harmful set makes accuracy meaningless.
3. top-1 / top-3 recall of the exact-argmin candidate, within token.
4. regret: `exact` of the proxy's argmin minus `exact` of the true argmin,
   normalised by the token's exact spread.

Primary pairing is `px_shared` vs `dL_seq` (the method's real quantity).
`px_tok` vs `dL_tok` is the diagnostic pairing.

## 7. Cost accounting

Reported as measured wall-clock and analytic FLOPs for one token, `m`
candidates:

- exact: `m` replays of layers `l+1..L-1` + norm + lm_head over the sequence;
- proxy: `m` local expert MLP forwards at one position + `1/T` of a shared
  backward already paid by training.

Kill condition §10 includes "exact rerouting cost is already small enough that
the surrogate has no practical advantage" — so the ratio is a result, not a
footnote.

## 8. Implementation validity checks (run before the headline numbers)

- **replay identity**: layer-replay from `l` with a zero patch must reproduce
  the full-forward logits to within dtype tolerance.
- **patch identity**: patching `h` with `Δh` computed for `j == i` (a no-op
  swap) must give `dL = 0`.
- **exact-vs-full-forward**: for a subsample, the replay-based `dL_seq` must
  match a genuine full forward with a routing-override hook. This is the
  check that the "exact" side is actually exact.
- **numerics**: model is run in **float32** for the pilot. bf16 would put the
  measurement noise floor near the effect size for small swaps, and a
  correlation measured against noise is not a result.

## 9. Pre-registered adjudication

Let `rho*` = per-token median Spearman for `px_shared` vs `dL_seq` on the
**hard** stratum, **boundary** pool, averaged over non-final layers.

- **CONTINUE** if `rho* >= 0.5` AND top-3 recall clearly above the pool's
  chance rate AND `px_shared` beats every §3 baseline on the same cells AND it
  is not confined to the last two layers.
- **KILL** if `rho* < 0.25`, or if `router_gap` matches the proxy, or if the
  proxy only works at layers >= 14.
- **In between**: report honestly, and do NOT rescue by adding second-order
  terms, per-layer temperatures, or filters. Those are §7 refinements of the
  registration and are explicitly gated behind evidence.

No router training, no benchmark, no Qwen3-30B until this is adjudicated.
