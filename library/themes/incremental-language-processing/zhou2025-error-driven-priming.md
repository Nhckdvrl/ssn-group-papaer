# Is In-Context Learning a Type of Error-Driven Learning?（NAACL 2025 Main；全文部分）

[主文](https://aclanthology.org/2025.naacl-long.586/)。实际读§3.1–3.2、3.5–3.6、§4分析定义与Fine-Tuning对照、§5讨论/limitations；全部scale结果与附录未完整核对。

- **形态/来源：** 以human structural priming的inverse frequency effect为诊断，问forward ICL是否呈error-driven计算（DOCUMENTED）。不要求prompt有demo/answer；普通连续文本也可视作parallelism。
- **动作/数据：** 改造Prime-LM core，22verb各50无词汇重叠target、4prime/target结构组合，92,400 pairs；另同量pronoun版本。Fine-Tuning阳性对照后测concatenation，按verb bias预测priming slopes，保留代词改变verb bias的影响。
- **ownership：** off-the-shelf冻结LM上下文predictive adaptation、词/结构偏好调节、异句泛化与human priming联系已有owner，不能把E25可迁移关系priors泛泛叫新ICL机制。
- **距离与压力：** 本线晚来participant信息只在一个episode有效，重点是同/另一episode如何改变具体patient关系预测与分类的迁移方向；需要修订范围与内容依赖，不能只把dative换NPZ。
- **解释边界：** 作者承认behavioral empirical证据，mechanistic proof缺；IFE支持error-driven解释不唯一证明forward梯度算法。我们不复制训练或白箱动作，保留no-training约束。

14页，1,521,407 bytes，SHA256 `6f16e2b0c0142472ef34a9abbff472079082bffb0ef1a43bdbc8530cda561f38`；直接无代理下载，PDF cache-only，未读公开评审/分数。
