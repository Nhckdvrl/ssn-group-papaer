# Pre-registered prediction: the curse should follow the *interface*, not the model

**Date:** 2026-09-14, written before any few-shot beam sweep was run.
**Status:** exploratory extension (E00-EXT), outside the pre-registered E00 gate.

## What prompted it

Termination geometry — `log p(stop immediately | source)`, measured before any beam search:

| system | interface | `log p(stop)` | `log p(greedy)` | empty beats greedy |
|---|---|---|---|---|
| `facebook/wmt19-en-de` | sentence-level NMT | **−9.31** | −18.88 | 61.6% |
| `google/gemma-3-12b-it` | chat template | **−35.33** | −23.02 | 2.3% |
| `Qwen/Qwen2.5-7B-Instruct` | chat template | **−25.98** | −7.02 | 1.3% |
| `Qwen/Qwen2.5-7B-Instruct` | 2-shot plain text | **−15.32** | −43.52 | 99.7% |
| `Qwen/Qwen2.5-7B` (base) | 2-shot plain text | **−9.41** | −34.25 | 100% |

Under a plain few-shot interface (where a translation ends at the line break, as in classic
sentence-level setups), a 2024 decoder-only LM has essentially the **same** termination geometry as
the 2019 encoder-decoder: stopping immediately costs ≈ 9 nats, and the empty hypothesis outscores
the model's own greedy output. The chat interface is what makes stopping astronomically expensive.

## Prediction

If termination geometry is the operative variable, then the beam-search curse is a property of the
**interface**, not of the model generation:

1. `gemma-3-12b-it` under a **chat** interface, RAW beam search: no curse at beam 64
   (0% empty, flat BLEU) — already observed at beams 4 and 16.
2. The **same checkpoint** under a **few-shot** interface with the line break as the stop symbol,
   RAW beam search: the classic curse returns — BLEU falls as the beam widens, length ratio falls,
   empty/near-empty outputs appear.
3. The uncertainty conditioning of that returning curse should again be flat or reversed, not
   concentrated in high-`u` segments.

Falsifier: if the few-shot sweep is as flat as the chat sweep, then termination geometry measured at
step 0 does not govern the curse and the account is wrong.

Grid: first 400 segments of `newstest2019`, beams 1/4/16/64, RAW (`length_penalty = 0`),
`max_new_tokens = 128`, stop symbol = newline, everything else as in the E00 contract.
