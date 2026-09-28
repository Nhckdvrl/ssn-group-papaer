# L11 Experiment Registry

**Updated:** 2026-09-09

## L11-E01: Parent-Compatible Feasibility Reproduction

- **Linked claim:** L11-C1
- **Question:** Does Qwen2.5-7B-Instruct reproduce an Arithmetic-over-MATH policy-gradient contrast under a GRPO-style objective while local reward gain is not larger?
- **Unit:** prompt group; four sampled rollouts form one GRPO advantage group.
- **Data:** 8 deterministic multi-digit arithmetic prompts and 8 numeric-answer MATH-500 prompts for gradient estimation; disjoint held-out prompts for local movement/gain.
- **Reward:** `-0.1` missing required answer tag, `0.1` parseable but wrong, `1.0` correct, matching the parent.
- **Estimator:** token-mean GRPO surrogate; group-centered, standard-deviation-normalized advantages; two independent prompt-half gradients and their cross-product for unbiased squared-norm estimation. Full last transformer block is the parent-compatible measurement target.
- **Controls:** prompt/response tokens, reward and absolute advantage, number of rollouts, generation settings, clipping configuration, checkpoint revision.
- **Primary metric:** cross-product estimate of squared full-last-block task gradient.
- **Uncertainty:** prompt-group bootstrap (2,000 resamples) and seed sensitivity in later confirmation; this first run uses seed 17.
- **Kill/reconstruct:** investigate fidelity if ordering is absent or estimator is sign-unstable; do not proceed to a mechanism claim from a failed proxy.
- **Config:** `configs/pilot.json`
- **Command:** `scripts/run_pilot.sh`
- **Raw outputs:** `results/pilot_seed{17,18,19}_len512/raw.jsonl`
- **Summaries:** `results/pilot_seed{17,18,19}_len512/summary.json`
- **Status:** completed across seeds 17-19; feasibility contrast not stable.

### L11-E01a (superseded length-192 run)

The first implementation run capped responses at 192 tokens. All 64 rollouts hit the cap; MATH rewards were almost uniformly missing-format, advantages collapsed, and the full-block MATH estimate was zero. This run is retained at `results/pilot_seed17_len192/` but is **invalid for the task-gradient contrast**. It identified a response-truncation confound before interpretation; the preregistered metrics and seed are unchanged in E01b, with only the cap raised to 512 and EOS padding correctly removed.

### L11-E01b (simple Arithmetic saturation)

At 512 tokens the format confound was repaired, but simple Arithmetic reached mean reward 0.859 with only 1/8 prompt groups having reward variance. The split estimator therefore had a zero-gradient half. MATH had mean reward 0.656 and 6/8 informative groups. This run is valid evidence that this particular Arithmetic subset is saturated, but **not** a valid parent anomaly estimate. Raw: `results/pilot_seed17_len512_simple_arithmetic/`.

### L11-E01c (difficulty calibration)

Before another gradient run, compare three preregistered natural arithmetic families using reward and number of nonzero-advantage groups only: long multiplication, two-product differences, and six-term sums. Select the family closest to the MATH reward/support region; gradient magnitude is not inspected for selection. Raw: `results/arithmetic_calibration_seed1702/`.

Result: six-term sums were selected (mean reward 0.719; 4/4 informative groups), versus long multiplication (0.156; 1/4) and two-product differences (0.088; 1/4). The fixed family is recorded as `six_term_sum_seed1702`.

### L11-E01c seed-17 result and stability extension

The seed-17 point estimate orders Arithmetic above MATH (`0.0277` versus `-9.25e-5` full-block cross-products), while the fixed-coordinate sketch bootstrap intervals both cross zero. Arithmetic has lower mean individual attention-gradient norm (`0.0886` versus `0.1224`) but higher coherence ratio (`0.353` versus `0.240`). This tentatively weakens a pure individual-sensitivity account and strengthens aggregation/coherence, but is not stable evidence. Seeds 18 and 19 are run unchanged as the smallest stability check.

## L11-E02: Gradient Anatomy

- **Linked claim:** L11-C2
- **Question:** Is loudness primarily individual attention-score norm or across-rollout coherence?
- **Measurement:** fixed-coordinate sketches (stride 256, norm-rescaled) of per-rollout gradients over the final self-attention module, validated against the full-last-block aggregate ordering; report mean norm, norm of mean, coherence ratio, pairwise cosine, and effective rank.
- **Interpretation:** this is localization, not causal proof. A winning account must motivate a within-task matched intervention.
- **Status:** completed as a routing diagnostic; no account promoted because E01 was unstable.

## L11-E03: Local Function-Space Calibration

- **Linked claim:** L11-C3
- **Question:** Under the same small task-specific update rule, does raw parameter movement predict held-out sequence KL/log-prob movement and reward movement across tasks?
- **Primary functional metric:** mean token KL on a shared held-out union after one last-block update; secondary metrics are answer log-prob and verifier reward movement.
- **Caveat:** one local last-block step is not a full RL learning curve. It can rank immediate function movement but cannot by itself reproduce the parent's long-horizon learning-gain claim.
- **Status:** preregistered as conditional on E01 producing stable gradients.
