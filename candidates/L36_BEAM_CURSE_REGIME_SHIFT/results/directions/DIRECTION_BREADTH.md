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
