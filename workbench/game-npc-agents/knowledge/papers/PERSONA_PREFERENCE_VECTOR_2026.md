# Probing Persona-Dependent Preferences（2026预印本；会场未核实）`[证据：正文/关键附录/局部代码入口]`

[论文](https://arxiv.org/html/2605.13339v1)、[作者代码](https://github.com/oscar-gilg/Preferences)。已读§2–4、C/D/E/F/H/I/J/K；代码仅README/CODE_GUIDE及模块定位，尚未完整实现审计/复现。

1. 形态：偏好构念＋表征/因果实验。DOCUMENTED来源是同一模型不同persona的偏好 machinery是否共享。
2. 方法：6000任务、5000/1000划分；pairwise选择拟合Thurstonian utility，残差线性probe，跨话题/人物与匹配随机向量steering。utility是模型任务选择推断，不是独立游戏收益。
3. 强证据/边界：Gemma有强因果steering；Qwen122B解码更强但steering约15倍更弱，附录保留负结果。固定2000任务，更多persona提高迁移；SFT persona迁移接近零。去除canonical方向仍98–99%选择一致，支持分布式而非唯一必要方向。
4. 关键审计：附录明确多维偏好、prompt/weight层差异、EOT位置与任务内容分解。不能只读摘要声称任意共享向量/跨人物传递新颖；README概述也不能替代这些限定。
5. 对我们：E39方向传递/可读性与因果响应分离均有强近邻owner。当前I03用原生利益、实际状态和训练绑定经验研究角色控制形成；不能仅增加NPC名字重包装此表示结论。
