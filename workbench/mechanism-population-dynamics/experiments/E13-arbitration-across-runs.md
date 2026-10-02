# E13 — Is context-vs-memory arbitration reproducible across independent runs?（2026-10-02）

- **状态：** RUNNING（冻结于运行前；canonical 冒烟后补充次要读数）
- **类型：** PILOT（第二机制：检验 F1“电路可复现、使用策略 run 特异”是否超出 induction）
- **对应：** C01、C02；Yu, Merullo, Pavlick 2023（记忆头 / 上下文头、单头缩放可控采信）；Fouilhé et al. 2026（31 模型复现，代码 `gfouilhe/IC-factual-public`）
- **阳性对照：** canonical `pythia-410m` 应复现 Yu 2023 / Fouilhé 2026 报告的方向（实体越常见，越倾向记忆答案）
- **噪声地板 + MIE：** 每个 seed 的采信率用国家级 bootstrap 给 CI；实验单位 = seed（n=10）；MIE = seed 间采信率极差 ≥ 15 个百分点（≥ 3× 国家级 bootstrap 半宽）
- **决策表（跑之前写）：** 见下方
- **问题（只回答这个）：** 在 410M 的 10 个独立 run 中，(1) 对“确实记得”的事实，模型采信上下文反事实的比例在 run 之间是否显著不同（自然文本 loss 相同）？(2) 记忆头 / 上下文头这一角色结构是否在每个 run 中都存在、位于相近的层？(3) 若采信率不同，差异是来自角色成分的有无，还是来自成分的增益？

## 设置
- 模型：`pythia-410m` + `seed1..9`，step 143000（R0 审计后使用）。
- 数据：ParaConflict World Capital（218 条），Yu 2023 原模板 `The capital of {country} is {distractor}. Q: What is the capital of {country}? A:`；每个国家抽 20 个干扰首都（固定种子）。
- **已知集合：** 干净提示 `Q: What is the capital of {country}? A:` 下，正确首都的 log-prob 高于全部 20 个干扰首都的国家。
- **读数：** 采信率 = 已知集合上，反事实提示中干扰首都 log-prob > 正确首都 log-prob 的比例（Fouilhé 的 lp 判定）。
- **角色：** 按 Yu 2023 的 head attribution：每个头在最后位置对（正确 − 干扰）logit 差的直接贡献；记忆头 = 贡献最正，上下文头 = 贡献最负；报告每个 seed 的 top-3 及其层。
- **次要读数（2026-10-02 补充：canonical 冒烟显示采信率 94%，接近天花板；在任何 seed 运行前加入）：** 记忆边际 = 已知集上 mean[lp(正确) − lp(干扰)]（连续、无天花板），国家级 bootstrap CI；判据同主读数，但以“seed 间极差 ≥ 3× bootstrap 半宽”衡量。
- **混杂控制（2026-10-02，seed 运行前预注册）：** 各 seed 的已知集合不同；主比较同时在“所有 seed 已知集合的交集”上计算采信率与记忆边际（需要每个国家的逐条结果，脚本保存 per-country 数组）。
- **增益检验：** 每个 seed 把各自的 top-1 记忆头输出缩放 ×{0, 0.5, 2}，测采信率变化（Yu 的干预）。

## H_support 的第二机制检验（2026-10-02 预注册；此时只看到 canonical 与 seed1 两个 run 的汇总数）
- 国家频率 = pile-10k 原始文本中国家名的出现次数（字符串计数，大小写敏感）。按频率三等分（只用所有 seed 已知集合的交集）。
- 读数：每个国家的记忆边际在 10 个 seed 间的 SD；Spearman(国家频率, 跨 seed SD)。
- 预测：低频三分位的跨 seed SD > 高频三分位，且 Spearman < 0（p < 0.05）。不成立 → H_support 不跨机制，只写在 induction 门控上。

## 决策表
- **F1 推广成立：** 采信率 seed 间极差 ≥15 pp 且 CI 不重叠，而 (2) 角色结构 ≥9/10 seed 存在、层位置可复现 → “电路可复现、仲裁策略 run 特异”跨机制成立；进一步检验差异是否落在增益上（3）。
- **仲裁策略也可复现：** 采信率极差 <15 pp → F1 是 induction 特有的（或 70M 小容量特有的）；主线收缩为 induction 门控 + 机制可复现层级。
- **角色结构本身不可复现：** <7/10 seed 有清晰记忆头 → 该机制在 410M 不是稳定对象，结论只写“不可判定”。
