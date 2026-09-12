# L29 — Agent Handoff / Pilot Brief

**Project:** Losing the Steering Gain  
**Status:** **KILL — final E01R instrument gate failed**
**Date:** 2026-09-13
**Target:** ACL / EMNLP / NAACL Main

This document is the handoff for the agent that will execute the first bounded study. It is intentionally written as a **scientific brief rather than a mechanical recipe**. The goal is to preserve the research question, novelty boundary, causal quantity, and inference requirements while leaving implementation choices open when a cleaner design is available.

**Execution update:** The bounded audit completed on steps 100, 1400, and 2800.
Common support was feasible, but exact-word suppression failed the positive early-gain
instrument check after neutral-reminder and lexical-priming controls. The apparent
decline under the first neutral wording was an intervention artifact. Read
`notes/E01_PILOT_REPORT.md` and its referenced raw artifacts before proposing a new
design. No mechanism work or larger sweep is authorized by this result.

**Reconstruction authorization:** E01R replaces persistent suppression with a fresh,
mid-reasoning balanced-binary codebook. Run `notes/E01R_DESIGN.md` exactly as a staged
gate: step 100 and instrument-development questions first; no later checkpoint or
confirmation outcome until both case and tag instruments pass. Failure kills L29 with
no further wording search.

**Final E01R outcome:** All 48 step-100 development questions had natural forks, but
case directional gain was 0.00 pp and tag gain was +1.30 pp. Both failed the frozen
15 pp gate and robustness checks. No later checkpoint or untouched confirmation
outcome was generated. `notes/E01R_REPORT.md` is the final record. Do not reconstruct
L29 again or begin mechanism work.

Before doing substantive work, sync the latest `main` and read:

- `CURRENT_SEARCH.md`
- `RESEARCH_TOPIC_SELECTION.md`
- `RESEARCH_EXECUTION.md`
- `candidates/L29_COT_CONTROL_GAIN/README.md`
- this file

Work only inside the L29 subproject unless a root status update is genuinely required. Do not change the paper identity merely because a convenient experiment suggests a different story.

---

# 1. Understand the question before designing the experiment

The established phenomenon is not our contribution.

Recent work has already shown that reasoning models can be much harder to control in their chain of thought than in their final answer, and that CoT controllability can become dramatically worse as reasoning-oriented RL proceeds. Longer reasoning is also an obvious confound: a longer trajectory creates more opportunities to violate a constraint and places the original instruction farther from the current generation point.

Our question is narrower and more causal:

> **When CoT controllability deteriorates during reasoning post-training, has the model actually become less locally steerable by an explicit constraint, or is the apparent collapse mostly a cumulative consequence of longer / more extended reasoning?**

Another way to say it:

> Suppose the model is already at some still-valid reasoning state. If we make a constraint locally available right now, how much does that constraint change what the model does next? Does that causal leverage itself shrink over the same reasoning-RL training trajectory?

This local leverage is the current scientific object. We provisionally call it **constraint→policy control gain**. The terminology is not sacred; the quantity is.

Do not reduce L29 to “reasoning models ignore instructions,” “RL hurts instruction following,” or “repeating the instruction helps.” Those are already neighboring results in the literature and are too broad to be our contribution.

---

# 2. What is already owned, and what is potentially ours

The project sits close to several strong owners, so the novelty boundary matters more than the experiment name.

**CoT-Control / Reasoning Models Struggle to Control their Chains of Thought** owns the mother phenotype: reasoning models show poor CoT controllability; controllability changes with reasoning length/test-time compute and along reasoning-training trajectories; the mechanism remains unresolved.

**MathIF** already shows that bringing a constraint closer to the generation point / repeating it after reasoning can recover some compliance. Therefore “a reminder helps” is not our novelty and must never become the headline.

**Compliance versus Sensibility** already supports the broad picture that reasoning-related instructions can remain internally represented while the model nevertheless follows its preferred reasoning behavior, and it explores activation steering. Therefore a static “represented but unused” probe result is not our contribution.

**ReasonIF / Scaling Reasoning, Losing Control** occupy the broader reasoning-capability versus instruction-adherence space. A new benchmark or another endpoint comparison is not enough.

The strongest reviewer compression we must survive is:

> “CoT-Control already shows training and length reduce control; MathIF already repeats the instruction near the answer; Compliance-vs-Sensibility already says the model can encode an instruction and still ignore it. This is just those papers plus checkpointed logits.”

L29 only survives that compression if it establishes a new training-causal statement of roughly this form:

> **Across a same-base reasoning-RL trajectory, the local causal influence of an explicit constraint on the continuation policy itself changes, even after separating that effect from accumulated trajectory length/opportunity and from off-distribution state artifacts.**

That is the positive branch. If local gain is stable, the current Main-level paper identity probably dies; we do not turn the null into a weak “length matters” paper because that neighborhood is already known.

---

# 3. The competing explanations

Think in terms of explanations, not experiment labels.

### Account A — opportunity / distance accumulation

Reasoning training mainly creates longer, richer, or more persistent trajectories. The model is exposed to the constraint for longer and gets more chances to violate it. The original instruction may also become contextually distant. Global exact compliance can therefore collapse even if the model is **still just as locally responsive** when the constraint is made salient at a currently reachable reasoning state.

### Account B — constraint-signal degradation

Post-training changes the model such that the constraint becomes less available or less stably represented at the point where continuation is selected. The local causal effect of the constraint should fall.

### Account C — policy-gain / attractor override

The constraint signal may remain available, but reasoning training strengthens competing continuation dynamics: learned reasoning habits, attractors, or outcome-driven policy tendencies dominate token selection. The constraint is “there” yet exerts less causal leverage.

The first pilot is **not** allowed to distinguish B from C yet. It only asks whether A is sufficient or whether some genuine local-control change ({B,C}) remains after the major confounds are removed.

Only if that first distinction survives should the project return to selection and consider representation/mechanism work.

---

# 4. What the pilot actually needs to identify

Do not optimize for reproducing a benchmark score. We need an estimate of an **intervention effect**.

At a reasoning state `h` and checkpoint `c`, conceptually we care about something like:

`local control gain = behavior under an active constraint - behavior under an otherwise matched control instruction`

The exact observable can be designed intelligently. It may be a next-token probability mass over mechanically compliant continuations, short-horizon violation probability, continuation-level compliance, or another quantity that more cleanly captures the same causal contrast.

The important properties are:

- the constraint/control difference should be the thing causing the contrast, not an accidental difference in length, formatting, task difficulty, or answer information;
- compliance should be mechanically or very reliably identifiable, not judged by an opaque LLM evaluator if that can be avoided;
- the scientific unit should be the question / reasoning state or another defensible independent unit, not individual tokens treated as independent samples;
- the quantity should be comparable across checkpoints from the **same underlying training trajectory**;
- the analysis should make it possible to tell “local responsiveness changed” apart from “the model simply reasoned longer / reached different states.”

Raw endpoint compliance is useful as context and sanity checking, but it is not the load-bearing estimand.

---

# 5. Why the current design has two identification legs

The README names them E01A and E01B. Treat these as **roles that the evidence must play**, not sacred implementation scripts.

## E01A role — compare local gain at a shared observable history without relying on obviously OOD prefixes

The attractive idea is to hold the visible reasoning history fixed across checkpoints so trajectory length and visited-state differences cannot explain the result. The old version of this idea had a serious flaw: an identical teacher-forced prefix may be natural for an early checkpoint and extremely unlikely for a later checkpoint. Then a checkpoint trend could simply be an OOD/teacher-forcing artifact.

The current solution is a **common-support** principle. Shared histories should only be used when they are reasonably natural/reachable under every checkpoint and prompt arm being compared. Likelihood/NLL relative to each checkpoint's own natural prefixes is one plausible operationalization, but the agent is allowed to improve this if there is a stronger defensible support criterion.

The scientific role of E01A is:

> **At essentially the same externally observable reasoning history, does the causal effect of the constraint become weaker as reasoning RL proceeds?**

If the implementation changes, preserve that role and explicitly explain why the revised construction is less confounded.

## E01B role — verify the result on states each checkpoint actually visits

Even careful common-support matching may not completely remove concerns about teacher forcing or shared-prefix selection. Therefore we also need an intervention on **natural checkpoint-specific trajectories**.

The current proposal is to let each checkpoint reason naturally, intervene while it is still constraint-compatible, and compare a fresh constraint reminder against a matched neutral reminder on the same forked natural prefix. The reminder itself is not novel; it is a diagnostic perturbation.

The scientific role of E01B is:

> **When the checkpoint is in one of its own naturally visited states, how much can a freshly supplied constraint causally change the immediate future trajectory, and does that effect decline across reasoning training?**

Again, exact insertion locations, short horizon, wording, or measurement need not be copied mechanically if a better construction answers this question more cleanly.

The reason we want both roles is triangulation: E01A controls the state/history while E01B guarantees natural-state validity. A convincing training-induced local-gain claim should not depend on only one side.

---

# 6. Do not over-freeze details before inspecting the actual model flow

The current README mentions public OLMo-3/3.1 7B RL-Zero checkpoints because they provide the same-base training trajectory needed for the causal story. Verify the exact released model-flow/checkpoint structure and use the scientifically comparable checkpoints that actually exist.

Likewise, CoT-Control-style constraints are a strong starting point because the mother phenomenon and automatic checkers already exist. But do not blindly inherit every constraint. Prefer constraints for which **local compliance is genuinely interpretable over a short continuation**. Some constraints may only make sense globally at the end of a trace and therefore be poor instruments for this question.

The first implementation decisions should be driven by identification quality:

- Which constraints expose a clean local decision?
- Which checkpoints form a genuinely same-base reasoning-training trajectory?
- What constitutes a natural/common-support history for those checkpoints?
- At what kinds of natural states does a refresh intervention have an interpretable meaning?
- Which horizon is long enough to express the policy response but short enough not to reintroduce cumulative-opportunity confounding?
- Can the primary contrast be measured with low enough noise to make the pilot decisive at small scale?

Do a bounded design/support/noise audit before expensive expansion. It is fine if this audit changes implementation choices. It is **not** fine if it changes the scientific question after seeing the sign of the result.

---

# 7. Freedom granted to the executing agent

You are not being asked to reproduce a fixed sequence of commands. You are expected to reason about the experiment.

You may revise the exact checkpoint subset, question subset, constraint family, support criterion, reminder wording, insertion rule, horizon, local compliance statistic, or implementation architecture when there is a clear scientific reason. If you find a more convincing way to estimate the same local causal quantity, use it.

For every meaningful deviation, record:

> **What objection in the old design does this change solve? What new confound does it introduce? Does the resulting observation still discriminate opportunity accumulation from a genuine local controller change?**

Do not optimize those choices after looking for the most favorable checkpoint trend. Design flexibility is for better identification, not for sign hunting.

If you discover that the proposed estimand cannot actually be identified with these checkpoints/constraints, stop and report the blocker rather than fabricating a runnable proxy.

---

# 8. Scientific invariants that are not flexible

Several things *are* fixed because changing them would change the paper.

- The first question is **A versus {B,C}**, not B versus C.
- The headline quantity is the **causal effect of the constraint on continuation**, not raw compliance, probe accuracy, hidden-state similarity, or final task accuracy.
- The training comparison must retain a defensible same-base trajectory; a model-family cross-section cannot substitute for training causality.
- Length/opportunity must not be allowed to explain the positive result trivially.
- The matched-history result must not rely on obviously off-support teacher-forced states.
- A fresh-reminder effect itself is not novel; the question is how the effect changes over training.
- Do not run hidden-state probing, activation steering, patching, new training, or a large model zoo before the behavioral/causal gate is passed.
- Do not invent a fallback Main story after a null. A changed scientific identity must return to topic selection.

---

# 9. How to interpret the pilot without protecting the story

The current project is deliberately falsifiable.

### Both identification legs show a material decline in local gain

This is the result L29 needs. It would indicate that reasoning post-training changed the controller itself in a way that cannot be reduced to merely spending more tokens / accumulating more chances to fail, and the natural-state leg would make a pure teacher-forcing artifact much harder to maintain.

Do **not** immediately claim a specific internal mechanism. Report the behavioral-causal finding, quantify it, audit alternatives, then return to selection before deciding how to distinguish signal degradation from policy-attractor override.

### Local gain is approximately stable

Then Account A is sufficient for the present question: global control can collapse while instantaneous/local steerability remains largely preserved. That is a useful scientific answer, but the current Main paper should be killed because length/distance explanations and reminder recovery are already too well occupied.

### Shared-history gain declines but natural-state gain does not

Treat the apparent training effect as vulnerable to support/teacher-forcing artifacts. L29 has not established its headline claim. Diagnose only enough to verify the interpretation; do not rescue it with a representation statistic.

### Natural-state refresh gain declines but matched-history gain is stable

This suggests something different and potentially interesting: training may be moving the model into **different, less recoverable state distributions**, rather than weakening constraint leverage at the same history. That is not the current L29 claim. Preserve the evidence and formulate a new candidate only through re-selection.

### The effect is tiny or too noisy

Stop if the scientifically meaningful distinction cannot be resolved at a reasonable budget. Do not repeat the L19 mistake of scaling a weakly resolvable effect simply because compute exists.

---

# 10. Measurement and statistical discipline

Prefer paired comparisons wherever possible. Keep the unit of inference explicit. Repeated continuations can reduce Monte Carlo noise but do not create new independent questions/states.

Before interpreting checkpoint trends, understand the variance of the local causal contrast and the amount of common support that remains. A tiny common-support slice can create a highly selected population even if its likelihood threshold looks principled; inspect what kinds of states survive.

Do not report only an average curve. Look for obvious design pathologies such as one constraint family dominating the result, reminder wording changing the task, later checkpoints having systematically different support composition, or a compliance checker ceasing to mean the same thing across trajectory stages.

Heterogeneity can be reported diagnostically, but it should not become a new paper identity unless the conditioning variable was scientifically motivated rather than discovered by slicing until something works.

The purpose of the pilot is a **decision**, not a maximal table.

---

# 11. Expected implementation/research record

Follow `RESEARCH_EXECUTION.md`: every load-bearing conclusion should be traceable from claim → experiment → config/code → raw result → summary → interpretation.

Keep the L29 directory understandable to another researcher. As work proceeds, maintain a compact experiment record containing the scientific question for each run, the compared conditions, what changed besides the intended variable, exact models/checkpoints, prompts/constraints, decoding settings, support criterion, checker, random seeds where relevant, raw result path, summary statistics, and the conclusion the result actually licenses.

Do not dump large checkpoint files into git. Preserve model identifiers/revisions, commands/configs, hashes/manifests where useful, and enough metadata to reproduce the analysis.

Code and scripts should be organized around concepts rather than one-off shell commands. Do not touch unrelated candidate directories or clean up other users' files/processes on shared machines.

---

# 12. What I want you to report back after the first real study

Do not come back with only “E01 accuracy = X”. Explain the scientific answer.

A good report should make it possible to answer, in plain language:

> **Did reasoning RL actually make the model locally harder to steer, or did it mostly make the model reason for longer / reach trajectories where violations accumulate?**

Then show why the evidence supports that answer: what was intervened on, what causal contrast was measured, whether the shared-history and natural-state views agree, how large and resolvable the training change is, what important alternative explanations remain, and whether L29 should be **KILL / RECONSTRUCT / return to selection for mechanism work**.

Do not continue automatically after a positive pilot. The current authorization ends at E01A/E01B.

---

# 13. Literature anchors to understand, not mechanically imitate

Read the closest owners carefully enough to know what they already claim and what they actually measure:

- Yueh-Han Chen et al., **Reasoning Models Struggle to Control their Chains of Thought** / CoT-Control — mother phenomenon, length/training trend, same-base model-flow motivation.
- **MathIF** — constraint adherence under reasoning and the already-owned result that moving/repeating a constraint closer can help.
- Tan et al., **Compliance versus Sensibility: On the Reasoning Controllability in Large Language Models** — broad encoded-yet-not-followed / reasoning-prior story and activation steering.
- **Scaling Reasoning, Losing Control** and **ReasonIF** — broader reasoning versus instruction-following neighborhood.
- **Verifier-Induced Support Reshaping in On-Policy Optimization** — nearby evidence that RLVR can alter later behavioral support; useful context, not our claim.

Continue lightweight owner checking while executing. If a direct paper appears that already measures the same-base **training curve of local constraint→continuation causal gain** with adequate length/state controls, stop and reassess novelty rather than finishing experiments by inertia.

---

# 14. Compact identity reminder

If you remember only one thing, remember this:

> **L29 is not about whether reasoning models follow constraints. It asks whether reasoning post-training changes the instantaneous causal leverage that an explicit constraint has over the reasoning policy itself.**

The first pilot exists to distinguish that controller-change account from the simpler explanation that longer reasoning merely accumulates more opportunities to fail.

Experiment details may improve. **That scientific distinction must not drift.**
