# When Context Misleads: In-context Learning with Jurisdiction in Large Language Models（arXiv 2609.27603v1，接收状态未核对）`[证据级别：主文§3–5、附录F；完整数据/代码未审计]`

1. **形态：** 构念/benchmark＋post-training方法＋有限机制分析。
2. **压力：** 模型能归纳一致的示例规则，但该规则未必有权约束当前现实问题。
3. **改变的前提：** 区分规则归纳与适用性判断；不能假设context总应覆盖参数知识。
4. **idea来源（RECONSTRUCTED）：** 一致的伪理论示例诱导系统性错误，促成正/负适用性的配对训练；非完整发现记录。
5. **距离：** MetaICL/Symbol Tuning、truthfulness、知识冲突；把适用性判断纳入query-only训练，并控制私有/官方的措辞与实际scope。
6. **证据：** FakeContext-bench 700 theory families/3500实例；多模型行为、四backbone训练；held-out family的晚层MLP替换；相同适用范围下换私有/官方措辞。
7. **限制：** 参数事实与context规则的取舍不等于两个context Source的选择。MLP干预效应小，作者也未称完整authority电路；Reality Rate分母排除Other，必须与全分母输出同时读。接受状态未核对。
8. **研究动作：** 使“表面authority cue”与“真实适用性”给不同预测；训练对象保持query/目标固定，改变不适用的证据及表述。
9. **ICES定位：** “哪些示例约束query”作为广义问题已有直接近邻，不能当空白；其范式侧重现实规则与误导context，ICES侧重两个合法Source在共享标签下的计算选择。E84/E85的field/code冲突是机制诊断，不等于authority能力测试。novelty需落在具体读取依赖及能预测的新反事实，不能另造“适用性”名称。

[主文](https://arxiv.org/html/2609.27603v1)。本卡不是对benchmark规范假设或全部评分代码的背书。
