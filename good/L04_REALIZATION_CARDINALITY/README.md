# L04 — Morphological Inflection Has Realization Cardinality

**Status:** NO-GO / K180 — NOT ACTIVE  
**Paper mainline:** RETIRED  
**Target:** NAACL Main  
**Canonical research package:** this directory  
**Last audited:** 2026-09-07  
**Novelty risk:** HIGHER than L02/L03

> **Closure — K180:** Retired after Main-level re-audit for paper-scale/outcome fragility, not because the classical parent is old. The exact modern question was not found fully occupied, but the surviving story depended too heavily on a consequential ranking/generalization change and lacked strong cross-resource replication.
>
> **Plain-language thesis:** For a lemma and a morphosyntactic cell, the linguistically licensed answer is not always exactly one form. There may be no form, one form, or several valid forms.

---

## 1. One-sentence research question

> Does standard single-canonical-target morphological inflection preserve scientific conclusions about generalization once the natural **realization cardinality** of paradigm cells—zero, one, or multiple licensed forms—is restored?

This is not a discovery paper about defectivity or overabundance. It is a **measurement-validity / task-definition** paper candidate.

## 2. Natural object

The object predates modern models:

- **defectivity:** some paradigm cells have no conventionally licensed realization;
- **ordinary realization:** some cells have one licensed form;
- **overabundance:** some cells license more than one form.

The question remains natural without LLMs:

> Is forcing every inflection target into one canonical string an empirically harmless simplification, or does it change what we conclude about morphological knowledge/generalization?

## 3. Why ACL / NLP cares

Morphological inflection is a mature NLP task used to study:
- low-resource generalization;
- typological transfer;
- paradigm completion;
- inductive bias;
- model comparison.

If benchmark construction silently canonicalizes away zero/many realizations, evaluation may measure string transduction rather than the fuller paradigm relation.

## 4. Competing accounts

### Account A — Canonicalization is empirically safe

One canonical target preserves the scientific conclusions usually drawn from inflection benchmarks.

If this wins:
- model rankings and generalization conclusions remain stable;
- zero/many cases do not materially alter interpretation;
- the conventional task is validated as a practical simplification.

### Account B — Canonicalization hides a distinct generalization problem

Existence/cardinality and form realization are separate quantities.

If this wins:
- models can hallucinate forms into defective cells;
- they can collapse legitimate overabundance;
- canonical scoring can overstate or mischaracterize paradigm knowledge;
- explicit cardinality→form factorization can change conclusions.

### Principled heterogeneity

If canonicalization is safe for ordinary cells but unsafe for certain paradigm classes or frequency regimes, the paper becomes a boundary result.

## 5. Outcome robustness

**If ranking reversal or dramatic model failure does not occur, what is the paper?**

A robust preservation result can still validate a decades-old evaluation simplification:

> canonical one-target inflection is empirically non-inferior to relation-aware evaluation under specified conditions, despite known zero/many morphology.

That result requires real leverage:
- enough independently labeled noncanonical cells;
- uncertainty-aware preservation testing;
- replication or a strong generality argument.

A vague “we saw little difference” is not enough.

## 6. Paper identity

**Primary identity:** measurement validity of canonical morphological inflection.

**Not the identity:**
- discovery of defectivity;
- discovery of overabundance;
- first set-valued inflection representation;
- first full-paradigm generation;
- “LLMs make mistakes on rare Estonian morphology.”

## 7. Planned C1 → C2 → C3

### C1 — Core scientific answer
Measure agreement between canonical single-target evaluation and zero/one/many realization-aware evaluation.

### C2 — Explanation / boundary
Separate:
- realization existence/cardinality;
- form generation conditional on cardinality;
- paradigm/lexeme class;
- frequency/attestation;
- direct generation vs explicit cardinality→forms generation.

### C3 — Consequence
Determine whether standard inflection evaluation:
- remains scientifically valid;
- requires a relation-aware output/evaluation unit;
- or is valid only in identified regimes.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Defectivity and overabundance are established paradigm properties. |
| SCIENTIFIC TENSION | **YES** | Canonicalization may be harmless or may hide a separate generalization quantity. |
| GOOD DATA | **YES** | Eesthetic/Paralex explicitly encodes defectiveness, overabundance, and distinguishes DEF from missing source data. |
| PAPER-LEVEL NOVELTY | **YES, fragile current audit** | Prior work owns the phenomena and even proposes richer form sets; current candidate survives only as a model/evaluation-conclusion test. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Preservation, failure, or clear boundaries each answer the measurement question. |

## 9. Main danger

Reviewer compression:

> **“This is TACL 2022’s suggested set-of-forms extension implemented on Eesthetic, plus defectivity.”**

This is the strongest attack of the three current good candidates.

The compression is false only if the paper demonstrates a new scientific consequence:

> **Does canonicalization preserve or alter the conclusions we draw about modern morphological generalization?**

If the result is merely “some forms have variants and models miss them,” KILL.

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) — classical ownership, TACL/ACL neighbors, 2026 collision pressure, claim boundaries.
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md) — Eesthetic/Paralex extraction contract and validity checks.
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md) — pilot, measurement design, C1→C2→C3, kill/promote path.

L04 remains **pilot-authorized but novelty-fragile**.
