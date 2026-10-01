# Eighth Wave: Translation Intervention Positive Control

Status: diagnostic reproduction, not novelty. No training. Previous turn changed primary-source ownership constraints and cached the mechanistic prior.

## Before Scoring

Official MONOWEB EN-DE FWB/MWB/MWB+P, nominal 34K, already cached immutable checkpoints. Pin WMT16 `wmt/wmt16` revision `41d8a4013aa1489f28fea60ec0932af246086482`, de-en test and validation Parquet files, standard HF cache. First 200 test examples in both directions, a convenience pilot with news-topic clusters, not the complete test benchmark. Five validation examples sampled once with Python Random(1234), same IDs for all conditions/directions. Exclude literal source overlap with demonstrations; do not select by model performance.

Reference harness revision `d6de81643928d653435c431bae19945d41d32520`: translation/wmt16_en-de.yaml, reverse direction, wmt_common_yaml and utils.py. Prompts `English phrase: {text}\nGerman phrase:` and reverse, demonstrations joined by two newlines. Inspect and cache exact upstream files. Paper Section 4.3 reports five-shot harness, but does not specify its commit or demonstration IDs. Hence this is a qualitative intended-effect check, not exact reproduction.

Native FP32 loading/computation, greedy generation, newline/EOS stopping, max 256 new tokens. Batch eight with left padding; no input truncation. Exclude oversized items jointly before comparing models. Keep raw decoded output, token IDs, stop/cap diagnostics, exact source-copy flags and all prompts. Source-copy is only a conservative language-failure diagnostic, not an estimated on-target-language rate. Inspect a fixed small raw-output sample without claiming representative language annotation.

SacreBLEU 2.5.1 case-sensitive BLEU/13a and chrF/chrF++ signatures retained. Report both directions and absolute scores. No prompt tuning. If MWB loses translation and MWB+P restores it, the intervention is behaviorally active; this does not imply a new mechanism. If not, resolve evaluation/checkpoint validity first. Do not infer broad reasoning from these metrics. P4 stays closed.

## Additional Direct Prior

Leino and Tiedemann, *On the limited utility of parallel data for learning shared multilingual representations*, arXiv v1, Sections 3-6 and Appendices A-F read. Four scratch 1.4B EN/FI models, 200B tokens, 0/1/2/5% parallel, fixed language mix and domain baseline. Pair formats and packing differ from MONOWEB. They examine PWCCA, neurons and language steering throughout training; early sharing acceleration and weak final-dose effects are already owned. Steering coherence does not establish precise factual fidelity. Cosine similarity has anisotropy/shared-token caveats. The method is not a semantic-content-matched factorial isolating every coupling effect. Generic dose, early alignment and language-control narratives are not new. Public repository contains evaluation code; weights were not located in its README. No assumption of their availability.

Primary: https://arxiv.org/html/2603.29026v1

PDF SHA256: `db293950a24fe4ace06eff51d630aaf46c403fbd228ea1ab10c6b991176cfbe5`.

## Execution Audit

Initial three launches failed before loading because the final-model manifest names omit the step suffix. Fixed only this path; manifests explicitly point to `iter_0034000/hf_model`. No scored outputs were produced by the failed launches. No change to prompts, data, decoding or selection.

## Completed Positive Control

All three runs completed, 400 outputs each, with identical audited input hashes and no context exclusions. No empty output. BLEU/13a and chrF below; chrF++ and complete signatures are in `results/p2_translation_control_34k.json`.

| Direction | FWB BLEU / chrF | MWB BLEU / chrF | MWB+P BLEU / chrF |
| --- | --- | --- | --- |
| en->de | 24.16 / 48.52 | 11.47 / 32.72 | 21.36 / 46.11 |
| de->en | 28.90 / 53.34 | 20.11 / 44.52 | 26.01 / 49.24 |

Exact-source copies, out of 200 per direction: en->de 1 / 27 / 2; de->en 0 / 17 / 1. Token-cap hits: only FWB de->en has two, all other cells zero. Copies are not a complete language-failure classifier. Results support the qualitative intended effect in BOTH directions, not exact reproduction of the paper's magnitude.

The fixed sample IDs 0/50/100/150/199 were manually read in both directions for every model. Even FWB and MWB+P sometimes omit, invert or invent information while producing target-language text. For example, several outputs invent locations for the headline at ID 0; ID 150's preference polarity is lost in some models. This motivates checking semantic fidelity separately from surface quality, but the small sample does not establish differential error rates. The existing literature owns translation-vs-understanding separation, output-language failures, generic circuits and coarse representation sharing. These examples alone are NOT a novel finding.

## Decision

The existing MONOWEB training intervention is active locally; its downstream stress tests are not comparisons of intervention-inert checkpoints. Keep the original acquisition-regime explanation downweighted. Do not mistake the restored BLEU or source-copy reduction for new science. A next experiment must distinguish a specific remaining causal mechanism, use meaningful absolute competence gates and challenge a prior's conclusion; another metric sweep or hand-tuned template is insufficient. P4 remains closed, no candidate registered, no training started.

Inventory: 52 complete inference runs, 186,336 item-cell rows, including corrupted-context and diagnostic formats, NOT independent questions. This wave adds three runs and 1,200 generations. All three GPU workers exited successfully; analysis and inventory checks completed. New scripts compile; tracked diff whitespace check passed.
