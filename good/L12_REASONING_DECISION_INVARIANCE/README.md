# L12 - Reasoning-Induced Invariance

## Trajectory Takeover

**Status:** **GO / PREREGISTERED MECHANISM STUDY COMPLETE**
**Target:** NAACL Main, continuously calibrated to ACL/EMNLP Main
**Last audited:** 2026-09-10

> **Research question:** Why does reasoning-oriented post-training make decisions invariant to presentation, and is that transition accompanied by a reallocation of causal control from the prompt to a self-generated reasoning trajectory and its pre-answer decision state?

“Trajectory takeover” does not mean the chain of thought is fake. It names a possible change in how the model forms decisions: prompt information can remain available while a self-generated trajectory becomes the dominant route into final decoding.

## Current answer

The discovery pilot supports **progressive construction plus late consolidation**:

1. Think-SFT is more frame-consistent than sibling Instruct-SFT: **0.992 vs 0.750** on the parent prospects.
2. Frame identity remains recoverable early/mid, so simple erasure is inadequate.
3. After terminal choice language is stripped, the remaining trajectory still controls decision direction: own-stripped minus empty margin **+2.62 [2.01, 2.99]** and own-stripped minus opposite-stripped **+4.86 [3.47, 5.77]**.
4. The terminal portion remains important, adding **+7.05 [6.75, 7.40]**. The correct claim is distributed construction with terminal amplification, not “the last sentence does not matter.”
5. Opposite-decision pre-answer state substitution reverses the target from layer 17 onward and reaches a **+5.09 [3.77, 5.98]** donor-directed shift.
6. In the prompt-by-trajectory factorial, trajectory control is **+0.586 [0.278, 0.857]** in Think-SFT but **+0.012 [-0.324, 0.393]** in Instruct-SFT. The branch difference in trajectory-minus-prompt control is **+0.569 [0.026, 1.062]**.
7. Across 36 new independent decisions, the order-conditional behavioral branch difference is **+0.299 [0.239, 0.357]** and the trajectory-minus-prompt control difference is **+0.399 [0.337, 0.464]**, positive on **36/36** decisions.
8. On an 18-decision preregistered subset, state substitution again reverses the mean margin at layer 17; final donor shift is **+4.868 [4.056, 5.813]**, positive on **18/18** decisions.
9. The OLMo branch contrast persists at DPO checkpoints: Think-DPO minus Instruct-DPO trajectory-minus-prompt control is **+0.472 [0.401, 0.555]**, positive on **36/36** decisions.
10. With Qwen3-8B weights fixed, the official thinking route raises frame consistency from **0.160 to 1.000**, a matched change of **+0.836 [0.757, 0.911]**, and raises trajectory-minus-prompt control by **+0.604 [0.550, 0.661]**.
11. In a Llama-ecosystem external comparison, DeepSeek-R1-Distill raises frame consistency from **0.000 to 0.947**, a difference of **+0.947 [0.913, 0.976]**, and has stronger trajectory-relative control than Llama-Instruct by **+0.067 [0.037, 0.099]**.
12. DeepSeek state substitution independently supports pre-answer mediation: the final donor-directed shift is **+1.222 [0.299, 2.181]**, after a near-zero early profile and a sustained late rise beginning at layer 14.
13. Across 151 natural CPC18 decisions, the OLMo reasoning-minus-standard
    trajectory-relative control contrast is **+0.202 [0.162, 0.244]** and the
    same-weight Qwen route contrast is **+0.163 [0.121, 0.205]**. In both cases,
    the prompt-control difference includes zero.
14. The matching behavioral presentation-consistency changes are **+0.225
    [0.177, 0.271]** for OLMo and **+0.276 [0.223, 0.327]** for Qwen, robust
    to worst/best invalid-output assignment.
15. The unmatched Llama/DeepSeek axis does not generalize this transition:
    control difference **+0.019 [-0.005, 0.043]** and behavioral consistency
    difference **-0.225 [-0.264, -0.188]**. This establishes that behavioral
    invariance can also arise from stable near-chance choice, and is not itself
    evidence of rational decision formation.
16. On 48 frozen CPC18 decisions with naturally opposite explicit/history
    choices, pre-answer state substitution again has a sustained late causal
    profile: first mean margin reversal at layer 18 and final donor shift
    **+7.094 [5.914, 8.276]**, positive on 45/48 decisions.
17. On the untouched CPC18 competition split, the preregistered primary gate
    passes independently for both controlled axes: OLMo Think-minus-Instruct
    `Delta_R - Delta_P` is **+0.097 [0.002, 0.180]** and Qwen
    thinking-minus-non-thinking is **+0.219 [0.152, 0.288]**.
18. The supporting behavioral result is heterogeneous: Qwen's heldout
    presentation-consistency change is **+0.163 [0.051, 0.268]**, while OLMo's
    is **-0.013 [-0.095, 0.065]**. Causal-route reorganization is therefore
    more stable than, and not sufficient by itself for, behavioral invariance.

## Claim architecture

- **C1 - Progressive trajectory construction:** reasoning before the terminal commitment already carries decision direction, with terminal amplification.
- **C2 - Trajectory-built decision state:** a pre-answer internal state causally transfers that direction.
- **C3 - Causal-control reorganization:** reasoning-oriented computation shifts
  control toward trajectories; whether this yields behavioral invariance depends
  on the decisions those trajectories construct.

E12-E15 provide checkpoint persistence, same-weight route triangulation, external-family replication, and external state mediation underneath C2-C3. They are not additional headline claims.

Behavioral invariance, probe decodability, generic trajectory causality, and individual layer effects are supporting evidence, not standalone contributions.

## Novelty boundary

Recent work already owns the parent behavioral phenomenon, iterative CoT computation, trace injection, and reasoning-induced latent policy states. L12's surviving paper identity is narrower:

> explain an established presentation-invariance transition through matched-branch evidence that causal control moves away from prompt presentation and toward self-generated trajectory-mediated decision formation.

See `RELATED_WORK.md` for the live compression audit.

## Final study boundary

The independent-decision and natural description/history expansions are complete.
Under the corrected order-conditional construct, a preregistered per-item
association between invariance change and control change is not supported (rho =
-0.001, p = 0.997) and is permanently demoted. The supported bridge is the
construct-level reallocation reproduced over 151 CPC18 calibration decisions
under OLMo sibling and Qwen same-weight identification.

E12 is complete. It establishes persistence over a real OLMo checkpoint axis, not attribution of the original divergence to DPO.

E13 is also complete. Qwen3 supplies a complementary identification because weights are identical, but the official switch changes the native placement of the same stripped text: inside the reasoning channel versus after an empty closed reasoning channel. Therefore the result supports **route-dependent integration**, not a latent mode variable isolated from channel and position.

E14-E15 are complete. The Llama/DeepSeek axis replicates the aligned increase in presentation invariance and trajectory-relative control, then verifies late pre-answer state mediation within DeepSeek. This is external replication rather than training attribution because the pair is unmatched.

The current paper answer is that reasoning-oriented computation reorganizes
decision formation toward a progressively constructed trajectory and late decision
state. This is not merely an OLMo-local result: it survives a same-weight Qwen mode
contrast, a qualitatively different presentation family, and an untouched
competition split. The OLMo heldout behavior result shows that the route change is
not sufficient for invariance, while the Llama boundary shows that invariance can
also reflect stable chance-level choice. The paper must therefore measure behavior,
EV alignment, and causal route jointly rather than call any invariance
"rationality."

The planned evidence chain is complete. Further model families, layer searches,
or post-hoc item correlations are not justified unless manuscript review exposes a
load-bearing identification gap.

The primary unit is always the base decision. Repeated traces and patch layers do not count as independent evidence.

## Reproduction

- Experiment registry: `EXPERIMENTS.md`
- Claim ledger: `CLAIMS.md`
- Identification: `DATA_AND_GOLD.md`
- Current report: `PILOT_REPORT.md`
- Paper skeleton: `PAPER_OUTLINE.md`
- Calibration/confirmation synthesis: `results/cpc18_replication_summary.json`
- Raw execution audits: `results/cpc18_calibration_seed121/execution_audit.json`,
  `results/cpc18_competition_seed137/execution_audit.json`
- Environment: `ENVIRONMENT.md`
- E07: `scripts/run_trajectory_takeover.sh`
- E08: `scripts/run_state_substitution.sh`
- E09: `scripts/run_control_reorganization.sh`
- E10 behavior/control: `scripts/run_breadth_behavior.sh`, `scripts/run_breadth_control.sh`
- E11 state replication: `scripts/run_breadth_state.sh`
- E12 checkpoint validation: `scripts/run_checkpoint_control.sh`
- E13 same-weight Qwen validation: `scripts/run_qwen_mode_behavior.sh`, `scripts/run_qwen_mode_control.sh`
- E14 Llama-ecosystem validation: `scripts/run_llama_external.sh`
- E15 DeepSeek state mediation: `scripts/run_deepseek_state_substitution.py`, `scripts/summarize_deepseek_state.py`
