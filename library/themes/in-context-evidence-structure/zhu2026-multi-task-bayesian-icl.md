# Multi-Task Bayesian In-Context Learning（ICML2026，arXiv记录）[主文§1–7]

[v1正文](https://arxiv.org/html/2606.20538v1)，Zhu / Oermann / **Kyunghyun Cho**（不是Hakaze Cho）。2026-10-10读主文§1–7、特别§5.2.2；附录/代码未读全，内部电路未建立。

1. **形态：** 训练型分层Bayes预测器与先验适应。
2. **压力：** 标准PFN把训练prior放在weights里；测试时仅给target数据，不能灵活改变prior。
3. **改变前提：** 其它任务的数据不必是target的额外样例，可以提供关于task prior的信息。
4. **idea来源：** RECONSTRUCTED；prior不可变→用多组related datasets表达prior→比较先验适应与错误pooling。
5. **距离：** PFN/Neural Processes、latent-conditioning和多任务ICL；新接口在data空间表达prior，不是首次hierarchical Bayes或跨任务共享。
6. **实验：** 从头训练小GPT-2/RoPE，raw数值token+概率输出head；d8、20 prior tasks×50数据点。线性/logistic、heavy-tail/flow prior、ERA5。oracle与hierarchical MCMC/SVI明确区分信息权限。§5.2.2固定target和query、只改prefix，并比较把全部样本视作同latent的pool-MCMC与正确prior oracle。
7. **边界：** “mechanism match”是预测分布对不同算法的匹配，不是native neural circuit定位；需要指定生成模型/共享prior；meta训练小网络不能自动解释自然LLM的Source条件化。
8. **动作：** 同一组外任务数据可以通过不同统计层次起作用；先构造有不同预测的pooling与prior inference，不能只看“外数据改变了预测”。
9. **对ICES：** 不应把foreign influence都定义成错误。候选问题是Source关系怎样决定哪些信息可共享、这种标准相关信息在demo上下文化还是query阶段进入计算。宽版本已被该文/多任务学习覆盖；潜在增量须落在原生Source规则推断的功能与因果证据，不能靠改名或Source-specific格式。
