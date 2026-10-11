> **2026-09-08 closure:** NO-GO / K180. Retired for Main-level paper-scale and outcome fragility; not because the classical morphology parent is old.

> **Canonical research package moved to [good/L04_REALIZATION_CARDINALITY/](L04_REALIZATION_CARDINALITY/).**  
> This top-level file is retained for backward compatibility with earlier repository references. Future edits should go to the package directory.

---

# L04 — Morphological Inflection Has Realization Cardinality

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Date promoted:** 2026-09-07

> **Plain-language thesis:** For a lemma plus morphosyntactic cell, the linguistically licensed answer is not always exactly one form: there can be no form, one form, or several valid forms.

---

# 1. One-sentence RQ

> Does the standard single-canonical-target formulation of morphological inflection preserve conclusions about morphological generalization once the natural **realization cardinality** of paradigm cells—zero, one, or multiple licensed forms—is restored?

This is deliberately **not** the claim that defectivity or overabundance is newly discovered, and **not** the claim that LLMs are the first systems capable of completing paradigms.

---

# 2. Why ACL / NLP cares

Morphological inflection is a mature structured-generation task used to study low-resource generalization, typological transfer, paradigm completion, and model inductive bias. Standard benchmarks usually operationalize `lemma + features -> one target string`; if real cells are partial or set-valued, that evaluation can condition away exactly the cases that distinguish lexical/paradigmatic knowledge from string transduction.

---

# 3. REAL OBJECT

The object predates modern models:

- **defectivity:** a paradigm cell has no conventionally licensed form;
- **ordinary realization:** a cell has one licensed form;
- **overabundance:** a cell licenses multiple forms with the same morphosyntactic function.

Plain examples:

- a plural-only lexeme can have no legitimate singular form;
- another lexeme can license two alternate forms in the same cell.

The question remains meaningful after deleting LLM/model names: what is the correct output unit of morphological inflection, and does canonicalization change what our evaluations measure?

**Gate: YES.**

---

# 4. Exact old technical restriction

The standard supervised inflection task is normally formulated as:

> `lemma + feature bundle -> one inflected word-form`.

*TACL 2022, Morphology Without Borders: Clause-Level Morphology* explicitly notes that overabundance means several forms can occupy the same cell, but the resource construction still keeps **one canonical form per cell**; it states that a richer extension could accommodate **sets of forms** in a cell.

Therefore the old restriction itself is not novel. The open scientific question is whether that canonicalization is empirically harmless or changes conclusions about system generalization/evaluation once zero/one/many realization cardinality is restored.

---

# 5. What modern generation newly changes

Do **not** claim that LLMs uniquely make full-paradigm generation possible. ACL 2020 *Unsupervised Morphological Paradigm Completion* already takes raw text + lemma lists and generates complete paradigms, including paradigm-size discovery.

The modern opportunity is narrower and cleaner:

> general-purpose autoregressive generators can be evaluated with an open cardinality-typed output—`NO_FORM`, one form, or an arbitrary set of forms—without forcing one canonical string as the answer.

This makes the classical benchmark abstraction directly testable against a relation-aware output/evaluation unit. The contribution is primarily a **task-definition / measurement rewrite**, not an LLM capability claim.

---

# 6. Competing accounts

## Account A — Canonicalization is a harmless measurement simplification

One canonical target is sufficient for the scientific conclusions normally drawn from inflection benchmarks.

Predictions:
- systems that generalize well on canonical cells also handle realization existence/cardinality;
- adding `NO_FORM` and multi-form sets changes little about model ranking or error interpretation;
- explicit cardinality→form factorization adds little.

## Account B — Canonicalization hides a distinct generalization problem

Existence/cardinality and form realization are separate quantities.

Predictions:
- models can generate plausible strings while hallucinating into defective cells;
- they can learn one dominant form while systematically collapsing legitimate overabundance;
- canonical accuracy can overstate paradigm knowledge and can change rankings/conclusions relative to relation-aware evaluation;
- explicit cardinality→form factorization can materially change errors.

Both accounts are plausible before seeing target-model results.

**Gate: YES.**

---

# 7. GOOD DATA + independently extractable gold

## Primary decisive substrate — Eesthetic / Paralex Estonian paradigms

Beniamine et al. (LREC-COLING 2024), *Eesthetic: A Paralex Lexicon of Estonian Paradigms*, releases a machine-readable paradigm lexicon derived from Ekilex.

Paper/project:
- https://aclanthology.org/2024.lrec-main.491/
- https://sbeniamine.gitlab.io/eesthetic/
- dataset archive: https://doi.org/10.5281/zenodo.14069724

### Exact extractable unit

The `forms` table includes, among other fields:

- `lexeme`;
- `cell`;
- orthographic/phonological form fields;
- `overabundance_tag`;
- `defectiveness_tag`.

The Paralex standard explicitly requires defective forms to have their own rows and identifies them with `defectiveness_tag`; the normal form fields use the code `#DEF#` for a defective realization, distinct from `#MISSING#` for unavailable source/transcription information.

Eesthetic's description further states that one lexeme × cell may have **multiple alternate-form rows** for overabundance.

Therefore the experimental gold is directly recoverable without author semantic labeling:

- `NO_FORM`: lexeme×cell represented as defective / `#DEF#`;
- `ONE_FORM`: one non-defective licensed realization;
- `MULTIPLE_FORMS`: multiple licensed alternate form rows for the same lexeme×cell, with their form set.

This is the load-bearing improvement over the previously demoted L04: both zero-cardinality and multi-cardinality cases are now verified in the same public representation.

## Scale

The published Eesthetic resource contains thousands of noun and verb lexemes and hundreds of thousands of inflected-form rows, with explicit defectivity/overabundance metadata.

## Why gold identifies the claimed quantity

The labels come from the released lexical resource and its source lexicographic/paradigm annotations, not from evaluated LLMs or author-created test labels. Crucially, `#DEF#` is semantically distinguished by the standard from `#MISSING#`, preventing ordinary resource missingness from being silently reinterpreted as linguistic defectivity.

**Gate: YES.**

---

# 8. Action mapping

For each `(lexeme, cell)` target, define the externally determined output as:

```text
{
  realization_cardinality: NO_FORM | ONE_FORM | MULTIPLE_FORMS,
  forms: [] | [form] | [form_1, form_2, ...]
}
```

Scoring is decomposed into:

1. realization-status/cardinality accuracy;
2. invalid-form generation rate on `NO_FORM`;
3. form exactness on `ONE_FORM`;
4. set precision / recall / exact-set recovery on `MULTIPLE_FORMS`;
5. conventional canonical-form score on the subset/formulation that forces one reference.

No author-created ontology is needed beyond the deterministic 0/1/>1 cardinality mapping induced by the resource.

---

# 9. NEW PARENT — novelty assassination

## Classical / bridge literature that does NOT count as novelty

- defectivity and overabundance are established morphology objects;
- ACL 2020 *Unsupervised Morphological Paradigm Completion* already owns full-paradigm generation / paradigm-size discovery;
- TACL 2022 *Morphology Without Borders* explicitly acknowledges overabundance and says its own construction selects one canonical form while a set-valued extension would be empirically richer;
- Eesthetic itself is designed to represent defectivity and overabundance.

Thus none of the following claims are available:

> “Inflection is sometimes non-single-valued.”

> “We are the first to suggest storing sets of forms.”

> “LLMs are the first way to discover whether paradigm cells exist.”

## Fresh modern search

Fresh 2024–2026 searches covered LLM/morphological inflection, full paradigm completion, defectivity, overabundance, pronunciation/variant-style multi-reference generation, and contemporary SIGMORPHON-style inflection work.

The closest 2026 theoretical neighbor is Bouton & Bonami, *The implicative structure of overabundant paradigms* (Journal of Language Modelling, 2026), which shows that standard paradigm-cell-filling predictability does not naturally accommodate overabundance and develops measures for overabundant paradigms. This makes the measurement issue more important, but it does not evaluate modern morphological generators under a unified zero/one/many output ontology or test whether canonical benchmark conclusions are preserved.

No direct 2024–2026 paper was found whose parent question is:

> **Does canonical single-target morphological-inflection evaluation preserve model/generalization conclusions when independently annotated zero/one/many realization cardinality is restored?**

### Reviewer compression

> “This is just TACL's suggested set-of-forms extension implemented on Eesthetic, plus defectivity.”

### Why that compression is not yet decisive

The candidate does not claim the representation itself as the contribution. The decisive estimand is a **measurement-validity question**: whether a canonical single-target benchmark yields the same scientific conclusions as relation-aware evaluation after both zero- and multi-realization cells are restored.

TACL establishes the restriction; Eesthetic supplies exact gold; the proposed paper tests whether the restriction is scientifically consequential.

If the pilot cannot show a consequence beyond “these known phenomena exist and models sometimes miss them,” this compression wins and the candidate must be killed.

**Gate: YES, but this is the most fragile gate and must be re-audited after the pilot.**

---

# 10. DECISIVE PAPER

## C1 — Core structural / measurement finding

Quantify whether canonical single-form inflection performance agrees with realization-aware performance over `NO_FORM / ONE_FORM / MULTIPLE_FORMS`.

## C2 — Why / boundary

Factorize errors into:

- realization existence/cardinality;
- actual form generation conditional on cardinality;
- lexeme/paradigm class;
- frequency/attestation where available;
- direct generation versus explicit cardinality→forms generation.

The key question is whether failures arise because the model lacks morphology, or because the task asks it to emit a string before establishing that one string is the correct output type.

## C3 — Consequence

Test whether the standard canonical formulation changes:

- model ranking;
- conclusions about generalization to unseen lexemes/cells;
- apparent error rates by paradigm class;
- the usefulness of explicit structured factorization.

A ranking or conclusion reversal is the strongest Main-level outcome. A robust non-reversal is also meaningful: it would validate canonicalization as an empirically safe simplification under identified conditions.

### Outcome map

| outcome | scientific meaning | informative? |
|---|---|---|
| canonical and relation-aware conclusions agree | the one-target abstraction is empirically safe under tested conditions | YES |
| relation-aware evaluation changes conclusions | canonical benchmarks hide a distinct realization-cardinality problem | YES |
| explicit factorization helps only 0/many cells | cardinality is a load-bearing intermediate state only outside ordinary cells | YES |
| effects are narrow/noisy and change no conclusion | topic is too small for Main | KILL |

**Gate: YES.**

---

# 11. Minimum decisive pilot

Use Eesthetic only; do not begin with multilingual resource engineering.

1. Build exact lexeme×cell groups directly from the released forms table.
2. Stratify a modest sample of `NO_FORM`, `ONE_FORM`, and `MULTIPLE_FORMS` cells.
3. Verify counts and tag semantics automatically; exclude `#MISSING#` from defectivity.
4. Evaluate a small set of strong current generators plus one conventional inflection baseline where practical.
5. Compare:
   - conventional single-target scoring;
   - cardinality-aware direct generation;
   - explicit `cardinality -> form(s)` factorization.
6. Primary estimands:
   - realization-cardinality accuracy;
   - invalid-form rate on defective cells;
   - multi-form set recall/precision;
   - ranking/conclusion agreement versus canonical evaluation.

### Pilot kill conditions

KILL if any of these occurs:

- exact Eesthetic counts reveal too few reliable zero/many cases for stable analysis;
- defectivity/overabundance tags turn out to mix incompatible phenomena such that the deterministic action mapping is not valid;
- modern systems are near ceiling and relation-aware evaluation changes no scientific conclusion;
- the only contribution becomes “LLMs make mistakes on rare morphology”;
- a direct modern-parent collision is found;
- cross-resource/language replication required for Main cannot be secured without reconstructing gold.

### Pilot continuation conditions

Continue if either:

- canonical evaluation and realization-aware evaluation yield robustly different conclusions/model rankings/error interpretation; or
- strong modern generation robustly makes the canonical simplification scientifically safe, with enough noncanonical cells and replication to support that conclusion.

---

# 12. Five hard gates

| Gate | Verdict | Reason |
|---|---|---|
| REAL OBJECT | **YES** | Defectivity and overabundance are natural, established paradigm properties. |
| NEW AXIS | **YES** | The tested quantity is realization cardinality and the validity of canonical single-target measurement, not another morphology competence probe. |
| GOOD DATA | **YES** | Eesthetic/Paralex exposes lexeme×cell rows with explicit defectiveness and overabundance tags; `#DEF#` is distinct from ordinary missing data. |
| NEW PARENT | **YES, survived current audit / fragile** | Prior work knows the phenomena and even proposes sets, but fresh search did not find the decisive canonical-vs-0/1/many measurement-validity test on modern generators. |
| DECISIVE PAPER | **YES** | Preservation versus reversal of canonical conclusions are both scientifically interpretable; a no-consequence narrow result kills the topic. |

# Final status

# **PILOT-AUTHORIZED**

# **NOT MAINLINE APPROVED**

This promotion supersedes the earlier demotion because the previously missing load-bearing data condition has now been concretely satisfied by Eesthetic/Paralex. The topic remains more novelty-fragile than L02/L03 and should be killed quickly if the pilot cannot demonstrate a task-definition/evaluation consequence.