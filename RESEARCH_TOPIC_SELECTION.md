# Research Topic Selection — Decide Whether a Question Deserves Compute

Updated: 2026-09-12. Target: ACL / EMNLP / NAACL Main.

This file evaluates a **concrete candidate** after search has found a worthwhile question.

It does not tell us where to search. See [RESEARCH_TOPIC_SEARCH.md](RESEARCH_TOPIC_SEARCH.md). Work after authorization is governed by [RESEARCH_EXECUTION.md](RESEARCH_EXECUTION.md).

The purpose of selection is simple:

> **Before spending serious compute, can this question produce a substantial, identifiable, resolvable contribution without changing its identity after seeing the result?**

---

## 1. Keep Four Objects Separate

| Object | Question |
|---|---|
| **Research question** | Is there a natural, consequential uncertainty worth resolving? |
| **Scientific account / operation** | What explanations or quantities can actually be distinguished? |
| **Evidence design** | Will the proposed observation support the intended inference? |
| **Paper contribution** | If successful, what new understanding would readers gain beyond prior work? |

A strong RQ does not rescue a weak operation. A clean experiment does not create a contribution. A large effect does not establish novelty.

---

## 2. First Classify the Candidate: Mechanism or External-Task

Do **not** force every topic through the same notion of “gold.”

### A. Mechanism / model-computation candidate

Typical questions:

- why a stable model behavior occurs;
- what changes across training stages;
- whether information is absent, represented, suppressed, rerouted, or misread;
- when a reasoning trajectory forms or revises a decision;
- which computation causally controls a behavior.

Required identification:

- a credible **mother phenomenon / behavioral observable**;
- a clear causal or discriminating **estimand**;
- competing accounts that imply different outcomes under the operation;
- an intervention/comparison whose meaning is controlled;
- a defensible bridge from observed change to the claimed mechanism.

A mechanism paper does **not** need human annotation simply because external-task papers do. But “decodable” is not “causally used,” and a patch effect is not automatically a mechanism.

### B. External-task / data / measurement candidate

Typical questions:

- extracting or predicting a real external state;
- evaluating a metric against a real target;
- reconstructing a scientific/document state;
- using naturally occurring labels or outcomes.

Required identification:

- **DIRECT GOLD** for the load-bearing estimand;
- clear object and independent unit;
- label/observable = the scientific quantity we claim, not a neighboring proxy;
- provenance, version, leakage and missingness understood.

A convenient annotation name is not enough. This is the lesson from K175-style construct mismatch.

### Hybrid candidates

If a paper uses an external task only to test a mechanism, separate the two layers explicitly:

> external behavioral observable → mechanistic operation → mechanistic inference

Do not let clean task gold substitute for the mechanistic bridge.

---

## 3. Natural Question and Mother-Phenomenon Gate

Before novelty details, ask:

1. Would the question still be interesting without our proposed method?
2. Does it arise from a real model behavior, training transition, empirical law, contradiction, or scientific problem?
3. If it is a mechanism paper, is the **mother phenomenon already credible**?
4. Are we studying why something happens, or secretly betting that the thing happens at all?

A mechanism project is strongest when the phenotype is already established and the uncertainty is the explanation.

Do not promote a one-cell anomaly merely because it is surprising.

---

## 4. Anti-Resurrection and Ownership Gate

Check `failed/KILLED_LEDGER.md`, archived candidates, recent search rounds, and relevant historical mechanistic work.

If similar to KXXX, write:

> **Not KXXX because ...**

The difference must change the scientific inference or leverage, not only model/dataset/prompt/domain.

Then perform a two-sided novelty audit.

For the proposed paper identity write:

1. central scientific statement without incidental model/dataset names;
2. closest primary works and exactly what each establishes;
3. strongest reviewer compression: **Prior A + Prior B + Prior C = our paper**;
4. strongest surviving contribution: what that compression still cannot explain or imply;
5. why resolving that remainder changes model understanding or an important NLP decision.

Judgments:

- **DIRECT COLLISION** — central answer/consequence already owned;
- **INSUFFICIENT CONTRIBUTION** — technically open but obvious, narrow, or low-value;
- **UNRESOLVED NOVELTY** — source verification still incomplete;
- **PLAUSIBLE INDEPENDENT CONTRIBUTION** — substantial open inference remains.

Component overlap is not collision. Component combination is not contribution by itself.

---

## 5. SAME-QUANTITY Gate for Reversal / Contradiction Stories

If the candidate relies on “old result vs modern result” or “Paper A vs Paper B,” verify:

- same object;
- same unit;
- same observable/gold when applicable;
- same estimand;
- same intervention meaning.

If this fails, the supposed contradiction is not established.

Do not build a paper on a bridge that still needs to be invented after the result.

---

## 6. Successful-Result Test

Assume the cleanest, strongest expected result occurs.

Write:

> **observation → measured quantity → inference → Main-level contribution**

For each arrow ask what simpler explanation survives.

Common failures:

- probe accuracy → claimed causal use;
- activation transplant → claimed computation that formed the state;
- behavior change + internal change → claimed mechanism without connecting them;
- model-family difference → claimed training effect;
- ranking reversal → claimed scientific law with no explanation;
- metric change → claimed construct validity without direct target evidence.

If even a spectacular effect only proves “another bias,” “another fragile benchmark,” “another model-specific failure,” or “this module matters,” the candidate is not ready.

Redesign or kill before scale-up.

---

## 7. Outcome Interpretation — Do Not Require Three Different Papers

The goal is **not** to force every positive/null/heterogeneous outcome into a publishable story.

The goal is to prevent post-hoc identity mutation.

Before pilot, state what the main plausible outcomes mean.

For a mechanism paper, for example:

- **Outcome A:** supports Account A over B because intervention X changes Y while the key control does not;
- **Outcome B / null:** rules out A or shows the proposed mechanism is not load-bearing; candidate may die or favor B;
- **Outcome C / heterogeneity:** meaningful only if a conditioning variable was scientifically motivated in advance.

A null may legitimately kill the route. That is fine.

What is forbidden is:

> A fails → invent paper B → B collides → invent paper C.

Evidence may motivate a **new candidate**, but the new identity must restart selection.

---

## 8. Resolution / Feasibility Gate — L19 Lesson

Before authorizing any expensive training or large-scale inference, estimate whether the scientifically important effect can be **resolved** with available resources.

Record, as far as can be estimated:

- parent / prior effect size;
- expected magnitude or upper bound of our discriminating effect;
- evaluation noise floor / minimum detectable effect;
- number of independent units;
- expected run-to-run / seed variance;
- required seeds or repeats;
- approximate GPU-hours and storage burden;
- whether the **interesting** outcome is a null that needs a tight confidence interval.

The decisive question is not:

> “Can we run a pilot?”

It is:

> **“Can our feasible experiment distinguish the scientific outcomes that matter?”**

If the expected signal is below the attainable resolution, mark:

- `HOLD — RESOLUTION/COST`, or
- `NO-GO — UNRESOLVABLE AT CURRENT BUDGET`.

Do not shrink the claim until it fits the hardware.

This gate would have stopped L19 before substantial compute: the matched effect was bounded below an already small parent effect and the meaningful null required parent-scale budgets.

---

## 9. Contribution-Path and Main-Level Gate

A selected candidate needs a plausible path beyond the first effect.

Ask:

- What would readers understand after C1 that they did not before?
- What deeper explanation, boundary, prediction, training origin, or intervention would naturally follow?
- Does C2/C3 deepen the **same** scientific contribution rather than pad the paper?
- What independent model/training/task axes are necessary for the claimed scope?
- What meaningful consequence follows if the mechanism/account is correct?

Do not require exactly three claims. Do require a paper-scale intellectual advance.

Calibrate against strong Main papers using at least the dimensions that matter:

- problem importance;
- decisive inference;
- explanatory depth;
- breadth required by the claim;
- consequence;
- remaining workload.

Awards are calibration, not templates.

---

## 10. Promotion States

- **ROUGH LEAD** — search-stage only; do not compute.
- **SERIOUS CANDIDATE** — worth full selection audit; no substantial compute.
- **PILOT-AUTHORIZED** — one named bounded experiment that resolves a specific uncertainty.
- **GO-TO-FULL-STUDY** — current contribution, evidence design, feasibility, and workload justify the program.
- **HOLD** — one explicit blocker plus a bounded way to decide it.
- **RECONSTRUCT** — a substantively new account/paper identity must restart selection.
- **ARCHIVED / NO-GO** — stop the route; preserve useful evidence and reason.

Directory names, previous approval, experiment count, and sunk compute confer no status.

---

## 11. Compact Authorization Record

A candidate package needs only one compact selection record containing:

1. **RQ + mother phenomenon + why important**
2. **candidate accounts / scientific operation**
3. **anti-resurrection + closest owners + reviewer compression**
4. **identification**
   - mechanism: observable + estimand + intervention + inference bridge; or
   - external-task: DIRECT GOLD + independent unit + construct bridge
5. **successful-result chain**
6. **pre-result outcome interpretations / kill conditions**
7. **resolution and compute budget**
8. **Main-level growth path and comparator gap**
9. **verdict and exact authorization scope**

Do not create additional root checklists.

---

## 12. Final Pre-Compute Questions

Before `PILOT-AUTHORIZED`, all must have satisfactory answers:

- Is the question itself worth knowing before we see the result?
- Is the mother phenomenon real enough for the proposed paper identity?
- Is the core quantity identified rather than proxied by a neighboring label?
- Is the decisive operation actually discriminating?
- Is the central question not already owned?
- Would the strongest positive result establish something substantial?
- Are plausible outcomes interpreted in advance rather than narratively rescued later?
- Can the important outcomes be statistically/computationally resolved within budget?
- Can the result naturally grow into a Main-level contribution without padding?

If not, do not compute simply because the experiment is cheap.

> **Selection protects scientific identity and investment. It should not dictate where we search, and it should not force mechanism science into a data-annotation template.**
