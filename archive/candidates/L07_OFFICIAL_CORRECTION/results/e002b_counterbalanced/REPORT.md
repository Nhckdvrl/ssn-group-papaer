# E002b Counterbalanced Model Pilot

**Verdict:** GO for 150-item expansion; no paper claim yet.

## Design

- 10 items whose original excerpt contains the old selector and not the new selector.
- Publisher notice explicitly contains both old and new content.
- Three cached instruction models: Gemma 3 12B, Mistral Small 24B, Qwen 2.5 32B.
- Six evidence conditions.
- Every item/condition is run twice with A/B candidate order reversed.
- 120 decisions per model, 360 total; greedy decoding.

E002a fixed OLD in the first candidate position. Mistral's strong first-option tendency made that run non-identifying; it is retained under `results/e002a_fixed_old_first/` as a design event and is not claim evidence.

## Results

| Model | Original only | Correction only | Flat, mean document orders | Explicit update | Unrelated correction |
|---|---:|---:|---:|---:|---:|
| Gemma 3 12B | 100.0 | 85.0 | 62.5 | 75.0 | 95.0 |
| Mistral Small 24B | 80.0 | 70.0 | 65.0 | 70.0 | 65.0 |
| Qwen 2.5 32B | 95.0 | 85.0 | 82.5 | 85.0 | 95.0 |
| Macro mean | 91.7 | 80.0 | 70.0 | 76.7 | 85.0 |

Requiring correctness under both A/B orders reduces flat accuracy to 50% for Gemma, 40% for Mistral, and 80% for Qwen (macro 56.7%). Explicit update improves macro accuracy by 6.7 points over flat but is not a complete remedy. Document order has little aggregate effect in this small pilot; candidate position does.

## Interpretation boundary

This pilot rejects the immediate kill condition that strong models simply copy the corrected value at ceiling. It does not establish a general failure rate: n=10 is small, the task is forced choice, and Mistral also shows false overrides under the unrelated-correction control. The scaled experiment must add free generation, larger natural contexts, confidence intervals, and enough items for correction-type and locality analyses.

Reproduce each model with `scripts/run_model_pilot.py`, then:

```bash
.venv/bin/python scripts/summarize_model_pilot.py
```
