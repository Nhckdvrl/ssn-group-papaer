# Li, Yosinski, Clune, Lipson, Hopcroft — Convergent Learning: Do Different Neural Networks Learn the Same Representations?（ICLR 2016；arXiv 1511.07543）

**阅读范围：** ar5iv 全文。2026-10-17 精读。

## 设计与结果
- **设置：** 4 个不同初始化的 AlexNet 式网络（ImageNet，top-1 58.65–58.84%）。
- **匹配方法：** 单元激活相关；一对一（二分匹配）、多对一、稀疏少对一（L1 线性映射）、多对多（谱聚类）。
- **结果：**
  - 没有相关 > 0.5 伙伴的单元比例：conv1 17%、conv2 37%、conv3 63%、conv4 92%、conv5 75%。
  - 有些特征被可靠学到，有些没有。
  - 单元张成的低维子空间在网络之间共享，具体基向量不同。
- **结论：** 局部码与轻度分布式码混合。

## 对我们
- 这是“单元层面不对应、子空间层面对应”这一模式最早的系统证据。我们的 E89 是功能层面（因果效应 + 多任务分工）的类似问题，在 LM 的注意力头上。
