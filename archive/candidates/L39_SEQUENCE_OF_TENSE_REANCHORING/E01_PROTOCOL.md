# L39 E01 Protocol — Human-Validated Sequence-of-Tense Core

**Authorization:** `E01 ONLY`  
**Parent:** `candidates/L39_SEQUENCE_OF_TENSE_REANCHORING/README.md`  
**Goal:** cheap, decisive go/no-go test before any project expansion.

---

## 0. E01 must answer one question

> **When English past-under-past permits a simultaneous interpretation, do strong LLMs preserve that context-relative interpretation, or do they incorrectly treat embedded past as requiring anteriority?**

Do not use E01 to explore every tense phenomenon. Do not optimize for a publishable effect. The job is to decide whether L39 has a real mother phenomenon.

---

## 1. Pre-run owner sanity check

Before any model run, spend a bounded search checking only direct ownership of this parent RQ.

Search exact and conceptual variants around:

- Sequence of Tense + LLM;
- past-under-past + language model;
- embedded tense + LLM;
- simultaneous reading + LLM/transformer;
- context-relative tense interpretation + LLM;
- SOT downstream inference / temporal re-anchoring.

Check ACL/EMNLP/NAACL/TACL, arXiv 2025–2026 and obvious author successors.

If a paper already directly tests whether modern LLMs license/deploy the simultaneous past-under-past interpretation in downstream inference, STOP and report the collision. Do not shrink the claim.

---

## 2. Source recovery and provenance manifest

Primary source:

Mucha, Renans & Romoli (2023), *Sequence of tense and cessation implicatures: evidence from Polish*, NLLT, DOI `10.1007/s11049-022-09545-2`.

Recover the English Experiment-1 materials from Appendix A.

Create a machine-readable file such as:

`data/e01_mucha_sot_core.jsonl`

Each row should preserve at least:

- `source_paper`
- `source_experiment`
- `original_item_id`
- `original_condition`
- `language`
- `source_context`
- `indirect_report`
- `matrix_verb`
- `embedded_predicate`
- `context_relation` (`shifted` / `simultaneous` as defined by the source experiment)
- `report_tense` (`past` / `present`)
- `task_variant`
- `gold_type` (`human_accuracy_judgment`, `compatibility`, `non_entailment`, control type)
- `adapted` boolean
- `adaptation_note`
- `license_note`

Verify and record that the reused article/material is licensed for the intended use. Do not assume a copied web page or third-party mirror has the same rights as the source publication.

Keep original and adapted instances distinguishable.

---

## 3. Freeze prompts before full run

Use a tiny smoke test only to verify parsing/formatting. Do not use the 24 critical items to prompt-search.

Freeze 2 prompt surfaces maximum for robustness, for example:

### Prompt P1 — report accuracy

Give source speech/context and indirect report. Ask whether the report **can accurately convey** what was said in context. Require fixed response format.

### Prompt P2 — temporal consequence

Give the context/report and ask a logically explicit compatibility or entailment question. Require fixed response format.

Avoid explanatory wording that teaches SOT in the main task.

Balance YES/NO and option order where applicable.

---

## 4. Task A — published report-accuracy replication

Use the English 24 lexicalizations and source four-condition structure.

Primary condition:

- source context forces/intends simultaneity via present direct speech;
- indirect report uses embedded past.

Measure whether the model accepts the report as a possible faithful report.

Also retain the source experiment's matched conditions so the target is not an isolated one-sided classification task.

If desired, retain selected published fillers as obvious good/bad report controls.

Do not reinterpret the source paper's ordinal human rating as a categorical semantic theorem; use it as empirical evidence that the simultaneous past report is licensed/acceptable for English speakers.

---

## 5. Task B — consequence-sensitive inference

This is the key step beyond merely reproducing a human judgment paradigm.

For the same lexical families, derive minimal questions whose gold follows from **licensing/non-entailment**, not from choosing one reading of an ambiguous sentence.

Required quantities:

### B1. Simultaneous compatibility

Test whether an embedded-past report is compatible with the state holding at the matrix attitude/speech time.

Gold for English SOT critical items: **compatible / possible**.

### B2. False anteriority

Test whether embedded simple past **requires / entails** that the state is earlier than the matrix attitude/speech time.

Gold: **NO**.

Use wording like `Does this report require ...?`, not `When did ... happen?`.

For a controlled subset, explicitly describe a simultaneous world and ask whether the past-under-past report is compatible with it. Keep the semantic manipulation minimal and auditable.

---

## 6. Controls

### C1. Explicit anteriority

Create matched examples where anteriority really is encoded, e.g. with past perfect or an overt earlier-time modifier.

The model should infer BEFORE here.

### C2. Explicit simultaneity / ordinary temporal relation

Use transparent temporal descriptions to verify that the model can reason about SAME-TIME vs BEFORE independent of SOT.

### C3. Faithful/unfaithful reporting

Use obvious report-preservation controls, preferably from the source paper's fillers when suitable.

### C4. Surface/polarity balance

Prevent global answer frequency, label token and position from identifying the target.

A model family that fails basic controls cannot support the L39 claim.

---

## 7. Task D — metalinguistic knowledge control

After the main tasks are frozen, separately ask a small set of direct questions such as whether English simple past embedded under a past attitude verb can describe a state simultaneous with the matrix attitude time.

This task measures **declarative knowledge**, not performance on the mother phenomenon.

Keep its results separate from Task A/B.

The scientifically strongest pattern would be:

- high explicit SOT knowledge;
- high ordinary temporal controls;
- low simultaneous licensing / high false-anteriority errors in contextual inference.

---

## 8. Model selection

Use 2–3 strong current model families already available to the local environment/API.

Do not model-shop after results.

Record:

- exact model ID / checkpoint;
- access date;
- system prompt if any;
- decoding temperature/top-p;
- max tokens;
- reasoning mode / thinking setting if externally configurable;
- API or serving stack version where relevant.

Main classification run should be deterministic or low-temperature.

---

## 9. Analysis

Produce item-level outputs and aggregate tables.

At minimum report:

- Task A condition-wise acceptance/accuracy;
- Task B simultaneous-compatibility rate;
- Task B false-anteriority rate;
- C1 explicit-anteriority accuracy;
- C2 ordinary temporal accuracy;
- C3 report-control accuracy;
- D metalinguistic SOT knowledge;
- paired differences and bootstrap confidence intervals over items where meaningful.

The best analysis is paired: same lexical content and ideally same indirect report, with the context/reference relation changed.

Do not hide model-family heterogeneity behind a single pooled average.

---

## 10. Decision

### `KILL`

Recommend closing L39 if:

- strong models handle simultaneous licensing/non-entailment well;
- failure is weak/model-specific;
- failure collapses under an innocuous prompt rewording;
- generic temporal/report controls also fail;
- apparent effect depends on author-created ambiguous gold;
- direct owner collision is found.

No salvage.

### `PROMOTE TO RE-SELECTION`

Recommend returning L39 to selection only if at least two strong model families show a robust, item-level SOT-specific failure while controls are strong.

### `STRONG PROMOTE TO RE-SELECTION`

Same as above, plus a clear knowledge–deployment dissociation: models can state the SOT rule but fail to apply it in contextual inference.

Do not automatically run E02/E03 after a pass.

---

## 11. Deliverables

Before finishing E01, leave the repository with:

- provenance-preserving data manifest;
- extraction/adaptation script or notes;
- frozen prompt templates;
- model-run script/config;
- raw model outputs;
- item-level scored results;
- summary table(s);
- `E01_REPORT.md` containing:
  - exact setup;
  - controls;
  - main results;
  - confidence intervals;
  - representative failure analysis;
  - `KILL` or `RETURN TO SELECTION` recommendation;
  - any novelty collision discovered.

Do not write a paper narrative before the mother phenomenon is established.
