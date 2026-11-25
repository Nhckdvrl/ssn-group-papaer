# E134：rebuttal 补充对照（SST-5）——匹配边数/注意力量的阻断、不归一化阻断、无上下文的名字、分组排列、注意力 2×2（2026-11-25）

- **状态：** RUNNING（跑前写定）
- **对应：** ARR 审稿意见（Submission 7986）。Lcz2-W1（阻断后重新归一化、需要匹配边数/注意力量的对照）；Lcz2-W2（名字 token 的状态含有之前评论的信息）；AZuR-W3（简单基线：每位标注者的样例放在一块）；nsWy-W3（路径上的计算原理）。只回答审稿人明确提出的问题，属于对已有实验（E132）的小补充。
- **材料：** 与 E132 确认批次完全相同（`make_contexts(seed=132101, validation)`，32 个 prompt，SST-5 两极），token 流与 E132 逐字相同；世界只用 origin / cross。
- **模型：** Qwen3-8B、Qwen3-14B、Mistral-7B-v0.3、Llama-3.1-8B、Gemma-2-2B、Gemma-2-9B（与论文同一 revision）；FP32、eager；新环境 `~/.venvs/ices-tf457`（torch 2.8.0、transformers 4.57.6，与论文相同版本；原 verl-clean 已不存在）。
- **环境复核：** normal / answer_cross_off / all_cross_off / iso_names 四个政策与 E132 确认批次逐条比较，最大 |Δz| 应 ≤ 1e-3（同一 prompt 同一模型）。不过则先查环境再看结果。

## 条件（formation 政策；每个都测 native 与 A-only 读取，两个来源，两个世界）

| 名称 | 说明 | 回答 |
|---|---|---|
| normal、answer_cross_off、all_cross_off、iso_names | 同 E132 | 基线 + 复核 |
| matched_count | 每个标签位置屏蔽与“对方答案 token 数”相同数量的对方**评论** token（随机，固定种子） | Lcz2-W1 |
| matched_mass | 每个标签位置屏蔽对方的非答案、非名字 token，按原生注意力（层、头平均）从高到低选，直到屏蔽的注意力量 ≥ 对方答案的注意力量 | Lcz2-W1 |
| answer_norenorm | 选择性阻断改为 softmax 之后把对方答案的权重置零、**不重新归一化**（输出 = 原生权重下其余 token 的加权和） | Lcz2-W1 |
| all_cross_off_cf、iso_names_cf | 所有名字 token（`\nAnnotator: X`）只能看开头说明和自己这段名字，不能看任何评论、答案、其他名字；在此基础上完全隔离 / 只重开对方名字 | Lcz2-W2 |
| all_cross_off_cl、iso_names_cl | 同上，但名字 token 还能看本条 demo 自己的评论（不能看之前任何 demo）。冒烟测试（2 个 prompt）中 cf 的名字增益消失，跑前加入此中间条件，用来区分名字状态需要的是“本条评论”还是“之前的 demo” | Lcz2-W2 |
| grouped_AB、grouped_BA | 两个来源各自 8 条按原相对顺序放成一块（A 在前 / B 在前），normal 与 answer_cross_off | AZuR-W3 |

命名空间：shared（都用 no/yes）跑全部；far（B 用 pass/flag）跑 normal、answer_cross_off、all_cross_off、iso_names、all_cross_off_cf、iso_names_cf、grouped normal。

**注意力 2×2（nsWy-W3）：** origin 与 cross 两个世界的原生 prompt，A 的标签位置对 B 答案词 token 的注意力（层、头平均，按 token 平均），按“B 的答案词与 A 这条的答案词是否相同”×“B 的评论与 A 的评论是否同一情感类”分 4 格。opposite 世界里同词 = 异类，same 世界里同词 = 同类，两个世界合起来给出 4 格。

## 读数
- 准确率（全词表 argmax，两个来源、两个世界平均；冲突世界单列）；Δ（A-only 读取下 B 约定对 A 的拉力，nats）。
- 每个政策实际屏蔽的注意力量（A 标签位置的原生注意力中被屏蔽的比例）。
- 按 prompt bootstrap 95% CI。

## 判定（跑前写定）
- **Lcz2-W1：** 若 matched_count 与 matched_mass 的 Δ 减少量都明显小于 answer_cross_off（差的 CI 不含 0，≥ 4/6 模型），且准确率提升也小于 answer_cross_off → 效果是答案→标签路径特有的，不是“删掉同样多的边/注意力”造成的。若 matched_mass 与 answer_cross_off 相当 → 路径特异性的主张要降级，回复里如实说明。answer_norenorm：若 Δ 减少与准确率提升和 answer_cross_off 同向且量级相近 → 结论不依赖重新归一化。
- **Lcz2-W2：** iso_names_cf − all_cross_off_cf（冲突世界准确率、separate words 的全词表准确率）若保留 iso_names − all_cross_off 的大部分（≥ 一半，多数模型）→ 名字本身（不带之前评论的信息）就足以分开规则；若大幅下降 → 改写为“名字位置（含其汇集的上下文）”，回复里如实说明。
- **AZuR-W3：** grouped 的原生准确率与 A-only 读取下的 Δ 如实报告；若分组仍有 Δ > 0 且准确率低于单来源上限 → 分组不能替代；若分组接近单来源上限 → 在回复中承认它是一个简单有效的提示层面做法，并与换词一起写进讨论。
- **nsWy-W3：** 只描述 2×2 的结果，不预设方向；用来说明标签位置按“类相似”还是按“词相同”检索之前的答案。

## 算力
每个 8B 模型约 0.5–1 GPU 小时；6 个模型共约 5 GPU 小时，fvcrc21 / fvcrc11 空闲卡。

## 结果（2026-11-25，6 模型 × 32 确认 prompt；`results/e134/*_confirmation/analysis.json`，汇总 `scripts/rebuttal_summary.py`）
- **复核：** 与 E132 同条件逐条比较，6 模型最大 |Δz| ≤ 2e-4（Qwen3-8B、Llama、Gemma-2-2B 完全一致）。
- **Lcz2-W1 匹配对照：** 匹配注意力量的屏蔽去掉的注意力与选择性阻断相当（4.2–5.7% vs 4.2–8.2%），但 A-only Δ 基本不变（Q8 0.63→0.61；选择性阻断 →0.24），准确率不变；选择性阻断 − 匹配注意力量：准确率 +4.4 – +10.6 点、Δ 减少多 0.09–0.48 nats，6/6 CI 不含 0。匹配边数同样无效。**不重新归一化：** Δ 减少与选择性阻断相当或更大（6/6），准确率比原生高 1.5–15.3 点（5/6），Gemma-2-2B 降 8.1 点。→ 按判定表：效果是答案→标签路径特有的，结论不依赖重新归一化（Gemma-2-2B 的准确率除外）。
- **Lcz2-W2 名字：** 名字只看自身（cf）或只看本条评论（cl）后，重开对方名字的增益消失（冲突世界 −0.8 – +2.3 点，对照原设定 +15.6 – +32.8 点；换词全词表同样）。→ 按判定表改写：起分离作用的是对方名字位置上汇集的、该来源之前 demo 的信息（来源身份与其 demo 绑定在名字位置），不是名字 token 本身。论文 §5 的说法要相应收窄。
- **AZuR-W3 分组：** A 在前时 A 的 Δ 按构造为 0；B 在前时 A 的 Δ 约为交错时的两倍（1.04–1.77 vs 0.52–0.86）。原生准确率比交错高 0–3.6 点（冲突世界 −3.8 – +7 点），低于交错 + 选择性阻断（89.4–97.1%）；分组 + 选择性阻断 82.5–97.9%。→ 分组只保护放在前面的来源，不能替代。
- **nsWy-W3 注意力 2×2：** A 标签位置对 B 答案词的注意力，“同词”效应 1.9–6.2（×10⁻³）远大于“同类评论”效应 0.5–1.0，两者 6/6 CI 都不含 0，交互小。→ 检索主要按标签词身份寻址，评论类别相似只起小作用。

## 运行记录
- 2026-11-25 09:10：Gemma 第一次运行漏了 BOS（论文的 Gemma 运行经 `scripts/run_gemma.py` 在开头加 BOS；新脚本直接调用时没有）。与 E132 逐条比较时发现差异（最大 |Δz| 12.7），作废，输出移到 `results/_invalid_nobos/`，Gemma 的 E134/E136 全部经 `run_gemma.py` 重跑。Qwen3-8B 与 E132 逐条完全一致（128 个条件，最大 |Δz| = 0）。
