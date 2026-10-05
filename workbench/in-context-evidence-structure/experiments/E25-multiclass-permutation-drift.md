# E25：多类别映射的 concept drift——可交换汇总是不是二分类特有？（2026-10-05）

- **状态：** RUNNING（卡片与运行同时写下，结果出来之前）
- **类型：** CLAIM
- **对应：** C02 的边界；I02“察觉但不重置”的前提——映射通道在 K>2 时是否仍可交换
- **问题（一句话）：** 二分类时“新映射=旧映射取反”，模型也许只是在两个答案间按计数投票；当 K=4/6、新 regime 是类别→标签的置换（derangement）时，映射通道还是可交换的吗？
- **设置：** AG News（K=4：world/sports/business/technology）、TREC 粗粒度（K=6：abbreviation/description/entity/person/location/number），公认自然数据，直接使用（不经 step 审计）。300 base/任务，SEED0=740000；16 条 demo（AG 每类 4 条；TREC 3,3,3,3,2,2）；偶数 base A=恒等、B=随机 derangement，奇数 base 反之。11 个模式（allA、single_1/16、suffix_3/4、disp_4、noise_2__suffix_3、suffix_8、prefix_8、block_start4、allB）。`scripts/build_mc.py` → `data/mc`。
- **oracle：** `ices/oracle_perm.py`——全部 K! 双射上的 HMM，λ×ε 网格与先验同主 oracle；路径穷举单测通过（`tests/test_oracle_perm.py`）。
- **读数：** logit[P(B 标签)/P(A 标签)]（K 个候选中只比较这两个）；成簇 suffix4−disp4、噪声 noise_2__suffix_3−suffix_3、后8−前8、末位−首位；allA/allB 准确率。
- **决策表：** 映射通道仍可交换（噪声方向反、后8≈前8）→ 可交换性与类别数无关，是“关联记忆”的一般性质；若出现规范方向 → 二分类的结论只是“取反”特例，需重写 C02 的范围。

## 结果（2026-10-06，Qwen3-8B、Qwen2.5-7B）
| 模型 | 任务 | allA 准确率（A=恒等 / A=置换） | 成簇（oracle +4.4） | 噪声（oracle −1.61） | 后8−前8（oracle +6.1/+6.7） |
|---|---|---|---|---|---|
| Qwen3-8B | AG News | 0.90 / 0.25 | +0.12 [−0.19,0.42] | **+1.10** | +0.75 |
| Qwen3-8B | TREC | 0.83 / 0.23 | +0.75 | **+0.86** | +2.34 |
| Qwen2.5-7B | AG News | 0.87 / 0.27 | +0.12 | **+0.44** | +0.45 |
| Qwen2.5-7B | TREC | 0.77 / 0.24 | +0.46 | **+0.35** | +0.96 |
- 噪声方向 4/4 错；成簇远低于 oracle。置换映射本身几乎学不会（自然标签词的语义锚定，Krishna Kumar 2025），故只作方向性证据：多类别时条件结构同样没有规范的变化推断。
