# E001b — Direct native-label validation

Completed both frozen runs: 84 jobs per model, 168 total, with **zero invalid
responses**. Exactly the E001a samples, contexts, target markers and role
definitions are retained; only the A/B mapping is replaced by direct greedy
generation of DNI or INI (max_new_tokens=8). This is exploratory validation
triggered by E001a, not a confirmatory method comparison. No outputs discarded.

| Model | Context | Correct / 42 | Complete pairs correct / 21 | DNI predictions / 42 |
|---|---|---:|---:|---:|
| Qwen3-32B | Sentence | 20 | 2 | 37 |
| Qwen3-32B | Full story | 20 | 0 | 41 |
| Mistral-Small-24B-Instruct-2501 | Sentence | 24 | 3 | 17 |
| Mistral-Small-24B-Instruct-2501 | Full story | 20 | 0 | 41 |

Qwen has 3 wrong→right and 3 right→wrong transitions with full context; Mistral
has 10 and 14. A decline in aggregate accuracy is **not replicated across both
models**. Both favor DNI with full context, but the size of that shift differs.
Do not infer a general context-harm law.

The one full-context INI prediction differs between models: Qwen `s12_f6_e3`
(Measure_duration / Process); Mistral `s272_f4_e1` (Calendric_unit / Whole).
Both are source DNIs. All 21 source INIs receive DNI predictions in both full
runs. This is an **interpretation-label tendency**, not 21 independently verified
unsupported fillers.

The selection is gold-balanced within 21 frame-role strata from one training
story, not a prevalence sample or independent test. Source terminal rendering
retains tokenization and encoded punctuation. No few-shot demonstration, prompt
ensemble, new human adjudication of the 42 cases, or calibrated uncertainty claim.

This check removes arbitrary letter mapping and makes native output inspectable.
It does not establish intrinsic inability to represent the distinction, a benefit
of status-first grounded extraction, or context-induced hallucinations. DUST and
the classical interpretation literature remain the comparison; H01–H03 are not
promoted. `analysis.json` retains all decisions. The four-run provenance check in
`runs/verification_models_20260908.json` verifies 504 total records over the same
42 samples, script/input/output hashes and E001b's unchanged context/role text.
