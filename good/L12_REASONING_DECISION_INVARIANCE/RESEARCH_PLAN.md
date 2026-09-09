# L12 Research Plan

## Core RQ

> Why does reasoning-oriented post-training produce presentation-invariant decisions, and does it reorganize causal control from prompt-conditioned choice to trajectory-mediated decision formation?

## Evidence chain now established

1. **Behavioral substrate:** order-conditional frame consistency rises from 0.750 in Instruct-SFT to 0.992 in Think-SFT on the parent prospects.
2. **No simple erasure:** frame identity remains decodable early/mid, weakening simple representational erasure.
3. **Distributed trajectory control (E07):** after terminal decisions are removed, own stripped trajectories exceed empty by +2.62 [2.01, 2.99] and opposite stripped trajectories by +4.86 [3.47, 5.77]. The terminal portion adds +7.05 [6.75, 7.40].
4. **Decision-state mediation (E08):** opposite-decision state substitution has negligible early effects, reverses the mean target margin at layer 17, and reaches a +5.09 [3.77, 5.98] donor-directed shift with 0.804 donor flips at the final layer.
5. **Mechanism-phenomenon bridge (E09):** stripped-trajectory control is +0.586 [0.278, 0.857] in Think-SFT and +0.012 [-0.324, 0.393] in Instruct-SFT. The branch difference in trajectory-minus-prompt control is +0.569 [0.026, 1.062].

The current interpretation is **progressive construction plus late consolidation**: the natural trajectory establishes a decision direction before explicit commitment, a late state carries that direction into decoding, and this route is substantially stronger in the reasoning-oriented branch.

## Next phase: breadth that tests the explanation

### E10 - Independent-decision behavioral and control bridge - completed

Build a preregistered set of at least 30 simple, gold-verifiable base decisions. First run the sibling behavioral comparison, then the E09 prompt-by-trajectory factorial on successful matched traces.

Primary questions:

1. Does Think-SFT's invariance advantage replicate across independent base decisions?
2. Is Think-SFT's trajectory-minus-prompt control consistently larger than Instruct-SFT's?
3. Across base decisions, is the branch change in causal-control structure associated with the branch change in presentation invariance?

The corrected order-conditional behavioral difference is +0.299 [0.239, 0.357]. The causal-control branch difference is +0.399 [0.337, 0.464], positive on all 36 decisions. The recomputed item-level association is null (rho = -0.001, p = 0.997); no monotonic per-item coupling claim is made.

### E11 - Mechanistic replication on a stratified subset - completed

On 18 preregistered decisions, the mean margin again reverses at layer 17; final donor shift is +4.868 [4.056, 5.813] and positive for 18/18 decisions.

### E12 - Meaningful training-axis validation - completed

The documented Instruct-SFT -> Instruct-DPO and Think-SFT -> Think-DPO axis preserves the mechanism. The DPO Think-minus-Instruct trajectory-relative control difference is +0.472 [0.401, 0.555], positive on all 36 decisions. This is continuation-axis persistence, not one-variable training attribution.

### E13 - Same-weight cross-family route validation - completed

On Qwen3-8B, the official thinking route increases frame consistency from 0.160 to 1.000, a matched +0.836 [0.757, 0.911], and exceeds the non-thinking route in trajectory-minus-prompt control by +0.604 [0.550, 0.661]. Because the native hard switch changes whether stripped text appears inside the reasoning channel or after an empty closed reasoning channel, this is complementary evidence for route-dependent integration rather than a pure latent mode intervention.

### E14 - Llama-ecosystem external replication - completed

The aligned behavior/control transition replicates. DeepSeek exceeds Llama-Instruct in frame consistency by +0.947 [0.913, 0.976] and in trajectory-minus-prompt control by +0.067 [0.037, 0.099]. The behavior result uses an audited terminal-answer parser; the initial generic-parser summary is invalid and retained nowhere as evidence.

### E15 - External state mediation - completed

On the frozen 18-decision subset, opposite-decision pre-answer state substitution is near zero early, becomes reliably donor-directed at layer 14, and reaches +1.222 [0.299, 2.181] at the final layer. This supports an external state-mediation correlate without implying identical layer geometry or effect universality.

### E16 - CPC18 calibration audit and frozen corpus construction

Audit all 210 calibration problems before model scoring. Predefine known-risk,
ambiguity, EV definability, dominance, tie, outcome-complexity, and independent-history
criteria. If at least 150 independent problems support a clean matched
description/history intervention, CPC18 becomes the primary breadth corpus;
otherwise it supplies the description/history subset and Choices13k supplies scale.

### E17 - Description/history control reorganization

On a representative 120-180 problem calibration subset, cross description/history
prompts with conclusion-stripped natural trajectories. Estimate prompt control,
trajectory control, and their difference using `CAUSAL_FRAMEWORK.md`. This is the
next load-bearing test: it distinguishes a general presentation-control
reorganization from a gain/loss-specific mechanism.

### E18 - Held-out confirmation

Freeze dataset, templates, parser, stripping, exclusions, and statistics before
accessing the 60 competition problems. Run one confirmatory evaluation. If E17 is
strong, replicate state mediation on 32-48 preregistered decisions; do not add more
model families or layer-localization searches.

## Decision rule

- **GO:** C1-C3 remain directionally stable over independent decisions, a credible training-axis validation agrees, and at least one complementary family-level route validation agrees qualitatively.
- **RECONSTRUCT:** takeover is restricted to a clear, meaningful boundary such as arithmetic transparency; make that boundary the conclusion.
- **HOLD/KILL:** the three-prospect mechanism fails across independent units, or closest prior work compresses the complete paper identity.
