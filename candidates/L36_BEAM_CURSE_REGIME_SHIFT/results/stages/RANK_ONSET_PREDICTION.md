# Pre-registered prediction: the beam width at which the curse appears is set by the *rank* of the stop token

**Date:** 2026-09-14, written before the onset sweeps below were run.
**Status:** exploratory (E00-EXT / stage line), outside the pre-registered E00 gate.

## The quantity

At the first generated position, with the interface's stop set (`src/termination.py`):

```
rank_stop = rank of the best stop token in the full next-token distribution
margin    = log p(best non-stop token) − log p(stop set)
```

HuggingFace beam search keeps the top `2b` candidates at the first step, so the "stop immediately"
hypothesis can only *enter* the beam once `2b ≥ rank_stop`. Whether it then *wins* is decided by the
margin, because under RAW (unnormalised) scoring a one-token hypothesis accumulates no further
negative log-probability.

Predicted onset: `b* = ceil(rank_stop / 2)`.

## Measured so far (400 segments, frozen substrate)

| system | interface | margin | `log p(stop)` | median `rank_stop` | `b*` | observed |
|---|---|---|---|---|---|---|
| `facebook/wmt19-en-de` | NMT | +9.09 | −9.57 | **106** | 53 | empty 0.05 % @ b4, 5.4 % @ b16, 6.7 % @ b32, **13.1 % @ b64** |
| `allenai/Olmo-3-1025-7B` (base) | few-shot | +7.70 | −8.67 | **532** | 266 | empty 0 % @ b1, 0 % @ b16 |
| `allenai/Olmo-3-7B-Instruct-DPO` | few-shot | +2.17 | −3.24 | **4** | 2 | empty 17.5 % @ b1, **79.5 % @ b16** |

## Predictions

1. **`Olmo-3-1025-7B` base, few-shot:** no collapse at beam 64 or 128 (`2b < 532`), and a clear
   collapse appearing by beam 512 (`2b = 1024 ≥ 532`). This is the decisive out-of-sample test: the
   model is *predicted to be curse-free where the classic system collapses*, and *cursed* at a beam
   width nobody would normally run.
2. **`gemma-3-12b-it`, chat:** `rank_stop` should be very large (≥ 10³), consistent with the
   observed absence of any collapse through beam 64.
3. Across the Olmo-3 lineage under the **chat** interface, `rank_stop` should be large at every
   post-training stage; under the **few-shot** interface it should collapse toward 1 after SFT.

Falsifier: a system that collapses far below its `b*`, or that stays clean far above it, breaks the
account. In particular, if `Olmo-3` base is still clean at beam 512, rank is not the gating variable.

## Why this matters more than `log p(stop)` alone

`log p(stop)` is a scalar that says the empty hypothesis is *cheap*; it does not say when a search
will *find* it. Rank is the exposure variable and gives a quantitative onset, so the account becomes
a prediction rather than a description — and it explains why the classic 2019 system needs beam ≈ 64
while a post-trained model prompted out-of-format collapses by beam 16.
