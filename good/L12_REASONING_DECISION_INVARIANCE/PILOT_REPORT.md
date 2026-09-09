# L12 Mechanism Pilot Report

**Date:** 2026-09-09  
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

## D. Results

Behavioral frame consistency is **0.817** for Instruct-SFT and **0.992** for Think-SFT; difference **+0.175 [0.025, 0.367]**.

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

- Instruct-SFT frame consistency: **0.729 [0.670, 0.785]**.
- Think-SFT frame consistency: **0.977 [0.960, 0.993]** on 35 analyzable decisions.
- Think-minus-Instruct difference: **+0.242 [0.179, 0.302]**; worst/best missing-unit bounds **[0.221, 0.249]**.
- Think-minus-Instruct trajectory-minus-prompt control: **+0.399 [0.337, 0.464]**, positive on **36/36** decisions.

E11 repeats state substitution on 18 preregistered stratified decisions. The mean margin again reverses at layer 17; layer-31 donor shift is **+4.868 [4.056, 5.813]**, positive on **18/18** decisions.

Raw and summarized results are in `results/trajectory_takeover_seed43/`, `results/state_substitution_seed43/`, `results/control_reorganization_seed43/`, `results/breadth_seed71/`, and `results/breadth_state_seed73/`.

## E. Interpretation

The best current answer is **progressive trajectory construction with late consolidation**. The reasoning before explicit commitment already establishes decision direction; the terminal portion strongly amplifies it; a late pre-answer state carries it into decoding. Crucially, the same stripped trajectory text has strong, prospect-consistent control in Think-SFT but heterogeneous near-zero average control in Instruct-SFT.

This strengthens distributed takeover, decision-state mediation, and causal-control reorganization. It weakens pure frame erasure, arithmetic-snippet, and terminal-only accounts.

## F. Data and identification validity

Trajectory stripping removed a terminal conclusion from all 47 valid traces, left no decision markers, produced no empty traces, and retained 48.1% of characters on average. E08 transfers hidden state without donor text. E09 independently crosses prompt and trajectory frames and uses identical donor text across branches.

The main mechanism now has 36-unit control breadth and 18-unit state-substitution breadth. Native answer-transition formats still differ across siblings, and released sibling branches do not isolate one training operation. Think-SFT had a 0.875 valid-generation rate at the 1,024-token cap; one decision lacked one full cell, and sensitivity bounds are reported.

## G. Novelty after seeing the result

The closest compression is:

> Mind the DH Gap + iterative/causal CoT + persistent latent policy states.

The paper survives only because E09 links the behavioral branch transition to a direct reallocation between prompt and trajectory control. Generic latent-state or CoT-causality claims are removed from our novelty claim.

## H. ACL / EMNLP / NAACL Main alignment

- **RQ scale:** strong and natural.
- **Evidence strength:** coherent causal chain plus independent-decision replication.
- **Mechanism depth:** now credible; E07, E08, and E09 advance one explanation rather than accumulating probes.
- **Novelty:** viable but narrowed by 2026 latent-policy-state work.
- **Consequence:** explains what the invariance transition changes about decision formation.
- **Weakest dimension:** checkpoint/model-family breadth and exact training attribution.

## I. Verdict

**GO.** C1-C3 survive dozens of independent decisions and a preregistered state-replication subset. This clears the scientific mechanism gate; it does not erase the remaining checkpoint-breadth limitation.

## J. Next smallest decisive experiment

**E12:** run the already preregistered Instruct-DPO/Think-DPO continuation-axis validation once their exact weights are locally available. The first attempt was stopped because external transfer stayed below 0.1 MB/s; no result is claimed.
