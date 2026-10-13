# 本地研究 Agent 直接接手：矿区 A · Persona vs Strategic Utility

**2026-10-14 / 当前任务已由用户选择 A**。这里是执行引导，不是第二套科研总宪章。所有科研准则继续以[根AGENTS](../../AGENTS.md)、[本目录AGENTS](AGENTS.md)、[EXECUTION](../EXECUTION.md)为准。

## 不要被历史文件误导
历史 E00/E02–E05、旧“必须跑LIGHT目标计划”的 LOCAL_AGENT_START、旧 RESEARCH_TERRITORIES 和过时 manifest 已退出当前HEAD；在 Git 旧提交可找回。当前**只有 E06 是PLANNED**，E01是早先CPU源码测试，不是NPC模型结果。不会从旧历史目标问题中“自动恢复”主线。安全、经济、人格漂移等领域全图保持开放，A 只是**本轮**优先探索。

## 接手即做
**先评估真实近邻：** 读 [RELATED_WORK](knowledge/persona-behavior/RELATED_WORK.md) 以后，不相信笔记代替原文，优先打开 ICML2026 *The Personality Illusion* 的正文与关键附录、2026 *Rethinking Psychometric* 原文与代码、2026 *The Story Shapes the Agent*、*Persona Vectors in Games*，以及 PCSP 真实动作环境、训练和独立行为测量。记录作者已有的最强结论、其因果/样本/统计和你重新构造 idea 来路。**尤其别把“自报和行为不同”当新发现。**

**再定位最适合探索的NPC对象：** PCSP Mini-Inzoi 的 persona/style reward 是硬编码目标之一，不能自动代表真实 RPG 玩家-NPC 策略利益。先审 PCSP (行为训练)、ccb/agent-sandbox (有合法行动的社会NPC)、LIGHT/Dragon (作者角色任务) 的**原始数据、实际用途、脚手架和成本**，建立一个从 NPC 人物设置→目标/局部状态→动作→真实世界结果的可回放链。任何一次 NPC“放弃自身利益”都要有合法游戏目标判据，不靠刻板性格推理。

**行动优先于无限写笔记：** 检查 fvcrc10/11/12/13/15/20/21 已授权 SSH 节点的实际GPU占用，优先复用已有 conda/venv、本地模型缓存与vLLM/SGLang服务。探究同时最多使用 12 张**实际授权且空闲的** GPU，但不要为了用满而占卡；全链路禁止云 API 默认回退。先在一节点跑 CPU 引擎合法动作正负控制，再本地模型 1 条成功+失败可回放轨迹。若环境无法恢复，不沉没一周；写清具体错误后转向**仍能回答游戏NPC A问题**的另一个公开底座。

**研究设计：** 认真阅读 [E06](experiments/E06-persona-strategy-baseline.md)，不是机械跑完它的四条件矩阵。先用自然案例理解角色目标、行为机会和结构相同的条件是什么。选 1–2 个高信息量干预；普通强 Prompt、task-specific TPB、等语义/长度控制、叙事背景变化、动作词锚点都应考虑。模型词风/自报与真实动作分别记录；弱基线能做不到的动作别冒充persona失效。对任何可信观察写 Fact→Interpretation（至少两个替代解释）→Speculation（下一实验），然后检查与已知 claim owner 的距离。

**机制/方法可以主动跟进，但不能预支：** 只有出现可靠、独立、有NPC意义的现象，且提示/接口/场景措辞/量表解释不足，才考虑 actor隐状态探针、activation steering、SFT/LoRA/GRPO 或新评价；最便宜的决定性对照优先。不要为了满足“矿区A”而需要所有实验都跑出 gap。

## 每次汇报
明确列出所用源commit/model/data/状态、作者事实和你实测的事实、CPU/GPU/token成本、异常及负结果、未排除解释、下一个最有信息增益的动作；更新 knowledge/persona-behavior/、E06、logs/results/CLAIMS/PAIN_LOG，**不把这次仓库文件整理当科研发现**。
