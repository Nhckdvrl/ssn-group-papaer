# Startup & Hugging Face Genealogies 04 — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues STARTUP_HF_GENEALOGIES_01/02/03.
>
> This batch focuses on:
>
> 1. realtime systems where the real issue is **multiple time scales**, not a scalar latency number;
> 2. world models whose usefulness is defined by **decision fidelity**, not visual similarity;
> 3. adversarial failure discovery as a data-generation mechanism;
> 4. the distinction between a **strong research thesis** and a merely useful open deployment/compression artifact.

---

# S35 — "Realtime" decomposes into multiple clocks

A large fraction of recent voice/world-model releases advertise:
> realtime.

That word now has almost zero scientific specificity.

The deeper question is:

> **what state changes on what clock, and which clocks must remain synchronized?**

Recent systems expose several fundamentally different answers.

---

## S35.1 Inworld TTS-2: TTS output depends on the conversational acoustic past

Traditional TTS receives:

text
+ optional speaker/style control
→ audio.

Even high-quality expressive TTS often treats each utterance as a largely independent synthesis problem.

Inworld TTS-2 makes a different product/model claim:

> the model conditions on the actual audio of prior conversation turns, not just their transcript.

So the same text can be rendered differently depending on:
- prior tone;
- pacing;
- hesitation;
- emotional state;
- conversational momentum.

Primitive change:

\`\`\`
TTS = text-conditioned rendering
→ TTS = conversation-conditioned acoustic continuation
\`\`\`

The model's generation state is no longer reset at a sentence boundary.

---

## S35.2 This turns paralinguistic history into model state

The model must preserve information that a transcript discards.

Examples:
- how tense the previous speaker sounded;
- whether a joke just landed;
- whether speech was hesitant;
- pacing / energy / affect.

Thus:

\`\`\`
conversation history = words
\`\`\`

is replaced by:

\`\`\`
conversation history = semantic + acoustic interaction state.
\`\`\`

This is a clean changed premise.

It does not require full duplexity.

A turn-based system can still have continuous acoustic state across turns.

---

## S35.3 Natural-language voice direction changes control semantics

TTS-2 also exposes style control through natural-language directions rather than only fixed emotion labels.

This turns:

\`\`\`
style = categorical control code
→ style = language-conditioned behavior
\`\`\`

The interesting scientific question is not:
> prompt TTS with words.

It is:
> whether language becomes a sufficiently compositional interface over prosodic/acoustic generation.

The public source does not provide enough mechanistic evidence to make this a taste anchor by itself.

It is a deployment pressure.

---

# S36 — Full-duplex tool use introduces a second output clock

NVIDIA NemotronLabs VoiceChat provides a useful open sibling to DuplexSLA and GPT-Live.

---

## S36.1 One unified voice model, but tool calls have a separate output channel

VoiceChat uses:
- streaming speech encoder;
- Nemotron backbone;
- text/audio generation path;
- separate output channel for tool-call scripts.

So the model can simultaneously participate in a spoken interaction while also emitting structured actions.

Primitive change:

\`\`\`
assistant output = one speech/text stream
→ assistant output = conversational stream + action/script stream
\`\`\`

This is not identical to ordinary function calling.

The two output products obey different temporal/semantic contracts.

---

## S36.2 Tool latency is hidden through conversational continuation

The model card describes configurable "on-hold" messages spoken when a tool is triggered, while the external tool runs.

This is an important realtime systems move:

\`\`\`
tool call
→ silence until result
\`\`\`

becomes:

\`\`\`
tool call
→ conversational state continues while external computation is pending.
\`\`\`

So tool execution latency becomes something the dialogue policy can mask.

This is related to MoshiRAG's asynchronous retrieval, but the delayed resource differs:

- MoshiRAG: retrieval evidence;
- VoiceChat: arbitrary tool result.

The common structure is:

> exploit conversational slack to perform slower cognition/action asynchronously.

---

## S36.3 Tool-call accuracy and interaction quality become coupled objectives

A standard tool benchmark can optimize:
- tool choice;
- argument correctness.

A realtime spoken assistant must also optimize:
- interruption behavior;
- no awkward silence;
- when to announce action;
- what to say before result;
- when to resume factual response.

Thus:

\`\`\`
correct function call
≠
good realtime tool interaction.
\`\`\`

This is one reason static BFCL-style evaluation is insufficient as the only metric.

---

## S36.4 Open artifact value

VoiceChat is unusually useful because it releases:
- ~11B checkpoint;
- model/training config;
- tool-call protocol;
- full-duplex examples;
- data summary;
- inference path.

Training from scratch is impossible for us.

But inference-level experiments on:
- tool timing;
- action/speech interference;
- context protocol;
- interruption

are relatively accessible.

---

# S37 — Multimodal realtime world models are multirate dynamical systems

Odyssey Starchild-1 makes this explicit.

---

## S37.1 Visual causal rollout already has a compounding-error problem

An interactive video world model repeatedly consumes its own generated history.

Thus:

\`\`\`
small state error_t
→ future conditioning error
→ larger state error_{t+k}.
\`\`\`

This is already harder than offline bidirectional video generation.

---

## S37.2 Adding audio does not merely add another modality

Starchild-1 argues that audio and video differ in:
- temporal frequency;
- information density;
- spatial/temporal structure;
- error propagation behavior.

Therefore forcing both through one synchronous cache/update schedule can be poorly matched.

This is a real basic-object change:

\`\`\`
multimodal generation = aligned modalities on one token clock
→ multimodal world = coupled processes with different clocks.
\`\`\`

---

## S37.3 Standard video distillation fails under cross-modal asymmetry

The Starchild technical report explicitly states that video-only causal-distillation strategies are insufficient for joint audio-video causal generation.

The reason is not only:
> more modalities are harder.

It is:
> the teacher's bidirectional multimodal representation must be converted into a causal student while preserving synchronization between dynamics that evolve at different rates.

This makes the distillation problem itself multimodal-dynamical.

---

## S37.4 Asynchronous KV cache is derived from the temporal mismatch

Starchild introduces an asynchronous KV-cache / rollout-adaptation design tailored to the differing spatiotemporal properties of audio and video.

This is a good example of:

failure property
→ systems representation.

The cache is not asynchronous because asynchronous systems are fashionable.

It is asynchronous because:
> the modalities do not naturally advance under identical state-update schedules.

---

## S37.5 The evaluation regime also changes

Short offline video metrics do not fully capture:
- long causal rollout;
- multimodal error coupling;
- mid-rollout steering;
- persistent synchronization;
- state recovery after user intervention.

So:

\`\`\`
offline clip quality
→ interactive long-horizon dynamical stability.
\`\`\`

This is analogous to full-duplex speech, but the state object is a simulated world.

---

# S38 — Multiplayer world models introduce shared hidden state

MIRA provides another distinct world-model pressure.

---

## S38.1 Single-agent interactive world models have one observer/action stream

A single player:
- observes one view;
- supplies actions;
- model predicts next world observation.

Even if the state is partially observed, the interaction topology is simple.

---

## S38.2 MIRA must maintain one world across four action/observation streams

MIRA models 2v2 Rocket League.

Its data contains:
- synchronized observations for all four players;
- each player's actions;
- game state.

The model generates a coherent multiplayer future at 20 FPS.

Primitive change:

\`\`\`
world state for one observer
→ shared latent world state consistent across multiple observers and action streams.
\`\`\`

This introduces constraints absent from single-agent video:
- one player's action must affect all views consistently;
- agents can lose sight of each other;
- hidden world events must remain consistent;
- different views cannot drift into different realities.

---

## S38.3 Representation autoencoder is not only a compression device

MIRA combines:
- a video representation autoencoder;
- a latent diffusion world model.

The representation must preserve:
> the aspects of state necessary for interactive prediction across multiple viewpoints.

This makes codec quality downstream-dependent.

A codec optimized only for:
> reconstructive perceptual fidelity

may discard state variables needed for:
> action-faithful dynamics.

This is a recurring world-model lesson.

---

## S38.4 Synthetic game environments are used as a scientific instrument

The project explicitly argues Rocket League is not the end application.

Advantages:
- exact actions;
- game state;
- synchronized multi-view data;
- huge controllable data generation;
- no unsafe physical collection.

Thus the game serves as:

> a controlled instrument for studying world-model dynamics before physical AI.

This is the right role for synthetic environment work.

Not:
> synthetic game benchmark as contribution.

---

# S39 — World-model fidelity → decision fidelity

World Labs makes one of the strongest recent industrial reframings of simulator evaluation.

---

## S39.1 Renderer/simulator/planner are different contracts

World Labs' functional taxonomy distinguishes:

### Renderer
Outputs observations/pixels.
Contract:
> visual plausibility.

### Simulator
Outputs/maintains structural world state.
Contract:
> geometry/physics/dynamics faithful enough for downstream computation.

### Planner
Outputs actions.
Contract:
> task success / action quality.

The word "world model" hides these different output contracts.

---

## S39.2 R2S2R sharpens simulator fidelity further

In robot development, a simulation does not necessarily need:

\`\`\`
sim success rate = real success rate
\`\`\`

point by point.

It needs to support the same **engineering decisions**.

World Labs explicitly frames useful simulation as one that can:
- rank which policy is better;
- track checkpoint improvement/plateau;
- identify similar success/failure regions;
- predict which changes will transfer to hardware.

This gives a stronger operational quantity:

\`\`\`
state/pixel fidelity
→ decision fidelity.
\`\`\`

---

## S39.3 Decision fidelity is task-relative

A simulation can have:
- imperfect texture;
- imperfect absolute success probability;

yet still be useful if:
> the relative policy ordering and failure boundary are preserved.

Conversely a photorealistic simulator can be useless if:
> policy ranking reverses.

This is an extremely important evaluation lesson.

The correct metric depends on the simulator's downstream use.

---

## S39.4 This connects directly to Proxy Fidelity

Our earlier Proxy Fidelity rule said:

> a cheap proxy is useful if it preserves decision-relevant ordering/relationships at full scale.

World Labs' simulator criterion is structurally the same:

> a simulation is useful if it preserves decision-relevant ordering/relationships in reality.

This is a cross-domain mathematical structure worth retaining.

Not a method transfer.

---

# S40 — Failure discovery can become an active policy

Odyssey PROWL-1 moves beyond passive dataset scaling.

---

## S40.1 Static world-model training waits for failures to appear

Standard training:
- collect trajectories;
- fit world model;
- hope rare failure regions are represented.

If a failure is rare,
random data scaling can waste most compute on already-solved states.

---

## S40.2 PROWL makes failure discovery an RL objective

An RL explorer interacts with the true/game environment.

Its objective is to find trajectories where the world model fails:
- geometry;
- motion;
- action-following;
- temporal consistency;
- state persistence.

The discovered trajectory then becomes training data for the world model.

Primitive change:

\`\`\`
data collection = sample environment distribution
→ data collection = optimize for model regret/failure.
\`\`\`

---

## S40.3 The explorer is constrained to realistic behavior

An unconstrained adversary could discover:
> bizarre out-of-distribution exploits that do not matter.

PROWL therefore keeps exploration near realistic behavior.

This creates a genuine tension:

\`\`\`
informativeness
vs
distributional relevance.
\`\`\`

The best data are:
> hard for the model but still meaningful under the target environment.

This is much sharper than generic hard-example mining.

---

## S40.4 PAT buffer changes curriculum state from difficulty to unresolved model failure

As the world model learns a failure,
that trajectory should stop consuming most of the training budget.

The Prioritized Adversarial Trajectory buffer deprioritizes solved failures and promotes unresolved ones.

Thus:

\`\`\`
curriculum = hard examples
→ curriculum = currently unresolved model-regret regions.
\`\`\`

This is closely related in structure to DiagEvo failure memory.

But the object differs:
- DiagEvo: reasoning error causes;
- PROWL: dynamical-world-model failure trajectories.

---

## S40.5 World model and data collector co-evolve

The loop is:

\`\`\`
world model improves
→ previous adversary becomes less informative
→ explorer must find new failures
→ new failures improve world model.
\`\`\`

This is a genuine coupled-learning system.

The scientific challenge is not merely:
> active data collection works.

It is:
> whether the failure search remains informative rather than exploitative as both systems change.

---

# S41 — Conversation-conditioned TTS vs full-duplex SpeechLM: same user experience, different model boundary

Inworld TTS-2 and NVIDIA VoiceChat are an important contrast.

---

## S41.1 Inworld keeps a modular pipeline but preserves richer cross-module state

Inworld's product stack contains:
- STT / user profiling;
- model/router;
- TTS.

But unlike a traditional text-only handoff,
TTS receives:
- prior audio context;
- user acoustic/emotional state;
- conversation history.

So modularity is retained while information loss at boundaries is reduced.

---

## S41.2 NVIDIA collapses the speech loop into one end-to-end model

VoiceChat instead integrates:
- streaming understanding;
- LLM;
- speech generation

in one full-duplex model.

A separate action/tool channel remains.

These represent two competing architectural philosophies:

### Rich modular interfaces
Keep components separate, but pass richer state.

### Unified model
Collapse the boundary and learn end-to-end interaction.

---

## S41.3 This is the real research comparison

Not:

> modular bad, end-to-end good.

The question is:

> **which information should cross module boundaries, and which computation benefits from joint training?**

Inworld suggests:
> preserving acoustic conversational state may recover some advantages without full end-to-end unification.

VoiceChat suggests:
> turn-taking and speech generation benefit from joint realtime modeling.

This is an actual competing-abstraction genealogy.

---

# S42 — Some trending HF models are instruments, not research-thesis sources

The recent HF scan provides good contrast cases.

---

## S42.1 Audio8 TTS 0.6B

Useful properties:
- 0.6B model;
- DualAR architecture;
- full 44.1kHz codec;
- zero-shot voice cloning;
- 11 languages;
- complete checkpoint/code;
- separate CPU-oriented INT4 ONNX release.

But:
> DualAR is explicitly inspired by Fish Audio's prior design.

The current model card does not present a new scientific explanation.

Therefore:

### Technical-thesis value
B-/C+

### Instrument value
A

Why?
Because we have:
- compact BF model;
- compact INT4 pair;
- local CPU runtime;
- open codec.

This is ideal for cheap studies of:
- quantization behavior;
- codec/model interface;
- local TTS latency/quality.

It is not automatically a positive taste anchor.

---

## S42.2 DeepGrove Maple Preview

Useful properties:
- 20B total / 1B active;
- 256 experts, 8 active;
- ternary weights;
- 3:1 local/global attention;
- 5.31GB checkpoint;
- >200 tok/s claimed on Mac Mini M4;
- minimal general RL / weak agent post-training.

The technical thesis is:
> design a reasoning model for local inference from the beginning.

But the current public card has little:
- controlled ablation;
- training detail;
- failure diagnosis.

Therefore:

### Thesis value
B-

### Deployment pressure value
A-

### Instrument value
B

Monitor it.
Do not build research taste from benchmark claims.

---

## S42.3 Syzygy Mach-1 Additive

Useful artifact:
- very low-bit/additive/trellis-coded representation of a Qwen-family MoE;
- explicit decode implementation;
- compression manifest;
- full-precision retention table;
- local GGUF runtime.

But the public release currently emphasizes:
- codec format;
- retention;
- systems implementation

rather than a controlled scientific argument.

Thus:

### Compression artifact value
A

### Scientific-thesis value
C/B-

It may become more valuable if a report exposes:
- why the trellis/additive representation was selected;
- failure modes of simpler quantizers;
- which structures require high-precision side streams.

For now:
> do not retroactively invent a mechanism from the codec.

---

# S43 — Artifact transparency and scientific explanation are orthogonal

This batch strengthens a key distinction.

A release can be:

### Highly transparent, weak thesis
Example:
- open compressed model, decoder, benchmark table.

### Strong thesis, weak artifact
Example:
- closed world model with a clear changed abstraction.

### Strong on both
Example:
- matched controlled checkpoints + report explaining failure and repair.

We should score these separately.

---

# S44 — Updated four-axis artifact score

Future startup/HF scans should record:

## 1. Thesis Value
Does it change a real assumption/basic object?

## 2. Failure-Provenance Value
Does it expose what failed and why?

## 3. Instrument Value
Does it release a usable matched experiment?

## 4. Proxy-Fidelity Evidence
Does it show that cheap proxy findings transfer to larger/deployed regime?

The ideal source is high on all four.

But different sources can play different roles.

---

# S45 — Current cross-domain principle: state is increasingly multirate and consumer-relative

Recent strong examples:

### Conversation audio
Long-lived acoustic state crosses utterances.

### Full-duplex tool use
Speech state and tool-action state evolve on different clocks.

### Audio-video world model
Modalities have different temporal rates.

### Multiplayer world model
Multiple observers/actions share hidden state.

### Simulator
Useful state depends on downstream policy decisions.

### Robot memory
Short visual memory and long semantic memory have different abstraction/time scales.

This is not a topic generator.

It is a reading lens:

> **When a system contains multiple kinds of state, ask whether forcing them into one uniform token/time/memory representation creates the observed bottleneck.**

Only use it when the target literature contains independent evidence of such a bottleneck.

---

# S46 — Current conclusion

The newest startup/open-lab work is making two older simplifications increasingly unsafe:

### Simplification 1
"Realtime = low latency."

More accurate:
> realtime systems are coupled processes with different clocks and deadlines.

### Simplification 2
"World-model fidelity = how accurate the generated world looks."

More accurate:
> fidelity is defined by the downstream decision contract.

Together they produce a broader research-taste rule:

> **The useful representation of state is determined jointly by its dynamics and by the consumer that must act on it.**

Still no formal candidate generation.
