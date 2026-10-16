# McGrath, Rahtz, Kramár, Mikulik, Legg — The Hydra Effect: Emergent Self-repair in Language Model Computations（arXiv 2307.15771）

**阅读范围：** HTML 全文。2026-10-17 精读。
## 设计与结果
- **设置：** Chinchilla 族 7B（32 层，**训练时无 dropout**），Counterfact 事实回忆，1,209 个上下文，重采样消融整层。
- **结果：**
  - 消融一个注意力层后，下游某个注意力层增大直接效应以补偿；第 23 层上，补偿解释了直接效应变化方差的 92%；补偿斜率在第 13 层之后都 < 1。
  - 中间层的 Hydra 效应加上后层 MLP“擦除”的减弱，共恢复约 70% 的 logit 损失。
  - 后层 MLP 压低最可能的 token（擦除）。
- **结论：** 消融式重要性会低估组件；自修复不需要 dropout。
- **局限：** 整层粒度、单模型、单数据集。
## 对我们
- 推理时自修复的经典来源。E97：损伤瞬间的再分配与此一致；训练期的修复是另一回事。
