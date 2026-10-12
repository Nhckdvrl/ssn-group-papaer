# E132：哪些跨来源交互让模型分得清两条规则？（2026-10-13）

- **状态：** RUNNING（跑前写定，结果追加在下方）
- **对应：** 论文 §5「完全隔离使规则无法区分」的机制解释；回应两份模拟审稿意见：GPT W2/W3/建议1，Claude W2/W7。
- **问题（一句话）：** 完全切断跨来源 formation 后，冲突约定下准确率降到随机水平。是哪一类跨来源边（对方的名字、评论、答案）让模型能把规则对应到来源？标签词泄漏取决于"是否共享"，还是取决于 no/yes 这对特定词？

## 设置

沿用 E123 的 SST-5 引擎：token 流与 E123 逐字相同，世界构造、gold、query 方式都不变；材料是新的种子。

**命名空间（4 种）**

| 名称 | A 的标签词 | B 的标签词 |
|---|---|---|
| shared | no/yes | no/yes |
| far | no/yes | pass/flag |
| shared_pf | pass/flag | pass/flag |
| far_swap | pass/flag | no/yes |

**formation 政策**

- normal
- answer_cross_off：选择性阻断，与 E123 相同。
- all_cross_off：完全隔离，与 E123 相同。
- iso_names：完全隔离，但允许看对方的 `Annotator: name` token。
- iso_comments：完全隔离，但允许看对方的 `Comment: ...` token。
- iso_answers：完全隔离，但允许看对方的答案 token。
- no_answer_senders：只阻断对方的答案 token 被任何本源 token 看到。

**覆盖范围**

- shared 和 far 跑全部 7 种政策。
- shared_pf 和 far_swap 只跑 normal、answer_cross_off、all_cross_off。
- shared 另跑分层带实验：把选择性阻断只施加在第 k 个四分之一层段（k=0..3），只用 A-only 读取。
- 世界：origin（相反约定）、cross（相同约定）、within（类内交换对照）。读取范围：native 与 gate（只读被询问来源）。

**注意力权重读数**

shared 和 far 的 normal origin 预填充中记录：A 的标签位置（标签词首 token）在每层、按 head 平均后，分给各类较早 token 的注意力质量：B 答案（与本标签同词/异词）、A 答案（同词/异词）、B 名字、B 评论。

**模型与材料**

- Qwen3-8B/14B、Mistral-7B-v0.3、Llama-3.1-8B：先跑 discovery n16（seed 132001），再跑 confirmation n32（seed 132101）。
- Qwen3-32B、Llama-3.1-70B：只跑 confirmation n32，只用 shared 和 far，政策取 normal/answer/all/iso_names/iso_comments/iso_answers，世界取 origin/cross，跑 native 和 gate，并记录注意力。

**执行约定**

- FP32、eager、权重冻结。
- 冻结读数在跑前确定，以下列出。discovery 和 confirmation 同时启动；没有任何读数或条件会因看到 discovery 结果而改变。

## 冻结读数

1. 准确率（全词表 argmax）：按政策 × 命名空间 × 读取范围，分 both / A / B / opposite / same，并记录"答成另一来源的词"的比例。
   - **主对比 1**：iso_X − all_cross_off。shared 看 opposite 世界的准确率，far 看 full-vocabulary 准确率。
2. Δ = ½E[g_A(z_cross − z_origin)]，含 signed 和 |D_c|。
   - **主对比 2**：gate 下 shared_pf 对比 far_swap，看是否复现 shared 对比 far 的模式。
   - 另报 A 预测翻转率：origin 对 cross 的翻转，与 origin 对 within 的翻转（对照）比较。
3. 分层带：gate 下第 k 段阻断带来的 Δ 减少量。
4. 注意力质量：shared 对比 far，同词对比异词。

## 阳性对照与噪声

- 数值检查：缓存与全序列打分的差 ≤1e-3。
- 自检：E123 对应条件（normal / answer / all 三种政策）在本引擎里可重复，与 E123 发现批同样本构造的差异另外核对。
- bootstrap 以 prompt 为单位，10000 次。

## 决策表

| 结果 | 更新 |
|---|---|
| 名字边恢复区分而评论边不恢复 | 来源区分依赖名字之间的交互；上下文长度无法解释，因为评论边提供的 token 远多于名字边 |
| 答案边恢复 | 答案同时携带有害泄漏和有用的来源-词空间信息，论文如实写出这种二重性 |
| 都不单独恢复 | 区分需要多类边共同作用，如实报告 |
| shared_pf/far_swap 复现 shared/far 模式 | "共享"本身是关键，与 no/yes 的语义无关 |

## 算力

夜间可用全部空闲卡。fvcrc21/20 跑 4 个小模型（discovery 与 confirmation 并行）；fvcrc10/11/13 跑 70B confirmation（按 context 分三片）；fvcrc15/12 跑 32B confirmation（分两片）。

## 结果（运行后追加，2026-10-13）

discovery 与 confirmation 方向一致；完整数字见 `results/e132/*/analysis.json`、论文附录 I 和 `paper/figures/numbers.json`。数值误差全部 ≤2e-5。

**确认批（n32），已完成的模型**

| 模型 | shared 冲突约定：隔离 → +名字 / +评论 / +答案（native） | far 全词表：隔离 → +名字 / +评论 / +答案 | Δ(gate)：shared / far / shared_pf / far_swap |
|---|---|---|---|
| Mistral-7B | 52.1 → 70.9 / 51.6 / 53.3（71.3） | 52.4 → 86.6 / 51.7 / 61.1 | .52 / .00 / .58 / .07 |
| Llama-3.1-8B | 51.2 → 69.5 / 54.3 / 52.5（58.8） | 53.9 → 82.3 / 60.0 / 53.9 | .61 / .01 / .50 / .04 |

**结论**

- 名字边单独就能恢复大部分区分能力；评论边虽然 token 多得多，几乎不起作用。这否定了"上下文变短"这一解释。
- 泄漏取决于标签词是否共享，与具体是哪组词无关。
- 分层带上，路径作用集中在前半网络。
- 共享标签词时，A 的标签位置给 B 答案的注意力质量更高（+0.9 到 +1.3 个百分点，CI 不跨 0）。

其余模型（Qwen3-8B/14B/32B、Llama-3.1-70B、Gemma-2-2B）完成后补入下表与论文。

### 全部 8 个模型确认完成（2026-10-13 08:45）

- **名字边：** 冲突约定下准确率从 49–53% 恢复到 67–88%（5/8 个模型超过原生水平）；分离词时全词表准确率从 50–56% 恢复到 82–96%。
- **评论边、答案边：** 52–62%，几乎不恢复。
- **词角色对调：** shared_pf 的 Δ 为 0.39–1.01，far_swap 为 0.04–0.10。
- **分层带：** 6 个模型都是第二个四分之一层段贡献最大，最后一段为零。
- **注意力：** 共享标签词时 A 标签位置给 B 答案的注意力质量高 0.3–2.3 个百分点，8 个模型 CI 都不跨 0。

已全部写入论文 §3/§4.2/§5、Figure 1/4 和附录 I。
