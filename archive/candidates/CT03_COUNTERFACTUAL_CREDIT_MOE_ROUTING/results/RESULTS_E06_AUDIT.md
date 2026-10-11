# CT03 E06 — action-space audit: one-swap is not EPO's action space

**Run:** 2026-09-22, Qwen3-30B-A3B fp32, 4 cards (two 2-card shards) · 119
problems × 8 hard tokens × L36/L44 = 1,902 cells, each with **exact** downstream
CE for 32 one-swap routes **and** 32 parent-style Gumbel top-k routes over the
same top-(K+m) pool. `src/e06_collect.py`.

## Why it was needed

E05 measured proxy screening inside the **one-swap** space `S' = S - {i} + {j}`.
EPO samples full Gumbel top-k routes that may change several experts at once. So
"we cut EPO's 32 reruns to 4" was a claim about a possibly narrower action space
than EPO actually uses. Both spaces were therefore evaluated exactly, on the same
tokens.

## A broken first attempt, recorded because it nearly produced a false result

The first run reported one-swap capturing **93.4%** of the full-route oracle,
which would have settled the question in our favour. It was wrong. The Gumbel
sampler produced **one identical route across all 60,864 draws**:

```python
g = -torch.log(-torch.log(u).clamp_min(1e-30))     # parses as -(log(u).clamp_min(eps))
```

`log(u)` is negative everywhere, `clamp_min` lifts it to `+1e-30`, the negation
gives `-1e-30`, and the outer `log` of a negative is **NaN**. With all-NaN
scores `topk` degenerates to a fixed index set. The tell was that "mean experts
changed by the best Gumbel route" came out as exactly **4.00** on both layers —
a number too clean to be a mean over 951 cells.

Fixed with explicit intermediates plus `assert torch.isfinite(g).all()`; the
sampler now yields 28.7 unique routes per cell out of 32, with the
experts-changed distribution `{0:1503, 1:16209, 2:28548, 3:13046, 4:1558}`.

## Result: the two action spaces are not nested, and neither dominates

Mean over cells where some route beats the base route. `union` = the better of
the two spaces per cell.

| layer | n | best swap | best gumbel | union | **swap/union** | gumbel/union | swap ≥ gumbel |
|---|---|---|---|---|---|---|---|
| L36 | 951 | −0.2358 | −0.2468 | −0.2814 | **0.822** | 0.923 | 0.308 |
| L44 | 951 | −0.2864 | −0.2721 | −0.3226 | **0.870** | 0.865 | 0.429 |

One-swap captures only **82–87%** of the combined oracle, and is at least as good
as the best Gumbel route on only **31% (L36)** / **43% (L44)** of tokens. The
Gumbel space misses a comparable share in the other direction. **Each space finds
gains the other cannot reach.**

## Consequence for the screening claim

E05's "m=4 retains 94–96%" is retained gain *within* the one-swap space, and that
space is itself worth 82–87% of the union. Composed, proxy top-4 recovers roughly

```
L36:  0.937 x 0.822 ~= 0.77        L44:  0.962 x 0.870 ~= 0.84
```

of the union oracle — before accounting for something not measured at all:
**the proxy's ranking quality over multi-expert Gumbel routes is unknown.**
`g^T dh` is a first-order estimate and E03.7 showed a non-additive component that
grows toward shallow layers; several simultaneous swaps is exactly where it
should be weakest.

So the honest statement is **not** "cheap screening can replace EPO's search".
It is: *the proxy screens well inside the one-swap space, and the one-swap space
is not EPO's action space.* Any screening claim about EPO needs the proxy
evaluated on the route space EPO actually samples.

## Status

CT03 remains **KILLED** (`CT-KILL-20260922-1`). This is an audit of an archived
estimator property, and it narrows rather than supports the screening story.
