# Fan et al. — Towards LLM Unlearning Resilient to Relearning Attacks: A Sharpness-Aware Minimization Perspective and Beyond（arXiv 2502.05374）

**阅读范围：** HTML 正文（约 95%）。2026-10-17 精读。
## 设计与结果
- **设置：** WMDP（Zephyr-7B、Llama-3-8B）、MUSE；以 NPO 为主，另有 GradDiff、RMU、TAR 等。
- **SAM：** 遗忘写成 min-max：内层找半径 ρ = 0.01 内最能撤销遗忘的权重扰动，外层在该点最小化遗忘损失；理论上等价于压低遗忘损失的曲率（更平坦 → 更抗重学）。
- **结果：**
  - 20 样本重学攻击下，NPO + SAM 的遗忘效果保持约 0.70，NPO 降到 0.57；3 轮攻击后分别为 0.59 与 0.37。
  - TAR 达到类似效果，但耗时约 7,442 分钟，NPO + SAM 只需 11.5 分钟。
- **组件分析：** RMU 只改第 5–7 层；对第 1–7 层施加 SAM 比只对第 5–7 层更鲁棒。他们把 RMU 的脆弱归因于“只改部分层，而攻击可以改整个模型”。
## 对我们
- 他们从优化几何（平坦度）解释抗重学；我们从组件接口解释。两者可能互补：只改读出侧参数（QK）的遗忘，可能恰好落在一个“尖锐、一推就回”的方向上。可检验——测 QK 式与 OV 式遗忘点的曲率。
