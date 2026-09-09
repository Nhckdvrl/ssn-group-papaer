# L12 Full Study Report

**Date:** 2026-09-10
**Verdict:** **GO**

## A. Current RQ

> How does reasoning-oriented post-training change the causal formation of
> presentation-sensitive decisions, and is behavioral invariance a necessary
> consequence of that change?

## B. What prior work owns

*Mind the (DH) Gap!* owns broad reasoning-model invariance in risky choice.
Recent work owns generic trace injection, iterative answer construction,
distributed CoT patching, cue-dependent CoT faithfulness, and reasoning-induced
latent policy states. L12 cannot claim merely that reasoning models are more
rational, CoT affects answers, decisions emerge over tokens, or reasoning
fine-tuning reorganizes latent dynamics.

## C. What we actually tested

- **E01-E03:** parent/stimulus audit, shared-base OLMo branch behavior, and a
  noncausal frame-information diagnostic.
- **E05-E09:** natural-trajectory interventions, terminal stripping, all-layer
  pre-answer state substitution, and prompt-by-trajectory causal decomposition.
- **E10-E15:** 36-decision breadth, frozen state replication, OLMo DPO
  persistence, Qwen same-weight route comparison, and Llama/DeepSeek external
  triangulation.
- **E16-E17:** 151 independently collected CPC18 calibration decisions, exact
  distribution versus three real 20-trial histories, six regimes, and the frozen
  causal factorial.
- **E18:** one-shot confirmation on the untouched CPC18 competition set under a
  contract committed before source access.
- **E19:** symmetric opposite-choice state substitution over 48 frozen natural
  CPC18 decisions and all 32 OLMo layers.

The base decision is always the scientific unit. Histories, displayed order,
samples, factorial cells, patch directions, and layers are nested observations.

## D. Results

### Mechanism discovery

- Terminal-stripped own trajectories exceed empty by **+2.624 [2.008, 2.988]**
  and opposite-stripped trajectories by **+4.863 [3.469, 5.773]**. Restoring the
  terminal portion adds **+7.047 [6.746, 7.402]**.
- OLMo pre-answer state transfer is negligible early, reverses the mean target
  margin at layer 17, and reaches **+5.090 [3.766, 5.977]** at layer 31.
- Across 36 independent decisions, Think-minus-Instruct trajectory-relative
  control is **+0.399 [0.337, 0.464]**, positive on 36/36 decisions. The
  preregistered 18-decision state replication reaches **+4.868 [4.056, 5.813]**.
- The OLMo DPO contrast persists at **+0.472 [0.401, 0.555]**. Qwen's same-weight
  thinking route exceeds non-thinking by **+0.604 [0.550, 0.661]**.

### Natural presentation breadth

On 151 CPC18 calibration decisions:

| Axis | Behavior consistency difference | `Delta_R - Delta_P` difference |
|---|---:|---:|
| OLMo Think - Instruct | +0.225 [0.177, 0.271] | +0.202 [0.162, 0.244] |
| Qwen thinking - non-thinking | +0.276 [0.223, 0.327] | +0.163 [0.121, 0.205] |
| DeepSeek - Llama | -0.225 [-0.264, -0.188] | +0.019 [-0.005, 0.043] |

Prompt-control differences include zero on both controlled axes. Their positive
control contrasts come from stronger trajectory control. Llama's 0.970
presentation consistency coexists with chance-level exact-EV choice (0.502
explicit, 0.499 history), demonstrating that invariance is not rationality.

### Preregistered competition confirmation

Forty-four of 60 untouched problems pass unchanged inclusion criteria, exceeding
the frozen gate of 40:

| Axis | Behavior consistency difference | `Delta_R - Delta_P` difference |
|---|---:|---:|
| OLMo Think - Instruct | -0.013 [-0.095, 0.065] | **+0.097 [0.002, 0.180]** |
| Qwen thinking - non-thinking | **+0.163 [0.051, 0.268]** | **+0.219 [0.152, 0.288]** |

The preregistered primary causal-route gate passes on both axes. The supporting
behavioral hypothesis passes for Qwen and fails for OLMo. In E19, natural CPC18
state substitution first reverses mean margin at layer 18 and reaches **+7.094
[5.914, 8.276]**, positive on 45/48 decisions with 0.823 donor flips.

Raw files are local and ignored. Compact results are in
`results/cpc18_replication_summary.json`, the two `cpc18_*_seed*` directories,
and the earlier experiment directories listed in `EXPERIMENTS.md`.

## E. Interpretation

The supported mechanism is **progressive trajectory construction, late
pre-answer state mediation, and causal-control reorganization**. Reasoning-oriented
computation consistently gives self-generated trajectories more causal control
over final choices. The untouched OLMo result falsifies the stronger, tempting
account that this route shift is by itself sufficient for behavioral invariance.

The scientific answer is therefore two-level: reasoning training changes *what
computational route controls the decision*; presentation invariance occurs only
contingently, rather than as a defining property of that route change.

## F. Data / Identification Validity

- CPC18 contributes real human experimental histories, exact model-independent
  EV gold, and independent base problems rather than synthetic worlds.
- The competition contract was committed as `9e4a532` before source access.
- The stricter `cpc18_terminal_commitment_v3` parser was frozen before heldout
  access and prevents prompt restatements from masquerading as commitments.
- Every raw row, four-cell factorial, summary count, byte count, and SHA-256
  passes `scripts/validate_cpc18_execution.py` on both splits.
- Base-decision bootstrap is primary. Calibration MixedLM fits did not converge;
  heldout fits have boundary/Hessian warnings. Neither supports the main claim.
- OLMo is a sibling-branch association, Qwen compounds native route with channel
  placement, and Llama/DeepSeek is unmatched. None is presented as an isolated
  one-step training treatment.

## G. Novelty After Seeing the Result

The strongest compression is:

> Mind the DH Gap + Persistent Latent Policy States + Sequential Activation
> Patching / FACE-Eval.

It does not own the full identity: an established invariance puzzle; natural,
terminal-stripped trajectory construction; text-free state mediation; frozen
prompt-by-trajectory intervention under sibling and same-weight comparisons; a
qualitatively different presentation family; and an untouched confirmation that
separates control-route change from behavioral invariance. Fresh audit details
are in `RELATED_WORK.md`.

## H. ACL / EMNLP / NAACL Main Alignment

- **RQ scale:** natural and consequential; it reinterprets a 2026 Outstanding
  Paper phenomenon rather than introducing a local probe question.
- **Evidence:** correlational constraint, textual intervention, hidden-state
  intervention, controlled axes, 151-problem breadth, and heldout confirmation.
- **Mechanism depth:** C1-C3 form one causal chain rather than a layer catalogue.
- **Novelty:** the full paper identity survives the September 2026 audit.
- **Consequence:** reasoning can relocate sensitivity instead of eliminating it;
  behavioral invariance and rationality must not be inferred from route alone.
- **Weakest dimension:** no available checkpoint pair isolates a single training
  operation, so the training claim remains an association across complementary
  identification strategies.

## I. Verdict

**GO.** The preregistered primary confirmation passed, the internal carrier
replicated on natural stimuli, and the heterogeneous behavior result improved the
scientific interpretation instead of requiring a rescue analysis.

## J. Next Smallest Decisive Experiment

No further experiment is currently justified. The planned mechanism, breadth,
boundary, and confirmation chain is complete. The next decisive operation is a
paper-level robustness review: draft the manuscript around C1-C3 and add data only
if that draft exposes a load-bearing identification gap.
