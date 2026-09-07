# L03 — Data and Independent Gold

**Core rule:** the load-bearing status labels must come from the data provider, not from our interpretation of what a symbol “seems to mean.”

---

## 1. Primary decisive substrate — U.S. Census ACS

Official ACS developer documentation exposes estimate variables and paired annotation variables.

Current official behavior:
- estimate variables may return sentinel numeric values;
- annotation variables provide character representations when ordinary numeric information is not the correct representation;
- example: estimate value -888888888 paired with annotation (X);
- Census documentation defines (X) as “not applicable or not available.”

Primary documentation:
- https://www.census.gov/data/developers/data-sets/acs-5year.html
- https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html

This is unusually strong gold because:
- the source is official;
- the semantics predate the experiment;
- the status is machine-readable;
- the evaluated model does not create or judge the label.

---

## 2. Load-bearing unit of analysis

For each estimate/annotation pair:

- table/group identity;
- geography;
- variable;
- visible estimate representation;
- annotation value, if present;
- provider-defined interpretation;
- local table/variable metadata;
- documentation excerpt needed to infer the meaning.

The target should be expressed as an **observation object** with:

- observation status;
- scalar value only when the status licenses one;
- qualification/status text where applicable.

The exact experimental label inventory must be derived deterministically from official documentation.

---

## 3. Distinguish the critical cases

The dataset must contain enough examples of:

### A. Genuine numeric values
A scalar exists and should be returned.

### B. Genuine zero
The value is zero, not missing.

### C. Provider-defined non-value
The provider explicitly says the ordinary scalar is not applicable/available or otherwise replaced by a status.

### D. Qualified / suppressed observations
Only include if the source provides a clean externally defined state and exact mapping.

Do not merge C and D into generic “N/A” if the source distinguishes them.

---

## 4. Rendering for natural TableQA

The experiment should not simply hand the model the raw API annotation field.

Construct natural evidence packages from:
- table snippet;
- row/column headers;
- visible displayed symbol/value;
- relevant legend, note, or official documentation;
- natural-language question.

The core test is whether the model can infer the provider-defined semantics from the evidence a real user would have.

A secondary structured/API condition may be useful as an upper bound, but it must not replace the natural-table condition.

---

## 5. Memorization control

ACS alone creates a risk that a strong model has memorized common sentinel codes.

Required controls:

1. documentation absent vs documentation present;
2. surface-form perturbation that preserves provider meaning only if done without inventing new semantics;
3. unfamiliar table groups/years;
4. ideally a second provider with independently defined status conventions.

The strongest transfer design is:
> same scientific output ontology, new provider-local symbol/status mapping.

---

## 6. Cross-provider replication status

CDC/NCHS provides a strong natural neighboring substrate:
- official tables can suppress unreliable estimates;
- asterisks and notes may represent reliability/suppression states;
- Data Query System outputs include downloadable source data plus data-issue/footnote notes.

Official references:
- https://www.cdc.gov/nchs/hus/sources-definitions/statistical-reliability.htm
- https://www.cdc.gov/nchs/dqs/user-guide/index.html
- https://www.cdc.gov/united-states-cancer-statistics/technical-notes/suppression.html

**Important:** this is not yet part of the load-bearing gold contract merely because the documentation exists.

Before using CDC/NCHS as Main-level replication, verify:
- an exact accessible table/data file;
- a machine-readable or deterministic status marker;
- a one-to-one mapping to provider-defined meaning;
- enough instances for stable analysis.

Until then, ACS alone supports the pilot; cross-provider replication remains a required pre-mainline task.

---

## 7. Primary metrics

Pre-specify:

- observation-status accuracy / macro-F1;
- false scalarization rate;
- false missingness rate on genuine numeric values;
- value accuracy conditional on status = VALUE;
- status confusion matrix;
- direct generation vs explicit status→value difference;
- documentation gain;
- familiar-source vs unseen-source transfer.

Ranking change is optional evidence, not the only success condition.

---

## 8. Data validity kill conditions

KILL or demote if:

- annotation semantics cannot be deterministically mapped;
- status-bearing cells are too rare for a stable pilot;
- natural rendering hides information that a real source user would have;
- the experiment is really code memorization;
- cross-provider replication needed for the main claim cannot be secured;
- label inventory requires author judgment rather than provider documentation.

The scientific quantity must remain externally grounded.
