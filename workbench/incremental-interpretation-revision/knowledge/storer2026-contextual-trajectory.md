# Contextual trajectory and incremental contextual displacement（2026 v1）

[原文](https://arxiv.org/abs/2610.00840v1)。实际读取：正文§1–5、C/D/I附录片段；52页PDF的大量图和其他附录未全部核对。cache与SHA见READING_LEDGER。

1. **论文形态：** 新表征读数的face-validity与分类验证，尚非行为修订机制。
2. **背景与压力：** 固定最终embedding可能掩盖逐词语境整合。
3. **改变的前提：** 每添一个词，重新编码RoBERTa完整prefix并跟踪指定token；并非autoregressive原token向后更新。
4. **idea来源（DOCUMENTED）：** 动态局部meaning construction；把已有GP surprisal/几何连接到上下文轨迹。
5. **近邻增量：** 位移向量、turbulence等轨迹指标；不只是最终GP/control embedding距离。Jurayj/Li为直接前身。
6. **方法与证据：** Grodner 80/20、100次CNN分类，验证约98.5%；Sturt独立集合约99.8%；打乱轨迹后约56%。首普通词trajectory也可分类；临界region首词holdout约54.9%，末端单差向量约50.9%。不把只报CLS的高分写成全token泛化。
7. **边界：** 顺序打乱损伤不唯一证明“U-turn”；也可能损伤其他有序特征。几何和高分类不能直接证明正确事件理解或修订。句法cue字节、位置、长度仍应控制；模型是双向重新编码器。
8. **可迁移动作：** 增加独立材料holdout；把正分类与末端/临界词泛化失败一起报；对轨迹形状提出额外可区分预测。
9. **对我们：** 通用GP轨迹/几何变化已有owner。当前不因此开启probe/训练；E11优先修读数。之后若测prediction/QA分歧，须给出语言证据和后果，不叫“发现轨迹不等于理解”。
