# L11 First-Round Pilot Report

**Date:** 2026-09-09  
**Verdict:** **CONDITIONAL**

## A. Current RQ

Why can one objectively verified reasoning task induce a much larger policy gradient than another without commensurately larger learning gain, and which part of the score-function update creates that loudness?

## B. What Prior Work Owns

Wu et al. (Findings of EACL 2026) own multi-task RL gradient imbalance, its mismatch with learning gain, the split-batch cross-product estimator, and basic reward/advantage/length checks. GradNorm, gradient surgery, CGPO, LearnAlign, VIGOR, PAC, and GMTS own balancing, conflict, curvature, selection, curriculum, and gradient-norm-signal ingredients. L11 cannot claim any of these alone.

## C. What We Actually Tested

- **L11-E01a:** Qwen2.5-7B-Instruct, simple Arithmetic/MATH-500 numeric, 8 prompts/task x 4 rollouts, 192-token cap. Invalid due 100% cap hits and missing-format advantage collapse.
- **L11-E01b:** same run at 512 tokens. Truncation repaired, but simple Arithmetic saturated: 1/8 informative advantage groups.
- **L11-E01c:** preregistered arithmetic difficulty calibration. Six-term sums selected using reward/support only, then full estimator repeated at generation seeds 17, 18, 19.
- **L11-E02:** full-last-block split cross-product plus deterministic attention-gradient sketches; individual norm, coherence, pairwise cosine, and effective rank.
- **L11-E03:** correctly gated off because E01 did not yield a stable contrast.

## D. Results

Full-last-block squared-norm cross-products:

| Seed | Arithmetic | MATH numeric | Ordering |
|---|---:|---:|---|
| 17 | 0.02772 | -0.000092 | Arithmetic (MATH estimate sign-unstable) |
| 18 | 0.00340 | 0.01391 | MATH |
| 19 | 0.00000 | -0.01164 | indeterminate |

Arithmetic reward means were 0.888/0.831/0.859; MATH 0.594/0.588/0.691. Arithmetic/MATH mean individual attention-gradient norms were 0.0886/0.1224, 0.1033/0.0937, and 0.0568/0.0584. Coherence ratios were 0.353/0.240, 0.340/0.280, and 0.350/0.349.

Every per-seed prompt-bootstrap interval for the full-block sketch included zero. The cross-product estimator's negative values are permissible finite-sample estimates, but their frequency shows insufficient support.

Raw and summaries:

- `results/pilot_seed17_len192/`
- `results/pilot_seed17_len512_simple_arithmetic/`
- `results/arithmetic_calibration_seed1702/`
- `results/pilot_seed{17,18,19}_len512/`
- `results/pilot_multiseed_summary.json`

## E. Interpretation

The micro-pilot does **not** reproduce a stable parent contrast. A pure per-example sensitivity account is not supported: individual norm ordering changes across seeds. Aggregation/coherence is the leading routing candidate because Arithmetic coherence exceeds MATH in two seeds and ties in one, but the primary magnitude ordering itself is unstable, so no mechanism account is promoted. Parameter/function miscalibration remains untested.

## F. Data / Identification Validity

Reward, advantage, token normalization, response truncation, estimator bias, and sample support were directly audited. The 192-token result and simple-Arithmetic result are explicitly invalid for mechanism inference. The six-term-sum/MATH run has objective gold and nonzero support, but 8 prompt groups and one checkpoint step are inadequate substitutes for the parent's multi-step EMA. The MATH numeric prefix is a feasibility slice, not representative MATH.

## G. Novelty After Seeing the Result

Closest new threats are PAC (EMNLP 2026 Main), GMTS (Findings of EMNLP 2026), SFT Conflicts/RL Coexists, and Pre-carved Niches. Strongest compression is **“Imbalanced Gradients plus PAC/GMTS diagnostics.”** It currently remains avoidable only if later work identifies and intervenes on a task/output source of loudness and connects it to function movement. No current paper owns that full chain, but there is no result yet to promote.

## H. ACL / EMNLP / NAACL Main Alignment

- **RQ scale:** Main-level; simple and consequential.
- **Evidence strength:** below Main; feasibility gate not passed.
- **Mechanism depth:** absent; diagnostic candidate only.
- **Novelty:** corridor remains, increasingly guarded by 2026 work.
- **Consequence:** plausible measurement implication, untested.
- **Weakest dimension:** stable reproduction/estimator support.

Compared with strong ACL/EMNLP/NAACL Main work, the question is calibrated but the current evidence is not. Expanding claims would lower the bar.

## I. Verdict

**CONDITIONAL.** Keep the RQ alive, do not approve a paper mainline, and do not run causal coherence or function-space experiments until the parent contrast is stable in our stack.

## J. Next Smallest Decisive Experiment

Recover the parent's exact Arithmetic source/config (author code is not publicly linked in the paper/author audit), then run at least 32 prompt groups per task over multiple adjacent checkpoints/steps. Use the documented full-last-block split cross-product and EMA, preregistering success as consistent Arithmetic>MATH ordering across at least 80% of measured steps with a prompt/bootstrap interval excluding equality. Only then run a within-task coherence manipulation and E03 function-space calibration.

