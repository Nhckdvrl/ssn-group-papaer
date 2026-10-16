# Rushing & Nanda — Explorations of Self-Repair in Language Models（ICML 2024；arXiv 2402.15390 v2）

**阅读范围：** HTML 全文。2026-10-17 精读。

## 设计与结果
- **定义：** 自修复 = Δlogit − ΔDE（被消融组件的直接效应损失中由下游补回的部分）；主要用重采样消融。模型：Pythia-160M / 410M / 1B、GPT-2 S / M、Llama-7B，各 1M token 的 Pile。
- **结果：**
  - 自修复普遍但不完全，主要在后层，逐头差异大。
  - 机制一：最终 LayerNorm 的缩放，平均约解释 30%。
  - 机制二：稀疏的“反擦除”神经元。
- **迭代推理假说：** 支持证据是自我压制的头、backup name mover。**反证：previous-token 头与 induction 头没有自修复。**
- **局限：** 只测直接效应；只用训练完成的模型（不看训练过程）；大部分自修复未被解释。

## 五个透镜
- **Failure case：** 推理时，previous-token / induction 头没有自修复；而我们在继续训练中看到 previous-token 角色被修复（E96：替补被放大，原头在有接口时回归）。训练期修复与推理时自修复是两种机制，前者覆盖了后者不覆盖的头。
- **对我们的意义：** E97 中“接管的大头是损伤瞬间的推理时自修复”与本文一致；E96 / E101 中训练期修复回到原配置，是本文没有的维度。
