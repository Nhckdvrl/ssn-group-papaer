# Literature Calibration Closeout — 2026-09-19

> **Status: BROAD CALIBRATION CLOSED**
>
> This file marks the end of the broad academic / industry / startup / Hugging Face literature-calibration phase.
>
> It does **not** mark the end of literature reading.
>
> From now on, reading becomes:
>
> - candidate-specific;
> - nearest-prior-specific;
> - dangerous-overlap-specific;
> - or triggered by a genuinely changed premise / newly released experimental artifact.

---

# 1. What has been built

The repository now contains four interacting libraries.

## Academic genealogy library

Purpose:
> learn how scientific questions grow across parent→successor lineages.

Coverage includes:
- RLVR;
- test-time scaling;
- ICL mechanisms;
- diffusion;
- VLA/action representation;
- pretraining/scaling;
- SFT;
- distillation;
- architecture/inductive bias;
- VLM interface/token lifecycle;
- multimodal latent reasoning;
- speech/full duplex;
- negative/limits papers;
- optimization dynamics;
- multimodal objectives;
- speech tokenization;
- CoT faithfulness;
- video/world models.

---

## Industry frontier library

Purpose:
> observe regimes, bottlenecks and operational variables unavailable to ordinary academic-scale experiments.

Coverage includes:
- model routing / effort;
- long-running agents;
- context/cache economics;
- production traces;
- async RL;
- environment generation;
- full-duplex systems;
- serving/power/resource control;
- robotics/world models;
- deployment-derived training loops.

---

## Startup / Hugging Face library

Purpose:
> find sharp technical theses and, especially, public experimental instruments.

The 11 genealogy waves cover:
- mutable harnesses;
- temporal pretraining;
- full-duplex subproblems;
- world/action models;
- fast weights / memory;
- cheap proxy → full scale;
- scientific foundation models;
- failure/evaluator qualification;
- scientific experience/environment;
- harness maturity/evaluation correction;
- long-horizon state/correction;
- final frontier wave on pretraining value, world-model consumer contracts, modality extension, sparse selector targets and residual-capability data.

---

## Evidence/source ledger

Purpose:
> separate:
- measured evidence;
- company interpretation;
- our reconstruction;
- inspiration value;
- execution transferability;
- current artifact availability.

Important consequence:

> an A-level technical thesis can still be an F-level experimental artifact for us.

And:

> a modest 2B–6B model with matched checkpoints can be more useful than a frontier closed model.

---

# 2. What broad reading changed in the research-search process

The largest change is that we no longer search by surface topic.

Bad:

> reasoning is hot → find reasoning idea.

> world models are hot → find world-model idea.

> self-evolution is hot → do self-evolution.

Good:

\`\`\`
recover lineage
→ identify current pressure
→ identify what old abstraction became load-bearing
→ locate the minimum causal contrast
→ search for an existing public instrument
→ run the cheapest decisive test
→ only then derive a method/project.
\`\`\`

---

# 3. The strongest stable lessons

These are not idea templates.

They are audit habits.

---

## 3.1 The basic object often moves

Research frontiers repeatedly change what is treated as the unit of analysis:

- token → decision token;
- output → transition;
- task → trajectory;
- data amount → mixture/exposure/order;
- teacher quality → teacher–student relation;
- context → persistent state/reuse structure;
- world model → consumer-specific simulator/representation/planner;
- modality extension → parameter-sharing placement;
- pretraining → a specific transfer capability.

But:

> changing the object is not itself a generator.

The pressure must come first.

---

## 3.2 Proxy targets must be audited against the real consumer

Examples:
- dense attention ranking vs sparse-budget utility;
- token count vs actual compute;
- FLOPs vs latency;
- action-prediction loss vs task completion;
- simulation realism vs policy decision fidelity;
- runtime pass vs correctness certification;
- synthetic-environment quantity vs transferable learning pressure.

Canonical question:

> **What downstream ordering/decision is this proxy supposed to preserve?**

---

## 3.3 Failure localization is often more valuable than global regularization

Across:
- reasoning;
- long-form TTS;
- streaming geometry;
- optimization;
- agent trajectories;

late failure may originate from:
- a local transition;
- a slowly accumulating drift;
- missing persistent state;
- an incorrect evaluator;
- a wrong proxy objective.

Diagnose the dynamics before choosing the intervention.

---

## 3.4 Resource constraints can become scientific variables

Examples:
- remaining reasoning budget;
- context budget;
- cache lifetime;
- input/output compute asymmetry;
- tool latency;
- power cap;
- model identity;
- effort;
- prefill/decode asymmetry.

But:

> "adaptive resource allocation" has zero novelty by itself.

The state/action/objective relation must be specific.

---

## 3.5 Public artifacts change what is feasible

Before training:
> search for the intervention pair.

Useful pairs include:
- base vs SFT vs RL;
- sequential vs shuffled pretraining;
- pre-anneal vs post-anneal;
- BF16 vs quantized;
- high/low effort;
- same-language vs English reasoning;
- original vs JEPA continual pretraining;
- old/new tokenizer;
- world-model/action-head variants.

This makes:
> artifact archaeology

a formal part of pilot design.

---

# 4. Final hard gates added during the broad phase

Canonical guide now includes, among others:

- Repo-State Priority
- Nearest-Prior Audit
- Reviewer Compression
- Identification Gate
- Data/Compute Gate
- Changed-Premise Gate
- Mechanism→Method Necessity
- Industry Scale-Stripping
- Cheap Causal Echo
- Same-Surface/Different-Genealogy
- Genealogy Evidence Tags
- Contrast Gate
- Minimum Scale of Causal Visibility
- Proxy Fidelity
- Failure Provenance
- Operator First
- Domain Structure Placement
- Evaluator Qualification
- Development Tree ≠ Controlled Experiment
- Knowledge Location Audit
- Oracle Role Separation
- Harness Evaluation Correction
- Auto-Research Protocol
- AI-Research Role Decomposition
- Failure-Onset Localization
- Multi-Timescale Correction
- Research Memory Provenance
- Long-Horizon Failure Classification
- Pretraining Value Decomposition
- World-Model Consumer Contract
- Modality Extension Placement
- Public Artifact Maturity
- Proxy-to-Consumer Fidelity

The purpose is not bureaucracy.

It is:
> kill attractive but structurally weak ideas before they consume GPU time.

---

# 5. Surfaces that broad reading now treats as crowded by default

Not forbidden.

But they no longer carry novelty.

- generic GRPO variant;
- entropy/selective-token RL;
- generic adaptive reasoning effort;
- generic test-time scaling;
- generic visual-token compression;
- generic latent reasoning;
- generic self-evolving harness;
- generic long-context memory;
- generic world model;
- generic full-duplex model;
- generic synthetic environment scaling;
- generic multi-teacher OPD;
- generic harness diversity;
- generic QAD;
- generic sparse attention;
- generic capability routing;
- generic unified multimodal/scientific model;
- generic "pretraining helps";
- generic "data diversity helps".

Any future candidate using these surfaces must identify:
> the unresolved relation underneath the label.

---

# 6. What industrial material is for

Industry evidence is most useful for:

> **finding variables academia accidentally holds fixed.**

Examples:
- user idle time;
- cache lifetime;
- scaffold version;
- remaining context;
- rollout staleness;
- tool schema;
- intervention timing;
- power;
- workload phase;
- task duration;
- production failure distribution.

It is not a license to copy frontier-lab recipes.

Industry-derived seed:

\`\`\`
frontier observation
→ strip scale/company implementation
→ isolate relation
→ find independent academic pressure
→ find cheap causal echo
→ only then candidate audit.
\`\`\`

---

# 7. What startup/HF material is for

The strongest new lesson:

> **model cards can be natural-experiment catalogs.**

A model release is disproportionately valuable when it exposes:
- intermediate stage;
- matched control;
- small-scale mechanism-faithful model;
- failed/regressed stage;
- quantized/full precision pair;
- objective/backbone contrast;
- logs / W&B;
- public evaluation/runtime.

Do not equate:
> open model
with
> useful research instrument.

And never equate:
> "coming soon"
with
> released.

---

# 8. Stopping rule

Broad reading is now stopped deliberately.

Why stop?

Because beyond this point:

- marginal new genealogy decreases;
- surface repetition increases;
- trend-chasing bias grows;
- pattern-shopping becomes easier;
- time should move from catalog expansion to specific question selection/audit.

Future broad scan is re-opened only if:

1. user explicitly requests recalibration;
2. a new model/training regime clearly changes a premise;
3. an artifact changes what experiments are feasible;
4. a trend enters a negative/evaluation-correction phase;
5. a candidate enters an under-read field.

Otherwise:
> do not crawl companies/HF for its own sake.

---

# 9. Next research-search posture

For a future concrete seed:

\`\`\`
1. identify target field / pressure
2. reconstruct immediate lineage
3. find nearest dangerous prior
4. check current industrial/startup evidence if relevant
5. search public matched artifacts
6. define one cheap discriminative pilot
7. pre-register kill criteria
8. run
9. PILOT-AUTHORIZED or KILL
\`\`\`

No long-lived "SERIOUS".

No 20-idea dump.

No trend label as novelty.

---

# 10. Final calibration sentence

The target research taste is now:

> **Follow important moving fields, but do not copy their surface methods. Recover why the field moved, identify the assumption or relation that became load-bearing, and exploit public artifacts or cheap proxies to test the smallest decisive claim before paying full-scale cost.**

This is the final state of the broad calibration phase.
