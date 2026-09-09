# Good Candidates

> **good/ means pilot-authorized, not paper-mainline-approved.**

**Approved paper mainline:** NONE

## Active

| ID | Candidate | Canonical package | Status |
|---|---|---|---|
| **L03** | **Table Value ≠ Observation Status** | [L03_TYPED_OBSERVATION/](L03_TYPED_OBSERVATION/) | **PILOT-AUTHORIZED** |

Historical L02/L04 experiment packages may remain in this directory for reproducibility, but they are **not active**:
- L02 → NO-GO / K175
- L04 → NO-GO / K180

Use **failed/KILLED_LEDGER.md** for the actual closure reasons. Do not duplicate those histories here.

---

# Meaning of promotion

A candidate enters good/ only after the pre-pilot gates in **RESEARCH_TOPIC_SELECTION.md** are materially satisfied:

- natural/important RQ;
- genuine scientific tension;
- credible data/evidence identification;
- surviving paper-level novelty;
- outcome robustness / scientific depth;
- Main-level calibration.

Promotion means only:

# **PILOT-AUTHORIZED**

It does not mean:
- paper mainline approved;
- novelty permanently safe;
- expected phenomenon must occur;
- candidate should be rescued after a bad pilot.

After the minimum decisive pilot, re-audit:
- data validity;
- interpretation;
- novelty/reviewer compression;
- Main-level scale;
- remaining C1→C2→C3 or equivalent.

---

# Canonical package

The candidate directory is the source of truth.

Keep the smallest useful set of candidate documents:
- **README.md** — current RQ, accounts, paper identity, verdict;
- **DATA_AND_GOLD.md** — data/evidence contract;
- **RELATED_WORK_AND_NOVELTY.md** — closest ownership/collisions;
- **RESEARCH_PLAN.md** — decisive pilot and expansion/kill routes;
- **PILOT_CARD.md** — exact first decisive experiment.

Execution artifacts such as claims, experiment registry, code, configs, data, and results stay inside the concrete candidate directory.

Do not create extra root-level candidate cards.

---

# L03 warning

Do not reduce L03 to:

> “Can an LLM understand Census sentinel codes?”

Its scientific identity must remain about whether **provider-defined observation status is a load-bearing semantic representation for modern table understanding**, with a real downstream modeling/evaluation consequence.

The local survivor is not the quality ceiling. Continue judging L03 against strong ACL/EMNLP/NAACL Main work during execution.
