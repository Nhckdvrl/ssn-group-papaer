# E25：多类别映射的 concept drift——可交换汇总是不是二分类特有？（2026-10-05）

- **状态：** RUNNING（卡片与运行同时写下，结果出来之前）
- **类型：** CLAIM
- **对应：** C02 的边界；I02“察觉但不重置”的前提——映射通道在 K>2 时是否仍可交换
- **问题（一句话）：** 二分类时“新映射=旧映射取反”，模型也许只是在两个答案间按计数投票；当 K=4/6、新 regime 是类别→标签的置换（derangement）时，映射通道还是可交换的吗？
- **设置：** AG News（K=4：world/sports/business/technology）、TREC 粗粒度（K=6：abbreviation/description/entity/person/location/number），公认自然数据，直接使用（不经 step 审计）。300 base/任务，SEED0=740000；16 条 demo（AG 每类 4 条；TREC 3,3,3,3,2,2）；偶数 base A=恒等、B=随机 derangement，奇数 base 反之。11 个模式（allA、single_1/16、suffix_3/4、disp_4、noise_2__suffix_3、suffix_8、prefix_8、block_start4、allB）。`scripts/build_mc.py` → `data/mc`。
- **oracle：** `ices/oracle_perm.py`——全部 K! 双射上的 HMM，λ×ε 网格与先验同主 oracle；路径穷举单测通过（`tests/test_oracle_perm.py`）。
- **读数：** logit[P(B 标签)/P(A 标签)]（K 个候选中只比较这两个）；成簇 suffix4−disp4、噪声 noise_2__suffix_3−suffix_3、后8−前8、末位−首位；allA/allB 准确率。
- **决策表：** 映射通道仍可交换（噪声方向反、后8≈前8）→ 可交换性与类别数无关，是“关联记忆”的一般性质；若出现规范方向 → 二分类的结论只是“取反”特例，需重写 C02 的范围。
