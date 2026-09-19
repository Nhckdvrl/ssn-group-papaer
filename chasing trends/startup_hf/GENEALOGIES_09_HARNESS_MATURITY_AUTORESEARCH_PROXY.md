# Startup & Hugging Face Genealogies 09 — Harness Maturity, Auto-Research Protocols, R&D Partnership, and Cheap Compression Proxies — 2026-09-19

> Status: literature / research-taste calibration only.
>
> NO formal CT candidate generation.
>
> This file continues Startup/HF Genealogies 01–08.
>
> Main update:
>
> > **A research trend should be considered mature when papers stop asking whether the mechanism can work and start asking whether the measured gain is real, transferable, budget-matched, and compatible with the rest of the system.**
>
> The agent-harness literature has reached that phase extremely quickly in 2026.
>
> This batch also adds two non-harness lessons:
>
> - Atria Dawn: project-level AI R&D should be decomposed by role and verification, not one "AI scientist" score.
> - X-AuT / Qwen-Audio-VAE: compression and representation choices should be evaluated against the downstream consumer contract, with cheap probes used before expensive repair/training.

---

# S92 — Harness evolution: representation → adaptation → evaluation correction → compatibility

By September 2026, "self-improving harness" is no longer a useful novelty statement.

The genealogy itself now contains several distinct scientific stages.

---

## S92.1 Stage 0 — harness becomes an explicit object

Natural-Language Agent Harnesses externalizes high-level agent control from runtime-specific code into:
- editable natural language;
- explicit module contracts;
- a common runtime.

This matters historically because a thing cannot be systematically:
- compared;
- transferred;
- ablated;
- optimized

until it is represented as an object.

Primitive change:

\`\`\`
controller glue
→ inspectable harness representation.
\`\`\`

This is a prerequisite for the later self-improvement literature.

---

## S92.2 Stage 1 — can the harness improve from experience?

Continual Harness, RHI, Self-Harness, Evo-Harness and related systems ask variants of:

> Can a fixed model improve by changing the surrounding harness?

They differ in:
- online vs benchmark-level adaptation;
- memory/skill compilation;
- pairwise feedback;
- weakness mining;
- task-specific vs general harness;
- whether edits persist.

At this stage the headline claim is:
> harness adaptation can improve task performance.

That is no longer enough.

---

## S92.3 Stage 2 — the first major identification correction: search budget

Rethinking the Evaluation of Harness Evolution asks a more important question:

> Is the gain caused by a better reusable harness, or simply by spending more feedback/search compute on the benchmark?

Harness evolution repeatedly:
- tests tasks;
- observes feedback;
- modifies candidates;
- tests again.

Therefore it should not be compared only with:
> one-pass baseline harness.

The paper compares against:
- parallel sampling;
- sequential refinement;
- harness scaling/search

under matched feedback and inference budgets.

Reported on Terminal-Bench 2.1:
- harness evolution does not consistently beat simple test-time search baselines;
- gains generalize weakly to held-out tasks in the tested settings.

### Primitive change

\`\`\`
harness evolution gain
→ gain after subtracting search-budget advantage.
\`\`\`

This is exactly the kind of measurement correction that signals a method family is maturing.

---

## S92.4 Stage 3 — benchmark-disjoint generalization becomes explicit

ModularRSI responds to another problem:

> evolving directly on evaluation tasks can conflate reusable harness improvements with benchmark-specific adaptation.

Its answer is:
- external 2,000-task evolution set;
- successful-vs-failed trajectory contrasts;
- five functional harness modules;
- independent module evolution;
- integration after local changes.

The important move is not "modular harness."

It is:

\`\`\`
optimize on evaluation set
→ evolve on benchmark-disjoint tasks
→ measure transfer later.
\`\`\`

Again the question has moved from:
> "can we optimize?"

to:
> **"what survives separation between development and evaluation?"**

---

## S92.5 Stage 4 — model–harness compatibility becomes a new failure mode

Co-Evolving Harnesses and Models exposes a deeper failure.

Experimental sequence:
1. evolve a harness around a weaker model;
2. observe that a stronger expert often uses that harness even better;
3. imitate the expert's complete trajectories with the weaker model.

The seemingly natural third step backfires.

Reported:
> full expert-trajectory imitation regresses performance on all seven enterprise tasks by 4–30 points across the tested Qwen3-Coder and Gemma 4 settings.

The analysis attributes the failure to:
> model–harness fit.

The weaker model learns the expert's planning style,
but lacks the competence required to execute it,
and now no longer behaves like the policy around which the harness was evolved.

### Primitive change

\`\`\`
harness quality as an intrinsic property
→ harness quality relative to a model's native policy/competence.
\`\`\`

This mirrors earlier distillation genealogy:

teacher quality
→ teacher–student compatibility.

Here:

harness quality
→ harness–model compatibility.

---

## S92.6 Local on-policy correction repairs compatibility better than full imitation

The proposed repair preserves the student's own rollout.

A meta-level system:
- identifies the failing turn;
- asks the stronger expert to rewrite only that turn;
- trains from localized corrections.

This keeps:
- the student's planning trajectory;
- the harness's expected interaction style;

while importing local expert capability.

### Research-taste lesson

The method is constrained by the diagnosis.

If the problem is:
> global strategy transplant breaks model–harness fit,

then:
> localized correction on student states

is more natural than:
> more expert imitation.

This is a clean failure→mechanism→method instance inside an already crowded trend.

---

# S93 — SoL-Pi: auto-research must itself obey experimental discipline

SoL-Pi is particularly valuable because it directly cites the harness-overfitting/evaluation problem and structures its auto-research around avoiding it.

---

## S93.1 The project does not begin from "discover a better harness"

It begins from a constrained objective:

> reduce token/inference cost without reducing useful completed work.

This is a Pareto problem:
- capability constraints;
- efficiency objective.

Before search:
- capability metrics are fixed;
- tolerances are fixed;
- efficiency metrics are fixed.

The optimizing agent cannot modify these acceptance criteria.

This matters.

Without a frozen objective:
> an auto-research loop can redefine success to match what it found.

---

## S93.2 Search and final validation are separated structurally

SoL-Pi uses:
- development environments for mechanism search;
- held-out EdgeBench only after the harness is frozen.

Held-out failure does not trigger another patch.

This follows a crucial research principle:

\`\`\`
validation result
\not\to
search feedback.
\`\`\`

If failed held-out evidence feeds back into method design repeatedly,
the held-out set becomes another development set.

---

## S93.3 Breadth is not evidence; selection is the scientific object

The project explores roughly:
- 152 proposed directions;
- 535 executable search environments;
- >3,000 runs;
- >60,000 agent–environment interactions.

Only four mechanisms survive:
- Action Fusion;
- Online Context Compact;
- ObservationPack;
- Evidence-Preserving Reducer.

The paper explicitly notes:
> these search counts do not establish a scaling law.

That caveat is important.

The scientific value is not:
> "more auto-research runs always yield better ideas."

It is:
> a broad search funnel can be made experimentally disciplined enough that a small number of reusable mechanisms survive independent gates.

---

## S93.4 The four winning mechanisms expose four different waste units

### Action Fusion
Waste:
> an unnecessary model round trip between a mutation and predictable validation.

Unit changed:
> tool/action transaction.

### Online Context Compact
Waste:
> compaction performed without considering rewrite cost vs future reuse.

Unit changed:
> context-management decision becomes an economic break-even calculation.

### ObservationPack
Waste:
> replaying a large tool observation in full across many future requests.

Unit changed:
> observation persistence and exact recall.

### Evidence-Preserving Reducer
Waste:
> forcing the expensive main model to reread long logs when only verified evidence matters.

Unit changed:
> diagnostic evidence vs raw output.

These are not four versions of one compression method.

They target four different boundaries in the agent loop.

---

## S93.5 Evidence preservation is treated as a hard constraint

ObservationPack:
- archives originals;
- keeps exact paged recall.

Evidence-Preserving Reducer:
- extracts with a cheaper model;
- verifies schema/hash/exit status/exact quotations;
- falls back to the original on failure.

This avoids a common efficiency trap:

\`\`\`
compress information
→ silently reduce capability
→ report lower token cost.
\`\`\`

Instead:
> efficiency is allowed only under explicit evidence-preservation and capability gates.

---

## S93.6 SoL-Pi is not a cheap academic project despite open code

The extension itself is open and lightweight.

But reproducing the discovery process required:
- hundreds of executable environments;
- thousands of agent runs;
- frontier API models.

So distinguish:

### Mechanism reproduction
Potentially cheap.

### Discovery-process reproduction
Expensive.

### Scientific lesson
Very transferable:
> **search cost and validation cost must be separated from the cost of the final method.**

---

# S94 — Harness trend maturity: appearance of evaluation-correction papers is itself a signal

A useful meta-rule emerges.

A trend often moves through:

\`\`\`
representation
→ method success
→ method zoo
→ generalization concerns
→ budget-matched evaluation
→ compatibility/boundary studies.
\`\`\`

Harness research is already here.

Therefore:

> "new harness self-improvement algorithm" should now receive a very high novelty burden.

The stronger questions are:
- what quantity was falsely attributed to harness quality?
- what transfers benchmark-disjoint?
- what is model-relative?
- what is merely test-time search?
- what capability floor exists?
- what adaptation channel should change: harness or weights?

This maturity signal should be used for other hot trends too.

When papers start appearing whose main contribution is:
> correcting the evaluation protocol of the trend,

the surface label is probably saturated.

---

# S95 — Atria Dawn: "AI scientist" becomes a division-of-labor problem

Atria Dawn Preview is a large open model, but the benchmark table is not its most interesting research artifact.

The more important part is the development-process study.

---

## S95.1 Training experience is task + trajectory + artifact + external verification

The Verifiable Experience Pipeline retains experience only when it connects:
- task objective;
- tool-mediated trajectory;
- produced artifact/state;
- externally checked outcome.

Verification can come from:
- tests;
- numerical metrics;
- file/application state;
- geometric structure;
- source evidence;
- human-defined criteria.

This is a stronger unit than:
> conversation trajectory.

The learning object is:
> **a trajectory anchored to a verifiable artifact/outcome.**

---

## S95.2 Failure analysis feeds task/environment construction

The report says recurring failures such as:
- ineffective tool selection;
- incomplete verification;
- missing evidence;
- failed recovery

motivate:
- additional training tasks;
- environment refinements;
- new quality checks.

This creates the loop:

\`\`\`
training/deployment failure
→ diagnostic category
→ task/environment construction
→ reusable training experience.
\`\`\`

This independently converges with:
- DeepSeek failure replay;
- Echoverse;
- ScienceIDE;
- BlueLM-GUI.

---

## S95.3 Real R&D logs separate method proposal from method selection

Atria analyzes:
- 769 task records;
- 56 participants;
- agent logs from its own development.

The central question is not:
> can the agent complete a benchmark?

It is:
> **who performs which research role?**

The report distinguishes roles such as:
- proposing methods;
- selecting methods;
- diagnosing problems;
- implementing revisions;
- final judgment/steering.

Its qualitative conclusion:
- agents increasingly propose approaches and execute changes;
- humans still concentrate on evaluation, selection and direction-setting.

This is the same bottleneck migration seen independently in OpenAI/Anthropic internal R&D reports.

---

## S95.4 "AI scientist capability" is therefore not one scalar

At least four separable capabilities exist:

1. **Proposal generation**
   Can the model generate plausible methods/experiments?

2. **Execution**
   Can it implement/run them?

3. **Evidence interpretation**
   Can it decide what a result means?

4. **Direction selection**
   Can it choose what is worth pursuing next?

Current industrial evidence suggests automation progresses unevenly across these.

That matters directly to research-topic search.

As execution becomes cheaper:
> selection and evidence interpretation become more valuable bottlenecks.

---

## S95.5 This is also a measurement warning

A benchmark may give an AI scientist:
> a problem already selected by humans.

That benchmark cannot directly measure:
> ability to identify worthwhile research problems.

Similarly:
> producing 100 ideas

does not measure:
> choosing the one experiment that changes belief.

So future AI-scientist evaluation needs to distinguish:
- throughput;
- project success;
- information gain;
- human intervention;
- decision quality.

Again, not a candidate here.

---

# S96 — X-AuT: cheap behavioral probes can screen compression choices before full repair

X-AuT is a useful recent example of the cheap-proxy→full-method chain.

The target is modest:
> reduce speech-LLM audio encoder depth.

The research process is more interesting than the compression result.

---

## S96.1 Direct layer removal causes behavioral errors, not just embedding drift

Removing encoder blocks can cause:
- deletions;
- premature EOS;
- downstream decoder mismatch.

So compression quality cannot be measured only by:
> representation cosine distance.

The relevant proxy must connect to:
> actual decoder behavior.

---

## S96.2 Short behavioral probes select candidate layer combinations

Instead of fully distilling every pruning choice,
the method first uses short behavioral probes to identify promising combinations.

Only selected candidates undergo the more expensive repair pipeline.

This is a direct instance of:

\`\`\`
large combinatorial design space
→ cheap task-relevant proxy
→ expensive optimization only for survivors.
\`\`\`

The key word is:
> task-relevant.

A cheap proxy is only useful if it predicts downstream ordering.

---

## S96.3 Progressive compression beats one-shot compression

Reported under the matched recipe:

- progressive 18→16→14: mean error 5.75%;
- direct 18→14: 6.73%.

This says the endpoint architecture is not the full specification.

The **path by which the student reaches that architecture** matters.

That parallels:
- continual learning;
- curriculum;
- progressive context growth.

But the causal reason here is specific:
> the decoder must adapt gradually to a moving audio representation.

---

## S96.4 Teacher scale changes distillation quality

The reported 1.7B teacher gives substantially better mean error than self-distillation in the tested setting.

Thus:

\`\`\`
compression architecture
+
repair objective
+
teacher quality
\`\`\`

jointly determine the final model.

A paper that compares only:
> layer count

would miss the actual system.

---

## S96.5 Evidence caveat

The abstract explicitly describes the reported operating points as single-run results and notes benchmark-dependent effects.

That lowers the strength of any general law claim.

But it increases taste value:
> the paper does not hide the evidence tier.

---

# S97 — Qwen-Audio-VAE: representation quality includes producer throughput

Audio autoencoders are commonly judged by:
- reconstruction quality;
- bitrate;
- perceptual metrics.

Qwen-Audio-VAE adds a deployment/training constraint:

> a latent representation used for huge text-to-audio training must also be fast to **produce**.

---

## S97.1 The encoder is an upstream data-processing system

If millions of hours of audio must be converted into latents,
encoder throughput directly changes:
- preprocessing cost;
- training pipeline throughput;
- iteration speed.

Therefore:

\`\`\`
VAE quality = reconstruction × compression
\`\`\`

is incomplete.

The practical object becomes:

\`\`\`
representation utility
=
fidelity
× latent compactness
× encoding throughput
× downstream trainability.
\`\`\`

---

## S97.2 Asymmetric encoder/decoder is derived from the consumer contract

The release uses:
- causal encoder-decoder;
- window Transformer blocks;
- latency-aware encoder pruning;
- asymmetric design.

Why asymmetry?

Because:
> encoding the training corpus and decoding generated output are not equally frequent or equally constrained operations.

The representation producer and consumer have different cost profiles.

This is a recurring industrial pattern:
- prefill vs decode;
- encoder vs decoder;
- world vs action branch;
- draft vs target model.

System asymmetry can justify model asymmetry.

---

## S97.3 This is not the same problem as X-AuT

X-AuT:
> compress a speech encoder while preserving a frozen LLM consumer.

Qwen-Audio-VAE:
> design a representation producer whose throughput enables downstream generative-model training at scale.

Same surface:
> "audio encoder efficiency."

Different causal contract.

---

# S98 — New canonical rule: trend maturity needs a different reading strategy

Once a trend reaches evaluation-correction stage:

Do not search primarily for:
> another method.

Search for:

1. **Attribution error**
   What gain was previously assigned to the wrong cause?

2. **Matched-resource control**
   Does the method beat simpler ways to spend the same budget?

3. **Generalization boundary**
   Does the discovered object transfer to held-out tasks/models?

4. **Compatibility**
   Is the solution relative to the model/data/harness that produced it?

5. **Capability floor**
   Does the self-improvement mechanism require a strong base system?

6. **Measurement qualification**
   Can the evaluator itself distinguish success from shortcut?

This is especially important in fast-moving 2026 clusters, where method novelty can saturate within weeks.

---

# S99 — Research-instrument assessment for this batch

## SoL-Pi
Technical-thesis value: HIGH  
Open mechanism value: HIGH  
Discovery-process replication cost: VERY HIGH  
Cheap experimental use: HIGH for individual mechanisms

Useful artifact:
- four independent opt-in mechanisms;
- no base-Pi source patch required;
- exact context/evidence handling exposed in code.

## Atria Dawn Preview
Technical-thesis value: MEDIUM/HIGH  
Process-observation value: HIGH  
Training replication: IMPOSSIBLE for us  
Inference value: LOW/MEDIUM due 744B base  
Research-log value: conceptual rather than downloadable raw task log.

## Co-Evolving Harnesses and Models
Technical-thesis value: HIGH  
Execution transfer: MEDIUM  
Key value:
- clean negative result for naive expert imitation under evolved harness.

## Rethinking Harness Evolution
Technical-thesis value: HIGH as evaluation correction  
Execution transfer: MEDIUM/HIGH if API budget available  
Key value:
- directly tests whether a trend's claimed gain survives matched search budget.

## X-AuT
Technical-thesis value: MEDIUM/HIGH  
Execution transfer: HIGH  
Key value:
- cheap behavior probe → progressive repair chain on small speech models.

## Qwen-Audio-VAE
Technical-thesis value: HIGH for systems/representation taste  
Training replication: LOW  
Inference/profiling artifact value: potentially useful if open weights/code available.

---

# S100 — Current conclusion

This batch adds a new question to our paper/model-card autopsy:

> **What phase of the research trend is this artifact in?**

### Early phase
- exposes a new basic object;
- first proof that it matters.

### Expansion phase
- multiple methods attack the new object.

### Maturity phase
- evaluator/resource/generalization corrections appear.

### Consolidation phase
- compatibility/boundary conditions become more important than new modules.

Harness evolution is already in maturity/consolidation.

The right lesson is not:
> "harness is hot."

It is:
> **watch how a hot topic stops being a novelty problem and becomes an identification problem.**

At the same time, X-AuT and Qwen-Audio-VAE reinforce a practical theme:

> expensive full-scale model design often becomes tractable only after identifying a cheap proxy whose relation to the final consumer is explicitly tested.

This remains research calibration, not a candidate menu.
