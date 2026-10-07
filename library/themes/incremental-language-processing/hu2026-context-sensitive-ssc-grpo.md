# Reasoning Error from Known Fact / SSC-GRPO（浙大2026-07-21预印本）

证据：[arXiv v1](https://arxiv.org/html/2607.18915v1)主文§1–6/Limitations完整，AppA–D/F/G文字与H算数例子；E/I图片prompt未逐字核对。正式接收未核对，不冒充顶会正文。HTML外置SHA acb0a951b5b4057895ad27f111f670d633c6af9e3a70ae5ee6991c13375db936。

1. **形态：** 失败taxonomy＋内生step奖励方法；不是直接神经回路因果定位。
2. **压力：** 长reasoning里简单事实也错，补外部知识不一定对应瓶颈；GRPO只分配最终结果奖励，已有SelfCheck又恰好需要多个rollout。
3. **改变前提：** 将知识缺失与context中不会使用分开；既然单独询问可以成功，尝试用模型自身跨rollout支持为具体step给credit，不把每step均等分配最终优劣。
4. **idea来源（RECONSTRUCTED）：** hallucination taxonomy/参数知识与使用分离→错误step改写成独立问题→发现context-sensitive类别多→SelfCheckGPT的NLI一致性和GRPO已有多rollout相配→CriticSearch式advantage重分配。方法创新主要是诊断与现成训练接口的连接，不是全新优化器。
5. **近邻距离：** SelfCheck只检测，此文进RL步骤credit；FSPO外部事实奖励，此文内部跨样本支持；SEED-GRPO整轨迹semantic entropy，此文具体step；Lepori新context几何部署失败，此文reasoning factual片段；Shi irrelevant-context distraction为补充实验证据祖先。一般“知道却受context干扰”已有主旨占有，不能靠GP命名获得创新。
6. **材料/方法：** Qwen3-4B Instruct/Thinking 2500 BOBA，235B judge按错最终答案找首错step、改写孤立问题；同trace换GPT-OSS120B复核总比例。训练Q3-4B base/instruct、Llama3-8B，Hotpot2k与math 200BOBA+8kSimpleRL；8H20/full参数、2epoch、8rollouts、温度1。每step对其他trace（去最终答案）做NLI +1/0/−1，由outcome正确/错给予.8/.2权重，均值/std标准化再按advantage符号缩放/clip；基线同数据verl GRPO/FSPO/SEED。
7. **结果/短板：** taxonomy Q3I correct66.32%、context-sensitive22.76%，约67.6%在错最终答案子集中，不能称所有CoT steps的70%错误。训练后72.24/16.90%。七benchmark平均相对最强baseline+1.80/+1.01/+1.50pp，AIME pass32与其他pass1混合、评估2次无CI；部分基线更好（HaluEval/某AIME），SOTA仅限所比。MathNLI83.3/92.18%，SNLI base53.6%；尚未量化训练step分布上reward真伪。NLI稳定增加不证明真值增加，稳定共同错误仍可获支持；外部outcome reward仍需要，不能叫完全无监督。孤立改写同时改变task/信息，原context导致错误的机制未因果定位；appendix额外无关条件使GSM下降约13–14pp，只支持干扰存在。公式clip和不同step token数使“总advantage完全不变”不自动成立，未核对代码实现。
8. **可借动作：** 将失败所在知识点变成独立可解问题，诊断先于方法；利用已有rollout产生内生信号，要说明它替代什么而不等同真值；把资源优先给能够改变解释的对比，不补无穷controls。
9. **对我们：** 数据载体可借源支持NLI，但E70的判断对象是实际表达的关系，不是模型自一致；E71保持相同上下文只改变正确局部表达的消费路径，比孤立prompt对比更能区分具体来源。若仅发现context有害，叙事会被该文及Shi压缩；若找到正确修订何时制造另一依赖错误并改变它，才有更独立的对象。仍是待证方向，不自动关闭。
