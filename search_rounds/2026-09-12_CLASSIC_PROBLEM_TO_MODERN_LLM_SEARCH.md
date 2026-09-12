# 2026-09-12 — Classic Problem → Modern LLM Search

**Target:** ACL / EMNLP / NAACL Main  
**Search preference:** favor the intellectual shape of *The Imperfective Paradox in Large Language Models*: a clean classical scientific problem whose answer becomes newly consequential in modern LLM / agent systems.  
**Scope note:** no new speech/audio topics; avoid pure linguistics competence tests. Prefer a classical distinction only when it creates a modern systems / reasoning / memory / evaluation consequence.  
**Rule:** combine multiple reliable literatures when useful; do not depend on one paper's unexplained anomaly; anti-resurrection first; no survivor quota.

## Survivor

### L24 — Same Entity ≠ Same Epistemic File

**Status:** SERIOUS / PRE-PILOT — DATA-SCALE + DIRECT-COLLISION AUDIT — NO COMPUTE AUTHORIZED  
Package: `candidates/L24_EPISTEMIC_FILES_VS_CANONICAL_ENTITIES/`

**RQ:** If two names/descriptions denote the same real-world entity, is it always safe for an LLM agent's long-term memory to canonicalize them into one entity node, or can that merge destroy the perspective / mode-of-presentation information required for correct belief reasoning?

**Why it survived this pass:** it connects an old referential-opacity / mental-file problem to a concrete modern operation—agent-memory entity resolution. The intended contribution is not another semantic competence test. It is a representation-only causal intervention asking whether global canonicalization has an **extensional benefit but an intensional/perspective cost**, and whether a two-level world-entity + epistemic-file representation resolves the trade-off.

**Main blockers before pilot:** direct-owner refresh; paper-scale natural identity/perspective gold; rule out token-budget/retrieval confounds.

---

## Compact rejection record

### Source monitoring / speaker provenance in long-term dialogue memory — KILL
**Question:** When multiple people contribute memories, does a global store lose who supplied which information and create source-monitoring errors?  
**Why not:** 2026 dialogue-memory work already directly attributes source-monitoring errors to global streams that obscure speaker provenance and introduces participant-specific stores. Direct modern parent collision.

### Frame Problem / persistence under action — KILL
**Question:** After an action changes a few facts, can an LLM preserve everything that should remain unchanged instead of recomputing the world incorrectly?  
**Why not:** recent action-reasoning benchmarks explicitly root the task in the classical frame problem. A new dataset/model would be another capability cell, not a new scientific parent.

### AGM belief revision / stale-memory replacement — KILL
**Question:** When later evidence invalidates an earlier belief, does an agent revise the belief or merely accumulate contradictory memories?  
**Why not:** stale-memory and belief-revision benchmarks already directly study when memories become invalid and how agents update/recover. Parent is active and crowded.

### Partial observability / explicit belief state — KILL
**Question:** Is an agent's failure under incomplete information caused by not maintaining an explicit distribution over possible world states?  
**Why not:** 2026 work already builds belief-memory / belief-state engines for partial observability, including multiple hypotheses and probabilistic state. Direct collision.

### Structural analogy vs surface similarity in experience retrieval — KILL
**Question:** Should an agent retrieve past experience by surface similarity or by shared causal/relational structure?  
**Why not:** scientific analogy work already separates structural from surface matching, while current experience-memory work directly studies similarity-induced behavior and misgeneralization. The proposed bridge compresses to existing parents.

### Memory reconsolidation / retrieval changes memory — KILL
**Question:** Does repeatedly retrieving and rewriting a memory improve it, or can retrieval itself corrupt an initially correct memory?  
**Why not:** 2026 memory-consolidation work directly reports useful memories becoming faulty under continual updates; reconsolidation-style memory updates are already an explicit agent-memory design axis.

### Common knowledge vs mutual knowledge — DO NOT REOPEN
**Question:** Does everyone knowing X imply the common knowledge needed for coordination?  
**Why not:** already killed as **K005**. It remains a textbook distinction + higher-order ToM competence check without a new modern causal operation. No new ID.

### Object permanence / identity tracking in VLMs — KILL
**Question:** When an object disappears, reappears, or changes view, does a multimodal model preserve object identity rather than treat each observation independently?  
**Why not:** recent VLM benchmarks already directly target object permanence, temporal object continuity, and identity tracking. This is now a benchmark parent rather than an open bridge.

### Permission vs capability / authorization in tool agents — KILL
**Question:** If an agent can execute an action, does it distinguish that capability from permission or obligation to execute it?  
**Why not:** attractive classical deontic distinction, but current deontic-agent and authorization/security work already directly studies permissions, prohibitions, obligations, confused-deputy failures, and underspecified authorization.

### Independence of Irrelevant Alternatives in LLM choice/judging — KILL
**Question:** Should adding an irrelevant option change an LLM's preference between two existing options?  
**Why not:** 2026 preference-axiom work directly measures IIA violations in LLM recommenders and alignment rules. Direct ownership.

### Set vs multiset memory / duplicate meaning vs repeated evidence — KILL
**Question:** When two memories say nearly the same thing, are they duplicates to merge or repeated observations whose multiplicity/provenance should matter?  
**Why not:** the scientific core collapses into the already-killed dependent-evidence parent **K010** plus **L23 Similarity Is Not Provenance**. Existing memory systems already choose among semantic deduplication, reinforcement counts, and immutable repeated events. A memory-specific wrapper does not create a new parent.

### Experience abstraction / Simpson-like aggregation — KILL
**Question:** Can compressing many successful trajectories into one general rule erase a condition that reverses the rule in a subgroup?  
**Why not:** current experience-memory work already owns cross-trajectory abstraction, negative transfer from fixed abstraction, and consolidation-induced corruption. Simpson's-paradox framing gives a cleaner diagnostic but not a sufficiently independent Main-level scientific object.

### Consistent snapshot vs individually fresh evidence in RAG/memory — KILL
**Question:** Can retrieving the individually newest version of every document assemble a context that never existed as one coherent world state?  
**Why not:** the database-style idea is attractive, but 2026 agent-memory work already imports snapshot isolation/MVCC explicitly to prevent evidence tearing, while temporal/version-aware RAG is crowded. The modern operation is already owned closely enough that a new benchmark would not buy a distinct Main identity.

### Open-world vs closed-world assumption in agent knowledge — KILL
**Question:** Does absence from an agent's knowledge store mean false, or merely unknown—and when is each assumption safe for action?  
**Why not:** EACL 2026 open-world KGQA and ICML-era open-world logical-reasoning work directly center incomplete knowledge and the closed/open-world distinction. A new agent-memory wrapper would be a domain transfer, not a new question.

### Value of Information / when should an agent ask rather than act — KILL
**Question:** Is uncertainty alone enough to decide when an agent should ask a clarification question, or should it ask only when the information can change a consequential decision?  
**Why not:** ACL 2026 directly introduces a Value-of-Information framework for human–agent communication across multiple domains. Direct collision.

### Qualification / ramification problem for tool agents — KILL
**Question:** Can an agent reason about open-ended action preconditions and indirect consequences that are not exhaustively listed in a tool schema?  
**Why not:** ICLR 2025 ActionReasoningBench already explicitly grounds LLM evaluation in reasoning about actions/change, action executability, effects, frame/ramification constraints. Tool-agent versions would be a narrower contemporary instantiation.

### Explicit recall vs implicit/procedural enactment — KILL
**Question:** Can an LLM explicitly state a learned rule yet fail to automatically enact it later, revealing a declarative–procedural dissociation?  
**Why not:** ACL 2026 Best Resource ImplicitMemBench already makes explicit recall vs implicit behavioral adaptation the motivating distinction; MemoryBench spans declarative/procedural memory, and 2026 Neural Procedural Memory explicitly frames a text–action disconnect. The remaining comparison is too compressed by current work.

### Generic statement vs universal rule under structured memory — HOLD, NOT PROMOTED
**Question:** When an agent converts a generic such as “birds fly” into a reusable graph/rule memory, does the structured representation silently turn an exception-tolerant default into a universal rule?  
**Why interesting:** this has the right shape—classical generic/default semantics → modern text-to-graph/structured-memory operation → downstream exception reasoning. Existing work shows LLMs already overgeneralize generics, GenericsKB supplies millions of naturally occurring generic statements, and structured agent memory is now common.  
**Why not serious yet:** the clean downstream exception gold is weaker than the source-generic data; much of the strongest exception set is automatically generated/human-sample-validated rather than natural independent gold. The paper is also outcome-fragile if raw text and triples behave similarly. Keep as a search seed until a natural paired substrate or a stronger outcome-robust estimand is found.

### Essential indexical / de se self-location × action — HOLD, NOT PROMOTED
**Question:** Can an agent know all third-person facts about the world yet still fail to act because it does not represent which entity/location is *itself / here / now*?  
**Why not yet:** conceptually strong old-problem→agent bridge and no direct collision found in this pass, but current versions rely on synthetic philosophical scenarios, lack an obvious natural gold substrate, and risk becoming a pure semantics/ToM competence test. Keep only as a search seed; no compute.

---

## Search takeaway

The useful pattern from this pass is **not** “pick an old philosophical distinction and test whether an LLM knows it.” Most such candidates die exactly that way.

The stronger pattern is:

> **classical distinction → modern operation that silently assumes the distinction away → representation/intervention with a real downstream consequence.**

L24 survived because entity canonicalization is a concrete modern operation with a plausible causal trade-off. Continue searching for more topics with that structure rather than lowering the bar.
