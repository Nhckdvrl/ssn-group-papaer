# Conditional Co-Ablation: Recovering Self-Repair Backups in Transformer Circuits（CoAx；arXiv 2607.01940，2026）

**阅读范围：** HTML 前约 45%（正文主要部分）。2026-10-17 精读。
## 设计与结果
- GPT-2-small IOI：3 个主 name mover 加 8 个已知 backup。CoAx 按“移除主集后，候选头的消融效应增长了多少”（Fisher 几何）排序，只需 O(|U|) 次前向。
- **结果：**
  - 识别 backup 的 AUC 0.941（最强基线 0.767）；
  - 移除主集后，backup 的直接贡献从 +0.57 升到 +1.68；
  - 主集与 backup 一起消融的效应是各自之和的 1.9 倍；
  - 在 8 个非 GPT-2 模型上都优于随机。
- **只做推理时**，不涉及训练。
## 对我们
- 推理时的 backup 识别做到了很精细。我们的 E97 已显示，“接管”的大头是损伤瞬间的推理时自修复。训练期修复在此之上**回到原配置或休眠**，这一维度是他们没有的。
