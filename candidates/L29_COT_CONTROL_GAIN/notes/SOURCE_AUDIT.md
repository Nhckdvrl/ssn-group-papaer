# Primary-source and interface audit — 2026-09-12

- CoT-Control code: https://github.com/YuehHanChen/CoTControl, pinned
  5d78aeffe0152ba087c2d31cd07712d029c64785. Existing prompt families and QA CSV used.
- CoT-Control paper: https://arxiv.org/html/2603.05706v1, Appendix E.
  The released 3.1 Math trajectory is explicitly used by the mother experiment.
  Its RL-Zero interface is raw text completion, no chat template. The models do not
  provide a reliable separate think channel. Therefore this audit uses short
  pre-answer prefixes and reports answer/termination events; it does not mechanically
  copy the parent's removal of the last 10% of full output into a local checker.
- Model card: https://huggingface.co/allenai/Olmo-3.1-7B-RL-Zero-Math.
  API refs and immutable revisions in configs/models.json; early/middle/late branches
  all come from this one release. We do not compare 3.0 vs 3.1 endpoints or unrelated
  SFT/DPO variants. The model card's final 'Model Details' section erroneously repeats
  Code dataset text, so the trajectory identity relies on model ID, declared dataset,
  branch sequence and the mother's explicit identification, not that copied paragraph.
- MathIF: https://arxiv.org/abs/2505.14810 and
  https://github.com/TingchenFu/MathIF. MathIF and 'Scaling Reasoning, Losing Control'
  are the SAME work, not independent owner evidence. The reminder recovery belongs
  to this prior. L29 uses a reminder as an instrument, not a method contribution.
- Compliance vs Sensibility: https://arxiv.org/abs/2604.27251.
  Logical-schema conflicts, representation and steering already occupy the broad
  internally encoded but behaviorally overridden story. None of this pilot uses probes.

A lightweight fresh search did not locate an exact local causal-gain training-curve
owner. This is not a claim of exhaustive novelty clearance. Scientific priority is
still conditional on obtaining identifiable evidence and returning to selection.
