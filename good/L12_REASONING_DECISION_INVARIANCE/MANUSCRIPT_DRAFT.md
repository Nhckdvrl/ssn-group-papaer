# Reasoning Changes What Models Are Sensitive To

## Causal Decision Control Shifts from Presentation Form to Evidence

**Target:** NAACL Main; calibrated to ACL/EMNLP Main  
**Draft status:** complete scientific narrative, pre-LaTeX  
**Date:** 2026-09-10

## Abstract

Reasoning models often make strikingly consistent decisions across changes in
framing and presentation. Why? Behavioral invariance could reflect robust
reasoning, loss of contextual information, or a policy that simply ignores its
input. We study the causal process behind this transition in risky choice. Natural
reasoning trajectories influence decisions well before their explicit conclusion
and consolidate their direction into a transferable pre-answer hidden state.
Crossing prompts with conclusion-stripped trajectories shows that reasoning-
oriented regimes shift relative decision control from prompt presentation toward
the trajectory. An untouched description/history evaluation then produces a
revealing failure: this control shift replicates, but behavioral invariance does
not always do so. The reason is that finite histories change not only form but also
observed evidence. We therefore prospectively orthogonalize form and evidence
using previously unscored histories over 137 decisions. Across OLMo sibling branches and Qwen3 with
fixed weights, reasoning decreases sensitivity to form while sharply increasing
sensitivity to evidence. Evidence-bearing trajectories, rather than prompts,
produce the corresponding causal shift, and state substitution shows that the
pre-answer state carries evidence direction far more strongly than form. The same
behavioral and trajectory-control pattern replicates in an external Llama
ecosystem. Reasoning thus does not make models indiscriminately invariant. It
changes what controls their choices, reallocating sensitivity from presentation
form toward evidence integrated through a self-generated trajectory.

## 1 Introduction

Reasoning-oriented post-training changes more than benchmark accuracy. Reasoning
models are less affected by option order, gain/loss framing, explanation, and the
presentation of risky prospects as descriptions or outcome histories
([Ge et al., 2026](https://aclanthology.org/2026.acl-long.479/)). This pattern is
appealingly described as rationality or invariance. Yet the behavior alone leaves
the central computational question unanswered: **what changed in how the model
forms its decision?**

Several explanations are compatible with the same stable answer. Reasoning
training may canonicalize equivalent inputs, removing their task-relevant
differences. The model may retain presentation information but suppress its use at
a late policy readout. Alternatively, a long self-generated trajectory may become
the dominant causal route to the answer, progressively constructing a decision
state that overrides the direct influence of the prompt. These accounts disagree
about what information remains, where the decision forms, and which intervention
should change it.

We trace this process from prompt to trajectory, pre-answer state, and final
choice. Frame information remains recoverable in early and middle prompt
representations, weakening simple erasure. Natural trajectories retain causal
decision direction after their explicit conclusions are removed. Substituting an
opposite-decision residual state transfers that direction without inserting donor
reasoning text. Most importantly, a prompt-by-trajectory factorial shows that
reasoning-oriented regimes assign substantially more relative control to the
trajectory than standard instruction regimes.

Our heldout study initially seems to break this account. The trajectory-control
shift confirms in both OLMo and Qwen, while OLMo's description/history invariance
does not. Inspecting the construct reveals why: an exact generating distribution
and a finite outcome history are not information-equivalent. A history can provide
empirical evidence for the opposite choice. What looked like a pure presentation
test had varied both the wrapper and the evidence.

This failure leads to the paper's decisive experiment. Using previously unscored
real-history cells, we cross two evidence directions with two exactly evidence-
preserving forms: a raw trial sequence and its empirical frequency summary.
Reasoning models become almost invariant to the form while becoming much more
sensitive to the evidence. Crossed causal interventions locate the change in
evidence-bearing trajectories, and state substitution finds the same selectivity
inside the pre-answer state. The pattern holds under a common-base OLMo sibling
comparison, a same-weight Qwen route comparison, and a bounded external
Llama/DeepSeek replication.

Our contribution is a single explanatory chain:

1. **Decision construction and consolidation.** Natural reasoning develops
   causal decision direction before explicit commitment and consolidates it into
   a transferable pre-answer state.
2. **Causal-control reallocation.** Reasoning-oriented computation shifts final-
   decision control from prompt-level presentation toward the trajectory and the
   state it builds.
3. **Selective sensitivity.** This reallocation suppresses sensitivity to
   representational form while preserving or amplifying sensitivity to decision
   evidence.

The distinction matters beyond risky choice. A model that repeats an answer after
receiving different information is not robust in the same sense as one that
ignores a harmless reformatting. Reasoning robustness should therefore be tested
by independently manipulating form and evidence, not by treating every change in
presentation as information-preserving.

## 2 Related Work

### Reasoning models and decision invariance

*Mind the (DH) Gap!* establishes the parent phenomenon over 20 open and frontier
models, with human and expected-payoff baselines. It owns the broad finding that
reasoning and conversational models differ in risky choice. We instead ask which
causal route controls the decision and why invariance appears for some input
changes but not others. Work on framing and instructed bias likewise establishes
behavioral or representational sensitivity, but does not separate availability
of a cue from its causal use in a reasoning-trained decision policy.

### Causal roles of reasoning trajectories

Injected reasoning can change outputs even when models fail to report its
influence ([Hao et al., 2026](https://aclanthology.org/2026.acl-long.1986/)).
Other work studies iterative answer computation, CoT faithfulness, distributed
reasoning circuits, and trajectory geometry. These results make generic
"reasoning affects answers" or "the answer forms over tokens" claims
insufficient. Our object is the comparative allocation of control between prompt
and trajectory, followed through a text-free internal carrier and tied to the
specific behavioral invariance puzzle.

Persistent latent policy states are especially close: reasoning fine-tuning can
produce stable internal dynamics whose states can be transplanted
([Harrasse et al., 2026](https://arxiv.org/abs/2607.18532)). We do not claim generic
latent-state formation. We identify what decision content gains causal control:
evidence direction rather than presentation form.

### Mechanistic explanations in NLP

Our evidence progression follows the standard set by mechanistic Main papers.
*Racing Thoughts* moves from a computational hypothesis to correlational evidence,
causal tests, and an intervention
([Lepori et al., 2025](https://aclanthology.org/2025.naacl-long.155/)). *The LLM
Language Network* treats localization as a beginning and establishes causal role
and cross-model breadth. We likewise use decodability only as a constraint, then
require directional text interventions, state transfer, and independent-stimulus
replication.

### Description versus experience

Decision science has long distinguished a true mode-of-presentation effect from
sampling error in finite experience. Observed frequencies may differ from the
generating distribution, so description and experience can contain different
decision evidence. This literature owns the sampling distinction. Our use of it
is mechanistic: orthogonalizing form and evidence reveals what reasoning
trajectories and their causal states selectively track.

## 3 Causal Setup

### 3.1 Variables and estimands

We represent decision formation as

```text
prompt P -> reasoning trajectory R -> pre-answer state H -> choice Y,
```

while allowing direct paths from the prompt to the state and answer. The graph
does not assume faithful verbalization or complete mediation.

For a binary decision, let `m(p,r)` be the probability or A/B margin for a
reference choice after prompt `p` and conclusion-stripped trajectory `r`. Crossing
two prompts and two trajectories gives

```text
Delta_P = 1/2 ([m(p1,r1)-m(p2,r1)] + [m(p1,r2)-m(p2,r2)])
Delta_R = 1/2 ([m(p1,r1)-m(p1,r2)] + [m(p2,r1)-m(p2,r2)])
Delta_control = Delta_R - Delta_P.
```

`Delta_P` measures prompt control with trajectory fixed; `Delta_R` measures
trajectory control with prompt fixed. `Delta_control` is an interventional control
index, not a natural indirect effect or the causal effect of training.

In the form-by-evidence study, `p_A(e,f,o)` is the conditional probability of the
underlying option A for evidence direction `e`, form `f`, and displayed order `o`.
We define form sensitivity as the mean absolute raw-versus-summary difference at
fixed evidence, evidence sensitivity as the signed A-evidence minus B-evidence
difference at fixed form, and selective sensitivity as evidence sensitivity minus
form sensitivity. All quantities are first computed within base decision.

### 3.2 Models and identification axes

Our deepest comparison uses `Olmo-3-7B-Instruct-SFT` and
`Olmo-3-7B-Think-SFT`, sibling branches from a common OLMo base. DPO checkpoints
test persistence along both branches. Qwen3-8B supplies a complementary
same-weight comparison through its official thinking and non-thinking routes.
Finally, Llama-3.1-8B-Instruct and DeepSeek-R1-Distill-Llama-8B provide an external
ecosystem replication.

The axes answer different questions. OLMo supports a training-regime-associated
contrast, Qwen fixes weights but compounds reasoning route with native channel
placement, and Llama/DeepSeek changes training data, pipeline, template, tokenizer,
and configuration. We never treat the external pair as a one-variable training
experiment.

### 3.3 Decisions and outcomes

Mechanism discovery reconstructs the three prospects from the parent work. A
frozen 36-decision set then varies payoff scale, EV gap, and probability/payoff
tradeoff without dominance, ties, duplicates, or affine-equivalent units.

For natural breadth, we use CPC18 risky-choice problems and real human outcome
histories. Exact expected payoff supplies model-independent gold; human choices
never label model answers. Frozen inclusion retains known probabilities,
independent outcomes, non-tied EV, manageable support size, and at least three
distinct histories. This yields 151 calibration decisions and 44 untouched
competition decisions.

The decisive form-by-evidence study uses 137 base decisions from the frozen CPC18
pools but selects real histories and form-by-evidence cells that were not used in
the hypothesis-generating analysis. For each decision, one real history
empirically favors A and another favors B.
Evidence strengths are matched with ratio at most 1.5 and minimum normalized gap
0.02. Each history appears as either its ordered 20-trial table or an exact
frequency summary of the same observations. No model output enters selection.

### 3.4 Inference and execution validity

The base decision is the unit of inference. We use 5,000-draw base-decision
bootstrap intervals, preserving histories, orders, generations, directions, and
layers as nested variation. Invalid answers remain in execution counts. We report
conditional estimates and sharp worst/best assignment bounds when invalidity can
affect conclusions.

Prompts use both displayed option orders. The terminal parser maps shown labels
back to underlying options. Strict reasoning traces require a closed reasoning
block, a valid terminal answer, a nonempty prefix, and removal of explicit
commitment language. Result manifests record raw byte counts, row counts, and
SHA-256 hashes; raw continuations remain outside Git.

## 4 Decisions Form Along the Natural Trajectory

### 4.1 Frame information is not simply erased

The OLMo sibling pilot reproduces the parent substrate: frame consistency is
0.992 for Think-SFT and 0.750 for Instruct-SFT on the parent prospects. Yet frame
identity remains linearly recoverable in early and middle prompt representations.
This diagnostic cannot show causal use, but it rules against the cheapest account
in which reasoning training simply deletes presentation information everywhere.

### 4.2 Control develops before explicit commitment

We insert natural Think-SFT trajectories before answer decoding. A full own-
decision trajectory shifts the choice margin by +9.34 relative to an empty
prefix, while an opposite-frame trajectory shifts it by -9.07. Short answer-free
arithmetic snippets do not reproduce this effect, routing the explanation away
from a generic calculation fragment.

We next remove the suffix beginning with the first directional comparison or
explicit commitment. The remaining own trajectory still exceeds empty by
**+2.624 [2.008, 2.988]** and an opposite stripped trajectory by **+4.863
[3.469, 5.773]**. Restoring the terminal portion adds **+7.047 [6.746,
7.402]**. Thus control is distributed through the reasoning process, but the
final commitment strongly consolidates it. We do not claim that the conclusion
is irrelevant.

### 4.3 A pre-answer state carries the constructed decision

To test whether the text effect has an internal carrier, we substitute the
donor's final-prefix residual state into an opposite-decision target without
inserting donor text. Effects are negligible early, rise in middle/late layers,
reverse mean target margin at layer 17, and reach **+5.090 [3.766, 5.977]** at
the final layer.

The profile replicates on a frozen 18-decision subset, with final donor shift
**+4.868 [4.056, 5.813]**, positive for all 18 decisions. On 48 natural CPC18
decisions, mean margin first reverses at layer 18 and final donor shift reaches
**+7.094 [5.914, 8.276]**, positive for 45/48 decisions. DeepSeek shows a
weaker but positive external correlate, **+1.222 [0.299, 2.181]**. The
scientific object is a sustained late carrier, not a privileged layer number.

## 5 Reasoning Reallocates Causal Control

The state results show what can carry a decision, but not whether reasoning-
oriented computation relies on that route more strongly. We therefore cross
prompt frames with the same conclusion-stripped trajectories and score all four
factorial cells under each regime.

On the discovery prospects, Think-SFT trajectory control is +0.586 while
Instruct-SFT trajectory control is +0.012. Across 36 independent decisions, the
Think-minus-Instruct change in `Delta_control` is **+0.399 [0.337, 0.464]**,
positive on 36/36. The OLMo DPO contrast persists at **+0.472 [0.401,
0.555]**. With Qwen weights fixed, the thinking route exceeds non-thinking by
**+0.604 [0.550, 0.661]**.

The effect generalizes from gain/loss framing to exact descriptions versus real
outcome histories. Across 151 calibration decisions, reasoning-minus-standard
`Delta_control` is **+0.202 [0.162, 0.244]** for OLMo and **+0.163 [0.121,
0.205]** for Qwen; prompt-control differences include zero. On 44 untouched
competition decisions, the preregistered gate passes for both OLMo (**+0.097
[0.002, 0.180]**) and Qwen (**+0.219 [0.152, 0.288]**).

However, the supporting behavioral results diverge. Qwen becomes more consistent
across description/history on heldout decisions (**+0.163 [0.051, 0.268]**),
whereas OLMo does not (**-0.013 [-0.095, 0.065]**). Increasing sampling from
three to twenty generations per cell leaves the OLMo estimate null. Stronger
trajectory-relative control is real, but blanket presentation invariance is not
its automatic consequence.

## 6 The Failure Reveals Selective Sensitivity

### 6.1 Description and finite history change different things

An exact description reports the generating distribution. A 20-trial history
reports one finite realization whose empirical means may favor the opposite
choice. Description/history therefore changes both representational form and
decision evidence. A post-hoc audit of the completed data exposes this confound,
but supplies no confirmatory claim. It motivates a new prospective experiment on
previously unscored histories.

### 6.2 Orthogonalizing form and evidence

For every base decision, we cross evidence favoring A or B with raw-sequence or
frequency-summary form. Raw and summary contain the identical payoff multiset.
This design separately asks whether a model changes its choice when the wrapper
changes and when the observed evidence changes.

The answer is sharp. OLMo reasoning reduces form sensitivity by **-0.341
[-0.364, -0.317]** and increases evidence sensitivity by **+0.888 [0.865,
0.911]**, yielding a selective shift of **+1.229 [1.195, 1.262]**. Under
Qwen's same weights, the corresponding changes are **-0.266 [-0.291,
-0.241]**, **+0.443 [0.397, 0.491]**, and **+0.709 [0.638, 0.778]**. The
joint selective difference remains positive under sharp invalid-output assignment
on both axes. OLMo Think has a lower valid rate (0.704): its joint selective
difference remains positive under sharp assignment, but the form-only component
does not. We therefore treat the OLMo form decrease as conditional and the joint
selective shift as the robust result.

This is not broad insensitivity. Reasoning regimes are more invariant when form
changes and far more responsive when evidence changes. The heldout OLMo result
was not a failed mechanism: it combined cases in which a trajectory should build
the same decision with cases in which changed evidence should build a different
one.

### 6.3 The evidence is carried by the trajectory

We cross prompt evidence with stripped natural trajectories that followed either
evidence direction, separately within raw and summary form. OLMo reasoning-minus-
standard `Delta_control` is **+0.459 [0.401, 0.518]** for raw histories and
**+0.584 [0.532, 0.638]** for summaries. Qwen effects are **+0.563 [0.506,
0.621]** and **+0.749 [0.689, 0.808]**. Prompt evidence-control differences
are near zero; the shift comes from the trajectory.

Thus the behavioral result and the causal-control result concern the same
computation. Reasoning does not merely produce evidence-sensitive answers beside
an unrelated trajectory takeover effect. The evidence-bearing trajectory itself
gains relative causal control.

### 6.4 The same selectivity appears in the internal carrier

Within OLMo Think-SFT, we construct four natural prefixes per decision: two forms
by two evidence directions. For every target, we substitute donor states while
changing evidence and form independently. At the final layer, changing donor
evidence moves underlying-A probability by **+0.763 [0.694, 0.828]**, whereas
donor-form sensitivity is **0.174 [0.124, 0.227]**. Their preregistered
difference is **+0.590 [0.476, 0.704]**, positive on 30/32 decisions.

Evidence control is near zero at layers 0 and 8, appears at layer 16, and rises to
0.748/0.763 at layers 24/31. The trajectory-built state does not erase form
completely. It becomes a selective causal carrier whose evidence direction matters
far more than whether that evidence arrived as a sequence or summary.

### 6.5 External replication

We repeat the full behavioral decomposition in the Llama ecosystem. Relative to
Llama-Instruct, DeepSeek-R1-Distill changes form sensitivity by **-0.139
[-0.159, -0.119]**, evidence sensitivity by **+0.857 [0.839, 0.876]**, and
selective sensitivity by **+0.996 [0.962, 1.031]**, positive on 137/137
decisions. The joint result remains positive under sharp invalid assignment.

The external causal factorial also agrees: DeepSeek-minus-Llama trajectory-
relative evidence control is **+0.175 [0.131, 0.221]** in raw form and
**+0.143 [0.106, 0.180]** in summary form. Prompt-control differences are only
+0.0046 and +0.0021. This comparison cannot attribute the effect to a single
training operation, but it shows that selective trajectory control is not an
OLMo-specific curiosity or a Qwen template switch alone.

## 7 Discussion

### Invariance is selective

Our results change the interpretation of reasoning-model robustness. Reasoning
does not simply attenuate contextual influence. It changes which contextual
variation reaches the decision: representational form loses control, while
decision evidence gains it. A stable choice is therefore informative only when
the intervention truly preserves evidence.

### Trajectory takeover is not prompt blindness

The phrase "trajectory takeover" can suggest that a model stops listening to its
input. The evidence argues for a more useful account. The prompt supplies evidence;
the trajectory integrates it; a late state carries the integrated direction into
decoding. When evidence changes, the trajectory and answer change with it. Control
moves away from the prompt surface, not away from the information in the prompt.

### Generated reasoning is part of the decision policy

The trajectory is neither a guaranteed faithful explanation nor inert narration.
It is a causal component whose content can dominate final decoding and whose
internal endpoint can transfer the choice without donor text. This helps reconcile
apparently conflicting observations about CoT faithfulness: a trace can be causal
without verbally exposing every input influence, and an internal state can mediate
the decision without one token or layer being the entire mechanism.

### Consequence for evaluation

Robustness evaluations frequently compare paraphrases, formats, demonstrations,
or histories under the assumption that the underlying information is constant.
Our results show why that assumption must be audited. A useful evaluation should
cross evidence-preserving form transformations with evidence-changing controls.
Only then can invariance be distinguished from a failure to update.

## 8 Limitations

First, none of our public model axes isolates one optimization step. OLMo offers
the cleanest common-base sibling comparison, Qwen fixes weights but changes native
route and channel placement, and Llama/DeepSeek is unmatched. The convergent result
supports a reasoning-regime-associated computation, not a universal causal effect
of a named training recipe.

Second, the deepest state intervention is in OLMo. DeepSeek supplies earlier
external state triangulation, while the exact selective form/evidence state
factorial is not repeated in every family. Our claim concerns the replicated
behavior/control pattern and an identified internal carrier in the discovery
family, not identical layer geometry across architectures.

Third, inserted trajectories are mediator interventions implemented as text. They
identify route-specific control under the intervention but are not natural indirect
effects. State substitution further shows a text-free carrier, yet does not prove
complete mediation.

Fourth, the decisions are binary risky choices with independently computable
payoff evidence. This domain provides unusually clean identification. Whether the
same selective reallocation holds for open-ended factual, social, or normative
decisions remains open.

Fifth, reasoning generations sometimes fail to close before the token cap. We
retain invalids and report sharp bounds. A paired 20/100-history diagnosis becomes
uninterpretable at 100 trials because long raw tables cause severe truncation; it
is reported as an inconclusive audit rather than used as evidence.

## 9 Ethics and Reproducibility

CPC18 histories are derived from an existing human decision experiment. We export
only payoff histories and never participant identifiers. Human choices are not
used as gold labels. Frozen PII-free decision files, exact model revisions,
prompts, parsers, selection rules, statistical code, compact unit metrics, and
execution audits are included. Large model outputs and public source files remain
outside Git, with byte counts and cryptographic hashes recorded for verification.

All headline intervals resample independent base decisions. Repeated generations,
histories, orders, trajectories, patch directions, and layers are never counted as
independent scientific units.
