# L12 - Reasoning-Induced Invariance

## Trajectory Takeover

**Status:** **GO / MECHANISM AND STIMULUS BREADTH SUPPORTED**
**Target:** NAACL Main, continuously calibrated to ACL/EMNLP Main
**Last audited:** 2026-09-09

> **Research question:** Why does reasoning-oriented post-training make decisions invariant to presentation, and is that transition accompanied by a reallocation of causal control from the prompt to a self-generated reasoning trajectory and its pre-answer decision state?

“Trajectory takeover” does not mean the chain of thought is fake. It names a possible change in how the model forms decisions: prompt information can remain available while a self-generated trajectory becomes the dominant route into final decoding.

## Current answer

The discovery pilot supports **progressive construction plus late consolidation**:

1. Think-SFT is more frame-consistent than sibling Instruct-SFT: **0.992 vs 0.817**.
2. Frame identity remains recoverable early/mid, so simple erasure is inadequate.
3. After terminal choice language is stripped, the remaining trajectory still controls decision direction: own-stripped minus empty margin **+2.62 [2.01, 2.99]** and own-stripped minus opposite-stripped **+4.86 [3.47, 5.77]**.
4. The terminal portion remains important, adding **+7.05 [6.75, 7.40]**. The correct claim is distributed construction with terminal amplification, not “the last sentence does not matter.”
5. Opposite-decision pre-answer state substitution reverses the target from layer 17 onward and reaches a **+5.09 [3.77, 5.98]** donor-directed shift.
6. In the prompt-by-trajectory factorial, trajectory control is **+0.586 [0.278, 0.857]** in Think-SFT but **+0.012 [-0.324, 0.393]** in Instruct-SFT. The branch difference in trajectory-minus-prompt control is **+0.569 [0.026, 1.062]**.
7. Across 36 new independent decisions, the behavioral branch difference is **+0.242 [0.179, 0.302]** and the trajectory-minus-prompt control difference is **+0.399 [0.337, 0.464]**, positive on **36/36** decisions.
8. On an 18-decision preregistered subset, state substitution again reverses the mean margin at layer 17; final donor shift is **+4.868 [4.056, 5.813]**, positive on **18/18** decisions.

## Claim architecture

- **C1 - Distributed trajectory control:** reasoning before the terminal commitment already carries decision direction.
- **C2 - Trajectory-built decision state:** a pre-answer internal state causally transfers that direction.
- **C3 - Causal-control reorganization:** the reasoning-oriented sibling branch relies far more strongly on trajectory-relative control.
- **C4 - Checkpoint breadth:** test whether the same contrast persists through documented DPO branch continuations.

Behavioral invariance, probe decodability, generic trajectory causality, and individual layer effects are supporting evidence, not standalone contributions.

## Novelty boundary

Recent work already owns the parent behavioral phenomenon, iterative CoT computation, trace injection, and reasoning-induced latent policy states. L12's surviving paper identity is narrower:

> explain an established presentation-invariance transition through matched-branch evidence that causal control moves away from prompt presentation and toward self-generated trajectory-mediated decision formation.

See `RELATED_WORK.md` for the live compression audit.

## Current boundary and next phase

The independent-decision expansion is complete. A preregistered per-item association between invariance change and control change was not supported (rho = -0.203, p = 0.243); the paper should claim a stable branch-level reorganization, not monotonic item-level coupling.

E12 targets the official Instruct-DPO/Think-DPO continuation axis. Its code and exact revisions are ready, but the first run was stopped before loading because external checkpoint bandwidth was below 0.1 MB/s.

The primary unit is always the base decision. Repeated traces and patch layers do not count as independent evidence.

## Reproduction

- Experiment registry: `EXPERIMENTS.md`
- Claim ledger: `CLAIMS.md`
- Identification: `DATA_AND_GOLD.md`
- Current report: `PILOT_REPORT.md`
- Environment: `ENVIRONMENT.md`
- E07: `scripts/run_trajectory_takeover.sh`
- E08: `scripts/run_state_substitution.sh`
- E09: `scripts/run_control_reorganization.sh`
- E10 behavior/control: `scripts/run_breadth_behavior.sh`, `scripts/run_breadth_control.sh`
- E11 state replication: `scripts/run_breadth_state.sh`
- E12 checkpoint validation: `scripts/run_checkpoint_control.sh`
