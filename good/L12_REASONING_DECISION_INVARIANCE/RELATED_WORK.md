# L12 Live Related Work and Novelty Audit

**Search date:** 2026-09-10

## Direct owners

### Mind the (DH) Gap! - ACL 2026 Outstanding

<https://aclanthology.org/2026.acl-long.479/>

Owns the broad risky-choice result: reasoning models are less sensitive to order, gain/loss framing, explanation, and description/history presentation. L12 cannot claim that reasoning models are simply more rational or invariant.

### Reasoning Traces Shape Outputs but Models Won't Say So - ACL 2026

<https://aclanthology.org/2026.acl-long.1986/>

Owns generic causal evidence that injected reasoning changes outputs. Thus full-trajectory injection is substrate, not L12's paper identity.

### LLMs Faithfully and Iteratively Compute Answers During Chain-of-Thought - Findings EACL 2026

<https://aclanthology.org/2026.findings-eacl.59/>

Owns iterative answer computation during CoT in controlled arithmetic. E07 cannot be sold as the generic observation that answers form before the final token.

### Reasoning Fine-Tuning Induces Persistent Latent Policy States - COLM 2026

<https://arxiv.org/abs/2607.18532>

The closest new collision. It frames reasoning-tuned models as switching dynamical systems, identifies persistent latent policy states, and uses state swaps/transplants to argue that reasoning fine-tuning globally reorganizes latent dynamics. L12 therefore cannot claim generic latent policy states or global reorganization from reasoning fine-tuning.

### LLM Reasoning as Trajectories - ACL 2026

<https://aclanthology.org/2026.acl-long.1237/>

Finds step-specific representation geometry in mathematical CoT and argues that
reasoning training accelerates convergence toward termination-related subspaces;
trajectory steering changes correctness and reasoning length. It owns a geometric
trajectory account and late correctness divergence. It does not study presentation
invariance, independently intervene on prompt versus trajectory presentation, or
show that post-training-associated invariance coincides with causal-control
reallocation. L12 must therefore avoid selling generic late convergence or
"reasoning is a trajectory" as novelty.

### CASE: Causally Aligned Self-Explanation - 2026

<https://arxiv.org/abs/2607.18820>

Formalizes and trains an instruction-to-CoT-to-answer causal route while suppressing direct shortcuts. It is close to L12's control-route language, but it proposes a training method rather than explaining the established presentation-invariance transition.

### Making Reasoning Matter - Findings EMNLP 2024

<https://aclanthology.org/2024.findings-emnlp.882/>

Uses causal mediation across twelve LLMs and finds that models do not reliably use their intermediate reasoning steps, then proposes training to improve faithfulness. It owns neither the reasoning-post-training invariance transition nor L12's matched prompt-versus-trajectory control reorganization.

### Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps - EMNLP 2025 Outstanding

<https://aclanthology.org/2025.emnlp-main.504/>

Tests parametric faithfulness by unlearning reasoning steps across four models and five MCQA datasets. It raises the evidence bar for causal trace claims, but does not connect presentation invariance to a post-training-associated reallocation of control.

### Is Chain-of-Thought Really Not Explainability? - ACL 2026

<https://aclanthology.org/2026.acl-long.2217/>

Shows through causal mediation that non-verbalized hints can still affect predictions through CoT and cautions against lexical-only faithfulness judgments. This reinforces L12's use of causal state intervention rather than lexical trace inspection; it does not own the invariance mechanism question.

### Chain-of-Thought Faithfulness Varies with Where and How Preference Cues Are Delivered - 2026

<https://arxiv.org/abs/2608.29464>

FACE-Eval crosses cue location and explicitness over 5,100 samples and 15 models,
then measures verbalized commitment and unverbalized cue adoption. It establishes
that CoT faithfulness depends on cue delivery. It does not compare reasoning
post-training regimes, decompose prompt versus natural-trajectory control, study
equivalent risky-choice presentations, or intervene on a trajectory-built state.

### Mechanistic Interpretability of CoT via Sequential Activation Patching - 2026

<https://arxiv.org/abs/2608.22332>

Introduces sequential token/head patching for distributed CoT effects and validates
identified heads with ablations. It owns a method and evidence for distributed
reasoning-support subcircuits, so L12 must not sell temporal distribution or patch
localization alone. It does not explain an invariance transition or compare prompt
and trajectory control.

### Invariant Reasoning Directions in Latent Trajectories - 2026

<https://arxiv.org/abs/2606.29164>

Finds low-rank invariant refinement directions in latent-reasoning models and uses
them to improve paraphrase consistency. It owns latent geometric invariance and a
training-free intervention, not generated-CoT decision formation or the
presentation-to-trajectory causal reallocation studied here.

## Evidence-depth comparators

- **Racing Thoughts** (NAACL 2025): computational hypothesis, correlational evidence, causal evidence, then intervention. <https://aclanthology.org/2025.naacl-long.155/>
- **The LLM Language Network** (NAACL 2025): localization becomes scientifically useful only after causal ablation and breadth. <https://aclanthology.org/2025.naacl-long.544/>
- **Scaling Reasoning, Losing Control** (ACL 2026): reasoning-oriented training can trade off against external instruction control, but does not identify the internal route behind framing invariance. <https://aclanthology.org/2026.acl-long.1878/>

## Description-experience identification

### The Description-Experience Gap in Risky Choice - 2009

<https://doi.org/10.1016/j.tics.2009.09.004>

Hertwig and Erev synthesize evidence that description- and experience-based
choices can diverge, particularly in the impact of rare events. Crucially for
L12, finite experiential samples are not merely alternate wording: their observed
frequencies can differ from the generating distribution.

### Biased Samples, Not Mode of Presentation - 2009

<https://doi.org/10.1016/j.obhdp.2008.08.001>

Fox and Hadar directly argue that biased finite samples can explain apparent
experience effects. This makes E17/E18 unsuitable as a pure form-invariance test
and motivates holding the exact observed multiset fixed in E20.

### An Inquiry into the Nature and Causes of the Description-Experience Gap - 2022

<https://doi.org/10.1007/s11166-022-09393-w>

Cubitt and colleagues separate sampling bias, preferences, likelihood
representation, and memory in a unified design. Their model-free analysis finds
sampling bias to be the significant isolated driver while model-based analysis
allows a smaller residual gap without information differences. E20 imports this
identification logic into reasoning models: raw versus empirical summary isolates
form, while matched opposite empirical histories isolate evidence.

These papers own the form-versus-information distinction in human decision
science. L12's novelty is not that sampling error exists; it is that
reasoning-oriented post-training may relocate causal decision control toward an
evidence-bearing trajectory, yielding form invariance without evidence
insensitivity.

## Main-paper evidence calibration after E20-E21

| Structural comparator | What makes it Main-level | L12 alignment | Remaining gap |
|---|---|---|---|
| *Mind the (DH) Gap!* (ACL 2026 Outstanding) | A memorable behavioral puzzle established across 20 models, humans, and a rational baseline | L12 begins from its puzzle and contributes the missing causal explanation over 137 independent real decisions | Do not compete on model count or reclaim the parent phenomenon |
| *Racing Thoughts* (NAACL 2025 Main) | One computational hypothesis developed through correlational, causal, and intervention evidence | L12 now has process evidence, trajectory intervention, state substitution, and a falsification-driven form/evidence decomposition | Keep every result serving the sensitivity-reallocation explanation rather than accumulating patch variants |
| *The LLM Language Network* (NAACL 2025 Main) | Localization is followed by causal ablation and broad validation across 18 models | L12 moves beyond decodability/localization to direction-specific state transfer; OLMo and Qwen supply complementary controlled axes, and E22 adds bounded external-family behavior/control replication | L12 should not imitate an 18-model zoo; the remaining limitation is isolated training attribution |
| *What Makes a Good Reasoning Chain?* (EMNLP 2025 Main) | Chain structure explains failures across tasks/models and yields a Best-of-N consequence | L12 explains when apparent invariance should break and links the break to evidence carried by trajectory/state | The present weakest dimension is consequence/domain breadth, not another layer scan |
| *Persistent Latent Policy States* (COLM 2026) | Dynamics, state intervention, four benchmarks, 1.5B-32B breadth, and an inference-time use | L12 does not compete on generic state dynamics; it identifies what decision content gains control and why that produces selective invariance | Preserve the form-versus-evidence identity and avoid generic "reasoning creates states" language |

This calibration implies three load-bearing claims, not a longer list: decision
construction and consolidation; causal-control reallocation; selective sensitivity
to evidence rather than form. Probe accuracy, a particular layer, checkpoint
persistence, and another model family remain evidence underneath those claims.

## Strongest reviewer compression

> Mind the DH Gap + the decision-science sampling distinction + trace injection/persistent latent policy states.

This compression wins if L12 claims only that reasoning is causal, choices emerge through a trajectory, or a late hidden state can be swapped.

It does not own the complete L12 identity:

> an established presentation-invariance transition
> + matched sibling post-training branches
> + terminal-stripped distributed decision control
> + pre-answer choice-state mediation
> + a direct prompt-by-trajectory factorial showing that trajectory-relative causal control rises sharply in the reasoning branch
> + a prospective orthogonal form-by-evidence intervention showing that the new controller is selectively evidence-sensitive
> + direction-specific state substitution showing where that selective content becomes causally sufficient.

The unique center is not a generic latent state or the familiar observation that
sampling error exists. It is the **mechanistic explanation that reasoning
reallocates decision control away from presentation form and toward evidence
integrated through a trajectory-built causal state**.

## Novelty verdict after E21

**Paper identity survives and now has stimulus, checkpoint, complementary
model-family breadth, and untouched confirmation.** E09 remains essential:
without the control factorial, recent work compresses E07-E08. E12 shows that the
branch-level reorganization persists through official OLMo DPO continuations. E13
shows an aligned invariance/control transition in Qwen3 with weights fixed, under
an explicitly bounded native-route comparison.

This does not license the broad statement that every reasoning model uses an identical architecture. OLMo supplies the clean shared-base branch comparison and internal mediation evidence; Qwen supplies same-weight route triangulation; E14-E15 supply an external Llama-ecosystem replication and DeepSeek state mediation.

E17-E18 move the paper beyond a gain/loss curiosity and supply the productive
falsification. Exact distributions versus finite histories were not a pure
presentation manipulation: they changed observed evidence. E20 does not subgroup
the old results; it prospectively orthogonalizes those variables on 137 previously
unscored real histories. Under OLMo sibling and same-weight Qwen axes, reasoning
reduces form sensitivity while sharply increasing evidence sensitivity. E20-C
locates that selectivity in trajectory-relative control, and E21 shows that the
late causal state carries evidence direction far more strongly than form.

The strongest updated compression is:

> Mind the DH Gap + Persistent Latent Policy States + Sequential Activation
> Patching / FACE-Eval.

It still omits the complete L12 identity: an established invariance puzzle,
progressive construction, hidden-state mediation, matched prompt-by-trajectory
interventions, the heldout failure that exposes a construct confound, and a
prospective form-by-evidence decomposition showing that reasoning does not simply
remove sensitivity but redirects it toward evidence. E22 shows that the selective
behavior and evidence-trajectory control pattern also survives in the external
Llama ecosystem, while remaining explicitly non-attributive.
