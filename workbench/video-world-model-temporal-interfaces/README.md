# Video World Model Temporal Interfaces — Workbench

**Status: exploratory workbench — not a candidate.**

This workbench studies how modern video generators and interactive/world models represent, compress, align, and transmit **time** across their major interfaces.

The motivating literature contains several related pressures:
- video tokenizers / VAEs often compress multiple raw frames into one latent step;
- controllable world models may receive actions, camera motion, contacts, or state changes at a finer rate than their latent video stream;
- causalization, streaming inference, few-step distillation, and long rollout can change what temporal information remains available;
- some recent systems respond by changing temporal compression, preserving higher-rate control signals, or adding separate fine-timescale pathways.

These facts justify studying the territory. They do **not** establish that temporal compression is the bottleneck, that a phase effect exists, or that any particular interface needs a new method.

## Execution ownership

The default executor of this workbench is the **local research agent**.

Once the territory is admitted to `workbench/`, the agent should not behave like a consultant that proposes one experiment and waits for a human to choose the next step. It should carry the research loop forward autonomously:

> reproduce → inspect → perturb → analyze → search nearest prior → update the working explanation → choose the next highest-information experiment → repeat

The agent is expected to:
- read papers, repositories, issues, appendices, and current code rather than rely on summaries;
- clone and run strong baselines;
- diagnose implementation details;
- design and execute the next experiment itself;
- use failures as gradients rather than stopping after one null result;
- continuously check whether an emerging observation is already owned by prior work;
- strengthen or replace the working question when evidence changes;
- keep the repository state current with code, results, and concise conclusions;
- continue until either a genuinely defensible novel problem/idea emerges or the territory is exhausted enough to archive/kill.

Human input is for occasional taste calibration, resource constraints, or new insight—not per-experiment approval.

## Research target

The purpose of exploration is not exploration for its own sake.

The workbench should actively search for a **real, reproducible, novel research object** that can eventually crystallize into a candidate. A useful endpoint may be:
- a previously unrecognized failure/bottleneck in a strong baseline;
- a surprising dependency exposed by a simple perturbation;
- a mistaken assumption shared by current methods;
- a representation/interface limitation with downstream consequence;
- a strong-baseline result that invalidates part of an existing narrative;
- a minimal intervention that becomes natural only after the bottleneck is established.

Novelty must be checked against current nearest prior continuously, not only after a result looks good.

The agent should not stop merely because the initial temporal-compression intuition fails. It should use that failure to redirect within the broader temporal-interface territory, unless accumulated evidence shows the territory itself is no longer promising.

## Baseline residency

Begin from strong open artifacts rather than from a new architecture.

The first task is to become fluent in a small set of practical video/world-model stacks that fit a single node. Candidate families include:
- open causal video VAEs / tokenizers;
- Wan-style open video generation stacks;
- small/open interactive or action-conditioned world models;
- models with explicit camera/action conditioning and published inference code;
- where useful, paired teacher / causal / distilled checkpoints from the same lineage.

Before proposing a research claim:
- reproduce the strongest practical baseline we can run;
- map the exact temporal interfaces in code: raw FPS, latent stride, first-frame handling, padding, causal context, action grouping, camera conditioning, rollout chunking, and any distillation/streaming conversion;
- record quality, controllability, latency, memory, and failure slices;
- distinguish tokenizer artifacts from downstream model behavior.

No foundation-model pretraining is required or authorized at the beginning.

## Exploration space

The workbench should explore several axes and let the important object emerge from experiments.

Potential axes include:
- **temporal representation:** what information changes when time is compressed or tokenized differently;
- **alignment:** how frames, latents, actions, camera trajectories, and state transitions are synchronized;
- **causality / streaming:** what changes when a bidirectional or teacher-forced system becomes causal or online;
- **control resolution:** whether coarse latent steps and fine-grained control signals interact cleanly;
- **event timescale:** whether short events, contacts, reversals, or fast motion behave differently from slow dynamics;
- **boundary / phase effects:** whether temporal chunk boundaries matter after strong implementation controls;
- **stage effects:** tokenizer vs generator vs causalization vs distillation vs rollout;
- **compensation:** whether a downstream model repairs information losses visible at an earlier stage;
- **efficiency tradeoffs:** which temporal simplifications actually buy useful speed and which silently remove control-relevant information.

“Temporal control bandwidth” is therefore one **possible diagnostic lens**, not the registered paper question.

## Research discipline

Do not:
- assume a phase/bandwidth phenomenon before measuring it;
- build the workbench around one synthetic pulse experiment;
- train a new video foundation model to make the question exist;
- turn the project into a generic long-video-memory, action-following, or VAE leaderboard;
- propose a module/loss before a stable bottleneck survives strong baselines;
- protect the initial temporal-compression story if another interface becomes more load-bearing.

Prefer:
- frozen-model diagnostics first;
- matched comparisons within the same model lineage;
- small perturbations that reveal hidden dependencies;
- failures that change which interface should be studied next;
- lightweight adapters / conditioning changes only after an actionable bottleneck is established.

## Compute boundary

The workbench must remain practical on one node:
- up to 4×A100 80GB, or
- up to 4×RTX PRO 6000 96GB.

The two available nodes cannot be assumed to communicate.

Therefore:
- VAE/tokenizer analysis and frozen inference are preferred early;
- repeated sweeps should favor roughly 1B–5B open backbones when possible;
- small LoRA / adapter / conditioning experiments are acceptable;
- multi-node foundation-model pretraining is out of scope.

## What would justify promotion

Remain exploratory until the workbench produces a simpler scientific object than the one we started with.

Promotion would require something like:
- a reproducible temporal/interface dependency that survives a strong baseline;
- evidence that it is not merely one implementation bug or one model family;
- a clear downstream consequence or changed understanding;
- a nearest-prior boundary that cannot be compressed into “already known”;
- a realistic confirmation path under the single-node compute budget.

It is fully acceptable for this workbench to end as a negative result or a reusable map of temporal interfaces.

## Starting literature / artifact audit

Before running substantial experiments, re-verify the latest primary papers, code, checkpoint availability, and exact licenses for candidate baselines. In particular, audit recent work on:
- causal / temporally compressed video VAEs;
- open video generation stacks;
- action- and camera-conditioned world models;
- causal / streaming / few-step world-model conversion;
- adaptive temporal tokenization or frame-rate allocation;
- embodied video tokenizers.

Do not treat any one of these lineages as the final paper identity.
