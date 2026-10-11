# L34 — Does Future Access Shape What Gets Learned?

**Initial selection:** 2026-09-13  
**Final decision:** 2026-09-14  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **KILL — CURRENT SCIENTIFIC IDENTIFICATION FAILED; NO E02 AUTHORIZED**

## Final verdict

> **Kill L34 as a candidate. Do not repair E01 by merely adding a grounded curriculum and an order-control arm.**

E01 did not provide evidence against prospective encoding: its manipulation failed before the scientific question was tested. However, the post-E01 audit exposed deeper Selection problems. The original operationalization and decisive estimand do not uniquely identify the headline claim, so repairing implementation defects would not restore the paper identity.

The broader PIT pressure remains legitimate, but it is **not an authorized continuation of L34**. Any successor must be registered as a fresh candidate with a new ownership audit, new estimand, and new Selection authorization.

**Anti-resurrection:** no E02, larger-model rerun, prompt/attribute search, third-person grounding patch, added post-document arm, or renamed `prospective encoding` continuation under L34.

## What E01 established

The frozen first-stage gate failed decisively on Llama-3.2-3B:

- `CROSSOVER_postP1(OLD)` = **-0.1554** [-0.1853, -0.1266] held-in;
- `CROSSOVER_postP1(OLD)` = **-0.0844** [-0.1136, -0.0552] held-out;
- `PIT_A` made its own trained family worse by **+0.383 nats/token**;
- `PIT_B` made its own trained family worse by **+0.413 nats/token**;
- 10/12 arm × attribute cells degraded.

The largest cell, `PIT_A / birth_city = +1.835`, was caused by the disjoint-city-pool control. Phase-1 therefore mainly installed answer-family priors/interference rather than the intended access specialization. The NEW phase is not interpretable for accounts A/B/C.

The recorded primary interaction was large (`PROSPECTIVE` +0.4215 held-in; +0.8134 held-out) and paraphrase-robust, but is void because the construct gate failed. Its best reading is an **answer-family prior × knowledge recency** interaction. This demonstrates that a large `NEW - OLD` interaction can arise without encoding-specific causation.

See `results/e01/G1_RESULTS.md` and `results/e01/G0_AND_BLOCKED_PRIMARY.md`.

## Correction: `NO_PIT` was not the PIT baseline

Jiang et al.'s relevant contrast is order: both sides receive a QA/instruction phase (`QA -> DOC` versus `DOC -> QA`). `NO_PIT` receives no curriculum, so it is not the baseline for the parent PIT effect. Commit `ee7bfe2` correctly withdrew the earlier overclaim that the parent phenomenon was reversed.

A true order-control arm would be necessary in a faithful PIT-derived study, but it is not sufficient to save L34.

## Deeper Selection failure 1 — the experiment changed the scientific object

The intended A/B manipulation was two access views over the **same underlying fact**. E01 instead used different relations:

- A: `birth_date`, `university`, `work_city`;
- B: `birth_city`, `company`, `major`.

A positive result could therefore be explained as relation/task-specific transfer: prior training on relation family A makes later family-A learning easier. That does not identify the stronger claim that anticipated access to the same knowledge changes how that knowledge is encoded.

## Deeper Selection failure 2 — `NEW - OLD` does not identify encoding locus

The original estimand was:

```text
CROSSOVER(age) = PREF(PIT_A, age) - PREF(PIT_B, age)
PROSPECTIVE    = CROSSOVER(NEW) - CROSSOVER(OLD)
```

The intended logic was that OLD subtraction would remove retrieval-policy specialization. E01 shows that a pure readout/output prior can affect newly learned facts more strongly than older facts. Therefore:

> **NEW-specific is not encoding-specific.**

Knowledge age is not a valid proxy for causal locus. This attacks the decisive quantity itself, not only the implementation.

## Why an order-control repair is still insufficient

`QA -> DOC != DOC -> QA` can arise from generic path dependence: gradient alignment/interference, optimization-state dependence, forgetting, representation priming, relation-specific plasticity, or asymmetric readout priors. An order effect alone does not establish prospective encoding.

A successor would need an estimand tied directly to **what an identical document update does**, not only the final QA preference.

## Final authorization state

- E01 closed; no account A/B/C is supported or rejected by it.
- The +0.42/+0.81 interaction is preserved for reproducibility only.
- No 7B/8B escalation.
- No E02.
- No grounded-rerun repair.
- No order-arm-only repair.

> **L34 is KILL because question -> manipulation -> estimand does not uniquely identify the headline claim.**

## Pressure retained outside L34 — NOT A CANDIDATE

Retain only this pressure for future broad search:

> **Does learning an access function change the learning operator by which later raw-text exposure makes new facts usable?**

A future candidate should measure the increment caused by an identical document update, e.g. `Delta_q = L_q(theta) - L_q(U_doc(theta))`, and ask whether identical document updates produce selectively different `Delta_A - Delta_B` after different prior access training.

Before registration it must independently pass:

1. **Same-fact gate:** A/B are different access functions for the same underlying fact.
2. **Output-matching gate:** answer tokens/distributions, length, space, and format are matched.
3. **First-stage construct gate:** prior training demonstrably installs the access function on grounded third-set facts while target NEW facts remain unseen.
4. **Update-level identification gate:** primary estimand is the increment from the identical document update, not final QA preference or NEW-OLD subtraction.
5. **Fresh owner gate:** re-audit PIT successors, curriculum/continual-learning, gradient-alignment, and factual-learning dynamics for the exact quantity.

Failure of any gate means no new candidate.

## Durable lesson

A sophisticated interaction is not automatically an identifying experiment. A three-way interaction can be large, seed-stable, and paraphrase-robust while being generated by a nuisance mechanism whose strength differs across knowledge age. For mechanism questions, the operation must selectively manipulate the proposed causal route itself.