# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Current phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K183**; newer compact rejections are also recorded under `search_rounds/`.

## Current search preference

- No new speech/audio topics.
- Avoid pure-linguistics competence tests.
- Strong preference for the intellectual shape of *The Imperfective Paradox in Large Language Models*: **clean classical problem → modern LLM/agent consequence → larger scientific claim**.
- Do not require a candidate to inherit one paper's unexplained phenomenon. Combining several reliable literatures into a new scientific pressure is encouraged.
- A classical distinction is useful only if it changes a modern operation, inference, representation, evaluation, or system consequence; “does the LLM know the distinction?” is usually not enough.

---

## Active pilot-authorized portfolio

### L16 — Same World, Different Partitions

**Status:** **PILOT-AUTHORIZED — bounded E01/E02 only**  
Package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

RQ:

> Holding atomic hypotheses, evidence, target proposition and reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull elicited credence toward a partition-specific ignorance prior?

Identity fence: not generic prompt sensitivity / calibration. If the directional partition law is absent, kill rather than rescue through a weaker invariance story.

### L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** **PILOT-AUTHORIZED — E01 only; EXISTING PROJECT, OUTSIDE NEW-SEARCH PREFERENCE**  
Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

RQ:

> After a few transcribed examples from one speaker, what generalizes to new utterances: speaker-global state, sublexical acoustic–phonetic mapping, or mainly lexical/textual context?

The user's current topic-search preference excludes new speech/audio leads. Do not scientifically kill L17 merely because the search preference changed; its existing authorization remains bounded by its own evidence.

### L22 — Bad Dimensions or Bad Directions?

**Status:** **PILOT-AUTHORIZED — E01 symmetry audit only**  
Package: `candidates/L22_EMBEDDING_BASIS_IDENTIFIABILITY/`

RQ:

> When modern NLP work says some text-embedding dimensions are harmful or query-specifically important, are those claims properties of the learned representation itself, or artifacts of the coordinate basis used to write an equivalent embedding geometry?

E01 is cheap and deterministic: reproduce modern dimension-deletion / DIME-style effects, apply preregistered Haar-random orthogonal rotations that leave full-dimensional cosine/dot-product retrieval exactly unchanged, then rerun coordinate-level claims. Keep only if a substantive modern conclusion changes or the native basis unexpectedly stands out against random rotations.

Identity fence: not generic old basis dependence, not L08 continued under a new name, not a new compression method. Novelty lives in **current NLP conclusion identifiability under function-preserving symmetry**.

---

## Serious pre-pilot leads — no compute

### L21 — When Is Contextual Entrainment Rational?

**Status:** **SERIOUS / PRE-PILOT — IDENTIFICATION BLOCKER — NO COMPUTE AUTHORIZED**  
Package: `candidates/L21_ENTRAINMENT_CACHE_PRIOR/`

RQ:

> Is contextual entrainment a learned online-cache prior calibrated to real lexical self-recurrence, or an overgeneralized / distribution-insensitive copying bias?

Fresh audit revoked the previous E01 authorization. Natural self-recurrence mixes topic, coreference, syntax and other legitimate recurrence sources, while the salient entrainment phenomenon occurs even for irrelevant/random tokens. The project must first identify a comparator that matches the intervention DGP. Findings ACL 2023 repetition-learning-bias work also narrows the remaining novelty.

Do not run E01 until the identification blocker is closed.

### L23 — Similarity Is Not Provenance

**Status:** **SERIOUS / PRE-PILOT — NO COMPUTE AUTHORIZED**  
Package: `candidates/L23_SIMILARITY_NOT_PROVENANCE/`

RQ:

> When an LLM-generated scientific idea strongly overlaps with an existing paper, can that observable similarity identify source-specific copying, or can the same level of overlap arise through independent reconstruction from shared antecedent literature?

This lead deliberately combines multiple literatures: generated-idea overlap/plagiarism, future/held-out idea reconstruction, and causal provenance. Before compute, audit direct recent owners, full training/post-training cutoffs, and whether a cutoff-safe open model yields enough high-overlap reconstructions for a matched comparison.

### L24 — Same Entity ≠ Same Epistemic File

**Status:** **SERIOUS / PRE-PILOT — DATA-SCALE + DIRECT-COLLISION AUDIT — NO COMPUTE AUTHORIZED**  
Package: `candidates/L24_EPISTEMIC_FILES_VS_CANONICAL_ENTITIES/`

RQ:

> If two names/descriptions denote the same real-world entity, is it always safe for an LLM agent's long-term memory to canonicalize them into one entity node, or can that merge destroy the perspective / mode-of-presentation information required for correct belief reasoning?

Intended identity: not another referential-opacity or ToM competence test. The modern operation is **entity canonicalization itself**. The decisive target is an extensional/intensional crossover: global merge helps ordinary identity/fact retrieval but selectively damages perspective-sensitive belief reasoning, while a two-level world-entity + epistemic-file representation preserves both.

Before compute: refresh direct-owner search; verify usable identity-false-belief gold; establish a path from the small first kill test to a credible paper-scale natural substrate; rule out token/retrieval confounds.

---

## Most recent search decisions

Full recent records include:
- `search_rounds/2026-09-12_POST_L18_ANTI_RESURRECTION.md`
- `search_rounds/2026-09-12_CONTINUED_SEARCH.md`
- `search_rounds/2026-09-12_CONTINUED_SEARCH_II.md`
- `search_rounds/2026-09-12_CLASSIC_PROBLEM_TO_MODERN_LLM_SEARCH.md`

The newest pass searched classical-problem→modern-LLM bridges across source monitoring, frame problem, belief revision, partial observability, analogy, reconsolidation, common knowledge, object permanence, deontic authorization, IIA, duplicate-memory semantics, experience abstraction, and de-se/self-location. Most were killed because recent work already owns the modern parent or because the remaining formulation collapses to a competence benchmark. **L24** was the only new promotion from that pass; de-se/self-location remains only a search seed/HOLD.

Do not reopen dead parents by changing model, benchmark, terminology, or adding mechanism.

---

## Governing rule

Before generating or deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / historical repo → duplicate means discard first.**

For every survivor, perform the successful-result test and pre-register natural claim mutations before compute.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
