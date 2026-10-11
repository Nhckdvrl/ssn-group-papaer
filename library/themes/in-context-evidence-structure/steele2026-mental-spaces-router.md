# One mechanism for many mental spaces: a shared router over a value slot in language models（2026预印本，会议状态未核对）[证据：正文§3、§4.2、§4.6–4.7核对]

原文：https://arxiv.org/pdf/2607.10248

1. **形态：** 因果表示机制及跨语义构造统一。
2. **问题：** portrait、belief、past等并存空间的值，是否用共享的空间索引路由；报告某值与将它用于规则推断是否相同。
3. **idea来源：** DOCUMENTED为mental-space理论与形式语义不同分类、binding/lookback/JIT研究；未获作者过程记录。
4. **计算对象：** value-token slot、entity/query-token router、晚层output-writing区分；single-site手造patch/mean差失败不推出无绑定。
5. **方法：** 冻结模型，训练d×k正交DAS、Adam lr.005、约150步/batch16；Qwen L34由初始扫描选定，Pythia/Falcon取深度经验位。heldout样例与跨builder迁移，不是每item选层。
6. **重要反事实：** 单空间明确sorting rule blue/green→Anna、red/brown→Ben；分别训练color readout与consequent readout子空间，再交换消费者测试。Qwen color-trained能全改报告、0改consequent；consequent-trained全改consequent、.32改color。Falcon相互作用更大，另报子空间principal angle。
7. **审计：** 完整magnitude随机splice已有.55–.58输出leakage，不能把非零flip算机制；“on-manifold”是作者措辞，优化DAS本身不保证联合状态在原分布。报告/推理两个Goal与监督目标不同，双分离是有力功能证据但不是完整算法反推。§4.2的decodability/填充依赖是retrieval-shaped证据，非单独精确电路定位。
8. **最近邻：** Feng binding IDs、Prakash lookback、JIT、DAS、RAVEL直接方法与概念所有权。共享router/slot、可报告≠可推理均非ICES新概念。
9. **ICES切口：** E101局部criterion词受影响而判断不变不应包装成首次发现这种区分。E102不同之处是规则从私人demo推断，donor与recipient同名来源函数竞争；地址型结果只明确功能接口，不建立新的普遍router原理。未来DAS若做，应比较actual功能消费者，而非只强制criterion词或用监督修复替代原生解释。
