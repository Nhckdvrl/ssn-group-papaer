# L14 pilot data schema

Do **not** place LLM-generated main stimuli or LLM-generated gold here.

The runner expects `pilot_items.jsonl`, one row per condition. Each lexical/discourse base should contain at least `POS`, `DN`, `MN`, and `PARAPHRASE` rows with the **same target proposition**.

Required fields:

```json
{
  "base_id": "b001",
  "subtype": "lexical_strength",
  "condition": "MN",
  "text": "The movie wasn't good — it was excellent.",
  "target": "The movie was at least good.",
  "gold": "YES",
  "source": "human_authored_or_classical_source",
  "human_validated": true
}
```

Allowed `condition` values for E01/E02:

- `POS`
- `DN`
- `MN`
- `PARAPHRASE`

Allowed `gold` values:

- `YES`
- `NO`

Recommended `subtype` values:

- `lexical_strength`
- `linguistic_form`
- `scalar_diagnostic` — must remain non-load-bearing

## Validation metadata

Paper-level data should additionally record human audit fields, e.g.:

```json
{
  "naturalness_mean": 4.6,
  "target_reading_agreement": 0.92,
  "world_state_agreement": 0.96,
  "n_annotators": 5
}
```

The code refuses unvalidated rows by default. `--allow-unvalidated-exploratory` exists only for bounded development/debugging and any resulting numbers must be labeled exploratory.

## Source seeds

Use human experimental sources to design/audit items rather than translating them automatically with an LLM:

- Blochowiak & Grisot (2018): https://doi.org/10.5334/gjgl.440
- SWISSUbase Experiment 1: https://www.swissubase.ch/en/catalogue/studies/13418/latest/datasets/1022/1629
- SWISSUbase Experiment 2: https://www.swissubase.ch/en/catalogue/studies/13418/latest/datasets/1023/1630/overview
- Noh et al. (2013): https://doi.org/10.1016/j.pragma.2013.07.005

SWISSUbase reports that Experiment 1 used **16 paired DN/MN stimuli**, three segments (NEG, correction, wrap-up), and picture-grounded human judgments. Treat those materials as design evidence and seed material, not automatically as English benchmark gold.
