# Contextual trajectory and incremental contextual displacement（2026-09-30 arXiv v1） `[证据级别：完整主文]`

[作者原文](https://arxiv.org/abs/2610.00840)。UVM；读主文§1–5/pages1–18全部、引言/RelatedWork/方法每项实验/讨论与局限，长附录未深读。52页不是52页都精读。接收/评审未核对。

1. **形态/压力：** 表征测量，研究utterance-specific意义如何构建，而非宏观词义漂移。DOCUMENTED来源是Futrell/Li的incremental上下文＋Jurayj contextual embeddings＋Bigelow narrative trajectory；RECONSTRUCTED增量是以token随新增context的位移序列来描述同一句内部变化。
2. **前提：** 同一token随着prefix变长，重新做encoder完整forward后比较末层CWE。RoBERTabase为主，附录DeBERTa/DistilBERT辅助，不是三个独立大decoder族，也不是修改因果decoder的旧KV。
3. **实验/数据：** Sturt/Grodner GP/cue，1Dconv以增量向量序列分类，80/20split，100随机实例×25epochs；Sturt外部holdout。CLS约98.5%validation/99.8%holdout；first word约97.8/99.7%，critical-region first word94.8/54.9，penultimate change59/50.9。shuffle序列重训约56%，说明有序信息，不唯一证明classifier用的是重析。main未明确词汇组完全分离/各数据集准确条目数，附录未核对。
4. **后续与限制：** dadjokes平均U形无匹配monologue控制，run词义/PCA/UMAP探索；主文承认图低维丢大部分variance。GP/cue插词/逗号产生有序轨迹差，shuffle掉时间/位置标记也能破坏分类，故高分类分数≠正确角色解析；作者说需要未来验证surprisal/误读关联。没有最终QA/角色、没有因果角色干预。
5. **距离与可借：** Jurayj比较最终token向量，本工作比较变化轨迹；Li测surprisal与自报告，本工作分类。可借新增context到底改变哪些token的纵向视角，不能复刻U形曲线就叫新修订机制。对我们的关键压力是将变化连接到正确关系的可复用功能，E64原word states可被消费的因果入口不能由此几何文献覆盖；同样不能借它把粗状态替换改称语义因素。不是该空间的桌面判决。
