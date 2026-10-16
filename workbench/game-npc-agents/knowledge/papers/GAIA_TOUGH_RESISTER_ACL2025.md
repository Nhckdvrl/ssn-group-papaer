# Battling against Tough Resister: Strategy Planning with Adversarial Game for Non-collaborative Dialogues（ACL 2025 Main）

证据：正文与关键附录；未复现训练。主源：[正式页](https://aclanthology.org/2025.acl-long.184/)、[PDF](https://aclanthology.org/2025.acl-long.184.pdf)。核读 §3.3–3.7、§4.1–4.6/Table1–4/Fig2–3、Appendix A/CoM 模板、D.1/D.2/策略表、E 人评；B/C 的论证结构有读，不声称独立验证其理论证明。未找到可确认作者实现仓库，未将第三方解读当源码。

1. **形态与问题：** 方法＋多轮非合作对话实验。背景是刺激式提示与外部策略规划器难以适应强抵抗对手。
2. **Idea 来源：** DOCUMENTED：让策略规划器面对可增强、多样的对手，交替自博弈优化；以 Chain-of-Mind 推断对手状态后规划。RECONSTRUCTED：将“对手难度”从固定环境假设变成显式实验变量。
3. **对手怎样控制：** 在 SFT 中保存不同表现的抵抗策略 planner；训练中 planner 选策略，LLM 按角色/目标/策略生成回复，双方交替 RL；另给抵抗生成器 Big Five 风格。不是直接给一条静止请求。
4. **训练/评价区别：** 主表与消融使用单一、无策略 planner 的 LLM 对手；另测不同 planner 强度与人格，强度按 SFT 策略 F1 分组。不能把主表当全部强对手上的表现。
5. **数据与基线：** CB 价格谈判、DC 反仇恨、CP 慈善说服。Table1 比较 Standard、ProCoT、ICL-AIF、MCTS、PPDPP、TRIP；Table2 拆模块，Table3 测对手强度；最大12轮。全量训练算力/seed 本轮未核对。
6. **关键评价边界：** Appendix D 的成功由对话 critic/文本指标判定；CB 的“成交”不等于引擎中已付款和移交物品。Appendix E 有真人对话及后续人评，也没有库存守恒式原生交换。主表正结果不能替代我们的实体后果。
7. **距离与可迁移动作：** 有目标、有人格、有响应的对手和多轮策略规划都有强先例。直接继承对手控制与训练/评测分离的思想；下一步重点问响应怎样改变 NPC 的目标采纳、必要行动和实际资源去向，不必再造 self-play 训练线。
8. **对整体研究：** 有响应玩家是研究条件，不是单独 novelty。人设—自身作者目标—社会互动—物理前提的联合解释仍是我们的完整问题。不能因近邻已有策略对手，就退回只申领某一动作提示或管道细节。

只读 PDF 缓存：`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/gaia.pdf`；SHA256 `8e46751b5c6d16aeaf4a76b58fdb9b661fc3b62fc2a39baf5c0b15d58585808b`。
