# Current Research State — 2026-09-13

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Phase:** **continued mechanism-first search + one new bounded L30 pilot + existing projects under their own gates**  
**Killed ledger:** authoritative through **K184**. Compact kills **K185–K189** are recorded in `search_rounds/2026-09-12_CONTINUED_SEARCH_VII.md` and should be folded into `failed/KILLED_LEDGER.md` at the next ledger-maintenance pass.

## Current search preference

The open-ended search target remains:

> **stable model phenomenon → unresolved why → competing computational accounts → decisive causal/discriminating operation**

or:

> **training/model-regime change → old empirical law no longer sufficient → new conditional computational explanation**

Highest-priority tracks:

- stable repeated anomaly → mechanism;
- training / post-training transitions: learn vs select vs suppress vs reroute vs read out;
- reasoning / inference-time computation with a concrete new scientific object;
- representation → causal use, never probe-only;
- old empirical law rewritten by a modern model/training regime;
- SAME-QUANTITY contradictions with a hidden condition;
- community mechanistic beliefs whose causal evidence is materially weaker than assumed.

Strongly deprioritize RAG/retrieval/search, benchmark/evaluator/metric work, annotation/data-first topics, scientific-evidence infrastructure, generic Agent/memory/RL/judge/harness questions, new speech/audio topics, pure competence tests, and generic calibration/hallucination/safety surveys unless an exceptional model-science question clearly transcends the framing.

Before deep search ask:

> **If the dataset, benchmark, metric, system label, or method name disappeared, would we still urgently want to know the answer?**

and:

> **Is the paper fun because it explains why the model works this way, or because an evaluation/data pipeline is imperfect?**

No survivor quota. Zero survivors is valid.

---

# Active portfolio after 2026-09-13 update

## L30 — What Does Pairing Teach?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`

Package: `candidates/L30_PAIRING_SURPLUS/`  
Selection record: `search_rounds/2026-09-13_PAIRING_SURPLUS_SELECTION.md`

> **If pretrained language models can become substantially instruction-following from responses alone, what additional behavior is actually learned from the correct correspondence between an instruction and its response?**

The central quantity is **pairing surplus**: the marginal causal value of the joint `X↔Y` correspondence after holding the prompt and response marginals fixed.

Strong mother evidence comes from response-only tuning / inherent instructability, WIT prompt-side supervision, and low-complexity post-training access to pretrained abilities. Broad instruction-response alignment is **not** the novelty: MAIN, FedDQC, Hindsight Instruction Relabeling, and related work already own that parent.

The missing inference is narrower and causal:

> **Holding the same prompt pool and response pool fixed, what changes because each response is paired with its correct instruction rather than no usable correspondence or a wrong correspondence?**

E01 uses the conceptual P/D/S decomposition:

- **P — Paired:** correct `x_i → y_i` correspondence;
- **D — Decoupled:** remove usable pair dependence while preserving the relevant response-marginal/budget controls;
- **S — Shuffled:** same prompt and response pools, wrong correspondence.

Primary quantities are `P-D`, `D-S`, and especially the same-marginal `P-S` contrast. A conventional response-only arm may be used only to validate that D is not an attention/position artifact.

Preferred pilot regime is Gemma-2-2B + Alpaca-Cleaned with deterministic IFEval-style evaluation, prompt-clustered uncertainty, and multiple training seeds, subject to exact source compatibility checks before execution.

**Hard scope gate:** E01/C1 is only identification. A result like “shuffling drops IFEval by N points” is not enough for Main because prior work already owns broad alignment importance. The promising paper-scale path is a later conditional law asking whether the pretrained model's existing `X→Y` association predicts where paired supervision has marginal value. That C2 requires re-selection and is not authorized yet.

**Resolution rule:** a noisy near-null is HOLD, not evidence that pairing is irrelevant. If the pilot can only bound the effect loosely enough to allow a meaningful ~3–4 pp surplus, stop rather than narratively rescuing the claim.

## L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** `PILOT-AUTHORIZED — E01 only; EXISTING PROJECT, OUTSIDE CURRENT NEW-SEARCH PREFERENCE`

Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

Mother phenomenon: same-speaker in-context examples improve speech recognition. The live question separates global speaker adaptation from sublexical acoustic-phonetic adaptation and lexical/textual explanation with matched-speaker / matched-transcript controls.

**Why it stays:** unlike the newly killed legacy topics, it begins from an established mother effect and already has competing computational accounts plus a discriminating operation. It remains an existing project only. **Do not use this as permission to create new speech/audio topics.**

## L29 — Losing the Steering Gain

**Status:** `RECONSTRUCT-AUTHORIZED — ONE FINAL INSTRUMENT AUDIT (2026-09-13)`

Package: `candidates/L29_COT_CONTROL_GAIN/`

> **When reasoning post-training makes chain-of-thought control collapse, is the loss merely caused by longer trajectories accumulating more opportunities to violate the constraint, or does training itself weaken the local causal influence of an explicit constraint on the reasoning policy?**

Broad “represented but ignored” reasoning-control stories are already owned. L29 survives only as the same-base **training-induced local constraint→policy gain** question.

The previous matched-prefix OOD blocker was closed on paper by requiring two agreeing identification legs:

1. **E01A — common-support same-history gain:** shared reasoning prefixes are admitted only when they remain within the natural likelihood/support range of every compared checkpoint and prompt arm; compare the causal effect of the real constraint versus a matched neutral instruction on the next reasoning policy.
2. **E01B — natural-state constraint-refresh gain:** each checkpoint generates its own natural, still-compliant trajectory; fork that exact prefix and compare a fresh constraint reminder against a matched neutral reminder over the next short horizon.

MathIF already owns the fact that moving/repeating a constraint near generation can improve obedience. L29 does **not** claim that intervention as novelty. The unowned quantity was whether the **causal effect of the constraint itself changes over the same RL training trajectory**.

**E01 outcome:** The shared-history and natural-state pipelines were both feasible, and common support retained multiple questions from every source stage. The retained exact-word suppression instrument nevertheless failed its validity gate. A first neutral reminder retrieved the original rule and created an apparent 6.25 pp decline; target-matched, structural, and target-free anaphoric controls removed that result and showed no robust positive early-checkpoint gain. Expanding the sample would estimate wording/lexical effects rather than the intended controller change. L29 therefore returns `RECONSTRUCT`; see `candidates/L29_COT_CONTROL_GAIN/notes/E01_PILOT_REPORT.md`.

**E01R authorization:** One qualitative reconstruction is allowed. It removes all
earlier constraints and neutral reminders, then applies a fresh balanced-binary local
codebook at a natural reasoning boundary. Case and fixed-tag families must both show
clear positive leverage at step 100 on a separate 48-question development split under
two templates and swapped rule mappings. Failure kills L29 with no third reconstruction;
success freezes the instrument before any untouched step-100/1400/2800 comparison.

No hidden-state work, steering method, new training, or broad model sweep is authorized before re-selection.

---

# Removed from active portfolio in the 2026-09-12 re-screen

## L16 — Same World, Different Partitions

**Status:** `KILL / ANTI-RESURRECTION — duplicate of K006`

The repository already killed **K006 Partition Dependence** because the parent was occupied by statistical partition/self-consistency plus framing/choice-set work. L16 reintroduced the same scientific parent with a sharper `1/M` ignorance-prior prediction. More importantly under the current search doctrine, the exact LLM effect is not an established mother phenomenon: the paper identity still depends on first discovering the desired partition shift. A sharper equation and cleaner pilot do not reopen K006.

## L21 — When Is Contextual Entrainment Rational?

**Status:** `KILL — K185`

Recent 2026 work now directly centralizes the contextual-entrainment scaling law, including the split whereby semantic entrainment decreases with scale while arbitrary/non-semantic copying can increase. L21's surviving contribution would be to explain this mature phenotype using a corpus self-recurrence/cache statistic whose normative quantity is itself difficult to identify independently of topic/discourse/syntax. That is too narrow and too correlational for the current Main-level mechanism bar.

## L22 — Bad Dimensions or Bad Directions?

**Status:** `KILL — K186`

The orthogonal-rotation argument is mathematically clean, but the paper remains a representation/retrieval-method identifiability audit: “coordinate dimensions are arbitrary under basis change.” Its strongest reviewer compression is the old rotation/basis-invariance fact applied to modern embedding-dimension attribution. It does not give us the desired model-computation mother problem, and current search explicitly deprioritizes retrieval/measurement audits.

## L23 — Similarity Is Not Provenance

**Status:** `KILL — K187`

The temporal impossible-copy control is elegant, but the parent is a provenance/measurement-validity question: can similarity identify copying rather than independent reconstruction? Under the current portfolio taste this is not a sufficiently central `why does the model compute this way?` question, and the natural growth path remains plagiarism/provenance evaluation rather than model mechanism.

## L24 — Same Entity ≠ Same Epistemic File

**Status:** `KILL — K188`

This route was already HOLD/deprioritized. It sits inside the hottest generic Agent/long-term-memory state-tracking space and requires a memory harness plus difficult perspective/state gold before the central claim is secure. The current project explicitly does not spend open-ended search budget there. Do not reactivate via another memory architecture or benchmark.

## L26 — Same PICO ≠ Same Causal Question

**Status:** `KILL — K189`

The estimand distinction is scientifically legitimate, but the paper is fundamentally a scientific-document/evidence-synthesis representation and data-gold project. It requires expert trial/estimand reconstruction and a defensible pooling consequence before the NLP claim is identified. This is exactly the high-workload data/scientific-IE route the current search has moved away from; clean clinical methodology does not make it the right portfolio question.

---

# Recent important kills / holds

## L19 — Causal Ingredients of Long→Short SFT Transfer

**Status:** `ARCHIVED / NO-GO (K184) — cost/resolution kill, not novelty kill`

The causal gap remains open, but the expected matched effect is below the available evaluation/training resolution. Credibly separating a meaningful null from a small effect would require roughly 100–300 GPU-hours. Do not shrink the claim to fit the budget.

## Temporal Forgetting

# **DO NOT RESURRECT**

This entire parent is hard-banned for current search: forgotten≠erased, old-prefix rescue, checkpoint rescue, earlier ability suppressed, final-checkpoint readout, temporal sampling, capability shift, or renamed variants.

---

# Search discipline

Before promoting a hook:

> **scientific object + estimand + decisive operation + synonyms → killed ledger / archived candidates / recent search rounds → repeated mother evidence → SAME-QUANTITY check → direct-owner assassination → reviewer compression → only then SELECT**

Do not mine one paper's Discussion as the default source of novelty. Prefer 2–4 independent strong papers exposing the same abnormal quantity under different names, or an old empirical law whose load-bearing premise genuinely changes in the modern regime.

Search V–VII are the current anti-duplication frontier. In particular, do not reopen reasoning-length/overthinking, CoT faithfulness, metacognition-control, RLVR entropy/mode collapse/capability boundary, self-correction, generic instruction-following loss, generic post-training rerouting, or other recently killed parents by adding another intervention/model family.

L30 does **not** reopen generic instruction-following loss: it is specifically the marginal causal value of the **joint correspondence structure in supervision**, with fixed prompt/response marginals and a later conditional-law path.

> **The goal is not to keep a portfolio full. The goal is to find one scientific object worth months of mechanism, boundary, intervention, and theory work.**
