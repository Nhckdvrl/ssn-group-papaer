# 2026-09-13 — Pressure-First Search IX

This file closes the currently open pressure leads before the next conversation handoff. It does **not** promote a new candidate. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

Current portfolio remains:

- L32 — `PILOT-AUTHORIZED — E01 ONLY`
- L33 — `PILOT-AUTHORIZED — E01 ONLY`
- L17 — existing speech project, outside current new-search preference
- Mainline — **NONE**

The purpose of this closeout is to prevent attractive but under-identified semantic questions from being accidentally reported as new topics.

---

## Hook P36 — Neg-raising as one inference supported by two causal routes

**Status:** `PRESSURE ONLY — PRIORITY HANDOFF LEAD — NOT SELECTION / NO COMPUTE`

### Scientific pressure

Neg-raising is the familiar inference in examples such as:

> `I don't think p` → often understood roughly as `I think not-p`.

This remains a live linguistic object rather than a solved textbook curiosity. The literature contains genuinely different explanatory sources:

- classical syntactic NEG-raising / movement accounts, motivated in part by strict NPI and Horn-clause diagnostics;
- semantic/pragmatic accounts based on excluded-middle-style strengthening, exhaustification, discourse accessibility, and related mechanisms;
- hybrid views arguing that syntactic evidence and semantic/pragmatic inferences are both needed for different parts of the empirical pattern.

Recent work continues to redraw this boundary rather than closing it. Examples include:

- Gajewski, *Neg-raising, accessibility and propositional anaphora* (SALT 35): https://journals.linguisticsociety.org/proceedings/index.php/SALT/article/view/35.017
- Lu & Davidse (2026), *I don't think or I think … not – What is the difference?*: https://doi.org/10.1016/j.pragma.2026.04.008
- overview of syntactic vs semantic/pragmatic diagnostics: https://academic.oup.com/edited-volume/41364/chapter-abstract/352591529

### Why it is interesting for LLMs

The strongest possible LLM question is **not** `can an LLM do neg-raising?`.

A better scientific object is:

> **Does a decoder LM obtain the same lower-negation interpretation through two causally separable computations — one tied to grammatical/syntactic licensing and another tied to semantic-pragmatic strengthening — or does one learned route explain both classes of diagnostics?**

This would be attractive because the same surface inference may arise from different causal sources, and classic linguistic diagnostics already tell us where theories should diverge.

### Why it is NOT a candidate yet

Two requirements are unmet:

1. **Mother / first-stage gate is not established on a pre-specified open model.** We need robust behavior on at least two theoretically distinct diagnostic families, not merely ordinary `I don't think p` paraphrase judgments.
2. **No selective operation has been identified.** A valid E01 must suppress one proposed route while preserving the other. Generic activation patching, hidden-state steering, or deleting a negation-related direction would not identify the theory.

Without both, promoting this topic would repeat the old failure mode `beautiful theory → invent a patch → narrate result`.

### Handoff instruction

This is the **highest-priority unresolved semantic pressure** from the closeout, but it is not `SERIOUS`, not `PILOT-AUTHORIZED`, and authorizes zero GPU compute.

The next session may revisit it only by first finding:

- published/classic diagnostic families that make the competing accounts diverge;
- a cheap behavioral mother gate on one pre-specified base model;
- a genuinely selective same-checkpoint intervention.

Do not spend a long session merely collecting more neg-raising theory papers.

---

## Hook P37 — Gradable adjectives: where does the contextual standard enter computation?

**Status:** `PRESSURE ONLY — HANDOFF LEAD — NOT SELECTION / NO COMPUTE`

### Scientific pressure

Relative gradable adjectives such as `tall`, `warm`, and `expensive` do not have one fixed threshold. The same physical degree can count differently under different comparison classes (`tall for a child` vs `tall for a basketball player`). Formal/pragmatic work explicitly models the comparison class and contextual standard.

Useful background:

- Tessler-style comparison-class inference / computational pragmatics: https://pmc.ncbi.nlm.nih.gov/articles/PMC9286384/
- SCiL 2026 CrosSing already shows that modern LLM adjective-scale behavior changes under overinformative context: https://aclanthology.org/2026.scil-main.36/
- 2026 multilingual adjective-representation work already studies gradability geometrically, so simple probing is not novel: https://aclanthology.org/2026.brigap-1.3/

### Strongest possible question

> **When context changes what counts as `tall`, does the model causally recalibrate the adjective/degree representation itself, or keep a relatively stable degree representation and apply a context-dependent comparison standard only at the decision/composition stage?**

The contribution would need to identify the **locus of contextual standard-setting**, not merely show that context affects predictions.

### Why it is NOT a candidate yet

Current LLM behavioral work already establishes context sensitivity, so another benchmark/minimal-pair result is insufficient.

The mechanistic distinction is also easy to fake because late decoder positions naturally aggregate the prefix. A patch that finds `context matters later` could simply rediscover architecture position effects.

A viable E01 therefore needs theory-driven controls, for example a construction where the same adjective/degree dimension is present but the positive-form contextual standard should not be required in the same way (e.g. a carefully selected comparative/explicit-standard control). The intervention must make different predictions under `lexical/degree recalibration` and `late contextual standard` accounts.

### Handoff instruction

Keep as a **secondary unresolved pressure**, below Neg-raising. Do not promote unless a selective operation plus negative control is found first.

---

## Hook P38 — Prototype vs exemplar computation in in-context category learning

**Status:** `DROP FOR CURRENT SEARCH — REVIEWER-COMPRESSIBLE`

### Initial attraction

Classic cognitive category-learning paradigms provide diagnostic stimuli on which prototype and exemplar models make divergent predictions. The 5/5 task is especially attractive because it was designed to sharpen ambiguity in the classic 5/4 structure and can reveal shifts between exemplar and prototype strategies.

Human background:

- *Prototype or Exemplar Representations in the 5/5 Category Learning Task* (2024): https://pmc.ncbi.nlm.nih.gov/articles/PMC11200643/

### Why it is dropped

The LLM-side scientific ownership is already too compressed:

- current ICL theory frequently models prediction as similarity/kernel-weighted aggregation over demonstrations;
- recent mechanistic categorization work shows that demonstrations can remain heterogeneous, complementary local task states rather than collapsing into one global task vector;
- 2026 LLM work already explicitly frames category production through prototype theory and finds stable prototypical category structure: https://doi.org/10.1111/tgis.70242

This leaves a narrower question — whether a model that preserves individual demonstrations also computes an abstract prototype for final decisions — but the strongest paper identity is still reviewer-compressible as `classic cognitive categorization paradigm applied to ICL + existing local-vector/kernel accounts`.

The 5/5 diagnostic would be a useful experiment, not currently a Main-level scientific parent.

### Anti-resurrection

Do not make this a priority next session unless a new result creates a direct contradiction with existing kernel/local-demonstration accounts.

---

## Hook P39 — Scalar implicature: online alternative construction vs learned enriched mapping

**Status:** `DEPRIORITIZE / CLOSE CURRENT ROUTE — NO COMPUTE`

### Pressure

The attractive theoretical question was:

> **When `some` is interpreted as `not all`, does the model online construct and reject the stronger alternative `all`, or has the enriched mapping become a learned/default interpretation?**

### Why the current route closes

The neighboring LLM literature is now dense enough that `scalar interpretation + internal direction/steering` is not fresh:

- ACL SRW 2024 explicitly interprets BERT/GPT-2 behavior through default-vs-context-driven scalar-implicature accounts: https://aclanthology.org/2024.acl-srw.2/
- ACL 2026 Main, *Continuous Interpretive Steering for Scalar Diversity*, causally steers pragmatic interpretation in activation space across four LLMs: https://aclanthology.org/2026.acl-long.577/
- alternative uncertainty has already been computationally connected to scalar-diversity strength: https://aclanthology.org/2022.cmcl-1.8/

Most importantly, we still lack a selective operation that blocks **the computation of an alternative** without deleting the semantics of the alternative itself or directly changing the answer. `Erase/patch an all-like direction` does not identify online exhaustification.

### Anti-resurrection

Do not reopen generic `does the model represent all when seeing some`, `steer pragmatic vs literal reading`, or `context makes scalar implicature stronger`.

A future return requires a qualitatively new identifying instrument.

---

## Hook P40 — Free-choice / focus particles (`only`, `even`) as alternative-based computation

**Status:** `DROP AS NEXT-SESSION PRIORITY — OWNER-ADJACENT + IDENTIFICATION WEAK`

### Why not continue now

These are genuine formal-semantic objects involving alternatives, exhaustivity, or modal enrichment. However:

- the same selective-alternative-computation problem that blocks scalar implicature remains;
- a new August-2026 preprint already directly studies whether humans and LLMs construct stable scalar representations for focus particles `even` and `only`: https://arxiv.org/abs/2608.08227
- 2025 work on `just` already probes fine-grained discourse-particle senses including exclusive uses related to `only`: https://arxiv.org/abs/2506.04534

Therefore `only/even representation + probe/patch` is already too close to an active line, while free-choice lacks a clean pre-specified mother and selective intervention in our current search.

### Anti-resurrection

Do not spend the next conversation doing generic focus-particle / free-choice competence or alternative probes.

---

# Closeout verdict

No new topic is promoted by this closeout.

**New survivor: 0.**

The only unresolved leads worth carrying to the next conversation are:

1. **Neg-raising dual-route computation** — higher priority, but `PRESSURE ONLY / NO COMPUTE`.
2. **Gradable-adjective contextual-standard locus** — secondary pressure, `NO COMPUTE`.

Everything else in this file should be treated as closed/deprioritized unless genuinely new evidence changes the ownership or identification picture.

The next session should **not** begin by developing these two leads. It should resume broad pressure-first search across independent scientific objects, using them only as optional leads alongside new pools.
