# SSN Group Paper — Research Workflow

Target: ACL / EMNLP / NAACL Main.

The repository follows one simple decision chain:

> **SEARCH → SELECT → EXECUTE → RE-SELECT when the claim changes → PAPER or KILL**

The root documents have deliberately separate responsibilities. Do not combine them into one giant checklist.

## 1. SEARCH — find the right kind of scientific question

[RESEARCH_TOPIC_SEARCH.md](RESEARCH_TOPIC_SEARCH.md)

Answers:

- what kinds of questions we currently want;
- what search spaces are deprioritized;
- how to mine strong papers for topic provenance;
- anti-resurrection before deep search;
- how to turn a hook into a rough lead;
- SAME-QUANTITY checks and bounded owner search.

It does **not** authorize compute.

Current search taste strongly prioritizes:

> stable anomaly → mechanism; training/post-training dynamics; reasoning computation; representation → causal use; old empirical laws under modern model regimes.

It strongly deprioritizes data/benchmark/RAG/retrieval/metric/annotation/workflow topics unless an exceptional scientific question clearly transcends that framing.

## 2. PLAYBOOK — optional generators

[TOPIC_SEARCH_PLAYBOOK.md](TOPIC_SEARCH_PLAYBOOK.md)

A library of ways a question may originate.

Primary generators are model-computation/mechanism oriented. Data/evaluation/workflow generators remain available only as secondary options.

The playbook generates leads; it never approves them.

## 3. SELECT — decide whether the question deserves compute

[RESEARCH_TOPIC_SELECTION.md](RESEARCH_TOPIC_SELECTION.md)

Answers:

- is the RQ natural and consequential;
- is the mother phenomenon credible;
- is the question already owned;
- does the evidence identify the intended quantity;
- does the strongest successful result support a Main-level inference;
- are plausible outcomes interpreted before seeing results;
- can the scientifically important effect be resolved within the compute/noise budget;
- is there a natural Main-level growth path.

Selection explicitly separates two evidence regimes:

- **mechanism/model-computation:** observable + causal estimand + discriminating intervention + inference bridge;
- **external-task/data:** DIRECT GOLD + independent unit + construct validity.

This prevents mechanism papers from being forced into an annotation template while preserving strict construct validity.

## 4. EXECUTE — develop an authorized contribution

[RESEARCH_EXECUTION.md](RESEARCH_EXECUTION.md)

Answers:

- what each experiment must establish;
- how to track claim → experiment → result → conclusion;
- how to refresh resolution/noise estimates before expensive runs;
- how to distinguish phenotype, representation and causal control;
- when a claim mutation forces re-selection;
- how to calibrate depth/breadth against strong Main work;
- when to hold, reconstruct, archive, or prepare a manuscript.

Candidate-specific retrospectives belong in candidate/archive packages, not in the root workflow. Root execution keeps only durable transferable lessons.

## 5. Current state and anti-resurrection

[CURRENT_SEARCH.md](CURRENT_SEARCH.md) is the dated portfolio and current taste.

[failed/KILLED_LEDGER.md](failed/KILLED_LEDGER.md) is the authoritative anti-resurrection record.

Recent `search_rounds/` preserve investigated dead hooks so later agents do not repeatedly rediscover them.

A new model, dataset, prompt, domain, narrower mechanism, or prettier diagnostic does not reopen a killed scientific parent.

## 6. Repository practice

Read the current candidate’s latest README/status before action. Directory location is not authorization.

Ordinary project execution edits only the selected project. Root workflow maintenance requires explicit scope.

Preserve concurrent work. Keep large regenerable artifacts outside git when appropriate, with provenance/reproduction notes. Inspect outgoing history before pushing.

---

## Core philosophy

> **Easy to understand, hard to answer.**
>
> **Question first. Observation first. Method second. Abstraction last.**

The workflow is strict because we want Main-level questions, but strictness should filter bad realizations of good science — not steer the search toward whichever topic happens to have the cleanest dataset.
