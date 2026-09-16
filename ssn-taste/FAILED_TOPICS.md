# Failed Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: keep a durable record of questions that were seriously considered but rejected, so later search rounds do not accidentally repackage and revive them.

## Logging rule

For every rejected topic, record:

1. **Question** — the scientific question in plain language.
2. **Why it initially looked promising** — the evidence or research pressure that made it worth checking.
3. **Nearest prior work** — the papers most directly overlapping the question.
4. **Failure reason** — especially whether the nearest-prior difference is too small, the question is already answered, the framing is benchmark-centric, the required data is impractical, or the experiment cannot cleanly answer the question.
5. **What would be required to revive it** — only concrete new evidence can reopen a topic.

Do **not** reject a topic merely because the answer is uncertain, the first hypothesis may be false, the method is simple, or the work is not mechanism-heavy.

---

## Current-round failures

### F01 — Is post-training uncertainty lost, or merely unreadable?

**Question.** After instruction/alignment/reasoning post-training makes an LLM overconfident, is uncertainty information actually erased from the model, or does it remain internally represented but fail to reach the model's explicit confidence/readout?

**Why it initially looked promising.** This has a very Sasano-compatible structure: a clear empirical paradox (post-trained models become overconfident) followed by source/readout separation. It is easy to explain, requires no difficult dataset construction, and could in principle be tested with base-vs-post-trained checkpoints, probes, and controlled interventions.

**Nearest prior work.**
- Miao & Ungar (2026), *Closing the Confidence-Faithfulness Gap in Large Language Models* (arXiv:2603.25052): explicitly shows that internal accuracy/calibration and verbalized confidence are separable/roughly orthogonal signals, describes the problem as a readout failure, and uses activation probing/steering.
- Tan et al. (ACL 2026), *BaseCal: Unsupervised Confidence Calibration via Base Model Signals*: shows base models can retain better calibration than their post-trained counterparts and learns a projection from post-trained hidden states back into the base-model representation space to recover calibrated confidence.
- Slobodkin et al. (EMNLP 2023), *The Curious Case of Hallucinatory (Un)answerability*: already shows that hidden states can encode answerability even when the model produces overconfident hallucinations.

**Failure reason.** The central distinction — uncertainty/correctness information remaining internally available while the surface confidence/readout is wrong — is already directly demonstrated. Re-running it on newer reasoning models or another alignment recipe would be exactly the kind of “old question + newer models” novelty that Sasano has warned against. The remaining space would need a substantially different causal question, not a new model family or benchmark.

**What would be required to revive it.** Only a genuinely different premise that makes existing explanations diverge, e.g. a specific post-training operation predicted to destroy the latent signal rather than merely alter readout, with evidence that existing work did not test that distinction. Otherwise do not revive.
