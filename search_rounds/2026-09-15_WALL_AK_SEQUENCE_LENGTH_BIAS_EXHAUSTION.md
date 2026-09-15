# WALL-AK — Sequence length bias / EOS / decoding

Date: 2026-09-15
Status: EXHAUSTED

## Mother question
Why do maximum-likelihood locally normalized sequence models often prefer outputs that are too short, especially as search improves? Is brevity caused by search, EOS miscalibration, local normalization, or the mismatch between sequence probability and sequence utility?

## Direct-owner lineage
This is a mature NMT/decision-theory program rather than an open modern-LM question.

- Murray & Chiang (WMT 2018), *Correcting Length Bias in Neural Machine Translation*, directly links the brevity problem and beam-search degradation and analyzes the role of local normalization/label bias and EOS, showing that correcting brevity largely removes the beam problem.
- Yang, Huang & Ma (EMNLP 2018), *Breaking the Beam Search Curse*, systematically analyzes rescoring and stopping criteria and explains the wider-beam degradation.
- Later empirical work separates search errors from model errors and continues to find that higher sequence probability need not correspond to better translations.
- Minimum Bayes Risk decoding provides the mature decision-theoretic account: MAP/model probability and downstream utility are distinct objects.

## Verdict
No new L-series. Modern-chat/reasoning length phenomena would need an independently inherited theory that predicts a new quantity, not a re-run of the NMT brevity/beam-search program.

## Anti-resurrection
No:
- EOS-probability diagnostics on chat LMs;
- beam width / length normalization studies;
- reasoning-length bias without a distinct theory;
- 'higher probability prefers shorter outputs' as novelty;
- model probability versus quality framed as new (covered by MBR/AC).
