# S11 E03 research log

## Observation

Frozen design and item commit: `d48fdc9`. The same `Qwen/Qwen2.5-7B-Instruct` revision (`a09a35458c702b33eeacc393d103063234e8bc28`) answered 320 new prompts from 80 base values disjoint from E01/E02. Runtime matched E01/E02: bfloat16, greedy decoding, batch 16, 2 GiB per-GPU model-placement cap, maximum four new tokens. All 320 raw answers were exact A/B parses.

| Evidence | Greater coarse | Greater fine | Less coarse | Less fine |
|---|---:|---:|---:|---:|
| Rounded report | 0/40 | 40/40 | 4/40 | 2/40 |
| Explicit interval | 16/40 | 40/40 | 40/40 | 40/40 |

Each count is analytic correctness. Every base has the target coarse No/fine Yes. Matched response patterns:

| Evidence | Direction | Correct No/Yes | Yes/Yes | No/No | Reversed Yes/No |
|---|---|---:|---:|---:|---:|
| Rounded report | Greater | 0 | 40 | 0 | 0 |
| Rounded report | Less | 0 | 2 | 4 | 34 |
| Explicit interval | Greater | 16 | 24 | 0 | 0 |
| Explicit interval | Less | 40 | 0 | 0 | 0 |

Thus direct intervals repair the `less than` decisions on this batch, but do **not** make the `greater than` coarse decision stable. For example, the interval `[28.85 m, 28.95 m)` cannot certify a true length greater than `28.88 m`, yet the model answered Yes. The explicit-interval `greater/coarse` cell is 16/40, well below the frozen 34/40 gate, and has only 16/40 correct coarse/fine pairs versus the 30/40 gate. This is preregistered Pattern D.

## Validity

The generator and tests passed before inference. `Decimal` derives every center, interval, threshold, and label; no threshold touches an interval endpoint. The pool contains 80 unique central values absent from E01/E02, balanced 40/40 by inequality direction. Each base has four matched prompts, and every direction × representation × precision cell has exactly 40 items. The rounded-report template is exactly the frozen E01/E02 explicit-rule template apart from new numbers; the downstream question sentence is identical in both E03 representations. Manual inspection covered four spread-out bases before the freeze. Raw IDs and expected labels match the frozen item file in order, model revision and runtime settings are uniform, and all 320 parser outputs are valid. E01/E02 files were not modified.

The rounded-report arm also reproduces the old behavior: all 40 `greater than` pairs are Yes/Yes; 34/40 `less than` pairs are reversed Yes/No. The E03 interval result is therefore not explained by a model or runtime change.

## Interpretation candidates

1. A rounded report may fail to evoke the correct compatible interval, as the `less than` improvement after giving the interval suggests. E03 does **not** identify this as the sole failure source.
2. The downstream universal-certification readout itself fails in at least one direction: 24/40 coarse `greater than` interval items receive Yes although the stated interval straddles the threshold. This could reflect center-comparison or question-form behavior; E03 does not separate those explanations and does not promote either to a new research question.

## Knowledge consequence and verdict

**KILL current S11 threshold route.** E03 establishes that interval → certified decision is not stable even when the interval is explicitly supplied. Report → interval construction may also contribute, particularly to the `less than` errors, but the current readout cannot cleanly identify its contribution or support selective-invariance claims. No further prompt strengthening, CoT, model additions, or mechanism work on this route.

## Next decisive experiment

None within the current threshold route. Any future S11 attempt would require an independently motivated and newly frozen instrument, not iterative repair of this readout or reuse of E01–E03 as validation data.
