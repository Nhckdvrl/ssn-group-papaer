# Data Plan — Incremental Interpretation & Revision

## Principle

**Reuse first; synthesize only to separate explanations.** Garden-path stimuli are calibration data, not the final novelty.

## Sources

| source | files / scale | role | redistribution |
|---|---|---|---|
| Amouyal et al. ACL 2026 release | `extended_gardenpath_experiments.csv` + other difficult-structure CSVs; includes sentence/question/answers/set_id/condition | behavioral positive control + human-aligned task format | follow upstream license; record revision/hash |
| Jurayj et al. BlackboxNLP 2022 | audited revision: 43 NP/Z, 19 NP/S, 28 MV/RR component rows + `make_sents.py` (original plan's 20/20 was inaccurate) | controlled generation of ambiguity, blocker, comma/`that`, unreduced, context/extension variants | Apache-2.0 repo; retain attribution |
| Microsoft Turing Experiments | `Christianson_2001.tsv`, `Alternates_2022.tsv` | independent classical GP replication | keep source provenance; follow repo license |

## Local normalized schema

Do not commit copied upstream data until license/provenance audit is complete. Build a local cache and normalize to:

```text
item_id
source
construction          # NPZ / NPS / MVRR / ...
condition             # gp / non_gp / blocked / explicit_cue / ...
sentence
question_type         # intended / lingering / simple
question
gold
initial_parse_claim
final_parse_claim
ambiguity_start
disambiguator_index
cue_type
extension_length
source_row_id
```

The two crucial labels are:
- `initial_parse_claim`: proposition licensed by the tempting initial interpretation;
- `final_parse_claim`: proposition licensed by the globally correct interpretation.

This lets us measure **residual old-interpretation support and successful new-interpretation support separately**.

## First data build

1. Audit and cache upstream revisions.
2. Reproduce Amouyal GP/non-GP behavior without modifying items.
3. Parse Jurayj component TSVs and generate canonical variants.
4. Unit-test every generated pair:
   - same lexical content except intended manipulation where feasible;
   - gold final interpretation verified;
   - disambiguator position logged;
   - blocker/explicit cue actually removes the intended ambiguity.
5. Hand-audit at least 20 items before any large run.
6. Keep held-out items for any later prompt development.

## What we do NOT build initially

- no 1,000-item synthetic LLM-generated benchmark;
- no human annotation campaign;
- no multilingual expansion;
- no lexical/referential/scope dataset bundle;
- no white-box labels.

Those are conditional on a concrete competing-account question emerging from E00/E01.

## Audit / loader status (2026-10-05)

Pinned revisions, licenses, exact hashes and counts: [D0 audit](results/D0-audit.md), [machine-readable manifest](results/D0-source-audit.json). Local loader: `scripts/data.py`; cache-only normalized data. Missing upstream gold/position stays null. E00 question type is confounded with Yes/No polarity; main readout remains within-set same-question GP/nonGP contrast. Generated Jurayj gold requires a separate pre-inference audit; lexical blocker effects cannot be pooled with same-verb explicit cues.

**2026-10-05 用户修订：** 人明确要求取消agent附加的停步gate，继续系统观察与idea生长；进入E01（不追认E00通过），构造/改造语义标注审计改用Step5，最多8并发。持续论文阅读写入既有 `library/themes/incremental-language-processing/`。先前等待科学分支的请求已被此指令替代，不再据此停步。

## 阅读驱动的额外原始资料：SAP

Huang 2024 / Yoshida 2026共同使用的[公开SAP材料](https://github.com/caplabnyu/sapbenchmark)，固定revision `15e61066d510b5349e17740e6488c976abc3e1ac`、MIT、5文件blob/SHA256及统计见[审计](results/D0-SAP-source-audit.json)。原Excel有72 GP/explicit-cue题对、144句、24共享lexical sets；原问题/答案无需agent构造。Excel与CSV仅有6个目标标记差异，全部保留。原文cache `upstream/sap-discovery/`、共享schema loader `scripts/sap.py`；E09用原题迁移校对E01元语言读数，不更换研究对象。未下载人类participant数据，不伪造人机配对结果。

此前opencode外审的概率探索层保持原协议和null gold，不追改已跑分数。

## 当前独立审计授权（2026-10-05，最新用户修订）

opencode免费模型与Step模型均可用于逐条数据审计；额度、格式或判断分歧无法解决时，可用GPT Luna子agent逐条复核。**不再把Step-only当作审计或研究推进条件。** 选择取决于任务和可用性，保留provider/model、逐ID答案、输入/响应hash、完成状态和不确定项；语义标注不由主执行agent自判。新标签的采用规则在相应推理前写清，既有null-gold实验不追改为能力分数；模型审计不宣称等同人类gold。下载仍全部无代理，API最多8并发。

## 问句之外的自然后文：Slattery2013

[E13](experiments/E13-natural-followup-without-diagnostic-question.md)来自已读原论文AppendixB的24原两句item/96作者四条件变体。[D0](results/D0-Slattery-source-audit.json)记录PDF SHA、copyright、规范化、完整S2一致性与字面reference缺失；不是MIT开放数据，不复制原text/normalized到git。`scripts/slattery.py`与shared schema仅扩作者comma/NP选项，无新增语义gold，source9/10仍保留主读数。PDF双栏running header初次试抽取混入item11，已在任何推理前按y>50pt crop修正；独立逐source外审进行，不能把机械parity当人工语义gold。
