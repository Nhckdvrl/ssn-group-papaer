# E05 — 错误检索的收益是否仅由难度/长度/类型重配解释（2026-10-02）

- **状态：** DONE（运行前设计已冻结；单训练种子，按决策表停止扩种子）
- **类型：** EXPLORE；E04 第一个 seed 在 held-out280 上较原静态多 16 题，复种子进行中。
- **对应：** I02、P03、E04。
- **问题：** E04 的训练收益是错误题的词面相似度携带了决策信息，还是因为检索集恰好更难、更长、覆盖不同类型？
- **解释区分：** 构造同 120 题、逐条匹配 E04 检索集的 `(level,type)` 和总字符长度，但在该格内不看学生错误、从剩余真值训练池取最近长度题。与 E04 在相同 parent/seed/预算下对比训练后收益。
- **设置：** 复用 E00/E04 锁定的 Gemma2-2B-IT revision、官方 prompt/scorer、开发切片、LoRA 超参。候选是排除 1740 dev/5000 test 题面 hash 的 MATH train，额外排除 E04 检索的 120 条；每个目标按 `(level,type)` 找未用候选中 `abs(log1p(problem+response chars)_candidate - log1p(... )_target)` 最小者，固定平局按 `record_id` 排序。绝不依照模型错误或检索相似度挑 control。
- **读数：** 280 道未用于 feedback 的题上严格正确率，以及配对的 matched-minus-retrieval、matched-minus-static17；352 全集仅辅助。报告数据中 level/type 完全一致、平均字符数与训练监督 token 差异，以及它对反馈题的 TF-IDF 相似度（后验诊断）。
- **阳性对照：** E04 检索数据相对 base 的可学性、训练 hash 与 eval 题零精确重复；若 E05 control 学不动，则首先查标签/截断/训练代码。
- **噪声地板 + MIE：** E00 静态三 seed 在 held-out280 的 48/53/58 题给出粗略种子范围。先做配对 seed17；若 matched 与 retrieval 差至少 5pp 且 E04 复种子同向，再决定是否做 seed29/43；差距更小视为“简单分布变量足以吸收”的优先解释，而不是显著性裁决。
- **混杂审计：** 标签来源、120 条、epoch、更新步、父模型、optimizer reset、prompt、解码和 held-out 一致；字符长度是 token 的粗代理，训练 token 仍可能不同。排除检索样本本身可能改变数据质量；本卡不证明因果机制，只决定继续挖的方向。
- **决策表（跑之前写）：** matched 追平检索 → 优先研究覆盖/难度/长度、廉价静态配方与数据动作成本，不造复杂错误反馈方法；检索跨 seed 稳定优于 matched ≥5pp → 检验相似度/模板/近重复与新 learner state 的可迁移性；两者都不稳定 → 暂不升级主张，换更高分辨率/更强任务设置。
- **算力预算：** 首轮 1 训练 + 1 评测 ≤0.2 GPU·时；必要时再 2 训练种子。CPU 选数单次、API 0。**实际：** 待填。

## 结果（2026-10-02）

- 120 条 control 与 retrieval 的 `(level,type)` 逐条相同，平均题目+解答字符数 849.3 对 852.1，平均绝对长度差 8.54 字符，无相同训练题。实际监督 token/epoch 却为 **30,274 对 28,105**（+7.7%）；字符匹配不是 token 匹配。见 [`results/E05_matched_manifest.json`](../results/E05_matched_manifest.json)。
- 原先统一 few-shot＋格式的 held-out280：static17 **48/280**、retrieval17 **64/280**、matched17 **58/280**。matched－retrieval 为 −6/280 = −2.14pp，逐题 bootstrap 95% 区间 [−6.07,+1.79]pp；matched－static 为 +10/280 = +3.57pp。全 352 题 matched 79/352，retrieval 81/352，static 66/352。见 [`results/E05_dev_analysis.json`](../results/E05_dev_analysis.json)。
- 看到 E04/E05 结果后做的 **POST-HOC 提示审计**：统一 zero-shot＋格式的 held-out280 则 static17 55、retrieval17 60、matched17 58；matched－retrieval 仅 −2/280 = −0.71pp。全 352 题为 73/77/75。见 [`results/E00_E04_E05_zero_format_analysis.json`](../results/E00_E04_E05_zero_format_analysis.json)。不能挑前一个更大差值当方法结果。
- 训练 wall 105.8s，352 题评估 wall 116.8s（few-shot）和 74.7s（zero-shot），合计约 0.083 GPU·时；API 0。原始文件外部缓存 `runs/e05/`。
- **按决策表：** 在唯一已跑的配对 seed 上，匹配题型/难度/长度后检索优势小于预设 5pp，且 E04 复种子本身没有稳定大优势；不扩 E05 的 29/43 seed。当前最节约的解释是粗分布重配及提示协议影响较大，但单 seed 和 token 不完全匹配不能证明已解释全部。C03 仍 **L0**；下一步应换更有行动差异的强生成/选择方法或学生状态，而不是围绕此 6 题差距继续局部优化。
