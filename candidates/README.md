# Six-Candidate Research Portfolio — 2026-09-08

**Target:** NAACL Main  
**External bar:** ACL / EMNLP / NAACL Main, aspirationally Best / Outstanding / Best Theme  
**Approved paper mainline:** NONE

> This directory contains **serious candidates under active comparison**. It is intentionally separate from `good/`: `good/` means pilot-authorized, while a detailed package here means the topic has survived broad search strongly enough to deserve full data/novelty/pilot auditing.

**Local execution entrypoint:** [`../LOCAL_AGENT_START.md`](../LOCAL_AGENT_START.md). Give that single file to the local agent when starting experiments.

---

## Current six-topic pool

| ID | Candidate | Status | Canonical package |
|---|---|---|---|
| **L03** | **Table Value ≠ Observation Status** | **PILOT-AUTHORIZED** | [../good/L03_TYPED_OBSERVATION/](../good/L03_TYPED_OBSERVATION/) |
| **L06** | **Study Identity Is Not Document Identity** | **SERIOUS / PILOT-READY** | [L06_STUDY_IDENTITY/](L06_STUDY_IDENTITY/) |
| **L07** | **Official Correction ≠ Current Scholarly Claim** | **SERIOUS / data-yield audit before pilot** | [L07_OFFICIAL_CORRECTION/](L07_OFFICIAL_CORRECTION/) |
| **L08** | **Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning** | **SERIOUS / A-** | [L08_READOUT_DIMENSION/](L08_READOUT_DIMENSION/) |
| **L09** | **RLVR Disagreement: Erased or Suppressed?** | **SERIOUS / A-** | [L09_RLVR_DISAGREEMENT/](L09_RLVR_DISAGREEMENT/) |
| **L10** | **Success Teaches, Failure Doesn't?** | **SERIOUS / A-** | [L10_SUCCESS_FAILURE_ASYMMETRY/](L10_SUCCESS_FAILURE_ASYMMETRY/) |

---

# Portfolio rule

These are **six topics to compare and assassinate**, not six approved papers.

A detailed package does not protect a candidate from death.

Each active package must answer:
1. What is the simple natural RQ?
2. What direct data/intervention actually identifies it?
3. What prior work already owns?
4. What is the exact paper-level novelty?
5. What happens if the expected headline effect is absent?
6. What is the smallest decisive pilot?
7. What result/literature/data failure kills it?

---

# Current maturity order

## Tier A / nearest to action

### L03 — Table Value ≠ Observation Status
Already pilot-authorized. Cross-provider design now includes Census ACS and Eurostat/SDMX.

### L06 — Study Identity Is Not Document Identity
Data/gold and novelty are strong enough for a small pilot. Main risk is collapsing to “CochraneForest grouping ablation”; the experiment must hold papers fixed and manipulate evidence-unit identity through oracle / absent / split / merge states.

### L07 — Official Correction ≠ Current Scholarly Claim
Scientific object and novelty are strong. The remaining blocking gate is empirical dataset yield: run the publisher-authored old→new proposition audit before target-model compute.

## Tier A- / serious mechanistic candidates

### L08 — Low-Dimensional Readout
The phenomenon is already reported by an EMNLP 2025 People’s Choice paper. Our paper only exists if it explains the cross-capability asymmetry by separating local readout damage, autoregressive accumulation, task-specific geometry, and output-length artifacts.

### L09 — RLVR Disagreement
The EACL 2026 behavioral result is the parent, not our novelty. The candidate lives on causal representation-preservation vs readout-suppression decomposition, ideally with a controlled pre/post RLVR pair and behavioral recovery intervention.

### L10 — Success vs Failure Adaptation
ImplicitMemBench establishes preference≈75% vs inhibition≈17.6%; EscapeBench gives natural useless-repetition cases. The candidate lives on locating the asymmetry at outcome memory / credit assignment / policy knowledge / actual inhibition, followed by targeted repair.

---

# Required package structure

Every L06–L10 directory now contains:

1. **README.md**
   - simple RQ;
   - natural object;
   - competing accounts;
   - outcome robustness;
   - paper identity;
   - C1→C2→C3;
   - hard gates;
   - main reviewer compression.

2. **RELATED_WORK_AND_NOVELTY.md**
   - direct parent;
   - closest 2024–2026 neighbors;
   - what prior work owns;
   - what we cannot claim;
   - exact new paper-level story;
   - reviewer compression;
   - kill-level collision definition.

3. **DATA_AND_GOLD.md**
   - exact data/evidence;
   - load-bearing gold or intervention;
   - conditions;
   - metrics;
   - controls;
   - validity kill conditions.

4. **RESEARCH_PLAN.md**
   - minimum decisive pilot;
   - competing outcome routes;
   - causal/diagnostic phases;
   - C1→C2→C3;
   - Main-level expansion requirements;
   - kill conditions.

---

# Important distinction from L03

Do **not** mechanically force all topics to imitate L03's provider-defined annotation structure.

- L03/L06/L07 are largely external-state/data-identification papers.
- L08/L09/L10 are causal behavior/representation papers.

For mechanism papers, objective benchmark/human/environment observations plus controlled interventions can be the correct evidence chain. “External provider gold” is not a universal requirement.

---

# Immediate next actions

1. **L07:** run correction-notice proposition-yield audit before any expensive compute.
2. **L06:** run a small matched-paper oracle/flat/split/merge pilot.
3. **L08:** exact reproduction + teacher-forcing vs free-running decomposition.
4. **L09:** secure a credible open pre/post RLVR pair or train a controlled pair.
5. **L10:** build/adapt a tightly matched positive-vs-negative four-stage pilot.
6. Continue L03 pilot under its existing canonical package.

After these pilots, re-rank all six against the same external Main bar and kill aggressively.
