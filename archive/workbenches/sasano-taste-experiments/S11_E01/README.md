# S11 E01 — frozen minimal selective-invariance pilot

## Question

Can one open instruct model ignore trailing zeros when only numerical value matters, preserve them when a rounded measurement must support a downstream threshold decision, and ignore an exponent-zero notation change that preserves both value and reporting step?

The three cells share **100 generated central values** (`SEED=110126`). Each base value yields `x.x`, `x.x0`, and `x.x0 × 10^0` strings. The model is cached `Qwen/Qwen2.5-7B-Instruct`; independent chat prompts, bfloat16, greedy decoding, four generated tokens maximum, exact A/B parsing. The initial runtime is batch size 16 with a 2 GiB per-GPU model-placement cap because shared GPUs are occupied. Runtime changes after resource failures require archiving incomplete outputs and rerunning affected items from the beginning.

## Frozen cells and labels

| Cell | Prompts per base | Analytic target |
|---|---:|---|
| Pure value | 1 | `x.x = x.x0` as exact numbers. Ask same/different with balanced polarity. |
| Measurement | 4 | Coarse and fine reports under both explicit and natural preambles. Ask if the report certifies a strict threshold. Coarse: No; fine: Yes, derived from intervals. |
| Notation nuisance | 2 | `x.x0 m` and `x.x0 × 10^0 m` have identical centers and rounding steps. Ask same/different compatible true-value sets, with balanced polarity under both preambles. |

Total: **700 items**. All A/B labels are generated, balanced within every cell × layer (50/50 for 100-item cells, 100/100 for 200-item measurement layers). Measurement thresholds are derived from each center, not chosen by hand. For an `x.x` report the unit step is 0.1 and the compatible true-value interval has half-width 0.05; for `x.x0` the step is 0.01 and half-width 0.005. Thresholds are `x ± 0.02`, inside the coarse interval but outside the fine interval, strictly away from every endpoint. Direction (`greater than` / `less than`) is balanced 50/50. Exact `Decimal` parsing determines value, decimal step, intervals, and certification; it also parses `× 10^0` rather than relying on string equality.

The explicit preamble says the true length was rounded to the last shown decimal place with no other error. This is the **construct-validity layer**: its measurement labels are logical consequences of a stated rule. The natural preamble merely identifies a standard laboratory measurement report. Its labels express the same *conventional precision interpretation*, which the text does not explicitly force; natural misses indicate lack of spontaneous uptake and must not be described as formal logical errors. Keep explicit and natural results separate.

## Primary reporting and interpretation

Report exact accuracy by cell and layer, measurement coarse/fine and threshold direction, and the paired coarse/fine response pattern (`No/Yes`, same answer, or reversed). Never use an LLM judge or CoT grading. The primary selective-invariance profile requires high value and notation invariance together with coarse/fine differentiation in measurement. Predeclare descriptive gates: value and each notation layer ≥90/100; each measurement layer ≥160/200, with ≥80/100 correct in both coarse and fine. A failed explicit layer blocks claims about natural precision semantics.

- **Selective invariance:** all gates pass, including natural measurement.
- **Instruction-only precision:** value/notation and explicit measurement pass; natural measurement fails.
- **Value collapse:** value/notation pass; measurement pairs predominantly receive the same answer, with no explicit-rule competence claim if explicit fails.
- **Surface sensitivity:** value or notation invariance fails materially, whatever measurement performance looks like.
- **Other/mixed:** report the actual cell pattern; do not force it into one label.

The goal is behavioral selective use, not proof of separate internal numerical representations. E01 is discovery data for any new pattern; a new hypothesis requires a fresh held-out seed and frozen E02. No model zoo, prompt search, probing, training, or mechanism work in this phase.

## Freeze procedure

Commit this design, generator/evaluator, tests, and `items.jsonl` **before any main model output**. Run unit tests and deterministic checks; manually inspect several bases across all three cells and both measurement layers. Check parser exactness, item IDs, shared value templates, interval nesting, strict threshold gap, label balance, and identical explicit/natural bodies. If a bug is found after inference, archive the affected raw batch, commit the correction, and rerun from the beginning; never pool versions.
