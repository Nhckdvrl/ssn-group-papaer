# L11 Live Novelty Audit

**Search date:** 2026-09-09

## Search Protocol

Searched ACL Anthology, arXiv, author pages, and title/code queries for task gradient magnitude, gradient coherence, score-function geometry, multi-task RL, policy KL/function movement, data selection, and task weighting. No work dated after 2026-09-09 can yet exist; this audit covers indexed work through the current date.

## Closest Current Work

- Wu et al., *Imbalanced Gradients in RL Post-Training of Multi-Task LLMs*, Findings of EACL 2026: owns the anomaly, estimator, reward/advantage/length controls, and gradient/gain mismatch. <https://aclanthology.org/2026.findings-eacl.164/>
- Yu et al., *PAC: Progress-Augmented Advantage Curriculum for Multi-Task Reinforcement Learning of LLMs*, EMNLP 2026 Main: operationalizes the distinction between advantage-derived update magnitude and recent reward gain for curriculum allocation. It owns a practical mixture method, not the source or meaning of cross-task parameter loudness. <https://arxiv.org/abs/2608.30528>
- Lv et al., *GMTS*, Findings of EMNLP 2026: uses gradient magnitude to rank tokens and explicitly notes that entropy-to-gradient relations do not transfer uniformly across answers. It raises the stakes for construct validity but studies within-answer token selection, not cross-task loudness/gain miscalibration. <https://arxiv.org/abs/2608.30632>
- Zhu et al., *SFT Conflicts, RL Coexists* (2026): attributes SFT/RL multi-task interference differences to sparse, near-orthogonal RL updates and advantage-normalized variance. It is the closest direction/coherence neighbor; it does not explain why RL tasks have different magnitudes or calibrate them to function movement. <https://arxiv.org/abs/2608.03573>
- Li and Li, *Pre-carved Niches* (2026): tracks task partitions, gradients, effective updates, and weights during small-model pretraining. Its “gradient supply does not propagate to updates/weights” observation is a measurement neighbor, but its object, regime, and conclusion differ. <https://arxiv.org/abs/2609.01170>
- GradNorm, PCGrad/gradient surgery, Modular Gradient Surgery, CGPO, LearnAlign, and VIGOR own generic balancing, conflict, curvature, selection, and gradient-norm-as-signal ingredients.

## Reviewer Compression After Refresh

Strongest attack: **“Imbalanced Gradients plus PAC/GMTS diagnostics.”** It wins if the project only correlates another statistic with gradient norm or proposes weighting. It does not win if the paper identifies a natural LLM-level source of loudness, manipulates it within task, and shows that a function-calibrated pressure quantity changes the scientific interpretation.

## Current Novelty Verdict

**PASS for pilot, guarded.** No located paper owns the full identity:

> established gradient/gain paradox -> score/aggregation anatomy -> controlled within-task manipulation -> parameter/function calibration -> consequence for multi-task RL measurement.

The post-result audit must be rerun around the winning mechanism.

