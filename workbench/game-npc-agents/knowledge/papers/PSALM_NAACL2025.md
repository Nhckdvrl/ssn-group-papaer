# PSALM — 从环境反馈推断动作语义

*Language Models Can Infer Action Semantics for Symbolic Planners from Environment Feedback*，NAACL2025 main。[正式页](https://aclanthology.org/2025.naacl-long.440/) · [正文/附录PDF](https://aclanthology.org/2025.naacl-long.440.pdf)。2026-10-15核读§3–5、Table1–3/Figure4–6、AppendixB.1与C/Figure14–19；未审计代码或复现。

**DOCUMENTED：** idea源于LLM会猜计划但难追状态、符号规划器须已知动作语义的互补。通过执行错误与状态变化更新前/后条件的概率记忆，再用FAST-DOWNWARD。七域各20任务；选需覆盖全部动作的任务学习，再测其余任务，三次运行。§4.3明确错误提示指出未满足前提；还有直接解析反馈的规则模块。§5.4去错误文本显著受损。AppendixB另测从部分动作任务持续学习。

**定位判断：** 反馈学习动作语义、补齐前提并恢复规划已有直接owner，不能将E70机制事实或E72错误恢复包装成首次发现。我们的对照保留NPC自有作者目标与另一角色请求，主要区分“交付给谁”与“操作路径是否走通”，并测人物效应是否随条件改变。若E72解释了旧失败，应当更新测量解释；增量不来自再实现一个PDDL系统。

**边界：** PSALM依赖符号谓词/动作头、可重置环境与给出前提的反馈，其100%不是任意视觉NPC保证。正文有规则推断和规划器，不能称纯LLM内在能力。E72也不能由纠错后的恢复单独推断模型早已知道规则。
