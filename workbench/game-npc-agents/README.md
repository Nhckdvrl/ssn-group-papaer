# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED，当前驻留矿区 A：Persona / Character Identity ↔ Strategic Behavior。** 这是用户于 2026-10-14 选定的**本轮探索优先级**，并不意味着已证明言行解耦，也**不覆盖整个领域**。全局 ACTIVE 名额与其他 workbench 不变。

## 两个层次，严格分开
- **领域整体：** 游戏内 RPG、社会角色、队友、敌人、商人等 NPC 的行动、人物、记忆、安全、经济、协作、训练、具身与玩家体验。[完整领域地图](knowledge/DOMAIN_ATLAS.md)是长期总入口，任何一个矿区都不能将其删除。
- **当前矿区 A：** 人物设定/自述、与具体游戏决策相关的意图、实际策略选择和世界后果之间是什么关系？当 NPC 面临真实的玩家请求、利益约束与角色目标时，哪些控制信号真正影响其行动？优先**现象/测量/机制**，必要时发展训练/控制方法。只需证明游戏 NPC 中有意义的认识，不强制每个实验涉及3D或完整商业游戏。

**禁止再次把“LLM自称人格却不行动”当新发现：** ICML2026 *The Personality Illusion* 已报告自述/行为不可靠；2026作者公开的 *Rethinking Psychometric Evaluation* 进一步指出人格测量粒度/会话上下文影响预测；2026 *The Story Shapes the Agent* 报告叙事背景强烈影响相同决策结构的 agent 策略；PCSP 自己的独立行为评估也有不同于内部指标的结果。具体贡献距离见 [矿区 A 文献图](knowledge/persona-behavior/RELATED_WORK.md)。

## 唯一当前执行入口
| 层次 | 文件 |
|---|---|
| **直接交给本地 Agent** | [LOCAL_AGENT_START.md](LOCAL_AGENT_START.md) |
| 当前研究问题/竞争解释 | [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) |
| 矿区 A 的原始研究认知 | [knowledge/persona-behavior/README.md](knowledge/persona-behavior/README.md) |
| 已有最强文献与不能冒领的点 | [knowledge/persona-behavior/RELATED_WORK.md](knowledge/persona-behavior/RELATED_WORK.md) |
| 作者代码已核部分与待审路径 | [knowledge/persona-behavior/CODE_AUDIT.md](knowledge/persona-behavior/CODE_AUDIT.md) |
| 自然数据、对照和初步可否决实验设计 | [experiments/E06-persona-strategy-baseline.md](experiments/E06-persona-strategy-baseline.md) |
| 知识库全域导航 | [knowledge/README.md](knowledge/README.md) |
| 运行资源/来源/观测纪律 | [LOCAL_FIRST.md](LOCAL_FIRST.md)、[BASELINES.md](BASELINES.md)、[knowledge/MEASUREMENT.md](knowledge/MEASUREMENT.md) |
| 当前主张/痛点/结果 | [CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md)、[results/README.md](results/README.md) |

## 目录简化
旧的 `RESEARCH_TERRITORIES.md` 与过时 `configs/entry_manifest.json` 已从当前 HEAD 清除。未执行且因用户明确变更选题而失效的 E00/E02–E05 实验卡也移出当前树：可在[历史快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/37f4e9ba4152c3a21c36c73830897221a186924b/workbench/game-npc-agents/experiments)和 git 中追溯，**不是实验否定/科研失败**。E01 实际 CPU 源码检查、全部深读论文卡及领域安全/经济知识库保留。新的 E06 只是**PLANNED，未运行**。

## 实验与资源现状
2026-10-14已跑通作者ActionCastle本地闭环，Qwen3-32B/Gemma3-12B/Qwen3.5-27B与原生free-text/single-tool/per-action tool对照全部保留。普通一句提示将E12首次合法48/133提高到92/135，先前失败不能直接讲Persona机制。PCSP公开已训练v3政策恢复480原生动作+160精确重放，人物条件明显影响行为。LIGHT原作者7486quest/2111human demos核验，692条可在完全相同图中匹配bot独立作者目标，当前12自然图×3seed本地NPC运行中。[结果与校对清单](results/README.md)、[源码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md)、[日志](logs/2026-10-14.md)。**C01仍L1基线可行性，新科学增量仍0。**

## 资产位置与重建
模型复用HuggingFace缓存，完整rollout/LLM输入输出不进Git，位于本机 `/home/xiang/.cache/game-npc-research/runs/`；上游源码/paper分别在同缓存 `sources/` / `papers/`，commit与PDF hash见 `results/E08_sources.json`。用 `scripts/native_actioncastle.py` 和E07卡重跑；现有Conda fgvd配合隔离deps overlay，具体版本由每次manifest固定。用户已授权七节点全部GPU，07:00 Asia/Tokyo起本项目最多8卡，优先现有Conda/venv；零付费API与单节点优先见LOCAL_FIRST。

## 当前科学判断
E09的literal-location与格式校对不能合并：Qwen32单句2/9→6/9经POST-HOC唯一房间审计仅5/9→6/9；Gemma原本9/9知自己位置但动作仍常非法。E10/E12的raw parser数包含递归，已独立重建root归因，不把子命令当新模型选择。E14首2条speech载荷遗漏是本地adapter错误，通信证据降级后全量重跑，不归因NPC失败。强近邻新加入ReflAct、ReFract、FAccT2026 Identity Overrides Incentives；不冒领goal-state reflection、role gate、Persona×payoff交互。没有建立新的策略/人格科学主张。
