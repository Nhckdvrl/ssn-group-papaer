# L03 experiment log

## 2026-09-08 — L03-E000, data feasibility

**Decision:** continue data preparation; Phase 0 incomplete; model pilot blocked.
**Starting repository revision:** `820818d3b1dffc0dc74979761dc7e30c8933080f`.
**Write scope:** this project directory only.

L03 was selected because its official API and provider-owned status semantics
offer a direct route to auditing gold before model work. L02 requires recovery of
an older task resource; L04's package explicitly identifies higher novelty risk.
This is a prioritization judgment, not evidence that L03 will yield a stronger paper.

### Executed work and evidence

| Record | Actual outcome | Permitted interpretation |
|---|---|---|
| Initial access probes | Two observation queries returned HTTP 200 HTML titled Missing Key; one B19013 metadata query returned JSON. A bulk-download directory probe returned HTTP 520. | Access reconnaissance only; no experimental observations or frequencies. |
| [Primary run](experiments/E000_data_audit/runs/20260908_access_audit/report.json) | Four metadata files acquired; all four observation requests returned `API_KEY_REQUIRED_HTTP_200_HTML`. Direct notes HTML retrieval failed with HTTPError. | Acquisition blocked, not zero status prevalence. |
| [Metadata inventory](experiments/E000_data_audit/runs/20260908_access_audit/inventory.json) | B01001: 49 pairs; B19013: 1; B19013D: 1; S0101: 228. Eight estimate fields selected, each paired with an annotation field. | Metadata structure verified; actual annotation values and sample size unverified. |
| [First offline replay](experiments/E000_data_audit/runs/20260908_offline_replay/report.json) | Reproduced the blocked report. An absent notes cache was recorded as FileNotFoundError. | Software replay only; no new acquisition. |
| [Verified offline replay](experiments/E000_data_audit/runs/20260908_verified_replay/report.json) | After preserving original acquisition errors in replay, report, inventory, observations JSONL, and unresolved JSON are byte-identical to the primary run. All available source, script, and protocol hashes verified. | Reproduction of the same evidence, not independent replication. |
| Software validation | Nine unit tests passed, including label drift, scalar/zero distinction, bounded medians, unknown pairs, duplicate units, and schema failures. | Parser behavior on synthetic fixtures only. |

**Model calls:** 0. **Acquired empirical observations:** 0.
No accuracy, effect size, confidence interval, hypothesis verdict, or paper-level
conclusion is reported. An empty observations file must not be used as a dataset.

### Protocol amendment before observations

The original protocol is preserved inside the primary run. Version 1 selected
`S0101_C02_031E` based on the current documentation example's variable numbering.
The retrieved 2023 metadata identifies it as the percentage aged 75 years and over,
not the intended sex-ratio cell. Version 2 instead selects `S0101_C03_033E`, whose
official label identifies a sex ratio in the Male column. The script now checks
that exact label and the corresponding annotation field. This correction was
validated against archived metadata. Its presumed `(X)` value is **not observed**.
Version 2 has not been used for a new acquisition; do not combine it with version 1
results as though they came from the same run.

The amendment responds to schema/semantic evidence, not model outcomes or observed
status frequencies. All other selected variables and thresholds remain fixed.

### Source verification and limitations

The official [ACS 5-year developer page](https://www.census.gov/data/developers/data-sets/acs-5year.html)
now explicitly requires keys for data queries. `CENSUS_API_KEY` was not configured
in this process. This corroborates the saved error responses.

The [official annotation notes](https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html)
were readable using the web retrieval tool. Its [parsed response snapshot](experiments/E000_data_audit/sources/official_notes.web.json)
and SHA-256 are archived separately; this is **not raw publisher HTML** and does
not silently substitute for the failed acquisition recorded in the run manifest.
The notes support the conservative gold mapping, including combined `(X)` semantics
and non-exact median bounds. No frequency or provider-transfer claim follows.

### Next executable step

Configure a Census key as `CENSUS_API_KEY` in the execution environment, then run
the v2 audit under a fresh run ID. Do not put the key in this repository or in a
research log. Resolve/document the direct notes archival failure as well; the
current implementation conservatively blocks readiness without that source.

Once acquisition succeeds: inspect all unresolved cases and status coverage;
audit parser outputs against raw rows; validate natural table rendering; then
write and freeze E001's model/evaluation protocol with justified margins and
uncertainty analysis. Cross-provider gold and a fresh novelty audit remain required
before any paper-mainline decision. None of these gates has been waived.
