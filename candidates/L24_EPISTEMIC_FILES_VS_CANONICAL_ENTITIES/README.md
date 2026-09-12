# L24 — Same Entity ≠ Same Epistemic File

**Status:** **HOLD / DEPRIORITIZED — HOT-DIRECTION + HARNESS + DATA-GOLD RISK — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

> **Search-priority correction — 2026-09-12:** Although the classical identity/perspective tension is intellectually clean, the current paper identity lands inside the extremely active Agent / long-term-memory area, depends on choices made by a memory/entity-resolution harness, and lacks an easy paper-scale natural identity×perspective gold substrate. Do not spend current search or compute budget on this route. Reopen only if the same scientific question can be made substantially framework-independent with strong natural data; otherwise archive/kill rather than building a bespoke memory stack.

## One-sentence RQ

> **If two names or descriptions denote the same real-world entity, is it always safe for an LLM agent's long-term memory to canonicalize them into one entity node, or can that merge destroy the perspective / mode-of-presentation information required for correct belief reasoning?**

## Plain example

Suppose an agent learns that **Dr. Chen** and **the anonymous reviewer** are the same person.

Alice, however, only knows Dr. Chen under the first description and does not know the identity. She says:

> "I trust Dr. Chen."

A conventional entity resolver may merge both mentions into one canonical node. If that merged node is then used to answer what Alice believes, the system can silently turn Alice's belief into:

> "Alice trusts the anonymous reviewer."

That substitution is valid for an extensional database lookup, but it is not generally valid inside a belief context.

## Why this is a real modern pressure

This candidate is not built from one paper's unexplained anomaly. It is created by a collision between several mature lines of work:

1. **Classical semantics / philosophy:** substitution of co-referring expressions can fail in referentially opaque contexts; mental-file / mode-of-presentation theories explicitly allow distinct cognitive files for the same referent.
2. **Modern LM semantics:** Wu et al., TACL 2023, directly show that referential opacity is a hard semantic phenomenon for language models.
3. **Theory-of-Mind evaluation:** ToMBench includes identity false belief as a distinct ability; broader ToM work requires reasoning from an agent's information state rather than from omniscient world truth.
4. **Modern agent memory engineering:** production memory systems perform entity resolution, aliasing, deduplication, and canonicalization so that repeated mentions of the same person/object map to a stable entity.
5. **Perspective-bounded memory:** 2026 character-agent work shows that globally shared factual memory causes factual overreach and that memory must respect what each character could know.

The unresolved scientific tension is therefore:

> **The world may contain one entity while a reasoner must still maintain more than one epistemic file for that entity.**

## Classical anchor

- Wu et al. (TACL 2023), *Transparency Helps Reveal When Language Models Learn Meaning*  
  https://aclanthology.org/2023.tacl-1.36/
- Recanati (Synthese 2024), *Memory-based modes of presentation*  
  https://link.springer.com/article/10.1007/s11229-024-04531-0

The classical object is not merely "can the model solve a linguistic puzzle?" The useful principle is stronger:

> **Coreference in the world does not imply interchangeability inside another agent's belief state.**

## Modern anchors

### Identity / belief reasoning

- ToMBench (ACL 2024) explicitly includes **Identity False Beliefs**:  
  https://github.com/zhchen18/ToMBench
- Wu et al. already establish the modern LM referential-opacity problem, but study LM semantic representations rather than memory canonicalization as a causal operation.

### Agent memory / canonicalization

- Neo4j Agent Memory performs entity resolution / deduplication and can auto-merge high-confidence aliases:  
  https://neo4j.com/labs/agent-memory/explanation/resolution-deduplication/
- SurrealDB Agent Memory is especially informative because its `same_as` relation can keep two entities separate rather than making identity automatically destructive:  
  https://surrealdb.com/docs/agent-memory/reasoning/reconciliation-and-supersession

### Perspective pressure

- Tang et al. (2026), *Staying In Character: Perspective-Bounded Memory For Book-Based Role-Playing Agents*, constructs KBF-QA with 4,386 questions across eight novels and shows large factual-overreach failures when memory ignores character knowledge boundaries:  
  https://arxiv.org/abs/2606.25632

## Prior work owns

- Referential opacity and de re / de dicto distinctions are old and have already been tested in neural language models.
- False-belief / identity-belief competence is already benchmarked.
- Entity canonicalization / alias resolution is an established KG and agent-memory operation.
- Perspective-bounded retrieval is already an active modern agent-memory direction.

## Prior work does NOT yet appear to own

A controlled modern agent-memory study where **entity canonicalization itself is the causal intervention**, with the same world facts and same base model, asking whether:

1. canonical merging helps ordinary extensional retrieval;
2. the same merge selectively corrupts intensional / perspective-sensitive reasoning;
3. separating **world identity** from **epistemic-file identity** can preserve both.

That operation-level bridge is the candidate's novelty. Fresh direct-collision search is still required before compute.

## Competing representations

Hold the underlying story / observations fixed and vary only the memory representation:

### A. Separate files
Two mention/entity nodes remain distinct unless the relevant perspective knows the identity.

### B. Global canonical merge
All aliases known by the system collapse into one entity node.

### C. Two-level identity
Keep a canonical world entity, but preserve perspective-indexed mention / epistemic-file nodes and the identity relation between them.

The important comparison is not which architecture has the highest aggregate score. It is the predicted **crossover**:

> global canonicalization should be useful for extensional identity retrieval yet can be harmful when a query is evaluated inside a subject's belief state.

## Decisive pilot

Use existing gold before creating a new benchmark.

1. Start with the identity-false-belief subset of ToMBench and referential-opacity items from the TACL line.
2. Convert each item into the same structured observation history.
3. Feed the same base model three memory views: A / B / C above.
4. Evaluate paired outputs on:
   - **extensional questions:** who is actually the same person / which facts belong to the same real entity;
   - **intensional questions:** what a specific character believes, predicts, or can rationally act on.
5. Match retrieval budget, token budget, prompt, and base model so that only representation changes.

A useful result is not merely "C wins." The load-bearing evidence is a selective representation effect:

- B preserves or improves extensional identity use;
- B damages the opaque / perspective-sensitive cases;
- C recovers the intensional cases without giving up the extensional benefit.

## Data path

### Existing gold for the first kill test

- **ToMBench**: identity false belief is explicitly labeled and immediately usable for a small causal representation audit.
- **TACL 2023 referential-opacity materials**: useful as a second, independent semantic substrate.

### Possible paper-scale natural substrate

The 2026 KBF-QA benchmark provides 4,386 human-verified questions over eight novels and explicit character visibility boundaries. It does **not** by itself provide an alias/identity benchmark, so it is only a possible substrate for mining naturally occurring identity-revelation cases, not ready-made gold for the central claim.

Do not authorize a Main-scale expansion until we know that enough naturally grounded identity/perspective cases can be obtained without turning the paper into a bespoke-stimulus project.

## Successful-result test

### Outcome 1 — canonical merge selectively breaks belief reasoning
Strong support for the central claim: entity resolution is not semantics-preserving across extensional and intensional uses.

### Outcome 2 — no harm from canonical merge
This is informative about robustness but probably **not enough for a Main paper by itself**. Unless a stronger positive result shows that modern LLMs reconstruct perspective boundaries despite destructive storage, kill rather than rescue with a generic robustness story.

### Outcome 3 — only weak models fail / stronger models reconstruct the distinction
Potentially useful heterogeneity result if there is a principled boundary (model scale, reasoning mode, memory architecture), but must be re-selected before expansion.

## Development path if the pilot survives

1. **C1 — Representation consequence:** establish the extensional/intensional crossover under representation-only intervention.
2. **C2 — Boundary:** identify when a merge is safe: ordinary factual queries, speaker-known identity, post-revelation state, etc.
3. **C3 — Repair / stronger prediction:** show that a two-level world-entity + epistemic-file representation predicts and repairs the unsafe cases.
4. **Consequence:** audit common agent-memory canonicalization schemes and show which downstream tasks require identity to be perspective-indexed rather than globally collapsed.

## Strongest reviewer compression

> "This is just referential opacity + ToM + perspective-aware memory."

### Survival condition

That compression wins unless the paper demonstrates something none of those components alone establishes:

> **a standard memory operation—canonical entity merge—is itself a causal source of downstream epistemic error, with a clean extensional/intensional crossover and a representation that resolves the trade-off.**

If the work drifts into "LLMs are bad at referential opacity" or "perspective-aware memory helps ToM," kill/reconstruct immediately.

## Main risks before pilot

1. **Direct-owner risk:** a 2025–2026 memory paper may already test alias/entity merging specifically against false-belief or perspective-sensitive downstream reasoning.
2. **Data-scale risk:** ToMBench's identity subset is suitable for a kill test but likely too small for the final paper.
3. **Representation leakage:** C may win merely because it contains more tokens / duplicate information; budgets and information content must be matched.
4. **Capability confound:** a model may already fail the belief question before any memory manipulation. Only items solved under a faithful non-merged representation are diagnostic for the canonicalization effect.
5. **Engineering-known objection:** some production systems already keep `same_as` links rather than destructively merging aliases. The contribution must be a scientific identification result, not the engineering advice "do not merge blindly."
6. **Fashion/harness risk:** even a positive result can be reviewer-compressed into a crowded Agent-memory design choice, and changing the memory harness may change the observed effect. This is now a first-class reason not to prioritize the route.

## Kill conditions

- A direct recent paper already performs the same canonicalization intervention with perspective / identity-belief outcomes.
- Faithful-vs-merged representation changes produce no selective effect on models that can solve the base cases.
- The apparent effect is fully explained by token count, retrieval differences, or extra explicit perspective annotations.
- We cannot obtain a credible paper-scale substrate beyond a tiny bespoke set without author-defined semantic gold.
- The final contribution compresses to a generic ToM benchmark or a memory-engineering best practice.
- The question cannot be reframed away from framework-specific Agent-memory machinery without losing its scientific identity.
