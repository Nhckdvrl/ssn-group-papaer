# Frame-Semantic Knowledge Injection for Event-Level Inference in LLMs（ACL2026 short）[证据级别：部分正文]

[Primary论文](https://aclanthology.org/2026.acl-short.55/)，Rai / Croce / Basili。实际读摘要、§1–3（frame监督、491k QA、NLI、Table1/2及诊断切片），后续SRL细节、limitations与附录未完整读；未训练/复现。PDF303,646bytes，SHA256 `447c3b5037313f0b750d7ce2ddc3ccf4decf36f306cd0853058a4e57178fe44b`。

1. 形态：语言资源驱动的事件知识注入＋NLI迁移。
2. 压力：surface cues不足以处理frame／role／事件间关系。
3. 前提：FrameNet的roles、senses、semantic types、inter-frame relations可作为principle监督。
4. 来源（DOCUMENTED）：由约60frames覆盖扩到1200+，改变监督为原则而非只存facts。
5. 距离：frame知识带来event-level entailment／contradiction改善；这类宽泛“结构事件推理”已有owner。
6. 方法：Llama3.1-8B LoRA，CONFER及FrameNet-filtered SNLI、SRL支持。CONFER改进强依few-shot；切片与总体分开报告。
7. 边界：NLI结果不是跨事件预测机制；没有直接测试I01的角色作用反向。框架资源不是我们的训练授权。
8. 可迁移动作：把role与事件间关系拆开，在已出现的竞争解释上选择结构干预。
9. 对I01：坚持frozen inference；精确增量是局部角色事实在新的事件中如何重新作用，避免泛称新event reasoning benchmark。
