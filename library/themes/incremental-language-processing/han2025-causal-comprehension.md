# Beyond Surface Structure: A Causal Assessment of LLMs’ Comprehension Ability

[ICLR2025主页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/88139fdcc82fc597090620d77b023282-Abstract-Conference.html)；实际方法核对用[arXiv v1](https://arxiv.org/abs/2411.19456v1)，未核对最终accepted版差异。

1. **形态：** 理论估计量 + 跨任务干预；不是incremental parsing专门论文。
2. **压力：** 表层扰动会降分，不足以推出只会表层匹配。
3. **动作：** 同时修改意义和形式，与目标意义保留的形式修改作比较；ADCE是两个改变输出比例之差。
4. **来源（DOCUMENTED）：** 既有surface-robustness批判不能独立辨识core-semantics依赖，借causal mediation定义问题。
5. **距离：** 不只accuracy下降；提出DCE/ICE代理及必要性/充分性解释。泛泛“问法敏感不等于不能理解”不是我们新贡献。
6. **实做：** 12模型、五任务；先选原来答对项，再用Mask或Claude3.5生成/自检查。Appendix F按gold是否改变确认所谓意义改变/保留，最多10次生成；两个group近似相同表面改动。CivilComments fine-tuning只是其验证，不是我们获授权训练。
7. **限制：** 真实surface mediator无法固定，论文也承认approximation。只保持答案标签不保证整句意义不变；formal必要性/充分性还假设monotonicity。原答对项的条件化使结论范围随模型变化。不能照搬其proxy便宣称识别了内部parse的因果效果。
8. **可迁移动作：** 语义效应与测量形式效应一起测；负/失败对照完整报告，谨慎区分操作量和理论对象。
9. **对我们：** E11的head/span修复若成立，是measurement correction；还须解释GP语言操作或后续自然事件使用。E09自然题cue效应保留，所以也不能用模板伪影解释全部现象。
