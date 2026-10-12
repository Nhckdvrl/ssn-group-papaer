# Xeno-Interpretability · 模型原生表征与观察者的解释边界

**PROPOSED**（用户已批准独立 workbench，尚未批准改变 ACTIVE 资源分配）；原始启发：[Pierucci et al. 2026](https://arxiv.org/abs/2609.20408)。
**科学中心**：已有可解释性发现了大量人类能命名的概念。这究竟反映了模型天然的组织，还是**发现程序本来就在选择人类熟悉的变量**？若先不命名，而研究内部对象的稳定关系和自然计算作用，能否找到更充分、可预测的解释？

## 入口
- [knowledge/README.md](knowledge/README.md) · 本项目知识库与阅读深度说明。
- [knowledge/LITERATURE_MAP.md](knowledge/LITERATURE_MAP.md) · 领域谱系、最近邻的 claim ownership、科学假设与初步方向选择。
- [knowledge/papers/CORE_READS.md](knowledge/papers/CORE_READS.md) · 先前 17 篇研究卡 + 这轮新增的强论文、idea 来源重建和证据边界。
- [knowledge/papers/PIERUCCI_2026_XENO.md](knowledge/papers/PIERUCCI_2026_XENO.md) · Xeno 45 页原论文重读。
- [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) · **给本地研究 agent 的初步实验入口**（问题、竞争解释、决定性实验与反馈原则）。
- [knowledge/READING_QUEUE.md](knowledge/READING_QUEUE.md) · 全文/部分/摘要与确实无法获取的来源分开。

## 状态与纪律
当前只有研究空间和可检验的初始假设；**无复现、无实际 GPU 结果、无 L1+ 主张、无选定论文标题**。任何测量必须先按 [EXECUTION](../EXECUTION.md) 创建 E## 实验卡；不能以复杂图形、难命名标签或普通 prompt 反例直接宣布发现 Xeno。强 baselines、负对照、同预算比较、置信区间及独立校对不可省略。

**本次方向选择：** 保持 Xeno 的大问题，优先探索**概念先验的发现偏差与无标签计算结构的解释增量**，而非选定 SAE、latent MAS、某个应用模型或新控制算法作为研究目标。每轮根据观察继续阅读文献、调整科学问题，允许彻底推翻现在的初步实验入口。状态和资源调整仍由用户决定。
