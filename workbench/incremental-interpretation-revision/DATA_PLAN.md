# Data Plan — Incremental Interpretation & Revision

> **2026-10-06 新路线：** 数据来源、配对规则、统一 schema、真实错误条目的定义、规模对齐与 Step5 标注协议见 [EXECUTION_BRIEF](EXECUTION_BRIEF.md) §4。以下内容是旧路线的来源审计与许可记录（仍然有效，可复用）。

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

## 独立Ceháková/Chromý2025材料（E24 preparation，尚未推理）

[Zenodo v1 record16358492](https://zenodo.org/records/16358492)原Stimuli.zip10,891 bytes已明确无代理下载，发布MD5及内部三CSV SHA通过；API license CC BY4.0，publisher copyright notice一并保留。384experimental QA/48source（24NPZ/24MVRR），每source8条件，96unique sentences；70filler/3practice。[source audit](results/D0-Cehakova2025-source-audit.json)记录revision/hash/license，原CSV/脚本只cache。correct编码已由127KB PC Ibex archive原脚本核对：as=[yes,no]、hasCorrect=parseInt(correct)，0=Yes/1=No；内部embedded CSV与Stimuli.zip逐字一致；原intransitive self问题不当逻辑gold。独立预测先在24NPZ/12同动词family验证C04，避免把派生版本当独立N；当前只提取/审字段，不事后挑源。

## 语篇身份/指称的自然材料（2026-10-06，仅资产阶段）

GUM pinned commit `22fdf87f9c71c96bcc771461d06e689b1f90020d`，下载所有news24/fiction19个dep文件：43文档、34,683 tokens、1,835 sentences，3,650,638 bytes，无代理，每文件SHA256与Git blob SHA1双验证。[审计](results/D0-GUM-natural-reference-audit.json)。已有coreference/entity/information-status/语法标注可用来核对角色迁移是否只在人工frame出现；不是另开coref研究对象。news文本CC-BY-2.5，fiction文本CC-BY-NC-SA-3.0，全部标注CC-BY-4.0（不能将全体叫单一许可）；原文只cache，尚无event-role semantic gold或模型推断。

GUM完整外审最终v2：174候选均保留，160role/reference clear并非160personpatientgold；仅14有明确pre-event Name+Description（6文档，多同源事件）。18有两种form但部分same-entity不清，原审计/修订全cache保留，[结果](results/D0-GUM-natural-role-review.json)。没有GUM推断。

## 已标注自然event-role资产（2026-10-06）

WikiEvents作者S3六release文件直连下载，repository253e0889b2377e0f7084cb406cf5d4142ee8a365、S3 ETag/LastModified2021-09-23+六SHA256；无不可证的immutable data revision声称。[审计](results/D0-WikiEvents-source-audit.json)。Train/dev/test206/20/20docs、3241/345/365events、4542/428/566rolelinks、实体coref4682/402/451clusters；本文本是Wikipedia reference中的news，不是全部Wikipedia文本。代码MIT、论文researchrelease不等于news文本再分发授权；raw只cache `upstream/wikievents-audit/`。Loader `scripts/wikievents.py` 保留原句/标注/null：原absolute offsets不能用于released concat document text，用每原句核对，train6span/text不一致显式保留，dev/test0。六release未暴露event-coref，mentionID不同不证明事件不同；仍需语义外审。目前仅source/schema审计，无模型推断，不另开event extraction题目。

### 2026-10-06 用户资源/审计修订
构造、改造、新增标注与必要逐条语义审核使用 **Step Plan / step-5-preview**；Messages https://api.stepfun.com/step_plan/v1/messages，Chat https://api.stepfun.com/step_plan/v1/chat/completions；禁止现金账户端点。Key只读本地私有配置、不写git或日志，总并发≤8。现成高认可度自然数据优先复用公开标注，只查来源、版本/hash、license、loader/适配所需检查，不对全库机械重审。历史Luna审计保留来源，不追改成Step审核。

### 2026-10-06 自主执行中的用户再次确认
逐条语义审计仅用 Step Plan 的 `step-5-preview`；Messages/Chat 完整路径只允许 `/step_plan/v1/messages` 与 `/step_plan/v1/chat/completions`，禁止现金账户。密钥只存本地私有配置，不写版本库或请求日志。一般自然、认可度高的数据集复用公开标注，不做全库机械审核；GP 材料缺失且直接决定真实错误资格的三类蕴含标签属于必要新增标注。

### 2026-10-06 模型传输约束
用户要求 Hugging Face 只用镜像站，禁止直连（避免 VPN 流量）。模型下载使用 hf-mirror.com 或已可达的 ModelScope 公共镜像；固定镜像 revision/逐文件SHA，推理 local_files_only。此前少量HF metadata连通诊断已结束；没有正在运行的HF直连下载。
