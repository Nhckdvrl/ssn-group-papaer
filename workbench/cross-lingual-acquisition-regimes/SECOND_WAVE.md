# Second wave: the selected checkpoint is part of the intervention

Exploratory state, 2026-09-30. No registered paper identity, no training.
This supplements, rather than silently replaces, the first-wave observations.

## New evidence

1. Four XCOPA runs repeated in FP32 compute with the same BF16-rounded weights.
   The earlier ID->ZH prior-adjusted evidence interaction is now +3.74 pp
   [-0.83,8.11], not clearly positive. Its continuous margin interaction remains
   +0.449 nats. ZH->ZH calibrated interaction is +6.86 [1.87,11.85], but raw
   accuracy interaction and continuous margin remain inconclusive.
2. Four fixed-format, zero-shot XStoryCloze runs used all 1,511 aligned eval
   stories in four language cells, with original or unrelated story context.
   Raw ID->ID improves +2.51 pp [0.93,4.10], but ZH->ZH -0.33 [-1.99,1.26].
   Prior-adjusted original-context ZH accuracy is unchanged at 54.40%, while
   its evidence interaction is +5.29 pp [2.18,8.34]: the paired model performs
   worse on unrelated contexts. This is **not equivalent to improving useful
   reasoning**. The ID->ZH continuous-margin signal from XCOPA does not clearly
   replicate here (+0.133 nats, interval crosses zero). These are uncorrected,
   single-seed exploratory results, not confirmation tests.
3. Independent LM diagnostics: 128 native Wikipedia excerpts and 360 disjoint
   XStoryCloze train contexts per language, four JGP models. Native Wiki loss:

| Selected model | ID bits/byte | ZH bits/byte |
|---|---:|---:|
| No-Parallel | 1.876 | 2.693 |
| Multilingual | 1.285 | 1.645 |
| Non-Adjacent | 1.756 | 2.046 |
| Distributed | 1.324 | 1.645 |

   Within-language loss improves with target-text exposure. Non-adjacent is
   markedly worse than ordinary multilingual; correct pairing recovers much of
   that difference. This suggests a missing comparison: **positive benefit over
   independent target text vs recovery from an incoherent pairing control**.
   It does not establish either explanation: selected steps differ, English-side
   content differs for Multilingual, and exact processed target dose needs audit.
   The Wikipedia convenience sample is not proven absent from pretraining; the
   different languages' absolute bits/byte must not be ranked as competence.

Evidence: `results/p1_pairing_evidence_control_fp32.json`,
`results/p1_xstory_pairing_fp32.json`, `results/p1_xstory_evidence_fp32.json`,
`results/p1_lm_exposure.json`, `results/p1_lm_pairing.json`,
`results/p1_lm_shuffled_english.json`.

## A necessary correction to causal interpretation

The primary paper explicitly selects checkpoints by average MT dev BLEU.
The official model card confirms `main` contains the paper-evaluated selected
model, with other steps on branches. Comparing weight-file SHA256 against all
released branches finds:

| Paper-selected main | Equal weight hash on step branch |
|---|---|
| No-Parallel | 110000 |
| Multilingual | 155000 |
| Non-Adjacent | 150000 |
| Distributed | **10000 and 115000** |

The duplicate Distributed aliases prevent identifying its actual training step
from branch labels alone. This is a release/metadata ambiguity, not evidence of
misconduct or a proven training bug. All first/second-wave `main` results are
observations on **paper-selected weights**, not equal-time causal effects.
Hashes and immutable revisions: `results/jgp_checkpoint_audit.json`.

The next available safe experiment is therefore fixed 160K checkpoints for the
same four regimes, with the same corpus, tasks and numerical precision. Download
to the standard HF cache and the LM/XStoryCloze comparisons are now complete.
No outcome-dependent checkpoint choice.
If the contrast disappears, retire it; do not build a paper around a release
ambiguity. If it persists, compare ordinary multilingual, shuffled pairs and
true pairs at the same step before attributing it to acquisition or alignment.

### Fixed nominal-160K results supersede the provisional interpretation

These are the official branches labelled `160000`. Exported weight files do not
contain optimizer-step metadata, so equal-time interpretation assumes those
branch labels are accurate; the earlier alias ambiguity is not ignored.

| Nominal 160K model | Native ID bits/byte | Native ZH bits/byte |
|---|---:|---:|
| No-Parallel | 1.812 | 2.660 |
| Multilingual | 1.347 | 1.966 |
| Non-Adjacent | 1.273 | 1.591 |
| Distributed | 1.263 | 1.593 |

The large Non-Adjacent vs Distributed LM gap **disappears**. ID difference is
-0.0102 bits/byte; ZH +0.0017 [-0.0043,0.0078]. Thus the selected-weight result
cannot justify "shuffled pairing damages language acquisition". Also, ordinary
Multilingual is no longer as good as either bilingual condition on this corpus;
do not carry its earlier ranking forward. Selected-checkpoint sensitivity is a
real observed issue, but its cause (learning dynamics, data order, exported
metadata, or their combination) is not established.

XStoryCloze at nominal 160K, Non-Adjacent -> Distributed:

| Cell | Raw accuracy change pp [exploratory 95% CI] | Prior-adjusted change pp |
|---|---:|---:|
| ID->ID | +2.05 [0.33,3.77] | +1.85 [-0.60,4.30] |
| ID->ZH | -2.18 [-3.97,-0.40] | -0.33 [-3.44,2.78] |
| ZH->ID | -0.73 [-2.58,1.13] | -0.73 [-3.90,2.38] |
| ZH->ZH | +1.39 [-0.20,2.91] | +0.53 [-1.92,2.91] |

Raw cross-minus-mono interaction is -3.18 pp [-4.70,-1.59], but is not clearly
negative with the other readouts. Hence this is **not** established harm to
cross-language reasoning. The direct pure-pairing contrast still lacks a broad
reasoning effect under prior correction, despite essentially equal LM losses.
Distributed vs ordinary Multilingual has a raw ZH gain +2.78 [0.93,4.57], but a
prior-adjusted change -0.73 [-3.11,1.65], with content/target-dose confounds intact.

Machine-readable results use suffix `_160k.json`. The source corpus contains 976
texts, scored under eight model checkpoints in total; the frozen task inventory
now contains 27 runs / 85,516 item-cell scores (including diagnostic controls).

### Source-code audit motivates, but does not prove, a cadence alternative

The released [dataloader](https://github.com/nusnlp/just-go-parallel/blob/main/pretrain/tinyllama.py)
supports **file-level** interleaving. It uses `n_chunks=8`; its training-dataloader
call sets `shuffle=False`. Preprocessing script defaults differ: parallel chunks
`2049*8`, shuffled SlimPajama chunks `2049*1024`. Consequently "distributed"
must not automatically be interpreted as an IID, per-token language mixture.
Actual run commands, file inventories and chunk-size overrides are missing from
this audit, so these defaults cannot establish the parents' realized cadence or
explain the observed checkpoint oscillation. This leaves an identifiable
alternative: recent target exposure / optimization state, rather than cumulative
acquisition alone. Generic curriculum/recency observations are already owned;
only a distinct, reproducible interaction could justify a new paper object.

## Wider ownership checks

- [nmT5, ACL 2021](https://aclanthology.org/2021.acl-short.87/), primary main text
  read: continued pretraining from >1T-token mT5, 100B additional tokens, 10%
  parallel mixing. NMT objectives improve supervised downstream transfer beyond
  extra MLM, while TLM scarcely does. Limited **downstream labels** amplify gains;
  this is not synonymous with limited target-language pretraining exposure.
  Larger-size comparisons also use original mT5 baselines, so do not interpret
  their headline deltas as fully compute-matched objective effects.
- [Beyond the Rosetta Stone](https://arxiv.org/html/2508.11017v2), primary HTML
  main methods/results read; PDF fetch failed 406. Controlled facts are
  re-expressed in separate samples, not concatenated pairs. It already studies
  training phases, language-label priors and token overlap, plus unification as
  a transfer/checkpoint proxy. Generic "alignment phase" or "language priors
  hinder transfer" is therefore not an unowned idea. Its learned factual recall
  differs from use of inference-time supplied evidence; testing that difference
  would still need a concrete mechanism and independent behavioral validation.
- Macaroni explicitly controls incoherent word-level code switching and studies
  coherence-dependent alignment. "False bridges are bad" alone is also owned.

## Research decisions

Do not elevate the calibration-dependent branch. Cross-task replication has not
established a selective cross-language reasoning benefit. Independent loss
diagnostics revealed a larger design uncertainty, so resolve that uncertainty
before extending a local score effect.

Three field-scale branches remain distinct: acquisition/scaffolding; restoration
from harmful coupling; useful conditioning vs sensitivity to irrelevant evidence.
Their decisive comparisons are different. None earns a candidate from this wave.
P2 weak-language/generation stress and P3 independent-family replication remain
unfinished. P4 remains closed.
