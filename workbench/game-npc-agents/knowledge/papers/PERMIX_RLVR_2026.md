# PerMix-RLVR — 2026 预印本

- 原文<https://arxiv.org/abs/2604.08986>；已读§3–4方法/主表、A.5/A.6理论范围、B训练与PersonaGym入口。全文未见可确认完整作者code链接；会场未核验。
- **DOCUMENTED：** RLVR的准确性对persona稳定与role fidelity有权衡；以persona混合训练改善Math500 worst/best稳定度并保持PersonaGym一致性。学生Llama3.1-8B，QLoRA，教师和无教师实验分开。PSS=worst/best；高PSS也可能因所有persona都差，不能单看这个ratio。
- **理论范围：** A.6明确style/reasoning因子化是verifiable reasoning的抽象，不是LLM内部事实；persona-independent competence假设不能用于NPC自身utility随role变动的场景。准确性/PSS命题另依赖二值verifier/KL最优策略。
- **RECONSTRUCTED：** 训练目标能够改变persona敏感性→persona mixed RL而非不断搜prompt。不能把“RL优化压制/保留persona”重新命名成我们的发现。该文非原生游戏执行；全文其他appendix/数据代码未审完。
