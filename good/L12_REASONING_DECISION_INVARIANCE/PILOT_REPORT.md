# L12 Mechanism Pilot Report

**Date:** 2026-09-10
**Verdict:** **GO**

## A. Current RQ

> Why does reasoning-oriented post-training produce presentation-invariant decisions, and is that transition accompanied by a shift from prompt control to trajectory-mediated decision formation?

## B. What prior work owns

*Mind the (DH) Gap!* owns reasoning-model invariance in risky choice. Recent work owns generic reasoning-trace causality, iterative answer construction, and reasoning-induced latent policy states. We cannot claim “reasoning models are more rational,” “CoT controls answers,” or “reasoning fine-tuning creates latent states.”

## C. What we tested

- **E01-E03:** parent/stimulus audit, sibling behavioral comparison, and frame-recoverability diagnostic.
- **E05-E06:** natural-trajectory causal readout and short arithmetic control.
- **E07:** full, terminal-stripped, opposite-stripped, and empty trajectory readout.
- **E08:** matched opposite-decision pre-answer state substitution across all layers.
- **E09:** sibling-branch 2 x 2 prompt-frame by trajectory-frame causal-control factorial.
- **E10-E11:** 36-decision behavioral/control breadth and 18-decision state-substitution replication.
- **E12:** OLMo Instruct-DPO versus Think-DPO continuation-axis control validation.
- **E13:** Qwen3-8B same-weight thinking versus non-thinking behavior and native-route control factorial.
- **E14:** Llama-Instruct versus DeepSeek-R1-Distill behavior and prompt-by-trajectory external replication.
- **E15:** DeepSeek pre-answer state substitution on the frozen 18-decision subset.

## D. Results

Order-conditional behavioral frame consistency is **0.750** for Instruct-SFT and **0.992** for Think-SFT; difference **+0.242 [0.108, 0.417]**.

E07, 46 matched target rows:

| Contrast | Mean margin effect | Prospect-bootstrap 95% CI |
|---|---:|---:|
| own stripped - empty | +2.624 | [2.008, 2.988] |
| own stripped - opposite stripped | +4.863 | [3.469, 5.773] |
| own full - own stripped | +7.047 | [6.746, 7.402] |

E08: donor transfer is near zero through layer 13, ramps at 14-16, reverses the mean target margin at layer 17, and remains strong. At layer 31, donor-directed shift is **+5.090 [3.766, 5.977]** and donor-choice flip rate is **0.804**.

E09:

| Quantity | Mean probability effect | 95% CI |
|---|---:|---:|
| Think trajectory control | +0.586 | [0.278, 0.857] |
| Instruct trajectory control | +0.012 | [-0.324, 0.393] |
| Think - Instruct trajectory control | +0.575 | [0.037, 1.055] |
| Branch difference in trajectory-minus-prompt control | +0.569 | [0.026, 1.062] |

E10 adds 36 independent decisions:

- Instruct-SFT frame consistency: **0.674 [0.618, 0.729]**.
- Think-SFT frame consistency: **0.977 [0.960, 0.993]** on 35 analyzable decisions.
- Think-minus-Instruct difference: **+0.299 [0.239, 0.357]**; worst/best missing-unit bounds **[0.277, 0.304]**.
- Think-minus-Instruct trajectory-minus-prompt control: **+0.399 [0.337, 0.464]**, positive on **36/36** decisions.
- Corrected exploratory item-level behavior/control association: **rho = -0.001, p = 0.997**; no monotonic per-item claim.

E11 repeats state substitution on 18 preregistered stratified decisions. The mean margin again reverses at layer 17; layer-31 donor shift is **+4.868 [4.056, 5.813]**, positive on **18/18** decisions.

E12 preserves the OLMo contrast at DPO checkpoints. Think-DPO minus Instruct-DPO trajectory-minus-prompt control is **+0.472 [0.401, 0.555]**, positive on **36/36** decisions. The DPO branch difference exceeds the frozen SFT difference by a secondary **+0.073 [0.016, 0.133]**.

E13 fixes Qwen3-8B weights and changes the official reasoning route. Frame consistency is **1.000 [1.000, 1.000]** in thinking mode versus **0.160 [0.087, 0.240]** in non-thinking mode, a matched difference of **+0.836 [0.757, 0.911]** on 35 analyzable units. Thinking-minus-non-thinking trajectory-minus-prompt control is **+0.604 [0.550, 0.661]**, positive on **36/36** decisions.

E14 externally replicates the aligned transition. DeepSeek exceeds Llama-Instruct in frame consistency by **+0.947 [0.913, 0.976]** and in trajectory-minus-prompt control by **+0.067 [0.037, 0.099]**. Excluding nine trace pairs for which the stripping heuristic removed no terminal segment leaves the control difference at **+0.057 [0.027, 0.089]**.

E15 validates internal mediation within DeepSeek. The donor shift is near zero early, becomes reliably positive from layer 14, and reaches **+1.222 [0.299, 2.181]** at layer 31. The selected E15 traces do not include the nine stripping exceptions.

Raw and summarized results are in `results/trajectory_takeover_seed43/`, `results/state_substitution_seed43/`, `results/control_reorganization_seed43/`, `results/breadth_seed71/`, `results/breadth_state_seed73/`, `results/checkpoint_validation_seed79/`, `results/qwen_mode_seed83/`, `results/llama_external_seed89/`, and `results/deepseek_state_seed97/`. Large full reasoning-generation files remain local and ignored; compact summaries and regeneration code are tracked.

## E. Interpretation

The best current answer is **progressive trajectory construction with late consolidation and causal-control reorganization**. Across OLMo sibling/checkpoint axes, fixed-weight Qwen routes, and the Llama/DeepSeek ecosystem, increased presentation invariance is accompanied by stronger trajectory-relative control; OLMo and DeepSeek also show late state mediation.

This strengthens distributed takeover, decision-state mediation, and causal-control reorganization. It weakens pure frame erasure, arithmetic-snippet, and terminal-only accounts.

## F. Data and identification validity

Trajectory stripping removed a terminal conclusion from all 47 valid traces, left no decision markers, produced no empty traces, and retained 48.1% of characters on average. E08 transfers hidden state without donor text. E09 independently crosses prompt and trajectory frames and uses identical donor text across branches.

The main mechanism now has 36-unit control breadth, 18-unit state-substitution breadth, a documented OLMo checkpoint continuation, same-weight Qwen evidence, and Llama-ecosystem external replication. Native answer-transition formats differ across OLMo siblings, and released sibling branches do not isolate one training operation. In Qwen, the official routes place the same stripped text in different native channels. In E14, models and post-training pipelines are unmatched. These prevent pure one-variable training attribution.

## G. Novelty after seeing the result

The closest compression is:

> Mind the DH Gap + iterative/causal CoT + persistent latent policy states.

The paper survives because E09-E13 link the behavioral transition to a direct reallocation between prompt and trajectory control, then show checkpoint persistence and complementary same-weight family breadth. E14-E15 externally replicate the aligned transition and internal mediation. Generic latent-state or CoT-causality claims are removed from our novelty claim.

## H. ACL / EMNLP / NAACL Main alignment

- **RQ scale:** strong and natural.
- **Evidence strength:** coherent causal chain, independent-decision replication, checkpoint persistence, same-weight family evidence, and external state mediation.
- **Mechanism depth:** now credible; E07, E08, and E09 advance one explanation rather than accumulating probes.
- **Novelty:** viable but narrowed by 2026 latent-policy-state work.
- **Consequence:** explains a cross-family invariance transition as a change in how final decisions are causally formed.
- **Weakest dimension:** exact training attribution remains intentionally bounded, and the Qwen comparison compounds mode with native channel/position.

## I. Verdict

**GO.** C1-C3 survive dozens of independent decisions, a preregistered state-replication subset, and the OLMo DPO continuation. Qwen adds fixed-weight triangulation; DeepSeek/Llama supplies external control-route replication; DeepSeek state substitution supports external internal-state mediation.

## J. Next smallest decisive experiment

Test whether C3 generalizes from gain/loss framing to description/history presentation on the frozen CPC18 calibration set, then confirm once on the untouched competition split. No additional model family or exploratory per-item association is justified.
