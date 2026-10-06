# 文件索引（2026-10-06，用户暂停）

## 先读这几份

1. [完整阶段总结](PROGRESS_SUMMARY_2026-10-06.md)：51次尝试逐项结果、失败、反证、未完成项及当前判断。
2. [诊断与转向建议](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)：失败原因（执行/数据/领域）分析与新主线建议，待人决定。
   - [方向筛选](SCREENING_2026-10-06.md)：全文精读、[公开结果审计](results/D0-Amouyal-released-item-type-audit.json)（`scripts/analyze_amouyal_released.py`）、候选比较与C1数据方案。
3. [README](README.md)：简短状态页；注册仍PROPOSED，实际研究已按用户要求暂停。
4. [CLAIMS](CLAIMS.md)：C00–C05证据等级与降级记录；没有L2/L3主旨。
5. [PAIN_LOG](PAIN_LOG.md)：数据/读数/语义审计痛点；不是科学结论的替代品。
6. [I01](ideas/I01-event-reference-or-lexical-echo.md)：唯一当前探索idea，仍PILOT；局部角色预测/用途结构不等于好paper。

## 实验档案

所有事前卡、结果勘误和阴性证据留在 `experiments/`，不移动编号或重写历史。完整逐项索引见阶段总结§3；[机器可读卡片库存](results/EXPERIMENT_INVENTORY_2026-10-06.json)。E02没有卡/实验，明确保留这个编号空缺。

| 组 | 问题 | 原卡范围 |
|---|---|---|
| Calibration与任务读数 | GP deficit、order、label、boundary、cue/focus | E00/E01/E03–E12 |
| 自然后文与患者依赖 | whole-S2、event/aspect、patient crossover、entity/verb | E13–E18 |
| 晚到角色事实与功能用途 | named/generic、recency、free continuation、independent sources | E19–E24 |
| 事件范围和新活动 | old/new actor/event、comparison、NLI、source necessity、predicate | E25–E33 |
| 真修订history与输出任务 | retraction/hypothetical、R8、affirmative、time-role、selection | E34–E42 |
| 普通语言transport与frame | minimal/balanced/proper names、三因素、inventory/status、alias form | E43–E48 |
| 明说第二角色的联合使用 | direct/formal/ordinary/pair/keyed/count，完整审计及未完成 | E49–E51 |

## 数据来源、schema与审计

- [DATA_PLAN](DATA_PLAN.md)：数据边界、原源revision/license/hash、Step Plan新指令。
- [最初D0](results/D0-audit.md)、[逐文件source manifest](results/D0-source-audit.json)：Amouyal、Jurayj、Turing的锁定字节、规模与问题。
- [模型manifest](results/D0-model-manifest.json)：权重/tokenizer/config字节与HF revision独立核验。
- [GUM最终候选审核统计](results/D0-GUM-natural-role-review.json)、[WikiEvents source/schema audit](results/D0-WikiEvents-source-audit.json)：自然资产现状；两者尚无Qwen推断；[14-pair适配检查](results/D0-WikiEvents-pair-adaptation-review.json)保留全部候选和不确定项。
- `results/D0-E*-*.json`：各次材料候选/hash、外审来源、eligible/grammar/cohort、构造勘误；不把审核模型当人类oracle。
- [Step Plan暂停快照](results/D0-StepPlan-pause-snapshot.json)：E01 565/626、E51 39/192批完整；剩余失败类别与本地manifest哈希。没有新请求/后台运行。

## 结果怎么找

- 原 `results/E##-summary.json` 是各次已提交统计，旧原始bytes不改，配套图/CSV/config可按编号找。
- E23 first/second、E49 corrected-first/primary都保留；有争议统计在卡里标来源与无效解释，不能挑分数更好版本。
- [E51小统计](results/E51-literal-schema-compact.json)只保存literal-schema的数字、CI、未知上下界；不是完整Step语义结论。完整3.76MB新分析原样留cache，SHA/路径在文件里。
- [run库存](results/RUN_INVENTORY_2026-10-06.json)索引实际本地run/config/结果hash；不能把复用分析行当新的独立推断。
- [分析资产索引](results/ANALYSIS_ASSETS.json)列较大的既有统计/分数表原SHA及本地备份。没有压缩包；本次不新增大数据、checkpoint、逐条response或大分析文件。

## 代码入口

复现环境/CLI见 [scripts/README.md](scripts/README.md)，先source [env.sh](scripts/env.sh)，复用既有venv，资源下载无代理。

| 功能 | 入口 |
|---|---|
| 原源审计、统一schema、component构造 | `scripts/data.py`及各D0卡记录的构造入口 |
| FP32原生/原协议choice inference | `scripts/infer.py`，E00–E12各卡记录CLI和配置 |
| 自然后文、角色/事件条件概率 | `followup_probability.py`及各E13–E48卡所列builder/analyzer |
| 最后几轮固定事实角色问答 | `observed_role_use.py`、`joint_role_use.py`、`time_indexed_role.py` |
| 完整回答已有语义统计 | `analyze_observed_roles.py`；只使用其卡记录的冻结外审文件 |
| E51保守格式解析 | `analyze_role_occurrence_literals.py`；输出到本地cache，未解析为null |
| 构造句问审计 | `step_audit.py`、`step_role_audit.py`；Step Plan固定端点/model |
| E51回答批审计失败的完整实现 | `step_joint_role_audit.py`；192批/39完整，保留失败，当前不重跑 |
| Plan端点与并发控制 | `step_plan.py`；只接受Plan Messages/Chat URL，进程共享8槽，无代理；不含key |
| 自然WikiEvents loader/schema | `wikievents.py`；source-offset陷阱已处理，不自动把annotation ID当独立事件 |

仅源码/文档整理，不执行上述入口。私有key在本机私有配置，任何命令、索引、正文均不回显或上传。

## 知识库和过程账

- [领域地图](../../library/themes/incremental-language-processing/FIELD_MAP.md)：GP/lingering、priming、revision、entity retrieval、presupposition/multi-answer的owner与实际阅读范围。
- `library/themes/incremental-language-processing/*.md`：原论文/资产卡。摘要、部分正文、全文区分；没有把检索结果当完整阅读。
- [2026-10-05日志](logs/2026-10-05.md)、[2026-10-06日志](logs/2026-10-06.md)：实验→数字→升/降级→后续问题，保留原过程。

## 本地cache布局（完整原文件，不压缩）

`/data1/xiangding/work/incremental-interpretation-revision/`

- `upstream/`：固定上游代码/原数据与许可、source manifest。
- `normalized/`：统一loader输出；canonical/source bytes的关系见D0。
- `models/`：本地Qwen权重与模型manifest。
- `runs/E*/`：配置、scores/predictions/generations、原prompt/回答/hash。
- `E##-material-preparation-v*/`：作者字段、rendered材料、各审计版本/失败、最终冻结输入。
- `E01-Step5-full-v1/` / `E51-StepPlan-full-answer-audit-v1/`：请求/响应/完成或失败的逐批报告。
- `analysis-originals-2026-10-06/`：既有大分析的原字节备份；不是压缩版。

GitHub没有原始语料搬运、checkpoint或私有凭证。本次只提交文档、源代码、small stats/index；既有历史大分析保持原版本。
