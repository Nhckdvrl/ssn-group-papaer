# Candidate Card — Mandatory Pre-Pilot Template

> **No target-model compute before this card is complete and all five hard gates are YES.**
>
> A candidate is not allowed to depend on one exciting failure phenomenon, and novelty is judged at the **paper-story level**, not by demanding an untouched neighborhood.

## Metadata

- **Candidate ID:**
- **Short name:**
- **Date opened:**
- **Current status:** SEARCH / AUDIT / GOOD / KILL
- **Paper identity:** behavioral / measurement / linguistic theory / causal-mechanistic / methodology / task-definition / other
- **Search track(s):** high-level reverse / old-problem-new-method / data-first / competing explanations / measurement / representation necessity / new scientific operation / contemporary NLP / other

---

## 1. RQ — one sentence

> 

## 2. Why ACL / NLP cares — max two sentences



## 2.5 TOP-CONFERENCE ALIGNMENT — mandatory

This candidate is judged against **ACL / EMNLP / NAACL Main**, with **Outstanding / Best / Best Theme Paper** as the aspirational bar. L02/L03/L04 are not the quality benchmark.

### Closest high-level reference papers

At least 3 concrete papers, preferably including at least one award paper:

1. **Paper / venue / award:**
   - Similar paper identity because:
   - What its RQ scale teaches us:
2. **Paper / venue / award:**
   - Similar paper identity because:
   - What its evidence/C1→C2→C3 teaches us:
3. **Paper / venue / award:**
   - Similar paper identity because:
   - What its consequence/novelty teaches us:

### Dimension-by-dimension alignment

| Dimension | Top-conference reference bar | Our candidate | Verdict |
|---|---|---|---|
| RQ scale | | | PASS / WEAK / FAIL |
| Natural object | | | |
| Scientific tension | | | |
| Data / gold | | | |
| Identification / decisiveness | | | |
| Paper-level novelty | | | |
| C1→C2→C3 | | | |
| Consequence | | | |
| Breadth / generality | | | |
| Plain-language identity | | | |

### Outstanding-level reviewer test

> If the result is strong and clean, why is this a paper of independent scientific/methodological interest rather than a narrow benchmark cell or competence study?

> 

**Alignment gate:** PASS / WEAK / FAIL

Any serious FAIL blocks promotion to good/.

## 3. Plain example

Explain the object without model names, benchmark jargon, or specialist terminology.

---

## 4. REAL OBJECT

- What real language/NLP object existed before this project?
- Would the question remain important without “LLM”, model names, and dataset names?
- Why is it durable?
- Is the object natural rather than constructed to create leverage?

**Gate:** YES / NO

---

## 5. SCIENTIFIC TENSION / CONTRIBUTION AXIS

### Account A
> 

**Prediction:**

### Account B
> 

**Prediction:**

### Principled heterogeneity / boundary
> 

Why are A and B both plausible before seeing target-model results?

**Gate:** YES / NO

---

## 6. OUTCOME ROBUSTNESS — mandatory before compute

### If the expected phenomenon does NOT occur, what is the paper?

> 

This must be a real pre-specified scientific answer, for example:
- preservation;
- equivalence;
- non-inferiority;
- representation dispensability;
- stability;
- a principled boundary.

“Negative result / p > .05” is not enough.

### Near-null interpretation

- What equivalence/non-inferiority quantity or margin would make a preservation claim meaningful?
- What near-null result would instead mean the task simply had no leverage?

---

## 6.5 RESEARCH-SPACE ROBUSTNESS — mandatory before compute

- **Broader scientific object / decision problem:**
- **Natural subquestion 1:**
- **Natural subquestion 2:**
- **Natural subquestion 3:**
- **If the first planned effect is absent, which subquestions remain live?**
- **What mechanism / boundary / decision-map paper remains possible without inventing post-hoc hypotheses?**
- **Why is this not merely “if X causes Y, we have a paper”?**

**Gate:** YES / NO

A NO blocks promotion even if ordinary null-result robustness is technically possible.

---

## 7. GOOD DATA + GOLD

- **Exact dataset/resource/materials:**
- **Exact version/release:**
- **Why natural / externally grounded:**
- **Unit of analysis:**
- **Exact gold source:**
- **Why gold is independent of the evaluated model class:**
- **Evidence the required fields are already extractable:**
- **Deterministic action mapping:**
- **Any author-created stimuli or labels? If yes, why are they non-load-bearing?**
- **Replication substrate and its verification status:**

Do not write “after verifying,” “should support,” or “likely extractable” for load-bearing gold.

**Gate:** YES / NO

---

## 8. PAPER-LEVEL NOVELTY — literature assassination

### Classical / established ownership

What does prior literature already own that we should explicitly concede?

### Closest modern neighbors

1.
2.
3.

### Nearest direct collision

- **Paper:**
- **What it already owns:**
- **What it does not own:**

### Reviewer compression

> **“This is just ______.”**

The blank must accurately compress the **whole proposed paper**, not merely name its broad field.

### Why that compression is false

> The full scientific story differs because...

### What part of the full paper-level story is actually new?

> 

This answer cannot be only:
- dataset;
- model;
- prompt;
- language;
- exact benchmark cell;
- renamed classic distinction.

### Exact kill-level collision definition

> KILL if a prior paper is found that already...

**Gate:** YES / NO

---

## 9. DECISIVE PAPER

### C1 — Core scientific answer



### C2 — Explanation / mechanism / boundary



### C3 — Consequence

Consequence for at least one of:
- modeling;
- task definition;
- evaluation;
- representation;
- interpretation;
- methodology;
- established NLP conclusion.

### Outcome map

| outcome | scientific meaning | still informative? |
|---|---|---|
| Account A wins | | YES / NO |
| Account B wins | | YES / NO |
| principled heterogeneity / boundary | | YES / NO |
| preservation / equivalence | | YES / NO |
| near-null with inadequate leverage | | usually KILL |

### Minimum decisive pilot

- **Smallest exact dataset/subset:**
- **Smallest model set:**
- **Primary estimand:**
- **Pre-specified effect / equivalence criterion:**
- **What result would PROMOTE:**
- **What result would KILL:**

**Gate:** YES / NO

---

## 10. Development path

### Phase 0 — data/gold contract

### Phase 1 — minimum decisive pilot

### Phase 2 — outcome-based promote/kill decision

### Phase 3 — C1 full evidence

### Phase 4 — C2 explanation/boundary

### Phase 5 — C3 consequence

### Phase 6 — replication/generalization only if needed

---

# Final gate table

| gate | verdict | one-line evidence |
|---|---|---|
| REAL OBJECT | YES / NO | |
| SCIENTIFIC TENSION | YES / NO | |
| GOOD DATA | YES / NO | |
| PAPER-LEVEL NOVELTY | YES / NO | |
| OUTCOME-ROBUST DECISIVENESS | YES / NO | |
| RESEARCH-SPACE ROBUSTNESS | YES / NO | |

## Final decision

**KILL / KEEP SEARCHING / PROMOTE TO good/**

### If KILL

Append the result to failed/KILLED_LEDGER.md.

Record:
- primary failure type;
- secondary failure type(s);
- exact reason;
- collision/evidence if relevant;
- reviewer compression;
- reopen condition.

### If PROMOTE

Create a **candidate directory** under good/ with:

- README.md
- RELATED_WORK_AND_NOVELTY.md
- DATA_AND_GOLD.md
- RESEARCH_PLAN.md

Promotion means **pilot-authorized**, not paper-mainline-approved.
