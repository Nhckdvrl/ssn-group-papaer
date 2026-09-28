# NPC Deception Investigability — Workbench

**Lane: our-taste. Status: exploratory workbench — not a candidate.**

## Territory

This workbench studies a game-specific tension in LLM-driven NPC deception:

> A deceptive NPC is allowed to say things that are false, but a consequential false claim should still belong to the playable game world rather than create an investigation dead end.

The object is **not generic hallucination reduction**, generic agent deception, or “teach NPCs to lie.” The relevant unit is a false NPC claim together with the game-world affordances that let a player test, refute, or act on it.

Removing the game removes the scientific object: entities, rooms, witnesses, timelines, evidence routes, contradiction mechanics, and reachable player actions are load-bearing.

## Genealogy / why this territory exists

### ClueGen (AIIDE 2016)
Procedural NPC testimonies are generated from remembered events. Lies alter event details and omissions hide memories. This is rigid, but deception remains mechanically tied to world history and the player can accuse an NPC of lying.

### Lies, Deceit, and Hallucinations (CHI 2024)
Player evidence establishes that false statements are not one error class in games. Perceived intentional deception can acquire narrative/gameplay meaning, while apparently accidental falsehoods can break players' mental models.

### Free LLM detective NPCs
Open-ended dialogue increases linguistic freedom but can invent a depot, witness, timeline activity, item, or other entity that does not exist in the playable world. The player can then spend real gameplay effort pursuing something the game cannot represent.

### Structured Knowledge Tree (AIIDE 2026)
This work explicitly separates desired deception from game-breaking hallucination. Its LLM-only condition suffers heavily from unauthored false alibis and fabricated entities. SKT recovers reliability by retrieving an authored truth/lie node and telling the Dialogue LLM what content to express.

This is strong prior, not a strawman. It also reveals the pressure: the system largely removes the generative burden of **what to lie about**, and its tightly structured progression can make revelations feel forced.

The lineage therefore looks like:

> structured + mechanically grounded but rigid → generative + expressive but capable of untraceable dead ends → structured authored deception again

The workbench asks whether there is any scientifically nontrivial space between those endpoints. It is allowed to discover that there is not.

## Ownership boundaries

Already owned; do not claim:
- intentional lie vs hallucination;
- NPC knowledge/provenance tags;
- contradiction graphs;
- pre-authored lie nodes;
- “NPCs should be able to lie”;
- generic persona/deception benchmarks;
- generic LLM factuality or anti-hallucination.

A paper cannot be “SKT but with another verifier.”

## Strong executable substrate

Primary workbench substrate:

**DilanRG/ai-murder-mystery-v2 (Ashwick Trust / AI Murder Mystery Game)**

Why use it:
- immutable engine-authoritative canonical truth;
- distinct private knowledge per NPC;
- authored `LieDefinition` with `contradicts_fact_ids`;
- truthful observations and authorized misdirection are separate runtime actions;
- evidence has physical placement, discovery routes, prerequisites, and provenance;
- generated cases require independent complete evidence routes;
- deterministic replay and post-game audit;
- provider-free authored fixtures and dummy-provider end-to-end tests;
- model output cannot directly patch canonical world state.

Important limitation:
- this is an engineering substrate, not the scientific novelty source;
- current lies are authored finite candidates;
- the validator checks lie references/disclosures and validates global evidence reachability/solvability, but individual lies are not obviously required to have their own player-reachable refutation path.

Scientific comparison anchors remain ClueGen and SKT.

## Baseline residency

Before any new method:

1. reproduce the repository's deterministic procedural-acceptance test and authored demo cases;
2. inspect every current authorized lie and map:
   - what canonical fact it contradicts;
   - what evidence or testimony supports that fact;
   - when the player can reach that refutation;
   - whether pursuing the lie implies any valid game action;
3. freeze a small set of cases/questions where the current authored-lie system is unquestionably playable;
4. keep the engine, case, NPC private state, player state, question, backbone, and decoding fixed while changing only the **deception-authority interface**;
5. log the complete generated claim plus all world entities/time/location references before judging quality.

Do not begin with a new lie generator, graph module, or learned verifier.

## First diagnostic ladder

The first experiment is deliberately designed to **kill trivial versions of the idea**.

### B0 — Authored lie
Current Ashwick/SKT-style regime:
- the false proposition is author-defined;
- model may choose/realize it;
- maximum structural control.

This is the rigid strong baseline.

### B1 — Free lie
Give the same NPC its legitimate private context and deceptive goal, but let it decide what false claim to make.

Purpose: reproduce the actual failure surface, not assume it.

### B2 — Fact-targeted free lie
The model must first choose one canonical fact it intends to contradict; wording/content around that target remains generative.

This is a **diagnostic control, not the proposed method**.

If B2 already removes essentially all meaningful dead ends while retaining useful variation, stop: the territory collapses to an old ClueGen/SKT idea and is not worth a paper.

Only if B2 still fails in systematic, game-specific ways should the workbench ask what additional structure is actually load-bearing.

## What to measure

Avoid one generic “hallucination rate.” Decompose a generated deceptive claim into mechanical properties.

### World-reference validity
Do all consequential named entities, locations, objects, people, and temporal anchors exist in the current game world or authored case?

### Contradiction grounding
Can the false claim be mapped to at least one canonical proposition it contradicts?

### Refutation reachability
Is at least one contradiction-supporting fact/evidence item obtainable by the player through legal actions from the current game state before the relevant deadline?

### Affordance alignment
If the lie invites an investigation (“ask X”, “check room Y”, “look for item Z”), does the game actually expose an action/path that can pursue it?

### Information leakage
Does the lie accidentally reveal hidden canonical facts, the culprit, or future evidence?

### Narrative consequence
Does following the claim create a bounded detour / meaningful challenge, or an infinite dead end outside the game state?

### Generative freedom
How much semantic variation remains beyond paraphrasing one authored lie node?

Naturalness/character quality is secondary during early workbench experiments; use it only after mechanical validity is established.

## First pilot

Start inference-only. No training.

- one strong open instruct model first;
- deterministic authored/procedural fixture(s);
- same NPC/question/context across B0/B1/B2;
- repeated samples only to estimate generation variance;
- classify failures mechanically where possible from engine IDs; use model judgment only for residual semantic mapping, with manual spot audit.

First useful output is a **failure map**, not a headline score.

Examples of slices:
- fabricated entity/location;
- impossible timeline;
- valid world entity but unreachable refutation;
- valid contradiction but no player affordance;
- accidental truth leakage;
- vacuous denial that is safe but adds no gameplay;
- harmless background improvisation that should not be penalized;
- adversarial player premise adoption / sycophancy.

## Decision gradient

Possible outcomes and what they imply:

### Free lie fails; fact-targeted lie succeeds
Stop. The apparent research question reduces to “bind generation to an authored fact,” already anticipated by ClueGen/SKT.

### Free and fact-targeted lies both mostly succeed
Stop. There is no meaningful problem under a strong baseline.

### Fact-targeted lies still create systematic unreachable or unactionable claims
Then the relevant object may be **claim-to-world affordance coupling**, not factuality.

### Mechanical validity requires pre-authoring nearly the whole lie
Then the rigidity/improvisation trade-off is real, but method work is justified only if we can identify which minimal constraints account for it.

### Generated lies are valid but offer no player/game value beyond authored ones
Stop. More generative freedom is not itself a contribution.

## Method permission

No method at entry.

A method is allowed only after:

> free deception failure → stable mechanical bottleneck → minimal enforceable contract → improved playability without collapsing to authored-node paraphrase

Possible later interventions are intentionally unspecified. Do not pre-commit to a compiler, verifier, knowledge graph, constrained decoder, or training objective.

## Feasibility

This workbench is intentionally cheap at the start:
- no model training;
- deterministic provider-free game fixtures exist;
- the first analyses can run against local open models;
- world-state and evidence validity are already machine-readable;
- the main engineering task is an inference/evaluation harness around an existing tested game engine.

Human player studies are **not** required for the first gate. They become relevant only if a mechanically valid generative regime survives and the remaining claim is about player experience.

## Kill conditions

Stop early if any of the following holds:
- simple fact-ID targeting/whitelisting solves the failures;
- failures are mainly weak prompting or small-model artifacts;
- the system needs large amounts of newly authored lie/evidence annotation;
- “investigability” cannot be measured without subjective judge chains;
- the only benefit is stylistic diversity;
- nearest prior is found that already generates novel false claims with guaranteed in-world refutation/interaction paths;
- the work drifts into generic agent deception or generic factuality.

## Paper identity

None.

There is no registered RQ, method, or promised result. The workbench exists because the genealogy exposes a concrete NPC-specific pressure and the open substrate makes a cheap, high-information kill experiment possible.
