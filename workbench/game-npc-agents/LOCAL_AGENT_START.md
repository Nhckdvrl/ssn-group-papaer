# 本地研究 Agent 直接接手：矿区 A · Persona vs Strategic Utility

**2026-10-14 / 当前任务已由用户选择 A**。这里是执行引导，不是第二套科研总宪章。所有科研准则继续以[根AGENTS](../../AGENTS.md)、[本目录AGENTS](AGENTS.md)、[EXECUTION](../EXECUTION.md)为准。

## 不要被历史文件误导
**用户已明确恢复科研，并要求按总体审计判决重构。** 当前入口是 [I04](ideas/I04-commitment-conflict-stage-arbitration.md)、[E50](experiments/E50-commitment-decision-snapshots.md)、[E51](experiments/E51-stage-persona-causal-transfer.md) 与最新日志。PCSP／MeltingPot小模型RL冻结；禁止1200帧全图盲跑、单模块修改冒称完整persona效应、无实体flag任务。旧 [进度报告](PROGRESS_REPORT_2026-10-14.md) 只作历史背景。
历史 E00/E02–E05 和过时 manifest 不恢复。E06 是历史统领设计；E43 原为小MLP诊断，已冻结，新的LLM跨阶段白盒在E50实际执行。安全、经济、人格漂移等全域仍开放，A只是本轮优先探索。

## 接手即做
**先评估真实近邻：** 读 [RELATED_WORK](knowledge/persona-behavior/RELATED_WORK.md) 以后，不相信笔记代替原文，优先打开 ICML2026 *The Personality Illusion* 的正文与关键附录、2026 *Rethinking Psychometric* 原文与代码、2026 *The Story Shapes the Agent*、*Persona Vectors in Games*，以及 PCSP 真实动作环境、训练和独立行为测量。记录作者已有的最强结论、其因果/样本/统计和你重新构造 idea 来路。**尤其别把“自报和行为不同”当新发现。**

**再定位最适合探索的NPC对象：** PCSP Mini-Inzoi 的 persona/style reward 是硬编码目标之一，不能自动代表真实 RPG 玩家-NPC 策略利益。先审 PCSP (行为训练)、ccb/agent-sandbox (有合法行动的社会NPC)、LIGHT/Dragon (作者角色任务) 的**原始数据、实际用途、脚手架和成本**，建立一个从 NPC 人物设置→目标/局部状态→动作→真实世界结果的可回放链。任何一次 NPC“放弃自身利益”都要有合法游戏目标判据，不靠刻板性格推理。

**资源纪律：** 用户授权fvcrc10/11/12/13/15/20/21，先核实际空闲，不干扰他人；本轮最高同时8卡，独立单卡／单节点优先。复用conda/venv和模型缓存，禁止云API默认回退。Step5仅用于用户授权的数据构造／质检，固定Token Plan专用端点；NPC／玩家／实体评价保持本地。已有原生资格不从头重复。

**研究设计：** 认真阅读 [E06](experiments/E06-persona-strategy-baseline.md)，不是机械跑完它的四条件矩阵。先用自然案例理解角色目标、行为机会和结构相同的条件是什么。选 1–2 个高信息量干预；普通强 Prompt、task-specific TPB、等语义/长度控制、叙事背景变化、动作词锚点都应考虑。模型词风/自报与真实动作分别记录；弱基线能做不到的动作别冒充persona失效。对任何可信观察写 Fact→Interpretation（至少两个替代解释）→Speculation（下一实验），然后检查与已知 claim owner 的距离。

**机制/方法可以主动跟进，但不能预支：** 只有出现可靠、独立、有NPC意义的现象，且提示/接口/场景措辞/量表解释不足，才考虑 actor隐状态探针、activation steering、SFT/LoRA/GRPO 或新评价；最便宜的决定性对照优先。不要为了满足“矿区A”而需要所有实验都跑出 gap。

## 每次汇报
明确列出所用源commit/model/data/状态、作者事实和你实测的事实、CPU/GPU/token成本、异常及负结果、未排除解释、下一个最有信息增益的动作；更新 knowledge/persona-behavior/、E06、logs/results/CLAIMS/PAIN_LOG，**不把这次仓库文件整理当科研发现**。
