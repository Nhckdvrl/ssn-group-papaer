# 2026-09-15 — UID Estimator-Bias Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS.

## Question

> When real word orders look more information-efficient than counterfactual ones under neural language models, is that a property of the languages, or partly a consequence of the learner being better matched to real language?

**Final verdict:** `ARCHIVED / NO-GO — MOTHER-PHENOMENON / DECISIVENESS FAILURE`. No L-series. No pilot.

## Why the pressure is real

Clark et al. (TACL 2023), *A Cross-Linguistic Pressure for Uniform Information Density in Word Order*, estimate UID with Transformer LMs trained separately on real and counterfactual word-order corpora. The paper explicitly notes that modern LM architectures/hyperparameters were selected on real language and may therefore contain inductive biases favoring real word orders. It also explains that prior real-vs-counterfactual mean-surprisal differences can arise from the learning algorithm rather than the true language distributions.

The statistical decomposition makes the issue explicit. For true language distribution `p` and learned estimator `q`, measured cross-entropy is

`H(p,q) = H(p) + KL(p || q)`.

Thus a real/counterfactual contrast in LM-based information quantities can in principle contain both a property of the target distribution and a learner-dependent approximation term.

Xu et al. (TACL 2026), *Can Language Models Learn Typologically Implausible Languages?*, independently strengthens the concern: across carefully controlled English/Japanese counterfactual word-order languages, real / typologically plausible systems are often learned faster or better by GPT-style LMs. The approximation term is therefore not obviously symmetric across real and counterfactual languages.

## Why this is not currently a paper

The crucial missing mother phenomenon is **not** `LMs have a bias toward natural word order`; that now has substantial evidence. The paper would need a stronger fact:

> learner approximation bias materially changes, reverses, or otherwise invalidates the functional UID conclusion on the same scientific quantity.

That fact is not currently established.

Without it, the obvious experiment is to train several estimator families / scales on the existing real and counterfactual corpora and ask whether UID rankings are robust. This has two bad outcome shapes:

1. **Rankings remain stable:** useful robustness evidence, but little new language-science understanding.
2. **Rankings reverse:** suddenly a strong story, but the project's importance depended on discovering the reversal.

That is a classic `DECISIVENESS_FAILURE`: only the surprising positive outcome creates the Main-level paper.

Trying to rescue the route by introducing a corrected/extrapolated UID estimator would make the method create the question and push the project toward measurement/evaluator work, which is a current negative search prior.

## Strongest reviewer compression

> TACL 2023 already states that Transformer inductive bias can favor real word orders + TACL 2026 shows real/plausible word orders are often easier for LMs to learn -> re-run UID with more learner families / scales.

The combination creates a serious methodological warning, but no non-obvious scientific answer yet.

## Main-level calibration

This falls below recent strong-paper moves such as:

- ACL 2026 local attention: an established broken expectation plus formal explanation;
- ICML 2026 Flexibility Trap: a celebrated capability creates a robust, independently meaningful failure mode;
- NeurIPS 2025 RLVR: score improvement is separated from expansion of capability support;
- EMNLP 2025 Generative-or-Discriminative: a classical law is re-tested in a regime where its assumptions no longer hold, yielding a conditional law rather than a robustness check.

The present UID route has an important possible confound, but no established contradiction whose resolution would change the theory.

## Reopen only if

Reconsider only if independent evidence supplies at least one of:

1. a natural real-vs-counterfactual UID conclusion that **already disagrees across independently motivated learner classes**;
2. a theorem/bound showing the UID ordering is identifiable despite learner approximation under surprisingly weak conditions, or systematically non-identifiable under conditions used in the literature;
3. an existing unexplained cross-linguistic pattern whose explanation changes specifically when learner-bias and language-efficiency terms are separated.

Do not reopen merely with more estimators, larger models, more languages, or a new correction metric.

## Searcher lesson

> A later paper that makes an old paper's stated confound more plausible does not automatically create a new project. The confound must already bear on the load-bearing scientific conclusion, or there must be a non-obvious identifying result that can decide whether it does.
