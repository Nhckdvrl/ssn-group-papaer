# CT03 E01.5 — Is the shallow-layer weakness a perturbation-size boundary or a structural limit?

**Status:** FROZEN 2026-09-20, before any run. Nothing is trained.
**Predecessor:** `results/RESULTS.md` (E01, commit `317ad32`).
**Mandate:** one question only. Answer it, then go to Stage B or shrink CT03.

---

## 1. The one question

E01 found `px_shared` → `dL_seq` rises monotonically with depth:

| layer | 1 | 4 | 7 | 10 | 13 | 15 |
|---|---|---|---|---|---|---|
| rho_med (hard/boundary) | 0.286 | 0.524 | 0.762 | 0.929 | 0.988 | 1.000 |

The proxy is weakest where exact rerouting is most expensive. E01.5 asks whether
that is:

- **(A) a finite-perturbation boundary** — a full expert swap is simply too large
  a step for a first-order model when 15 nonlinear layers remain; or
- **(B) structural** — shallow-layer downstream gradients carry little usable
  information about route changes at all, at any step size.

(A) is a method constraint that can be designed around. (B) shrinks CT03 to
mid/late-layer router adaptation and forces the efficiency case to be re-argued
before anything touches a 30B model.

## 2. Why α-interpolation is the decisive instrument

For a replacement `i -> j` we scale the perturbation:

```
h'(a) = h + a * dh,   a in {0.125, 0.25, 0.5, 1.0}
```

The exact side is recomputed per `a`. The proxy is **exactly linear in `a`**:
`px(a) = a * g^T dh`. Two consequences that make this a clean instrument:

1. Spearman is scale-invariant, so the proxy's *ranking* of candidates is
   identical at every `a`. Any change in rho with `a` is therefore caused
   **entirely by the exact side becoming more linear**, not by the proxy
   changing. This isolates exactly the quantity in question.
2. As `a -> 0`, `dL_exact(a) / (a * g^T dh) -> 1` if and only if the gradient is
   correct. That ratio is recorded directly as `lin_ratio` — a sharper statement
   than a correlation, because it tests magnitude as well as order.

So: if layer 1 recovers at small `a`, the gradient was right all along and the
full swap was out of the linear regime → (A). If layer 1 stays near 0.3 at
`a = 0.125`, the gradient itself does not describe the loss surface there → (B).

## 3. Measurements

Layers `{1, 3, 5, 7, 15}` — weighted to the shallow transition, with 15 kept as
the known-good anchor. 24 problems x 8 tokens (4 hard / 4 easy).

Candidates, **both pools kept**: 6 boundary (`k+1..k+6`) and 6 random
unselected. E01 found layer-1 random (0.429) *beat* layer-1 boundary (0.286),
which is the opposite of the "large jumps hurt shallow layers" story, so
dropping the random pool would discard the one piece of evidence that already
contradicts the favoured hypothesis.

Per `(layer, alpha, pool)`: rho_med, top-1/top-3, sign accuracy, and `lin_ratio`.
Errors additionally stratified by `||dh||`, `|dL|`, and candidate router rank.

## 4. Noise floor is measured, not assumed

Every batch carries **two** zero-patch rows. Row 0 is the baseline; row 1 is
identical and its `dL` is therefore a direct empirical measurement of the
replay's numerical floor. This matters more here than in E01: at `a = 0.125` the
effects are ~8x smaller than the ones E01 measured, and at layer 15 the median
effect was already 2.9e-2. A recovery at small `a` is only believable if the
floor is far below the effect, so the floor is recorded per batch rather than
argued.

## 5. Suffix accumulation check (small, subsampled)

To separate "long nonlinear suffix" from "this particular shallow layer is
pathological", the replay captures the position-`t` hidden delta at **every**
downstream layer, for a subsample (shallow layers, boundary pool, 2 tokens per
problem). Against the `a = 0.125` response as the linear reference:

```
lin_dir    = d(a_min) / a_min          per-unit linear response
actual     = d(a)     / a              per-unit actual response
cos_lin    = cos(actual, lin_dir)      direction drift
norm_ratio = ||actual|| / ||lin_dir||  magnitude drift
```

If `cos_lin` decays smoothly with remaining depth for every shallow layer, the
cause is suffix length. If it collapses immediately at one layer, that layer is
pathological and the story is different.

## 6. Efficiency, recomputed at realistic operating points

E01's 131x amortised the shared backward over 768 candidates/sequence, which a
reviewer will rightly challenge. E01.5 recomputes cost as a **curve** over
candidates-per-sequence (4, 8, 16, 32, 64, 256, 1024, and the all-token
operating point), and reports the **break-even count** below which the proxy is
*more* expensive than exact rerouting. That break-even is a real property of the
method and must be published whichever way it falls.

## 7. Pre-registered adjudication

Let `r1` = rho_med at **layer 1, boundary, a = 0.125**.

- **STAGE B** if `r1 >= 0.60` and layers >= 5 are stable at `a = 1`
  (rho_med >= 0.70). Reading: controllable approximation boundary.
  Stage B begins with a *small* exact-vs-proxy calibration on Qwen3-30B-A3B —
  including router renormalisation, which OLMoE did not exercise — **not** with
  router training.
- **SHRINK** if `r1 < 0.40`. CT03 narrows to mid/late-layer counterfactual
  router adaptation, and the efficiency + benchmark upside is re-argued on that
  narrower scope **before** any 30B work. If the advantage has materially
  shrunk, KILL there rather than betting on a benchmark.
- **In between (0.40-0.60):** decide with the §6 break-even curve. Do not
  split the difference by adding machinery.

**No second-order term, no per-layer temperature, no curvature correction in
E01.5.** If the α sweep shows the problem is not curvature, a curvature patch
would have been the wrong repair — and adding one before knowing that is how a
clean project acquires a permanent conditional.
