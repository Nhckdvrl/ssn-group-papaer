# Understanding the Dynamics of Demonstration Conflict in In-Context Learning（arXiv 2603.04464v1，接收状态未核对）`[证据级别：主文§3–5及实验表；附录未完整审计]`

1. **形态：** 冲突行为＋机制定位＋消融。
2. **压力：** 从示例归纳规则时，一个错误示例可能压过多数正确示例。
3. **改变的前提：** 不把干扰只看成随机答错；观察竞争规则的编码与最终选择。
4. **idea来源（RECONSTRUCTED）：** 少数污染引起系统性采用错误规则，继而按表示、输出及位置敏感性分解过程。不是作者原始发现日志。
5. **近邻/距离：** Cho的query forerunner；induction/标签检索；位置偏置；规则归纳。这里把位置敏感的头与晚层输出贡献结合，不是首次发现attention可以分配示例权重。
6. **证据：** Operator Induction/Fake Word Inference，四模型；probe、logit lens、头消融、跨任务消融。baseline遵守单一规则＋少数污染，并预设多数原则。
7. **限制：** rule-ID提示的logit lens不等于原答案内部轨迹；改善是部分的；early/late划分不能仅由probe与输出解码差自动识别。主文有消融加强证据。
8. **可迁移动作：** 从具体错误采用哪条规则出发，而非只画accuracy；在两个阶段分别提出可干预读数。
9. **ICES定位：** 一般“冲突规则同时表示、晚层选择”“坏示例与位置偏好”已有所有权。ICES两规则各有合法Source，query决定适用范围，不是多数把少数当污染；这种区别是具体任务定位，不能单凭换设定宣称novelty。E85须靠身份cue的反事实依赖与组合预测提供增量。

[主文](https://arxiv.org/html/2603.04464v1)。未核对会议状态或全部附录。
