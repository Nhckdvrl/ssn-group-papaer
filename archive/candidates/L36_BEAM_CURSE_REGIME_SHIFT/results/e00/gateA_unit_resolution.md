# Gate A — resolution of the edit-distance unit, and a reproducibility finding

**Date:** 2026-09-14
**Trigger:** E00 §A.3 threshold failed — Spearman `rho = 0.904` (passes `>= 0.90`) but only
**69.2%** of segments share a quartile under the character- and word-level readings of `d_edit`
(threshold was `>= 80%`). Per §A.3 the unit must then be resolved against the authors' material
before E01. This file is that resolution. It was written **before any model output existed**.

## What we rebuilt

`newstest2019` En→De, 1997 segments, references = official WMT reference + Freitag et al. (2020)
`AR`. `u` per ACL-2022 eq. (1) with `n = 2`, i.e. `u = d_edit(y_wmt, y_ar) / ((|y_wmt| + |y_ar|)/2)`.

| reading | mean `u` | median | `u` by reference-length bucket `[0,10] (10,20] (20,30] (30,)` |
|---|---|---|---|
| character | 0.427 | 0.428 | 0.381 / 0.427 / 0.439 / 0.451 |
| word | 0.607 | 0.612 | 0.563 / 0.606 / 0.618 / 0.635 |

## Finding 1 — the paper's Figure 1 levels are not reproducible under eq. (1)

Figure 1 (rendered from the ACL PDF) plots MT-ende at roughly **3.5% / 8.5% / 14% / 23%** across the
same four reference-length buckets. Ours are 38–45% (character) and 56–64% (word).

The discrepancy is not a unit choice. Figure 1's bucket means grow **roughly proportionally to
sentence length** (a ~6.6× rise across buckets whose mean length rises ~5.7×). No quantity of the
form `d_edit / (per-segment reference length)` can behave that way — dividing by the segment's own
length makes `u` close to length-invariant, which is exactly what both of our readings show, and
what eq. (1) mandates. Reproducing Figure 1's profile requires an **unnormalised numerator over a
constant denominator**; the closest fit we found is `d_word(segment) / (corpus-mean reference length
in characters)`, giving 0.030 / 0.066 / 0.108 / 0.164, which tracks the shape but still undershoots.

So either Figure 1 plots a differently normalised quantity than eq. (1), or its MT-ende series was
produced by a different code path. We cannot tell from the released material; there is no code or
score release for this paper that we could find.

## Finding 2 — the paper's own Figure 6 contradicts Figure 1, and agrees with us

Figure 6 (MT-ende) bins segments by `u ∈ [0, 0.33] / (0.33, 0.66] / (0.66, 1]`, and all three bins
are populated in every length bucket. That binning is only meaningful if per-segment `u` for MT
spans `[0, 1]` — i.e. the scale our reconstruction produces, not the 3.5–23% of Figure 1.

Our reconstruction against those bins:

| reading | `[0,0.33]` | `(0.33,0.66]` | `(0.66,1]` | `u > 1` |
|---|---|---|---|---|
| character | 30.4% | 59.9% | 9.7% | **0.05%** |
| word | 10.9% | 46.8% | 42.3% | **3.30%** |

## Resolution

**Character-level is the primary unit**, on two grounds:

1. Figure 6's top bin is `(0.66, 1]` — the authors' support for `u` ends at 1. The word-level
   reading puts 3.3% of segments *above 1* (edit distance can exceed the mean length when the two
   references differ in length); the character-level reading puts 0.05% there.
2. Character level is the reading whose length profile is closest to Figure 1's ordering, and is
   the conventional reading of "relative edit distance" for raw text.

## Amendment to E00 §A.3 (made before any generation existed)

Because 31% of segments change quartile between readings, the unit is a live researcher degree of
freedom that a single primary choice does not neutralise. The gate is therefore **tightened, not
relaxed**:

> **A.3′** All stratified analyses (Gate B and E01) are computed under **both** readings from the
> same generations — re-stratification costs no extra inference. A gate or law-break claim counts
> as met only if it is met under **both** `u_char` and `u_word`. Character level remains the
> reporting primary; word level is not a fallback to be dropped if it disagrees.

**Gate A verdict: PASS with the recorded reproducibility caveat**, under A.3′.
The substrate is the ACL-2022 quantity as *defined* (eq. 1); it is not a reproduction of the
*plotted* Figure 1 values, and L36 may not claim that it is. If L36 ever states "we reuse the
Stahlberg et al. uncertainty scores", it must cite eq. (1), not Figure 1, and must carry this
discrepancy in the paper.
