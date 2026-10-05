# Data Plan — Incremental Interpretation & Revision

## Principle

**Reuse first; synthesize only to separate explanations.** Garden-path stimuli are calibration data, not the final novelty.

## Sources

| source | files / scale | role | redistribution |
|---|---|---|---|
| Amouyal et al. ACL 2026 release | `extended_gardenpath_experiments.csv` + other difficult-structure CSVs; includes sentence/question/answers/set_id/condition | behavioral positive control + human-aligned task format | follow upstream license; record revision/hash |
| Jurayj et al. BlackboxNLP 2022 | audited revision: 43 NP/Z, 19 NP/S, 28 MV/RR component rows + `make_sents.py` (original plan's 20/20 was inaccurate) | controlled generation of ambiguity, blocker, comma/`that`, unreduced, context/extension variants | Apache-2.0 repo; retain attribution |
| Microsoft Turing Experiments | `Christianson_2001.tsv`, `Alternates_2022.tsv` | independent classical GP replication | keep source provenance; follow repo license |

## Local normalized schema

Do not commit copied upstream data until license/provenance audit is complete. Build a local cache and normalize to:

```text
item_id
source
construction          # NPZ / NPS / MVRR / ...
condition             # gp / non_gp / blocked / explicit_cue / ...
sentence
question_type         # intended / lingering / simple
question
gold
initial_parse_claim
final_parse_claim
ambiguity_start
disambiguator_index
cue_type
extension_length
source_row_id
```

The two crucial labels are:
- `initial_parse_claim`: proposition licensed by the tempting initial interpretation;
- `final_parse_claim`: proposition licensed by the globally correct interpretation.

This lets us measure **residual old-interpretation support and successful new-interpretation support separately**.

## First data build

1. Audit and cache upstream revisions.
2. Reproduce Amouyal GP/non-GP behavior without modifying items.
3. Parse Jurayj component TSVs and generate canonical variants.
4. Unit-test every generated pair:
   - same lexical content except intended manipulation where feasible;
   - gold final interpretation verified;
   - disambiguator position logged;
   - blocker/explicit cue actually removes the intended ambiguity.
5. Hand-audit at least 20 items before any large run.
6. Keep held-out items for any later prompt development.

## What we do NOT build initially

- no 1,000-item synthetic LLM-generated benchmark;
- no human annotation campaign;
- no multilingual expansion;
- no lexical/referential/scope dataset bundle;
- no white-box labels.

Those are conditional on a concrete competing-account question emerging from E00/E01.

## Audit / loader status (2026-10-05)

Pinned revisions, licenses, exact hashes and counts: [D0 audit](results/D0-audit.md), [machine-readable manifest](results/D0-source-audit.json). Local loader: `scripts/data.py`; cache-only normalized data. Missing upstream gold/position stays null. E00 question type is confounded with Yes/No polarity; main readout remains within-set same-question GP/nonGP contrast. Generated Jurayj gold requires a separate pre-inference audit; lexical blocker effects cannot be pooled with same-verb explicit cues.
