# Startup & Hugging Face Genealogies 10 — Research Provenance, Streaming Correction, Persistent World State, and Failure-Onset Rollback — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues Startup/HF Genealogies 01–09.
>
> Recent-window focus:
> - Agora — Sep 16 2026
> - SURE-Map — Sep 14 2026
> - AlayaVista — Sep 13 2026
> - Taming Long-form TTS / LACI — Sep 15 2026
>
> Core observation:
>
> > **"Long horizon" is not one technical problem.**
>
> Recent systems fail for at least four structurally different reasons:
>
> 1. research knowledge disappears between independent workers;
> 2. small streaming errors accumulate into slow global drift;
> 3. local observations fail to represent off-screen persistent world state;
> 4. autoregressive generation enters a localized failure regime and then cascades.
>
> These require different state, different diagnostics, and different interventions.
>
> The correct question is never merely:
>
> > "How do we add memory / correction / long context?"
>
> It is:
>
> > **What quantity persists, what error accumulates, and where should intervention occur?**

---

# S101 — Collective research memory: transcript memory → claim/provenance DAG

Agora is one of the cleanest recent examples of redefining "memory" for research agents.

The basic problem is not:
> one agent forgets its conversation.

It is:
> separate research sessions repeatedly rediscover the same work because no durable public research state survives across workers.

---

## S101.1 Session-local memory is the wrong unit for a research community

A normal coding/research agent retains:
- conversation history;
- local worktree;
- temporary notes.

When the session ends:
- negative results disappear;
- abandoned branches disappear;
- reproduction status disappears;
- future workers reconstruct prior work from scratch.

Adding more workers can therefore increase:
> duplicated search

instead of:
> independent discovery.

This is a coordination-memory problem, not a context-length problem.

---

## S101.2 Agora changes the stored object from text history to scientific claims

Agora stores research as an append-only Git DAG.

Each contribution can be:
- result;
- negative result;
- insight;
- hypothesis;
- verification;
- report;
- work in progress.

Each node carries:
- immutable artifact;
- author;
- metric;
- tags;
- explicit parentage.

The parent edge means:
> "this contribution builds on that one."

### Primitive change

\`\`\`
memory = past conversation / notes
→ memory = typed claim + artifact + lineage + verification status.
\`\`\`

This is much closer to:
> a scientific institution

than to:
> chat memory.

---

## S101.3 Reproducibility becomes part of memory semantics

A memory item is not valuable merely because it exists.

Agora distinguishes:
- one worker's result;
- another account reproducing/building on it;
- failed verification;
- self-extension.

Evidence scores exclude self-citation and give high weight to independent verification.

The paper explicitly warns:
> the score is not truth.

It measures:
> how actionable / independently supported a contribution is.

### Research-taste lesson

A research memory should represent:
> **epistemic status**, not only content.

This is a more sophisticated object than ordinary agent memory.

---

## S101.4 Search diversity is a property of the memory interface

A single leaderboard creates monoculture.

Agora exposes:
- leaders;
- leaves;
- underexplored clusters;
- unverified claims;
- contested verification;
- open hypotheses;
- exploit / explore-known / explore-novel suggestions.

So memory does not merely answer:
> what happened?

It also shapes:
> what gets investigated next.

This means:

\`\`\`
research memory
→ attention-allocation mechanism.
\`\`\`

The interface to memory can alter the search distribution.

---

## S101.5 The 12-day run exposes both value and failure

In the reported weight-transfer run:
- 13 language-model workers;
- nearly 12 days;
- 1,703 contributions;
- 1,124 scored results;
- 165 verifications;
- frozen 119.6M target;
- 141 donor models;
- no training data / target gradient updates.

The best score improves from:
- 3.3923 bpb random initialization
to
- 1.899 bpb.

But the coordination trace is more interesting.

### Fast early exploitation
The first day's work captures roughly 98% of the total improvement.

### Search monoculture
Most subsequent work concentrates on one lineage.

### Parallel rediscovery
Many identical scores are independently rediscovered within hours.

### Human intervention
A mid-run visualization of concentration helps pull the community out of one basin.

This is valuable negative evidence:
> shared memory alone does not solve exploration collapse.

---

## S101.6 Agora explicitly does not claim causal discovery-efficiency gain yet

The paper proposes a matched comparison to test:
> whether the shared graph / analysis views improve discovery per unit compute.

That experiment is not yet the central established result.

This evidence discipline matters.

The sustained run demonstrates:
- feasibility;
- coordination dynamics;
- reproducible lineage.

It does not prove:
> Git-DAG memory is better than every alternative under matched budget.

### Taste lesson

A strong systems paper can state:
> what the trace demonstrates,
and separately:
> what causal comparison is still missing.

---

## S101.7 Artifact-value caveat

The public GitHub repository exposes:
- paper;
- project materials;
- contribution-graph description.

But the checked repo is not itself the full 12-day research history / production service deployment.

Thus:

- thesis value: HIGH;
- provenance-design value: HIGH;
- direct full-system reproduction value: currently lower.

Again:
> open repo badge ≠ full experimental artifact.

---

# S102 — Long-horizon streaming geometry: local uncertainty → slow global drift

SURE-Map is a useful counterexample to the generic belief:

> if each frame is predicted accurately enough, long-horizon reconstruction should remain accurate.

Streaming changes the error process.

---

## S102.1 Feed-forward streaming creates a state-estimation problem

Streaming geometric foundation models process limited recent context.

They are vulnerable to:
- dynamic objects;
- weak texture;
- local pose error;
- depth inconsistency.

A small local error changes the next inferred state.

Repeated errors accumulate.

Therefore:

\`\`\`
per-frame prediction error
→ state transition error
→ long-horizon trajectory drift.
\`\`\`

The final failure cannot be understood from one-frame confidence alone.

---

## S102.2 Conventional confidence measures the wrong object

Depth/point confidence typically asks:

> how reliable is this view's prediction?

SURE-Map instead defines cross-view geometric uncertainty:

> do predicted pose + depth induce geometrically consistent correspondences across views?

This changes the uncertainty unit from:

\`\`\`
single-view output confidence
\`\`\`

to:

\`\`\`
cross-view state-transition consistency.
\`\`\`

That is more directly aligned with streaming failure.

---

## S102.3 One correction timescale cannot solve both local error and drift

Local consecutive-frame optimization can:
- correct short-term translation;
- filter bad geometry.

But slowly accumulating scale error can survive local correction.

SURE-Map therefore uses:

### Fast loop
- consecutive-frame inference;
- uncertainty-weighted local correction.

### Slow loop
- sparse keyframe-window inference;
- longer-range geometric evidence;
- trajectory-scale recalibration.

### Primitive change

\`\`\`
self-correction = one feedback loop
→ self-correction = multiple loops matched to different error time constants.
\`\`\`

This is the key idea.

Not:
> "add a global module."

---

## S102.4 The expensive component is selective rather than continuous

Long-window inference is not run at every frame.

It is sparse.

This preserves streaming efficiency while allowing:
> low-frequency global recalibration.

The design mirrors a control principle:

> fast local loop handles high-frequency perturbations;
> slow loop handles accumulated low-frequency drift.

The analogy is useful because the error spectra are genuinely different.

---

## S102.5 The public artifact is comparatively strong

The repo currently provides:
- code;
- configuration;
- uncertainty checkpoint;
- training recipe;
- evaluation scripts;
- paper result targets;
- frozen geometric backbone integration.

Training the uncertainty head:
- freezes backbone;
- trains on TartanAir;
- uses 8–24-frame clips.

This is far more accessible than retraining a geometric FM.

### Instrument value
High for:
- uncertainty calibration;
- drift diagnostics;
- local/global correction ablation.

---

## S102.6 Cross-field transfer warning

It is tempting to generalize:

> all long-horizon systems need fast + slow correction.

Too broad.

The design is justified because:
- one error component is local;
- another accumulates slowly and becomes unidentifiable locally.

Any transfer must first show:
> two separable error timescales.

Otherwise "multi-timescale correction" is module stacking.

---

# S103 — Persistent world state: local observation history → global latent state

AlayaVista addresses a different long-horizon problem.

The problem is not primarily error correction.

It is:
> **partial observability under camera motion.**

---

## S103.1 Perspective video asks a local representation to remember an off-screen world

A perspective model only sees:
> current camera viewport.

As the camera moves:
- objects leave the frame;
- new areas appear;
- the model must preserve unseen scene content over long rollouts.

If the representation remains perspective-local, off-screen state must be stored implicitly through temporal history.

That becomes increasingly difficult.

---

## S103.2 A 360° latent state changes the basic world representation

AlayaVista starts from one perspective image, expands a panoramic prior, then evolves:

> a camera-conditioned 360° panoramic latent state.

A viewport renderer extracts:
> the requested local perspective latent.

A refiner restores:
- detail;
- local fidelity;
- super-resolution.

### Primitive change

\`\`\`
world state = sequence of perspective observations
→ world state = global panoramic latent
→ observation = selected rendering of that state.
\`\`\`

This is a state/observation factorization.

---

## S103.3 Persistent world and high-fidelity observation need not have identical representation

Global world state needs:
- broad coverage;
- persistence;
- consistency.

Perspective output needs:
- detail;
- high resolution;
- low artifact rate.

Forcing one representation to optimize both creates a trade-off.

AlayaVista separates:

### World evolution
panoramic latent.

### Observation synthesis
viewport rendering + local refinement.

This resembles classical state-space systems:

\`\`\`
latent state
→ observation model.
\`\`\`

But here the state is learned/generative and visually rich.

---

## S103.4 Streaming efficiency is recovered after the representation change

A panoramic state seems more expensive.

The system therefore adds:
- chunk-autoregressive generation;
- few-step distillation of panoramic generator;
- few-step perspective refinement.

This is an important genealogy pattern:

\`\`\`
representation fix solves persistence
→ creates compute pressure
→ distillation/streaming recovers efficiency.
\`\`\`

The efficiency modules are downstream of the state-factorization decision.

---

## S103.5 Data creation is a major execution trap

The paper constructs MUGEN:
- 1,318 hours;
- ≥4K panoramic video;
- semantic/geometric annotations.

This is a major resource component.

Thus:

- technical thesis value: HIGH;
- direct replication value: LOW;
- current artifact value: LOW/MEDIUM.

The checked GitHub roadmap says:
- paper/project page released;
- inference code/weights not yet released.

So this is inspiration-first, not pilot-first.

---

## S103.6 Relation to code/persistent-state world models

AlayaVista:
> persistent visual world state is panoramic latent.

Code World Model:
> persistent causal state is executable code.

Kairos:
> persistent world state is a learned multimodal/action representation.

These approaches compete over:
> **what representation should persist when observations are partial.**

The shared surface "world model" hides this central design choice.

---

# S104 — Long-form autoregressive failure: intervene at onset, not globally

LACI is one of the cleanest recent low-cost diagnosis→intervention papers.

The surface task is long-form TTS.

The general research move is more precise:

> catastrophic failure may be localized in onset even though its downstream damage is very long.

---

## S104.1 Short-form success hides a length-dependent phase transition

Open autoregressive TTS models such as:
- Qwen3-TTS;
- VoxCPM2

perform well on short inputs.

At long prompts/reference contexts they can:
- skip text;
- enter hallucinated repetitions;
- lose monotonic text/audio alignment;
- collapse speaker similarity.

The average short-form metric therefore hides:
> a rare but catastrophic tail regime.

---

## S104.2 The failure is detected through alignment dynamics

LACI monitors alignment behavior rather than waiting for final WER.

It tracks:
- which text region receives attention;
- coverage/progress;
- stalled reading;
- skipped regions.

This permits near-real-time detection of:
- skip onset;
- hallucination onset.

### Primitive change

\`\`\`
evaluate final generated sequence
→ monitor the internal alignment process for an onset event.
\`\`\`

This converts a terminal failure into a transition-detection problem.

---

## S104.3 Global constraint is not the right repair

One obvious response would be:
> force a hard monotonic attention mask for the whole generation.

But global constraints can damage generations that would otherwise be correct.

LACI instead:

1. detects failure;
2. rolls back to the onset;
3. changes random seed / retries;
4. temporarily applies a hard alignment guardrail;
5. removes the constraint after crossing the failure region.

### Primitive change

\`\`\`
global constrained decoding
→ localized temporary intervention around the failure basin.
\`\`\`

The method follows directly from the failure localization.

---

## S104.4 The rollback unit is the key research object

The system does not:
- restart the entire 1500-word synthesis;
- retrain the model;
- permanently change decoding.

It preserves all valid prefix work.

This matters because:

\`\`\`
failure damage length
≫
failure onset interval.
\`\`\`

The cost-effective repair is therefore:
> rewind only to the causal boundary.

This general pattern is potentially transferable only when such a boundary can be identified.

---

## S104.5 Reported gains are tail-risk gains, not just mean gains

On Qwen3-TTS-0.6B, the paper reports:
- worst-of-10-seed WER for >1500-word prompts: 35.2% → 3.4%;
- catastrophic WER >30% frequency under a long-reference condition: 26% → <1%;
- sliding-window speaker similarity improves strongly.

The paper also introduces wSIM because global SIM hides localized speaker failures.

### Important measurement lesson

If failure is local in time:
> a global aggregate metric can wash it out.

Thus:
> failure localization often requires a localized metric.

---

## S104.6 The method has a useful boundary

The reported method:
- works on Qwen3-TTS-0.6B;
- also helps larger Qwen3-TTS;
- is less complete in extreme VoxCPM2 long-form regimes according to the paper's reported discussion.

This is valuable.

The detector/guardrail cannot rescue:
> a base generator whose long-horizon coherence is fundamentally insufficient.

So:

\`\`\`
local repair
\neq
replacement for underlying capability.
\`\`\`

This defines a capability floor analogous to self-improving harnesses.

---

## S104.7 Artifact value is unusually high even without new training

Because the method is:
- inference-only;
- tested on open models;
- centered on 0.6B Qwen3-TTS;

the core phenomenon is comparatively cheap to reproduce.

This is exactly the kind of paper our project should value as a research-taste exemplar:

\`\`\`
large tail failure
→ local transition signal
→ targeted intervention
→ tail-risk evaluation
→ boundary.
\`\`\`

Not because it is TTS.

Because the causal chain is tight and inexpensive.

---

# S105 — Four distinct notions of "long-horizon state"

This batch lets us refine the vocabulary.

---

## 1. Epistemic/provenance state — Agora

Stores:
- what has been tried;
- what failed;
- what is verified;
- which claim builds on which.

Failure:
> duplicated search / monoculture / forgotten negative results.

---

## 2. Dynamical geometric state — SURE-Map

Stores:
- evolving camera/scene geometry.

Failure:
> local errors accumulate into global drift.

---

## 3. Persistent latent world state — AlayaVista

Stores:
- off-screen world content.

Failure:
> local observation sequence cannot stably carry broad scene persistence.

---

## 4. Autoregressive generation state — LACI

Stores:
- generated prefix + alignment trajectory.

Failure:
> a localized alignment error cascades into long future corruption.

---

## S105.1 "Memory" is therefore an invalid umbrella noun

These systems do not share:
- storage medium;
- update rule;
- timescale;
- error mode;
- retrieval mechanism;
- correction method.

Any future seed saying:
> "long-horizon memory"

must specify the exact state type first.

---

# S106 — New general distinction: persistent-state design vs correction design

A long-horizon failure can arise because:

### A. The representation does not preserve the needed state
Example:
- perspective world model loses off-screen state.

Then the likely intervention is:
> change state representation.

### B. The state representation is adequate but local updates accumulate error
Example:
- streaming geometry drifts.

Then:
> periodic recalibration / correction.

### C. The state is adequate until a localized transition enters a bad basin
Example:
- TTS alignment collapse.

Then:
> detect onset + rollback.

### D. The information exists but is not shared among workers
Example:
- research sessions repeat work.

Then:
> provenance/public-state mechanism.

These are mutually different failure diagnoses.

---

# S107 — Failure-Onset Localization Gate

A new rule should enter the canonical search guide.

When a final failure occurs late in a trajectory:

Do not immediately intervene on:
- every step;
- the whole sequence;
- all tokens;
- the entire model.

First ask:

1. When does the future outcome become predictably bad?
2. What observable changes at that onset?
3. Does the bad state persist/cascade after onset?
4. Can valid prefix work be preserved?
5. Is intervention only needed near the transition?
6. Does a global intervention harm normal cases?
7. Does the base model have enough capability to recover after rollback?

If:
> the causal boundary is local,

then a localized intervention may be more principled and cheaper than global regularization.

This rule is not TTS-specific.

But it only applies when onset is empirically identifiable.

---

# S108 — Multi-Timescale Correction Gate

Before adding fast/slow modules, require evidence for distinct error time constants.

Strong case:
- fast local noise/pose errors;
- slow accumulated scale drift.

Weak case:
> "short-term and long-term are both important."

Required audit:

1. estimate error growth over horizon;
2. show local correction leaves a residual low-frequency failure;
3. show long-window/global correction is unnecessary at every step;
4. match correction frequency to the measured error spectrum;
5. report cost vs correction frequency.

Without this:
> fast/slow architecture is likely story-driven module stacking.

---

# S109 — Research Memory Provenance Gate

For multi-agent/research-memory systems, memory quality is not judged only by recall.

The memory should ideally expose:

- artifact;
- claim;
- parent lineage;
- negative-result status;
- independent verification;
- conflict;
- open branch;
- provenance;
- reproducibility.

And it should be audited for:

### Duplication
Do workers still rediscover the same experiment?

### Monoculture
Does visibility of leaders collapse exploration?

### False consensus
Do many dependent descendants look like independent evidence?

### Verification independence
Are confirmations from genuinely independent runs/accounts?

### Attention allocation
Does the memory interface change what workers choose to explore?

This is a different evaluation regime from conversational memory benchmarks.

---

# S110 — Artifact / execution audit

## Agora
Thesis value: **A**
Evidence value: **A-**
Direct platform artifact: **B/C at checked repo**
Important caveat:
> paper explicitly says matched causal comparison for shared-state discovery efficiency remains open.

## SURE-Map
Thesis value: **A**
Instrument value: **A**
Execution transfer: **A/B**
Why:
- code;
- uncertainty checkpoint;
- frozen backbone;
- explicit training/eval scripts.

## AlayaVista
Thesis value: **A**
Instrument value: **C currently**
Execution transfer: **D/F**
Why:
- code/weights roadmap not yet complete;
- 1,318h high-res panoramic dataset is a major resource barrier.

## LACI
Thesis value: **A+**
Instrument value: **A**
Execution transfer: **A**
Why:
- inference-only;
- open 0.6B/1.7B TTS models;
- no foundation pretraining required;
- clear tail-risk metric.

---

# S111 — Current conclusion

This batch reinforces a deeper rule:

> **Do not classify long-horizon papers by the length of the task. Classify them by the dynamics of failure.**

A long trajectory can fail because:
- knowledge is not shared;
- state is not persistent;
- errors integrate over time;
- a local transition enters a bad basin;
- the correction signal is too local or too delayed.

Those imply fundamentally different research objects.

The useful reading sequence is:

\`\`\`
late failure
→ locate state that should persist
→ characterize error accumulation
→ identify onset / timescale / missing state
→ derive smallest intervention
→ verify that intervention acts only where diagnosis predicts.
\`\`\`

This remains literature calibration, not a topic menu.
