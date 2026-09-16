# ssn-taste

This directory is the working ledger for the Sasano-taste-driven NLP/LLM research-question search started on 2026-09-16.

## Venue hierarchy for research taste

The search targets **ACL / EMNLP / NAACL Main**. These three venues are the primary external calibration for what counts as a strong, appropriately scoped NLP/LLM research question.

**TACL / ICLR / ICML / NeurIPS** may be used as secondary calibration when they illuminate scientific-question quality, causal/mechanistic reasoning, representation analysis, post-training, or adjacent methodology.

**EACL / AACL are NOT taste-calibration venues for this search.** They may be searched aggressively for novelty checking, nearest-prior discovery, and duplicate detection, but their topic/style distribution must not be used to decide what we should pursue. In other words: an EACL/AACL paper can kill or narrow an idea because it already answered the question, but it cannot make an idea attractive merely because it resembles accepted EACL/AACL work.

The governing rule is advisor fit first: questions should be easy to understand, genuinely unanswered, clearly differentiated from nearest prior work, and testable with clean experiments whose claims do not exceed the evidence. At every search and filtering step, explicitly check both **Sasano taste** and **ACL/EMNLP/NAACL Main taste** rather than drifting toward generic LLM trends.

## Scope calibration is empirical, not subjective

Do **not** decide that a question should be “broader” or “narrower” by intuition alone. Every serious candidate must be calibrated against the actual scope of nearby **ACL / EMNLP / NAACL Main** papers and against Sasano's demonstrated project taste.

For each candidate, separately calibrate three levels:

1. **Parent scientific question.** What is the durable thing the paper is actually trying to learn about language/models/learning/interaction? It should normally be broader than one implementation toggle, one benchmark cell, one model quirk, or one API field, but it must not balloon into an entire area such as “how agents reason” or “what post-training changes.”
2. **Claim/contribution scope.** The paper may answer only a controlled slice of the parent question. Claims must stay at the width supported by the experiment; do not inflate a clean local result into a universal theory.
3. **Related-work neighborhood.** Related work must cover the scientific lineage a Main-conference reviewer would naturally use to compress the contribution: the nearest direct owners, neighboring explanations/measurements, and the parent problem. It must not be artificially narrow (“no one tested this exact flag”) or indiscriminately broad (“all tool-use papers”).

### Required width audit

Before promotion to a serious candidate, identify several nearby **ACL / EMNLP / NAACL Main** papers and ask:

- How wide is their Introduction-level question, not just their experiment?
- What scientific object do their Related Work sections treat as the relevant neighborhood?
- Would a reviewer summarize our idea as merely “one more condition / parameter / dataset / model inside X”? If yes, the parent is probably too narrow or already owned.
- Conversely, does the proposed parent require several weakly connected subquestions or a universal claim that the minimal experiments cannot support? If yes, it is too broad.
- Can the novelty sentence be stated at roughly the same abstraction level as the nearest Main papers, rather than one level below them?

This is a **calibration exercise, not a new kill gate**. A narrow experimental manipulation is perfectly acceptable when it identifies a Main-sized scientific question; a broad topic is not automatically better. The target is the width actually used by strong ACL/EMNLP/NAACL Main work and by Sasano-approved projects.

### Sasano width anchors

Use Sasano's demonstrated examples as additional calibration:

- **Sato:** one clear parent question (where character-level knowledge comes from) with several controlled source hypotheses. The project is wider than one tokenizer ablation but much narrower than “how LLMs learn linguistic knowledge.”
- **Utami:** one changed real-world premise and one interpretable linguistic consequence, not “LLMs changed language” in general.
- **Kisako:** one coherent compression/representation trade-off studied systematically, not “efficient NLP” broadly and not one isolated bit-width anomaly.
- **Oshika:** one missing intermediate operation in a larger workflow can be Main-sized when that operation is independently necessary and underexplored; the contribution is not required to cover the entire workflow.
- **Guo negative example:** a familiar parent cannot be rescued merely by shrinking to an exact newer-model cell when the nearest-prior difference remains small.

Therefore: **do not optimize for broadness; optimize for the correct scientific abstraction level.**

User-specific practical preferences are also applied: avoid benchmark-centric work, avoid topics that require unusually difficult data construction, and avoid heavily linguistic topics unless the semantics/phenomenon is simple and easy to explain.

Files:

- `FAILED_TOPICS.md`: ideas that were seriously considered and then dropped, with the concrete novelty/fit/feasibility reason. Do not revive these without new evidence that directly resolves the recorded failure reason.
- `SELECTED_TOPICS.md`: ideas that survive novelty, scope, and Sasano-taste checks and are worth concrete pilot design or execution.

This ledger is intentionally lighter than the old gate-heavy process. A topic should not be killed merely because it lacks a deep mechanism, a dramatic anomaly, or an Outstanding-Paper-scale contribution. Hard reasons to reject are mainly: the exact question is already answered, the nearest-prior difference is too small, the question is not naturally worth asking, its scientific abstraction level is badly mismatched to Main-conference/Sasano precedent, or there is no realistic experimental path.
