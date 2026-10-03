# Can Large Language Models Faithfully Express Their Intrinsic Uncertainty in Words? — EMNLP2024 main

[最终论文](https://aclanthology.org/2024.emnlp-main.443/) · Yona, Aharoni, Geva。13页PDF服务器直连取得（717309bytes），不经当前环境代理。

- **阅读范围：** 正文§1–6、Limitations完整；附录A/B/C与D主要judge提示逐节读，未核对代码、原输出/人类逐条数据和所有图像。References未逐篇追完。不把这张卡算完整复现。
- **idea来源 DOCUMENTED：** 自信的错误答案会导致人类过信；先问自然语言表达是否忠实于模型已有信念，而不是继续优化factual accuracy。最近邻多测后验confidence/factual calibration，论文改变目标为回答本身的语言承诺与内部consistency的关系。
- **对象与测量：** 以assertion为单位，decisiveness由读者仅根据回答给truth probability；intrinsic confidence以20次采样中不矛盾比例近似；平均二者绝对差得到faithfulness。非双向蕴含的答案如具体城市/所属州可以兼容，作者不用语义熵相同簇定义confidence。这是建模选择，不能说consistency透明读出了内部知识。
- **实验与数据：** PopQA保留6relations/移除短entity，和非ambiguous NQ各932；5个闭源aligned endpoints，greedy回答、20samples+GeminiUltra抽assertion/矛盾judge。100个改写回答与已有WEP survey比对，100个作者标签的confidence相关.97；不能当所有任务judge质量保证。Vanilla cMFG约.52–.57、最好prompting.70；许多hedges不能正确跟随intrinsic proxy，非证明现代2026模型一般失败。
- **强近邻距离：** semantic entropy依赖互相蕴含簇；factual calibration看external labels；Mielke2022把预测错误概率变成control token。该论文新对象是assertion-levelfaithfulness和连续decisiveness。由压力→改变评价对象→proxy与人工校对→zero/fewshot干预构成论文，不靠再增加一个benchmark。
- **限制值得借鉴：** 报punt1/3/10/8%的不同coverage后在非punt子集评分，不能把其分数直接与我们的all-item invalid bounds混比；作者也限制到single-answer factual QA，讨论说明source of uncertainty重要。正文/附录的epistemic/aleatoric用词与常见统计习惯不同，后续优先明确model/data/speaker/interpretation来源而不沿用术语。
- **对当前E51的推理：** IQAP human definitely/probably标记听者解释B意图的判断；不等于B自身knowledge，也不等于模型factual confidence。DPO后probable候选上升可能是回答政策/措辞偏好，不能直接说speaker commitment能力变差。full candidate质量较高只能排除一类输出支持问题，仍需原source的语义与referent控制。
- **我们可能改变的premise（未取得证据）：** 在真实间接交流中，模型必须区分表达受损、说话者知识不足、意图歧义以及自身解释不确定，不是统一输出更保守的hedge。检验这些证据是否产生正确且可迁移的条件预测，比复述generic“自信与行为不一致”有价值；不退到普通factual calibration，也不claim首次分解uncertainty/首次模型judge。
