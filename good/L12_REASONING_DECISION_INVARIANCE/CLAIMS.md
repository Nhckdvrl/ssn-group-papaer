# L12 Claim Ledger

**Updated:** 2026-09-10

## Current RQ

> Why do reasoning models become invariant to some changes in presentation while remaining sharply sensitive to others, and does reasoning reorganize decision control from prompt form toward an evidence-bearing trajectory and its pre-answer state?

## Major claim chain

| ID | Claim | Evidence | Current status |
|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | *Mind the (DH) Gap!* | **Established prior; not ours** |
| **L12-C1** | Natural reasoning progressively constructs a decision before explicit commitment and consolidates it into a pre-answer causal state. | E05-E08 + E11 + E19; E15 triangulation | **Supported from process to internal carrier; 48-decision natural-stimulus breadth and external state triangulation** |
| **L12-C2** | Reasoning-oriented computation reallocates causal control from prompt-level presentation toward the self-generated trajectory and the state it builds. | E09-E10 + E12-E14 + E17-E18 | **Confirmed under OLMo sibling and same-weight Qwen axes, checkpoint persistence, an untouched natural split, and bounded external replication** |
| **L12-C3** | The reallocation is selective rather than indiscriminate: sensitivity falls for representational form while rising for decision evidence, and this selectivity is carried by the same late pre-answer state. | E20 behavior + E20-C + E21 | **Prospectively confirmed on 137 real CPC18 decisions under both controlled axes; external-family test E22 in progress** |

## Supporting evidence, not headline claims

| ID | Result | Role |
|---|---|---|
| **L12-S1** | Think-SFT frame consistency is 0.992 versus 0.750 for sibling Instruct-SFT. | Reproduces the behavioral substrate on the three parent prospects using order-conditional consistency. |
| **L12-S2** | Frame identity remains linearly recoverable through early/middle prompt representations. | Rules against a simple information-erasure story; probe evidence is not causal use. |
| **L12-S3** | Full own/opposite trajectories produce margins +9.34/-9.07, while short arithmetic snippets do not reproduce that effect. | Routes the mechanism toward the natural trajectory rather than a generic calculation fragment. |
| **L12-S4** | DeepSeek's opposite-decision pre-answer state produces a late donor-directed shift of +1.222 [0.299, 2.181]. | External triangulation for C2 without making a new layer-localization claim. |
| **L12-S5** | C3 persists at OLMo DPO checkpoints, under Qwen3's same-weight mode switch, and in the Llama/DeepSeek ecosystem. | Checkpoint, route, and family breadth for C3; these are not additional headline claims. |

## Interpretation discipline

- E07 supports **distributed control plus terminal amplification**, not the stronger statement that the terminal commitment is irrelevant. Stripping retains a +2.62 margin effect over empty, while the terminal portion adds +7.05.
- E08 supports a coherent decision-state profile: transfer is negligible through layer 13, rises at 14-16, reverses the mean target margin at layer 17, and remains strong thereafter. The paper claim is not that one layer is the mechanism.
- E09 is the mechanism-phenomenon bridge. Its scientific object is branch-specific prompt-versus-trajectory control, not merely an injected-text effect.
- E12 shows persistence, not that DPO created the original divergence. The DPO Think-minus-Instruct control difference is +0.472 [0.401, 0.555], positive on 36/36 decisions; its increase over the frozen SFT difference is a secondary +0.073 [0.016, 0.133].
- E13 provides a second model family and fixes weights, but its official modes necessarily place stripped text in different native channels. It identifies route-dependent integration, not an unobserved switch or a pure effect of extra test-time tokens.
- E14 aligns behavior and mechanism under external replication. DeepSeek-R1-Distill exceeds Llama-Instruct in trajectory-minus-prompt control by +0.067 [0.037, 0.099] and in frame consistency by +0.947 [0.913, 0.976]. The comparison is not a one-variable training attribution.
- E15 verifies that DeepSeek's external text-level result has an internal mediation correlate. Its late effect is weaker and less unit-universal than OLMo's, so do not claim identical layer geometry across families.
- E17 generalizes C3 from gain/loss framing to explicit distributions versus
  real outcome histories. The reasoning-minus-standard `Delta_R - Delta_P`
  contrast is +0.202 [0.162, 0.244] for OLMo and +0.163 [0.121, 0.205]
  for same-weight Qwen. Prompt-control differences include zero; the transition
  is specifically trajectory-relative.
- The unmatched Llama/DeepSeek E17 axis is a genuine boundary: its control
  contrast is +0.019 [-0.005, 0.043], while behavioral consistency decreases.
  Llama-Instruct's high consistency accompanies chance-level EV choice, so
  invariance alone must never be labeled rationality.
- E17's preregistered random-slope MixedLM did not converge for any pair. Its
  coefficients are retained as an audit artifact but not used as confirmation;
  the primary base-decision cluster bootstrap was specified in advance and
  carries all E17 inference.
- E19 supplies natural-stimulus mediation breadth for C2. Across 48 frozen base
  decisions and symmetric opposite-choice patches, the mean state intervention
  first reverses target margin at layer 18 and reaches +7.094 [5.914, 8.276]
  at the final layer; 93.8% of base-decision shifts are positive. Interpret the
  sustained late profile, not layer 18 as an isolated mechanism.
- E18 passes its preregistered primary decision rule on both controlled axes,
  while OLMo's supporting behavioral consistency hypothesis does not. E18 first
  falsified indiscriminate invariance; E20 then prospectively identifies the
  omitted distinction: a finite history changed observed evidence as well as
  form.
- E20 is not a post-hoc subgroup rescue. It freezes 137 previously unscored real
  histories and orthogonalizes form and evidence. Its selective-sensitivity shift
  is +1.229 [1.195, 1.262] for OLMo and +0.709 [0.638, 0.778] for same-weight
  Qwen. E20-C ties the behavior specifically to evidence-bearing trajectory
  control rather than increased prompt sensitivity.
- E21 closes the mechanism-behavior bridge at the internal carrier: final-layer
  donor evidence control is +0.763 [0.694, 0.828], versus donor-form sensitivity
  0.174 [0.124, 0.227]. The claim is comparative selectivity, not form erasure.
- The released OLMo checkpoints are sibling branches from a common base. They support a training-regime-associated contrast, not strict attribution to one isolated optimization step.
- E10 uses 36 independent base decisions and E11 uses a preregistered 18-decision stratified subset. Repeated traces and layers remain within-unit observations.
- The corrected exploratory decision-level association between the behavioral branch difference and control difference is unsupported (rho = -0.001, p = 0.997). Do not claim monotonic per-item coupling; the supported bridge is the matched branch/mode/family-level reorganization replicated across units.

## Current verdict

**GO.** The current paper has one cumulative answer rather than three adjacent
interpretability results: reasoning progressively builds a causal decision state,
reallocates control toward that trajectory/state, and thereby changes what the
model is sensitive to. E20-E21 prospectively show that the change is selective:
form sensitivity falls while evidence sensitivity and evidence-bearing trajectory
control rise. E22 now tests whether this crown is broader than the controlled
OLMo/Qwen axes; E18L tests the finite-sample consequence without becoming a new
headline claim.
