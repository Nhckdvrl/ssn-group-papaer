# L02 — Semantic Role Completion ≠ Referential Commitment

**Status:** PILOT-AUTHORIZED  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Date promoted:** 2026-09-06

> **Plain-language thesis:** Understanding that an event has a missing role does not necessarily license inventing a specific missing entity.

---

# 1. One-sentence RQ

> When language leaves an argument unstated, can modern generative models distinguish **semantic role completion** from **referential commitment**—recovering a concrete entity only when a specific discourse referent actually exists?

---

# 2. Why ACL / NLP should care

Modern semantic-role and event-argument extraction increasingly use document-level inference and free-form generation.

Classical implicit-argument work explicitly separated:
1. detecting a missing role;
2. deciding whether it has a definite/recoverable referent;
3. resolving the filler only when such a referent exists.

Free-form generation may make that separation obsolete—or may collapse it and encourage plausible but unsupported specificity.

This is directly relevant to semantic parsing, information extraction, document understanding, grounding, and hallucination.

---

# 3. Real object

The object predates LLMs:

> **Some linguistically omitted roles refer to a particular discourse entity; others are semantically understood without denoting any particular missing entity.**

FrameNet calls the first class DNI and the second INI, but the paper should not lead with those acronyms.

Everyday explanation:

- a missing participant can be **elsewhere in the discourse and recoverable**;
- or the event merely implies a role/type and **there is no particular entity to recover**.

---

# 4. Competing accounts

## Account A — End-to-end generative completion

A strong generative model can jointly infer referential status and filler identity.

Prediction:
- it emits specific entities on recoverable omissions;
- it abstains / stays non-specific on non-referential omissions;
- explicit factorization into “is there a referent?” then “which referent?” adds little.

## Account B — Referential overcommitment

Generation makes semantic plausibility leak into entity commitment.

Prediction:
- once a role is expected, the model generates a plausible concrete filler even on non-referential omissions;
- role/type understanding can remain high while referential correctness fails;
- explicit referential-status modeling materially reduces errors.

These accounts imply different conclusions about whether classical task factorization remains necessary in the LLM era.

---

# 5. Exact data + independent gold

## SemEval-2010 Task 10 — primary decisive substrate

Running-text fiction data with gold semantic argument structure and null-instantiation links.

Published corpus statistics:
- **Train:** 438 sentences; 303 DNI; 277 INI; 245 resolved DNI.
- **Test:** 525 sentences; 349 DNI; 361 INI; 259 resolved DNI.

The classic task explicitly separates:
1. null-instantiation detection;
2. definite-vs-indefinite decision;
3. filler resolution only for definite cases.

This gives independent pre-LLM gold for both the referential-status decision and many concrete DNI fillers.

## FrameNet — scale/replication substrate

FrameNet contains approximately **55,700 null-instantiation labels**, including lexically licensed definite/indefinite omissions.

Use FrameNet for scale/coverage only after verifying the exact extractable release fields and contextual availability.

---

# 6. Closest parents

## Classical parent

- Ruppenhofer et al. (2010), *SemEval-2010 Task 10: Linking Events and Their Participants in Discourse.*
- Earlier/later null-instantiation resolution work already knows DNI ≠ INI.

This means **“can LLMs distinguish DNI and INI?” is NOT novel.**

## Modern generative neighbors

- Roit et al. (ACL 2024), *Explicating the Implicit: Argument Detection Beyond Sentence Boundaries.*
- Sharif et al. (EMNLP 2024), *Explicit, Implicit, and Scattered: Revisiting Event Extraction to Capture Complex Arguments.*
- Sharif et al. (Findings of EMNLP 2025), *REGen: A Reliable Evaluation Framework for Generative Event Argument Extraction.*

These modernize cross-sentence / implicit argument extraction and generative evaluation. Their “implicit” target is generally **unstated but inferable**.

The searched gap is:

> **generative argument extraction evaluated around referential status itself: role understood vs concrete entity licensed.**

No direct 2024–2026 collision owning this exact modern evaluation/modeling question was found in the terminal audit.

---

# 7. Reviewer compression

## Attack

> “This is just the old FrameNet DNI/INI distinction tested on LLMs.”

## Required rebuttal

The semantic distinction is intentionally old.

The contribution is the **changed modeling assumption**:

> classical systems separated referential-status classification from resolution; modern free-form generation can attempt both in one output.

The paper asks whether this architectural/task-definition change is scientifically valid.

This is an Old Problem / New Method revisit, not a claim to invent DNI/INI.

If the empirical paper cannot demonstrate consequences of the changed generative formulation, KILL after pilot.

---

# 8. Outcome map

## Outcome A — generation respects the boundary

Modern LLMs correctly stay non-specific on INI and recover DNI referents.

Scientific consequence:

> the classical detect-definiteness-then-resolve factorization is no longer necessary for strong generative models, at least under identified conditions.

## Outcome B — generation overcommits

Models often generate plausible entities for INI despite knowing the role/type.

Scientific consequence:

> generative argument extraction needs explicit referential-status modeling / abstention; role completion is not evidence of grounded entity recovery.

## Outcome C — principled heterogeneity

Performance depends on predicate/frame, discourse distance, conventionality, or availability of salient candidate entities.

Scientific consequence:

> identify the boundary conditions under which generative end-to-end completion is safe.

All three outcomes are interpretable; the project should not depend on one quirky failure.

---

# 9. Proposed C1 / C2 / C3

## C1 — Core finding

Measure whether current generative models preserve the boundary between semantic role completion and referential commitment.

## C2 — Why / boundary

Disentangle:
- role/type knowledge;
- referential-status judgment;
- filler selection.

Test whether explicit typed factorization changes error rates and where.

## C3 — Consequence

Evaluate a typed output/evaluation unit distinguishing:
1. explicit argument;
2. recoverable omitted referent;
3. non-specific omitted role.

The strongest consequence is a changed conclusion about how generative implicit-argument extraction should be modeled/evaluated—not a new benchmark score.

---

# 10. Minimum decisive pilot

**Do not start with FrameNet-wide engineering.**

Use the SemEval-2010 Task 10 test/train material first.

For a small stratified sample of DNI and INI cases:

1. Ask several current open/closed LLMs for the omitted role.
2. Require a structured output that can express:
   - `SPECIFIC_REFERENT + filler`;
   - `NON_SPECIFIC`.
3. Independently ask for role/type information without entity commitment.
4. Compare:
   - referential-status accuracy;
   - DNI filler accuracy;
   - INI overcommitment rate;
   - role/type accuracy conditional on referential error.
5. Compare one-shot free generation with explicit two-stage factorization:
   - “Does a specific referent exist?”
   - if yes, “Which one?”

### Pilot kill condition

KILL if:
- modern generative systems already trivially preserve the boundary with near-ceiling performance **and** factorization changes nothing;
- the old data prove too small/noisy/domain-specific to support stable estimates and FrameNet cannot cleanly replicate;
- direct literature collision appears during implementation;
- the only interesting result is one model hallucinating badly.

### Pilot continuation condition

Continue only if:
- there is a stable, interpretable difference between role understanding and referential commitment; **or**
- strong end-to-end generation robustly eliminates the classical need for factorization.

---

# 11. Five hard gates

| Gate | Verdict | Reason |
|---|---|---|
| REAL OBJECT | **YES** | Natural omitted-argument/reference problem predates LLMs. |
| NEW AXIS | **YES** | Old DNI/INI distinction becomes a test of whether generative end-to-end completion can collapse a formerly explicit modeling step. |
| GOOD DATA | **YES** | SemEval-2010 provides running text + gold status + DNI links; FrameNet provides scale. |
| NEW PARENT | **YES, survived current direct audit** | Classical distinction is old, but searched modern generative literature does not own the exact “role completion ≠ referential commitment / is factorization still necessary?” question. |
| DECISIVE PAPER | **YES** | Both success and failure of end-to-end generation yield different modeling conclusions; heterogeneous boundaries are also informative. |

# Final status

# **PILOT-AUTHORIZED**

Not paper-mainline-approved.

The topic is automatically demoted if the pilot cannot support a consequence about the generative task definition/modeling assumption.
