# L12 ACL/EMNLP/NAACL Main Paper Outline

## Working title

**Reasoning Changes What Models Are Sensitive To**

Alternative subtitle: **Causal Decision Control Shifts from Presentation Form to Evidence**

## One-sentence identity

> Reasoning-oriented computation does not make language models indiscriminately
> invariant: natural trajectories progressively build a causal decision state
> that becomes comparatively insensitive to presentation form while remaining
> sharply responsive to decision evidence.

## Abstract logic

1. **Puzzle:** reasoning models appear unusually invariant to framing and
   presentation, but invariance alone cannot distinguish robust reasoning from
   insensitivity or a stable response bias.
2. **Process:** terminal-stripped natural reasoning already carries decision
   direction; the final commitment amplifies rather than creates it.
3. **Carrier:** direction-specific state substitution shows that the trajectory
   consolidates its decision into a late pre-answer causal state.
4. **Control transition:** prompt-by-trajectory factorials show that reasoning
   regimes give the self-generated trajectory substantially more relative control
   than standard instruction regimes.
5. **Productive failure:** this control shift confirms on heldout CPC18 decisions,
   yet OLMo's description/history invariance does not. The apparent contradiction
   reveals that finite histories changed evidence as well as form.
6. **Decisive decomposition:** on 137 previously unscored real decision units,
   orthogonal form-by-evidence interventions show that reasoning reduces form
   sensitivity while increasing evidence sensitivity.
7. **Mechanistic closure:** the selective behavioral shift is reproduced in
   evidence-bearing trajectory control and in the content of the pre-answer state.
8. **Breadth:** the result holds under OLMo sibling branches, a same-weight Qwen
   route comparison, and an external Llama/DeepSeek ecosystem comparison.
9. **Takeaway:** reasoning changes what controls the choice and therefore what
   kinds of variation a model ignores, rather than simply making it invariant.

## Three major claims

### C1. Trajectories construct and consolidate decisions

Natural reasoning develops causal decision direction before explicit commitment
and consolidates it into a transferable pre-answer state. E07 establishes
progressive construction; E08/E11/E19 establish the sustained internal carrier;
E15 supplies bounded external triangulation. No particular layer is a claim.

### C2. Reasoning reallocates causal control

Reasoning-oriented computation shifts final-decision control from prompt-level
presentation toward the trajectory and state it builds. E09-E10 are the core
matched branch bridge; E12 shows checkpoint persistence; E13 fixes weights under
Qwen's native route switch; E17-E18 supply natural-stimulus and heldout breadth.

### C3. The reallocation is selectively evidence-sensitive

Reasoning suppresses sensitivity to representational form while preserving or
amplifying sensitivity to decision evidence. E20 orthogonalizes form and evidence
prospectively; E20-C locates the shift in evidence-bearing trajectory control;
E21 shows the same selectivity in the late causal state; E22 supplies external-
family behavior/control replication. This is the paper's crown.

## Narrative progression

### Act I: Why invariance is ambiguous

Reproduce the parent phenomenon, then show that presentation identity remains
available. This rules out a simple erasure story but is only the setup.

### Act II: Who controls the choice?

Use natural terminal stripping, opposite trajectories, and direction-specific
state substitution to show progressive construction and consolidation. Cross
prompt and trajectory rather than treating generic trace injection as novelty.

### Act III: The heldout result that changes the question

Show that route reorganization survives where OLMo description/history invariance
does not. Do not narrate this as a failed replication to be explained away. It
exposes a construct error: raw finite histories are not information-equivalent to
their generating distributions.

### Act IV: What should reasoning ignore?

Introduce the prospective 2 form x 2 evidence experiment. The memorable result
is a relocation in the sensitivity plane, not a subgroup p-value: all three model
axes move away from form and toward evidence. Trajectory factorial and state
substitution establish that this is one causal mechanism.

### Act V: Consequence

Use the paired 20/100 history diagnosis to show how finite-sample evidence changes
the behavioral appearance of invariance. Keep it as a consequence of the account,
not a fourth claim. The paper ends with a practical interpretive warning: observed
robustness is meaningful only after separating harmless changes in representation
from changes in decision evidence.

## Main figures and tables

1. **Figure 1 - Puzzle and causal alternatives:** prompt form/evidence to
   trajectory, state, and answer; erasure, direct prompt control, and trajectory
   mediation make different intervention predictions.
2. **Figure 2 - Progressive construction and consolidation:** full, stripped,
   opposite-stripped, and empty trajectories beside the broad state-transfer
   layer profile.
3. **Figure 3 - Causal-control reorganization:** `Delta_P` versus `Delta_R` under
   OLMo siblings, Qwen same weights, and checkpoint/external evidence.
4. **Figure 4 - Selective sensitivity:** the tracked three-panel artifact
   `results/selective_sensitivity_story/`: behavior-plane arrows, trajectory-
   relative evidence control, and late state selectivity.
5. **Table 1 - Identification axes:** common-base OLMo siblings, Qwen native
   same-weight routes, and unmatched Llama ecosystem, with exact allowed claims.
6. **Table 2 - Evidence breadth:** independent decision counts, calibration versus
   heldout status, repeated generations, valid rates, clustered intervals, and
   sharp invalid-output bounds.
7. **Figure/Table 5 - Finite-history consequence:** paired 20/100 evidence
   agreement and description/history consistency; supporting, not headline.

## Evidence scale

- **Independent stimuli:** 36 controlled gain/loss units; 151 CPC18 calibration
  decisions; 44 untouched competition decisions; 137 new form-by-evidence units.
- **Mechanistic depth:** natural trajectory construction, crossed prompt/trajectory
  interventions, and direction-specific text-free state substitution.
- **Model/training axes:** OLMo SFT siblings plus DPO persistence; Qwen3 same
  weights under native thinking/non-thinking routes; Llama-Instruct versus
  DeepSeek-R1-Distill as bounded external replication.
- **Statistics:** base decision is always the scientific unit. Histories, orders,
  generations, trajectory samples, directions, and layers are nested observations.

## Main-level calibration

- Like *Racing Thoughts*, the paper advances one computational explanation from
  behavioral puzzle through causal process to intervention evidence.
- Like *The LLM Language Network*, representation/localization is not the endpoint;
  direction-specific state substitution establishes causal role and breadth.
- Like *What Makes a Good Reasoning Chain?*, trajectory analysis culminates in an
  explanation of failure/boundary and a consequence, rather than another metric.
- Unlike *Mind the (DH) Gap!*, L12 does not compete on model-count breadth; it owns
  the causal explanation and uses complementary identification axes.
- Unlike *Persistent Latent Policy States*, L12 does not claim generic reasoning
  dynamics; it identifies which content gains causal control and why behavioral
  invariance is selective.

## Reviewer compression defense

**Strongest compression:** *Mind the DH Gap* + decision-science sampling bias +
trace injection/persistent latent policy states.

**Why it fails:** those works separately own the behavioral puzzle, the fact that
finite experience changes evidence, and generic causal reasoning/state effects.
They do not show that reasoning post-training reallocates decision control, use a
prospective orthogonal form-by-evidence intervention to identify what the new
controller tracks, or connect that selectivity from natural trajectory to a
direction-specific internal state across sibling, same-weight, and external axes.

## Interpretation boundaries

- Do not call consistency rationality without evidence-sensitive behavior.
- Do not call frame decodability causal use or non-decodability erasure.
- Do not claim terminal commitments are irrelevant; they strongly amplify control.
- Do not claim the state is form-free; its evidence effect is comparatively larger.
- OLMo supports training-regime association, not attribution to one optimization
  step. Qwen's official switch also changes native route/position. Llama/DeepSeek
  is external replication, never a matched training contrast.
- Repeated generations and patched layers do not inflate the independent sample.

## Submission-readiness gate

Before paper drafting, regenerate all summaries/figures from tracked code, run
parser/coordinate/factorial validators, verify local raw hashes, and preserve the
calibration/heldout chronology. Further experiments require a load-bearing gap in
this three-claim story; another model, layer, or prompt variant by itself is not a
contribution.
