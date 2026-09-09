# L12 ACL/EMNLP/NAACL Main Paper Outline

## Working title

**Who Controls the Choice? Reasoning Reorganizes Causal Decision Formation**

## One-sentence identity

> Reasoning-oriented computation changes not only what language models decide,
> but which computational route controls the decision, shifting control toward a
> progressively constructed trajectory and pre-answer state without guaranteeing
> presentation-invariant behavior.

## Abstract logic

1. **Puzzle:** reasoning models are unusually invariant to equivalent risky-choice
   presentations, but behavioral invariance does not identify how decisions form.
2. **Competing accounts:** presentation erasure, terminal self-commitment, and
   trajectory-mediated control make distinct predictions.
3. **Process:** terminal-stripped natural reasoning already carries decision
   direction; the conclusion strongly consolidates it.
4. **Internal carrier:** opposite-decision pre-answer state substitution transfers
   the final choice with a coherent late-layer profile.
5. **Bridge:** a frozen prompt-by-trajectory factorial shows substantially stronger
   trajectory-relative control in reasoning-oriented branches/routes.
6. **Breadth/confirmation:** this result generalizes from gain/loss framing to
   exact descriptions versus real outcome histories and confirms on an untouched
   CPC18 competition split.
7. **Boundary:** the OLMo route effect confirms without a heldout invariance gain;
   stable route reorganization is not sufficient for invariance. Llama additionally
   shows that invariance can arise from chance-level choice.
8. **Consequence:** reasoning relocates sensitivity rather than simply removing it.

## Main claims and evidence

### C1. Progressive trajectory construction

Decision direction develops before explicit commitment and is then strongly
consolidated. Lead evidence: E07 terminal stripping and opposite-trajectory
contrast. E05-E06 are routing controls, not separate claims.

### C2. Pre-answer state mediation

The trajectory constructs a late internal state that causally carries decision
direction into decoding. Lead evidence: E19 over 48 natural CPC18 decisions;
E08/E11 establish discovery and controlled replication; E15 is external
triangulation. Report a sustained profile, never a privileged-layer claim.

### C3. Causal-control reorganization

Reasoning-oriented computation increases trajectory-relative decision control
under OLMo sibling and Qwen same-weight identification. E17 supplies natural
description/history breadth; E18 is the confirmatory crown. Behavioral invariance
is a contingent outcome, not the definition of the estimand.

## Main figures and tables

1. **Figure 1 - Puzzle and causal graph:** `P -> R -> H -> Y`, with prompt-to-answer
   alternatives and the three competing explanations.
2. **Figure 2 - Progressive construction:** full, stripped, opposite-stripped, and
   empty trajectory contrasts; show terminal amplification explicitly.
3. **Figure 3 - Internal carrier:** E19 donor-directed margin by layer with E08/E11
   replication markers.
4. **Figure 4 - Causal control plane:** `|Delta_P|` versus `|Delta_R|`, separated by
   gain/loss and description/history; use existing PNG/PDF artifacts.
5. **Table 1 - Identification axes:** OLMo sibling/DPO, Qwen same weights, and
   unmatched Llama/DeepSeek with exactly bounded interpretations.
6. **Table 2 - CPC18 calibration and heldout:** behavior, `Delta_P`, `Delta_R`, and
   `Delta_R - Delta_P`, with base-decision counts and clustered intervals.
7. **Figure 5 - Robustness relocated:** calibration and heldout paired arrows from
   standard to reasoning regimes; highlight OLMo's route/behavior dissociation.

## Section structure

1. **Introduction:** parent phenomenon, why behavior cannot identify mechanism,
   paper answer, and three contributions.
2. **Causal framing:** distinguish information availability, prompt control,
   trajectory control, state mediation, invariance, and EV alignment.
3. **Study 1 - How trajectories construct choices:** E03/E07.
4. **Study 2 - What carries the constructed choice:** E08/E11/E19 and E15.
5. **Study 3 - Does reasoning reorganize causal control?:** E09/E10/E12-E14.
6. **Study 4 - Natural presentation breadth and confirmation:** E16-E18.
7. **Discussion:** robustness relocation, why route change is not sufficient for
   invariance, and implications for interpreting reasoning-model behavior.
8. **Limitations:** post-training attribution, inserted-text intervention,
   risky-choice domain, invalid completions, model access, and hidden CoT scope.

## Evidence discipline

- Use base-decision bootstrap as primary throughout; report mixed models only as
  unsuccessful/fragile sensitivity analyses.
- Keep calibration and competition results visibly separate.
- Never call consistency rationality without EV behavior.
- Never call Qwen a pure mode intervention; native channel/position also changes.
- Never call Llama/DeepSeek a matched training comparison.
- Do not elevate probes, layer locations, DPO amplification, model replications,
  or the null item-level correlation into headline claims.

## Reviewer compression defense

**Compression:** *Mind the DH Gap* + latent policy states + sequential CoT patching.

**Answer:** those works own the phenomenon and generic ingredients. L12 directly
crosses prompt and natural-trajectory interventions under complementary training
and route comparisons, connects that control shift to a text-free internal carrier,
and confirms it on a frozen external description/history split. The unexpected
heldout dissociation further shows that causal-route reorganization is a distinct
computational object, not another name for invariance.

## Submission-readiness gate

Before drafting claims into prose, regenerate all compact tables from tracked
summaries, run both execution audits and parser tests, verify raw hashes locally,
and keep all large continuations, checkpoints, caches, and state tensors outside
Git. New experiments require a specific load-bearing gap identified during paper
review; breadth for its own sake is out of scope.
