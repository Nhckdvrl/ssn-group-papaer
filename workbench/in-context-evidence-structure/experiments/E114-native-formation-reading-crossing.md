# E114：形成路径怎样参与原生的多来源判断？（2026-10-11）

- **状态：** PLANNED
- **类型：** PILOT / 原生计算的阶段竞争与确认
- **对应：** C21/C22、I04、P17；拟C23仅在结果支持时登记。
- **问题（一句话）：** 已定位的label形成消息在模型正常读取全部Source时是否仍有功能作用，输出命名的效果由形成后的本来源证据、foreign缓存读取及二者交互怎样共同实现？
- **设置：** Qwen3-8B FP32/eager，E111明确情绪/私人yes-no任务，A原文/标签固定；origin/cross/within配对与shared/far namespace不变。n16 seed114001 discovery旧材料；若有明确杠杆，以同源码/条件n32 seed114101 validation词/句式确认，再在Mistral冻结接口确认家族范围。不选层/头/alpha，不训练。
- **干预：** 对每个origin/cross世界，把A全部prefix KV的形成状态(shared/far)与B全部prefix KV的读取状态(shared/far)作2×2 crossing；HEAD一致，00/11分别精确重建两端native。query全程允许读取全部prefix，保持原请求和A输出空间。B缓存已上下文化，不称其为纯词身份/直接复制；cross cache是诊断干预，不宣称模型原生会进入这些混合状态。另将far的A label或只在A label形成时重算的历史B答案K/KV/V送给每个B读取环境，保持其它A缓存固定；后继状态自然演化。
- **条件数：** namespace 2世界×(4 stage corners＋8 label/edge×B读取条件＋3 gated接口对照)=30；within-native1、固定标签关联label/答案反事实6、关系stage交叉额外2、single A1、instruction3，共43条件×8query×context＝5504/11008评分。全部条件预定，不按pilot只选好路径。
- **读数：** 首要是原生Source条件下配对的rule效应：D=mean_q gold*(cross−origin)；比较本来源形成改变在两种B读取环境中的条件效应、B读取改变在两种A形成环境中的条件效应，全部signed/absolute与交互均报告，不强求加性/正向。效应context-bootstrap10000次seed910；冻结系数1的答案K/KV/V重建，对原生A label接口与全A形成接口分别报逐query rule双差分RMSE/r及zero、bootstrap10000次seed109910（E109已冻结函数）。固定label配对的cross−within效应在原生读取下重复，实际全词表argmax和label margin同时报，不把效果自动叫准确率修复。
- **阳性对照：** 00/11与native端点精确一致；HEAD/source缓存不变，single A/private方向阳性；sender layer0 KV对关联反事实不变，whole-query gating对照匹配原E111功能对象，self edge0、实际消费全部层。原生/split完整query第0ctx逐例核对≤.001，不能把长度/缓存数值差当形成作用。
- **噪声地板 + MIE：** 所有干预FP32 matched-shape。CI按context抽样，报告原读数而非拟合份额。namespace总体弱或干预影响很小仍保留全条件，不能由微小r高宣布解释完整；K-only/V-only仅该边不直接改另一通道。
- **决策表（跑之前写）：**

| 结果 | 更新 |
|---|---|
| native形成条件效应明确、label/答案边仍重建 | 将受控形成路径接回原生判断，确认新材料；形成与读取贡献/交互作为叙事证据 |
| gate路径保持但native作用弱 | 解释限定Source-gated接口，原生可能有补偿/主导其它路径；报告差异，不继续细化头 |
| 全A形成作用明确但label/答案边不足 | 保留部分形成解释，报告其对原生功能的覆盖，不为残差开新矩阵 |
| 2×2明显非加性 | 放弃简单两阶段相加解释，保留条件效应，确认相同交互；不事后找更好系数 |
| 数值/原子阳性失败 | 修执行或限定不可识别，不进行机制叙述 |

- **算力预算：** Qwen discovery+确认及必要Mistral确认合计≤.6 GPU·时，独立单卡；实际待记。
- **定位/依据：** CTA在完整功能图中验证路径；How Few-Shot Examples Add Up §5的2×2保留两个背景下的条件效应。本项不是首次factorial/QK-V，也不照搬最终FV操作：交叉对象是本来源形成后的证据与foreign读取环境；目标为原生多来源私人判断。CoSToM提供保持接口接回实际功能的尺度。此实验补叙事必需的native联系，不增加新能力任务或逐层搜索。

## 结果（运行后追加）

待运行。
