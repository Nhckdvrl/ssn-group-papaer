# L04 — Morphological Inflection Is Not a Total Single-Valued Function

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Date promoted:** 2026-09-07

> **Plain-language thesis:** Given a lemma and grammatical features, the correct output is not always exactly one word form: some paradigm cells have no accepted form, while others legitimately have more than one.

---

# 1. One-sentence RQ

> Does modern free-form morphological generation preserve the fact that inflection is a **partial, sometimes set-valued mapping**—returning no form for genuinely defective cells and all licensed alternatives for overabundant cells—or does it force every feature bundle into one plausible-looking canonical form?

---

# 2. Why ACL / NLP should care

Morphological reinflection and paradigm completion are classic NLP tasks and remain central for morphologically rich and low-resource languages. Their standard input-output abstraction strongly encourages `lemma + features → one form`, even though real paradigms contain both gaps and alternative realizations.

Generative LMs make arbitrary feature-conditioned querying and open output natural, allowing the task ontology itself—not merely accuracy on known cells—to be tested.

---

# 3. REAL OBJECT

Two established linguistic objects predate LLMs:

## Defectivity

A lexeme lacks an inflected form expected from the paradigm's feature space.

## Overabundance

Two or more forms legitimately realize the same paradigm cell.

Everyday intuition:

> A conjugation table is not necessarily a spreadsheet where every grammatical cell contains exactly one canonical string.

**Gate: YES.**

---

# 4. What LLMs newly enable

Classic reinflection benchmarks overwhelmingly condition evaluation on licensed/observed target cells. Systems are therefore asked **which form**, not whether a legitimate form exists or how many valid realizations there are.

Modern instruction-following generators can instead be queried over arbitrary `lemma + feature bundle` combinations and can naturally emit:

- `NO_FORM`;
- one form;
- a set of valid alternative forms.

The scientific question is whether the old single-output abstraction remains valid when generation is no longer restricted to an attested target inventory.

This is not simply “can an LLM conjugate verbs?”

---

# 5. Competing accounts

## Account A — Generative models internalize paradigm availability

Strong LMs infer lexical restrictions and variation from usage.

Prediction:
- they abstain on genuine defective cells;
- preserve multiple licensed forms where appropriate;
- explicit partial/set-valued modeling adds little.

Scientific conclusion:
> modern generation can remove a classical closed-target assumption.

## Account B — Productive overgeneration / canonicalization

Generative models learn productive inflectional rules that encourage a form for every bundle and a single high-probability realization.

Prediction:
- plausible but unattested/unlicensed forms are hallucinated for defective cells;
- overabundant cells collapse to one canonical form;
- ordinary reinflection accuracy can remain high while paradigm-availability semantics fail.

Scientific conclusion:
> current reinflection evaluation hides a structural error; generation requires explicit existence/set-valued targets.

Both accounts are plausible before results.

---

# 6. GOOD DATA + independent gold

## Defectivity

- **Surrey Defectiveness Database**: typological database covering defectivity across languages, accompanied by a broad cross-linguistic survey.
- **Wiktionary defectivity categories**: especially rich for Italian; categories explicitly record missing future, imperative, participle, present-indicative/subjunctive and other paradigm portions.
- Sakunkoo & Sakunkoo (ACL 2025 SRW), *Lost and Found: Computational Quality Assurance of Crowdsourced Knowledge on Morphological Defectivity in Wiktionary*, independently validates defectivity information using corpus evidence and reports especially strong reliability for Italian.

Sources:
- https://www.smg.surrey.ac.uk/defectiveness/
- https://aclanthology.org/2025.acl-srw.73/

## Overabundance

Overabundance is a well-defined classical morphology object: multiple forms realize the same feature cell (e.g. English `dreamed/dreamt`). Published resources and studies document such cells, including extensive Italian and Latin inventories.

Thornton's work provides the formal object and documented cases; Latin lexical resources such as Lemlat can support larger-scale variant inventories after exact release auditing.

Source:
- https://academic.oup.com/edited-volume/61882/chapter/547711117

## Important restriction

The pilot must use only cells whose absence or multiplicity is independently documented. Corpus non-attestation alone is **not** gold for defectivity.

**Gate: YES, conditional on exact extractable resource audit before scaling.**

---

# 7. Classical technical restriction

A particularly important explicit statement appears in *Morphology Without Borders: Clause-Level Morphology* (TACL): for overabundance, the construction retains **one canonical form per cell**, while noting that an empirically broader representation could use **sets of forms in every cell**.

Source:
- https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00528/114370/Morphology-Without-Borders-Clause-Level-Morphology

SIGMORPHON reinflection/paradigm-completion tasks likewise evaluate generation of target inflected forms rather than the general partial/set-valued paradigm-availability problem.

This provides unusually direct evidence that the richer quantity is not invented post hoc.

---

# 8. NEW PARENT — novelty assassination

## Classical parent

Morphological defectivity and overabundance are old. Their age is not the novelty claim.

## Modern neighbors searched

- current LLM/GPT G2P and morphology studies test inflectional generation/consistency;
- ACL 2025 SRW studies **quality assurance of defectivity records**, not whether generative reinflection should be partial/set-valued;
- standard reinflection/paradigm-completion literature evaluates licensed targets;
- existing multi-answer shared-task scoring acknowledges multiple correct strings in some cases, but does not jointly make `NO_FORM | SET(forms)` the scientific output ontology over arbitrary paradigm cells.

Fresh 2024–2026 search did not locate a direct paper asking:

> **Should LLM-era morphological inflection be evaluated as a partial, set-valued relation rather than a total single-valued function?**

### Reviewer compression

> “This is just testing LLMs on defective/overabundant morphology.”

### Why that compression is currently false

The candidate is not a phenomenon-competence paper. Its decisive comparison is between two **task definitions**:

1. conventional target-conditioned single-form reinflection;
2. arbitrary-cell partial/set-valued generation.

The paper only survives if the pilot shows that conclusions under (1) fail to predict behavior under (2), or conversely that modern generation makes the richer explicit representation unnecessary.

**Gate: YES, survived current direct audit.**

---

# 9. DECISIVE PAPER

## C1 — Core structural finding

Measure whether high-performing generative inflectors know **paradigm availability and multiplicity**, not merely form construction conditional on an existing target.

## C2 — Why / boundary

Analyze by:
- defectivity type;
- lexical frequency;
- productivity/regularity;
- paradigm neighborhood support;
- single vs multiple licensed forms;
- language/resource.

Compare direct generation against explicit first-stage `does this cell exist / how many variants?` factorization.

## C3 — Consequence

Re-evaluate morphological generation with a typed target:

```text
NO_FORM
ONE_FORM: x
MULTIPLE_FORMS: {x, y, ...}
```

Ask whether rankings / conclusions from ordinary reinflection accuracy survive the corrected output space.

### Outcome map

| outcome | scientific meaning | informative? |
|---|---|---|
| Account A wins | generative LMs learn paradigm availability well enough to relax classical target restrictions | YES |
| Account B wins | productive generation hallucinates nonexistent cells / canonicalizes real variation | YES |
| heterogeneity | identifies where partial/set-valued modeling is necessary | YES |
| ranking reversal | classic reinflection scores conceal paradigm-ontology failures | YES, strongest |

**Gate: YES.**

---

# 10. Minimum decisive pilot

1. Use one high-confidence language first, likely Italian, where defectivity records have independent validation and overabundance is well documented.
2. Construct a small balanced set of:
   - ordinary one-form cells;
   - independently documented defective cells;
   - independently documented overabundant cells.
3. Test several current LMs under the same natural instruction.
4. Compare:
   - forced single-form generation;
   - open `NO_FORM / one / multiple` generation;
   - explicit existence→generation factorization.
5. Primary estimands:
   - false-form rate on defective cells;
   - variant recall/precision on overabundant cells;
   - ordinary reinflection accuracy;
   - rank/conclusion change under partial/set-valued scoring.

### Pilot kill condition

KILL if:
- independent defectivity/overabundance gold cannot be extracted cleanly enough;
- the only effect is a handful of obscure lexical exceptions;
- current models are uniformly ceiling and the richer task changes no scientific conclusion;
- a direct modernized-parent collision appears.

### Pilot continuation condition

Continue only if ordinary reinflection competence diverges systematically from availability/multiplicity competence, or if strong generative systems robustly eliminate the classical restriction across independently documented cases.

---

# 11. Five hard gates

| Gate | Verdict | Reason |
|---|---|---|
| REAL OBJECT | **YES** | Defectivity and overabundance are real, established morphological properties. |
| NEW AXIS | **YES** | Changes reinflection from a total single-valued mapping to a partial/set-valued relation. |
| GOOD DATA | **YES, pilot-scale** | Independently documented high-confidence defectivity and overabundance cases exist; no corpus non-attestation is treated as gold. |
| NEW PARENT | **YES, survived current direct audit** | Current work studies inflection or defectivity resources, not the LLM-era output-space rewrite over arbitrary cells. |
| DECISIVE PAPER | **YES** | Both robust availability knowledge and productive overgeneration change how morphological generation should be formulated/evaluated. |

# Final status

# **PILOT-AUTHORIZED**

Not paper-mainline-approved.

Because this is linguistically narrower than L02/L03, it must be killed after pilot if the result cannot support a general task-definition / evaluation consequence beyond a list of defective words.
