# ssn-taste

This directory is the working ledger for the Sasano-taste-driven NLP/LLM research-question search started on 2026-09-16.

## Venue hierarchy for research taste

The search targets **ACL / EMNLP / NAACL Main**. These three venues are the primary external calibration for what counts as a strong, appropriately scoped NLP/LLM research question.

**TACL / ICLR / ICML / NeurIPS** may be used as secondary calibration when they illuminate scientific-question quality, causal/mechanistic reasoning, representation analysis, or adjacent methodology.

**EACL / AACL are NOT taste-calibration venues for this search.** They may be searched aggressively for novelty checking, nearest-prior discovery, and duplicate detection, but their topic/style distribution must not be used to decide what we should pursue. In other words: an EACL/AACL paper can kill or narrow an idea because it already answered the question, but it cannot make an idea attractive merely because it resembles accepted EACL/AACL work.

The governing rule is advisor fit first: questions should be easy to understand, genuinely unanswered, clearly differentiated from nearest prior work, and testable with clean experiments whose claims do not exceed the evidence. At every search and filtering step, explicitly check both **Sasano taste** and **ACL/EMNLP/NAACL Main taste** rather than drifting toward generic LLM trends.

## Topic-domain preference: do not chase hype

Sasano fit is not equivalent to working on the newest fashionable paradigm. The search must **not default to currently hot areas such as RL-for-reasoning, generic LLM agents, tool-use agents, multi-agent systems, or other trend-driven topics merely because the literature is active**.

These areas may be used for novelty checking or may occasionally contain a valid independent question, but they are **not preferred search pools** and must not dominate idea generation.

Prefer durable NLP/LLM scientific objects whose importance does not depend on current hype, including:

- language understanding and model knowledge;
- simple, interpretable semantics/pragmatics rather than highly technical linguistics;
- representation and readout questions;
- evaluation and measurement validity;
- generation behavior and communication;
- embeddings, compression, representation efficiency, and systematic trade-offs;
- multilingual or language-variation questions when the scientific distinction is genuinely new rather than another benchmark comparison;
- real-world language change caused by technology or social practice;
- missing independent decisions in established NLP workflows;
- older scientific questions that modern models make newly identifiable under a genuinely changed premise.

The test is: **would this still be an interesting NLP research question if the current hype cycle disappeared?** If the answer is no, deprioritize it.

This preference comes from the demonstrated Sasano examples: Sato, Utami, Kisako, Oshika, Yano, and related projects are driven by understandable scientific or workflow questions rather than by chasing the latest paradigm.

## Idea provenance: do not mine paper edges by default

The default idea generator must **not** be:

> a recent Main paper reports an interesting phenomenon -> it did not fully explain why / mechanism / boundary conditions -> we study that missing piece.

This route has repeatedly produced reviewer-compressible successor work. Once a strong mother phenomenon is visible, its obvious mechanisms and boundary conditions are usually already occupied by the same paper, parallel work, or immediate successors. A `future work` sentence is therefore weak evidence of a new research parent.

Before treating a seed as an independent question, apply the **remove-the-trigger-paper test**:

> If the specific recent paper that inspired this seed disappeared, would the scientific question still arise naturally from an independent problem, changed premise, theory, workflow defect, or real-world need?

If not, treat the seed as a likely follow-up and do not promote it merely because an exact experiment has not yet been run.

Preferred idea provenance is:

1. **Changed premise / changed regime.** A load-bearing assumption behind an older conclusion has genuinely changed, so the old question is no longer the same question. This is stronger than `old question + newer model`.
2. **Independent defect in an existing method or formulation.** Similar prior work is allowed when a concrete, scientifically meaningful defect or limitation can be identified and corrected. This follows Sasano's explicit guidance that fundamental novelty is preferable, but an existing method with a real improvement point can still form a research topic if the prior is understood thoroughly.
3. **Cross-lineage collision creating a new quantity.** Two mature literatures make different implicit assumptions about the same object, and their intersection creates a question owned by neither lineage. `Paper A + Paper B` alone is insufficient; the intersection must expose a new scientific variable or prediction.
4. **Exogenous real-world change.** Technology or practice changes the population/process being observed, making a previously stable measurement or behavior scientifically different (Utami-style).
5. **Hidden oracle / missing independent decision.** A mature workflow has two developed sides but still assumes a necessary intermediate structure or decision is given by humans/gold data (Oshika-style).
6. **New identifying operation for an old scientific debate.** Modern models make a previously confounded distinction experimentally identifiable in a way that changes what evidence can decide the debate. Merely re-running a classic psycholinguistic paradigm on an LLM is not enough.
7. **Clean systematic trade-off with an independent quantity.** Two ordinary system/representation choices interact around a coherent scientific quantity (Kisako-style). Do not manufacture this by attaching an arbitrary downstream property to compression/quantization.

### Successor work is not categorically forbidden

Do not overcorrect and kill every idea with related predecessors. Sasano explicitly noted that high fundamental novelty is preferable, but similar work can still support a research topic when the prior method has a **specific point that genuinely needs improvement**. The crucial distinction is:

- **Weak successor:** `they found X; we explain more of X / add one boundary / use a newer model / use a cleaner ablation`.
- **Potentially valid successor:** `the existing formulation/method makes a load-bearing assumption or has a structural deficiency; fixing it changes the scientific object, inference, or usable capability in a way reviewers can understand independently of the predecessor's future-work list`.

Novelty checking must therefore ask **what prior work owns**, **what it assumes**, and **what exactly is defective**, not mechanically reject anything adjacent.

## Scope calibration is empirical, not subjective

Do **not** decide that a question should be “broader” or “narrower” by intuition alone. Every serious candidate must be calibrated against the actual scope of nearby **ACL / EMNLP / NAACL Main** papers and against Sasano's demonstrated project taste.

For each candidate, separately calibrate three levels:

1. **Parent scientific question.** What is the durable thing the paper is actually trying to learn about language/models/learning/interaction? It should normally be broader than one implementation toggle, one benchmark cell, one model quirk, or one API field, but it must not balloon into an entire area such as “how models understand language.”
2. **Claim/contribution scope.** The paper may answer only a controlled slice of the parent question. Claims must stay at the width supported by the experiment; do not inflate a clean local result into a universal theory.
3. **Related-work neighborhood.** Related work must cover the scientific lineage a Main-conference reviewer would naturally use to compress the contribution: the nearest direct owners, neighboring explanations/measurements, and the parent problem. It must not be artificially narrow (“no one tested this exact flag”) or indiscriminately broad.

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

This ledger is intentionally lighter than the old gate-heavy process. A topic should not be killed merely because it lacks a deep mechanism, a dramatic anomaly, or an Outstanding-Paper-scale contribution. Hard reasons to reject are mainly: the exact question is already answered, the nearest-prior difference is too small, the question is not naturally worth asking, its scientific abstraction level is badly mismatched to Main-conference/Sasano precedent, it is mainly hype-driven rather than scientifically durable, or there is no realistic experimental path.
