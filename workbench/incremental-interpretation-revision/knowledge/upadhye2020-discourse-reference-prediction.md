# Predicting Reference（EMNLP 2020）[证据级别：正文§1–5；未逐条核参考文献]

- primary：[Upadhye/Bergen/Kehler](https://aclanthology.org/2020.emnlp-main.70/)，PDF直接无代理缓存；hash见D0-E45-reading-assets。
- 形态：心理语言学的三组预测→冻结LM的受控测试。把下一提及bias与指称形式/代词产生概率分开，不以Winograd问答代替online discourse。
- 实验：GPT2-large/TransformerXL；IC1/IC2、motion/transfer-of-possession、perfective/imperfective；12 referential frames×gender反向，共24，每类20或18谓词，三connective条件。以He/She归一条件概率测subject next mention。
- DOCUMENTED idea来源：人类语篇coherence和Bayesian代词模型；对表面近同句子做有方向的semantic预测。多数谓词/aspect预期不成立，connective部分起作用，阴性结果没有消失。
- 与我们距离：已拥有一般next-mention语义/结构/context contrast问题；E40描述NP与E45名字差不能本身卖第一项discourse sensitivity。原neutral noticed句是另一coherence/用途，减去它不自动得到纯角色。
- 可迁移动作：同一referent多种表达下区分identity-level信息与form-selection bias，控制语篇关系；这是下一alias检验的设计资源，尚未证明本线能有同样严密的functional claim。
- 未做：没有复现本论文、没有下载/审计其verbs代码或人类数据；读到的群体均值不用于我们的阈值。
