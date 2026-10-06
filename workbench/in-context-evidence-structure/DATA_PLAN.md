
# DATA_PLAN — In-Context Evidence Structure

> **2026-10-06 实际使用的数据（以此为准；下文为 10-05 的初始方案）**
> - **自然、公认数据集（直接使用，不送审）：** SetFit/sst5（两极）、fancyzhx/ag_news（K=4）、CogComp/trec 粗粒度（K=6，parquet 修订版）、Yelp/yelp_review_full（1/5 星，E35）、Todd et al. function-vector 任务（`data/fv_tasks/`，E19）。
> - **程序化数据（无需审计）：** 两位数大小/奇偶、±k 算术、类别条件算术、字母后继、大小写↔反转、标签流。
> - **构造的 nonce 词（逐条审计）：** StepFun step-5（Step Plan 接口）审计的标签词 84 个、属性名 26 个（`data/lexicon.json`、`data/lexicon_step5_verdicts.json`）；用于 E00–E02a 与 E31–E33、E32 的 nonce 标签。
> - **未用于结论：** DICES-350（`data/dices/`，评分者间 kappa 中位 0.19，噪声过大）。
> - 所有 `data/*/rows.jsonl` 由 `scripts/build_*.py` 以固定种子重建，不进 git。

## 0. Principle
**Build exact-gold procedural episodes first.** Public ICL datasets are calibration sources, not the core dataset.

The central variable is the **statistical relation among demonstrations**, so uncontrolled NLP benchmarks are a bad starting point.

## 1. Primary generator: nonce attribute-rule streams

### Input space
Each item has three binary attributes with freshly sampled nonce attribute names per episode.

### Output space
Two nonce labels, with label polarity randomized per episode.

### Hidden rule class H
Start with six hypotheses:
- label tracks attribute 1 / 2 / 3;
- each with either polarity.

This intentionally small hypothesis class gives:
- exact posterior enumeration;
- held-out combinations;
- low reasoning burden;
- easy scaling to conjunction/parity later if E00 saturates.

### Episode
A context is a stream of input-output demonstrations followed by one held-out query.

No natural semantic prior identifies the episode rule.

## 2. Generative structures

### STABLE
One h in H throughout the episode.
Optional independent label flip with probability epsilon.

### CHANGE
h_old until change point tau, then h_new.
Query uses h_new/current rule.

### CORRELATED
One rule, but input/examples are repeated or Markov-correlated.
Used only after E02.

### NOISE-vs-CHANGE matched family
Main E02 substrate.

Generate pairs with:
- same T;
- same nonce dictionary;
- matched input frequencies;
- matched number of demonstrations inconsistent with the initial best rule;
- matched label counts where rejection sampling permits.

Difference:
- NOISE: contradictions are isolated/dispersed under one stable rule + independent corruption;
- CHANGE: contradictions become persistent after a latent change point.

## 3. Exact oracle annotations

For every episode save:
- episode_id, seed;
- attribute_dictionary, label_dictionary;
- inputs, labels, query_input, query_gold;
- source_regime;
- h_true_initial, h_true_current;
- change_point, noise_positions;
- P(regime=stable | D), P(regime=change | D);
- P(query | set oracle), P(query | sequence oracle), P(query | meta oracle);
- log Bayes factor change vs stable.

Posterior is obtained by exact enumeration over finite H, possible change points, and the declared noise model.

This makes the main scientific readout independent of an LLM-as-judge.

## 4. Splits / anti-overfitting

Freeze three manifests:
- pilot_seeds.json: instrumentation/debug episodes;
- confirm_seeds.json: untouched confirmatory episodes;
- dictionary_seeds.json: nonce-renaming bank.

Do not look at confirmatory results while changing prompt wording or parser.

## 5. External calibration datasets

### Jiao et al. 2026 — Operator Induction / Fake Word Induction
Repo:
https://github.com/difanj0713/Understanding-ICL-Demo-Conflict

Use:
- verify a known single-conflict effect;
- optionally reproduce E02 structure on an independent task after our procedural result exists.

Do not copy their mechanistic claim.

### formaLLM — formal language generators
Repo:
https://github.com/bishwamittra/formaLLM

Use:
- DFA/PFSA/PCFG/PCSG as second-family generalization only after E02;
- not required for initial residency.

### Sequential correlations reference
Repo:
https://github.com/Pehlevan-Group/sequential-correlations-in-context-regression

Use:
- compare correlated-context qualitative predictions;
- not a production-LLM benchmark.

## 6. Do not do initially

- no MMLU/GSM8K/BBH;
- no LLM-generated benchmark;
- no human annotation;
- no natural-language topic labels with pretrained semantics;
- no multilingual expansion;
- no mechanism/probe labels;
- no large model sweep before the task passes E00.

## 7. First-scale budget

E00:
- roughly 300–1,000 procedural episodes;
- 0-shot + 4/6/8-shot conditions;
- 3–5 nonce dictionaries;
- one model.

E01/E02:
- hundreds of paired episodes per cell are cheap;
- bootstrap over episode seeds;
- exact paired designs preferred over adding model families.

Only after a stable E02 effect:
- second open model family;
- independent substrate;
- white-box analysis if needed.
