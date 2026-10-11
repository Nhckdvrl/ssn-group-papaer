# E08：Semantic audit of heuristic negatives（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I06
- **问题（一句话）：** TD-JEPA / RC-aux 训练时实际采到的 cross-batch/cross-trajectory negatives，有多少在环境语义上真的满足它们被赋予的“far / out-of-budget”标签？
- **设置：** **不训练新模型。** 在 pinned TD-JEPA 与 RC-aux pair samplers 上加入只读 audit。首选 TwoRoom，因为 dataset 有 episode_idx、step_idx、pos_agent/proprio，环境 topology 可做 privileged reachability audit。先复现真实 DataLoader batch/clip sampling，再对 sampled negatives做 oracle标注。至少审计 TD-JEPA canonical 与 RC-aux reachability两套 sampling rule。
- **读数：**
  - sampler-level pair count；
  - source/goal 是否来自同 original episode；
  - observed same-episode forward connection/gap（若存在）；
  - environment geodesic / shortest-step，或 validated reachable / out-of-budget bounds；
  - TD-JEPA negative semantic precision：D*(s,g) >= margin 的比例；
  - RC-aux negative semantic precision：D*(s,g) > h 的比例；
  - false-negative rate vs budget h、TD margin、geodesic distance、wall side、dataset region、source episode；
  - batch/window collision rate；
  - **unknown rate**：oracle 无法可靠判定时不强行二值。
- **阳性对照：**
  1. 同轨迹未来 pair 的 observed gap必须符合代码正例定义；
  2. 同轨迹且 h<observed gap 的 RC-aux temporal hard negative按构造是 trajectory-observation下 insufficient-budget，但不要叫 environment shortest oracle；
  3. 手工选 TwoRoom 明显近、同房间、无遮挡 pair，oracle应判在较大 budget内可达；
  4. 手工选隔墙且极小 budget pair，应判 out-of-budget。
- **噪声地板 + MIE：**
  - sampler stochasticity用多个固定 data/batch seeds估计；
  - CI cluster by source episode / batch，不把数百万 pairs 当独立样本；
  - **MIE 不拍脑袋定 5%。** 先做约 10k sampled-pair audit，若 contamination稳定且置信区间足以判断 E09 是否有可观样本量，再冻结 gate；
  - 同时报告不同 margin/budget 的 sensitivity，避免挑最差阈值。
- **混杂审计：**
  - 必须调用或逐行复刻 pinned repo 的**真实 pair sampling逻辑**；
  - TD-JEPA code audit显示 loss对 batch rows random permutation，未显式检查 original episode identity；audit保留这个 implementation事实；
  - RC-aux pinned code同样对 batch维度 permute goal，不使用 environment connectivity；
  - frameskip 与 temporal-gap单位换算到真实 env steps；
  - TD margin按实际 loaded window/config解析，不写死；
  - oracle只用于 measurement；
  - shortest-step若难以严格精确，改成 certified reachable / certified out-of-budget / unknown，不用近似值冒充真值。
- **决策表（跑之前写）：**
  - contamination稳定且非微小 → E09；
  - contamination极低且CI窄 → I06 PARK；
  - oracle大部分 unknown → 先做 certified-bound audit，不训练 intervention；
  - sampler与论文描述有 implementation差异 → 记录 provenance、核对 current/main vs pinned commit，不先做价值判断；
  - same-episode batch collision若是主要来源 → 先测 episode-aware permutation这个最简单control。
- **算力预算：** 主要 CPU + dataset scan；GPU只在需要 encoder/latent diagnostics时使用。优先 node-local dataset。  
- **实际：** 待运行

## 结果
未运行。