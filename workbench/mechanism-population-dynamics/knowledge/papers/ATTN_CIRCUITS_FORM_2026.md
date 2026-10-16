# When Do Attention Circuits Form? Developmental Trajectories of Capability and Attention-Sink Emergence Across Three 1B-Class Architectures（arXiv 2606.02378 v2，2026）

**阅读范围：** HTML 前约 90%。2026-10-17 精读。

## 设计与结果
- **模型：** Pythia-1B、OLMo-1B、OLMoE 1B-7B，每个约 10 个对数间隔的检查点；单种子。合成的 A B … A → B 序列。
- **注意力汇比例：**
  - Pythia：10.9%（6B token）→ 57.8%（300B）；
  - OLMo：0 → 80.9%；
  - OLMoE：3.5% → 75.8%。
- **induction 电路：** 6–25B token 内稳定在 3–6 个头，但成员会更替：与最终电路的 Jaccard 只有 0.29–0.33。
- **“因果退役”：** Pythia 中 3 个由 induction 转为注意力汇的头，形成时组消融 −10.2 pp，终点 +0.3 pp（z = +1.0）；OLMoE 中 1 个类似。保持 duplicate-token 角色的头仍然重要（−3.1 到 −4.0 pp），但只在 OLMoE 中看到。
- **局限：** 只有 4 个“退役”头；单种子；合成数据；低基线（4–5% top-1）；没有重置等干预。

## 对我们的意义
- 正常预训练中，失去作用的头会变成注意力汇（自然版本的“空操作化”）；induction 电路成员会更替（与 Tigges 2024 一致）。
- 我们提供的是受控干预版本：可以决定哪个头失去耦合，并观察它的去向。
