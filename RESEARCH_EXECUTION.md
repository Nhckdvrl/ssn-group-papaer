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
- current one-sentence paper identity;
- current paper narrative;
- current C1 / C2 / C3;
- what is established vs still hypothetical;
- strongest current reviewer compression;
- the next claim that actually needs evidence.

A planned document may be wrong. The mainline may change when evidence changes.

Individual subclaims need not each be unprecedented, but they must be scientifically useful and non-trivial. The **overall narrative, idea, and load-bearing claim architecture must remain distinctly ours**.

Never replace a serious mainline with a trivial claim merely because it is easy to prove.

Most importantly:

> **Novelty belongs to the current claim, not to the original topic.**

A project that passed topic selection does **not** receive permanent novelty approval. If the RQ, major claim, mechanism, or paper identity changes during execution, the new version must earn novelty again from zero.

---

# 3. Claim Mutation = Mandatory Novelty Reset

This is a hard execution gate.

Research often changes direction because an experiment fails, a new mechanism appears, a boundary becomes central, or a supporting result grows into the paper headline. Those changes may improve the science, but they also invalidate the old novelty check.

## 3.1 Mutation triggers

Immediately trigger a new novelty audit if any of the following occurs:

- the RQ is materially rewritten;
- a new load-bearing C1 / C2 / C3 is introduced;
- a supporting finding is promoted into a major claim;
- a failure or null result causes a reinterpretation of the phenomenon;
- the proposed mechanism changes;
- the paper title / one-sentence contribution / reviewer takeaway materially changes;
- the story pivots from behavior to mechanism, from mechanism to measurement, from measurement to evaluation, etc.;
- fresh literature changes who owns the current scientific object;
- the strongest reviewer compression changes.

A wording cleanup is not a mutation. A change in what the paper is **scientifically claiming** is.

## 3.2 Mandatory Claim Novelty Delta

Before further scaling, write a short audit in the existing claim/related-work documents containing:

1. **Old RQ / old claim / old paper identity**;
2. **New RQ / new claim / new paper identity**;
3. **What evidence forced the change**;
4. **What is genuinely new in the new version**;
5. **Closest direct owners**, prioritizing ACL / EMNLP / NAACL Main and Best/Outstanding, then other top venues;
6. **What each owner already owns** at the scientific-question level, not merely method overlap;
7. **Strongest reviewer compression** of the new paper into prior work;
8. **Main-level width test**;
9. verdict: `PASS / HOLD / RECONSTRUCT / KILL`.

Do not write only “paper X does not use our dataset/model/intervention.” Novelty must survive at the **scientific object and paper-identity level**.

## 3.3 Stop rule

Until the mutated claim passes this audit:

> **Do not continue broad experiment expansion, model-zoo scaling, layer scans, or expensive confirmatory runs.**

Only run a minimal diagnostic if it is strictly necessary to determine what the new claim actually is. Otherwise, literature assassination and paper-identity audit come first.

This prevents a project from spending weeks validating a claim that later turns out to be already owned.

## 3.4 Main-level width test

A claim can be precise; the **paper identity must not survive only as a tiny leftover gap**.

For the current paper identity, ask:

- If model names, layer numbers, dataset IDs, and intervention names are removed, is there still a natural scientific question?
- Can the RQ be explained in one or two ordinary sentences without relying on method details?
- Does the question matter at a width comparable to strong ACL / EMNLP / NAACL Main papers of the same type?
- Is the paper studying a real scientific object, mechanism, failure mode, measurement problem, or evaluation principle — or only a conjunction of conditions nobody happened to test together?
- Are we forced to preserve novelty by stacking restrictions such as **this domain + this model + this intervention + this metric + this subset**?
- If the strongest related papers are named in the first page of the introduction, can we still state a clean, non-defensive gap?

### Narrowness warning

Trigger `HOLD` or `RECONSTRUCT` when the only defensible novelty becomes something like:

> “A studied X, B studied Y, C studied Z, but nobody combined X+Y+Z on our dataset with our intervention.”

A combination may still be publishable if it reveals a genuinely new scientific principle, but **the combination itself is not enough**.

Strong Main papers often have narrow experiments but a clear and reasonably broad scientific object. Do not confuse precise claims with a microscopic paper identity.

## 3.5 Reviewer-compression test

For every mutated mainline, explicitly try to defeat the paper with the strongest possible compression:

> `Prior Work A + Prior Work B + Prior Work C = our paper.`

Then ask:

- What scientific statement remains that none of A/B/C owns?
- Is that remainder understandable and important without citing our exact experimental machinery?
- Is it large enough to carry a Main paper rather than only a supporting experiment?

If the answer is no, do not protect the project with narrower wording. Reconstruct or kill it.

---

# 4. Continuous Top-Conference Alignment

Before every **new load-bearing claim** or **new major experiment**, inspect the strongest relevant ACL / EMNLP / NAACL Main work; use Best/Outstanding/Theme papers and other top venues when appropriate.

This check must be repeated after every claim mutation under Section 3. The original topic-selection audit cannot be reused automatically for a materially different claim.

Alignment is **dynamic, not a fixed checklist**. Select comparison papers and dimensions according to the project type. A mechanistic project may need stronger causal controls; a measurement paper may need stronger construct validation; a document-NLP system may need stronger real-data coverage and error analysis.

Useful checks include:

### Problem
- Is our RQ too narrow or too broad?
- Does it matter at the same level?
- Does the current RQ still look like a Main-level scientific question after methods are removed?

### Claim
- Is the claim novel enough **in its current wording and abstraction**?
- Is it too obvious?
- Does it deepen the mainline or merely state an expected fact?
- Would a reviewer ask “why did this experiment need to be run?”
- Has a recent paper already owned the abstract principle even if our implementation differs?

### Evidence
- Is the experiment decisive enough for the claim?
- Are controls/baselines/uncertainty comparable to strong papers?
- Does the evidence identify the claimed construct rather than a convenient proxy?

### Narrative
- Are we developing a genuinely new paper story?
- Even if individual questions/claims have nearby precedents, is the final narrative distinctly ours?
- Is the narrative new because of a scientific insight, or only because several known ingredients are connected?

A project is not allowed to drift below the top-conference bar simply because implementation has already begun.

---

# 5. Data Is a First-Class Scientific Object

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

# 6. Claim Discipline

Every load-bearing claim receives an ID in the claim ledger.

For each claim record:
- exact wording;
- why it matters to C1/C2/C3;
- novelty status;
- date / literature scope of the latest novelty audit;
- nearest related work and what each work owns;
- strongest reviewer compression;
- supporting experiments;
- current status: hypothesis / supported / weakened / rejected / HOLD-for-novelty.

Before adding or promoting a claim, ask:

> Is this claim scientifically non-trivial?

> Does it deepen our narrative, discriminate explanations, establish a boundary, or change an NLP decision?

> Has this exact **current** claim passed the mutation-triggered novelty and width audit?

A result being discovered in our experiment does **not** imply that the resulting scientific claim belongs to us. The claim may already have a prior owner even if our observation was independent.

Avoid:
- “method X performs better” without a scientific reason;
- obvious control results promoted into main claims;
- tiny benchmark observations;
- post-hoc claims invented only because a number happened to move;
- treating an internally discovered mechanism or reinterpretation as novel before searching its direct owners;
- narrowing a collided claim until only a technically unique but scientifically small remainder survives.

---

# 7. Experiment Discipline

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

If the result changes the RQ, paper identity, major mechanism, or C1/C2/C3, **stop and execute Section 3 before designing the next major experiment**.

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

Do not use additional experiments to compensate for a paper identity that has become too narrow after novelty collisions.

---

# 8. Model and Environment Policy

- Prefer the existing local virtual environment.
- If dependencies genuinely conflict, create a clean project-specific environment rather than destabilizing the shared one.
- Models already in the Hugging Face cache should be reused.
- Download additional models when scientifically justified.
- Choose model sizes/families that reviewers care about.
- Do not over-invest in tiny models merely because they are cheap.
- Scale should be sufficient to test the claim, while pilots should remain as small as possible.

Where model-family robustness is load-bearing, use multiple credible families/sizes rather than many near-duplicate checkpoints.

---

# 9. Iteration and Kill Logic

A failed expected effect does **not** automatically kill a healthy research question.

Re-evaluate:
- did Account B win?
- is there a meaningful boundary?
- is there preservation/equivalence?
- did the experiment lack leverage?
- did the data/gold fail?
- did fresh literature occupy the narrative?
- did the failure create a new scientific claim that now requires a full novelty reset?

A productive failure may improve the project by revealing a better construct or mechanism. But the new interpretation is **not automatically ours**. Treat it as a new candidate RQ and run Section 3 before investing further.

Kill or reconstruct when:
- the data cannot identify the claim;
- the paper-level novelty is gone;
- the remaining claim becomes trivial;
- the research space collapses;
- no credible C1→C2→C3 remains;
- the only remaining novelty is a narrow conjunction of dataset/model/intervention/metric restrictions;
- the strongest reviewer compression fully captures the paper and the remainder is too small for Main;
- Main-level width can be recovered only by overclaiming beyond the evidence.

Use `HOLD` when evidence quality is strong but current paper-level novelty/width has not yet cleared the Main bar. `HOLD` means stop expansion and re-audit; it does not mean protect the project because of sunk cost.

Do not continue due to sunk cost.

---

# 10. Reproducibility and Project Hygiene

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

# 11. Relationship to Topic Selection

Topic selection and project execution are separate:

**Selection asks:** is this a Main-level question worth starting?  
**Execution asks:** what evidence is required to answer it rigorously, and does the evolving claim still deserve Main-level status?

Execution must send the project back to selection/re-audit when:
- direct gold fails;
- novelty changes;
- the main claim becomes obvious;
- the expected paper shape collapses;
- a productive failure produces a new central interpretation;
- a supporting finding becomes the new paper identity;
- new literature compresses the current narrative;
- the current claim passes only by becoming materially narrower than strong ACL / EMNLP / NAACL Main work.

The key rule is:

> **A selected topic is not grandfathered into novelty. Every materially new claim must re-earn the right to be the paper.**

Selection must not dictate unnecessary methodology.  
Execution must not lower the selection bar because work has already been invested.
