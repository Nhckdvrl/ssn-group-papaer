# L12 First-Round Pilot Report

**Date:** 2026-09-09  
**Verdict:** **CONDITIONAL**

## A. Current RQ

Does reasoning-oriented SFT produce risky-choice invariance by canonicalizing the prompt, overriding preserved context at readout, or using an inference-time trajectory to construct the decision?

## B. What Prior Work Owns

Ge et al. (ACL 2026 Outstanding) own the reasoning-versus-conversational behavioral contrast, including gain/loss, order, explanation, and description/history effects, and the association with mathematical reasoning training. *Framing Matters* owns representation-level framing intervention; Hao et al. own generic thought-injection evidence. L12 cannot claim that reasoning models are more rational, that frame labels are decodable, or that traces generally affect answers.

## C. What We Actually Tested

- **L12-E01:** commit-pinned parent artifact and exact appendix stimulus audit.
- **L12-E02:** 3 published prospects x gain/loss x both orders x 20 samples on exact sibling Instruct-SFT and Think-SFT revisions. The common base was also audited but failed semantic instruction adherence.
- **L12-E03:** final-prompt residual frame probe across all 33 embedding/layer states, leave-one-prospect-out with 500 label shuffles per layer.
- **L12-E04:** preregistered injected-`</think>` mode intervention; invalid because generation continued reasoning and produced 0/240 strict direct answers.
- **L12-E05:** forced readout after own, empty, or matched opposite-frame natural reasoning prefixes on 48 completed traces.
- **L12-E06:** answer-label-free correct, swapped, or rule-only calculation prefixes across all 12 cells.

## D. Results

Published aggregate audit across nine matched prospect/style cells:

| Branch | Frame consistency | 95% CI |
|---|---:|---:|
| Instruct-SFT | 0.843 | [0.751, 0.913] |
| Think-SFT | 0.965 | [0.938, 0.991] |

Our strict native-template run:

| Branch | Valid | Frame consistency | Order consistency | EV-consistent |
|---|---:|---:|---:|---:|
| Instruct-SFT | 240/240 | 0.817 [0.625, 0.958] | 0.783 | 0.508 |
| Think-SFT | 219/240 | 0.992 [0.950, 1.000] | 0.992 | 0.995 |

Think-minus-Instruct frame consistency is +0.175, hierarchical-bootstrap 95% CI [0.025, 0.367]. The order-consistency difference CI is [0.092, 0.408]. The base generated unrelated multiple-choice continuations, so a generated-behavior base delta is not identifiable.

The frame probe reaches 1.0 through most early/middle Think layers and 0.75 at the final layer; the final score equals that layer's shuffle 95th percentile. With 12 lexically explicit conditions, this is only evidence that prompt frame information is not obviously erased early.

E05 correct-option margins are +9.34 with the own trace, -0.08 with an empty trace, and -9.07 with an opposite-frame trace. Own-minus-empty is +9.42 [8.54, 10.10]; own-minus-opposite is +18.41 [17.46, 19.32]. E06 does not isolate arithmetic content: correct-minus-rule-only is +0.32 [-3.92, 4.33], and correct-minus-swapped is +0.39 [-0.13, 0.96].

Raw and summarized results are under `results/parent_audit/`, `results/pilot_seed29/summary.json`, `results/pilot_seed29/frame_probe.json`, `results/pilot_seed29/reasoning_prefix_intervention/`, and `results/pilot_seed29/calculation_intervention/`.

## E. Interpretation

Current account ranking:

1. **Inference-time trajectory/deliberation:** strengthened. Think-SFT is nearly perfectly invariant and its complete natural trace causally controls the final readout.
2. **Preserved context plus downstream policy/readout:** plausible. Frame identity is recoverable before generation, but its causal use has not been tested.
3. **Representational canonicalization:** not supported by the cheap diagnostic, but not ruled out at task-relevant states.
4. **Arithmetic specialization:** weakened as a simple snippet account by E06; the broader arithmetic-transparency boundary is untested.

E05 cannot be promoted to “arithmetic causes invariance”: natural traces contain decision conclusions, and the answer-leakage-controlled operation does not reproduce the large margin effect.

## F. Data / Identification Validity

Checkpoint revisions, prompt hashes, seeds, invalid outputs, templates, and parser rules are recorded. The two SFT models are sibling branches from a common base, not a sequential lineage. Native chat templates are required for generated behavior. The common base is valid for teacher-forced activation/logit diagnostics but not instruction-following behavior. Only three parent prospects exist, so uncertainty is clustered at prospect level and external validity remains narrow.

E04 is a documented failed operation, not evidence: fresh work and our outputs both show that `</think>` need not stop reasoning. E03 is a lexical decodability diagnostic, not mechanism. E05 is a causal forced-readout result, but E06 exposes its answer-content boundary.

## G. Novelty After Seeing the Result

Closest papers are *Mind the DH Gap*, *Framing Matters*, *Reasoning Traces Shape Outputs but Models Won't Say So*, and *`</think>` Doesn't Stop Reasoning*. Strongest reviewer compression is **“Mind the DH Gap plus a standard thought-injection test.”** That compression currently remains dangerous. The full identity remains available only if the next phase identifies how the decision state is constructed from preserved frame information and demonstrates a natural arithmetic/deliberation boundary.

## H. ACL / EMNLP / NAACL Main Alignment

- **RQ scale:** Main-level and easy to state.
- **Evidence strength:** strong behavioral gate; one causal readout effect with a serious content-specificity limitation.
- **Mechanism depth:** promising but below Main; prompt-to-trajectory-to-choice localization is incomplete.
- **Novelty:** paper-level corridor remains, but generic trace causality is already owned.
- **Consequence:** a potential reinterpretation of “reasoning-induced rationality” as trajectory-dependent computation, not established yet.
- **Weakest dimension:** decision-specific mechanism and boundary generalization.

The project now resembles a strong Main question with pilot leverage, not yet a Main paper claim.

## I. Verdict

**CONDITIONAL.** The behavioral substrate and branch contrast pass. Continue the project, but do not promote canonicalization, policy override, or arithmetic mediation until a decision-specific causal operation survives answer-leakage controls.

## J. Next Smallest Decisive Experiment

Patch the matched own versus opposite-frame trajectory state into the target computation layer by layer at the pre-answer position, while separately removing explicit conclusion spans. Success requires a localized switch in target-choice margin that survives conclusion removal. Then cross that localized operation with a small arithmetic-transparent versus arithmetic-obscured matched set. This directly tests whether invariance is carried by a constructed decision state rather than generic trace text.
