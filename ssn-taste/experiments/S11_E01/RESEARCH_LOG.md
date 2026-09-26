# S11 E01 research log

## Observation

Frozen design commit: `55c19a2`. One model, `Qwen/Qwen2.5-7B-Instruct` (revision `a09a35458c702b33eeacc393d103063234e8bc28`), greedy decoding. There are 100 base values and 700 prompts. Exact parser invalids: 0.

| Cell | Correct / total | Relevant structure |
|---|---:|---|
| Pure value | 100/100 | Same value despite trailing zero. |
| Measurement, explicit rounding rule | 58/200 | Coarse 7/100; fine 51/100. Correct coarse No/fine Yes pairs: 0/100; same response: 58/100; reversed: 42/100. |
| Measurement, natural report | 100/200 | Coarse 50/100; fine 50/100; all 100 pairs received the same response. |
| Notation nuisance, explicit | 98/100 | Exponent-zero notation preserved the interval almost always. |
| Notation nuisance, natural | 100/100 | Same interval. |

The explicit measurement error is strongly directional. For the 50 `greater than` bases, both coarse and fine received Yes in every pair. For the 50 `less than` bases, 42 pairs received **coarse Yes/fine No**, the opposite of the analytic target; seven received No/No and one Yes/Yes. In the natural layer, every `greater than` pair received Yes/Yes and every `less than` pair No/No. Thus a single measurement accuracy number conceals a systematic response pattern.

Example: `33.8 m` and `33.80 m`, threshold `33.82 m`, ask whether the true length is certainly **less** than the threshold. The explicit intervals are `[33.75, 33.85)` and `[33.795, 33.805)`. The correct answers are No and Yes. The model answered Yes and No. For the natural preamble it answered No to both.

## Validity

The committed generator and tests passed before inference. Exact `Decimal` parsing derives every center, reporting step, interval, threshold, and label. Each threshold is strictly between a coarse and fine endpoint and never on a boundary. All 100 base IDs have the seven planned prompts; cell/layer answer labels are balanced; the explicit and natural measurement question bodies match. The raw file has 700 unique item IDs, uniform model revision and runtime settings, and zero invalid A/B parses. Independent inspection of the example above confirms the scorer's direction and labels. No E01 design, items, or scorer was changed after the frozen commit.

The explicit measurement layer missed its predeclared construct-validity gate of at least 160/200 and at least 80/100 for each reporting precision. Consequently the natural layer cannot establish whether the model spontaneously uses conventional measurement precision. Its 100/200 is only a description of its responses under that preamble.

## Interpretation candidates

1. The model may compare the displayed center with the threshold and fail to quantify over the compatible true-value interval. This is consistent with the natural layer's complete within-pair collapse and the explicit `greater than` Yes/Yes pattern, but does not alone explain the explicit `less than` reversal.
2. The explicit rounding instruction, the word `certify`, and inequality direction may interact to induce an unstable or inverted decision rule. The `less than` reversal suggests more than a uniform inability to parse trailing zeros. This is a behavioral possibility, not a mechanism claim.
3. There could be a residual numerical or question-form artifact. The analytic labels and parser checks rule out the obvious generator/scorer errors, but one batch cannot establish that the direction asymmetry is stable.

## Knowledge consequence

E01 demonstrates value and notation invariance for this model, but **does not demonstrate selective invariance**. It also does not cleanly establish either value collapse or instruction-only precision: the explicit rule condition fails, and 42 explicit pairs are reversed rather than collapsed. The mother question remains open for this model and formulation.

## Next decisive experiment

Freeze a new, disjoint 60-base E02 batch before output. Keep the exact E01 explicit measurement preamble, question, labels, parser, model, and decoding; use no natural or new wording. The primary replication target is the paired pattern separately for `greater than` and `less than`. If the same asymmetry recurs, treat it as a reproducible behavioral observation, while withholding a precision-semantics conclusion. E02 is not a prompt repair or a new benchmark.

## Current verdict

**continue original RQ**, limited to this one held-out replication of the unexpected explicit-layer behavior. E01 alone did not pass the validity gate for the intended selective-invariance claim.
