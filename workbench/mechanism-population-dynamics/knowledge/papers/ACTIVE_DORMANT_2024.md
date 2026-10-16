# Guo, Pai, Bai, Jiao, Jordan, Mei — Active-Dormant Attention Heads: Mechanistically Demystifying Extreme-Token Phenomena in LLMs（NeurIPS 2024 workshop；arXiv 2410.13835 v2）

**阅读范围：** HTML 前约 40%（正文第 1–4 节、OLMo 证据；结论与附录 B.3 / G 未读）。2026-10-17 精读。

## 设计与结果
- **玩具任务：** Bigram-Backcopy（64 个 token；遇到触发 token 时复制前一个 token）。1 层 1 头加 MLP，Adam 训练 1 万步。
- **主动—休眠机制：**
  - 在触发 token 上，头主动关注上下文；在其他 token 上，它把注意力放在 ⟨s⟩ 上，value 很小，此时“休眠”。
  - **休眠的条件是：模型不用这个头也能预测，而且加入其他 token 的 value 反而有害。**
  - Llama-2 中 L16H25 在 GitHub 文本上主动、在 Wikipedia 上休眠。
- **相互强化动力学（定理 2）：** 注意力汇的 logit 按 ½ log t 增长；value 被压低到 ∝ e^(−α)；稳定态是所有非触发 query 对 ⟨s⟩ 有几乎相同的大 logit。
- **Adam vs SGD：** 换成 SGD 去掉了残差范数尖峰，但注意力汇仍在；换成 ReLU 注意力则全部消失。
- **OLMo-7B 预训练：** 注意力汇早期迅速形成；value 范数、Δlogit 在 1 万–10 万步间约按对数变化。
- **未讨论：** 被重置的头或功能失效的头会怎样。

## 对我们的意义
- E102 中“断开连接的头被推成注意力汇”**正是这个理论的预言**：联合训练中，其他组件已经吸收了功能，模型不再需要这个头，它就进入休眠。所以这一条不能单独作为新发现。
- 我们的增量只能是：给出受控条件（何时进入休眠、何时被重新招募），并与 Schallon 的冻结手术对照（E106）。
