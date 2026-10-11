# CT03 E01.5 — Results and adjudication

**Run:** 2026-09-20 · OLMoE-1B-7B-Instruct fp32, one card (`fvcrc20:0`) · MATH-500.
**Scale:** 24 problems × 8 tokens × 5 layers × 12 candidates × 4 α = **46,080 records**
(+32 depth-drift records). **Design:** `docs/E015_DESIGN.md`, frozen before the run (see git history for `docs/E015_DESIGN.md`).

## Verdict: CONDITIONAL — one pre-registered condition passed, one failed

§7 required **both** `r1 >= 0.60` **and** layers ≥5 stable at α=1 (rho ≥ 0.70).

| condition | value | outcome |
|---|---|---|
| `r1` (layer 1, boundary, α=0.125, hard) | **0.829** | **PASS** (bar 0.60) |
| layer 5 at α=1 | **0.600** | **FAIL** (bar 0.70) |
| layer 7 at α=1 | 0.771 | pass |
| `r1 < 0.40` → SHRINK | 0.829 | not triggered |

Neither branch fires cleanly, so §7 sends this to the break-even curve. This is
**not** a clean Stage-B green light and should not be reported as one.

## A. The α sweep — rho_med(px_shared, dL_seq), hard tokens

| layer | α=0.125 | α=0.25 | α=0.5 | α=1.0 |
|---|---|---|---|---|
| 1 | **0.829** | 0.657 | 0.600 | 0.257 |
| 3 | 0.914 | 0.657 | 0.486 | 0.429 |
| 5 | 1.000 | 0.800 | 0.657 | 0.600 |
| 7 | 0.943 | 0.914 | 0.829 | 0.771 |
| 15 | 1.000 | 1.000 | 1.000 | 1.000 |

Shallow layers recover strongly as the step shrinks — layer 1 goes 0.257 → 0.829.
Since the proxy's ranking is α-invariant by construction, this is caused entirely
by the exact side becoming more linear. **The shallow-layer gradient is correct;
the full expert swap is outside its linear regime.** That is hypothesis (A).

Caveat on resolution: 6 candidates per pool makes per-token Spearman quantised
(0.829, 0.771, 0.657, 0.600 … are the attainable values at n=6). 96 tokens per
cell. The trend is far larger than that granularity, but single cells should not
be read to three digits.

## B. Correction — the mechanism is dispersion, not shrinkage

I reported from a 1-problem smoke test that layer-1 α=1 recovered only 57% of the
predicted change (`lin_ratio` 0.574), i.e. systematic shrinkage. **That did not
replicate.** At n=24 the median `lin_ratio` is ~0.96–1.00 in every cell. The
first-order term is *not* systematically biased. The actual failure is in the tails:

| layer | α | median | IQR | frac \|r−1\|>0.5 | **frac wrong sign** |
|---|---|---|---|---|---|
| 1 | 0.125 | 0.997 | 0.151 | 0.337 | 0.163 |
| 1 | 1.0 | 0.960 | **8.794** | 0.829 | **0.399** |
| 7 | 1.0 | 0.988 | 1.303 | 0.558 | 0.209 |
| 15 | 1.0 | 0.965 | 0.434 | 0.285 | 0.057 |

At layer 1 under a full swap, **40% of candidates get the wrong sign** and the IQR
of the ratio is ~9. The typical candidate is fine; the distribution has heavy
tails that scramble the ordering. This matters because a median-based summary
would have called layer 1 healthy.

Two confounds checked and rejected:

- **Not candidate crowding.** Within-token spread of exact `dL` relative to its
  magnitude is flat (~2.4–2.7) across every layer and α. Shallow candidates are
  not harder to separate; the estimate is simply noisier.
- **Not depth accumulation.** Direction drift `cos(actual, linear)` first falls
  below 0.95 at **absolute layer 13–14 regardless of source layer** (from L3 at
  rel-depth 10, L5 at 9, L7 at 6), and **for L1 it never falls below 0.95 at all**.
  The "long nonlinear suffix" account in the design is not supported. Whatever
  produces layer-1 loss-level dispersion is not visible as hidden-state direction
  drift, and E01.5 does not identify it. Left open deliberately.

## C. The caveat that actually governs Stage B

**α-interpolation is a diagnostic, not a method.** Router training needs credit
for the routing change it would actually make, which is α=1 — a discrete swap.
A proxy accurate only at α=0.125 estimates the loss of a *fractional* expert
substitution, which is not a routable action. So "layer 1 recovers at small α"
does **not** hand us usable shallow-layer training signal; it tells us the
gradient is locally right, which is necessary but not sufficient.

The number that governs usable credit is the α=1 column: **layer 1 = 0.257,
layer 5 = 0.600, layer 7 = 0.771, layer 15 = 1.000** — and at layer 1, 40%
sign errors is close to useless for a pairwise ranking objective.

Honestly stated: `r1` passed as written, but `r1` was a partly mis-specified
threshold. It measures local gradient correctness, not deployable credit. I am
not moving the goalpost after the fact — the pre-registered number is reported
above as it fell — but the decision should rest on the α=1 column.

## D. Cost — break-even is low, and the 131× was conservative

Ratio exact/proxy vs candidates harvested per shared backward:

| cands/seq | L1 | L5 | L7 | L15 |
|---|---|---|---|---|
| 4 | 0.7 | 0.5 | 0.4 | 0.1 |
| 8 | 1.4 | 1.0 | 0.8 | 0.1 |
| 64 | 10.9 | 8.1 | 6.7 | 1.1 |
| 768 (E01) | 130.6 | 96.9 | 80.0 | 12.7 |
| 16384 (all-token) | 2482.8 | 1842.3 | 1522.0 | 240.9 |

**Break-even: ~5.8 candidates/sequence at layer 1**, rising to 60 at layer 15.
Your reviewer worry runs the opposite way to the fear: E01's 768 was not an
inflated operating point but a modest one. Below ~6 candidates the proxy is
*more* expensive than exact rerouting, which is a real published limit — but any
realistic multi-layer, multi-token setting is far above it. Layer 15's break-even
of 60 restates that final-layer rerouting is cheap anyway.

## E. Recommendation

CT03 is alive and the shallow-layer weakness is **characterised, not cured**.

Proposed scope: **full-swap counterfactual credit is reliable from roughly the
model's middle onward** (layer 7 of 16 = 0.771, and E01 gave 0.929/0.988/1.000 at
10/13/15). That is not the narrow "final-layer only" case the registration feared
— it is most of the network by count, and the expensive half by rerouting cost.

Two ways to go, and this is a scope call rather than a technical one:

1. **Stage B now**, on layers ≥7, with the shallow-layer sign dispersion reported
   as a boundary of the method. The cost case is strong and cross-family
   calibration (incl. router renormalisation) is the untested risk.
2. **One more cheap check first**: whether a sign-robust or magnitude-clipped
   objective recovers usable layer-1 credit at α=1. This is the only repair the
   evidence actually licenses — and notably it is *not* a curvature correction,
   since the α sweep shows the problem is dispersion, not systematic curvature.
   Adding a Hessian term here would have been the wrong repair.

I lean (1): the depth gradient is now explained and bounded, and E01.5 has done
its job. Option (2) risks becoming the first of a series of conditionals.
