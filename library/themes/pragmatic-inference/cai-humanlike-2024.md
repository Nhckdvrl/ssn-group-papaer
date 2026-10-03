# Do large language models resemble humans in language use?（arXiv2303.08014v2，2024）

来源：[固定v2](https://arxiv.org/abs/2303.08014v2) · 原OSF vu2h3/sygku。评审/后来出版版本未核对。

1. **阅读：** 背景概述、noise实验完整结果/方法、讨论相关论证、supplement噪声重分析深读；其它11实验未全部深入，39页不是全文覆盖。PDF SHA b66f52263d1602c269524251289a184181122bbf44204131b6a03927cb99a156。
2. **idea来源：DOCUMENTED。** 从系统psycholinguistic现象判断LLM像人在哪些方面，继承人的实验压力而非synthetic错误清单。12实验、每item约1000重复，ChatGPT/Vicuna10/7符合主要human现象；这些是原论文结论，未重跑。
3. **噪声结果：** ChatGPT对implausible DO/PO nonliteral .92/.56，Vicuna .54/.47；并有plausible controls。拥有原生LLM的noisy-channel形状相似性，不能声称我们首次发现语言修复。DO/PO推断方向符合噪声账户，未干预模型内部channel，也未证明唯一机制。
4. **协议距离：** ChatGPT多trial随机history、Vicuna单trial且无filler；checkpoint/系统与trial结构同时变化。non-preregistered去两个示例item分析全部透明报告；我们不删示例或筛模型正确item。原自动yes/no并人工处理极少例，与E57严格EOS并报bounds不同，不冒充精确评分复现。
5. **最近邻/增量：** Gibson人类原场景→LLM行为对应；后续EMNLP2025 external noisy model→预算与算法。下一自然问题是模型是否根据真正信号证据调整解释，而不仅生成相似平均形状；训练前后这种条件关系能否跨知识限制与意义prior验证。
6. **对我们：** E55跨结构/现代family只是驻留。E57固定原句操纵公开exposure，仍是parent迁移，不能仅靠新endpoint或humanlike/不像humanlike写贡献。机制/重新归因需独立来源识别、读数与自然数据规范共同约束。
7. **资产：** OSF材料/模型原raw/人工coding尚未完整取得、旧模型不可按现代checkpoint精确复现；当前只用已核对的Gibson原材料。不要把原1000重复当1000独立场景，也不把单trial/two-family差叫规模因果。
