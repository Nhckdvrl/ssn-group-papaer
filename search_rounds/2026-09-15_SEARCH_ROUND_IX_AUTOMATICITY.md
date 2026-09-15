# Search Round IX — 2026-09-15

## Status

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Preference:** mechanistic interpretability / LLM science, while keeping training, reasoning, architecture, and theory open

**Result:** **1 NEW BOUNDED SURVIVOR**

> **L44 — Does Internalization Produce Automaticity?**  
> `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

Package:

- `candidates/L44_REASONING_AUTOMATICITY/SELECTION.md`
- `candidates/L44_REASONING_AUTOMATICITY/E01_PREREGISTRATION.md`

There is still **no approved Mainline project**.

---

# 1. Search behavior in this round

This round implemented the corrected split:

> **standing important problem bank × independent new-leverage bank**

Recent 2025–26 papers were used primarily to calibrate taste or provide leverage, not automatically as the source of the next gap.

The round repeatedly triggered heartbeat recalibration after crowded walls. The main failure mode remained owner density: several questions were scientifically good but were already current research programs once audited at the parent level.

The round did **not** shrink those questions into smaller residual cells.

---

# 2. Serious walls audited and not promoted

## IX-1 — Does an inference-time mechanism explain how a capability is learned / updated?

Question:

> If a component is causally load-bearing for executing a behavior, is the same structure where training gradients must act to learn or modify that behavior?

Why it mattered:

Mechanistic interpretability often moves from `how the trained model computes` toward claims about training, debugging, editing, or forgetting.

Why it stopped:

Forward-vs-backward attribution, mechanistic data attribution, localization/editing, and mechanistic unlearning already make the execution/update relationship an active object. Preserving novelty would require a particular task or attribution cell.

**Verdict:** `KILL CURRENT SEARCH ROUTE — CROWDED PARENT`.

---

## IX-2 — Why are useful LLM concepts so often linearly represented?

This was an attractive deep standing question rather than a new-paper gap.

But the modern lineage is already a full program:

- ICML 2024 formalizes what linear representation means;
- ICLR 2026 gives a next-token-prediction explanation for latent-concept posterior geometry;
- 2026 theory separates representational linearity from linear accessibility and studies capacity limits.

**Verdict:** `KILL AS NEW TOPIC — ACTIVE RESEARCH PROGRAM`.

---

## IX-3 — Are early training mechanisms developmental prerequisites or merely transient correlates?

The strong version asks whether an early circuit / scaffold is causally required for a later capability rather than merely preceding it.

ICML 2024 already uses training-time optogenetic-style interventions to test induction-head developmental prerequisites. HAPAX then directly attacks whether induction copying is a necessary building block for more abstract ICL by suppressing the relevant training signal.

The durable lesson is useful:

> `appears earlier in training` does not establish `developmental prerequisite`.

But another IH/ICL study would be a successor.

**Verdict:** `KILL CURRENT OBJECT`.

---

## IX-4 — Does inference-time circuit sharing predict learning interference / forgetting?

This briefly looked like a strong bridge between mechanistic interpretability and classical multi-task / continual-learning interference.

The strongest nearby work already shows that high, nearly fixed circuit overlap can coexist with forgetting varying from almost zero to almost complete when **functional conflict** at the shared locus changes. The bridge itself is therefore already an explicit research program; raw overlap is not the missing explanation.

**Verdict:** `KILL — SCIENTIFIC STATEMENT ALREADY SPLIT BY PRIOR WORK`.

---

## IX-5 — Are different sampled reasoning traces genuinely different algorithms?

Mother question:

> Does self-consistency / pass@k sample multiple computational hypotheses or mostly surface variants of one internal mode?

This is scientifically meaningful, but the current frontier already contains representation-collapse analyses and methods explicitly optimizing latent / activation reasoning diversity. The remaining move would be to replace `representation diversity` with `causal circuit diversity`, which is exactly instrument-first leakage.

**Verdict:** `STANDING PROBLEM ONLY — DO NOT CANDIDATEIZE NOW`.

---

## IX-6 — Does fine-tuning reuse existing features or learn new ones?

2026 *Feature Drift* directly frames fine-tuning as recombination / repurposing of existing concepts versus new-feature learning, with causal evidence in refusal. ACL 2026 work also explicitly studies reusable latent skills / experience composition.

**Verdict:** `KILL — CURRENT PARENT OCCUPIED`.

---

## IX-7 — Predictive-state sufficiency vs decision/task sufficiency

The old question is whether next-token prediction learns a compact sufficient predictive state and what later training does to it.

Belief-state theory and modern Transformer work make the distinction important, but the naive prediction — task/reward training removes predictive distinctions irrelevant to the downstream objective — is too theoretically expected. No new leverage discovered in this round created a sufficiently uncertain causal statement.

**Verdict:** `KEEP IN STANDING BANK; NO CANDIDATE`.

---

# 3. Survivor — L44

## Mother question

> **When a skill becomes behaviorally direct / compressed through learning, has its computation actually become automatic?**

Operational version:

> **As overt reasoning is progressively internalized, does causal dependence on a shared flexible-reasoning workspace decrease, increase, remain invariant, or change non-monotonically?**

This is not another CoT-benefit paper and not another hidden-reasoning visualization.

The paper's scientific object is the relation between:

- **internalization:** fewer explicit reasoning steps / faster direct computation;
- **automaticity:** independence from the causal shared workspace.

---

# 4. Why this survived where nearby ideas did not

## Old standing problem

Skill acquisition has long distinguished deliberate resource-demanding computation from automatic practiced computation. LLM work increasingly uses `System 1`, `internalization`, `compiled reasoning`, and `direct answer` language, but those labels are usually behavioral.

## New leverage 1 — controlled internalization trajectories

Deng et al. 2024 progressively removes explicit CoT during training. Singh et al. 2025 observes a natural fine-tuning trajectory where reasoning first grows and later shrinks. Huang et al. 2026 gives theory for implicit-CoT internalization. Tsilivis et al. 2026 formally studies internalization and exposes an OOD cost.

These supply a controllable **learning axis**.

## New leverage 2 — causal workspace dependence

Gurnee et al. 2026 identifies J-space as a shared workspace and explicitly proposes J-space independence as an operational definition of automaticity in LMs.

Crucially, the same paper finds that direct-answer GSM8K is **more** vulnerable to J-space ablation than explicit-CoT GSM8K, because writing intermediate steps can externalize information that direct answering must hold internally.

This breaks the easy behavioral inference:

> `no visible reasoning -> automatic computation`.

The missing scientific quantity is therefore now measurable.

---

# 5. Strongest owner risk — Learning through Internalization

This paper had to be read as a serious owner, not waved away.

It already:

- motivates internalization through human automatic skill;
- formally defines internalization as replacing a slow multi-step procedure with a faster same-class program;
- asks how representations evolve;
- asks whether internalized computation mirrors explicit reasoning vertically or exploits parallel shortcuts;
- finds wider models internalize better than deeper ones in its setting;
- finds internalization can degrade OOD generalization through shortcuts.

Therefore L44 **cannot** claim:

> `we discover what happens internally when CoT is internalized`.

That parent is occupied.

The surviving independent statement is narrower but still scientific and consequential:

> **Does computational internalization imply mechanistic automaticity?**

Tsilivis et al.'s quantity is runtime / step compression. Gurnee et al.'s quantity is shared-workspace dependence. Neither paper establishes their relationship over learning.

This survives the abstract test: neither closest parent can honestly claim the answer without performing a longitudinal causal workspace experiment.

---

# 6. Why L44 is exploratory rather than gambling

For each internalization checkpoint `s`, estimate selective workspace dependence:

> `W_s = damage(J-space ablation) - damage(matched non-J perturbation)`.

Then estimate the trajectory of `W_s` as explicit reasoning is removed.

All resolved outcomes matter:

- **decrease:** genuine automatization;
- **increase:** overt CoT became silent workspace deliberation;
- **non-monotonic:** latent-deliberation stage before automatic compilation;
- **precise zero / invariance:** runtime internalization and automaticity are orthogonal;
- **task-dependent relation:** some computations are compilable and others remain workspace-bound.

The candidate is therefore not betting on a reversal or wake-up phenomenon.

---

# 7. Why only E01 is authorized

The largest risk is **instrument validity on open weights**, not problem importance.

Anthropic's strongest causal evidence is on Claude. The released Jacobian-lens code supports open-weight decoder Transformers and examples use Qwen, and independent open replications now exist. But the exact causal `automatic vs deliberate` dissociation must reproduce on the chosen model before a longitudinal training study is trusted.

E01 therefore begins with a positive-control gate:

1. direct multi-step reasoning must be selectively J-space-sensitive;
2. explicit CoT for the same task must be less sensitive;
3. a routine / automatic control must be substantially more robust;
4. matched perturbations must exclude generic representation damage.

Only after this passes is a stepwise internalization trajectory run.

**No Mainline promotion is implied.**

---

# 8. Standing Important Problem Bank after Round IX

These are not candidates. They are questions worth keeping alive without forcing a paper today.

1. **Skill acquisition:** when does practice change the computational organization rather than only accuracy/speed? — L44 is one currently testable slice.
2. **Predictive vs task-sufficient state:** what state does NTP force a model to preserve, and what later objectives discard?
3. **Algorithm multiplicity:** when behavioral stochasticity corresponds to genuinely different internal algorithms rather than surface variants.
4. **Mechanism vs learning path:** which properties of a mature mechanism reflect developmental necessity versus contingent training history?
5. **Functional modularity:** when apparent component specialization is a causal organizational fact rather than coordinate/method artifact.
6. **Computation sharing:** when shared internal computation implies shared transfer, interference, or only common implementation.
7. **Robustness organization:** when redundancy is naturally scheduled versus only counterfactually available — already instantiated by L43; do not generate a sequel.
8. **Representation sufficiency:** which encoded distinctions are predictive, reportable, causally usable, or flexibly reusable?
9. **Serial vs parallel computation:** which learned procedures fundamentally need sequential state and which can be compiled into parallel depth/width?
10. **Architectural inductive bias:** which common Transformer design choices constrain the algorithm learned rather than merely efficiency/stability?
11. **Mechanistic evidence semantics:** what claims about natural computation are actually identified by an intervention/probe?
12. **Flexibility vs efficiency:** whether cheap specialized computation systematically trades away recombination / OOD flexibility.

Do not turn this list into twelve topics. It is a bank for future leverage matching.

---

# 9. New Leverage Bank after Round IX

Again, these are not topics by themselves.

- **J-space / Jacobian-lens causal workspace interventions** — new operational separation of flexible workspace use from automatic processing.
- **stepwise CoT internalization checkpoints** — controllable axis from externalized to direct reasoning.
- **training-time optogenetic interventions** — can identify developmental necessity rather than temporal correlation.
- **conditional co-ablation / higher-order mediator methods** — expose counterfactual alternatives hidden from first-order attribution.
- **matched checkpoint / curriculum trajectories** — allow within-model developmental relations rather than model-zoo correlation.
- **formal internalization theory** — distinguishes slow procedures from fast learned programs and exposes generalization costs.
- **open-weight Jacobian-lens implementation** — permits causal workspace work outside closed models, conditional on validation.
- **multiple-circuit / intervention-divergence results** — leverage for asking what intervention-based explanations mean, not a generator for another circuit paper.

---

# 10. Heartbeat lesson

The strongest correction in this round came from repeatedly refusing attractive but saturated bridges.

The survivor did **not** come from asking `what is missing from the Anthropic paper?`.

The standing problem came first:

> **what does it mean for a learned skill to become automatic?**

Only afterwards did two independent 2026 developments make the distinction identifiable:

- internalization gives a controlled learning trajectory;
- J-space gives a causal workspace-dependence quantity.

This is the search shape to retain.

Do not turn it into a template like `old cognitive concept × new interpretability tool`. The durable rule is simply:

> **keep an old important ambiguity alive until a new intervention turns its competing meanings into measurable quantities.**
