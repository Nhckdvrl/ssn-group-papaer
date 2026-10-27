# 计算分担、表征稳定与专家合作：全文复核（2026-10-27）`[证据级别：全文]`

来源：[Sparsity Moves Computation v2](https://arxiv.org/abs/2605.09403v2) 33页；[Beyond Routing v1](https://arxiv.org/abs/2605.20610v1) 21页；[Basic-Refinement，ACL 2025 Main](https://aclanthology.org/2025.acl-long.1093/) 16页。root完整阅读正文、附录、参考和图表文字，前两篇关键图另查看PDF渲染；第三篇Terra也独立全文核接口。PDF/文本留NFS，SHA与覆盖见[阅读manifest](../../../workbench/mechanism-population-dynamics/moe/notes/PRIMARY_READING_2026-10-27.json)。未执行作者代码；预印本后续录用/评分未核对。

| 模板项目 | Sparsity Moves Computation | Beyond Routing | Basic-Refinement |
|---|---|---|---|
| 1. 论文形态 | 受控机制实验 | 构念与跨实例测量 | 跨层归因与推理干预 |
| 2. 背景压力 | FFN设计会改变attention学到的计算 | routing难以刻画专家编码 | 动态专家交互难以用dense归因解释 |
| 3. 改变前提 | 分开active width、稀疏分配和router学习 | 直接读expert表示与连续特征 | 将shared/routed及head联系起来 |
| 4. idea来源（DOCUMENTED） | Behrens 2024计数策略；Nanda 2023算法；Zuo 2021随机专家 | Pavlitska 2023、LIMoE 2022与视觉神经科学工具 | Geva 2022、Yu 2024归因及DeepSeekMoE共享结构 |
| 5. 近邻距离（由作者论证） | 从随机路由性能到attention–FFN实际分担 | 从routing类别到MEI、行为维度和二阶RSA | 从dense神经元归因到加门权的专家归因与组合干预 |
| 6. 对象/证据 | 单层3算法任务，通常5seed；移除/patch/probe；narrow/random/top2控制 | 约46M CNN、3个E配置、约10独立实例/配置；STL10→THINGS | 3 MoE+3 dense、12 LRE关系；HIT/MRR；shared/top-k、阻断、head抑制和expert强制 |
| 7. 强度/未核对 | 有真实干预；结构改变与history改变是不同对象；冻结随机模块仍存在 | 稳定性是强制expert读出的RDM结构；没有以此直接证明下游因果职责 | 有真实任务干预；局部残差归因另列；前向层范围/归一化细节未明确，数字冲突另存 |
| 8. 可迁移动作 | 将架构可实现性、训练后的依赖和替代路径分开 | 同时比较单体调谐与总体几何，避免把编号当对应 | 在同一成功任务上测shared/routed合作与实际预测 |
| 9. 对我们的作用 | 固定架构与active k后的历史分担，是自然下一层问题 | 保留跨初始化的稳定motif可能，另直接测实际依赖/重用 | 把既有合作解释推进到同谱系历史可变性与跨来源函数重组 |

**全文后应修正的具体理解：** Beyond Routing的E=4/8最优为2簇，E=16的Fig.S3/S4为3簇，不能把所有配置说成严格二分；方法还说明3 exemplar加30个独立训练，具体所用checkpoint未逐项核对。Sparsity的“某一模块冻结”仍保留该随机模块，其App.G/H自己区分了这种可解性与移除后的替代性。Basic-Refinement的表2有shared+top1保留大部分任务表现的实测；一般shared/routed合作已有直接先例，不应被简化成相关性。其整网/局部读出边界及原表数字见[接口报告](../../../workbench/mechanism-population-dynamics/moe/results/basic_refinement_full_reading_2026-10-27.json)。

**我们自己的研究判断：** 架构提供可用路径，任务给出预测要求，学习历史选择实际分担与配套。E155同一44个成功决策中的逐题转移，更符合新增共同依赖而非简单R→S替代；E156固定成熟父接收者，进一步检验哪些函数能够携带有用的任务计算与选择部署性质。这里的正面目标是识别可重复/可重用的合作整体。输入CI不替代独立初始化总体，邻近工作也不构成贡献上限；下一步由真实来源矩阵决定，不因发现先例改线。
