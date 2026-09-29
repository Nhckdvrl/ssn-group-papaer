# Game NPCs in the Foundation-Model Era — Landscape & Genealogy

**Last verified:** 2026-09-29  
**Scope:** reusable research material for game NPCs / interactive characters. This is **not** a candidate list and does not authorize a paper direction.

## 0. Why “NPC” is not one research problem

The most useful lesson from *AI for Games in the Foundation Model Era* is that foundation-model NPCs sit across several roles rather than one isolated category:

- **Play & Act:** an NPC/companion is an agent that perceives, plans, acts, communicates, and coordinates.
- **Generate & Adapt at Runtime:** dialogue, quests, character behavior, personalization, and narrative events are generated during play.
- **Model Players & Games:** learned world/state models can determine what an NPC sees, predicts, and reacts to.
- **Test & Evaluate:** NPC quality must be established in the actual game loop, not only on isolated utterances.

The survey repeatedly asks three cross-role questions that are especially useful for NPC research:

1. **Boundary:** what state, rules, control, memory, and authority come from the game, and what is assigned to AI?
2. **Transfer / reuse:** what generalizes across characters, games, interfaces, and players?
3. **Evidence:** does the evaluation support the claim where the NPC is actually used?

A fluent character is therefore not automatically a good NPC. An NPC can separately fail at knowledge, memory, persona, game-state grounding, action execution, cooperation, authorial constraints, latency, or player experience.

## 1. Survey map

### S1 — AI for Games in the Foundation Model Era (Luo et al., 2026)
- 120-page cross-lifecycle survey with a living bibliography.
- Key move: classify by **what AI output is used for**, not by model family.
- For NPCs, the relevant pressure is the coupling of dialogue, memory, personality, actions, shared world state, and runtime constraints.
- Runtime evaluation should exercise complete sessions, revisit prior state, compare adaptive vs non-adaptive controls, and measure player/game outcomes.
- Primary sources:
  - https://arxiv.org/abs/2609.16679
  - https://eurekaleo.github.io/awesome-ai-for-games/
  - https://github.com/Eurekaleo/awesome-ai-for-games

### S2 — A Survey on Large Language Model-Based Game Agents (Hu et al., ACM CSUR 2026)
- Decomposes LLM game agents into perception, memory, thinking, role-playing, action, and learning.
- Useful because NPC work frequently optimizes one component while evaluation silently depends on several.
- https://arxiv.org/abs/2404.02039

### S3 — AI-Native Games: A Survey and Roadmap (Xu et al., 2026)
- Defines AI-native games counterfactually: remove/trivially replace generative AI and the core play should materially collapse/change.
- Useful NPC lesson: open-ended generation only becomes gameplay when goals, rules, state, feedback, pacing, and agency make it consequential.
- Relationship/companion play and multi-agent simulation are relatively underrepresented in the surveyed corpus, but this is a landscape fact, **not** an idea by itself.
- https://arxiv.org/abs/2607.00527

### S4 — Narrative and dialogue generation for video-games: A systematic mapping (Salmaze et al., 2026)
- Maps 55 peer-reviewed empirical studies.
- Recurrent problems: incoherence, repetition, memory limits, latency; evaluation is heterogeneous and often questionnaire-heavy.
- Important negative lesson: “memory/coherence” is now a generic problem label, not enough to define a new scientific object.
- https://doi.org/10.1016/j.engappai.2026.115041

### S5 — Survey on LLM-Based Social Agents in Game-Theoretic Scenarios (Feng et al., TMLR 2025)
- Useful bridge from character role-play to beliefs, incentives, communication, social action, and game-specific evaluation.
- https://openreview.net/forum?id=CsoSWpR5xC

---

## 2. Lineage A — From dialogue NPC to grounded/action-capable NPC

### Parent state
Classic NPC dialogue systems separated authored dialogue from game mechanics. Early LLM work made language open-ended but risked becoming a chatbot attached to a game.

### A1 — Craft an Iron Sword (Volum et al., 2022)
- Early, unusually clean changed premise: the same model can emit **dialogue and executable code/API calls**, making language consequential in Minecraft.
- Public prototype: microsoft/interactive-minecraft-npcs.
- Research move worth keeping: do not measure only what the NPC says; expose an execution interface.
- https://github.com/microsoft/interactive-minecraft-npcs

### A2 — Collaborative Quest Completion with LLM-Driven NPCs in Minecraft (Rao et al., 2024)
- Moves from isolated command demos to human–NPC collaboration over a quest.
- Public user-study/gameplay logs: microsoft/collaborative-quest-completion.
- Pressure: language-only reasoning is insufficient when rich game state / visual grounding matters.
- https://arxiv.org/abs/2407.03460
- https://github.com/microsoft/collaborative-quest-completion

### A3 — Commonsense Persona-Grounded Dialogue Challenge (CPDC 2025)
- Explicitly joins persona/worldview with task-oriented function calling.
- Three tasks separate task-oriented, commonsense/persona, and hybrid single-agent behavior.
- Public starter data/harness and a Llama-3.1-8B baseline.
- Strong public solution: Qwen3 with separate LoRA experts for tool call, direct dialogue, and post-tool dialogue; 1.7B/14B weights are public.
- Artifact:
  - https://github.com/Augustus2011/sony-cpdc-2025-starter-kit
  - https://github.com/MahammadNuriyev62/CPDC-challenge-2025-solution

### A4 — Deflanderization for Game Dialogue (2025)
- Directly studies the tension between maintaining a rich character and completing task-oriented interactions.
- Important ownership warning: generic “persona vs task execution trade-off” is already an explicit research framing.

### What is saturated / risky
- “Make NPC dialogue more persona-consistent.”
- “Add tool calling to a role-playing model.”
- “Persona vs task trade-off exists.”
These are useful baselines/pressures, not fresh territories by themselves.

---

## 3. Lineage B — Persona, role-play, memory, relationship

### B1 — Generative Agents (Park et al., UIST 2023)
- Memory stream → retrieval/reflection → planning; foundational for believable persistent agents.
- https://arxiv.org/abs/2304.03442

### B2 — MemoryRepository for AI NPC (2024)
- Explicit short-/long-term memory, summarization and forgetting in an NPC setting.
- Shows that “give the NPC long-term memory” already has a long implementation lineage.

### B3 — CoSER / DMT-RoleBench / RMTBench / PersonaArena (2025–2026)
- Role-playing moved from prompt demos to datasets, long multi-turn evaluation, established-character simulation, and arena-style evaluation.
- Consequence: raw persona fidelity is now a benchmark ecosystem, not an empty space.

### B4 — PersonaEval (2025)
- Important measurement warning: LLM judges can be substantially weaker than humans at identifying whether a response actually belongs to the intended role.
- Reusable lesson: LLM-as-judge scores for NPC “character quality” need external validity checks.

### B5 — Memory-Driven Role-Playing (Findings ACL 2026)
- Decomposes memory-grounded role-play into Anchoring / Selecting / Bounding / Enacting.
- Shows upstream memory quality can materially improve downstream role-playing even with a modest open model.
- Ownership warning: generic “better retrieval improves role-play” is not enough.

### B6 — One Policy, Infinite NPCs / PCSP (2026)
- Moves persona from **text style** into **behavioral policy conditioning**: one shared PPO policy is conditioned on a frozen language-model embedding of designer-authored persona text.
- The paper's headline evidence is trajectory-to-persona identification / semantic-behavior alignment, with an InfoNCE trajectory-consistency objective described as load-bearing.
- Public artifact is unusually complete: Mini-Inzoi environments, persona splits, checkpoints/results, ablations, Melting Pot validation, UE5 integration, and later audit documents.
- Primary paper: https://arxiv.org/abs/2605.23652
- Artifact: https://github.com/yoosunghong/pcsp

#### 2026-09-29 independent artifact audit — important correction
The current public repository contains later diagnostics that materially narrow the interpretation of the paper's internal metric:

- an **independent action-only Big-Five evaluator** reports mean balanced accuracy **0.482 full vs 0.511 no-consistency**; the paired bootstrap interval for full-minus-no-consistency is **[-0.056, -0.002]**;
- adding state summaries yields **0.556 vs 0.558**, with no meaningful separation;
- most independently recoverable action-only trait signal is extraversion, while conscientiousness falls below chance under the held-out shift;
- the learned persona projection keeps trait information but compresses raw Qwen embedding geometry strongly: raw Big-Five probe **0.898** vs projected **0.799**, raw/projected cosine-geometry correlation **rho=0.404**, effective rank **3.87**;
- gradient-path auditing shows the InfoNCE term updates the persona projection and trajectory encoder but has **no direct actor-head gradient path**. Any behavioral effect must therefore be mediated indirectly through the shared projection.

The repository itself states the defensible conclusion narrowly: InfoNCE is load-bearing for alignment between the learned trajectory encoder and persona projection, but these independent probes **do not establish an advantage in independently observable Big-Five behavior**.

This is a high-value baseline-first pressure because the headline representation/evaluator signal and an independent behavioral readout disagree inside the same open system. Do not summarize PCSP simply as “persona consistency solved.”

### B7 — Explicit behavioral-persona parents (2024–2026)
Two older/current families provide useful counterweights to PCSP rather than direct successors:

- **Multi-Agent System for Emulating Personality Traits Using Deep RL** (2024) and **Reinforcement Learning Methods for Emulating Personality in a Game Environment** (2025) define OCEAN traits through explicit game-behavior reward functions. They are less flexible than natural-language persona conditioning, but the behavioral semantics are inspectable.
- **Stack More Levels: How to Get General and Human-like Mario Playing** (IEEE CoG 2026) trains runner / killer / collector playstyles with explicit segment-based persona rewards, then PPO→DRAIL with human demonstrations. The full code, checkpoints, PCG levels, and evaluation are public. It is useful because persona preservation is measured in actual game outcomes (kill/coin behavior), not only representation-level identity.
  - https://github.com/carrotoxic/mario-personas

These parents make a clean comparison possible: **semantic flexibility of free-form persona text** versus **behavioral identifiability grounded in explicit action consequences**.

### Pressure that remains scientifically useful
The field has multiple incompatible operationalizations of “persona”: linguistic style, stated preference, recalled biography, representation-level identity, action tendency, social policy, and trajectory-level behavior. Treating them as interchangeable is unsafe.

A particularly important unresolved boundary is now visible:

> **Does a persona-conditioned NPC merely produce trajectories that are statistically distinguishable by a coupled evaluator, or does the persona semantics causally and predictably change decisions in the game states where that trait should matter?**

This should not be answered by inventing another persona score first. The open PCSP artifact allows counterfactual state/persona interventions, action-distribution analysis, trait-relevant state slicing, task-pressure sweeps, projection interventions, and independent behavioral readouts before any new method is proposed.

---

## 4. Lineage C — World/lore/state authority and narrative constraints

### Parent state
Free generation increases local flexibility but makes it harder to preserve quest logic, lore, secrets, commitments, and authorial intent.

### C1 — Personalized Quest and Dialogue Generation with KG + LM (CHI 2023)
- Knowledge graphs anchor character/location/game-state facts while an LM generates.
- Early example that structured state can be more load-bearing than a larger generator.

### C2 — SceneCraft (AIIDE 2023) → NarrativeGenie (AIIDE 2024)
- Moves from LLM-authored interactive scenes to runtime narrative beats constrained by explicit narrative structure/current state.
- Useful genealogy: generation becomes an operation over a controlled story representation rather than free text.

### C3 — KNUDGE: Ontologically Faithful Generation of NPC Dialogues (EMNLP 2024)
- Uses real *The Outer Worlds* quest/dialogue material and an ontology of lore/persona/entity relationships.
- Strong anchor for “faithfulness to authored world knowledge,” not generic chatbot helpfulness.
- https://aclanthology.org/2024.emnlp-main.520/

### C4 — PANGeA (AIIDE 2024)
- Unity-integrated runtime narrative/NPC generation with explicit validation and memory.
- Important baseline lesson: validation can dominate raw model scale on constraint satisfaction.

### C5 — Slice of Life (FDG 2025)
- Symbolic social simulation remains authoritative; LLM acts primarily as natural-language realization.
- Clear changed premise: the LLM does **not** need to own the social dynamics to make interaction feel generative.

### C6 — Symbolically Scaffolded Play (2025)
- Structured constraints help some NPC roles but can hurt others.
- Reusable lesson: more control is not uniformly better; role and interaction objective matter.

### C7 — Can LLM Agents Stick to the Script? / NCP-Bench (2026)
- Tests long-horizon narrative commitment preservation rather than isolated response quality.
- 100 structured narrative environments; public code/data/prompts.
- Ownership warning: generic long-horizon “stay consistent with facts/commitments” is now directly benchmarked.

### C8 — NarrativeWorlds / typed authoritative narrative state (2026)
- Separates generated dialogue from authoritative updates to state/relationships/secrets/events.
- Strong architectural evidence for **proposal vs authority** as a real deployment boundary.

### Durable question-forming pressure
Who is allowed to change world state, relationship state, quest state, or hidden facts? “Put everything in the prompt” and “let the LLM own the world” are not neutral design choices.

---

## 5. Lineage D — NPC as embodied teammate / social actor

### D1 — Proactive cooperative agents and MindAgent / game-agent work
- Cooperation requires partner modeling, communication, task allocation, and action, not only dialogue.

### D2 — Proact-VL (ICML 2026)
- Gaming companion/commentator that continuously watches video and must decide **when** to intervene, not only what to say.
- Useful new variable: interaction timing itself becomes part of the policy.
- Artifact is partial: code is public, but some model/data/training components were still marked TODO when checked.

### D3 — Lies We Can See (2026)
- MineAmongUs gives agents both verbal and non-verbal deception channels.
- Public Docker testbed, game logs, VLM-agent harness, memory/planning/state ablations, and human annotations.
- Key conceptual lesson: social behavior can be carried more strongly by **movement/action** than language; a transcript-only NPC evaluation can miss the load-bearing channel.
- https://github.com/JunseoKim0103/Lies-We-Can-See

### D4 — MARBO (EMNLP 2026)
- Relational belief grounding for social-deduction agents; makes “who believes what about whom” an explicit state for action and language.

### D5 — FAIRGAMER (ACL 2026)
- Extends NPC evaluation to social bias across transaction/cooperation/competition.
- Useful reminder that “believable” and “fair/useful” are distinct claims.

### D6 — LLM-guided RL for adaptive NPC combat (2026)
- LLM strategy tags can help some opponents but harm others; a near-constant high-level preference can become a bottleneck.
- Good failure-analysis exemplar, but narrow as a standalone territory.

---

## 6. Lineage E — NPC inside learned / generated game worlds

This lineage is distinct from LLM dialogue NPCs.

### E1 — ReactiveGWM (2026)
- Pressure: video game world models often model the player but treat NPC motion as passive/background dynamics.
- Changed premise: player control and NPC autonomy should be separate conditioning channels.
- NPC strategy is injected through cross-attention; reports zero-shot strategy transfer across Street Fighter variants.
- Exceptionally complete public artifact: inference, training, checkpoints, datasets, examples.
- https://arxiv.org/abs/2605.15256
- https://github.com/INV-WZQ/ReactiveGWM

### E2 — WorldMind (2026)
- Direct successor pressure: externally specifying the NPC’s strategy is not the same as an NPC understanding game state and deciding what to do.
- Adds an explicit state-understanding → decision → control → generation loop.
- Ownership/feasibility warning: this is a fast-moving, compute-heavy lineage; code/weights were not fully public when checked.

### Interpretation
This is perhaps the clearest example of “successful paradigm → next bottleneck”: once video world models can obey player actions, **other agents become the next missing controllable state variable**.

---

## 7. Lineage F — Multi-agent populations and scalable social simulation

### F1 — Project Sid (2024)
- 10–1000+ Minecraft agents; large-scale social specialization, rules, culture.
- Public repo/report: https://github.com/altera-al/project-sid

### F2 — AgentSociety (2025–2026)
- Large social simulation platform and evaluation ecosystem.

### F3 — CASCADE (2026)
- Hierarchical hybrid design: macro director → coordination hub → cheap local behavior trees / utility; LLM used selectively.
- Reusable production lesson: “every NPC calls a frontier LLM every tick” is not the only or necessarily useful abstraction.

### F4 — AI Agents Alone Are Not (Yet) Sufficient for Social Simulation (2026)
- Negative/measurement anchor: plausible role-play does not establish faithful population behavior; environment dynamics, schedules, priors and institutional structure can dominate.

### Risk
This area can become simulator engineering or social-science validity work before a tractable ML object emerges.

---

## 8. Lineage G — Player experience: more open-ended ≠ monotonically better

### G1 — The Double-Edged Sword of Open-Ended Interaction (2026)
- Randomized player study (N=130).
- LLM-driven open-ended NPC interaction can increase cognitive load; overall game-experience gains are not automatically significant.
- Effects depend on task/scenario; autonomy and usability/trust can move differently.
- Key changed premise: **more generative freedom is not automatically better NPC design**.

### G2 — Contextualized generative AI and player experience (2026)
- Dynamic state and adaptive NPC dialogue can improve presence/autonomy/enjoyment when generation is embedded in game logic.
- Useful contrast with G1: whether GenAI is consequential and contextualized matters.

### G3 — Token latency in NPC dialogue (2026)
- Player experience depends not only on time-to-first-token but ongoing delivery cadence; character personality interacts with latency perception.
- Physical-time constraints belong in NPC evaluation, especially voice.

### G4 — Static / hybrid / fully open dialogue comparisons (2026)
- Open dialogue can increase conversational naturalness/length but does not imply every player/task benefits equally.

### Durable pressure
The correct optimization target may be player agency, cognitive burden, trust, pacing, or task success—not “open-endedness” or judge-rated naturalness.

---

---

## 9A. Lineage H — Deception, hallucination, and investigability

This lineage is NPC-specific because a false statement can be a **game mechanic**, not merely a model error. The key question is not “is the utterance factually true?” but whether its falsity is intentional, world-compatible, and playable.

### H1 — ClueGen (AIIDE 2016)
- Procedural murder-mystery NPCs construct testimony from their own remembered events.
- A lie alters details of an existing testimony; an omission suppresses a remembered event.
- Players can accuse an NPC of lying/withholding, and the game knows whether the accusation is correct.
- Important primitive: deception is generated **from world history**, so it remains mechanically connected to something the player can challenge.
- https://doi.org/10.1609/aiide.v12i2.12896

### H2 — Deceptive Virtual Suspect (AAMAS 2017)
- An autonomous suspect maintains a real story and a parallel story, reasons about what the interviewer may know, and dynamically alters structured event/entity fields to construct less-incriminating alternatives.
- Important ownership warning: **runtime generation of lies is not new**. The old system already automated alternative-story construction from a structured event memory.
- Its boundary is equally important: interaction is query/template based, entities/events are authored into the knowledge base, and it does not solve modern open-language generation against a live evidence/action world.
- https://dl.acm.org/doi/10.5555/3091282.3091419

### H3 — Lies, Deceit, and Hallucinations (CHI 2024)
- Player study with deliberate human-authored falsehoods and human-approved LLM hallucinations.
- Perceived intentional falsehoods were often interpreted as meaningful narrative/gameplay behavior; seemingly accidental falsehoods instead conflicted with players’ mental models.
- Changed premise: “factual correctness” is the wrong scalar objective for deceptive NPCs.
- https://doi.org/10.1145/3613904.3642253

### H4 — Free LLM detective NPCs
- Open-ended LLM dialogue greatly expands linguistic freedom but creates a new failure: an NPC may invent a location, witness, timeline activity, or evidence that the game world cannot support.
- In a detective game this is worse than ordinary factual error because the player may spend real gameplay effort pursuing a **mechanical dead end**.

### H5 — Structured Knowledge Trees (AIIDE 2026)
- Explicitly distinguishes desired deceptive falsehoods from game-breaking hallucinations.
- In the reported LLM-only condition, unauthored false alibis and fabricated entities dominate critical failures.
- SKT cuts these failures by selecting an authored knowledge-tree node and telling the Dialogue LLM exactly which truth/lie to express.
- The cost is equally informative: “what to lie about” is no longer generative, and tightly coupled progression sometimes makes revelations feel forced or abrupt.
- https://arxiv.org/abs/2609.23043

### H6 — Current pressure (territory-level, not a registered RQ)
The lineage has swung:

> structured + mechanically grounded but rigid → generative + expressive but capable of untraceable dead ends → structured authored lie nodes again.

A useful object to keep investigating is therefore **deception as playable world state**, not generic hallucination reduction. A consequential false claim should be distinguishable from harmless improvisation and should interact with actual game affordances: entities, locations, timelines, witnesses, evidence, contradiction mechanics, and player actions.

Do **not** claim novelty for:
- intentional lie vs hallucination;
- knowledge/provenance tags;
- contradiction graphs;
- pre-authored lie nodes;
- “NPCs should be able to lie.”

Those are all owned. The unresolved pressure is whether open-ended generative deception can retain the mechanical properties that made structured/procedural deception playable.

### Executable substrate note — Ashwick Trust / AI Murder Mystery Game
The public `DilanRG/ai-murder-mystery-v2` repository is unusually useful for experiments:
- engine-authoritative canonical truth;
- per-NPC private knowledge;
- finite authorized lies and truthful observations;
- `contradicts_fact_ids`;
- physically reachable evidence and validated independent solution routes;
- deterministic replay and detailed knowledge/action audits;
- provider-free fixtures and dummy-provider E2E tests.

Its current validator checks that lie references name canonical facts and that fact disclosures are permitted, while the overall case/evidence graph is checked for reachability and solvability. It does **not** currently make “every individual lie has a player-reachable refutation path” an obvious first-class invariant. This makes it a useful *workbench substrate*, not scientific prior by itself.


## 9. Industry evidence — deployment abstractions

Industry evidence is not scientific proof, but it is valuable for detecting which constraints survive contact with a real game.

### Ubisoft NEO NPC → Teammates
- NEO NPC started with authored characters whose backstory/personality are supplied by writers and whose dialogue is improvised.
- Teammates moves the concept into FPS-style co-play: voice instructions, action, tactical cooperation, personality.
- Deployment pressure shifts from conversation quality to **acting usefully while remaining a character**.

### NVIDIA ACE / PUBG Ally
- Public technical descriptions use a two-timescale hybrid:
  - **System 1:** traditional behavior tree handles fast/reflexive movement/combat.
  - **System 2:** small local language model handles deliberate reasoning, coordination and speech.
- Strong practical evidence that the production abstraction is often **LLM + conventional controller**, not one end-to-end language agent.
- On-device latency, VRAM, game vocabulary and interface grounding are first-class constraints.

### Production lesson
When a research benchmark lets the LLM own everything, ask whether it is studying the same boundary that a deployed NPC actually uses.

---

## 10. Cross-lineage pressure map

| Pressure | What the literature already establishes | What not to mistake for novelty |
|---|---|---|
| Persona | Rich role-playing is benchmarked extensively | “better persona prompt / judge score” |
| Memory | Retrieval, reflection, summarization and long-turn tests exist | “add long-term memory” |
| Grounding | KGs/ontologies/structured state and tool APIs help | “RAG for NPC lore” |
| Narrative consistency | Long-horizon commitment benchmarks now exist | another consistency benchmark without a changed object |
| Action | NPCs increasingly act via tools/policies/world models | adding tool calls by itself |
| Social behavior | beliefs/actions/non-verbal channels matter | transcript-only social evaluation |
| Openness | can help autonomy but also cognitive load/usability | “more open-ended = more immersive” |
| Hybrid control | symbolic/state/BT + LLM is common in strong systems | assuming one LLM should own every timescale |
| Evaluation | isolated response quality is insufficient | another generic LLM-as-judge score |
| World-model NPCs | autonomy/reactivity is now modeled explicitly | generic “make world model interactive” |

---

## 11. Open artifact map

| Artifact | What is actually public | Experimental value |
|---|---|---|
| microsoft/interactive-minecraft-npcs | runnable Minecraft/Codex prototype | historical action-grounded NPC baseline |
| microsoft/collaborative-quest-completion | human–NPC gameplay logs/recordings | real collaborative interaction evidence |
| Sony CPDC starter kit | task data, harness, vanilla baseline | cheap persona + function-call experimentation |
| CPDC Qwen3 multi-expert solution | code + 1.7B/14B LoRA weights | strong practical dialogue/tool baseline |
| NCP-Bench | structured narrative environments, prompts/code/data | long-horizon commitment evaluation |
| INV-WZQ/ReactiveGWM | inference + training + models + dataset | strongest open world-model NPC substrate |
| JunseoKim0103/Lies-We-Can-See | Docker game, VLM harness, logs, dataset, annotations | embodied social NPC/agent analysis with ablation axes |
| Project Sid | report/repo for large multi-agent Minecraft simulations | population-scale NPC/social experiments |
| Proact-VL | public code, incomplete model/data/training release when checked | promising but weaker reproducibility |
| WorldMind | paper/project; artifact not fully released when checked | frontier prior, not baseline yet |

---

## 12. Research-navigation lessons

### Lesson 1 — “NPC quality” is not a scalar
A system can improve persona and hurt task utility; improve autonomy and hurt usability; improve dialogue while breaking authoritative state; win socially through movement rather than speech.

### Lesson 2 — find the authority boundary
Many strong systems become clearer when asking:
> Which component is allowed to decide / write / validate each piece of state?

Useful state includes world facts, character knowledge, relationship state, quest progress, intentions, action plans, and low-level controls.

### Lesson 3 — behavior must be evaluated where it matters
A dialogue-only score does not establish co-play quality. A video-world-model metric does not establish strategic NPC behavior. A believable social transcript does not establish faithful social dynamics.

### Lesson 4 — “more LLM” is not an obvious direction
Slice of Life, PANGeA, NarrativeWorlds, CASCADE, and PUBG Ally all preserve non-LLM structure for parts of the system. Hybridization is often a response to authority, latency, or validity—not merely engineering conservatism.

### Lesson 5 — the useful direction should be selected **after** baseline residency
Do not choose a final NPC paper from this landscape. First identify a territory with:
- a strong public substrate;
- a stable failure/pressure not already reduced to a benchmark label;
- multiple informative perturbations;
- a realistic path from failure → bottleneck → controllable action.

## 13. Explicit anti-ideas

Do not register these as directions without a materially changed object:

- “NPC long-term memory”
- “RAG for game lore”
- “more consistent persona”
- “tool-using NPC”
- “open-ended dialogue”
- “LLM + behavior tree”
- “multi-agent NPC society”
- “world-model NPC”
- “evaluate NPCs with LLM judges”

Each is already a populated lineage or system pattern. The work is to discover **which dependency or boundary inside these systems is actually load-bearing**.
