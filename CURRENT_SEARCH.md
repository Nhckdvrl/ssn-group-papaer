# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Current target:** find additional five-gate candidates without lowering the bar.

> Repository sync on 2026-09-07:
>
> - authoritative kill ledger is now through **K124**;
> - next kill ID is **K125**;
> - `good/` still contains only **L02 — Semantic Role Completion ≠ Referential Commitment**;
> - L02 remains **PILOT-AUTHORIZED / NOT MAINLINE APPROVED**;
> - no A-level or B-level live lead survived the latest task-ontology batches.

---

# Latest task-ontology dual-role audit

The previous version of this file lagged behind the actual search at K084. The broader search had already reached K117; the following newly audited leads are now formally closed:

| ID | lead | verdict | shortest reason |
|---|---|---|---|
| **K118** | Answer correctness ≠ evidence grounding | KILL | answer-vs-grounding/attribution is already a direct QA/RAG evaluation parent |
| **K119** | Entity coherence ≠ implicit discourse relation | KILL | PDTB already owns the label distinction; EntRel does not cleanly license “do not generate relation” |
| **K120** | Backchannel/acknowledgment ≠ agreement | KILL | classic dialogue-act work already makes exactly this distinction operational |
| **K121** | Primary trial outcome ≠ secondary outcome | KILL | old extraction schemas and modern LLM trial extraction explicitly own the roles |
| **K122** | Soft preference ≠ hard constraint | KILL | ACL 2026 HARPO directly models preferences and hard/soft constraints |
| **K123** | Speech overlap ≠ interruption | KILL | LREC annotations + Full-Duplex-Bench + 2026 TurnBench directly own the parent |
| **K124** | Accepted answer ≠ community-preferred answer | KILL | ACL Findings 2026 CoPA directly owns accepted-vs-top-voted divergence |

**Live leads after this batch: 0.**

---

# Stronger rule learned from K118-K124

The search target remains **Role A ≠ Role B**, but a mature annotation distinction is not enough.

A candidate fails if the best story is merely:

> “The old task already labeled A and B separately; now ask an LLM to reproduce the label or expose it in free-form output.”

That is not a new parent.

The required shape is stronger:

> **A pre-existing natural distinction + a modern action/output assumption that genuinely collapses the distinction + externally grounded evidence that the collapse can change the task’s scientific conclusion.**

In particular:

1. **Old labels do not automatically imply new actions.**  
   K119 fails because EntRel does not externally force “abstain from relation generation.”

2. **A perfect external state can still be fully occupied.**  
   K124 has exceptionally clean natural gold, but CoPA already owns accepted-vs-top-voted preference divergence.

3. **A modern system already exposing the roles is fatal to an “unrecognized ontology” story.**  
   K122 dies because HARPO already has separate preference and constraint operations and explicitly represents hard/soft constraints.

4. **The role distinction must change more than classification.**  
   If the modern consequence is simply “predict the old label before generating,” reviewer compression usually wins.

---

# Next search program

Do **not** spend more cycles on dialogue acts, PDTB relation labels, clinical outcome-role extraction, recommendation constraint types, turn-taking/overlap, or accepted-vs-voted QA.

Prioritize three narrower search shapes:

## 1. Same output, different correctness condition

Find mature NLP tasks where two examples can receive the **same observable model output** but that output has a different correctness interpretation because the underlying natural role differs.

The distinction must already exist independently, but modern evaluation/task definitions must actually merge the correctness conditions.

## 2. Task-specific measurement reversal

Look for an existing leaderboard/task score that combines two scientifically different quantities.

Require, before promotion:

- existing natural outputs/data;
- independent labels for the two quantities;
- a plausible ranking or scientific-conclusion reversal;
- fresh search showing the decomposition/reversal parent is not already owned.

## 3. External-state-grounded language interpretation

Use external reality only as gold for a language question.

The object must remain:

> “What role/state does this text express, and what linguistic action is licensed?”

—not software/business outcome prediction, personalization, or generic preference modeling.

---

# Mandatory search discipline

For every serious lead:

1. state the natural object and one plain-language example;
2. state the **modern action mapping** implied by the old/external gold;
3. write Account A and Account B before looking for an effect;
4. identify exact natural data and independent gold;
5. search the classical parent plus 2024–2026 ACL/EMNLP/NAACL and neighboring venues;
6. force reviewer compression: **“This is just ____.”**
7. kill immediately if the compression is true;
8. promote only if all five gates are clearly YES.

> **No GPU until all five gates are YES.**
