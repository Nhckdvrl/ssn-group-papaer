# Current Research State — 2026-09-12

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Phase:** **bounded kill-oriented pilots + continued topic search**  
**Killed ledger:** authoritative through **K184**; newer compact rejections live in `search_rounds/` until a later ledger sync.

## Current search preference

The open-ended search target is now explicit:

> **stable model phenomenon → unresolved why → competing computational accounts → decisive causal/discriminating operation**

or:

> **training/model-regime change → old empirical law no longer sufficient → new conditional computational explanation**

### Highest-priority search tracks

- **Stable anomaly → mechanism**: mother phenomenon should already be credible; search the unresolved explanation.
- **Training / post-training dynamics**: pretraining → SFT → preference/RL/RLVR; learn vs select vs suppress vs reroute vs readout.
- **Reasoning / inference-time computation**: decision formation, revision, commitment, recovery, trajectory/state control.
- **Representation → causal use**: absent vs represented vs accessible vs selected vs read out; probe alone is insufficient.
- **Old empirical law / challenge → modern model regime**: not “LLM is better,” but a changed bottleneck, conditional law, or explanation.
- **Two strong papers disagree on the SAME scientific quantity**: find the hidden condition that makes both true.
- **Strong mechanistic claim → weak direct causal evidence**: attack explanations that have guided method design but were never decisively intervened on.

### Strongly deprioritized for new open-ended search

Do not normally spend search budget on:

- RAG / retrieval / search / evidence retrieval;
- benchmark construction, benchmark auditing, benchmark contamination;
- metrics / evaluators / generic evaluation-protocol fixes;
- annotation / adjudication / labeling workflow;
- dataset-quality / dataset-bias / data-first topic generation;
- systematic review / evidence-synthesis infrastructure;
- generic Agent / long-term memory / RL / judge / harness questions;
- new speech/audio topics;
- pure linguistic competence tests;
- generic bias / calibration / hallucination surveys.

These are taste priors, not universal scientific bans. A truly exceptional question may override them, but clean data/gold is not itself a reason to search there.

### Search taste test

Before deep search ask:

> **If the dataset, benchmark, metric, retrieval system, or workflow name disappeared, would we still urgently want to know the answer?**

Current preference is for papers whose interesting core is:

> **“Why does the model work this way?”**

rather than:

> **“The current data/evaluation pipeline measures the wrong thing.”**

### General requirements that still hold

- No survivor quota. Kill aggressively rather than fill slots.
- Question first; method second.
- Do not manufacture an abstract distinction and then hunt for a dataset.
- A strong anomaly is a lead, not proof that explanation space is open.
- Old problems are welcome when the modern scientific question is genuinely unresolved.
- Search strong papers for **topic provenance**, not for templates.
- Natural means the scientific object exists before our benchmark/intervention.
- Do not salvage low-priority topics merely because natural witnesses exist.
- Prefer tractable data/observables once the question is good; do not let easy data choose the question.
- Anti-resurrection remains mandatory.
- For mechanism topics, identification means observable + causal estimand + discriminating operation + inference bridge; it does **not** require artificial annotation gold.
- For external-task/data topics, DIRECT GOLD remains mandatory for the load-bearing estimand.

---

## Pilot-authorized

### L16 — Same World, Different Partitions
**Status:** `PILOT-AUTHORIZED — bounded E01/E02 only`  
Package: `candidates/L16_PARTITION_DEPENDENT_BELIEF/`

> Holding atomic hypotheses, evidence, target proposition and reasoning budget fixed, does arbitrary refinement/coarsening of the displayed hypothesis space systematically pull elicited credence toward a partition-specific ignorance prior?

If the directional law is absent, kill rather than rescue with generic prompt sensitivity.

### L17 — What Does a Speech LLM Learn About a Speaker?
**Status:** `PILOT-AUTHORIZED — E01 only; existing project, outside current new-search preference`  
Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

Do not create new speech/audio candidates.

### L22 — Bad Dimensions or Bad Directions?
**Status:** `PILOT-AUTHORIZED — E01 symmetry audit only`  
Package: `candidates/L22_EMBEDDING_BASIS_IDENTIFIABILITY/`

> Are claims that particular embedding dimensions are harmful/query-important properties of the representation, or artifacts of the coordinate basis used to write an equivalent geometry?

---

## Serious pre-pilot

### L21 — When Is Contextual Entrainment Rational?
**Status:** `SERIOUS — IDENTIFICATION BLOCKER — NO COMPUTE`  
Package: `candidates/L21_ENTRAINMENT_CACHE_PRIOR/`

### L23 — Similarity Is Not Provenance
**Status:** `SERIOUS / PRE-PILOT — NO COMPUTE`  
Package: `candidates/L23_SIMILARITY_NOT_PROVENANCE/`

### L26 — Same PICO ≠ Same Causal Question
**Status:** `SERIOUS SEED — DATA / DIRECT-OWNER AUDIT — NO COMPUTE`  
Package: `candidates/L26_ESTIMAND_ALIGNMENT/`

### L29 — Losing the Steering Gain
**Status:** `SERIOUS / PRE-PILOT — IDENTIFICATION BLOCKER — NO COMPUTE`  
Package: `candidates/L29_COT_CONTROL_GAIN/`

> When reasoning post-training makes chain-of-thought control collapse, is the loss merely caused by longer trajectories accumulating more opportunities to violate the constraint, or does training itself weaken the local causal influence of an explicit constraint on the reasoning policy?

Broad “represented but ignored” reasoning-control stories are already owned; L29 survives only as the same-base **training-induced local control-gain** question. Before compute, a matched-state intervention must be shown not to reduce to an off-distribution teacher-forcing artifact. Stable local gain favors the already-known length/opportunity account and kills the paper identity rather than creating a fallback metric paper.

---

## Hold / deprioritized

### L24 — Same Entity ≠ Same Epistemic File
**Status:** `HOLD / DEPRIORITIZED — HOT-DIRECTION + HARNESS + DATA-GOLD RISK — NO COMPUTE`  
Package: `candidates/L24_EPISTEMIC_FILES_VS_CANONICAL_ENTITIES/`

---

## Recent rejections

### L19 — Causal Ingredients of Long→Short SFT Transfer
**Status:** `ARCHIVED / NO-GO (K184)` — **shelved for cost, not for novelty**

Parent: Zheng et al., *When Long Helps Short*, EMNLP 2025 Main. Its short/long contrast is five different datasets and no experiment anywhere varies sequence length with data source held fixed, so its central causal variable is unidentified; a 2026-09-12 search found no published critique, replication, or matched-length experiment. **The novelty gap is open.**

Stopped on resolution. The parent's own dataset swap, rerun in our regime, reproduces only **26%** of its effect (+0.47 vs +1.30 MMLU, +0.91 vs +5.67 LAMBADA) — already below the evaluation noise floor at our n. The matched contrast is a subset of that effect and the interesting outcome was the *null*, which needs parent-scale budgets plus enough seeds to estimate run-level variance: **~100-300 GPU-hours** on this hardware to chase a 2.7 pp effect. Treatment arms were never trained.

**Durable workflow addition from this route:** selection must compare expected effect size against the **evaluation noise floor / minimum detectable effect** before expensive compute. A scientifically good question can still be infeasible at the available resolution.

Reusable: 10,000 frozen matched NQ pairs (98.4x length contrast, token-identical targets, verified under both Llama-3 and Qwen chat formats), a 600-item context-reliance probe, and a working 8B SFT + vLLM evaluation stack.

Record: `candidates/L19_LONG_TO_SHORT_TRANSFER/README.md`, `failed/KILLED_LEDGER.md` K184.

### L27 — Sample / Effect Count ≠ Independent Evidence Units
**Status:** `NO-GO / ARCHIVED`

Killed despite natural shared-control examples. The question is too shaped by a particular extraction representation, requires cumbersome article↔registry/design reconstruction, and reviewer-compresses to the standard statistical fact that automatic meta-analysis needs dependence/design metadata. **Do not continue prevalence audits or rescue with more design families.**

Record: `candidates/L27_EFFECT_DEPENDENCE_STRUCTURE/README.md`.

### Regression Row ≠ Scientific Effect Claim
**Status:** `NO-GO / DO NOT PROMOTE`

The classical Table-2-fallacy issue is real, but mature extraction systems already preserve exposure/covariate/adjustment roles. A new paper would depend on selecting a bad pipeline or adding another schema field rather than exposing a new scientific question.

### L28 — Canonical Species ID ≠ Source Taxonomic Concept
**Status:** `NO-GO / DIRECT DOMAIN-PARENT COLLISION`

Concept-aware mapping/alignment is already directly owned in biodiversity informatics; adding LLM IE would mainly repeat a known representation error.

### L25 — Evidence Exists Somewhere ≠ One Source Establishes It
**Status:** `NO-GO / ARCHIVED`

The source-composition question was reverse-engineered around the intervention rather than independently motivated.

---

## Governing workflow

Before deep-searching a lead:

> **scientific object + estimand + decisive operation + synonyms → killed ledger / archived candidates / recent search rounds → duplicate means discard first**

Then use:

> **SEARCH** to decide whether this is the right kind of question → **SELECT** to decide whether it deserves compute → **EXECUTE** only within explicit authorization.

`SEARCH → SELECT → PILOT → RE-SELECT → DEVELOP → RE-SELECT → PAPER / KILL`

> **Evidence survives claim mutation. Authorization does not.**
