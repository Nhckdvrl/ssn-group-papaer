# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K183**; newer compact rejections live in `search_rounds/` until a later ledger sync.

## Current search preference

- No new speech/audio topics.
- Avoid pure-linguistics competence tests.
- **Strongly avoid very hot directions as the default search space**, especially generic Agent / long-term memory / RAG / RL / judge work.
- Prefer scientific questions that would remain important if the fashionable system label disappeared.
- Prefer the intellectual shape of ACL 2026 Best Paper *The Imperfective Paradox in Large Language Models*: **clean older scientific problem → new modern leverage/consequence → larger scientific claim**, without copying its subject.
- Study strong papers' **topic provenance**: what old problem, anomaly, hidden assumption, measurement bottleneck, identification problem, or real workflow caused the paper to exist before it had a method/title.
- A candidate may combine several reliable literatures; it need not depend on one paper's anomaly.
- Classical distinctions count only when they naturally create a modern scientific question; “does the LLM know the distinction?” is normally too weak.
- **Natural means the scientific object/question already exists independently of our intervention or schema.** A topic is bad if the question becomes interesting only after we invent a special benchmark, join several awkward datasets, or define a bespoke pipeline failure.
- **Do not salvage a topic merely because natural witnesses or executable examples can be found.** If the question itself is low-priority, overly constructed, data-engineering-heavy, or reviewer-compresses to an implementation fix, kill it and resume broad search.
- Prefer easy/native gold and direct data access. Data archaeology, multi-source linkage, heavy expert reconstruction, or bespoke annotation is a strong negative prior unless the scientific question is exceptional.
- No survivor quota. Kill aggressively rather than fill slots.

---

## Pilot-authorized

### L16 — Same World, Different Partitions
**Status:** `PILOT-AUTHORIZED — bounded E01/E02 only`  
Package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

> Holding atomic hypotheses, evidence, target proposition and reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull elicited credence toward a partition-specific ignorance prior?

If the directional law is absent, kill rather than rescue with generic prompt sensitivity.

### L17 — What Does a Speech LLM Learn About a Speaker?
**Status:** `PILOT-AUTHORIZED — E01 only; existing project, outside current new-search preference`  
Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

Do not create new speech/audio candidates.

### L22 — Bad Dimensions or Bad Directions?
**Status:** `PILOT-AUTHORIZED — E01 symmetry audit only`  
Package: `candidates/L22_EMBEDDING_BASIS_IDENTIFIABILITY/`

> Are claims that particular embedding dimensions are harmful/query-important properties of the representation, or artifacts of the coordinate basis used to write an equivalent geometry?

---

## Serious pre-pilot

### L21 — When Is Contextual Entrainment Rational?
**Status:** `SERIOUS — IDENTIFICATION BLOCKER — NO COMPUTE`  
Package: `candidates/L21_ENTRAINMENT_CACHE_PRIOR/`

### L23 — Similarity Is Not Provenance
**Status:** `SERIOUS / PRE-PILOT — NO COMPUTE`  
Package: `candidates/L23_SIMILARITY_NOT_PROVENANCE/`

### L26 — Same PICO ≠ Same Causal Question
**Status:** `SERIOUS SEED — DATA / DIRECT-OWNER AUDIT — NO COMPUTE`  
Package: `candidates/L26_ESTIMAND_ALIGNMENT/`

---

## Hold / deprioritized

### L24 — Same Entity ≠ Same Epistemic File
**Status:** `HOLD / DEPRIORITIZED — HOT-DIRECTION + HARNESS + DATA-GOLD RISK — NO COMPUTE`  
Package: `candidates/L24_EPISTEMIC_FILES_VS_CANONICAL_ENTITIES/`

---

## Recent rejections

### L27 — Sample / Effect Count ≠ Independent Evidence Units
**Status:** `NO-GO / ARCHIVED`

Killed despite natural shared-control examples. The question is too shaped by a particular extraction representation, requires cumbersome article↔registry/design reconstruction, and reviewer-compresses to the standard statistical fact that automatic meta-analysis needs dependence/design metadata. **Do not continue prevalence audits or rescue with more design families.**

Record: `candidates/L27_EFFECT_DEPENDENCE_STRUCTURE/README.md`.

### Regression Row ≠ Scientific Effect Claim
**Status:** `NO-GO / DO NOT PROMOTE`

The classical Table-2-fallacy issue is real, but mature extraction systems already preserve exposure/covariate/adjustment roles. A new paper would depend on selecting a bad pipeline or adding another schema field rather than exposing a new scientific question.

### L28 — Canonical Species ID ≠ Source Taxonomic Concept
**Status:** `NO-GO / DIRECT DOMAIN-PARENT COLLISION`

Concept-aware mapping/alignment is already directly owned in biodiversity informatics; adding LLM IE would mainly repeat a known representation error.

### L25 — Evidence Exists Somewhere ≠ One Source Establishes It
**Status:** `NO-GO / ARCHIVED`

The source-composition question was reverse-engineered around the intervention rather than independently motivated.

---

## Governing rule

Before deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / historical repo → duplicate means discard first.**

Before spending data/compute effort, additionally ask:

> **Would we still care about this question if the first pilot were never run? Is the question itself compelling enough that a reviewer immediately understands why it matters? Is the natural data path easy enough that the project is not mostly archaeology?**

If not, **kill and search anew; do not rescue.**

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
