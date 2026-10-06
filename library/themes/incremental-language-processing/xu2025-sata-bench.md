# SATA-Bench: Select All That Apply Benchmark for Multiple Choice Questions（arXiv v3，2025）

**证据范围：** primary v3摘要、§1–2、§3开头与Table2；其余结果分析/方法与附录未完整读。ICLR2026接收说法只见非primary页面，未核准。[原文v3](https://arxiv.org/html/2506.00643v3)。暂停前阅读补记。

1. 形态：multi-answer benchmark＋解码方法。
2. 压力：one-answer MCQ不覆盖多答案用途，集合完整度和猜测/漏选须独立评价。
3. 前提：可选集合不是一个winner；使用Jaccard/EM、selection与count指标。
4. 来源（DOCUMENTED）：已有reading/classification领域转换为SATA、分阶段人工过滤。
5. 距离：六domains、32models、1.47K最终evaluation；早期10K+材料与最终过滤集不是同一个规模。
6. 实验：best EM约41.8%；分析count/selection/speculation bias、提出Choice Funnel；具体方法细节本次未完整核对。
7. 短板：部分小模型用probability threshold，generation/format extraction混杂须注意；benchmark conversion不全是原生自然问题。
8. 动作：计数、每选项判断、完整输出分开测；不是只跑更多模型。
9. 对我们：generic multi-answer count bias已有近邻。E51两role slots允许同名，理论上不同于选distinct set，但当前只是待验证增量，不能把差异本身叫新颖性。
