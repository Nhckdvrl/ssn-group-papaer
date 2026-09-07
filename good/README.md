# Good Candidates

> **good/ means pilot-authorized, not paper-mainline-approved.**

Current state:

| ID | Candidate | Canonical package | Status |
|---|---|---|---|
| **L02** | Semantic Role Completion ≠ Referential Commitment | [good/L02_REFERENTIAL_COMMITMENT/](L02_REFERENTIAL_COMMITMENT/) | **PILOT-AUTHORIZED** |
| **L03** | Table Value ≠ Observation Status | [good/L03_TYPED_OBSERVATION/](L03_TYPED_OBSERVATION/) | **PILOT-AUTHORIZED** |
| **L04** | Morphological Inflection Has Realization Cardinality | [good/L04_REALIZATION_CARDINALITY/](L04_REALIZATION_CARDINALITY/) | **PILOT-AUTHORIZED / NOVELTY-FRAGILE** |

# Current scoreboard: 3 / 5

# Approved paper mainline: NONE

---

## Canonical good-candidate package format

Every promoted candidate now receives its own directory. The directory, not the old single Markdown card, is the authoritative research record.

Each package contains:

1. **README.md**
   - one-sentence RQ;
   - natural object;
   - why ACL/NLP cares;
   - competing accounts;
   - outcome robustness;
   - paper identity;
   - C1→C2→C3;
   - five gates;
   - main reviewer-compression danger.

2. **RELATED_WORK_AND_NOVELTY.md**
   - classical ownership;
   - modern neighboring papers;
   - closest collision pressure;
   - what prior work already owns;
   - what we explicitly cannot claim;
   - what part of the full paper-level story is new;
   - reviewer compression;
   - exact kill-level collision definition.

3. **DATA_AND_GOLD.md**
   - exact natural substrate;
   - exact independent gold;
   - deterministic action mapping;
   - extraction contract;
   - sampling;
   - metrics;
   - data-validity kill conditions;
   - replication status.

4. **RESEARCH_PLAN.md**
   - minimum decisive pilot;
   - Account A / B / boundary promotion routes;
   - preservation/equivalence handling;
   - C1→C2→C3;
   - phases of development;
   - paper skeleton;
   - pre-mainline promotion checklist.

The older top-level candidate files remain for backward compatibility with earlier repository references, but future work should use the package directories as the canonical source.

---

## Hard meaning of promotion

A candidate enters good/ only after passing:

- REAL OBJECT;
- SCIENTIFIC TENSION / NEW CONTRIBUTION AXIS;
- GOOD DATA;
- PAPER-LEVEL NOVELTY;
- OUTCOME-ROBUST DECISIVENESS.

Promotion means only:

# PILOT-AUTHORIZED

It does **not** mean:
- the paper mainline is approved;
- novelty is permanently safe;
- the expected phenomenon must occur;
- the candidate should survive a bad pilot by narrative rescue.

After the minimum decisive pilot, every candidate must be re-audited for:
- data validity;
- outcome interpretation;
- paper scale;
- direct modern collision;
- reviewer compression;
- C1→C2→C3 decisiveness.

---

## Mandatory anti-phenomenon-hunting question

Every good candidate must answer before compute:

> **If the expected “bad / surprising” phenomenon does not occur, what is the paper?**

The answer must be a pre-specified scientific conclusion such as:
- preservation;
- equivalence;
- non-inferiority;
- representation necessity / dispensability;
- a principled boundary.

“Then we have a negative result” is not sufficient.

---

## Mandatory paper-level novelty question

Every good candidate must also answer:

> **What part of the full paper-level story is actually new?**

The answer cannot be:
- a new model;
- a new prompt;
- an exact dataset cell;
- an untouched subcase;
- a renamed classic distinction.

The novelty must live in the load-bearing scientific framing, decisive comparison, measurement/intervention, conclusion, or their coherent combination.

---

## Candidate-specific warnings

### L02

Do not reduce it to:
> “Can an LLM classify DNI vs INI?”

It survives only as a question about whether **referential-status factorization remains load-bearing in generative implicit-argument extraction**.

### L03

Do not reduce it to:
> “Can an LLM understand Census sentinel codes?”

It survives only as a question about **provider-defined typed observation as the semantic output unit**, and whether explicit status modeling remains necessary.

### L04

Do not claim:
- defectivity is new;
- overabundance is new;
- set-valued morphology is new;
- LLMs first enable full paradigm completion.

It survives only as:

> **Does canonical single-target evaluation preserve computational-morphology conclusions when zero/one/many realization cardinality is restored?**

L04 remains the most novelty-fragile current good candidate and should be killed quickly if the pilot reduces to rare Estonian morphology errors.

---

## External quality bar — mandatory

The quality standard for good/ is **not “as strong as the current good candidates.”**

The external standard is:

# ACL / EMNLP / NAACL Main
# with Outstanding / Best / Best Theme Paper as the aspirational bar

Every current and future good candidate must be continuously compared to real high-level conference papers along:
- RQ scale;
- naturalness and importance;
- pre-result scientific tension;
- data/gold quality;
- identification strength;
- full-paper novelty;
- C1→C2→C3 decisiveness;
- consequence for NLP;
- breadth without padding;
- plain-language paper identity.

See [../TOP_CONFERENCE_ALIGNMENT.md](../TOP_CONFERENCE_ALIGNMENT.md).

L02/L03/L04 are **survivors, not exemplars**. They can still be demoted if deeper alignment review shows they are below this external bar.
