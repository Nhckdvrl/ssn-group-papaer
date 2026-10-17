# 基线、来源与本地资产

更新2026-10-16。**选择系统由科学问题决定；能下载、已跑通物理链、复现论文、足以回答NPC问题是不同事实。** 当前保持[暂停](AGENTS.md#当前执行边界)，本页不是待运行队列。整体认识见[项目报告](PROJECT_PROGRESS_REPORT_2026-10-16.md)，具体资格／结果／失败以原实验卡和manifest为准。

## 已恢复的基线与能力边界

| 系统 | 已实际取得的能力／证据 | 入口与边界 |
|---|---|---|
| agent-sandbox / Action Castle | 本地LLM→原parser→实体后果与回放 | [E07](experiments/E07-native-actioncastle-closure.md)、[源码审计](results/audits/SOURCE_AUDIT_2026-10-14.md)；重试、Reflect与fallback单列，不当策略成功 |
| LIGHT / Dragon原作者任务 | 原persona、各层动机、目标、原生typed工具、实际说话与双方物料状态；E81／E84完整互动、E85配对延续 | [E81](experiments/E81-authored-cooperation-and-partner-response.md)、[E84](experiments/E84-independent-goals-and-alternative-cooperation.md)、[E85](experiments/E85-partner-performance-and-revision.md)；动作标签、物理后果与完整目的分开 |
| 校园生成式NPC | 三条自然历史、原计划／记忆／对话及1200帧完整后续 | [E35](experiments/E35-original-three-npc-goal-loop.md)、[E49](experiments/E49-cross-role-commitment-causality.md)；历史资产保留，旧漫游及局部人物干预冻结 |
| PCSP / MeltingPot | 源码／奖励／梯度／编码审计、全预算训练与独立实体评价 | [E34](experiments/E34-full-budget-corrected-baseline.md)、[E38](experiments/E38-independent-strategic-environment.md)、[E41](experiments/E41-interventional-persona-coverage.md)；旧小模型执行已冻结，不再追加训练或种子 |
| MINDcraft / MineCollab | 原Minecraft双方库存→真实转移／制作→原validator的CPU见证 | [E82](experiments/E82-minecraft-original-cooperation-baseline.md)；原bookshelf共同任务，0模型，不当角色利益冲突证据 |
| Microsoft角色任务的明确重建 | Alaric找回剑／条件奖励切片，两条Qwen完整路径及独立收件读回 | [E83](experiments/E83-npc-quest-receipt-and-reward-baseline.md)；非微软原世界／原系统复现，同一角色两路径不作总体统计 |

## 当前比较能力的缺口

截至本次审查，后期主要是Qwen3-32B与Gemma3-12B，本地共享客户端关闭thinking、输出上限512；有原人物/各层动机、状态、合法工具和反馈，不能称裸提示。但尚无强商业推理模型加完整普通记忆/重规划的同域结果，合作上下文的最近32条消息也不等于有效承诺持久记录。具体源码、分母和未排除解释见[独立审查](results/audits/INDEPENDENT_RESEARCH_VALUE_REVIEW_2026-10-18.md#5-普通强基线还缺什么来自实际源码)。这些是证据缺口，不是认定商业模型必然解决；[完整比较原则](../knowledge/STRONG_BASELINES.md)不构成新执行队列。

## 本地数据、环境与复算

- 统一资产根为`/home/xiang/.cache/game-npc-research/`。`runs/`保存各E##原图、实际messages／schema／seed、原生事件、逐步状态、模型输出、manifest、启动／退出和失败；完整source与模型缓存另按manifest指针读取，不入Git。
- LIGHT源码pin为`71a06cae8573048b1af41507ac52fe33b650fab3`；quest档案SHA为`743d9a9dc85e9fd7737c6cb51762deae684382de326bf724cde5b72bcf7c7c7d`。不同实验的资格、曝光与图联集以各source结果为准，不能按文件名reserve推未见。
- NPC／Mini-Inzoi历史环境沿用`/home/xiang/miniconda3/envs/fgvd`与`/home/xiang/.cache/game-npc-research/deps`隔离依赖；MeltingPot历史环境为`lightwam`及其overlay。Minecraft沿用已有Node／Java和cache内依赖。冻结环境只用于解释／复算原资产，不构成启动许可。
- 已用Gemma3-12B-it revision `96b6f1eccf38110c56df3a15bffe176da04bfd80`、Qwen3-32B revision `9216db5781bf21249d130ec9da846c4624c16137`；27B和其他历史模型及chat template以各manifest为准。不能只用模型简称冒称同一配置。
- E70–77 raw为`runs/e70_*`至`e77_*`；E80为`e80_*`，E81／E84为各模型profile与full目录。E85最终outcome只取`runs/e85_{gemma,32b}_recover_s{0,1}/`，旧profile／full保留作精确输入cache及实际成本，不合并旧episode充N。
- 复算与执行脚本入口见[scripts](scripts/README.md)，最终统计、资格、成本及source hash见[results](results/README.md)。历史校园cassette可离线CPU重放，但当前暂停仍不启动引擎。一次性环境修复、partial与最终结果的区别以实验卡为准。
- 研究室共享资产可用已有SSH／共享文件系统读取或rsync；不要重下模型、盲目修节点或把弱网络多卡当高速mesh。资源、API与授权规则只在[AGENTS](AGENTS.md#资源权限与资产)维护。

领域候选资产见[通用资产目录](../BASELINES.md)；矿区A的数据入口见[data](data/README.md)。
