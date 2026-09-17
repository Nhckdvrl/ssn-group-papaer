# Failed Topics — 2026-09-17 Continued Search

**Status:** durable kill ledger. Read together with `FAILED_TOPICS.md` and `FAILED_TOPICS_2026-09-17.md` before generating new topics.

---

## F16 — Can SFT learn new knowledge that appears only in masked prompt/user tokens?

**Question.** In completion-only / assistant-only SFT, user and system tokens are present in the forward pass but contribute zero direct token loss. If genuinely new information appears only on the input side and is never itself an assistant prediction target, can that information nevertheless be incorporated into model parameters through gradients from the response loss? What is the boundary between conditioning on information and actually learning it?

**Why it looked promising.** The question comes directly from the standard conditional-likelihood objective rather than from a reported anomaly. It appears to separate direct token supervision from indirect gradient flow through context and could in principle distinguish memorization, task learning, and knowledge acquisition.

**Nearest prior.** Shi et al., NeurIPS 2024, *Instruction Tuning With Loss Over Instructions*, directly compares conventional output-only instruction tuning with objectives that also assign loss to instruction/prompt tokens and studies when prompt-side loss helps. Separate fine-tuning data-extraction work explicitly tests whether prompt information is memorized under completion-only loss and finds that some prompt information can still leave recoverable parameter traces, although extraction is much weaker than with full-sequence loss.

**Failure reason.** The broad mother question `does prompt-side information matter / get learned when prompt tokens are masked from direct loss, and what changes when prompt-side loss is added?` is already occupied. More importantly, the naive puzzle is partly resolved by the objective itself: masked prompt positions receive no direct prediction loss, but response-token gradients still backpropagate through representations that depend on the prompt. A new controlled factual-learning experiment would sharpen a boundary, but reviewer-level novelty would compress to mechanism/analysis of an existing prompt-loss question.

**Revival condition.** A distinct, naturally important quantity for which input-only knowledge and output-target knowledge make opposing predictions not covered by prompt-loss/memorization work; merely testing more facts, models, or mask ratios is insufficient.

---

## F17 — Does EOS induce a learned document-reset mechanism under causal packing?

**Question.** In standard causal pretraining with unrelated documents packed into one token stream, later-document tokens can attend to all earlier-document tokens. Does the model learn an internal reset / context-isolation computation at EOS so that information from the previous document becomes causally irrelevant, and where is that reset represented?

**Why it looked promising.** The puzzle arises directly from the training setup rather than a reported anomaly: the architecture carries previous context across a boundary even though the data-generating process says that unrelated documents should be conditionally independent. This gives natural competing explanations: learned boundary-triggered suppression, generic anti-mixing mechanisms, or continued cross-document interference. A causal-vs-intra-document masking intervention could in principle test where the ability comes from.

**Nearest prior.** Zhao et al., ACL 2024 Main, *Analysing The Impact of Sequence Composition on Language Model Pre-Training*, directly studies standard causal packing across documents, shows that previous documents act as distracting information, and compares it with intra-document causal masking that prevents cross-document conditioning. Barbero et al. (2025), *Why do LLMs attend to the first token?*, gives a mechanistic account of learned anti-over-mixing behavior via attention sinks and explicitly studies how data packing and BOS/EOS arrangements affect the phenomenon. Modern hybrid/SSM training systems also implement explicit state resets at document boundaries, further making boundary isolation an active architectural/training object rather than an unnoticed gap.

**Failure reason.** The honest reviewer-level parent becomes the intersection of two already occupied questions: `cross-document causal attention causes distraction and can be removed by document masking`, and `LLMs learn attention patterns that reduce information over-mixing, with packing affecting those patterns`. Asking whether EOS specifically implements a reset is a cleaner mechanistic follow-up, not an independently established mother question. It also becomes less generally important as modern training stacks increasingly use explicit document masks/state resets.

**Revival condition.** A boundary-specific causal signature that is not explainable by generic attention sinks/anti-mixing and that matters in a broadly used regime where no hard document isolation is present. Simply probing EOS attention, adding more model sizes, or comparing causal vs block-diagonal masks is insufficient.

---

## F18 — Long-context forgetting: temporal/distance decay versus semantic interference

**Question.** When information becomes harder for an LLM to use as more context arrives, is the loss mainly caused by token distance/position itself or by interference from semantically competing intervening information, analogous to decay-versus-interference theories of human memory?

**Why it looked promising.** This is a classic cognitive-science distinction with clean interventions: hold distance fixed while changing semantic overlap, or hold interfering content fixed while changing distance. Both outcomes would be interpretable and the question does not depend on one reported anomaly.

**Nearest prior.** Liu et al., TACL 2024, *Lost in the Middle*, established strong position/context effects. Wang & Sun (2025), *Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond Context Length*, directly imports proactive-interference paradigms and shows old semantically related associations disrupt newer values. Li et al., ICML 2026, *Understanding Generalization and Forgetting in In-Context Continual Learning*, provides a theoretical bias–variance–interference decomposition for sequential in-context tasks. ICLR 2026 work on in-context forgetting likewise makes selective suppression of interference an explicit object.

**Failure reason.** The parent `long-context failures arise from interference in addition to position/length limitations` is directly occupied both empirically and theoretically. A cleaner factorial decay×interference experiment would refine attribution but would remain a controlled follow-up inside an existing memory/interference literature.

**Revival condition.** A distinct memory-theoretic signature not predicted by proactive/intertask interference or positional effects, with an intervention that changes the qualitative mechanism rather than merely the amount of distraction.

---

## F19 — Does post-training reduce a model's future learnability?

**Question.** As an LLM moves through pretraining, SFT, preference optimization, and RL, does acquiring current capabilities reduce its ability to learn genuinely new capabilities later? This asks about future plasticity, not catastrophic forgetting of existing skills.

**Why it looked promising.** Loss of plasticity is a fundamental phenomenon in continual deep learning. The staged LLM training pipeline creates a natural testbed for asking whether one stage changes the model's later learnability, with possible mechanisms in weight magnitude, representation geometry, gradient conflict, or output-space collapse.

**Nearest prior.** Dohare et al., Nature 2024, establishes loss of plasticity in deep continual learning. Hernandez-Garcia et al. (2026), *Can Scale Save Us From Plasticity Loss in Large Language Models?*, directly demonstrates plasticity loss in GPT-style language models and studies scaling. Han et al. (2026), *Weight Decay Improves Language Model Plasticity*, studies downstream adaptability of pretrained LMs. Most directly, Liu et al. (2026), *When RL Fails after SFT: Rejuvenating Model Plasticity for Robust SFT-to-RL Handoff*, asks whether excessive SFT reduces the ability of the checkpoint to be reshaped by subsequent RL and analyzes the failure as loss of plasticity.

**Failure reason.** The mother question `does earlier LLM training reduce future learnability, including SFT→RL plasticity?` is now directly occupied. Restricting to another post-training stage, model family, or task would be an exact-cell extension rather than a new scientific parent.

**Revival condition.** A future-learnability phenomenon with a qualitatively different causal source and prediction not reducible to plasticity loss, gradient conflict, or SFT→RL handoff; merely measuring plasticity after DPO/RL/another checkpoint is insufficient.
