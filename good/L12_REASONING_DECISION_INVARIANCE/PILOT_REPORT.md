# L12 Full Study Report

**Date:** 2026-09-10
**Verdict:** **GO - MAIN-PAPER EVIDENCE PROGRAM COMPLETE**

## A. Current RQ

> Why do reasoning models become invariant to some changes in presentation while
> remaining sharply sensitive to others, and does reasoning reorganize decision
> control from prompt form toward an evidence-bearing trajectory and its pre-answer
> state?

## B. What Prior Work Owns

*Mind the (DH) Gap!* owns broad risky-choice differences between conversational
and reasoning models, including framing and description/history effects. Human
decision science owns the distinction between presentation effects and finite-
sample evidence differences. Recent reasoning work owns generic trace injection,
iterative answer construction, distributed CoT effects, cue-delivery effects, and
reasoning-induced latent policy states.

L12 therefore cannot claim merely that reasoning models are invariant/rational,
that CoT affects answers, that a decision emerges before the final token, that a
late state can be patched, or that finite histories contain sampling error.

## C. What We Actually Tested

| Stage | Experiments | Scientific role |
|---|---|---|
| Parent and constraint | E01-E03 | Reconstruct the parent stimuli/checkpoint relation; confirm sibling behavior; test and weaken simple representation erasure |
| Causal process | E05-E07 | Compare own, opposite, empty, arithmetic-only, and terminal-stripped natural trajectories |
| Internal carrier | E08, E11, E15, E19 | Direction-specific residual-state substitution over discovery, frozen breadth, external, and 48-decision natural sets |
| Training/route bridge | E09-E14 | Cross prompt and trajectory under OLMo SFT/DPO siblings, Qwen same weights, and bounded Llama ecosystem validation |
| Natural breadth and confirmation | E16-E18P | 151 CPC18 calibration decisions, 44 untouched competition decisions, frozen causal confirmation, and 3-to-20 generation precision audit |
| Selective-sensitivity crown | E20-E22 | Prospectively orthogonalize form and evidence on 137 previously unscored real decisions; test behavior, trajectory control, state content, and external-family replication |
| Supporting diagnosis | E18L | Paired 20/100 histories; retained as inconclusive because raw-table truncation prevents unconditional inference |

The base decision is always the scientific unit. Histories, orders, generations,
trajectory samples, factorial cells, patch directions, and layers are nested.

## D. Results

### D1. Decisions are constructed and consolidated in reasoning

- Terminal-stripped own trajectories exceed empty by **+2.624 [2.008, 2.988]**
  and opposite-stripped trajectories by **+4.863 [3.469, 5.773]**. Restoring
  terminal choice language adds **+7.047 [6.746, 7.402]**.
- OLMo opposite-decision state transfer is negligible early, reverses mean target
  margin at layer 17, and reaches **+5.090 [3.766, 5.977]** at layer 31.
- On the frozen 18-decision replication, final donor shift is **+4.868 [4.056,
  5.813]**, positive on 18/18 decisions.
- Across 48 natural CPC18 decisions, the effect first reverses mean target margin
  at layer 18 and reaches **+7.094 [5.914, 8.276]**, positive on 45/48 decisions.
- DeepSeek supplies external state triangulation: final donor shift **+1.222
  [0.299, 2.181]**. The weaker unit consistency prevents a shared layer-geometry
  claim.

### D2. Reasoning reallocates causal control

- Across 36 independent gain/loss decisions, OLMo Think-minus-Instruct
  trajectory-relative control is **+0.399 [0.337, 0.464]**, positive on 36/36.
- The OLMo DPO sibling contrast persists at **+0.472 [0.401, 0.555]**.
- With Qwen3 weights fixed, thinking versus non-thinking changes trajectory-
  relative control by **+0.604 [0.550, 0.661]**.
- On 151 natural description/history decisions, controlled-axis differences are
  **+0.202 [0.162, 0.244]** for OLMo and **+0.163 [0.121, 0.205]** for Qwen.
- On 44 untouched competition decisions, the frozen primary gate passes for both:
  OLMo **+0.097 [0.002, 0.180]**, Qwen **+0.219 [0.152, 0.288]**.
- The corresponding OLMo behavioral difference is null, **-0.013 [-0.095,
  0.065]**, and remains null with 20 generations/cell, **-0.011 [-0.089,
  0.067]**. This productive failure exposed that description/history changed
  evidence as well as form.

### D3. Reasoning changes what models are sensitive to

E20 freezes 137 previously unscored real CPC18 decisions and independently
crosses two evidence directions with two information-equivalent forms: the exact
same observations as a raw sequence or an empirical frequency summary.

| Axis | Change in form sensitivity | Change in evidence sensitivity | Change in selective sensitivity |
|---|---:|---:|---:|
| OLMo Think - Instruct | **-0.341 [-0.364, -0.317]** | **+0.888 [0.865, 0.911]** | **+1.229 [1.195, 1.262]** |
| Qwen thinking - non-thinking | **-0.266 [-0.291, -0.241]** | **+0.443 [0.397, 0.491]** | **+0.709 [0.638, 0.778]** |
| DeepSeek - Llama | **-0.139 [-0.159, -0.119]** | **+0.857 [0.839, 0.876]** | **+0.996 [0.962, 1.031]** |

The joint selective difference remains positive under sharp invalid-output
assignment for all three axes. The Llama ecosystem result is external replication,
not a matched training attribution.

The causal factorial shows that the same shift occurs in the controller:

| Axis | Raw-history change in `Delta_R - Delta_P` | Summary change in `Delta_R - Delta_P` |
|---|---:|---:|
| OLMo | **+0.459 [0.401, 0.518]** | **+0.584 [0.532, 0.638]** |
| Qwen | **+0.563 [0.506, 0.621]** | **+0.749 [0.689, 0.808]** |
| Llama ecosystem | **+0.175 [0.131, 0.221]** | **+0.143 [0.106, 0.180]** |

Prompt-control differences are near zero; trajectory-control differences produce
the effect. In E21, final-layer donor evidence control is **+0.763 [0.694,
0.828]**, donor-form sensitivity is **0.174 [0.124, 0.227]**, and state
selectivity is **+0.590 [0.476, 0.704]**. The evidence effect is near zero at
layers 0/8, appears at 16, and becomes large at 24/31.

### D4. Supporting history-length audit

Empirical EV direction agrees with the generating distribution on 0.750 of
20-trial histories and 0.847 of matched 100-trial histories. However, 100-trial
raw tables cause length truncation and reasoning history-cell valid rates of only
0.332/0.343. Conditional paired estimates disagree across OLMo and Qwen, and
sharp bounds cross zero. E18L is therefore **inconclusive** and carries no claim.

### Result pointers

- Selective behavior/control: `results/cpc18_form_evidence_seed157/`
- Selective state: `results/cpc18_selective_state_seed173/`
- External replication: `results/cpc18_form_evidence_llama_seed179/`
- Heldout precision: `results/cpc18_competition_precision_seed149/`
- History-length audit: `results/cpc18_history_length_seed163/`
- Paper-ready synthesis: `results/selective_sensitivity_story/`

Raw continuations and state rows remain local and ignored. Compact summaries,
unit metrics, model metadata, row/hash manifests, and execution audits are tracked.

## E. Interpretation

The results support one cumulative mechanism:

> Natural reasoning progressively constructs a decision, consolidates it into a
> causally sufficient pre-answer state, and shifts final-decision control away
> from prompt-level presentation toward that trajectory/state. Crucially, this
> shift is selective: the new controller tracks decision evidence far more
> strongly than the form in which equivalent evidence arrives.

Behavioral invariance is therefore not indiscriminate insensitivity. When form
changes but evidence is fixed, reasoning regimes become more invariant. When
evidence changes, those same regimes change decisions sharply. The memorable
answer is: **reasoning reallocates sensitivity from form to evidence.**

## F. Data / Identification Validity

- E20 uses previously unscored real CPC18 histories. Raw versus summary prompts
  contain exactly the same observed payoff multiset; opposite-evidence histories
  are strength-matched without model outputs.
- E20 has 137 independent decisions and 43,840 behavior generations. E22 adds
  21,920 behavior generations and 4,384 complete causal-factorial scores.
- All behavior condition keys, row counts, history IDs, prompt hashes, four-cell
  factorials, raw bytes, and SHA-256 values pass validators.
- E21's first run used displayed rather than underlying A under reversed order.
  It is explicitly invalid, excluded, and rerun after the coordinate fix and
  synthetic direction test. The corrected 2,560-row execution audit passes.
- Base-decision cluster bootstrap is primary. No generation- or layer-level
  pseudo-replication supports inference.
- OLMo identifies a common-base branch association; Qwen identifies a same-weight
  native-route contrast that also changes channel/position; Llama/DeepSeek is an
  unmatched external replication. The triangulated computation is broader than
  any one axis, but no single optimization step is isolated.
- OLMo Think and DeepSeek have nontrivial invalid rates. Joint selective effects
  survive sharp assignment; component claims are qualified where bounds cross.

## G. Novelty After Seeing the Result

The closest compression is:

> *Mind the DH Gap* + decision-science sampling bias + trace injection/persistent
> latent policy states.

It misses the complete identity. Prior work does not combine an established
reasoning-invariance puzzle with: progressive natural-trajectory construction;
direction-specific internal state mediation; crossed prompt/trajectory control;
a prospective orthogonal form-by-evidence intervention; and the finding that the
reasoning-associated controller is selectively evidence-sensitive across sibling,
same-weight, and external-family axes.

The novelty is not any ingredient. It is the answer:

> **Reasoning changes what models are sensitive to by moving causal decision
> control from presentation form toward evidence integrated in a trajectory-built
> state.**

Fresh paper-by-paper ownership and links are in `RELATED_WORK.md`.

## H. ACL / EMNLP / NAACL Main Alignment

- **RQ scale:** explains and reconceptualizes an ACL Outstanding Paper phenomenon;
  it is not a local interpretability question.
- **Evidence strength:** prospective construct decomposition, complementary
  identification axes, untouched confirmation, exact execution audits, causal
  text intervention, and text-free state transfer.
- **Mechanism depth:** behavior -> progressive process -> internal carrier ->
  training/route control shift -> selective behavioral consequence.
- **Stimulus breadth:** dozens to hundreds of independent decisions, with both
  controlled gain/loss and natural human-experiment history manipulations.
- **Model breadth:** one deep discovery family, one same-weight cross-family axis,
  one external post-training ecosystem, plus OLMo checkpoint persistence.
- **Novelty:** survives direct comparison with *Mind the DH Gap*, *Racing Thoughts*,
  *The LLM Language Network*, *What Makes a Good Reasoning Chain?*, *Reasoning
  Traces Shape Outputs*, and *Persistent Latent Policy States*.
- **Consequence:** common robustness evaluations can confuse invariance to form
  with failure to respond to changed evidence; the proposed decomposition tells
  them apart.
- **Current weakest dimension:** training attribution remains triangulated rather
  than isolated, and the deepest state surgery is in OLMo. This is a limitation,
  not a reason to shrink the paper into a route-only claim.

Relative to the structural comparators, L12 now matches the needed progression:
one clear computational hypothesis, correlational constraint, causal process,
causal carrier, broad behavioral test, falsification, decisive decomposition,
external validation, and consequence. Additional model count or layer scans would
increase volume without deepening that chain.

## I. Verdict

**GO.** L12 has moved beyond pilot status. The three load-bearing claims are
supported by distinct but linked interventions, 137-unit prospective confirmation,
three complementary model axes, internal mediation, and audited uncertainty. The
E18 surprise strengthened the paper by revealing selective rather than blanket
invariance; E20-E22 confirm that reconceptualization without post-hoc filtering.

## J. Next Smallest Decisive Operation

The next decisive operation is **full manuscript assembly and adversarial paper
review**, not another exploratory model or patch variant. Draft around the three-
claim chain and use the tracked Main-calibration table to identify any genuinely
load-bearing omission. New experiments are warranted only if the manuscript review
uncovers a specific inference that the present behavior, trajectory factorial,
and state substitution cannot support.
