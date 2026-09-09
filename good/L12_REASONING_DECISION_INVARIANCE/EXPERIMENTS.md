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
