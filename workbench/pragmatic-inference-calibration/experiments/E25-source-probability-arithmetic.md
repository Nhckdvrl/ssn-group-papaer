# E25：原概率算术的精确工程对照（2026-10-03）

- **状态：** DONE
- **类型：** D1 technical control，非科学机制/新metric
- **对应：** C02/P04，E23 exact source pipeline仍缺原dtype归一化
- **问题（一句话）：** 原BF16全词表softmax→候选截取→BF16除sum，与FP32候选softmax是否解释cache的非严格sum1及阈值翻转？
- **设置：** 与E23完全相同8items/96prompt、two orders/6states、同SHA1cfa9…、原enable_thinking=False。GPU2 original BF16 model(**inputs,output_hidden_states=True) singleton，**保留原logit dtype走原softmax/normalize**；同时以相同logits FP32 target softmax和FP32 global-then-target做纯arith控制。E23早float的source pipeline不是此原BF16算术，原文件保留并注明限制。不重跑整个matrix；no generatedreasoning。
- **读数：** 原两个option概率与sum、同logits三种算术差、source cache per-key差。order平均source>.5与source True>False分别记录（paper形式与code形式不同），不覆盖原metric。支持质量作为工程量，不讲能力。
- **阳性对照：** target字串均一token、96 exact source key覆盖；保存原dtype和inputtoken SHA；FP32 target与global-normalized max差容差1e-5，原源码prob完全相同计算步骤；正例sum1与反例rounded sum偏差都保存。
- **噪声地板 + MIE：** 固定工程probe非随机scientific sample；BF16分辨率与硬0.5阈值的关系不自动当科学贡献；未解释cache全量差不称精确repro。
- **混杂审计：** 三种算术同logits隔离输出运算，但cached原model版本未知、GPU数学不同仍可有差。由source non-additive缓存触发，不把post-hoc校对写成预注册科学假说。parent数值对照先完成再解释任一巨大效应。
- **决策表（跑之前写）：** A原算术逼近cache且sum偏差导致阈值翻转→技术说明，原能力证据隔离，不写新metric故事；B不解释→权重/template/cache provenance审计，不编因果；C差异微小且结果稳→保留parent，回条件证据主未知。
- **算力预算：** GPU2独立BF16 ≤5min，其他队列不干扰。CPU E24并列sum与两种原paper/code规则，不删原结果。

## 结果
跑前冻结；E24补充sum-to-one invariant属data质量审计，原primary不改。
