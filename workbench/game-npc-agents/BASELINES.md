# 基线、来源与本地资产

更新2026-10-16。**选择系统由科学问题决定；能下载、已跑通物理链、复现论文、足以回答NPC问题是不同事实。** 当前保持[暂停](AGENTS.md#当前执行边界)，本页不是待运行队列。整体认识见[项目报告](PROJECT_PROGRESS_REPORT_2026-10-16.md)，具体资格／结果／失败以原实验卡和manifest为准。

## 已恢复的基线与能力边界

| 系统 | 已实际取得的能力／证据 | 入口与边界 |
|---|---|---|
| agent-sandbox / Action Castle | 本地LLM→原parser→实体后果与回放 | [E07](experiments/E07-native-actioncastle-closure.md)、[源码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md)；重试、Reflect与fallback单列，不当策略成功 |
| LIGHT / Dragon原作者任务 | 原persona、各层动机、目标、原生typed工具、实际说话与双方物料状态；E81／E84完整互动、E85配对延续 | [E81](experiments/E81-authored-cooperation-and-partner-response.md)、[E84](experiments/E84-independent-goals-and-alternative-cooperation.md)、[E85](experiments/E85-partner-performance-and-revision.md)；动作标签、物理后果与完整目的分开 |
| 校园生成式NPC | 三条自然历史、原计划／记忆／对话及1200帧完整后续 | [E35](experiments/E35-original-three-npc-goal-loop.md)、[E49](experiments/E49-cross-role-commitment-causality.md)；历史资产保留，旧漫游及局部人物干预冻结 |
| PCSP / MeltingPot | 源码／奖励／梯度／编码审计、全预算训练与独立实体评价 | [E34](experiments/E34-full-budget-corrected-baseline.md)、[E38](experiments/E38-independent-strategic-environment.md)、[E41](experiments/E41-interventional-persona-coverage.md)；旧小模型执行已冻结，不再追加训练或种子 |
| MINDcraft / MineCollab | 原Minecraft双方库存→真实转移／制作→原validator的CPU见证 | [E82](experiments/E82-minecraft-original-cooperation-baseline.md)；原bookshelf共同任务，0模型，不当角色利益冲突证据 |
| Microsoft角色任务的明确重建 | Alaric找回剑／条件奖励切片，两条Qwen完整路径及独立收件读回 | [E83](experiments/E83-npc-quest-receipt-and-reward-baseline.md)；非微软原世界／原系统复现，同一角色两路径不作总体统计 |

## 本地数据、环境与复算

- 统一资产根为`/home/xiang/.cache/game-npc-research/`。`runs/`保存各E##原图、实际messages／schema／seed、原生事件、逐步状态、模型输出、manifest、启动／退出和失败；完整source与模型缓存另按manifest指针读取，不入Git。
- LIGHT源码pin为`71a06cae8573048b1af41507ac52fe33b650fab3`；quest档案SHA为`743d9a9dc85e9fd7737c6cb51762deae684382de326bf724cde5b72bcf7c7c7d`。不同实验的资格、曝光与图联集以各source结果为准，不能按文件名reserve推未见。
- NPC／Mini-Inzoi历史环境沿用`/home/xiang/miniconda3/envs/fgvd`与`/home/xiang/.cache/game-npc-research/deps`隔离依赖；MeltingPot历史环境为`lightwam`及其overlay。Minecraft沿用已有Node／Java和cache内依赖。冻结环境只用于解释／复算原资产，不构成启动许可。
- 已用Gemma3-12B-it revision `96b6f1eccf38110c56df3a15bffe176da04bfd80`、Qwen3-32B revision `9216db5781bf21249d130ec9da846c4624c16137`；27B和其他历史模型及chat template以各manifest为准。不能只用模型简称冒称同一配置。
- E70–77 raw为`runs/e70_*`至`e77_*`；E80为`e80_*`，E81／E84为各模型profile与full目录。E85最终outcome只取`runs/e85_{gemma,32b}_recover_s{0,1}/`，旧profile／full保留作精确输入cache及实际成本，不合并旧episode充N。
- 复算与执行脚本入口见[scripts](scripts/README.md)，最终统计、资格、成本及source hash见[results](results/README.md)。历史校园cassette可离线CPU重放，但当前暂停仍不启动引擎。一次性环境修复、partial与最终结果的区别以实验卡为准。
- 研究室共享资产可用已有SSH／共享文件系统读取或rsync；不要重下模型、盲目修节点或把弱网络多卡当高速mesh。资源、API与授权规则只在[AGENTS](AGENTS.md#资源权限与资产)维护。

## 仍开放领域的候选资产

以下是既有源码／论文审阅范围，不是已运行或现行推荐清单；原版本核验见知识页。当前矿区A优先不永久关闭这些领域。

| 领域 | 已有来源 | 已知范围与边界 |
|---|---|---|
| 角色安全／泄密 | [Gigax](https://github.com/GigaxGames/gigax)、[Shiomi](https://arxiv.org/html/2508.19288v1)、LIGHT、agent-sandbox | Gigax有本地GGUF与stepper；Shiomi仅单NPC单轮示范，非强长期基准；先分剧情许可与越权后果 |
| 动态人格／社会记忆 | LIGHT／Dragon、PCSP research、[MineAmongUs](https://github.com/JunseoKim0103/Lies-We-Can-See) | 读者应核原规则与时间尺度；MineAmongUs有Docker／日志但默认API与多agent运行成本未本地验证 |
| 游戏经济／群体互动 | [MMOAgent归档](https://doi.org/10.5281/zenodo.15526912)、[AI-Bazaar](https://github.com/sethkarten/AI-Bazaar)、[BAZAAR](https://github.com/lechmazur/bazaar) | MMOAgent小档案已下载和定点读码，未本地运行；后两者非天然NPC私有目标证据，不能把原子成交当未来兑现 |
| 多模态／具身 | MineAmongUs、[ReactiveGWM](https://github.com/INV-WZQ/ReactiveGWM) | 公开视觉／日志不等于本机已复现；视频I/O、服务器、默认推理与授权需按实际任务确认 |
| 邻接攻防／行为训练 | [AgentDojo](https://github.com/ethz-spylab/agentdojo)、[ASB](https://github.com/agiresearch/ASB)、EA商用引擎工作、UBCL／MultiGAIL | 通用工具代理不等于NPC；专有引擎与未开放资产不称可复现，不能因训练可跑就改科研问题 |

选任务时只核真正决定解释的来源／角色／规则／可行后果、私有信息边界、强普通基线与本地成本。语义规范、角色可信度和玩家体验不能由同源模型或单一物品分数替代。具体正文／附录／作者代码和可执行入口集中在[knowledge](knowledge/README.md)，不在此重复第二套综述。
