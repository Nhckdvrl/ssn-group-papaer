# L12 Claim Ledger

**Updated:** 2026-09-10

## Current RQ

> Why does reasoning-oriented post-training make decisions invariant to presentation, and is that transition accompanied by a shift in causal control from the prompt to a self-generated reasoning trajectory and its pre-answer decision state?

## Major claim chain

| ID | Claim | Evidence | Current status |
|---|---|---|---|
| **L12-C0** | Reasoning models are more invariant across risky-choice presentations. | *Mind the (DH) Gap!* | **Established prior; not ours** |
| **L12-C1** | Natural reasoning progressively constructs decision control before the terminal explicit commitment; the conclusion amplifies rather than creates the effect. | E05-E07 | **Supported on 3 parent prospects; breadth is supplied under C3** |
| **L12-C2** | Long reasoning constructs a pre-answer decision state that causally carries trajectory control into final decoding. | E08 + E11; E15 triangulation | **Supported across 18 OLMo decisions and externally in DeepSeek** |
| **L12-C3** | Reasoning-associated invariance is accompanied by a reorganization of causal control away from prompt presentation and toward trajectory-mediated decision formation. | E09-E10; E12-E14 triangulation | **Supported across 36 decisions and complementary checkpoint/mode/family comparisons** |

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
- The released OLMo checkpoints are sibling branches from a common base. They support a training-regime-associated contrast, not strict attribution to one isolated optimization step.
- E10 uses 36 independent base decisions and E11 uses a preregistered 18-decision stratified subset. Repeated traces and layers remain within-unit observations.
- The corrected exploratory decision-level association between the behavioral branch difference and control difference is unsupported (rho = -0.001, p = 0.997). Do not claim monotonic per-item coupling; the supported bridge is the matched branch/mode/family-level reorganization replicated across units.

## Current verdict

**GO.** C1-C3 establish progressive construction, state mediation, and causal-control reorganization. E12-E15 are persistence and triangulation beneath those claims, not separate contributions. The remaining load-bearing question is whether C3 survives a broad, natural description/history manipulation under the frozen interventional decomposition in `CAUSAL_FRAMEWORK.md`.
