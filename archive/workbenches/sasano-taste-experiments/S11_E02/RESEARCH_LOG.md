# S11 E02 research log

## Observation

Frozen E02 design/items commit: `e208230`. The same cached `Qwen/Qwen2.5-7B-Instruct` revision (`a09a35458c702b33eeacc393d103063234e8bc28`) answered 120 new explicit-rule prompts from 60 central values disjoint from E01. Exact A/B parsing: 120/120 valid.

| Direction | Correct coarse No/fine Yes | Yes/Yes | No/No | Reversed Yes/No |
|---|---:|---:|---:|---:|
| Greater than (30 pairs) | 0 | 30 | 0 | 0 |
| Less than (30 pairs) | 0 | 0 | 3 | 27 |

The prespecified descriptive replication criterion passed: `greater than` had at least 25/30 Yes/Yes (actual 30/30), and `less than` had at least 20/30 reversed (actual 27/30). Overall analytic correctness was 33/120; coarse 3/60 and fine 30/60. Thus the explicit measurement construct-validity gate again failed. This replication establishes that the E01 direction-dependent response pattern is stable across two held-out numeric batches under the same prompt and model, not why it occurs.

## Validity

The E02 generator selects 60 E01-unused central values with seed `110226`. Tests passed before inference, including item-file determinism, E01 disjointness, matched coarse/fine pairing, exact interval labels, strict non-boundary thresholds, balanced directions and labels, and the A/B parser. Four bases were manually inspected before the freeze. The E01 explicit preamble, question template, scorer, model, and decoding were reused unchanged. The 120 raw IDs are unique, their stored labels match the frozen items, and all parses are valid. No E01 or E02 frozen item was modified after output.

## Interpretation candidates

1. The model may compare the displayed center with the threshold instead of asking whether **all** true values compatible with the rounded report satisfy the inequality. This explains both natural-layer collapse in E01 and E02's Yes/Yes `greater than` pattern, but does not fully explain the reversed `less than` pairs.
2. The asymmetric `less than` reversal may arise from how the model combines the explicit rounding instruction with `certify` and the inequality direction. It may apply an incorrect direction-sensitive heuristic rather than a general center comparison. These two explanations remain unresolved.
3. A stable wording or response-format artifact is also possible. E02 repeats the same prompt by design, so numeric replication does not distinguish a task-form effect from a broader limitation in interval reasoning.

## Knowledge consequence

The current S11 E01/E02 **does not support selective invariance** or spontaneous measurement-precision use. Mathematical-value and exponent-zero-notation invariance were strong in E01, while downstream threshold certification failed even with explicit rounding semantics and then failed again on held-out values. The stable direction asymmetry is a real response pattern for this exact task; it is not an independently identified measurement-semantics phenomenon.

## Next decisive experiment

If S11 continues, use a new held-out batch for one construct diagnostic: provide the exact compatible interval explicitly and ask the same universal threshold question, then compare that with a rounded-report version on matched values. This would isolate interval construction from interval-based certification. Freeze its wording, labels, and interpretation before output. Do not vary many prompts, add models, or treat E01/E02 as validation of a newly proposed heuristic.

## Current verdict

**KILL the current S11 E01 task formulation as evidence for selective invariance.** The original mother question remains unanswered; any further S11 work needs a separately frozen construct diagnostic. Do not promote the direction asymmetry to a new mother question without a targeted novelty check and independent experiment.
