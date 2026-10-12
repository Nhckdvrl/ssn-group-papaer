# How Query Visibility Changes KV-Cache Compression Rankings（arXiv2026）

`[作者v1主文全部精读]` [原文](https://arxiv.org/abs/2607.11942v1)，Luo/Liang/Xuan，UTS；12p PDF SHA12e7d7fd72b77e13328cec59e2d067d7afad3c692ae0cc550e4fac62a668758a。Main1–8 pp1–10全部，补表6 p12全部，Table2/Fig1 p5与自然文本/后端 p8视觉核；参考文献定位，代码未核，接收未核。不会把该预印本结论当独立复现。

- **idea来源（RECONSTRUCTED）：** 压缩KV的经济用途是重复查询，但常见测量先显示当前问题；SCBench已揭示query-unavailable损伤→在相同输入预算上直接测每个scoring rule对问题可见性的依赖→发现method排序可变并检查是否只是benchmark/后端因素。不是“别人没做query-agnostic”的空白题，而是已有问题的定量定位。
- **方法尺度：** 六kvpress0.5.4方法、三个简单规则和FullCache；RULER650项13子任务×三模型×两协议×四比例144300记录，LongBench16×50共40800；配对50000bootstrap。Llama与两个Qwen谱系，不假称三独立架构。Best-of3 trivial作为参照，进一步matched-best-of3选择校正，不把最大值自动作公平结论。
- **结果/边界：** 作者报告SnapKV aware−agnostic gap约.198，KeyDiff约.011；KeyDiff的重复haystack优势在自然文本缩小，其它方法可超过。H2O后端混杂排名撤回；R1近地板与gemma超context记录保留，非能力判死。主表TOVA agnostic mean gap也为+.095且21/36胜，因此“only KeyDiff”应理解为更一致，而不能解释成其它方法平均全负。理论query-independent公式不代表不同协议所有实际logits完全不变。
- **机制证据尺度：** 六scorer代码中question占比与effect的顺序对应，是关联假说，不是已做连续窗口/反事实query因果证明。写清该范围有参考价值，但我们的探索无需照搬所有审计控制。
- **与I08距离：** “目标相关不等于可复用信息重要”已有明确owner。它研究预算下留下哪些信息，未测完整原文仍可见时非assertive目标能改善回答又增加明确错误关系。若我们的故事仅“query-aware状态不能泛化”，压缩风险大；应由E98 actual/joint输出决定更具体增量，而非借其部署叙事换名。
- **可借：** 改一个核心接口，画同模型配对迁移；再看自然数据上原强claim是缩小还是反转。不要用更多大量微控替代新认识，也不要把其它预印本“严谨词汇”当合格idea尺度。
