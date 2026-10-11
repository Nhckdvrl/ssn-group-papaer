# L03-E000 — ACS data feasibility and gold-contract audit

**Status:** protocol fixed before observation acquisition; no model experiment.
**Date:** 2026-09-08. **Runtime:** Python 3, standard library only.

## Purpose and decision

Establish whether the selected official data support a pilot with traceable labels.
This audit cannot decide whether generation needs an explicit status representation.
The protocol is locally versioned, not externally preregistered.

The selected release, variables, counties, selection rationale, and thresholds live
in `protocol.json`. Initial access probes received only a Missing Key page; no
observation outcomes informed selection. Metadata were accessible. Selection is
purposive: these tables are expected to expose relevant states. Frequencies cannot
be generalized to all ACS tables, and eight variables do not provide eight
independent provider conventions.

## Independent gold and conservative exclusions

Authority: [Census estimate/annotation notes](https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html),
accessed through web retrieval on 2026-09-08; each run attempts to save actual
source bytes and SHA-256. The initial direct HTML request failed, so raw-source
archival remains incomplete and is explicitly a readiness blocker.
The page currently covers estimates and margins of error together; this experiment
uses estimates only. The following identifiers are implementation names for provider
categories, not a claim that our ontology is new.

| Estimate + annotation | Gold identifier | Exact scalar? |
|---|---|---|
| Ordinary number + null annotation | VALUE | Yes, including zero and ordinary negatives |
| -666666666 + `-` | NOT_COMPUTABLE | No; do not infer which documented cause applies |
| -999999999 + `N` | NOT_DISPLAYABLE_INSUFFICIENT_CASES | No |
| -888888888 + `(X)` | NOT_APPLICABLE_OR_NOT_AVAILABLE | No; do not split the disjunction |
| null + null | NO_DATA_FOR_GEOGRAPHY | No |
| Numeric bound + median annotation ending in `+` or `-` | MEDIAN_LOWER_BOUND / MEDIAN_UPPER_BOUND | Bound only; not an exact median |

Unknown annotations, mismatched bounds, mismatched sentinels, and MOE-only codes
are retained as unresolved and prevent readiness. Empty annotations are not silently
treated as null. These conservative restrictions can exclude valid provider cases;
resolve such cases with an explicit protocol revision and official evidence.
Do not infer suppression, unreliability, or a specific absence cause beyond the
provider's actual distinction.

## Outputs and provenance

Every new run has an immutable directory name and contains:

- the executed script and protocol snapshots;
- request URLs without API keys, HTTP status, response hashes, and errors;
- original response bytes, including HTML error pages when returned;
- the estimate/annotation metadata inventory;
- deterministic observation JSONL with source hashes and unresolved records;
- the machine-readable decision and observed coverage.

No credentials are persisted. A successful HTTP status is insufficient: HTML and
invalid JSON do not become observations. Missing source data do not become a
measured zero count. A partial run is blocked even if one acquired subset is large.
Raw files with a `.json` suffix may contain a server's HTML error response; the
manifest records that failure explicitly.

The geographic unit is the county; observations are county × variable. County,
table, and variable dependencies prohibit treating all cells as independent trials.
This audit uses descriptive counts only: no significance tests, confidence
intervals, model rankings, or Account A/B decisions.

## Gate before model calls

The automated count gate requires at least 50 cells across at least 20 counties in
each of VALUE_NONZERO, VALUE_ZERO, NOT_COMPUTABLE, and
NOT_APPLICABLE_OR_NOT_AVAILABLE. These are feasibility thresholds, **not power
calculations**. Other documented statuses are reported if observed; their absence
must not be represented as coverage. Unknown pairs or unavailable sources block
the gate. Insufficient coverage calls for a documented revision or a data-gate
decision, never silent adaptive sampling.

Even `COUNTS_READY_FOR_MANUAL_AUDIT` is not authorization to claim Phase 0 complete:
review raw-to-gold examples across every observed status and all unresolved cases;
validate natural table rendering against provider displays; then freeze the model
pilot protocol. Gold fields and raw API annotations must not leak into the natural
TableQA prompts. The official displayed symbol is legitimate input.

## Reproduction

From the repository root:

```sh
python3 -B -m unittest discover -s good/L03_TYPED_OBSERVATION/experiments/E000_data_audit -v
python3 -B good/L03_TYPED_OBSERVATION/experiments/E000_data_audit/audit.py --run-id UNIQUE_RUN_ID
python3 -B good/L03_TYPED_OBSERVATION/experiments/E000_data_audit/audit.py --run-id UNIQUE_REPLAY_ID --replay ORIGINAL_RUN_ID
```

For authenticated acquisition, configure `CENSUS_API_KEY` in the process environment;
do not put it into command arguments, files, or research logs. Runs refuse to
overwrite existing directories. Replay uses the original protocol snapshot and
verifies its hash and raw response hashes without accessing the network. The
current script is separately snapshotted and hashed. A replay of blocked acquisition should
remain blocked. Exit code 2 means the count gate was not passed; it is intentional.
Synthetic unit-test fixtures verify software behavior, not empirical results.

## Changes and subsequent experiments

Never overwrite an old protocol snapshot, raw response, or run result. Change the
working protocol version, explain why in the experiment log, and use a new run ID.
Exploratory scope changes must remain distinguishable from confirmatory testing.

Before E001, specify: exact model/version and generation settings; identical
evidence and permitted abstention across conditions; direct versus structured
one-stage versus two-stage contrasts; total token/call budgets; geography/table
splits and development-only prompt tuning; human or deterministic answer coding
with blinded adjudication; denominators and malformed-output policy; paired and
cluster-aware uncertainty; effect/equivalence margins with power justification;
and primary versus secondary hypotheses. A two-stage advantage alone does not
establish representation necessity because it also changes computation and format.

Any claim of safe removal needs equivalence/non-inferiority evidence, not an
insignificant difference. Any claim beyond ACS needs independently verified
cross-provider data and transfer tests. Novelty must be re-audited before paper
promotion; E000 does not renew the prior novelty verdict.
