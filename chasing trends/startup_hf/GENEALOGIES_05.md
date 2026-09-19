# Startup & Hugging Face Genealogies 05 — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues STARTUP_HF_GENEALOGIES_01–04.
>
> Main theme:
>
> > **"More test-time compute" is not a scientific primitive.**
>
> Extra compute can implement very different operators:
> - fitting/tuning an in-context predictor;
> - counterfactual search before an irreversible action;
> - iterative generative transport;
> - repeated sampling/ensembling;
> - progressive representation refinement.
>
> Other systems instead move the needed cross-variable computation directly into the architecture and retain single-pass inference.
>
> Therefore the correct question is never only:
>
> > "Does test-time scaling help?"
>
> It is:
>
> > **What computation is being repeated/refined/searched, why does the task require that operator, and what error becomes cheaper to avoid by spending additional compute?**

---

# S47 — Tabular foundation models: synthetic prior → in-context predictor → fit-time computation

TabPFN is one of the cleanest counterexamples to the idea that "thinking" means language reasoning.

---

## S47.1 Parent idea: pretrain an inference algorithm, not a predictor for one dataset

TabPFN is pretrained exclusively on synthetic prediction problems sampled from a prior over tabular tasks.

The conceptual object is:

\`\`\`
one dataset → fit task-specific model
\`\`\`

replaced by:

\`\`\`
sample many possible data-generating tasks
→ train one network to perform inference on a new dataset in context.
\`\`\`

The prior is therefore expressed in:
> function/task space,

rather than only as a parameter prior for one downstream estimator.

This is why synthetic data here is not ordinary augmentation.

The synthetic generator defines:
> what kinds of prediction worlds the foundation model expects.

---

## S47.2 TabPFN-3: a single forward pass is already an inference algorithm

TabPFN-3's May 2026 report emphasizes that:
- synthetic-only pretraining;
- one forward pass;
- no real-data pretraining;
- no downstream gradient fit

can already compete with heavily tuned classical/AutoML systems.

The important changed abstraction is:

\`\`\`
forward pass = prediction
\`\`\`

becomes:

\`\`\`
forward pass = amortized fitting/inference over the provided table.
\`\`\`

The model's context is effectively the downstream training set.

---

## S47.3 TabPFN-3 introduces test-time compute without chain-of-thought

The report then adds TabPFN-3-Plus / Thinking.

This is crucial:

> "Thinking" here is not a hidden textual reasoning trace.

The service spends more compute during fit-time to explore/configure a better predictor for the table.

After fit:
> the resulting predictor is reused for ordinary prediction.

So the compute semantics are:

\`\`\`
extra compute
→ improve the fitted in-context predictor
→ amortize over many future predictions.
\`\`\`

This differs fundamentally from:
- longer CoT per query;
- best-of-N per query;
- tree search per query.

---

## S47.4 TabPFN-3.5 makes the inference-compute control explicit

September 2026 TabPFN-3.5 exposes:
- base model;
- smaller/faster 3.5-Fast;
- Plus;
- Thinking.

Thinking exposes:
- medium/high effort;
- timeout budget;
- task metric such as accuracy/log-loss/ROC-AUC/RMSE/MAE;
- grouping/time structure in relevant modes.

Thus the extra compute is not one universal "reasoning effort."

It is:
> **metric-conditional fit-time optimization.**

This is closer to:
- learned AutoML;
- configuration search;
- predictor composition

than language reasoning.

---

## S47.5 Architecture still matters: test-time compute did not replace a better base model

The 3.5 release also changes the base architecture.

Public repository documentation describes:
- distribution embedding;
- row-wise attention;
- cross-row attention;
- per-row readout.

The base/fast variants improve the one-pass predictor before Thinking is added.

This is an important lesson:

\`\`\`
better architecture
and
more test-time compute
\`\`\`

are not substitutes.

A stronger base changes:
- what each unit of additional compute can do;
- where the compute frontier starts.

---

## S47.6 TabPFN-3.5 expands the definition of "tabular"

The new model explicitly targets:
- temporal/grouped non-i.i.d. splits;
- high-cardinality categoricals;
- text/string/image features;
- wide tables;
- relational harnesses;
- time-series harnesses.

So the frontier is moving from:
> flat iid numeric table

toward:
> structured prediction problems presented through a tabular interface.

This will make the boundary between:
- architecture;
- harness;
- data representation

increasingly important.

---

## S47.7 Artifact value

Public:
- TabPFN-3.5 base weights;
- 3.5-Fast;
- source code;
- local GPU inference.

Hosted/proprietary:
- some Plus/Thinking capabilities/inference optimizations.

Therefore:

### Thesis value
A

### Instrument value
A for base-vs-fast / architecture analysis;
B/C for exact Thinking mechanism because part of the stack is hosted/proprietary.

Important rule:
> do not claim we can reproduce TabPFN Thinking internals just because base weights are open.

---

# S48 — Test-time compute in robotics: spend computation before irreversible action

τ₀-VLA provides a very different reason for test-time compute.

---

## S48.1 Parent failure: one high-level mistake is expensive after execution

Hierarchical robot policies often produce a high-level subtask with one forward pass.

Examples:
- open fridge;
- pick object;
- move to shelf.

If the high-level decision is wrong:
- low-level control may execute for seconds/minutes;
- the world changes;
- failure may be irreversible;
- recovery can be expensive.

So uncertainty is asymmetric.

A wrong token in text can be revised.

A wrong robot subtask can move the physical world.

---

## S48.2 Therefore compute is allocated before commitment

τ₀-VLA's high-level policy can take a fast route when confidence is sufficient.

Otherwise it invokes test-time computation.

The reported procedure is roughly:

1. proposal model samples candidate subtasks;
2. world model predicts visual consequences;
3. value model evaluates imagined outcomes;
4. beam search expands promising branches;
5. reflection commits to a final subtask.

Primitive:

\`\`\`
generate next subtask
→ act
\`\`\`

becomes:

\`\`\`
generate alternatives
→ imagine consequences
→ evaluate
→ commit
→ act.
\`\`\`

This is counterfactual decision search.

---

## S48.3 The trigger is decision risk, not "hard question length"

The adaptive router uses model confidence signals and calibrated thresholds to decide whether search is needed.

The important quantity is:

> **expected value of avoiding a bad commitment.**

This is why robotics provides a principled reason for adaptive compute.

Extra inference compute is justified when:

\`\`\`
search cost
<
expected cost of an incorrect irreversible action.
\`\`\`

This is more informative than generic:
> difficult inputs deserve more tokens.

---

## S48.4 World model is useful because the policy needs consequence prediction

The world model is not primarily there to generate pretty video.

Its consumer is:
> a high-level action search policy.

Therefore the relevant world-model error is:
> whether candidate actions are ranked/evaluated correctly enough before execution.

This connects directly to World Labs' decision-fidelity framing and GigaWorld's policy-evaluation contract.

---

## S48.5 Execution memory is part of the planning state

The high-level policy maintains execution memory:
- what has already happened;
- previous subtask;
- current observation;
- branch-local search memories.

This matters because long-horizon robot planning is not a fresh query every step.

Search must distinguish:
- persistent real execution state;
- hypothetical branch state.

That separation prevents imagined branches from overwriting actual task progress.

---

## S48.6 The open-source boundary is asymmetric

The public τ₀-VLA release currently provides:
- low-level policy checkpoint;
- Qwen3.5-2B VLA backbone;
- MoT action expert;
- unified 40-D state/action representation;
- example AgiBot post-training recipe;
- deployment/evaluation code.

The most distinctive high-level TTC components:
- proposal/reflection;
- world model;
- value model

are not all in the initial public checkpoint release.

Thus:

### Thesis value
A

### Instrument value
B/C for the full TTC thesis;
A/B for low-level cross-embodiment post-training.

This is a good warning:

> "open-source VLA" does not imply every scientifically central component is open.

---

# S49 — Extra compute outside language reveals the true abstraction: an operator, not "reasoning"

Across TabPFN and τ₀-VLA:

### TabPFN
Extra compute:
> optimize/configure a predictor for a fixed dataset.

### τ₀-VLA
Extra compute:
> search over possible future actions/world states before commitment.

Neither is:
> write a longer explanation.

Thus the common structure is only:

\`\`\`
allocate more computation at inference.
\`\`\`

That is too weak to form a research family.

The actual object is the repeated operator.

---

## S49.1 A useful taxonomy of test-time operators

### Predictor construction
Example:
- TabPFN Thinking.

Question:
> can more fitting/configuration compute improve a reusable predictor?

### Search / counterfactual evaluation
Example:
- τ₀-VLA.

Question:
> can more branching/imagination reduce decision error before action?

### Sample aggregation
Example:
- self-consistency / ensembles.

Question:
> can independent samples reduce estimator uncertainty?

### Progressive generative transport
Example:
- diffusion/flow sampling.

Question:
> can repeated denoising/integration improve fidelity?

### Iterative state refinement
Example:
- recurrent/looped/latent-depth models.

Question:
> can one state be progressively transformed toward a solution?

### Active information acquisition
Example:
- agentic video.

Question:
> which additional observation should be purchased?

These mechanisms have different:
- marginal returns;
- stopping criteria;
- failure modes;
- compute accounting.

---

## S49.2 "Adaptive compute" should therefore pass an Operator Identity Test

Any future paper using adaptive/test-time compute must answer:

1. What state is refined/searched?
2. What operator is repeated?
3. What evidence improves after each repetition?
4. What uncertainty/risk tells us to stop?
5. Why is the repeated operator better than putting equivalent compute into the base model?
6. Is the compute amortized across predictions or paid per decision?
7. Does the operator change the environment?

If these cannot be answered:
> "adaptive compute" is only a label.

---

# S50 — TimesFM-3 is the opposite lesson: put cross-variable computation into the forward pass

TimesFM-3 is a useful contrast because it adds capability without adding an iterative inference loop.

---

## S50.1 Parent limitation: TimesFM through 2.5 is univariate

Older TimesFM versions treat each series largely independently.

Real forecasting often depends on:
- correlated targets;
- related product/sensor series;
- past-only covariates;
- future-known covariates such as calendar/weather/promotion signals.

So the previous computational boundary is:

\`\`\`
one time series
→ one forecast.
\`\`\`

---

## S50.2 TimesFM-3 makes multivariate dependence native

The 330M model is pretrained for:
- multivariate targets;
- past-only covariates;
- past-and-future covariates.

Official evaluation code explicitly enables:
> cross-variate attention.

Thus:

\`\`\`
cross-series information = external preprocessing / separate model logic
→ cross-series information = native model computation.
\`\`\`

---

## S50.3 The system deliberately retains single-forward forecasting

Google emphasizes:
> the forecast is produced in one forward pass.

That is a useful anti-trend.

Not every richer inference problem should be converted into:
- iterative reasoning;
- search;
- tool loop.

Sometimes the right research move is:

> redefine the architecture/input contract so the interaction happens directly.

---

## S50.4 Forecasting contrasts with Tabby

Tabby uses:
- 145M model;
- deep/intermediate quantile supervision;
- staged convergence schedule;
- synthetic temporal SCM prior.

Its hypothesis interprets network depth as:
> progressive refinement of the forecast.

TimesFM-3 instead emphasizes:
> native multivariate dependency handling at inference in one pass.

So even inside time-series FMs we already have distinct computational theses:

### Tabby
What should happen across depth?

### TimesFM-3
What information should jointly interact within the prediction?

These should not be merged into:
> "time-series foundation models."

---

## S50.5 TimesFM-3 is a strong small research instrument

Public:
- 330M checkpoint;
- PyTorch implementation;
- MLX implementation;
- official benchmark runners;
- univariate vs multivariate modes;
- optional covariates;
- cross-variate attention switch/evaluation path.

This creates cheap contrasts:
- same weights, univariate vs multivariate;
- with/without covariates;
- cross-variate structure;
- series count/chunking.

These are dramatically cheaper than training a frontier LLM.

Again, formal novelty would need independent audit.

But artifact value is high.

---

# S51 — Audio foundation models disagree on what should be unified

AuK and StepAudio 3 Gen are both "general audio/speech models."

Their basic objects are very different.

---

## S51.1 AuK unifies tasks through an instruction-conditioned transformation interface

AuK supports:
- speech generation;
- content editing;
- enhancement/separation;
- paralinguistic editing;
- acoustic editing.

Every task is represented as:

\`\`\`
natural-language instruction
+ optional source/reference audio
→ target audio.
\`\`\`

The model combines:
- multimodal language model for semantic conditioning;
- joint VAE over speech/general audio/music;
- hybrid rectified-flow Transformer.

Primitive:

\`\`\`
many speech systems with task-specific interfaces
→ one conditional audio transformation interface.
\`\`\`

The unification object is:
> task interface.

---

## S51.2 AuK's training curriculum reflects asymmetric task difficulty

Training starts with:
> generation-only warm-up.

Then moves to:
> joint generation + editing pretraining.

Post-training differs by task:
- human-feedback preference optimization for open-ended editing;
- reward-based RL for speech generation.

This is important.

A unified model does **not** imply:
> all tasks should share one training signal.

The interface is unified,
while optimization remains task-structured.

---

## S51.3 AuK-Flash exposes a second failure: one fast sampler does not naturally preserve every task

The full AuK uses iterative rectified-flow sampling plus CFG.

AuK-Flash targets:
- four steps;
- no CFG.

The project uses:
1. trajectory-level consistency initialization;
2. task-routed Decoupled DMD;
3. special clean-prediction regression for separation.

The presence of task routing in distillation is informative:

> accelerating a unified model can reintroduce task-specific failure modes.

So:

\`\`\`
one model / one interface
\`\`\`

does not guarantee:
\`\`\`
one distillation dynamic.
\`\`\`

---

## S51.4 The public artifact is unusually useful

AuK publishes:
- base checkpoint;
- 4-step Flash checkpoint;
- code;
- fine-tuning implementation;
- intermediate checkpoint saving;
- EMA;
- per-noise-time validation curves;
- sample synthesis;
- one common ChatML-style data interface.

The public fine-tuning path freezes:
- Qwen2.5-Omni encoder;
- VAE;

and updates:
- generation backbone;
- conditioning/fusion.

This yields a relatively clean experimental boundary.

### Instrument value
A.

---

# S52 — StepAudio 3 Gen unifies audio at the representation/generative-operator level

StepAudio's unification thesis is different.

---

## S52.1 It rejects the dominant continuous-diffusion default

Recent general-audio systems often use:
> continuous latent + diffusion/flow Transformer.

StepAudio 3 Gen instead models:
> discrete RVQ audio tokens autoregressively.

The tokenizer operates at:
- 12.5 Hz;
- 16 residual codebooks;
- 2048 codes per layer.

Crucially each layer is designed to preserve both:
- semantic;
- waveform/acoustic

information.

Primitive:

\`\`\`
general audio = continuous denoising problem
→ general audio = discrete hierarchical sequence prediction.
\`\`\`

---

## S52.2 Two axes of autoregression are separated

Generation is factorized:

### Time axis
The backbone predicts the first codebook across time.

### Codebook axis
A lightweight causal Transformer completes the remaining residual codebooks.

So a high-dimensional audio token is not emitted monolithically.

It is:

\`\`\`
temporal semantic/coarse progression
→ residual acoustic completion.
\`\`\`

This is an explicit factorization of the generation object.

---

## S52.3 The most scientifically useful finding is interference, not the discrete codec itself

Adding massive audio-generation supervision to a pretrained LLM can damage:
- language;
- reasoning;
- coding;
- text understanding.

StepAudio explicitly treats this as a training problem.

The progressive curriculum includes stages such as:
- modality alignment while core language components are frozen;
- audio understanding with mixed text;
- detached generation where residual-code gradients do not immediately reshape the LLM hidden state;
- later deeper joint integration.

The paper reports better preservation of text benchmarks under the interference-aware curriculum than a simpler baseline.

Thus:

\`\`\`
new modality capability
vs
old backbone capability
\`\`\`

is a plasticity/interference trade-off.

---

## S52.4 This connects to Lychee-FD and Instella, but the mechanisms differ

### Instella
Specialized IF-RL hurts math/reasoning.
Repair:
> domain-conditioned teachers.

### Lychee-FD
Acoustic and semantic objectives conflict in deep shared parameters.
Repair:
> hierarchical parameter separation.

### StepAudio
High-volume audio-generation learning perturbs pretrained language capability.
Repair:
> progressive freezing/detachment/mixing.

Surface:
> "capability preservation."

Underlying mechanisms:
- objective specialization;
- gradient conflict;
- modality-volume/interference.

They are siblings, not one method family.

---

# S53 — Audio generation also shows that "fast inference" is task-dependent compression

AuK and StepAudio expose two different answers to fast generation.

### AuK
Full model:
> iterative flow.

Fast model:
> distill trajectory into four-step sampler.

### StepAudio
Base representation itself:
> discrete AR factorization over time/codebooks.

These are different places to attack latency:

\`\`\`
compress the inference trajectory
\`\`\`

vs

\`\`\`
choose a generation operator whose basic step has different cost structure.
\`\`\`

Again:
> "efficient audio" is not one scientific problem.

---

# S54 — Cross-domain synthesis: test-time compute only has meaning relative to error cost

Why does extra compute exist?

### TabPFN
Error cost:
> worse fitted predictive model across many repeated downstream predictions.

Compute can be amortized.

### τ₀-VLA
Error cost:
> wrong irreversible physical action.

Compute is paid before commitment.

### Diffusion/AuK
Error cost:
> insufficient generative fidelity from coarse numerical integration.

Compute refines one sample.

### Search/reasoning LLM
Error cost:
> wrong branch/answer.

Compute explores cognition.

### Active video
Error cost:
> buying/encoding irrelevant observations or missing decisive frames.

Compute acquires information.

This suggests a better abstraction:

\`\`\`
test-time compute policy
=
operator
+ state
+ error cost
+ stopping signal
+ amortization boundary.
\`\`\`

Not:
> number of tokens/steps.

---

# S55 — "Thinking" is becoming a dangerously overloaded product word

In 2026 product/model cards use terms such as:
- Thinking;
- Extended Thinking;
- reasoning effort;
- test-time compute;
- deliberation.

But they may mean:

### Language reasoning
Generate more hidden/visible reasoning.

### Predictor fitting
TabPFN fit-time search.

### Model routing
Choose a stronger model.

### Search
World-model/action beam search.

### Generative refinement
Diffusion/flow steps.

### Tool/retrieval delay
Spend wall-clock on external computation.

Therefore:

> **never infer mechanism from a product mode name.**

Always recover the actual repeated operator.

---

# S56 — Updated cheap-artifact shortlist from this batch

Not topic rankings.

## TabPFN-3.5 / Fast
Very high:
- ~220M / smaller fast variant;
- local inference;
- synthetic-prior foundation model;
- base-vs-fast;
- architecture source.

Limitation:
- exact hosted Thinking internals not fully public.

## TimesFM-3
Very high:
- 330M;
- univariate/multivariate mode;
- covariates;
- PyTorch + MLX;
- official benchmarks.

## AuK / AuK-Flash
High:
- base vs four-step distilled student;
- open fine-tuning;
- one common task interface;
- intermediate checkpoint and per-t validation support.

## τ₀-VLA
Mixed:
- low-level 2B VLA is very usable;
- full high-level world-model-guided search stack is only partially released.

## StepAudio 3 Gen
Current instrument status:
- technical thesis strong;
- full model/source availability must be checked before treating it as a cheap experimental platform.

---

# S57 — New screening rule: Operator First

Whenever a recent paper/model card says:
- reasoning;
- thinking;
- test-time scaling;
- adaptive compute;
- iterative inference;

first delete those words.

Rewrite the system as:

\`\`\`
state X
--operator O-->
new state X'
--evidence/reward E-->
continue or stop
\`\`\`

Then ask:

1. What is X?
2. What is O?
3. What makes O useful?
4. What is E?
5. Is O repeated on the same state, branches, or new observations?
6. Does O alter the external world?
7. Can compute be amortized?
8. Could the same compute be moved into training or architecture instead?

If the paper remains interesting after this rewrite:
> the scientific object is probably real.

If not:
> "test-time compute" was doing all the rhetorical work.

---

# S58 — Current conclusion

This batch provides one of the clearest corrections to our early "trend chasing" temptation.

A trend label such as:
> test-time scaling

can now include:
- tabular predictor fitting;
- robot consequence search;
- LLM deliberation;
- active perception;
- diffusion refinement;
- model routing.

Those systems may share resource economics but not scientific mechanisms.

The stronger research habit is:

> **identify the operator and the error cost first; only then ask whether extra compute is the right intervention.**

At the same time, the open ecosystem gives us unusually cheap instruments:
- 220M tabular FM;
- 330M time-series FM;
- 1.5B audio diffusion model;
- 2B low-level VLA.

That means future topic search should not default to expensive LLM experiments when the underlying scientific distinction can be tested more cleanly in another modality.

Still no formal candidate generation.
