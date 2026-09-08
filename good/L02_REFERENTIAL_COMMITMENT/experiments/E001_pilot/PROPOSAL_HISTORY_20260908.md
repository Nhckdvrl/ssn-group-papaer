# L02 — Semantic Role Completion ≠ Referential Commitment

> **Current status, 2026-09-08: ACTIVE; E000 executed; original model estimand requires revision.**
> Recovered 438 training sentences, 303 DNI and 277 INI. **11 INIs have source filler links**;
> INI is not an automatic gold label for unsupported generation. Read
> [E000 results](experiments/E000_data_audit/RESULTS.md), [claim ledger](CLAIMS.md),
> [current literature alignment](literature/ALIGNMENT_20260908.md), and
> [revised pilot draft](experiments/E001_pilot/PROTOCOL_DRAFT.md).
> The proposal and five-gate verdict below are historical, superseded where they conflict
> with E000. Research continues; no language-model finding has been established.

**Status:** PILOT-AUTHORIZED
**Paper mainline:** NOT APPROVED
**Target:** NAACL Main
**Canonical research package:** this directory
**Last audited:** 2026-09-07

> **Plain-language thesis:** Understanding that an event has a missing role does not necessarily justify inventing a particular missing entity.

---

## 1. One-sentence research question

> When language leaves an argument unstated, can modern generative systems safely collapse **role completion**, **referential-status judgment**, and **filler recovery** into one end-to-end generation step, or does correct interpretation still require deciding whether a specific discourse referent exists before generating an entity?

This is an **Old Problem / New Method** paper candidate. The old linguistic distinction is not the contribution. The paper-level question is whether the classical distinction remains **load-bearing** in modern generative information extraction.

## 2. Natural object

The object exists independently of LLMs:

- some omitted semantic roles correspond to a particular entity recoverable from discourse;
- other omitted roles are semantically licensed without committing to any particular entity.

FrameNet terminology includes **DNI** and **INI**, but the paper should explain the object in ordinary language first.

## 3. Why ACL / NLP cares

Modern event extraction, semantic role labeling, document understanding, and generative IE increasingly allow systems to emit free-form arguments. That changes an old modeling assumption: classical implicit-argument pipelines explicitly separated *whether a specific referent exists* from *which referent it is*. A generative system may make this separation obsolete—or may create unsupported specificity.

The scientific target is therefore not “does an LLM know DNI versus INI?” It is:

> **Is referential-status factorization still necessary for grounded generative argument extraction?**

## 4. Competing accounts

### Account A — End-to-end generation is sufficient

A strong generative model can internally infer whether a specific referent exists and only produce a filler when licensed.

If this account wins:
- explicit referential-status classification is historical scaffolding under the tested regime;
- direct generation can preserve the relevant semantic boundary;
- old pipeline factorization can be simplified without losing grounding.

### Account B — Generation induces referential overcommitment

Once a role is semantically expected, free-form generation tends to emit a plausible entity even when no particular discourse referent is licensed.

If this account wins:
- role/type understanding and referential commitment are empirically separable;
- generative IE requires an explicit abstention/status layer or equivalent constraint;
- current argument-extraction evaluation can over-credit plausible but unsupported fillers.

### Principled heterogeneity

If direct generation is safe only under certain frames, discourse distances, predicate classes, or evidence regimes, the paper becomes a **boundary paper** describing when factorization is and is not necessary.

## 5. Outcome robustness

**If the expected “overcommitment” phenomenon does not occur, what is the paper?**

A positive preservation result is still scientifically meaningful:

> strong generative systems can safely eliminate a classical explicit referential-status step under identified conditions.

That is not a failed negative result. It is a pre-specified preservation / necessity result.

The topic should be killed only if the data have no leverage, the distinction is trivial at ceiling, no modeling/evaluation consequence follows, or a direct modern paper already owns the full story.

## 6. Paper identity

**Primary identity:** scientific measurement + task-definition / modeling-assumption test.

**Not the identity:**
- a DNI/INI benchmark;
- a generic hallucination paper;
- a “LLMs fail at implicit arguments” paper;
- a new semantic distinction.

## 7. Planned C1 → C2 → C3

### C1 — Core scientific answer
Determine whether role understanding can be separated from referential commitment in modern generative systems, and whether direct generation preserves the boundary.

### C2 — Explanation / boundary
Decompose:
1. role/type recognition;
2. referential-status judgment;
3. filler selection.

Test discourse distance, frame/predicate class, salience, and direct versus factorized generation.

### C3 — Consequence
Determine whether generative implicit-argument extraction should:
- retain explicit referential-status structure;
- use a typed abstention output;
- or safely collapse the pipeline under stated conditions.

## 8. Five hard gates

| Gate | Verdict | Why |
|---|---|---|
| REAL OBJECT | **YES** | Natural omitted-role/reference distinction predates LLMs. |
| SCIENTIFIC TENSION | **YES** | End-to-end sufficiency and load-bearing factorization are both plausible. |
| GOOD DATA | **YES** | SemEval-2010 Task 10 provides independent status and many filler links; FrameNet is a scale/replication resource. |
| PAPER-LEVEL NOVELTY | **YES, current audit** | Classical distinction is old; searched 2024–2026 generative IE work does not currently own the same necessity/measurement story. |
| OUTCOME-ROBUST DECISIVENESS | **YES** | Success, failure, and boundaries each imply a different modeling conclusion. |

## 9. Main danger

Reviewer compression:

> **“This is just the old FrameNet DNI/INI distinction tested on LLMs.”**

That compression wins if the paper only reports classification accuracy.

It is false only if the paper decisively answers the modern load-bearing question:

> **Can generative IE safely collapse referential-status inference into filler generation, and what changes in modeling/evaluation if it cannot?**

## 10. Directory map

- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) — literature ownership map, collision boundary, allowed/forbidden claims.
- [DATA_AND_GOLD.md](DATA_AND_GOLD.md) — exact substrate, gold semantics, extraction and validation requirements.
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md) — experiments, pilots, C1→C2→C3, kill/promote rules, development roadmap.

This candidate remains **pilot-authorized only** until the minimum decisive pilot and a second novelty audit are complete.
