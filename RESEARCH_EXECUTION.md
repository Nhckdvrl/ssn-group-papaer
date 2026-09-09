# Research Execution — Authoritative Project Workflow

This document governs **how to execute a selected research project**.  
It is independent from topic selection, but execution may expose data, novelty, or scientific problems that force the topic back to selection/re-audit.

---

# 0. Repository Safety

1. **Only modify the concrete subproject directory being worked on.**
2. Do not edit surrounding/root directories during ordinary project execution; GitHub may update them independently and unnecessary edits create conflicts.
3. A subproject is the single source of truth for its own code, data contracts, experiments, claims, and current narrative.
4. Do not preserve a stale mainline merely because an old document predicted it. Documents contain hypotheses; evidence may legitimately change the project.

---

# 1. Minimal Subproject Structure

Keep the project organized enough that every claim is reproducible and auditable.

Recommended structure:

```
<subproject>/
├── README.md                 # current RQ, mainline, current verdict
├── CLAIMS.md                 # claim ledger
├── RELATED_WORK.md           # live novelty + top-paper alignment
├── DATA.md                   # data/gold contract and provenance
├── EXPERIMENTS.md            # experiment registry
├── src/                      # reusable code
├── scripts/                  # executable experiment/data scripts
├── configs/                  # exact configs
├── data/                     # raw/processed data or pointers
└── results/                  # outputs, summaries, plots, tables
```

Do not create files mechanically if they add no value, but the information above must exist somewhere explicit.

---

# 2. Mainline Before Experiments

At every major iteration, state:

- current RQ;
- current paper narrative;
- current C1 / C2 / C3;
- what is established vs still hypothetical;
- the next claim that actually needs evidence.

A planned document may be wrong. The mainline may change when evidence changes.

Individual subclaims need not each be unprecedented, but they must be scientifically useful and non-trivial. The **overall narrative, idea, and load-bearing claim architecture must remain distinctly ours**.

Never replace a serious mainline with a trivial claim merely because it is easy to prove.

---

# 3. Continuous Top-Conference Alignment

Before every **new load-bearing claim** or **new major experiment**, inspect the strongest relevant ACL / EMNLP / NAACL Main work; use Best/Outstanding/Theme papers and other top venues when appropriate.

Alignment is **dynamic, not a fixed checklist**. Select comparison papers and dimensions according to the project type. A mechanistic project may need stronger causal controls; a measurement paper may need stronger construct validation; a document-NLP system may need stronger real-data coverage and error analysis.

Useful checks include:

### Problem
- Is our RQ too narrow or too broad?
- Does it matter at the same level?

### Claim
- Is the claim novel enough?
- Is it too obvious?
- Does it deepen the mainline or merely state an expected fact?
- Would a reviewer ask “why did this experiment need to be run?”

### Evidence
- Is the experiment decisive enough for the claim?
- Are controls/baselines/uncertainty comparable to strong papers?

### Narrative
- Are we developing a genuinely new paper story?
- Even if individual questions/claims have nearby precedents, is the final narrative distinctly ours?

A project is not allowed to drift below the top-conference bar simply because implementation has already begun.

---

# 4. Data Is a First-Class Scientific Object

Before major experiments, verify the exact relation between the scientific question and the data.

Record:
- source and exact version;
- unit of analysis;
- gold definition;
- preprocessing;
- filtering;
- split construction;
- leakage risks;
- transformations;
- missing/ambiguous states;
- limitations;
- reproduction command.

Rules:
- prefer natural existing data when they genuinely fit the RQ;
- **new data / controlled stimuli may be constructed when scientifically necessary**;
- keep construction minimal, interpretable, and natural;
- do not manufacture leverage through elaborate synthetic worlds or hypothesis-shaped artifacts;
- independently validate load-bearing labels/gold when the claim requires gold;
- LLM assistance may be used for non-load-bearing preparation only with auditing; it must not become circular evidence for the main claim;
- distinguish missing/ambiguous states from negative labels;
- verify that the data or manipulation directly identify the claimed quantity;
- compare data construction and validation practice with strong papers of the same paper identity.

If the data/evidence do not directly support the scientific claim, stop and repair/rethink before scaling experiments.

---

# 5. Claim Discipline

Every load-bearing claim receives an ID in the claim ledger.

For each claim record:
- exact wording;
- why it matters to C1/C2/C3;
- novelty status;
- nearest related work;
- supporting experiments;
- current status: hypothesis / supported / weakened / rejected.

Before adding a claim, ask:

> Is this claim scientifically non-trivial?

> Does it deepen our narrative, discriminate explanations, establish a boundary, or change an NLP decision?

Avoid:
- “method X performs better” without a scientific reason;
- obvious control results promoted into main claims;
- tiny benchmark observations;
- post-hoc claims invented only because a number happened to move.

---

# 6. Experiment Discipline

Every substantive experiment receives an ID.

Before running it, record:
- linked claim;
- hypothesis/question;
- why the experiment is necessary;
- dataset/subset;
- model(s);
- baselines;
- controls/ablations;
- metric/statistical test;
- config/seed;
- expected informative outcomes;
- kill/interpretation conditions.

After running, record:
- exact command/config;
- environment/model version;
- raw result path;
- summarized result;
- uncertainty/significance where relevant;
- interpretation;
- what claim changed.

Experiments are evidence for claims, not a collection of plots.

## Evidence economy

Do **not** run an experiment merely because a reviewer might conceivably ask for it.

A new experiment should materially do at least one of:
- distinguish live scientific explanations;
- change a load-bearing claim;
- determine GO / RECONSTRUCT / KILL;
- establish a consequence that the paper identity actually requires.

Controls and replications are valuable when they protect identification or test a live alternative explanation. They are not a default battery.

Use the **simplest evidence strong enough**. Add mechanism/causal intervention only when the claim requires it, not to cosmetically deepen a weak story.

---

# 7. Model and Environment Policy

- Prefer the existing local virtual environment.
- If dependencies genuinely conflict, create a clean project-specific environment rather than destabilizing the shared one.
- Models already in the Hugging Face cache should be reused.
- Download additional models when scientifically justified.
- Choose model sizes/families that reviewers care about.
- Do not over-invest in tiny models merely because they are cheap.
- Scale should be sufficient to test the claim, while pilots should remain as small as possible.

Where model-family robustness is load-bearing, use multiple credible families/sizes rather than many near-duplicate checkpoints.

---

# 8. Iteration and Kill Logic

A failed expected effect does **not** automatically kill a healthy research question.

Re-evaluate:
- did Account B win?
- is there a meaningful boundary?
- is there preservation/equivalence?
- did the experiment lack leverage?
- did the data/gold fail?
- did fresh literature occupy the narrative?

Kill or reconstruct when:
- the data cannot identify the claim;
- the paper-level novelty is gone;
- the remaining claim becomes trivial;
- the research space collapses;
- no credible C1→C2→C3 remains.

Do not continue due to sunk cost.

---

# 9. Reproducibility and Project Hygiene

Every important result must be traceable:

> **claim → experiment → config/code → data → raw output → summarized evidence**

Keep:
- commands;
- seeds;
- package/environment versions;
- model identifiers/revisions;
- hashes where useful;
- data processing scripts;
- generated tables/figures.

Never manually edit an output in a way that cannot be reproduced.

---

# 10. Relationship to Topic Selection

Topic selection and project execution are separate:

**Selection asks:** is this a Main-level question worth starting?  
**Execution asks:** what evidence is required to answer it rigorously?

Execution may send the project back to selection when:
- direct gold fails;
- novelty changes;
- the main claim becomes obvious;
- the expected paper shape collapses.

Selection must not dictate unnecessary methodology.  
Execution must not lower the selection bar because work has already been invested.
