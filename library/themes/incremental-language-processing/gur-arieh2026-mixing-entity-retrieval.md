# Mixing Mechanisms: How Language Models Retrieve Bound Entities In-Context（ICLR 2026 主会）`[证据级别：正文部分]`

来源：[v2正文](https://arxiv.org/html/2510.06182v2)、[作者研究说明](https://yoav.ml/blog/2025/mixing-mechs/)。2026-10-06实际读§1–3.4及作者说明；§4–6、附录尚未逐段核对。v2=2026-05-28，arXiv页面标明主会接收；不声称查过评审。

1. **论文形态：** 机制解释＋因果模型；旧positional binding解释在更复杂setting里不足。
2. **压力：** 同一文本里的实体配对能被问答访问，不代表检索只靠一个位置地址；列表中间位置是区分解释的压力，而非仅追加模型规模。
3. **改变的前提：** 从单一位置机制改为position/lexical/reflexive三种共同作用；用interchange反事实使三个解释指向不同答案。
4. **idea来源（DOCUMENTED）：** 前人小列表的position解释在长列表中的低faithfulness；从失败条件设计相互区分的反事实。
5. **与近邻距离：** Feng/Steinhardt2024、Prakash2024/25、Dai2024的binding地址及lookback已有基础；这里把三机制输出分开，并用新反事实区分reflexive pointer和直接答案复制。不是首次提出entity binding。
6. **已核对实验：** §3九个Gemma2/Qwen2.5/Llama3.1模型，主要boxes/music；两个模型测十种binding任务。原始和counterfactual binding矩阵中每个解释预测不同实体；最后token residual的layer干预；§3.4把counterfactual答案从original词表中移除检验pointer。作者说明另报告三机制causal model和长padding，正文对应部分未读完，不能当本卡已复核结果。
7. **限制：** 主要templatic不同实体配对；所谓freeform主要是实体组间加入无binding句子，不能等同原始新闻/小说的跨表达、跨事件关系。也不能据此断言自然语言只有这三机制。
8. **可迁移动作：** 同一输入里让两个解释预测不同输出；成功retrieval需和其依赖证据拆开；模型概率变化不自动是latent binding的证明。
9. **对本线：** 一般lexical-versus-entity retrieval、角色binding和位置影响均已有强owner。E48名字/描述交叉只能定位角色后效应依赖什么表达，不能单独认证novelty；需要晚角色证据的具体事件范围和自然功能后果。用户禁止SAE/probe/训练，本线仍只做frozen行为与likelihood实验。
