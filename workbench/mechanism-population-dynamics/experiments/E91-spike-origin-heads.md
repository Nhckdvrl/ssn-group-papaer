# E91：预训练 loss spike 从哪个头开始？——单点瓶颈的 previous-token 头是不是起点（2026-10-15）

- **状态：** RUNNING
- **类型：** CLAIM（先做最便宜的定位：只读权重与前向统计，不训练）
- **对应：** E90（seed3 spike 74k→76k、seed4 122k→124k；两次 spike 当步被替换的都是 induction 的单点瓶颈 previous-token 枢纽头；正常种子 14 万步从不换该头）；E89（9/10 正常种子里 induction 与 ICL 依赖同一个早层 previous-token 头）。
- **最强已有认识：** 注意力 logit 增长 / 熵塌缩导致失稳（Dehghani 2023；Wortsman et al. 2023 small-scale proxies；Zhai et al. 2023）；Kimi K2（2025）报告 logit 爆炸只出现在少数头、用逐头 QK-Clip 抑制；arXiv 2505.15548 认为短程依赖使 logit 快速增长。**未见**在真实发生的 spike 中说明爆炸的是哪种功能的头，或把它与“功能集中在单个瓶颈头”联系起来。
- **为什么值得用训练轨迹：** spike 是时间局部事件，终点只能看到“换了头”，看不到起点在哪个头、是否有前兆；追踪的量（每头 logit 尖锐度、熵、previous-token 分数）可在同一 run 内比较。

## 问题
spike 之前，是哪一个（哪一类）头的注意力先变得异常尖锐？是不是 induction 的单点瓶颈 previous-token 头？

## 设置
- seed3：60k–76k 每 1k（17 个）；seed4：110k–124k 每 1k（15 个）。对照 seed0（原版）、seed1：60k–76k、110k–124k 每 2k；长程参照：seed3、seed0 的 1k、4k、16k、33k、48k。
- 每检查点：固定 32 篇 pile-10k × 512 token；每头记录 softmax 前 logit 的**行内尖锐度**（行最大 − 行均值，取全体行的最大值 spread_max 与均值 spread_mean；对整行平移不变，Pythia 的 QKV 偏置会让原始最大 logit 整体平移、不能直接用——冒烟时原始最大值在 20–23 层达 ~1.4×10⁴ 而熵 0.5–1.3）、注意力熵、previous-token 与 sink 分数、W_QᵀW_K 谱范数；全局：验证损失、输出 logit 最大绝对值、各层残差 RMS。
- 脚本：`scripts/e91_spike_heads.py`；结果 `results/e91/`；检查点下载到运行主机 /tmp、用完即删。

## 预测与决策表（看结果前写）
- **H-枢纽：** spike 前（seed3 ≤74k、seed4 ≤122k）尖锐度增长最快 / 超出对照同步范围最多的头是该 run 的 previous-token 枢纽头（seed3 6.12 或 4.6，seed4 5.11）或同层头，且早于损失变化 ≥ 1 个检查点 → 写“spike 起于功能单点瓶颈头”，下一步用受控训练（对该头做 QK 截断 / 加冗余）检验因果。
- **H-其他头：** 前兆集中在别的头 → 记录它的功能类型（previous-token 分数、层、熵、sink），按该类型重述。
- **H-无头级前兆：** 所有头的尖锐度在 spike 前与对照无异，只有 spike 当步变化 → spike 不是注意力 logit 驱动（转查输出 logit / 残差范数），本线止于描述。
- 对照两个正常种子的同步区间给出噪声与正常漂移范围；“异常”= 超出对照全部检查点的范围。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

### 中间结果（2026-10-15 22:50；21/76；对照种子尚未开始，以下只是同一 run 内的比较）
- **seed3（60k–76k，每 1k）：** spike 前（≤75k）两个 previous-token 枢纽头的尖锐度平稳（6.12：spread_max 25–27、熵 0.91–1.00；4.6：28–29、熵 0.72–0.76），没有增长前兆；全模型尖锐度最高的始终是第 23 层的头（≈75–97，同样平稳）。76k spike 当步，previous-token 头**变得弥散**（4.6 熵 0.75 → 4.82、spread 28 → 6.3；6.12 熵 → 4.25），即枢纽在 spike 中被破坏，而不是先爆炸。按 1k 分辨率，seed3 不支持 H-枢纽。
- **seed4（111k–117k 已出）：** 第 21 层的 21.14（previous-token 分数 0.01，不是枢纽）尖锐度在 113k 之后陡增：spread_max ≈ 90 → 452（115k）→ 979（117k），spread_mean 34 → 188 → 422，熵降到 0.08；同期损失不变（2.234–2.238），比 spike（122k→124k）早 ≥ 7k 步。previous-token 枢纽 5.11 平稳（35、熵 0.64）。若后续检查点延续，属 H-其他头：前兆在一个深层、非 previous-token 的头上。
- 待：seed4 118k–124k、两个对照种子同区间的正常范围。
