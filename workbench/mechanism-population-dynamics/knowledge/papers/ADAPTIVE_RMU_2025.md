# Dang et al. — On Effects of Steering Latent Representation for LLM Unlearning（Adaptive RMU；AAAI 2025；arXiv 2408.06223 v3）

**阅读范围：** HTML 全文。2026-10-17 精读。
## 设计与结果
- **RMU：** 在第 l 层把遗忘输入的表示推向固定的随机向量 c·u，同时保持保留输入的表示不变。理论上，这会让 logit 方差变大、置信度下降（近似推导）。
- **为什么中后层失效：** 中后层原表示范数大于 c，遗忘损失不收敛（Zephyr 第 11–31 层弱）。
- **Adaptive RMU：** 把 c 改成 β·‖h(x)‖（β = 5）。
  - Zephyr 第 7 层：WMDP-Bio 63.7 → 23.7，Cyber 43.5 → 26.5，MMLU 58.1 → 55.0。
  - Mistral 第 20 / 31 层仍然失效（Bio 45.7 / 66.0）。
  - 使用领域内保留集时几乎无效。
- **局限：** β 手调；只有白盒攻击的理论论证。
## 对我们
- 表示误导类遗忘作用在中间层表示上（写入残差流的内容），按我们的规律应当较难被重学——与 Deeb & Roger 中 RMU 仍可恢复 88% 的结果需要对照，是 E105 下一步的候选方法。
