# ssn-taste

This directory is the working ledger for the Sasano-taste-driven NLP/LLM research-question search started on 2026-09-16.

## Venue hierarchy for research taste

The search targets **ACL / EMNLP / NAACL Main**. These three venues are the primary external calibration for what counts as a strong, appropriately scoped NLP/LLM research question.

**TACL / ICLR / ICML / NeurIPS** may be used as secondary calibration when they illuminate scientific-question quality, causal/mechanistic reasoning, representation analysis, post-training, or adjacent methodology.

**EACL / AACL are NOT taste-calibration venues for this search.** They may be searched aggressively for novelty checking, nearest-prior discovery, and duplicate detection, but their topic/style distribution must not be used to decide what we should pursue. In other words: an EACL/AACL paper can kill or narrow an idea because it already answered the question, but it cannot make an idea attractive merely because it resembles accepted EACL/AACL work.

The governing rule is advisor fit first: questions should be easy to understand, genuinely unanswered, clearly differentiated from nearest prior work, and testable with clean experiments whose claims do not exceed the evidence. At every search and filtering step, explicitly check both **Sasano taste** and **ACL/EMNLP/NAACL Main taste** rather than drifting toward generic LLM trends.

User-specific practical preferences are also applied: avoid benchmark-centric work, avoid topics that require unusually difficult data construction, and avoid heavily linguistic topics unless the semantics/phenomenon is simple and easy to explain.

Files:

- `FAILED_TOPICS.md`: ideas that were seriously considered and then dropped, with the concrete novelty/fit/feasibility reason. Do not revive these without new evidence that directly resolves the recorded failure reason.
- `SELECTED_TOPICS.md`: ideas that survive novelty and Sasano-taste checks and are worth concrete pilot design or execution.

This ledger is intentionally lighter than the old gate-heavy process. A topic should not be killed merely because it lacks a deep mechanism, a dramatic anomaly, or an Outstanding-Paper-scale contribution. Hard reasons to reject are mainly: the exact question is already answered, the nearest-prior difference is too small, the question is not naturally worth asking, or there is no realistic experimental path.
