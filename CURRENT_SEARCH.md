# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Current phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K183**; newer search-round rejections are also recorded under `search_rounds/`.

---

## Active pilot-authorized portfolio

### L16 — Same World, Different Partitions

**Status:** **PILOT-AUTHORIZED — bounded E01/E02 only**  
Package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

RQ:

> Holding atomic hypotheses, evidence, target proposition and reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull elicited credence toward a partition-specific ignorance prior?

Identity fence: not generic prompt sensitivity / calibration. If the directional partition law is absent, kill rather than rescue through a weaker invariance story.

### L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** **PILOT-AUTHORIZED — E01 only**  
Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

RQ:

> After a few transcribed examples from one speaker, what generalizes to new utterances: speaker-global state, sublexical acoustic–phonetic mapping, or mainly lexical/textual context?

E01 uses matched transcripts, same-speaker vs other-speaker audio, text-only controls, and target-relevant phonetic coverage. If the established ICL benefit disappears under the matched design, archive rather than rescue.

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

---

## Most recent search decisions

Full records: `search_rounds/2026-09-12_POST_L18_ANTI_RESURRECTION.md` and `search_rounds/2026-09-12_CONTINUED_SEARCH.md`.

Recent deaths include:
- **L18 contextual entrainment × word-meaning priming causal identity** — only a narrow overlap/mediation story remains.
- **L20 rewarded-trajectory update unit** — narrow novelty, outcome fragility, expensive causal replay.
- **Temporal forgetting → latent survival via relearning** — owned forgetting parent + familiar persistence diagnostic.
- **Own-answer persistence vs generic anchoring** — direct self-attribution interventions already own the decisive comparison.
- **Query-conditioned compression as reusable future-query memory** — directly occupied by future-query reuse work.
- **Feedback specificity / partial feedback / answer leakage** — refinement literature already owns the key cells.
- **Long-context distance vs similarity interference** — proactive/retroactive interference is a direct modern parent.
- **Multimodal language-gating / text dominance** — direct cross-modality text-dominance work already exists.

Do not reopen dead parents by changing model, benchmark, terminology, or adding mechanism.

---

## Governing rule

Before generating or deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / historical repo → duplicate means discard first.**

For every survivor, perform the successful-result test and pre-register natural claim mutations before compute.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
