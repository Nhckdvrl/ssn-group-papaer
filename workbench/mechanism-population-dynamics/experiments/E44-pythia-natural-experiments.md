# E44：第二个模型家族的天然实验——Pythia 标准 / 去重共用初始化；PolyPythias 拆开初始化与数据顺序（2026-10-03）

- **状态：** RUNNING（2026-10-03 启动，39 个模型）
- **类型：** CLAIM（C05 的家族广度，以及初始化与数据顺序混杂的直接拆分）
- **对应：** C05；A02 §2“家族”和“初始化与数据顺序的混杂”两行；对标 PolyPythias（ICLR 2025）的 data-seed / weight-seed 设计、Bali et al. 2026
- **问题（一句话）：** 在 GPT-NeoX 架构的 Pythia 家族中，(a) 同初始化、不同数据（标准 Pile vs 去重 Pile）的两个模型，其 induction / previous-token / 取回头布局是否比同数据、不同 seed 的模型更相似？(b) 在 160M 上，起决定作用的是初始化还是数据顺序？
- **设置：**
  - 前提核查（已做，HF LFS sha256）：pythia-{70m,160m,410m} 与 pythia-{70m,160m,410m}-deduped 的 step0 权重文件哈希相同（1b 不同，不纳入）；pythia-160m-data-seed{1,2,3} 三者 step0 哈希相同（6654b4ea），weight-seed{1,2,3} 互不相同。**逐张量核对（跑前完成）：** 160M 的标准版、去重版、data-seed1、data-seed2 的 step0 张量完全相同（max|diff| = 0）；weight-seed1/2 与它们及彼此不同（0.16–0.19），seed1 也不同。PolyPythias 论文表：data-seed =“only data”，weight-seed =“only parameters”（数据顺序 = 默认）。注意：GPT-NeoX 先打乱文档再打包，所以“顺序”实际是批次组成。
  - (a) 尺寸 70M / 160M / 410M：标准版（seed 0）、去重版（seed 0，同初始化）、PolyPythias pythia-X-seed1…9（同为标准 Pile，不同 seed），最终步 step143000。
  - (b) 160M：data-seed1–3（同初始化、不同顺序）、weight-seed1–3（不同初始化、同顺序）、seed1–9（两者都变），最终步 step143000。
  - 测量：`scripts/census.py`（与 E35 同一套探针：M1 induction、M2 previous-token、M3 sink、M4 取回）。
- **读数：** 两两模型 [层×头] 图的 Spearman。(a) SI = (标准, 去重)，每尺寸 1 对；SD = 同数据不同 seed 的全部对（标准与 seed1–9 之间、seed 之间，共 45 对）；DD = (去重, seed_k)。(b) 三组：同初始化异顺序（标准版 + data-seed1–3 之间，6 对）、异初始化同顺序（标准版 + weight-seed1–3 之间，6 对）、两者皆异（seed1–9 之间，36 对）；另报告同初始化异数据（去重版 vs 标准版 / data-seed，4 对）。
- **阳性对照：** M2 两半文本信度 ≥ 0.8；每个模型 M1_max > 0.3（存在 induction 头）；census.py 在 DataDecide 1B 上复现 E35 的图（逐元素差 < 0.01，先跑）。
- **噪声地板 + MIE：** SD 对的分布（45 对）给出零分布；SI 只有 1 对 / 尺寸 → 报告 SI 在 SD 分布中的分位。MIE：SI − SD 均值 > 0.1（与 E35 同一门槛）。
- **混杂审计：** 数据差异较小（去重版与标准版的文档大量重叠，且顺序不同）→ (a) 测的是“同初始化、数据相近但顺序不同”，比 DataDecide 的数据差异弱，写进范围；(b) 直接拆开顺序与初始化；步数与超参在各变体间相同（PolyPythias 设计）；全部模型纳入，不筛 seed。
- **决策表（跑之前写）：**
  - (a) 3 个尺寸中 ≥ 2 个的 SI 高于 SD 分布的 95% 分位，且 SI − mean(SD) > 0.1 → C05 在第二家族复现；只有 1 个或 0 个 → 不复现，如实记录，C05 范围限定为 DataDecide。
  - (b) mean(同初始化异顺序) − mean(异初始化同顺序) > 0.1 → 起作用的是初始化而非顺序（直接排除 DataDecide 的混杂）；反过来 > 0.1 → 顺序起作用，C05 改写为“seed（初始化 + 顺序）决定”；|差| ≤ 0.1 且两者都高于“皆异” → 两者都起作用；都不高于“皆异” → 不可判定。
  - 每类图（M1 / M2 / M4）分别判；M3（sink）预期处处相似，只作描述。
- **算力预算：** 约 30 个模型 × 每个 < 2 分钟 ≈ 1 GPU·时（下载为主）　**实际：**

## 结果（跑完后填写）
