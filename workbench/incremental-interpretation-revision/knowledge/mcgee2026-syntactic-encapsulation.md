# Evidence Against Syntactic Encapsulation in Large Language Models（Cognitive Science 2026）`[证据级别：主文全文]`

来源：[出版社正式全文](https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.70187)，2026-03-10；UCLA McGee / Zhang / Blank。2026-10-07已读Introduction、Methods、Results、Discussion及Notes完整正文（网页125–434行），含全部表与图注；图未视觉校读。Supporting Information与OSF均403，附录/代码未读，不宣称全附录或复现。

**Source-grounded record.** The study asks whether apparently syntax-specialized attention heads remain sensitive to semantic plausibility. It selects heads on Penn Treebank dependencies against a fixed-distance baseline, then tests 50 minimal pairs per dependency in BERT, GPT-2 and Llama 2. The candidate heads are selected independently of the main materials. Main analyses model attention with word frequency; fuller models additionally control PMI and semantic similarity. Plausibility effects survive those fuller controls for four of six BERT dependencies, three of five GPT-2 dependencies, and four Llama dependencies. Semantically attractive, syntactically incorrect lures sometimes gain attention. Head specialization is imperfect; different models do not share every stimulus or dependency. Appendix analyses and code remain unread. The paper acknowledges that it does not establish the implementing mechanism or exclude encapsulated representations elsewhere. Its methods section lists three Llama dependencies while Results reports four, including a separately selected nominal-subject head; this reporting discrepancy is retained.

**论文形态与idea来源（我的重构）：** 从“哪里能找到syntax”推进到“该计算是否可被外部意义改变”。最强候选位置而非平均hidden是有力度的研究对象；如果连这些位置都受影响，反驳范围清楚。增量不是attention可视化，而是把一个领域长期争论的架构前提变成可以失败的预测。与Clark2019的定位、Manning的可读syntax、Gulordava的无意义句语法知识相比，换的是要解释的性质。

**对我们：** 不能把K改动叫纯句法地址，也不能把V叫纯实体内容。更值得问的是：帮助正常理解的合理性信息，何时开始阻碍对旧关系的修订？E69已测到行为的合理性效应，E84没有形成共同机制；两者之间缺的不是更多head图，而是能预测同一个关系在后到证据下究竟保留还是撤回的因果对象。此推论尚无证据，不叫新finding。

**可迁移动作与短板：** 先确定普通领域读者关心的前提，再选择它最强的可证伪实例；范围有限也可有价值。选择dependency-specialized heads与干预实际理解是不同证据，原文的attention变化不能认证latent parse，更不能直接证明隐式编辑。我们应优先复用成熟材料检验修订功能，不照搬其防御控制清单；若新增材料/断言才用Step Plan。
