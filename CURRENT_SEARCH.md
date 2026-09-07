# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 2 — L02, L03  
**Authoritative killed ledger:** through **K157**  
**Next kill ID:** **K158**

> `good/` currently contains **L02** and **L03**.
> Both are **PILOT-AUTHORIZED / NOT MAINLINE APPROVED**.
> Former L04 was demoted after stricter re-audit because GOOD DATA was only conditionally established.

---

# Critical rule correction — classic problems are allowed and actively preferred

A pre-LLM classic NLP problem is **not** a novelty failure merely because it was studied in 1991, 2001, or 2011.

The preferred Old Problem / New Method shape is now:

> **A durable classical language/NLP object + an LLM-era capability that makes a previously inaccessible scientific quantity, output, intervention, or measurement possible.**

A classic topic dies only when:

1. 2024–2026 or earlier modern neural/LLM work already owns the **same modernized parent question**;
2. the LLM merely replaces a classifier/parser without changing what can be scientifically asked;
3. data/gold do not identify the new quantity;
4. the new method cannot change interpretation, modeling, or evaluation.

Positive paper-identity reference:

- modern GEC closest-gold evaluation uses LLM generation to create valid system-conditioned references and can reverse conclusions produced by fixed-reference evaluation;
- this is stronger than “rerun GEC with GPT” because the LLM enables a new measurement operation.

Therefore reviewer compression must distinguish:

> **“This is a classic problem.”** — NOT fatal.

from:

> **“This is the already-published LLM-era modernization of that classic problem.”** — fatal.

---

# Latest classic-problem / new-method audit

| ID | lead | verdict | decisive issue |
|---|---|---|---|
| K151 | LexSub generation distribution vs human choice distribution | KILL CURRENT FORM | classic counts/graded acceptability do not identify one-shot human production probabilities |
| K152 | Logical metonymy as open covert-event recovery | KILL | AACL 2020 + GPT-3 already own covert-event recovery/context-vs-default modernization |
| K153 | PP attachment as open meaning reconstruction | KILL | 2025 LLM PP/syntactic ambiguity parent already occupied |
| K154 | Ellipsis as open meaning recovery | KILL | ACL 2023+ already modernizes ellipsis into LLM reasoning/open recovery |
| K155 | Prosody beyond transcript | KILL CURRENT FORM | ACL 2026 StressTest owns the broad SpeechLM meaning-from-prosody parent |
| K156 | Plan recognition without plan library | KILL CURRENT FORM | natural dialogue lacks independent hierarchical-plan gold; synthetic plan corpus violates data-first preference |

---

# Current live search principle

Do not primarily enumerate annotation labels.

Search for classical tasks where older methods were constrained to:

- closed candidate inventories;
- discrete labels;
- fixed references;
- hand-built symbolic resources;
- local/pipeline decisions;
- surface overlap metrics;

and where LLMs now make it possible to observe:

- open-ended natural-language interpretations;
- multiple valid outputs;
- system-conditioned valid references;
- counterfactual interventions;
- latent hypotheses grounded against external traces;
- decomposed scientific quantities that can reverse an established conclusion.

For every lead, require before promotion:

1. a simple natural example;
2. a precise statement of what **LLMs newly make possible**;
3. exact natural data and independent gold for that newly observable quantity;
4. a fresh search for the **modernized parent**, not merely the classical parent;
5. an outcome map where either answer changes scientific understanding.

---

# Newly promoted candidate — L03

## Table Value ≠ Observation Status

**Status: PILOT-AUTHORIZED / NOT MAINLINE APPROVED.**

Core RQ:

> In real statistical tables, can modern generative systems recover the typed observation represented by a cell—including provider-defined non-value states—rather than collapsing every cell into a scalar/string answer or generic missingness?

Why it survived the re-audit:
- U.S. Census ACS provides official paired estimate/annotation variables and provider-defined semantics;
- the gold is machine-readable and independent of evaluated models;
- recent TableQA work on missing values, table annotation, and data-referencing errors does not directly own the parent that a non-value state is itself the semantic denotation/output unit;
- the decisive pilot can test direct generation vs typed status→value factorization and whether value-centric evaluation changes model ranking/conclusions.

Critical caveat:
- it only remains Main-level if the pilot goes beyond symbol memorization and demonstrates cross-source documentation-conditioned semantics and/or a ranking/task-definition consequence.

---

# A-level live lead — former L04, DEMOTED

## Morphological Inflection Is Not a Total Single-Valued Function

**Status: A-LEVEL LIVE / NOT PILOT-AUTHORIZED / NOT in `good/`.**

Plain RQ:

> Should morphological generation be treated as a partial, sometimes set-valued relation—NO_FORM / ONE_FORM / MULTIPLE_FORMS—rather than assuming every lemma+feature bundle has exactly one target form?

Why it remains interesting:
- defectivity and overabundance are real pre-LLM objects;
- TACL explicitly notes that overabundance was reduced to one canonical form per cell and that sets of forms would be empirically richer;
- fresh 2024–2026 search did not find a direct LLM paper owning the exact joint partial/set-valued task-definition rewrite.

Why it was demoted:
- the prior file said GOOD DATA = “YES, conditional on exact extractable resource audit”; under project rules, conditional YES is not YES;
- Surrey defectivity resources establish the object, but exact pilot-scale mapping from lexeme+feature bundle to independently licensed NO_FORM still needs extraction verification;
- the overabundance side was even less concrete: published descriptions exist, but exact machine-extractable gold had not been secured;
- ACL 2020 unsupervised paradigm completion already includes complete-paradigm generation and paradigm-size discovery, so the claim that LLMs uniquely make paradigm availability testable must be phrased much more carefully.

Promotion condition:
1. verify an exact extractable defectivity dataset with lexeme + feature-cell + absence gold;
2. verify an exact extractable overabundance dataset with lexeme + feature-cell + complete licensed-form set;
3. show that this is not merely an LLM morphology competence benchmark and not subsumed by full-paradigm completion;
4. preserve a decisive C1→C2→C3 consequence.

Until all four are satisfied, do not return L04 to `good/`.

---

# Search target

Find **classic problem + genuinely new LLM method/scientific access**, not “old phenomenon on new model.”

**Current scoreboard: 2 / 5.**


---

# K157 final audit — MapTask collaborative plan

The strongest recent A-level lead has been **killed after full modern-parent audit**.

Former formulation:

> **Instruction Following ≠ Collaborative Plan Understanding**  
> / **Giver Intended Route ≠ Follower Realized Route**

Why it was genuinely promising:
- classic HCRC Map Task is natural human-human dialogue;
- 128 spontaneous dialogues with deliberately asymmetric maps;
- giver has an external reference route;
- follower has actual drawing/completed-route state;
- path-deviation outcome is externally measured;
- transaction coding links subdialogues to route segments and follower draw/cross-out actions;
- ACL 2010 explicitly discarded follower utterances and map asymmetry for tractability, making this a legitimate Classic Problem / New Method revisit.

Why it ultimately died:
- **Seeing Is Not Sharing (SIGDIAL 2026)** already uses the same 128 HCRC dialogues to show VLMs conflate potentially shared map information with interactionally established common ground.
- **Humans' ALMANAC (2026)** reimplements Map Task with human draw/erase/undo/reset trajectories plus self-reasoning, partner-intent and team-goal annotations, and benchmarks LLM next-action/mental-model prediction.
- **CollabSim (2026)** directly uses Map Task to study LLM collaborative competence beyond task completion, manipulating communication bandwidth and follower-canvas visibility and evaluating route outcome, communication/revision process, and shared-task/partner-state probes.

Therefore:
> **intended route vs realized route is a clean global instantiation of an already-modernized participant-specific collaborative-state parent.**

Reviewer compression:
> “Seeing Is Not Sharing / ALMANAC / CollabSim, but at whole-route granularity.”

**Verdict: K157 — CROWDED_PARENT + NOVELTY_PARENT_COLLISION.**

---

# Search rule after K157

Maintain the corrected classic-problem rule:

> **Old classic work is allowed.**

Do not kill because a problem appeared in 1991/2001.

But for every classic problem, explicitly search whether 2024–2026 work has already performed the relevant modernization.

The strongest target shape remains:

> **A classic NLP problem had to discard, discretize, or proxy a natural quantity because older methods could not represent/measure it. LLMs now remove that technical restriction. Does restoring that quantity change the scientific conclusion?**

Prefer classic tasks where:
- the discarded quantity has **existing independent natural gold**;
- the LLM-era operation is genuinely new (open output, intervention, dynamic valid gold, latent reconstruction);
- no 2024–2026 paper already owns that modernization;
- either outcome yields a C1→C2→C3 paper.

Avoid immediately:
- MapTask/common-ground/shared-plan modernization;
- modern LexSub generation;
- logical metonymy covert-event recovery;
- PP ambiguity with LLMs;
- ellipsis open recovery;
- generic prosody-to-meaning SpeechLM tests.

**Current good count is 2 — L02 + L03. Former L04 is A-level live but demoted. No approved mainline. Next kill: K158.**
