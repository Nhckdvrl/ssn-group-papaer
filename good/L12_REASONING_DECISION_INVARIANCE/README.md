# L12 - Reasoning-Induced Invariance

## Trajectory Takeover

**Status:** **GO / MAIN-PAPER EVIDENCE PROGRAM COMPLETE**
**Target:** NAACL Main, continuously calibrated to ACL/EMNLP Main
**Last audited:** 2026-09-10

> **Research question:** Why do reasoning models become invariant to some changes in presentation while remaining sharply sensitive to others, and does reasoning reorganize decision control from prompt form toward an evidence-bearing trajectory and its pre-answer state?

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
    is **-0.013 [-0.095, 0.065]**. This dissociation exposed that the original
    description/history contrast mixed representational form with sampled evidence,
    motivating the prospective E20 decomposition rather than a route-only ending.
19. Increasing heldout behavioral sampling from 3 to 20 generations per cell
    leaves this pattern intact: OLMo is **-0.011 [-0.089, 0.067]**, while Qwen
    is **+0.121 [0.026, 0.215]**. The OLMo null is not Monte Carlo imprecision.
20. Once form and evidence are orthogonalized over 137 real CPC18 decisions,
    reasoning changes what the model is sensitive to. The OLMo selective-
    sensitivity shift is **+1.229 [1.195, 1.262]** and the same-weight Qwen
    shift is **+0.709 [0.638, 0.778]**: sensitivity to form falls while
    sensitivity to decision evidence rises. The causal factorial confirms the
    same relocation: trajectory-relative evidence control rises by **+0.459/
    +0.584** (raw/summary) in OLMo and **+0.563/+0.749** in Qwen, while prompt
    evidence-control differences stay near zero.
21. The selective computation is present in the internal carrier. Across 32
    frozen decisions, final-layer state substitution yields evidence control
    **+0.763 [0.694, 0.828]**, form sensitivity **0.174 [0.124, 0.227]**, and
    state selectivity **+0.590 [0.476, 0.704]**. The evidence effect is near zero
    early and develops into the late pre-answer state.
22. The new crown generalizes beyond OLMo/Qwen. In the external Llama ecosystem,
    DeepSeek-minus-Llama selective sensitivity is **+0.996 [0.962, 1.031]**,
    positive on 137/137 decisions. Trajectory-relative evidence control rises by
    **+0.175 [0.131, 0.221]** for raw histories and **+0.143 [0.106, 0.180]**
    for summaries, while prompt-control changes remain near zero.
23. A paired 20/100-trial supporting diagnosis is inconclusive. Empirical evidence
    aligns with the generating EV direction more often at 100 trials (0.847 versus
    0.750), but long raw tables drive reasoning valid rates to 0.332/0.343 and
    sharp bounds do not identify either controlled-axis effect. It is retained as
    an audited limitation, not promoted into the story.

## Claim architecture

- **C1 - Trajectory construction and consolidation:** reasoning develops a causal
  decision direction before terminal commitment and consolidates it into a
  transferable pre-answer state.
- **C2 - Causal-control reallocation:** reasoning-oriented computation shifts
  control from prompt-level presentation toward the trajectory and state it builds.
- **C3 - Selective sensitivity:** that new controller becomes comparatively
  insensitive to representational form while remaining sharply sensitive to
  decision evidence.

E12-E15 provide checkpoint persistence, same-weight route triangulation, external-family replication, and external state mediation underneath C2-C3. They are not additional headline claims.

Behavioral invariance, probe decodability, generic trajectory causality, and individual layer effects are supporting evidence, not standalone contributions.

## Novelty boundary

Recent work already owns the parent behavioral phenomenon, iterative CoT
computation, trace injection, reasoning-induced latent policy states, and the
fact that finite samples can change decision evidence. L12's full paper identity
is their unresolved intersection:

> reasoning reallocates causal decision control from presentation form toward
> evidence integrated by a self-generated trajectory and its internal state,
> producing selective rather than indiscriminate invariance.

See `RELATED_WORK.md` for the live compression audit.

## Final study boundary

The independent-decision, natural description/history, and orthogonal form-by-
evidence expansions are complete. Under the corrected order-conditional
construct, a preregistered per-item association between the original gain/loss
invariance change and control change is not supported (rho = -0.001, p = 0.997)
and remains demoted. The stronger bridge is now intervention-level: changing
evidence carried by the trajectory controls behavior and the late internal state,
whereas changing form has a substantially smaller effect.

E12 is complete. It establishes persistence over a real OLMo checkpoint axis, not attribution of the original divergence to DPO.

E13 is also complete. Qwen3 supplies a complementary identification because weights are identical, but the official switch changes the native placement of the same stripped text: inside the reasoning channel versus after an empty closed reasoning channel. Therefore the result supports **route-dependent integration**, not a latent mode variable isolated from channel and position.

E14-E15 are complete. The Llama/DeepSeek axis replicates the aligned increase in presentation invariance and trajectory-relative control, then verifies late pre-answer state mediation within DeepSeek. This is external replication rather than training attribution because the pair is unmatched.

The current paper answer is that reasoning-oriented computation reorganizes
decision formation toward a progressively constructed trajectory and late state,
and that this controller tracks decision evidence far more strongly than its raw-
versus-summary form. This is not an OLMo-local result: the selective behavior and
trajectory-control transition holds under OLMo sibling, same-weight Qwen, and
external Llama-ecosystem axes. The paper must therefore distinguish form from
evidence and must never equate invariance alone with rationality.

The heldout result exposed a construct confound in description/history: a finite
history changes both surface form and observed evidence. Prospective E20
orthogonalizes those variables using previously unscored real histories; E20-C,
E21, and E22 connect the resulting behavior to trajectory control, state content,
and external-family breadth. E18L is the final supporting finite-history
consequence. Further model families, layer searches, and post-hoc subgroup claims
are not load-bearing.

The primary unit is always the base decision. Repeated traces and patch layers do not count as independent evidence.

## Reproduction

- Shared research story and claim map: `RESEARCH_STORY_AND_CLAIM_MAP.md`
- Experiment registry: `EXPERIMENTS.md`
- Claim ledger: `CLAIMS.md`
- Identification: `DATA_AND_GOLD.md`
- Current report: `PILOT_REPORT.md`
- Paper skeleton: `PAPER_OUTLINE.md`
- Current manuscript narrative: `MANUSCRIPT_DRAFT.md`
- Adversarial reviewer audit: `REVIEWER_AUDIT.md`
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
