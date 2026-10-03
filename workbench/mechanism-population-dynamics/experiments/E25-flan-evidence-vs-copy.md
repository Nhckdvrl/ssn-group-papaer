# E25 — Does ~1–2% instruction data (Flan) set reliance on in-context evidence, not verbatim copying?（2026-10-03）

- **状态：** DONE（2026-10-03；留出 seed 上三条判据全部成立）。原状态：REGISTERED（**假设形成于查看 default seed 之后**（见 logs/2026-10-03.md）；验证只用尚未计算的 4 个模型：dolma1_7 与 dolma1_7-no-flan 的 large-aux-2、large-aux-3。登记时这 4 个结果不存在）
- **类型：** PILOT（held-out seed 验证）
- **对应：** E20（default seed 描述：Flan 去除使 Coherent 冲突 6 类全部下降 1.2–5.2 nats，Substitution 平均约 1.0）；Goyal et al. ICLR 2025（指令微调与上下文依赖）；Kim et al. 2025
- **阳性对照：** 无需新增；clean 边际（知识）在两配方间差异应小（|Δ| < 1 nat 平均），否则效应可能来自知识差异
- **噪声地板：** E20 中其他配方的 3 seed 合并配方内 SD（Coherent 均值、Substitution 均值分别计算）
- **问题（只回答这个）：** 在未看过的 seed 上，去掉 Flan 是否主要降低“依据上下文证据作答”（Coherent 冲突），而不是“逐字复制”（Substitution 冲突）？

## 读数
- Coh = 6 个类别 Coherent 冲突采信边际的平均；Sub = 6 个类别 Substitution 冲突的平均；K = clean 边际平均。
- Δcoh = mean_aux Coh(dolma1_7) − mean_aux Coh(no_flan)；Δsub 同理（mean_aux = large-aux-2 与 large-aux-3 的平均）。
- SE = 合并配方内 seed SD × √(1/2 + 1/2)（用除这两个配方外、3 seed 齐全的配方估计）。

## 判据
- **证据依赖效应复现：** Δcoh ≥ 1.0 nat 且 Δcoh > 2·SE_coh，且 4 个交叉配对（dolma aux × no-flan aux）的 Coh 差全部 > 0。
- **特异于证据整合：** 在上一条成立时，Δcoh − Δsub ≥ 0.5 nat 且 Δsub < 2·SE_sub 或 Δsub < Δcoh/2。
- **知识混杂排除：** |ΔK| < 1 nat。
- 不成立 → 记为 default seed 上的偶然差异，不再追加条件。

## 补充（2026-10-03 02:00，有效性审计；4 个留出模型结果仍不存在）
1. **条目集合混杂：** E20 的 `margin` 在每个模型各自“已知”的条目上平均，两配方已知集合不同。**主读数改为共同条目版本**：Coh / Sub 只在 dolma1_7 与 no_flan 全部 seed（6 个模型）都已知的条目上，用 `margin_all_items` 计算；原 `margin` 版本只报告。判据阈值不变。
2. **解释范围：** Coherent 段落多次重复干扰答案，Substitution 只出现一次。E25 只能确立“Coherent 型上下文的效应”；把它归为“证据整合”而非“上下文中出现次数 / 篇幅”需要因子化实验（E26：同一干扰答案 × 出现次数 1/2/4 × 有无支持性论述 × 篇幅匹配的无关填充）。E25 结论中不使用“证据整合”一词，除非 E26 支持。

---
## 结果（`results/e25/analysis_{shared,own}.json`；2026-10-03 04:30）
| 读数 | Δcoh | Δsub | ΔK | 合并 seed SD（coh / sub / K；14 配方） | 交叉配对 Coh 差 |
|---|---|---|---|---|---|
| **共同已知条目（主）** | **+1.65** | +0.73 | +0.03 | 0.53 / 0.88 / 0.21 | 1.12 / 2.12 / 1.19 / 2.18 |
| 各自已知条目 | +1.65 | +0.73 | +0.03 | 0.52 / 0.87 / 0.21 | 1.15 / 2.05 / 1.25 / 2.14 |
- **判定：三条全部成立。** Coherent 型冲突的 Flan 效应在留出 seed 上复现（1.65 ≥ 1.0 且 > 2·SE = 1.05，4 个交叉配对全 > 0）；Substitution 效应不显著（0.73 < 2·SE = 1.76）；知识强度无差（0.03）。
- **限定（补充 2）：** 结论只到“Coherent 型上下文（问答格式 + 2–4 次提及 + 长段落）”；归因见 E26。
