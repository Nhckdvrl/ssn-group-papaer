# Local Agent Start — Execute the Six Research Candidates

**Date:** 2026-09-08  
**Target:** NAACL Main  
**Mode:** RESEARCH EXECUTION, not topic search  
**Approved paper mainline:** NONE

> **Give this file to the local research agent as the single starting document.**

The six-topic search portfolio is complete. Do **not** spend time generating more topics unless execution kills candidates and the user explicitly reopens search.

Your job is now to run the smallest decisive audits/pilots, update evidence, and aggressively kill or promote candidates according to the results.

---

# 1. Mandatory reading order

Before executing any experiment:

1. **This file — `LOCAL_AGENT_START.md`**
2. **`RESEARCH_EXECUTION.md`** — authoritative rules for claims, data, experiments, reproducibility, and kill logic.
3. **`candidates/README.md`** — six-topic portfolio and current maturity.
4. For the selected candidate, read **all five canonical files**:
   - `README.md`
   - `DATA_AND_GOLD.md`
   - `RELATED_WORK_AND_NOVELTY.md`
   - `RESEARCH_PLAN.md`
   - `PILOT_CARD.md`

For L03 the canonical directory is under `good/`; L06–L10 are under `candidates/`.

Do not execute from old rough notes in `CURRENT_SEARCH.md` when they conflict with the canonical candidate package.

---

# 2. Six canonical candidate packages

## L03 — Table Value ≠ Observation Status
Directory:
`good/L03_TYPED_OBSERVATION/`

Start from:
`good/L03_TYPED_OBSERVATION/PILOT_CARD.md`

Core pilot:
- Census ACS + Eurostat/SDMX;
- direct generation vs explicit status→value typing;
- documentation present/absent;
- held-out/cross-provider conventions;
- decide whether provider-defined observation status remains a load-bearing TableQA representation.

## L06 — Study Identity Is Not Document Identity
Directory:
`candidates/L06_STUDY_IDENTITY/`

Start from:
`candidates/L06_STUDY_IDENTITY/PILOT_CARD.md`

Core pilot:
- same exact papers;
- oracle vs flat vs wrong-split vs wrong-merge study identity;
- separate paper extraction from study/evidence accounting;
- measure synthesis-level consequences.

## L07 — Official Correction ≠ Current Scholarly Claim
Directory:
`candidates/L07_OFFICIAL_CORRECTION/`

Start from:
`candidates/L07_OFFICIAL_CORRECTION/PILOT_CARD.md`

**First action is a data-yield audit, not GPU inference.**

Core audit:
- collect ~500 linked PMC/PubMed correction notices;
- measure Tier-1/Tier-2 proposition-level old→new yield;
- kill if substantive direct gold is too sparse/homogeneous;
- only then run original vs flat original+correction vs explicit-update pilot.

## L08 — Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning
Directory:
`candidates/L08_READOUT_DIMENSION/`

Start from:
`candidates/L08_READOUT_DIMENSION/PILOT_CARD.md`

Core pilot:
- reproduce parent readout-dimension effect;
- GSM8K vs knowledge/extraction + long non-reasoning generation control;
- teacher-forced vs free-running reasoning;
- distinguish local readout bottleneck from autoregressive error accumulation and task-specific geometry.

## L09 — RLVR Disagreement: Erased or Suppressed?
Directory:
`candidates/L09_RLVR_DISAGREEMENT/`

Start from:
`candidates/L09_RLVR_DISAGREEMENT/PILOT_CARD.md`

Core pilot:
- reproduce established disagreement degradation;
- secure/create a clean pre/post RLVR model pair;
- layerwise human-disagreement information;
- at least one causal patch/steering/readout intervention;
- determine representation erasure vs output suppression.

## L10 — Success Teaches, Failure Doesn't?
Directory:
`candidates/L10_SUCCESS_FAILURE_ASYMMETRY/`

Start from:
`candidates/L10_SUCCESS_FAILURE_ASYMMETRY/PILOT_CARD.md`

Core pilot:
- matched positive/negative experiences;
- outcome memory → causal attribution → policy knowledge → actual first action;
- locate the first asymmetric transition;
- targeted repair;
- natural validation on EscapeBench-style failure repetition.

---

# 3. Default execution order

If only one local agent is available, use **information-gain / kill-cheaply-first** order:

1. **L07** — correction proposition-yield audit. Cheapest blocking gate; no GPU needed initially.
2. **L06** — matched-paper oracle/flat/split/merge pilot. Strong data and crisp causal intervention.
3. **L08** — reproduce + teacher-forcing/free-running mechanism split.
4. **L10** — matched success/failure four-stage pilot.
5. **L09** — secure/train matched RLVR pair, then causal mechanism pilot.
6. **L03** — continue/complete the already pilot-authorized cross-provider typed-observation pilot.

If compute/resources permit parallel work, L03/L06/L07/L08/L10 are largely independent. L09 may require the most setup because matched pre/post RLVR checkpoints are load-bearing.

This ordering is logistical, **not a scientific ranking**.

---

# 4. Execution discipline

For the candidate being executed, treat its canonical directory as the concrete subproject directory.

Create/use inside that directory as needed:

```
CLAIMS.md
EXPERIMENTS.md
src/
scripts/
configs/
data/
results/
```

Do not scatter candidate-specific experiment files into the repository root.

Before each substantive run, record in `EXPERIMENTS.md`:
- experiment ID;
- linked claim;
- exact question;
- data/subset;
- model/revision;
- conditions;
- metrics;
- expected informative outcomes;
- kill/interpretation conditions.

After each run record:
- exact command/config;
- raw result path;
- summary;
- uncertainty/statistical test where relevant;
- interpretation;
- whether the candidate survives, changes, or dies.

---

# 5. Hard rules for the local agent

## Do not protect a topic because it is in the six-topic pool
The six candidates are for **mutual assassination**. None except L03 is even pilot-authorized yet, and no paper mainline is approved.

## Do not gamble on one exciting effect
Use the pre-specified alternative outcomes in each `PILOT_CARD.md`.

## Do not invent new load-bearing gold
If the candidate's data/gold contract fails, stop and report the failure.

## Do not rescue a killed story with a new prompt/model/dataset
Re-run novelty/reviewer compression when pilot evidence changes the central story.

## Do not scale before the minimum decisive pilot
One clean causal/data result is more valuable than a large model zoo.

## Keep literature current
Before promoting a load-bearing claim, re-check the closest 2024–2026 ACL/EMNLP/NAACL and relevant ML papers.

---

# 6. What counts as completion of one candidate pilot

Return a compact decision package containing:

1. **Verdict:** GO / CONDITIONAL / NO-GO.
2. **Data validity:** did the actual data identify the claimed quantity?
3. **C1 result:** core answer.
4. **C2 result:** mechanism/boundary if tested.
5. **C3 consequence:** what NLP modeling/evaluation/practice changes?
6. **Novelty re-audit:** strongest reviewer compression after seeing the result.
7. **Evidence table:** main metrics + uncertainty.
8. **Exact reproducibility pointers:** scripts/configs/raw outputs.
9. **Next step:** expand, repair one missing control, or kill.

A low/negative expected effect is not automatically NO-GO. A broken estimand, invalid gold, fatal collision, or collapsed paper identity is.

---

# 7. Current portfolio status

- **L03:** PILOT-AUTHORIZED.
- **L06:** PILOT-READY.
- **L07:** DATA-YIELD AUDIT REQUIRED before model pilot.
- **L08:** SERIOUS / A-; mechanism pilot required.
- **L09:** SERIOUS / A-; clean pre/post RLVR pair required.
- **L10:** SERIOUS / A-; matched behavioral pilot required.
- **Approved paper mainline:** NONE.
- **Killed ledger:** through K180; next kill ID K181.

# Start now

If no other instruction is supplied, begin with:

> **`candidates/L07_OFFICIAL_CORRECTION/PILOT_CARD.md`**

Run the data-yield audit completely, write all code/data/results inside `candidates/L07_OFFICIAL_CORRECTION/`, and return a GO / CONDITIONAL / NO-GO decision before spending GPU on L07.
