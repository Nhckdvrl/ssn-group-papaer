# Failed Topics — 2026-09-17 Continued Search

**Status:** durable kill ledger. Read together with `FAILED_TOPICS.md` and `FAILED_TOPICS_2026-09-17.md` before generating new topics.

---

## F16 — Can SFT learn new knowledge that appears only in masked prompt/user tokens?

**Question.** In completion-only / assistant-only SFT, user and system tokens are present in the forward pass but contribute zero direct token loss. If genuinely new information appears only on the input side and is never itself an assistant prediction target, can that information nevertheless be incorporated into model parameters through gradients from the response loss? What is the boundary between conditioning on information and actually learning it?

**Why it looked promising.** The question comes directly from the standard conditional-likelihood objective rather than from a reported anomaly. It appears to separate direct token supervision from indirect gradient flow through context and could in principle distinguish memorization, task learning, and knowledge acquisition.

**Nearest prior.** Shi et al., NeurIPS 2024, *Instruction Tuning With Loss Over Instructions*, directly compares conventional output-only instruction tuning with objectives that also assign loss to instruction/prompt tokens and studies when prompt-side loss helps. Separate fine-tuning data-extraction work explicitly tests whether prompt information is memorized under completion-only loss and finds that some prompt information can still leave recoverable parameter traces, although extraction is much weaker than with full-sequence loss.

**Failure reason.** The broad mother question `does prompt-side information matter / get learned when prompt tokens are masked from direct loss, and what changes when prompt-side loss is added?` is already occupied. More importantly, the naive puzzle is partly resolved by the objective itself: masked prompt positions receive no direct prediction loss, but response-token gradients still backpropagate through representations that depend on the prompt. A new controlled factual-learning experiment would sharpen a boundary, but reviewer-level novelty would compress to mechanism/analysis of an existing prompt-loss question.

**Revival condition.** A distinct, naturally important quantity for which input-only knowledge and output-target knowledge make opposing predictions not covered by prompt-loss/memorization work; merely testing more facts, models, or mask ratios is insufficient.
