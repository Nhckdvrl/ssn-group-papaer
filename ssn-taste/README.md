# ssn-taste

This directory is the working ledger for the Sasano-taste-driven NLP/LLM research-question search started on 2026-09-16.

The search targets ACL / EMNLP / NAACL Main, with TACL / ICLR / ICML / NeurIPS used for calibration. The governing rule is advisor fit first: questions should be easy to understand, genuinely unanswered, clearly differentiated from nearest prior work, and testable with clean experiments whose claims do not exceed the evidence.

User-specific practical preferences are also applied: avoid benchmark-centric work, avoid topics that require unusually difficult data construction, and avoid heavily linguistic topics unless the semantics/phenomenon is simple and easy to explain.

Files:

- `FAILED_TOPICS.md`: ideas that were seriously considered and then dropped, with the concrete novelty/fit/feasibility reason. Do not revive these without new evidence that directly resolves the recorded failure reason.
- `SELECTED_TOPICS.md`: ideas that survive novelty and Sasano-taste checks and are worth concrete pilot design or execution.

This ledger is intentionally lighter than the old gate-heavy process. A topic should not be killed merely because it lacks a deep mechanism, a dramatic anomaly, or an Outstanding-Paper-scale contribution. Hard reasons to reject are mainly: the exact question is already answered, the nearest-prior difference is too small, the question is not naturally worth asking, or there is no realistic experimental path.
