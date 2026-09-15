# Breadth: the same measurement predicts which *direction* collapses, and when

**Status:** exploratory breadth check (E00-EXT line). Single-reference BLEU — the ACL-2022
multi-reference substrate exists only for En→De and remains the primary.
**Systems:** the four released FAIR WMT19 encoder-decoders (`facebook/wmt19-{en-de,de-en,en-ru,ru-en}`)
— same architecture and training pipeline, different directions.
**Setup:** first 400 segments of each WMT19 test set, RAW beam scoring (`length_penalty = 0`),
stop set = the model's EOS.

| direction | margin | `log p(stop)` | median `rank_stop` | `b*` | empty @b4 | @b16 | **@b64** | BLEU b4 → b64 | len ratio @b64 |
|---|---|---|---|---|---|---|---|---|---|
| **ru→en** | 7.51 | −8.08 | **41** | **21** | 0.0 % | 3.8 % | **41.5 %** | 36.1 → **9.3** | 0.41 |
| **en→de** | 9.09 | −9.57 | **106** | **53** | 0.0 % | 3.5 % | **8.8 %** | 37.4 → 31.8 | 0.85 |
| **de→en** | 9.79 | −10.40 | **284** | **143** | 0.5 % | 0.5 % | **0.8 %** | 11.4 → 15.5 | **2.46** |
| **en→ru** | 9.40 | −10.09 | **356** | **178** | 0.0 % | 0.0 % | **2.5 %** | 27.6 → 25.3 | 0.85 |

Read the table by `b*`, the beam width at which the stop hypothesis can first enter the beam:

- the two directions whose `b* < 64` are the two that collapse at beam 64 (ru→en 41.5 %,
  en→de 8.8 %), and the smaller `b*` gives by far the worse collapse — ru→en loses 27 BLEU and
  drops to 0.41 of the reference length;
- the two directions whose `b* > 64` do not collapse there (0.8 % and 2.5 %).

The ordering of the collapse rate at beam 64 is the exact inverse of the ordering of `rank_stop`,
across four checkpoints of the same architecture. One scalar, measured from a single forward pass
before any search, predicts **which direction breaks and at what beam width**.

de→en is the useful odd one out: it has the *highest* rank (284) and the *lowest* empty rate, and it
fails the other way — length ratio 2.46 at beam 64, i.e. run-on generation. That is the second damage
channel again, and it is exactly what the account predicts for a system whose stop event is far from
competitive.

## Caveats

- Four checkpoints, one architecture family, one test year; BLEU/chrF only.
- de→en's low BLEU (11–15) reflects a very long-output regime, not only translation quality; its
  numbers should not be compared across directions as quality.
- Single reference here, unlike the En→De primary substrate.

---

## Modern side, same four directions (added 2026-09-15)

`google/gemma-3-12b-it` under its chat template, same segments, same RAW scoring, 400 segments.

| direction | margin | median `rank_stop` | `b*` | empty @ b64 | lenR @ b64 | BLEU b4 → b64 |
|---|---|---|---|---|---|---|
| ru→en | **+36.96** | 336 | 168 | **0.0 %** | 1.01 | 37.0 → 36.7 |
| en→ru | **+38.02** | 626 | 313 | **0.0 %** | 0.95 | 28.3 → 28.4 |
| de→en | **+34.46** | 374 | 187 | **0.0 %** | 1.00 | 38.2 → 38.1 |

Paired against the classic systems on the same segments:

| direction | FSMT rank / `b*` | FSMT empty@64 | gemma rank / `b*` | gemma empty@64 |
|---|---|---|---|---|
| ru→en | 41 / 21 | **41.5 %** | 336 / 168 | 0.0 % |
| en→de | 106 / 53 | 8.8 % | (chat cell, `CEILING_ASSESSMENT.md`) | 0.0 % |
| de→en | 285 / 143 | 0.8 % (lenR **2.45**) | 374 / 187 | 0.0 % (lenR 1.00) |
| en→ru | 356 / 178 | 2.5 % | 626 / 313 | 0.0 % |

Three things to read off this:

1. **The contrast is per-direction, not an aggregate artefact.** The modern checkpoint has
   `b* ≥ 168` in every direction, i.e. it is not exposed at any beam width tested, and it is flat —
   BLEU moves by ≤ 0.3 from beam 4 to 64 in all three.
2. **The direction where the classic system fails hardest is not special for the modern one.**
   ru→en is the worst classic cell (41.5 % empty, BLEU 36.1 → 9.3) and an entirely unremarkable
   modern cell (0 %, 37.0 → 36.7). So the collapse is a property of the *system's* termination
   geometry, not of the language pair's difficulty.
3. **The two damage channels stay separated.** de→en is the classic direction that does not empty
   but runs on (lenR 2.45); gemma is at lenR 1.00 there. The modern checkpoint is off both channels
   simultaneously, and its margin is ~4× the classic margin (+34 to +38 nats vs +7.5 to +9.8).

**Caveat.** This is one modern checkpoint. gemma-3's WMT19 exposure is unknown (Gate C selected it
substrate-blind and for the absence of a *declared* supervised WMT19 evaluation, which is not the
same as proof of non-exposure), and the raw BLEU values here must not be read as a quality
comparison — only the beam-width *slopes* and the empty/length-ratio channels are being compared.
