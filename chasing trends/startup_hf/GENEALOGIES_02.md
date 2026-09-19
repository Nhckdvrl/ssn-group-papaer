# Startup & Hugging Face Genealogies 02 — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues STARTUP_HF_GENEALOGIES_01_2026-09-19.md.
>
> Main emphasis:
>
> 1. how large industrial/open models use cheap proxy regimes internally before full-scale commitment;
> 2. how domain-specific foundation models redefine the basic computational object;
> 3. how robotics/world-model startups disagree about what pretraining is actually for;
> 4. how public artifacts can turn otherwise-inaccessible training questions into low-cost diagnostics.

---

# S11 — Full-scale model development often contains its own cheap-proxy science

A common mistake when reading industrial technical reports is:

> final model used enormous compute
> → every useful claim in the paper requires enormous compute.

This is often false.

Strong industrial reports frequently reveal an internal two-level methodology:

cheap proxy regime
→ screen design hypotheses
→ full-scale confirmation.

For a small lab, the key object to copy is the proxy-validation bridge, not the final training run.

---

## S11.1 ZGCM-1 makes the proxy ladder unusually explicit

ZGCM-1 is a 7B open model whose repository exposes:
- pretraining code;
- data processing;
- midtraining;
- SFT;
- RL;
- stage descriptions;
- configs;
- intermediate artifacts.

Its final production training is large.

But the report/repository itself shows that key decisions were not all selected at production scale.

Examples include:
- roughly 0.3B-scale proxy runs for data-mixture exploration;
- smaller-token-budget experiments for architecture/attention choices;
- then scale-up only after the cheap regime identifies plausible choices.

This changes how we should read large-model papers.

The real methodology is often:

hypothesis
→ tiny proxy
→ medium sanity check
→ expensive confirmation.

Not:

idea
→ immediately train the final model.

---

## S11.2 ZGCM midtraining turns long-context growth into staged interventions

The released midtraining schedule expands context:

16K
→ 64K
→ 256K

over separate stages.

Interaction traces are reformulated as MDP state-action transitions alongside code, math, reasoning, knowledge and instruction data.

The important artifact is not merely 256K context.

It is:
> explicit boundaries where context regime and data semantics change.

These boundaries can serve as cheap observation points.

Again, they are not automatically causal stages.

But they make it possible to ask:
- what changes locally when the context regime expands?
- which effects persist after the next stage?
- which are just transient optimization artifacts?

without reproducing pretraining.

---

## S11.3 ZGCM RL publishes concrete selection logic, not only final reward

The RL stage publicly specifies:
- domain-specific rewards;
- group filtering;
- dynamic sampling;
- a correct-only length penalty;
- response-group size;
- maximum generation/context lengths.

One especially useful distinction:

length penalty is applied only to correct answers.

Thus:

efficiency pressure
is conditioned on
task success.

This is different from globally punishing long reasoning.

It reflects an important design principle:

> do not optimize cost before preserving success.

The exact recipe is not a novelty generator.

The value is that the public configuration exposes the training objective at enough resolution to study it.

---

# S12 — Open training pipelines can preserve intermediate failures, not only successful checkpoints

Instella-MoE is unusually useful because its public pipeline keeps the failure that motivated the final repair.

---

## S12.1 Pipeline

The public model flow includes:

pretraining
→ midtraining
→ long-context extension
→ SFT
→ DPO
→ instruction-following RL
→ multi-teacher on-policy distillation.

This is already more scientifically useful than a single final checkpoint.

But the key point is the explicit specialization failure.

---

## S12.2 IF-RL improves one capability and hurts another

The Instella repository states:

> instruction-following RL improves instruction following but regresses mathematical/reasoning capabilities.

This is a real local failure.

The final method is motivated by it.

So the paper's structure is not:

new distillation method
→ benchmark gains.

It is:

specialization objective
→ targeted capability improves
→ other capability regresses
→ use two teachers with different roles
→ recover a broader capability profile.

This is exactly the kind of method genealogy we want to learn from.

---

## S12.3 MOPD preserves two different behavioral anchors

Instella uses:
- an IF-RL teacher for instruction-following prompts;
- the earlier DPO checkpoint as a general-capability anchor.

The student generates on-policy rollouts.

Teacher routing depends on prompt domain.

Thus the repair is not simply:
> regularize toward the old model.

It says:

different task regions
need different reference policies.

Primitive change:

one global anchor
→ domain-conditioned anchors.

This is a much sharper object.

---

## S12.4 Why this artifact is useful to us

We do not need to reproduce 7.1T-token pretraining.

Potentially useful experiments can begin from released stages:
- DPO checkpoint;
- IF-RL expert;
- final MOPD model;
- data mixture definitions;
- teacher-routing code.

This creates a natural three-point observational contrast:

before specialization
→ specialized but damaged
→ repaired multi-teacher model.

Any formal study would still need controlled interventions.

But the phenomenon-discovery cost is low.

---

# S13 — Tabular foundation models are converging on synthetic SCM priors, but disagree on the computation unit

Recent EXAONE Tabular, Mitra-v2 and Xiaomi-TabLDM releases are especially useful because they share one high-level training paradigm while making different architectural bets.

That lets us distinguish:

shared paradigm
from
actual scientific disagreement.

---

## S13.1 Shared parent: synthetic tasks as a prior over learning problems

Modern tabular foundation models are not merely trained on a giant collection of real tables.

Many are pretrained on synthetic episodes generated from:
- causal graphs;
- random functions;
- synthetic feature/target mechanisms;
- task distributions.

The model learns an in-context prediction procedure.

At test time:
- labeled rows are context;
- predictions are made without dataset-specific gradient updates.

So synthetic data is not mainly augmentation.

It specifies:

> a prior over possible supervised-learning worlds.

This is much closer to meta-learning / Bayesian prior construction than ordinary synthetic data.

---

## S13.2 EXAONE Tabular challenges the row-compression boundary

A common architecture factorizes tabular ICL as:

features within row
→ compress row to embedding
→ learn across rows.

EXAONE argues that this one-time boundary is too lossy.

Its CAST architecture repeatedly alternates:
- feature-axis interaction within an item;
- support-conditioned item-axis interaction for each feature.

Item-summary and feature-summary tokens exchange information without fully collapsing the cell structure.

Primitive change:

row = atomic token after initial compression
→ cell/feature structure remains active throughout depth.

This is a basic-object change.

Not a new attention name.

---

## S13.3 The scientific claim is about iterative cross-axis refinement

The interesting hypothesis is:

> feature semantics should be refined using evidence from other rows, and row-level representations should in turn be refined using feature interactions, repeatedly across layers.

If correct, a staged architecture creates an artificial information bottleneck.

This resembles other fields where:
- local/global structure;
- spatial/temporal structure;
- token/channel structure

must repeatedly exchange information instead of being collapsed once.

But cross-domain transfer must preserve the actual relation, not the word "interleaved."

---

## S13.4 Mitra-v2 shows that scale is not the only path inside the same paradigm

Mitra-v2 remains small:
- about 77M parameters.

It expands:
- synthetic pretraining diversity;
- context length;
- feature-space capacity;
- optimization quality.

It reaches performance comparable to much larger tabular foundation models on reported benchmarks.

The useful lesson is not:
> 77M beats 1.6B.

The lesson is:

> in a domain where the pretraining prior is synthetic and highly structured, expanding task-distribution diversity can matter as much as raw parameter scaling.

This is an alternative growth axis.

---

## S13.5 Xiaomi-TabLDM introduces test-time compute into tabular ICL

Xiaomi-TabLDM combines:
- SCM synthetic pretraining;
- dual-stream feature grouping;
- lightweight attention residual;
- sparse MoE;
- a three-stage recipe.

The especially interesting new direction is:
> test-time compute scaling for tabular prediction.

Tabular prediction is usually framed as:
- fit once;
- predict once.

A foundation model changes this.

If additional inference computation can systematically improve a fixed prediction task, then tabular ICL starts to acquire:
> an inference-resource dimension.

This is conceptually surprising because there is no natural "reasoning chain" in the ordinary LLM sense.

So the next scientific question is not:
> can tabular models think longer?

It is:
> what computation is being refined when test-time budget increases?

That mechanism remains the more interesting object.

---

# S14 — Time-series foundation models can make intermediate checkpoints part of the training objective

Tabby is a 145M model, but its research value is mostly in the recipe.

---

## S14.1 The paper explicitly argues architecture is not the whole story

Tabby cites recent evidence that a generic patch Transformer with a good recipe can match specialized architectures.

It therefore focuses on:
- data;
- sampling;
- masking;
- LR schedule;
- checkpoint structure;
- intermediate supervision.

This is a valuable contrast to architecture-first research.

---

## S14.2 Progressive Convergence Schedule makes checkpoints intentional

Conventional cosine decay assumes a known final horizon.

Intermediate checkpoints may be:
- high-learning-rate;
- not locally converged;
- hard to compare.

Tabby instead uses repeated stable→decay stages.

Each stage ends in a locally converged checkpoint.

Primitive change:

checkpoint = accidental snapshot of one global schedule
→ checkpoint = deliberate intervention point.

This makes:
- evaluation;
- reconfiguration;
- data-mixture changes;
- continuation

much more interpretable.

This is closely aligned with our practical need for cheap pilot points.

---

## S14.3 Deep Quantile Supervision turns layer depth into a progressive prediction path

Tabby observes prior evidence that intermediate TSFM layers can be redundant.

Instead of only supervising the final layer, it attaches shared quantile decoding to selected intermediate exits.

Intermediate predictions are regularized toward a trajectory between the initial and final prediction.

Thus depth is interpreted as:
> progressive refinement of a probabilistic forecast.

This is not merely "deep supervision improves training."

The architectural hypothesis is:

layers should correspond to
a smooth refinement path in prediction space.

That is a testable representation/computation claim.

---

## S14.4 Synthetic SCMs are used as a structural prior over temporal worlds

CauKerV2 composes:
- trend/seasonality;
- ARIMA;
- regime-switching SDEs;
- change points;
- spikes;
- fractional Brownian motion;
- GARCH-like volatility;
- chaotic processes;
- other temporal generators

through randomly sampled SCMs.

The point is not realistic synthetic examples one by one.

It is:
> expose the model to a broad prior over temporal mechanisms.

This parallels tabular PFN-style synthetic pretraining, but with a different scientific object:
> temporal process families rather than static feature-target graphs.

---

# S15 — Robotics pretraining value is being redefined

Skild and Physical Intelligence expose a surprisingly important disagreement.

The question is no longer simply:

> does robot pretraining improve finetuning?

---

## S15.1 Skild S1 challenges the standard value proposition of pretraining

Skild argues:

If downstream task data becomes sufficiently dense,
a specialist trained from scratch can approach a post-trained foundation model.

If true, then:

"pretraining helps downstream finetuning"
is not a sufficient justification for expensive foundation pretraining.

Skild proposes a stricter criterion:

> pretraining should enable in-context learning of a new task from one/few demonstrations without weight updates.

This is analogous to the BERT→GPT-era shift they explicitly invoke.

Primitive change:

foundation model value = better initialization
→ foundation model value = new adaptation mode.

---

## S15.2 S1 uses demonstration video as the task specification

The task is not primarily specified by:
- a task ID;
- a finetuning dataset;
- a fixed instruction label.

The prompt contains:
> a video demonstration.

The model must infer:
- demonstrator intent;
- functional correspondences;
- progress;
- embodiment mapping.

So "task representation" itself changes.

This creates a robotics analogue of:
> in-context task inference.

---

## S15.3 Physical Intelligence develops a different adaptation decomposition

Physical Intelligence's 2026 work separately targets:

### Multi-scale memory
- short-term detailed visual memory;
- long-term textual/task memory;
- active choice of what to retain.

### RL Token
- compress VLA internal representations;
- freeze the large VLA;
- run sample-efficient online RL in a small actor/critic.

### π0.7 steerability/compositional generalization
- diverse conditioning;
- language;
- metadata;
- visual subgoals;
- cross-embodiment/task recombination.

This gives at least three distinct adaptation channels:

memory adaptation
online policy adaptation
in-context compositional steering.

---

## S15.4 RL Token is particularly clean conceptually

The problem:
> precise manipulation needs rapid online improvement,
but updating the full VLA on-robot is impractical.

Physical Intelligence learns a compact RL token that reconstructs/summarizes the VLA's internal representation.

Small actor/critic networks then operate on that token.

Primitive change:

online RL state = raw high-dimensional VLA internals / observations
→ learned bottleneck state extracted from the foundation model.

This resembles:
> freezing a large representation and adapting a small control head.

But the key scientific issue is:
> what information must the bottleneck preserve for rapid policy improvement?

That is sharper than generic parameter-efficient RL.

---

# S16 — "World model" is fragmenting by downstream contract

The recent world-model explosion becomes much clearer when papers are organized by what the downstream consumer needs.

World Labs' functional taxonomy is useful here.

---

## S16.1 Renderer contract

Output:
> visually plausible observations.

Primary metric:
- perceptual realism;
- visual coherence.

A renderer can be visually excellent and still be wrong for:
- policy evaluation;
- physical interaction;
- geometry.

---

## S16.2 Simulator contract

Output:
> state transitions faithful enough that another program/agent can act on them.

Primary metric:
- action-faithful dynamics;
- structural consistency;
- policy ranking;
- counterfactual reliability.

This is a much stronger contract than visual realism.

---

## S16.3 Planner contract

Output:
> actions.

Primary metric:
- task success;
- control/generalization.

Recent "World-Action Models" intentionally blur simulator and planner.

But the contract remains essential.

---

# S17 — World-model papers are beginning to ask which property is actually load-bearing

This is where GigaWorld, OpenWAM, Pelican-Sim, SolarWM and World Labs become scientifically useful.

---

## S17.1 GigaWorld-1: short-term visual realism is not the main evaluator property

GigaWorld studies world models specifically for robot policy evaluation.

The core finding:

> long-horizon action-faithful consistency matters more than short-term visual realism for ranking/assessing policies.

This is a clean changed objective.

A world model optimized for:
> pretty next frames

can be a bad policy evaluator.

Therefore:
> downstream contract determines which model errors matter.

---

## S17.2 OpenWAM: monolithic WAMs hide the design question

OpenWAM argues existing WAMs entangle:
- generative backbone;
- visual representation;
- architecture;
- world/action information flow;
- inference;
- data.

That makes it hard to know why a WAM works.

The project explicitly factorizes the design space and asks three questions in sequence:

1. What should be inherited from the world/video model?
2. How should world and action learning interact?
3. How does that synergy scale?

This is exactly the "do the science before the flagship model" pattern.

---

## S17.3 OpenWAM findings change the default explanation

Their controlled study reports:

### Upstream world knowledge
Transfers best through:
- a sufficiently capable video/generative backbone;
- compact, information-rich latent representation.

### World-action synergy
Needs:
- dedicated action capacity;
- explicit world→action information flow;
- synchronized joint denoising.

### Embodied pretraining
Mainly helps:
> out-of-domain generalization,

rather than simply improving all in-domain tasks uniformly.

This last point is especially important.

It changes the purpose of embodied pretraining:

better average policy
→ broader distributional support.

---

## S17.4 Pelican-Sim: action representation is treated as the bridge between embodiments

Pelican-Sim uses:
- a unified 28-D action-value representation;
- URDF/camera-rendered action videos;
- sparse MoE;
- causal/few-step distillation.

The most interesting component is action-visual injection.

Instead of forcing numerical actions directly into a video model,
it renders actions into a visual form aligned with the model's pretrained modality.

Primitive change:

action conditioning = append numbers/tokens
→ translate action into the modality where the backbone already has inductive strength.

This is a representation/interface thesis.

---

## S17.5 Pelican-Sim also shows why MoE can mean modality isolation, not only capacity

The report attributes improvement partly to sparse experts absorbing heterogeneous dynamics/action information while reducing inter-modality conflict.

So MoE's role is not only:
> larger capacity for same compute.

It can be:
> isolate heterogeneous dynamical subproblems.

This is similar in spirit to acoustic/semantic interference in speech,
but the mechanism/evidence is different.

---

## S17.6 SolarWM: backbone diversity itself is a reproducibility problem

SolarWM starts from a different bottleneck:

world-model results are hard to compare because:
- datasets differ;
- camera geometry differs;
- video backbones have different representations/objectives;
- model-specific pipelines entangle everything.

It builds:
- a unified data contract;
- shared training/inference interfaces;
- while preserving each backbone's native representation/objective.

This is subtle.

They do not force all backbones into one representation.

They normalize:
> the experimental interface,
not
> the internal model.

This can enable fairer cross-backbone science.

---

## S17.7 SolarWM's training horizon vs rollout horizon is another changed premise

SolarWM trains on short clips but supports very long autoregressive interactive rollouts through:
- bidirectional adaptation;
- teacher-forced autoregressive initialization;
- self-gradient/distribution-matching style distillation;
- sliding-window rollout.

The underlying problem is:

training sequence horizon
≪
deployment rollout horizon.

This is a general sequential-model pressure.

It appears in:
- agents;
- video;
- robotics;
- recurrent world models.

But each domain has different state-error dynamics.

---

# S18 — BlueLM-GUI: deployment closes the training/evaluation loop

BlueLM-GUI is expensive to reproduce, but scientifically clear.

It begins from three industrial failures:

1. sandbox→production distribution shift;
2. expensive real-device failures are discarded;
3. static benchmarks saturate and stop guiding development.

The entire system follows from those failures.

---

## S18.1 Every Sample Matters

Instead of using only successful trajectories,
the pipeline attempts to salvage failures through:
- consensus evaluation;
- error correction;
- trajectory derivation.

Primitive change:

failed rollout = waste
→ failed rollout = potentially recoverable supervision.

This resembles failure replay in other agents,
but here it is integrated with real-device collection.

---

## S18.2 Every Rollout Is Real

RL runs on hundreds of real phones.

The goal is specifically to remove:
> sandbox/production mismatch.

This is strong industrial evidence that simulator convenience can create a deployment gap large enough to justify expensive real-device RL.

For us this is mostly a resource warning.

---

## S18.3 Every Query Evolves

The benchmark itself is continuously upgraded as the model improves.

This challenges:

benchmark = fixed ruler.

In deployment-driven iteration:

benchmark
→ diagnostic instrument that must evolve when it saturates.

This is dangerous academically because a moving benchmark can make comparison unstable.

But it reflects a real industrial need:
> a saturated benchmark provides near-zero gradient for engineering decisions.

---

## S18.4 Transferable abstraction

We cannot reproduce hundreds of phones.

The useful question is:

> when a benchmark stops separating plausible next-system variants, what property should evolve while preserving comparability?

That is a measurement-design question,
not a reason to build another benchmark.

---

# S19 — Audio generation now contains two opposing unification strategies

Recent StepAudio 3 Gen and AuK are useful because both pursue broad audio capability but choose different generative abstractions.

---

## S19.1 StepAudio 3 Gen: unified discrete autoregressive audio timeline

StepAudio 3 Gen supports:
- TTS;
- voice design;
- vocals;
- SFX;
- music;
- mixed audio scenes.

It uses a discrete autoregressive formulation over shared RVQ tokens.

The design thesis is:

> general audio can be organized as one discrete event/timeline prediction problem.

This is notable because much recent audio generation relies heavily on diffusion/flow families.

---

## S19.2 AuK: generation and editing are one instruction-conditioned conditional-generation problem

AuK unifies:
- generation;
- content editing;
- enhancement/separation;
- paralinguistic editing;
- acoustic editing.

It uses:
- semantic conditioning via multimodal LM;
- joint VAE over speech/general audio/music;
- hybrid rectified-flow Transformer;
- generation-only warm-up then joint generation/editing training;
- preference optimization and reward-based RL;
- distillation to four-step inference.

Its central object is:

audio generation/editing
→ one natural-language-instruction + audio-context interface.

---

## S19.3 Same "unified audio" label, different thesis

StepAudio:
> unify audio types under a discrete autoregressive timeline.

AuK:
> unify operations under a conditional editing/generation interface.

These are not one lineage.

The basic object differs:
- token sequence over sound events;
- conditional transformation over audio context.

This is exactly why "unified multimodal/audio model" is scientifically empty without asking what is unified.

---

# S20 — The strongest open artifacts increasingly expose a "research ladder"

Across ZGCM, Instella, Ling, Tabby, OpenWAM, SolarWM, MiniCPM and others, the best artifacts repeatedly expose multiple rungs:

tiny proxy
→ intermediate checkpoint
→ mechanism-faithful larger model
→ final system.

This matters enough to become a formal reading criterion.

---

## S20.1 Research ladder fields

For each technical report/model card, record:

### Hypothesis rung
What cheap experiment first motivated the choice?

### Scale rung
At what size/token budget was it first tested?

### Transfer rung
Was the effect verified at a second size/regime?

### Production rung
Was it used in the flagship model?

### Artifact rung
Which checkpoints/configs remain public?

### Boundary rung
Where did the hypothesis fail or require repair?

A model release with all six is disproportionately useful.

---

## S20.2 Why this matters for our project selection

A research idea can be intellectually strong but unusable if:

> its first meaningful observation only appears after a 500B-token run.

Conversely, a trillion-model technical report can still be useful if:

> the authors demonstrate the key effect at 300M parameters / 10B tokens and then confirm it at scale.

The decisive quantity is therefore:

> **minimum scale of causal visibility.**

Not:
> final model size.

---

# S21 — New execution gate: Proxy Fidelity

When we reuse an industry's small proxy regime, we must test whether the proxy preserves the causal structure.

A cheap proxy is good only if the authors show evidence such as:

- ranking of methods survives scale;
- effect direction survives scale;
- mechanism metric behaves similarly;
- downstream improvement survives scale;
- known boundary moves predictably.

Bad proxy:
> only cheaper and convenient.

Good proxy:
> preserves the decision-relevant ordering/relationship.

Therefore future candidate design should include:

### Proxy Fidelity Audit
1. what full-scale quantity is the proxy supposed to predict?
2. did the source paper show proxy→scale transfer?
3. is our target intervention on the same causal path?
4. could the proxy reverse method ranking?
5. what is the smallest second-scale confirmation needed?

---

# S22 — Current strongest startup/HF research-taste examples from this batch

Not rankings of papers.

These are examples of distinct question-forming moves.

### ZGCM
Big training question
→ deliberately small proxy experiments
→ scale only selected hypotheses.

### Instella
Specialize one capability
→ observe damage elsewhere
→ domain-conditioned multi-teacher repair.

### EXAONE Tabular
Question the row-compression boundary
→ retain cross-axis structure throughout depth.

### Tabby
Make intermediate checkpoint convergence and intermediate-layer prediction explicit training objects.

### Skild S1
Question whether pretraining's value should be "better finetuning"
→ demand a new adaptation mode: in-context robot learning.

### Physical Intelligence RLT
Do not adapt the full VLA online
→ learn an RL-sufficient bottleneck for a small controller.

### GigaWorld/OpenWAM
Do not equate pretty futures with useful world models
→ define downstream simulator/action contracts and factorize the design space.

### BlueLM-GUI
Do not treat deployment as the end of the pipeline
→ deployment failures and benchmark saturation feed the next training/eval cycle.

---

# S23 — Current anti-patterns strengthened by this scan

## Anti-pattern 1
"Company X scaled this to 500B, therefore we need 500B."

Wrong if the key hypothesis was selected at 0.3B.

## Anti-pattern 2
"Open checkpoint stages let us study training dynamics."

Only if the target phenomenon is local/stable enough and confounds are explicit.

## Anti-pattern 3
"World model quality = video quality."

False for policy evaluation/control.

## Anti-pattern 4
"Pretraining helps because finetuning needs less data."

Potentially too weak in robotics; some labs now demand qualitatively new adaptation behavior.

## Anti-pattern 5
"Synthetic data is one category."

SCM pretraining can encode a prior over tasks/processes rather than merely augment examples.

## Anti-pattern 6
"Test-time scaling means reasoning tokens."

Tabular models can expose test-time compute without language reasoning.

So the true object is:
> iterative/refined computation under additional inference budget.

---

# S24 — What this changes in future search

Before rejecting an idea for compute:

1. inspect the flagship report's own ablations;
2. find the smallest proxy size used to choose the design;
3. check whether that proxy ranking survived scale;
4. search HF for matched checkpoints;
5. search for tiny/mechanism-faithful derivatives;
6. use full-scale model only as external validity.

Before accepting an idea because an industrial report is impressive:

1. strip away final model scale;
2. identify the exact changed assumption;
3. identify what was actually controlled;
4. ask whether the cheap proxy is faithful;
5. ask whether academic nearest prior already answers the relation.

The goal is not to imitate industrial scale.

It is:

> **steal the experimental decomposition that let industrial teams spend their scale intelligently.**
