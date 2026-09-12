# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K183**; newer compact rejections live in `search_rounds/` until a later ledger sync.

## Current search preference

- No new speech/audio topics.
- Avoid pure-linguistics competence tests.
- **Strongly avoid very hot directions as the default search space**, especially generic Agent / long-term memory / RAG / RL / judge work. Fashion density is a real negative prior because ownership is crowded and paper identity often collapses into a harness/framework choice.
- Prefer scientific questions that would remain important if the fashionable system label disappeared. Harness-dependent questions need unusually strong framework-independent inference and natural gold.
- Prefer the intellectual shape of ACL 2026 Best Paper *The Imperfective Paradox in Large Language Models*: **clean older scientific problem → new modern leverage/consequence → larger scientific claim**, but do not restrict search to semantics or copy that paper's subject.
- When calibrating against Best / Outstanding / strong Main papers, explicitly study **topic provenance**: what older problem, anomaly, hidden assumption, measurement bottleneck, identification problem, weakly evidenced claim, or real workflow caused the paper to exist; why it became answerable now; and how the first decisive result grew into the final paper.
- Transfer the **origin mechanism** of excellent papers into quieter domains rather than extending their fashionable topic directly.
- A candidate may combine several reliable literatures; it need not depend on one paper's unexplained anomaly.
- Classical distinctions only count when they change a modern operation, representation, inference, evaluation, or scientific consequence. “Does the LLM know the distinction?” is normally too weak.
- **Natural means scientifically natural, not everyday or layperson-simple.** A technical/domain-specific question is fine if the object and uncertainty pre-exist our benchmark/intervention and are recognized by the field. The warning sign is not “needs expertise”; it is “the question only exists because we invented the manipulation.”
- A plain example is optional communication support, never a selection gate.
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

Do not create new speech/audio candidates. Do not kill this already-authorized project merely because search preference changed; its fate is determined by its own E01 evidence.

### L22 — Bad Dimensions or Bad Directions?
**Status:** `PILOT-AUTHORIZED — E01 symmetry audit only`  
Package: `candidates/L22_EMBEDDING_BASIS_IDENTIFIABILITY/`

> Are claims that particular embedding dimensions are harmful/query-important properties of the representation, or artifacts of the coordinate basis used to write an equivalent geometry?

Identity = **current NLP conclusion identifiability under function-preserving symmetry**, not generic basis dependence or a new compression method.

---

## Serious pre-pilot

### L21 — When Is Contextual Entrainment Rational?
**Status:** `SERIOUS — IDENTIFICATION BLOCKER — NO COMPUTE`  
Package: `candidates/L21_ENTRAINMENT_CACHE_PRIOR/`

> Is contextual entrainment a learned online-cache prior calibrated to real lexical self-recurrence, or an overgeneralized / distribution-insensitive copying bias?

Natural recurrence mixes topic/coreference/syntax with the target phenomenon. No compute until an identified comparator exists.

### L23 — Similarity Is Not Provenance
**Status:** `SERIOUS / PRE-PILOT — NO COMPUTE`  
Package: `candidates/L23_SIMILARITY_NOT_PROVENANCE/`

> When an LLM-generated scientific idea strongly overlaps with an existing paper, can that observable similarity identify source-specific copying, or can the same overlap arise through independent reconstruction from shared antecedent literature?

Combines generated-idea overlap/plagiarism, future/held-out idea reconstruction, and causal provenance. Audit direct recent owners, full model cutoffs, and overlap yield before compute.

### L26 — Same PICO ≠ Same Causal Question
**Status:** `SERIOUS SEED — DATA / DIRECT-OWNER AUDIT — NO COMPUTE`  
Package: `candidates/L26_ESTIMAND_ALIGNMENT/`

> When automated evidence synthesis treats trials as answering the same PICO question, does it preserve whether they actually target the same treatment effect / estimand, or can it pool semantically similar studies that answer different causal questions?

Strong external scientific pressure exists from the estimand/evidence-synthesis literature. Do not reduce this to an estimand-label competence test. No compute until paper-scale natural/expert gold and a downstream compatibility/synthesis consequence are secured.

### L27 — Sample / Effect Count ≠ Independent Evidence Units
**Status:** `SERIOUS / PRE-PILOT — E00 DATA-ONLY AUTHORIZED — NO MODEL COMPUTE`  
Package: `candidates/L27_EFFECT_DEPENDENCE_STRUCTURE/`

> When automated scientific extraction converts papers into flat finding/effect records, does that representation preserve the independent experimental units and dependence structure required for valid evidence synthesis, or can every extracted number be correct while the evidence object is still scientifically insufficient?

Direct-owner search has not found a modern NLP paper owning experimental-unit/dependence-graph extraction as the central object. Public RCT extraction corpora plus ClinicalTrials.gov/AACT relational group/design structure provide a plausible external data-only identifiability audit. E00 may join public article records to registry structure and estimate whether flat finding schemas collapse scientifically different evidence states. No LLM/model compute is authorized before E00 survives.

---

## Hold / deprioritized

### L24 — Same Entity ≠ Same Epistemic File
**Status:** `HOLD / DEPRIORITIZED — HOT-DIRECTION + HARNESS + DATA-GOLD RISK — NO COMPUTE`  
Package: `candidates/L24_EPISTEMIC_FILES_VS_CANONICAL_ENTITIES/`

The classical identity/perspective tension is clean, but the current paper identity lands in saturated Agent / long-term-memory work, depends on a memory/entity-resolution harness, and lacks easy paper-scale natural identity×perspective gold. Do not spend current search or compute budget here. Reopen only if it can become substantially framework-independent with strong natural data.

### Regression Row ≠ Scientific Effect Claim
**Status:** `UNRESOLVED SEARCH LEAD — GOLD AUDIT FIRST — NO CANDIDATE ID YET`

> When scientific IE reads a multivariable regression table, can it distinguish the target exposure/effect the study was designed to estimate from adjustment-variable coefficients that appear in the same table but do not license the same scientific claim?

Classical Table-2-fallacy pressure is strong and 2026 LLM pipelines already extract exposure/outcome/covariate inventories for observational evidence synthesis. However, available public audits appear mostly article-level rather than row-level target-estimand gold. Do not promote until a natural row/model-level gold path and direct-owner audit survive.

---

## Recent rejections

### L28 — Canonical Species ID ≠ Source Taxonomic Concept
**Status:** `NO-GO / KILL CURRENT FORM — DIRECT DOMAIN-PARENT COLLISION`  
Record: `candidates/L28_TAXON_CONCEPT_IDENTITY/README.md`

The classical problem and gold were strong, but the intended modern bridge is already owned in biodiversity informatics: 2024 taxonomic-concept mapping work explicitly says information aggregators must compare/map concepts rather than only names, and 2026 work provides scalable concept-aware biological-taxonomy alignment for information reconciliation. Adding an LLM entity linker would mainly show a new extractor repeating an already-recognized representation error.

### L25 — Evidence Exists Somewhere ≠ One Source Establishes It
**Status:** `NO-GO / ARCHIVED`

The patent source-composition route is archived because the proposed general object was reverse-engineered around a specialized doctrinal distinction and matched source-partition intervention rather than an independently established NLP uncertainty with paper-scale consequence.

Record: `candidates/L25_SOURCE_BOUNDED_EVIDENCE/README.md`.

Recent provenance-calibrated search records:
- `search_rounds/2026-09-12_SOURCE_BOUNDED_EVIDENCE_SEARCH.md`
- `search_rounds/2026-09-12_AWARD_TOPIC_PROVENANCE_SEARCH.md`
- `search_rounds/2026-09-12_ESTIMAND_AND_SYNTHESIS_STRUCTURE_SEARCH.md`
- `search_rounds/2026-09-12_INDEPENDENT_EVIDENCE_UNIT_SEARCH.md`

---

## Governing rule

Before deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → search killed ledger / archived candidates / historical repo → duplicate means discard first.**

For every survivor: successful-result test before compute; if RQ/estimand/mechanism/central claim/paper identity changes, selection authorization resets.

For strong-paper calibration, additionally ask:

> **What caused this paper to exist before it had a method or title?**

Transfer that origin mechanism to quieter scientific objects; do not simply chase the same hot area.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
