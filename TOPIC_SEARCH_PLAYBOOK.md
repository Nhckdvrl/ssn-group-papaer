# Topic Search Playbook — Idea Generator Library

**Status:** evolving, non-authoritative  
**Use with:** RESEARCH_TOPIC_SEARCH.md

This file answers only:

> **Where might a strong research question come from?**

It does not decide candidate quality. That belongs to **RESEARCH_TOPIC_SELECTION.md**.

Generators can be added or removed freely. No generator is mandatory.

**2026-09-11 clarification:** every generator produces a lead, not a contribution.
Develop the lead into a question, candidate idea/operation, discriminating
observation, and consequential answer before promotion. Illustrations below
are historical examples, not endorsements of those candidates' current status.

---

# A. Established anomaly → unresolved mechanism

Look for a strong paper that already establishes a stable important phenomenon but leaves the explanation weak or incomplete.

Signals:
- capability A survives while B collapses;
- unexpected scaling;
- striking model-family difference;
- large ablation asymmetry;
- qualitative explanation much weaker than the empirical result;
- “surprisingly,” “unclear why,” “remains unexplained,” “future work.”

Question shape:

> **Why does this happen, where is the bottleneck, and what intervention separates competing explanations?**

Desired development:

> phenomenon → competing accounts → decisive intervention → boundary/localization → repair/consequence

Current illustration: **L08**. The parent phenomenon is not our novelty.
Whether a valuable, identifiable explanation space remains must be audited.

Failure modes: reproducing the parent ablation on more models/benchmarks;
treating an unexplained effect as proof that any plausible explanation is new;
turning phenomenon -> probe -> patch into a mandatory paper recipe.

---

# B. Two strong papers → contradictory observations → unifying explanation

Find two credible papers whose results appear to imply opposite capability orderings or incompatible mechanisms.

Do not ask only:

> “Which paper is wrong?”

Prefer:

> **What hidden bottleneck or intervention difference makes both observations true?**

A strong paper can unify two literatures and predict when each pattern appears.

---

# C. Known behavior → bottleneck localization

Start from a behavioral weakness that is already credible.

Useful decompositions:
- encoding vs retrieval;
- representation vs readout;
- memory vs attribution;
- policy knowledge vs action;
- extraction vs aggregation;
- stored information vs output suppression;
- local-step damage vs autoregressive accumulation.

Question shape:

> **At which stage does the behavior first diverge, and can targeted intervention restore it?**

Current illustrations:
- **L09:** disagreement erased vs still represented but suppressed.
- **L10:** failure adaptation breaks at memory, attribution, policy knowledge, or action.

Failure mode: probe-only papers making strong causal claims.

---

# D. Old Problem / New Scientific Operation

Revisit a durable classic NLP question when modern models make a previously impossible scientific operation available.

Possible new leverage:
- causal intervention;
- long-context document access;
- end-to-end collapse of an old pipeline boundary;
- representation inspection;
- controlled post-training;
- model editing/unlearning;
- scalable natural-context experiments.

Question shape:

> **Does the modern regime change the scientific answer, or finally make an old disputed quantity identifiable?**

Failure mode: “run the old task with an LLM.”

---

# E. Measurement / construct-validity rewrite

A mature task may use a convenient output or metric that is not the scientific quantity people think it measures.

Question shape:

> **What does the task actually measure, what does the real object require, and does repairing that mismatch change a substantive conclusion?**

Current illustration: **L03**.

Requirements:
- independently defensible state/gold/identification;
- a clear estimand;
- a consequence beyond “the metric is a little fairer.”

Failure mode: endless “X ≠ Y” distinctions with no modeling/scientific consequence.

---

# F. Intermediate representation necessity

A classical pipeline explicitly represented a state that end-to-end LLM systems often collapse or ignore.

Possible states:
- study identity;
- evidence unit;
- dialogue state;
- schema;
- document relation;
- provenance;
- update/supersession state.

Question shape:

> **Is this intermediate representation still load-bearing, or can modern models infer around it?**

Current illustration: **L06**.

Strong experiment shape:
- hold raw content fixed;
- manipulate only the intermediate state;
- separate local extraction from downstream consequence.

Failure mode: collapsing to clustering F1 or a routine ablation.

---

# G. Data-first reverse search

Start from unusually strong natural data containing two independently meaningful variables.

Procedure:
1. verify data/gold first;
2. identify the real scientific quantities;
3. ask whether their relationship changes an NLP assumption or decision;
4. novelty-check that exact relation.

Attractive substrates:
- official structured data;
- longitudinal scholarly records;
- repeated human annotations;
- provider-defined states;
- revision histories;
- study/publication relations;
- real interaction outcomes;
- published experimental materials.

Failure mode: inventing a question merely because an annotation field exists.

---

# H. Real state transition / supersession

Documents are not always independent timeless objects. Later official state can change how an earlier artifact should be interpreted.

Examples:
- correction/supersession;
- version history;
- study vs publication identity;
- official status change;
- revised claim.

Question shape:

> **Does an LLM need explicit state-transition structure to recover the current valid object, or is flat context sufficient?**

Current illustration: **L07**.

Failure mode: data yield. Many apparent “corrections” are only metadata/typo changes, so proposition-level gold must be audited before compute.

---

# I. Systematic anomaly discovery inside a natural object

This is the acceptable way to discover our own anomaly.

Start with a broad natural object, then scan a principled behavior/intervention landscape.

A promising anomaly should be:
- large enough to matter;
- replicated;
- natural;
- stable across reasonable settings;
- interpretable;
- immediately suggestive of at least two mechanisms;
- testable by decisive intervention.

Reject:

> “We changed 50 prompts/settings and one number moved.”

Failure risks: multiple testing, benchmark artifacts, single-model accidents, post-hoc storytelling.

---

# J. Main/Award paper “large result, small explanation” mining

Do not read only abstracts.

Inspect:
- tables;
- ablations;
- error analyses;
- appendices;
- limitations;
- conclusions/future work.

Look for:

> **the parent paper owns the phenomenon; is a consequential explanation still open?**

Always check later follow-up work before claiming the gap.

---

# K. Strong but under-compressed recent areas

A non-hot area can be attractive when:
- the object is durable;
- literature is mature enough to define the problem;
- high-quality natural data exist;
- the exact modern scientific question remains open;
- the area is not dominated by benchmark/product races.

“Cold” is not valuable by itself. Obscurity is not novelty.

---

# L. Methods as discriminators, not generators

Useful discriminative operations include:
- teacher forcing vs free running;
- causal tracing / activation patching;
- steering;
- checkpoint trajectories;
- controlled post-training;
- representation similarity;
- random projection vs coordinate deletion;
- matched interventions;
- counterfactual manipulation;
- retrieval/evidence deletion;
- controlled restoration.

Correct order:

> **natural question/anomaly → competing explanations → operation that separates them**

Wrong order:

> “We have activation patching; what can we patch?”

---

# M. Lab-style seeds — inspiration only

Use lab work to calibrate **natural question shape**, not to copy topics or define the quality ceiling.

Useful shapes from current project notes:
- **Hamdi-style:** concrete model behavior → internal explanation → causal intervention → consequence.
- **Kisako-style:** information organization / representation / compression with a concrete behavior or capability implication.
- **Sato-style:** simple capability-acquisition question → controlled training/intervention → mechanism.
- **Yoda/Oshika-style:** real scientific/scholarly documents → structured evidence/extraction/relations → downstream scientific use.

This project has a strong negative prior against heavily linguistic branches even if they are legitimate lab topics.

**These are search seeds, not gates.**

---

# Anti-pattern library

Avoid repeatedly generating:
- a broader-sounding name for an unchanged local result;
- a generic causal effect presented as an explanation of how computation works;
- a list of known components presented as either automatic novelty or automatic collision;
- a paper plan whose strongest positive result would still not identify its interesting claim;
- another single-vs-multiple-valid-output story;
- another generic provenance story;
- another hierarchy-aware label task;
- another generic confidence/calibration study;
- another “does the model know X?” competence test;
- another benchmark pseudoreplication cell;
- another generic Agent/RAG/RL failure;
- another X ≠ Y distinction without consequence;
- another topic that exists only if one narrow effect wins.

Use **failed/KILLED_LEDGER.md** for exact dead parents.

---

# Extending this playbook

Add a generator only when it is broader than one candidate and useful for future search.

For each new generator, record:
- signal;
- question shape;
- why promising;
- common failure mode.

Do not create a new root file for it.

> **This playbook may grow and shrink. The search rules and selection gates should remain much more stable.**
