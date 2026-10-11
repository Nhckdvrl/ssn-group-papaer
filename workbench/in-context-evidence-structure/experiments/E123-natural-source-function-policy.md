# E123：真实文本中，选择性形成能否保留两名来源的私人规则？

- **状态：** PLANNED（2026-10-12，首评分前）。
- **类型：** CLAIM；E122整体形成预测的独立自然语义/输出namespace检验，不扩head/层/强度矩阵。
- **对应：** C21/C22/C23、I04、P17。
- **问题（一句话）：** 对功能明确的真实评论，在同一prefix使用两Source私人约定时，限制答案关系形成与query隔离有何不同，这个区别是否与共享输出身份一致？
- **为什么现在做：** E120确认原生操作贡献与读取背景方向差；E121自然SST私有single可靠；E122四checkpoint在双方面合成任务确认平均收益与一致/冲突tradeoff。尚不能把SST阳性直接转成双方面能力，也不能由合成政策收益宣称天然一般策略。本项在自然SST同一Criterion/私人code竞争，交叉shared/far输出，提出形成政策的功能预测。其结果可支持或限制主文MC3，不通过新增组件名称或磨边界建立novelty。
- **设置：** 沿E121固定SST5 label0/4原文、5–64token与geometry匹配，无输出筛样本；train按SHA奇偶两个demo池、discovery validation-query/confirmation test-query，独立seed123001 n16→123101 n32。A固定pA sentiment，B origin为−pA、cross为+pA、within为−pA的同类移动控制；B raw input multiset/label stream/Source/位置固定。四模型/revision/FP32/eager沿E120–122。
- **政策：** 原E122三个对称prefix全层政策normal/answer_cross_off/all_cross_off、whole-query full/own-only两scope、两Actor共享每个prefix缓存。B输出shared=no/yes或far=pass/flag，A始终no/yes；各Actor用自己的两candidate计分，另保存full-vocabulary argmax。单token词与role/label/answer边界在CPU核。三world×两namespace×三policy×两scope×两Actor=72条件；single A＋两B约定×两namespace=5；origin/cross×两namespace×两Actorinstruction=8，总85×8=680评分/context。
- **读数：** primary每context均匀origin/cross两world×两Actor×八query的candidate accuracy（within额外控制不改变权重），分别报告A/B和两B约定，不是joint同时正确概率。targeted−normal、all−normal、targeted−all、query−native、formation×query；共享/分namespace的targeted成对收益差为预定competition读数。B约定对A的signed response及magnitude/SourceA正确margin保持，原生全Source与own-only均测；所有85条件accuracy/fullargmax/correctmargin保存。
- **阳性对照：** single A每pA、single B两namespace/两方向；一条按Source推断instruction；default-cache与native4D/fullsplit≤.001（首context两namespace/两Actor）、single Source的两形成policy实际cache no-op、双向all-cross+own-only时A对B worlds≤.001；全部层实际mask消费、strict past/self、query deepcopy指针/seq、label位与input movement几何/数据split原文核。
- **噪声地板 + MIE：** context-bootstrap10000 seed910，FP32 floor；n16→32四模型固定执行，未要求固定涨点门槛。收益方向/区间、private能力和输出namespace交互一起判断；不把n32每query当独立重复，不改policy追分。
- **混杂审计：** gold/长度筛选不看预测；Source/频率/私有方向平衡，原文multiset/geometry固定；shared/far词语义与先验并非严格等价，single B和各方向全部报，交互解释为具体输出namespace，不声称唯一身份变量。不同mask改变可达边/归一化并使状态活演化，保留一般访问不等于固定其信息；操作为构造机制测试非learned source recognizer，未训练/无需训练算力对照。SST语义可能pretraining见过，fresh私有pairing不同；两批demo/query独立，context间可复用text；Findings非投稿目标，不参考EACL。
- **决策表（跑之前写）：**

| 结果 | 更新研究判断 |
|---|---|
| shared下targeted平均/私有冲突函数改善，far收益减小，两Actor没有系统一方牺牲 | output-dependent形成解释产生自然任务功能预测，MC3连接两材料，不因两基准数量自动宣布novelty |
| targeted仍有效但shared/far差CI跨零 | 功能政策跨自然材料成立，output特异功能证据有限；C21 namespace因果重建保留，不把政策本身强绑同一通路 |
| query-only强但targeted弱/反，single可靠 | 形成子图参与不等于该政策普适修复，主体形成/内容解释保留，主文明确不同功能条件，不调层/强度或无限换数据 |
| only某Actor/某private方向收益 | 不称同时保住全部私有规则，报告分层与全部世界；仍按原primary进行确认 |
| 数值/几何失败 | 仅修实现并记录0-score/无效评分，所有条件不挑种子；源码再冻结后重跑 |

- **算力预算：** 四已缓存模型独立空卡，n16首数值有效即并行新n32，不按科学正负选模型；预计2–5 GPU·时（14B自然长prefix较慢），不填卡增加无用条件。

## 结果（运行后追加）
待首评分前源封版和CPU预检。

### 首评分前实现冻结

- 主源SHA256 `95a574892e7609a25146f730f7843d176fe27487353f2ad7c9fa7fd01971e9a5`。沿E122已校对的mask/query引擎，只替换SST builder、origin/cross/within私人函数与两namespace输出；85条件所有模型先CPU验证，未有E123评分。
