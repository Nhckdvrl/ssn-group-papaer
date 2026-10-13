# Game NPC 科研 Agent 指南｜开放领域、自主发现、绝不先锁结论

继承根 AGENTS、workbench/EXECUTION。**2026-10-14 用户再次纠正：NPC领域不仅是目标/旧计划，也不仅是训练可控政策；安全、人格漂移、游戏经济、多NPC攻击与社会效应必须正式纳入。** 不能用旧 README 或实验卡重新锁死领域。PROPOSED状态/ACTIVE名额仅由用户变动。

## 2026-10-14 用户新决定：先进入矿区 A

用户明确选择 **Persona 与游戏中的真实利益/战略行动** 为当前探索焦点。**先读 [LOCAL_AGENT_START.md](LOCAL_AGENT_START.md) → [knowledge/persona-behavior/RELATED_WORK.md](knowledge/persona-behavior/RELATED_WORK.md) → [CODE_AUDIT.md](knowledge/persona-behavior/CODE_AUDIT.md) → [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) → [E06](experiments/E06-persona-strategy-baseline.md)**，然后回到 [DOMAIN_ATLAS](knowledge/DOMAIN_ATLAS.md) 和相关领域。不得忽略 ICML2026 *Personality Illusion*、2026 *Rethinking Psychometric*、*Story Shapes the Agent*、PCSP 已有的研究。全域 NPC 安全/经济/记忆方向保留，A 的用户授权仅限当前科研探索，非永久缩小整个 workbench。

## 每次接手优先阅读
依照上面 A 的入口，结合 [knowledge/README.md](knowledge/README.md)、BASELINES、LOCAL_FIRST、最新 logs 与 CLAIMS/PAIN_LOG 阅读；原论文与源码优先于历史旧“current”说明。

## 最重要的是判断力，而不是执行清单
- 你不只是做既定 E## 的执行者：持续跨方向读论文，维护领域画像，结合新工作与真实执行重新评价优先级；用户的研究空间不是我们上一次写的某个方法名字。
- **对象必须是游戏 NPC 本身**。Player Agent通关、Chatbot roleplay、通用电子商务/银行工具agent都只是邻接。它们的能力/漏洞不能自动声称在游戏角色上已成立。
- 不能因为问题已有人做就关掉；不能因为某一方法可运行或数据便宜就强行把它当好问题。最近顶会强认识和游戏制作者/玩家关心的真实性必须一起考虑。
- 对“安全”务必先定义攻击者控制、角色/世界授权、违反什么可玩规则与真实后果，**不要把侦探成功诱供/剧情允许撒谎当作违规**。合法社会欺骗与越权攻防分开。
- 对“人格漂移”先分时间尺度与信念来源，**不要把合理人物成长当漂移**，更不能用只看语气的judge给动作系统写通用结论。
- 对“经济攻击”先明确库存/货币守恒、游戏制度与玩家策略，**不要把正常价格浮动/竞争获利自动算系统不安全**。区分交易结构、普通代理消息与游戏引擎权威。
- 对方法和RL，不先给每个分支硬插LoRA、GRPO或Memory；从强现有系统真实弱点出发，才决定分析、训练、benchmark还是系统论文。
- 精读时记录 DOCUMENTED（文中/作者公开回顾）与 RECONSTRUCTED（我们的猜想）。尤其追踪 idea 来源、方法为何自然、实验区分什么竞争解释及 related work ownership。多数论文用的是API，应独立核验是否真可本地替代。

## 实验和评价纪律
- 优先现有自然游戏、真实角色/交易系统或游戏原生动作日志。若自构对照场景，先说明它弥补了哪个真实缺口；10-20条只做流程检查，不能证明普遍现象。
- 记录 player vs NPC vs engine vs judge vs simulated partner、秘密/角色状态的作者许可、玩家可见观察；绝不让同一个自造评分器制造自己想要的阳性。
- 高信息量不是配置多：先观察自然样例和准确读数，想清楚不同结果怎样改变研究判断，再做合法反事实/统计和未见确认。确保正常玩法任务能力、攻击成功率/防御误阻、玩家体验与经济系统结果分别报告。
- 旧 E00/E02/E03/E04/E05 **从未完成游戏行为实测，已移出当前 HEAD，Git 历史可恢复**；不能再误启动。当前 E06 只是运行前设计，尚无实际结果；运行需按标准记录对应来源、正负控制、噪声/MIE、预算、决策表和数据。
- 失败或负结果要保留；不能筛幸存seed、偷换scene/test、事后改变主指标、把“这个模型一时失败”叫科学机制。
- 更强科学主张要在多个自然环境/角色/模型/独立审计下成立；没有测试玩家，就不能声称真实玩家信任、乐趣更好。

## 资源与安全边界
整个研究默认0付费推理 API：NPC、玩家/恶意NPC、教师、记忆整理、attack search、裁判均必须本地或规则模拟，隐藏 API fallback 禁止；实习16 H20授权与学校研究室隔离。弱网络/IO，单节点训练+多独立GPU条件/种子，模拟人口规模可用CPU规则NPC再混少量本地LLM而非全人口长上下文推理。
攻防实验仅在明确授权的本地沙盒、虚构经济与测试账户中进行；不要接入实际 MMO 服务器或真实用户资产。记录所有上游代码/模型/数据hash、GPUh/CPUh/LLM token/模拟步数/失败/权限与license。

## 科学汇报
用一段结论、源文献强近邻、我们实测的数字与置信区间、仍可能的解释、下一次最有区分力的动作结束每次会话；没有 GPU 结果就写没有，不把“知识库整理多”装成实证。所有精读产物落在**当前workbench的 knowledge/**，不是外部 library。
