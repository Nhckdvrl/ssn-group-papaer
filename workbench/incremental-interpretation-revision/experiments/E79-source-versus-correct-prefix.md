# E79：已确认正确P1后，Source与P1对下一关系的因果作用（2026-10-07）

- **状态：** DONE；生成器E431运行前改本线E79，非POST-HOC补卡。
- **对应：** C09 / I03 / P17，GP先前解释的修订及下一关系消费。普通草稿语义未知的E76–78块已整体自审收束，回已确认正确内容。
- **问题：** E71 MVRR有正确外显P1仍33–40%下一候选正确，NPZ则95.65–100%。E71切P1无共同恢复。保持Source和正确P1自身计算不变，后续直接读取Source是否妨碍使用这一正确解释？它区分原源后续消费与P1/早期组装，不再扫更多层/位置。
- **数据：** 原E71完整资格38pairs/76S、MVRR15/NPZ23，3新clause原子双遍/34裁决/unknown0已经完成，qualification在科学行为前固定；SHAe082e1039b1f5a39f181d92c373dd7c0f6cd79689d282c30c1a4adbcdfebd0b7。全部原S/固定P1/正确与不受支持P2候选原样使用；0新API、不重审成熟原数据、不改新子句资格，不按E71成功选输入。
- **条件：** NATIVE与CUT_P1完整E71原raw复用。唯一新CUT_SOURCE_LATE：同一完全相同prompt、token/候选，在所有层切原Source key→Sentence2标记及之后所有query。P1前部/源/Task前部计算都native不变，P1后续消费仍全部可用。不新增未来边、不把源hidden替换为oracle、正确P1是外部forced prefill。
- **核心读数：** 正确候选整句joint LP、正确概率/正确率；CUT_SOURCE_LATE−NATIVE，GP/cue及paired GP−cue，三族两构式全部；CUT_SOURCE_LATE−CUT_P1作来源路径比较，同时保留既有CUT_P1绝对读数。margin只次要；lexical cluster等权/10000 bootstrap seed71（沿E71便于复用同一panel），模型seed79/greedy固定。8独立H20按Source SHA分片，Q3/G2/L3，完整全部后读效果。
- **阳性对照：** 原cue native选择高；每族各分片固定首2源native4D/2D与E71 LP差<.001、Source至Sentence2之前全hidden差0、删除边非空且仅指定SourceKeys与laterQueries。母实验raw/model/data SHA闭合，native不重跑完整。
- **噪声地板：** FP32/eager/固定原revision；上述LP仪器/完整CI，38pairs是pilot，不用阈值自动认定novelty。不添加随机mask/层/head扫描。
- **混杂审计：** 此cut只切后续Source直接路径；Source信息仍可经原生P1/前部Task进入后续，null不能认证无Source作用，正效应也不代表删净原Source。正确P1是预填，候选选择不是自然产生/潜在能力；cue损伤和两构式不同baseline全报，不把ceiling/null和真实修复混同。不能把切任一来源的信息损失叫具体角色机制。
- **决策表（跑之前写）：** MVRR三族恢复、NPZ正确保持/cue稳定、Source切断好于P1切断→正确局部修订与后续源访问有具体竞争线索，再原生free续写核验实际后果与独立机制定位，仍不自动合格；Source/P1切断同样伤→一般消费/源约束，回E70原子脚印；Source切断无共同帮助→结束这一正确P1来源块，不续mask网格，回实际自由解释形成/操作；所有heterogeneity/阴性保留。科学好坏按interestingness，不把有人做过或null自动关线。
- **算力预算：** ≤.5 GPU·h，228新QA条件（76S×3族），每两候选fullLP，8独立H20/FP32/eager/offline。输入/gold/prefix全部reuse，0新teacher。原raw/assets外置E79，card/code/小摘要入git。

## 结果

原E71全部76源三族CPU验证Source key span/第二句query/完整候选/prompt相同，228任务。8分片Q3/G2/L3已启动；native与CUT_P1全E71复用，只跑Source晚期cut，未读partial效果。

## 完整结果与自审

8分片/228新条件/234格全部完成并读取，0API，.034736GPU·h；map SHA f4f0685a13107101da67e84586f06c71ca847e391433c6b2ccce7130ed206105。native4D/2D与E71 LP差0，Source至第二句前全部hidden差0，母资格/原raw SHA闭合。全图234格入results/E79-source-versus-correct-prefix-summary.json、原始资产外置E79。

- MVRR15 GP Sourcecut−native概率Q/G/L +40.96 [+19.37,+63.31] / +16.04 [-4.56,+38.70] / +22.01 [-1.49,+46.32]pp；cue +3.97 [-14.20,+22.24] / -29.57 [-53.32,-9.31] / +8.42 [-2.76,+23.77]。仅Q主要读数CI分离0；G交互+45.61包含cue损伤−29.57，不包装共同恢复；L margin正不能替代概率CI含0。
- NPZ23 GP -30.82 [-48.17,-15.01] / -9.11 [-22.15,-0.00] / -49.61 [-67.18,-31.87]；cue -51.49 [-70.13,-33.08] / -8.72 [-21.76,-0.00] / -49.96 [-68.30,-31.71]。正确第二句受到严重损伤，不满足另关系/构式保持。P1携带实体/关系信息本就不同，信息损失与模式偏好仍竞争，不认证具体更新机制。
- correct/p_correct/margin、全部六操作和GP−cue交互同报，不筛正cell；NATIVE与CUT_P1完整复用不重复。

自审：正确P1不是完整下一关系的透明状态。两来源依赖有构式差异，但Sourcecut只在一族MVRR稳恢复、并损伤NPZ及cue。没有三族两构式可预测共同规律，普通信息可用性/模式偏好仍竞争，尚不兴奋；停止Source/P1局部mask块，不以补同cell样本追显著，不关territory/idea/线。C06–08 L0/C09限定L1不变，无需人决定。接E70/E67实际语义脚印，并将E2解释重新拆开：世界合理性之外，模型是否把合法但低频的GP输入当成待纠正的语言？这是新竞争问题，不预设成立；先现成数据一个核心输入信任对比，0新审计。
