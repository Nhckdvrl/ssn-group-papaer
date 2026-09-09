# L12 Research Plan

## Core RQ

> Why does reasoning-oriented post-training produce presentation-invariant decisions, and does it reorganize causal control from prompt-conditioned choice to trajectory-mediated decision formation?

## Evidence chain now established

1. **Behavioral substrate:** frame consistency rises from 0.817 in Instruct-SFT to 0.992 in Think-SFT on the parent prospects.
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

The behavioral difference is +0.242 [0.179, 0.302]. The causal-control branch difference is +0.399 [0.337, 0.464], positive on all 36 decisions. The preregistered exploratory item-level association is unsupported and is not part of the claim.

### E11 - Mechanistic replication on a stratified subset - completed

On 18 preregistered decisions, the mean margin again reverses at layer 17; final donor shift is +4.868 [4.056, 5.813] and positive for 18/18 decisions.

### E12 - Meaningful training-axis validation - runnable

The documented Instruct-SFT -> Instruct-DPO and Think-SFT -> Think-DPO lineage is frozen. Code and revisions are ready; the first execution was stopped because checkpoint transfer bandwidth was below 0.1 MB/s. Resume when weights are locally available.

## Decision rule

- **GO:** C1-C3 remain directionally stable over independent decisions, and at least one credible training-axis validation agrees qualitatively.
- **RECONSTRUCT:** takeover is restricted to a clear, meaningful boundary such as arithmetic transparency; make that boundary the conclusion.
- **HOLD/KILL:** the three-prospect mechanism fails across independent units, or closest prior work compresses the complete paper identity.
