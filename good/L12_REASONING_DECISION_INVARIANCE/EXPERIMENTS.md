# L12 Experiment Registry

**Updated:** 2026-09-09

## L12-E01: Parent Data and Stimulus Audit

- **Linked claim:** feasibility and provenance for L12-C1
- **Source:** Ge et al. (2026) paper appendix and commit-pinned `Yongyan-Zhang/mind-the-dh-gap` repository.
- **Unit:** matched prospect x frame x option order x prompt style.
- **Primary axis:** explicit gain/loss framing with no explanation; order is crossed as a control.
- **Analysis:** paired frame-consistency and order-consistency with matched bootstrap confidence intervals using the public aggregate counts.
- **Important limitation:** the repository publishes aggregated choices, not raw prompts/generations. Exact templates and three base prospects come from Appendix B.3-B.4; the public CSV validates the factorial cells and counts.
- **Raw/source pointers:** `data/upstream/`; provenance manifest written by `scripts/fetch_parent_data.sh`.
- **Status:** completed. Public aggregate branch contrast reproduced; see `results/parent_audit/summary.json`.

Implementation audit: a common-raw first attempt on Instruct-SFT yielded 237/240 invalid choices (mostly immediate EOS), confirming that native SFT chat wrapping is required for generated behavior. The invalid run is retained at `results/pilot_seed29/instruct_sft_common_raw/`. Behavioral reproduction uses each released SFT checkpoint's native chat template; the base has no native chat template and is reported as a common-raw diagnostic, not treated as a directly comparable instruction-following agent. Hidden-state frame recovery is estimated within checkpoint, so the constant system wrapper cannot predict frame labels, but cross-checkpoint activation levels remain descriptive.

## L12-E02: Shared-Base Behavioral Branch Comparison

- **Linked claim:** L12-C1
- **Models:** `allenai/Olmo-3-1025-7B`, `allenai/Olmo-3-7B-Instruct-SFT`, `allenai/Olmo-3-7B-Think-SFT`, exact revisions in config/results.
- **Conditions:** 3 explicit prospects x gain/loss x both option orders, no-explanation direct choice.
- **Repeated sampling:** 20 generations per cell, seed 29, temperature 0.7, top-p 0.95.
- **Primary metric:** paired frame consistency after correcting the option identity under loss framing; secondary order consistency, EV-maximizing rate, invalid response rate.
- **Uncertainty/test:** matched prospect bootstrap CI; paired permutation test of the difference-in-change `(Think-SFT - base) - (Instruct-SFT - base)`.
- **Exclusion:** no post-hoc prompt or cell exclusion; invalid responses are reported and counted as missing only for choice metrics.
- **Kill/reconstruct:** no clean branch contrast after prompt/template fidelity checks blocks internal mechanism work on this substrate.
- **Config:** `configs/pilot.json`
- **Command:** `scripts/run_behavior.sh`
- **Status:** completed. Think-SFT used a corrected 1,024-token cap and strict post-`</think>` parsing. The common base failed semantic instruction adherence, so generated base deltas are not identifiable.

## L12-E03: First Internal Diagnostic

- **Linked claim:** L12-C2
- **Question:** At matched token positions and layers, is gain/loss frame identity linearly recoverable after accounting for prospect identity and order?
- **Representation:** residual stream at the final prompt token; all layers, generation-free teacher-forced prompt pass.
- **Validation:** leave-one-prospect-out cross-validation; label-shuffle permutation baseline; report balanced accuracy with bootstrap CI.
- **Interpretation:** decodability only routes L12-E04. It cannot establish canonicalization, use, or suppression.
- **Status:** completed as a routing diagnostic. Frame labels are recoverable through most layers, but there are only 12 conditions and the lexical sign cue is present in the prompt.

## L12-E04: Deliberation-Mode Intervention

- **Linked account:** inference-time deliberation (C).
- **Intervention:** same Think-SFT weights and native template, but immediately close the template-opened `<think>` block before generation; compare with normal native reasoning mode.
- **Primary outcome:** change in frame consistency; secondary order consistency and invalid rate.
- **Interpretation:** a loss of invariance strengthens a deliberation-mediated account. No change weakens a pure deliberation account but does not distinguish canonicalization from policy override.
- **Status:** executed and invalidated. With an injected `</think>` and a 32-token cap, 0/240 continuations were strict direct answers; all continued explanatory generation. A loose parser incorrectly read option letters inside those explanations. The run is archived at `results/pilot_seed29/think_sft_no_think_len32_invalid_parser/` and is excluded from all behavioral results. This failure matches the fresh warning in *`</think>` Doesn't Stop Reasoning* (2026).

## L12-E05: Matched Reasoning-Prefix Readout Intervention

- **Linked claim:** L12-C3.
- **Question:** Does the content of the generated calculation trace causally determine the final A/B readout?
- **Unit:** completed Think-SFT trace; first four completed traces in each of 12 prospect x frame x order cells (48 traces).
- **Conditions:** own trace, empty trace, or a trace from the matched opposite frame inserted after the same target prompt. Score A/B logits at the answer position without further generation.
- **Primary metric:** correct-option logit margin. Secondary metric: argmax EV-consistent rate.
- **Uncertainty:** paired cluster bootstrap over the 12 stimulus cells, sampling one trace within each resampled cell, 5,000 draws.
- **Interpretation boundary:** establishes trace-content-to-readout causality. It does not establish that prompt frame information was erased, nor that an injected end token stops inference-time reasoning.
- **Raw/summary:** `results/pilot_seed29/reasoning_prefix_intervention/`.
- **Status:** completed. Own trace strongly raises the correct margin; opposite-frame trace reverses it.

## L12-E06: Answer-Leakage-Controlled Calculation Intervention

- **Linked claim:** L12-C3/C4.
- **Question:** Is E05 driven only by an explicit answer mention, or does calculation content without A/B labels control the readout?
- **Unit:** 12 prospect x frame x order stimulus cells.
- **Conditions:** a correct pair of expected magnitudes, the same two magnitudes swapped, or the decision rule without computed values. All prefixes omit A/B answer labels and final-choice language.
- **Primary metric:** correct-option logit margin; secondary argmax accuracy.
- **Uncertainty:** paired prospect-cluster bootstrap, 5,000 draws.
- **Interpretation:** correct-over-swapped supports arithmetic-content mediation. It does not by itself distinguish where in the residual stream the computation is represented.
- **Status:** completed unchanged. Correct calculation did not reliably outperform rule-only or swapped calculation; both prospect-cluster intervals include zero. This weakens an arithmetic-snippet account and limits E05 to complete-trajectory causality.

## L12-E07: Conclusion-Stripped Trajectory Takeover

- **Linked claim:** L12-C4.
- **Question:** Does the long natural reasoning trajectory retain strong causal control over the final answer after its terminal explicit choice/conclusion is removed?
- **Model:** `allenai/Olmo-3-7B-Think-SFT`, frozen revision in `configs/trajectory_takeover.json`.
- **Stimuli:** the same three audited parent prospects x gain/loss x both option orders.
- **Natural traces:** 4 sampled trajectories per cell.
- **Conditions:** own full trace; own terminal-conclusion-stripped trace; matched opposite-frame stripped trace; empty trace.
- **Primary metric:** target-directed A/B logit margin under forced readout.
- **Primary contrasts:** own-stripped minus empty; own-stripped minus opposite-stripped.
- **Secondary quantity:** own-full minus own-stripped, interpreted as the incremental contribution of the terminal commitment.
- **Trace surgery:** deterministically remove trailing decision/conclusion sentences and record every removed span plus whether decision markers remain.
- **Outcome logic:** if stripped natural reasoning retains strong target-directed control, proceed to E08; if the effect collapses, reconstruct around late self-commitment rather than adding rescue controls.
- **Config:** `configs/trajectory_takeover.json`
- **Command:** `scripts/run_trajectory_takeover.sh`
- **Status:** completed. 48 traces were generated, 47 were valid, and 46 had a matched opposite-frame trace. All valid stripped traces had a conclusion removed, none retained a decision marker, and none became empty. Own-stripped minus empty margin = **+2.624 [2.008, 2.988]**; own-stripped minus opposite-stripped = **+4.863 [3.469, 5.773]**. The terminal portion adds **+7.047 [6.746, 7.402]**. This supports distributed trajectory control with strong terminal amplification.

## L12-E08: Pre-Answer Decision-State Causal Substitution

- **Linked claim:** L12-C5.
- **Prerequisite:** E07 shows non-trivial trajectory-level control beyond the terminal explicit conclusion.
- **Question:** Has the stripped natural reasoning trajectory constructed a causal pre-answer decision state that carries final-answer control?
- **Design:** for each matched target/opposite-frame trace pair, capture the donor final-token hidden state at every decoder layer and substitute it into the target forward pass one layer at a time.
- **Important property:** donor text is never appended to the target; only the internal pre-answer state is transferred.
- **Primary metric:** donor-consistent shift in the target A/B logit margin.
- **Secondary metric:** fraction of patched target readouts that flip to the donor decision.
- **Interpretation:** a coherent donor-consistent layer profile supports a trajectory-built causal decision state. The layer number itself is not the claim.
- **Config:** `configs/state_substitution.json`
- **Command:** `scripts/run_state_substitution.sh`
- **Status:** completed after E07 passed its gate. The donor-directed shift is negligible through layer 13, ramps at 14-16, reverses the mean target margin at layer 17, and stays strong afterward. At layer 31 the shift is **+5.090 [3.766, 5.977]**, with a **0.804** donor-choice flip rate. This is a coherent trajectory-built decision-state profile, not a claim about a privileged layer.

## L12-E09: Matched Causal-Control Reorganization

- **Linked question:** does the invariance transition align with a branch-level shift from prompt control toward trajectory control?
- **Design:** cross prompt frame (gain/loss) and conclusion-stripped trajectory frame (gain/loss) for the same prospect, order, and sampled trace pair. Score the probability of the fixed gain-optimal displayed choice.
- **Models:** exact sibling Instruct-SFT and Think-SFT checkpoints, with identical donor trajectory text and each checkpoint's native answer transition.
- **Primary within-branch quantities:** trajectory-control effect and prompt-control effect from the 2 x 2 factorial.
- **Primary bridge:** Think-minus-Instruct difference in `trajectory_control - prompt_control`, with prospect-cluster bootstrap uncertainty.
- **Identification boundary:** this is a matched released-branch comparison, not one-variable training causality; native answer-transition formats differ by construction.
- **Gate:** a paper-level bridge requires stronger trajectory-relative control in Think-SFT with consistent prospect direction, not merely a nonzero trace effect in either model.
- **Config/command:** `configs/control_reorganization.json`; `scripts/run_control_reorganization.sh`.
- **Status:** completed. Think-SFT trajectory control = **+0.586 [0.278, 0.857]**; Instruct-SFT = **+0.012 [-0.324, 0.393]**. Think-minus-Instruct trajectory control = **+0.575 [0.037, 1.055]**. The primary branch difference in trajectory-minus-prompt control is **+0.569 [0.026, 1.062]**. All three prospects agree in direction for Think-SFT; Instruct-SFT is heterogeneous. This supports the mechanism-phenomenon bridge but remains a three-prospect sibling-branch pilot.

## L12-E10: Independent-Decision Breadth and Control Bridge

- **Linked claim:** L12-C4.
- **Question:** do the behavioral transition and trajectory-relative control reorganization generalize beyond the three discovery prospects?
- **Unit:** at least 30 independently parameterized, gold-verifiable base decisions; frames, orders, and trace samples are repeated observations within unit.
- **Design:** preregistered simple two-option lotteries, crossed gain/loss frame and order. Run sibling behavior first; generate matched Think-SFT trajectories; then apply the E09 prompt-by-trajectory factorial to both branches.
- **Primary behavioral metric:** base-decision-level frame consistency difference, Think-SFT minus Instruct-SFT.
- **Primary mechanism metric:** base-decision-level difference in `(trajectory control - prompt control)`, Think-SFT minus Instruct-SFT.
- **Uncertainty:** base-decision cluster bootstrap; report stratum-level heterogeneity rather than treating traces as independent.
- **Exclusions:** frozen before model scoring; invalid or unpaired traces are reported, never silently replaced after inspecting model outcomes.
- **Secondary exploratory bridge (frozen before causal scoring):** Spearman association across base decisions between the sibling frame-consistency change and sibling trajectory-minus-prompt control change. This is not required for C3 because ceiling effects can attenuate it.
- **Status:** completed. The 36-unit audit passes all balance/uniqueness checks. Instruct-SFT frame consistency = **0.729 [0.670, 0.785]**; Think-SFT = **0.977 [0.960, 0.993]** on 35 analyzable decisions; difference = **+0.242 [0.179, 0.302]**. One Think cell had no valid completion; assigning its unit the worst/best possible consistency gives mean-difference bounds **[0.221, 0.249]**. Think-minus-Instruct trajectory-minus-prompt control = **+0.399 [0.337, 0.464]**, positive on **36/36** base decisions. The exploratory across-decision association with the behavioral difference is not supported (Spearman rho = -0.203, p = 0.243) and is not promoted to a claim.

## L12-E11: Stratified Decision-State Replication

- **Linked claim:** breadth of L12-C2.
- **Question:** does the trajectory-built pre-answer decision state replicate beyond the three discovery prospects?
- **Unit:** 18 independently parameterized base decisions, one from each payoff-scale x EV-gap x probability-gap cell.
- **Selection:** frozen in `configs/breadth_state_substitution.json`; alternate gain-optimal A/B in lexicographic stratum order. Use order AB and the lowest-index valid matched gain/loss trace, without reference to behavioral or control-effect size.
- **Intervention:** repeat E08 layer-wise opposite-decision final-token state substitution in both frame directions.
- **Primary signature:** coherent late-layer donor-directed shift with a base-decision bootstrap interval excluding zero and direction consistency across units.
- **Secondary:** first layer where the mean target margin reverses and donor-choice flip rate; no privileged-layer claim.
- **Status:** completed. The mean target margin first reverses at layer 17, matching the discovery pilot. At layer 31 the donor-directed shift is **+4.868 [4.056, 5.813]**, positive on **18/18** base decisions, with donor-choice flip rate **0.750**.

## L12-E12: DPO-Lineage Checkpoint Validation

- **Linked claim:** checkpoint breadth for L12-C3.
- **Question:** does the reasoning-vs-instruction causal-control contrast persist after the documented DPO continuation of each SFT sibling branch?
- **Lineage:** Instruct-SFT -> Instruct-DPO and Think-SFT -> Think-DPO, as declared by the official checkpoint metadata.
- **Design:** score the exact E10 stripped trajectories in the same prompt-by-trajectory factorial on the two DPO checkpoints. SFT results are frozen comparators.
- **Primary signature:** Think-DPO minus Instruct-DPO trajectory-minus-prompt control is positive with a base-decision bootstrap interval excluding zero and consistent direction across decisions.
- **Secondary:** DPO-minus-SFT change within each branch is descriptive. DPO is not treated as the origin of the branch difference.
- **Attribution boundary:** this tests persistence over a documented checkpoint axis, not an additional model family and not one-variable attribution of the original SFT divergence.
- **Status:** runnable and revisions audited. Execution was stopped before model loading because first-time Hugging Face transfer remained below 0.1 MB/s with and without `hf_transfer`, implying a multi-hour external I/O wait. No E12 result is claimed.
