# Structural Persistence in Language Models（TACL 2022；全文部分）

[主文](https://aclanthology.org/2022.tacl-1.60/)。实际读§3度量、§4.3 core构造、§7.1词/语义boost、§8讨论；模型与全部结果/附录未通读。

- **形态与来源：** 将人类structural priming迁移到冻结LM的受控行为测量；从abstract structure与lexical cue难分的压力出发（DOCUMENTED）。
- **研究动作：** 同一target在不同结构、相同语义与词汇的prime后评分，避免比较不同target时的先验混杂；每target配10prime。Prime-LM约1.3M pair，dative/active-passive；core去掉内容词和尽可能多的function word overlap、用人类association norms限制语义关联。
- **已拥有：** 不同新句/新actor仍会出现上下文结构持续效应；词和语义重复增强，function word boost可以很强，distance/exposure影响。不能把E25跨actor或释义迁移本身叫全新机制。
- **有用的距离：** 我们不是比较新target结构偏好，而是某旧活动的排他事实如何在后续患者关系/实体提及中使用，且GP与明确cue历史调节同一事实响应。是否真正具有更新特异增量，必须与普通priming分开，E29检验源句必要性。
- **短板与约束：** 作者明确未分boost来自同一结构表示还是独立因素；预测控制不证明episodic event graph或内部重绑定。我们不因阅读开始probe/训练。

20页PDF，436,504 bytes，SHA256 `e6852b12dfe726de75f3bffd3b1fffc48b70d91e9671a717a94a0ae8a96a4b81`；直接无代理下载，cache-only。正文声明CC BY4.0。未读公开评审，不编分数。
