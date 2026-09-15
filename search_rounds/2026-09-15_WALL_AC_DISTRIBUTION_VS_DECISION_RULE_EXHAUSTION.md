# WALL-AC — Predictive distribution vs decoding / decision rule

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
A generative model learns a predictive distribution, but deployment must map that distribution to one output/action. How much apparent 'capability' belongs to the learned distribution versus the decision rule used to decode it?

## Direct-owner audit
This is precisely the classical statistical decision-theory framing behind Minimum Bayes Risk (MBR) decoding.

- TACL 2022 explicitly challenges the assumption that highest model probability corresponds to highest human quality.
- EMNLP 2022 and subsequent work analyze sample-based MBR versus mode/MAP decoding and beam-search pathologies.
- ICML 2024 develops model-based MBR using model probabilities directly.
- NAACL 2024 studies how closely MBR samples approximate the true reference distribution.
- ICLR 2025 incorporates model uncertainty into MBR and abstention.
- 2025 theory gives explicit convergence guarantees and MAP-vs-MBR gaps.

Thus the distribution/action distinction is not an unowned scientific gap; it is the organizing principle of a mature decoding program.

## Verdict
No L-series. Applying the same distinction to another benchmark or reasoning setting is setting transfer, not a new scientific question.

## Anti-resurrection
No:
- greedy vs sampling vs MBR capability decomposition;
- 'the model knows it but decoding hides it' without a new theoretical quantity;
- MAP-vs-utility mismatch on reasoning benchmarks;
- another decoder comparison framed as scientific mechanism.
