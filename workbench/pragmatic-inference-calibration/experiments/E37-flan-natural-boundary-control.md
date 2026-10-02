# E37：原Hu强baseline Flan在自然承诺任务上的入口控制

- **状态：** DONE
- **对应：** C02/P02；原Flan1365/1365已复现的independent encoder-decoder endpoint
- **问题（一句话）：** E34/E36的自然类别/位置结构是否也出现在已精确复现Hu的Flan任务读数里，还是只限当前causal model接口？
- **设置：** google/flan-t5-xl原SHA7d6315df2c2fb742f0f5b556879d730926ca9001、原slow T5Tokenizer；E34同433items/218pairs，不新增材料或label。original/固定E36 strict各两order，T5 native encoder prompt（含源EOS），decoder原start token的数字1–8第一输出。没有chat接口，不造fake chat与causal entry对齐。
- **读数：** 原八数字restricted probability与global support/argmax、两order/一句strict恢复；E34同question cluster/四条件，原全部强弱/conditional contrast。只一个endpoint，无Base/Instruct谱系，不做training cause或架构归因。
- **阳性对照：** 数字1–8全单token已CPU核对；原data34268 majority/source/5/5选中hash完全同E34；slow tokenizer/pad/EOS保存；FP32单sequence/no padding首末repeat概率差<1e-6，4分片key并集/无重叠/完整input fingerprints。
- **噪声地板 + MIE：** single sequence/FP32/noTF32/数值重复gate；bootstrapquestion2000/seed0；4分片是一次run的数据并行不是4独立replicate。T5不加causal BOS/模板，不混直接likelihood与metalinguistic答案概率。
- **混杂审计：** Flan older/encoder-decoder/instruction mixture都不同，结果只能描述跨endpoint边界，不能归architecture机制。当前E34阴性weak的order artifact不能用Flan另一个高分洗掉；所有counterexamples保留。
- **决策表（跑之前写）：** A原强baseline能稳定区分→削弱数据一定不可能/强弱不可识别，保留instrument；B同样order/strict支配→读数普适限制，先不讲能力；C某contrast变好/反转→记录自然构念边界，不切成单dataset/model小paper；Dgate失败→技术隔离。无论结果不为此新增训练。
- **算力预算：** 4独立GPU0–3锁×question固定hash4分片，433×4单序列总1732；原checkpoint复用，Mistral权重仍下载。无API/子agent。

## 结果
跑前卡。既有Hu强baseline迁移只回答仪器/自然条件的边界，不把跨任务成功叫新能力。


## 完成与证据限度

四shard完整并按源ID×condition×order合并1732唯一读数，433源QA无重复/缺失，pair不跨分片，native encoder/token hash校对通过。负强度原序强/弱正确.5000/.8462，strict后.8462/.4615；强侧+.3462[.1923,.5385]、弱侧−.3846[−.5769,−.1923]、弱判强+.3846[.1923,.5769]。逆序另一结构，不能称泛化能力/架构原因；强化指令改善一侧不等于改善语用边界。结果：results/E37-flan-boundary-summary.json。

C01/C02仍L0；技术与原任务描述不升级为论文贡献。
