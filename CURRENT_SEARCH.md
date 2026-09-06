# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Current target:** find additional five-gate candidates without lowering the bar.

> Latest terminal audit:
>
> - K076 — answer correctness vs completeness: **KILL**
> - K077 — event mention vs instance cardinality: **KILL**
> - K078 — reported proposition vs speaker commitment: **KILL**
> - K079 — lexical trigger vs semantic event: **KILL**
> - K080 — textually expressed relation vs contextually inferable relation: **KILL**
> - **A-level live leads: 0**
> - **B-level / A-borderline live leads: 1**

---

# B-level / A-borderline live lead

## Entity Mention ≠ Discourse Entity
### Working stronger formulation: Semantic Salience ≠ Entity Reification

**Plain-language object**

- “John is a doctor.” — `a doctor` can function as a predicative description of John rather than introducing a second independently trackable doctor.
- “Dogs are mammals.” — a generic/kind-level nominal is not the same object as a specific individual discourse referent.

**Why the object is real**

Classical resources explicitly preserve distinctions that broad “entity/mention” outputs can collapse:

- ACE entity classes include Specific, Generic, Attributive, and Underspecified.
- ARRAU distinguishes referring expressions that update/refer to a discourse model from non-referring expressions such as predicatives and quantificational expressions; it also annotates genericity.
- GUM tracks discourse referents, information status, typed predication links, singletons, and generic/common-ground cases.

**Modern modeling tension**

Free-form entity/KG extraction often emits a list of salient entities/nodes directly. The candidate asks whether treating all salient nominal concepts as the same output unit is a harmless modern abstraction or whether it creates systematic reification errors.

### Account A — Unified typed semantic-node view

Specific individuals, generic kinds, and predicative concepts may all legitimately be graph nodes if node types and relations are explicit. Classical “only referring mentions become entities” factorization may therefore be unnecessary for modern semantic graphs.

### Account B — Referentially typed output remains load-bearing

Collapsing semantic salience into one untyped `ENTITY` unit may create spurious independent nodes, false identity/coreference, false edges, and distorted graph topology. A typed output separating individual referents, kinds/concepts, and predicative/non-referring expressions may be necessary.

**Current strongest data candidates**

- ARRAU 3.0 / freely distributable ARRAU subsets: referring vs non-referring, predicative, quantificational, genericity.
- ACE: Specific / Generic / Attributive / Underspecified entity classes.
- GUM: open, rich discourse-referent + information-status + typed predication annotations.

**Current assassination evidence / danger**

1. Porada et al., Findings ACL 2024, *Challenges to Evaluating the Generalization of Coreference Resolution Models: A Measurement Modeling Perspective*, already shows that generic and predicative expressions change the construct measured by coreference datasets.
   - https://aclanthology.org/2024.findings-acl.909/
2. Domingo et al., CRAC 2025, *Mention detection with LLMs in pair-programming dialogue*, explicitly includes predication and generic mentions in an LLM mention-detection setting.
   - https://aclanthology.org/2025.crac-1.4/
3. Modern KG work makes class/instance and node-design choices explicit; e.g. OntoGen (2026) separates classes from instances, and OntoKG (2026) frames KG construction as deciding which entities become nodes and which properties become edges.
   - https://doi.org/10.1039/D5DD00275C
   - https://arxiv.org/abs/2604.02618

**Main unresolved problem**

ARRAU/ACE referentiality labels are **not automatically gold for whether a KG should contain a node**. A KG can legitimately represent a generic kind or concept as a typed node. Therefore the candidate cannot define “non-referring = false node” without a construct mismatch.

To survive, it needs an **independent graph-level consequence** showing when unified node creation changes identity, relation truth, query answers, or graph topology relative to a representation with typed semantic status.

**Reviewer compression to defeat**

> “This is just referentiality / genericity / mention detection on LLMs, or ordinary ontology class-vs-instance design.”

**Current five-gate status**

| Gate | Verdict | Current reason |
|---|---|---|
| REAL OBJECT | **YES** | Referential vs non-referential/generic/predicative status is a natural pre-LLM object. |
| NEW AXIS | **BORDERLINE** | Modern node reification is a plausible changed assumption, but must be separated from old mention/coreference classification. |
| GOOD DATA | **BORDERLINE** | Excellent referentiality annotations exist, but they do not yet provide independent gold for “should this be a graph node?” |
| NEW PARENT | **BORDERLINE** | No exact direct collision found yet, but coreference construct-validity and KG class/instance/node-design work press hard on the parent. |
| DECISIVE PAPER | **NO YET** | Outcome A is not falsifiable without a graph-level downstream estimand; current formulation risks a normative representation preference. |

**Current status:** **KEEP SEARCHING — B-level / A-borderline. NOT `good/`.**

**Promotion requirement**

Do not promote unless a natural, independently labeled downstream quantity can show that collapsing referent/kind/predicate status into one node unit changes a scientific or task conclusion. Otherwise KILL.

---

# Immediate search program

1. Continue assassination of the entity-reification lead at the parent level:
   - what nominal expressions should become independent graph nodes?
   - concept vs instance node extraction;
   - generic/predicative nominals in IE/KG;
   - graph errors caused by node reification;
   - referential status in generative IE.
2. In parallel, reverse-search mature annotation/output schemes for other distinctions erased by free-form generation.
3. Prefer candidates where the old field already has natural independent gold **and** the modern output change yields a directly measurable consequence, avoiding normative “better representation” arguments.

---

# Search discipline

For every new lead:

1. state the natural object and plain-language example;
2. write two plausible accounts before searching for effects;
3. identify exact natural data and independent gold;
4. search the classical parent plus 2024–2026 ACL/EMNLP/NAACL and neighboring venues;
5. attack with “This is just ____”;
6. promote only if all five gates are clearly YES.

> **No GPU until all five gates are YES.**
