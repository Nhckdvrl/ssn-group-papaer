# One Token Can Be Enough: Bridging Prompting and Activation Steering with Prefix Steering（2026-10-04 arXiv v1） `[证据级别：完整主文]`

[作者正文](https://arxiv.org/abs/2610.04967)。OhioState；读§1–6主文全部、AppendixA配置/B1实际方向，长证明D/E未深读。34页PDF；接收/评审未核对。不是“所有场景一个token足够”。

1. **形态与压力：** 机制视角＋理论局部连接＋控制/能力方法比较。Steering全生成施加可伤能力，prompt只在最初输入却能影响后续行为。
2. **改变前提：** 把持续干预改为重定向后续轨迹。只改final prompt token也可以具有远期格式影响；使用现有DiM/加法/COAST，无新vector学习法。
3. **来源/距离：** DOCUMENTED：AxBench能力tradeoff、prompt/activation duality、Bao prompt-only训练等→注意力matching条件→现成direction的Prefix1/5。RECONSTRUCTED：创新在持续控制的时间对象、局部理论和预测，而不是全空白的prefix发明；作者承认Bao更早有短prompt窗口。
4. **理论：** 单head单layer、固定pre-intervention context/query，若query·WK在WV零空间有非零方向，可合并原token与新增prompt token的attention贡献；query变化在指定仿射集可保持匹配，离开后误差随投影距离。multi-token更高rank缩匹配集，single增强可按attention weight比近似multiple weaker。实际norm/RoPE不在定理，多个head还需兼容，不能称整模型/freegeneration等价。
5. **规模/协议：** 四模型Qwen3 1.7/14与OLMo3 7/32（两族）、五task：safety/sentiment/politeness及MATH500两种最终格式；100+100训练样本DiM，独立50层/强度tuning，MATH50construct/50tune/400test。九相对层、强度网格选择control最大且保住80%baseline capability；concept任务用MMLUPro、格式用MATH正确率。greedy，Gemini3.5FlashLite评judge，不把judge结果当语义定理。
6. **读数与界限：** shortprefix often有更好Pareto；prompt在情绪/礼貌/boxed好，steering在safety/plainformat更强；有些fullcontrol更高。曲线piecewise轴明确，Figure2/4 100例band是sampleSD非95CI。SinglePrefix远期成功可能经改动KV/latent状态或生成词传递，论文自己没有区分；现成DiM与理论构造方向只有局部相关、并非满足全部matching条件。
7. **可借动作：** 同样的数据/目标，改干预在计算中的时段，把“更久更好”先验变成精确可反驳比较；理论只说明局部可实现，实验必须另量外推。
8. **对我们：** “短源干预影响后续多用途”或“初始激活持续起效”不能单独算novelty。可以借编码路径/消费者路径/生成媒介的区分，但先针对自然先前关系修订提出有价值对象与预测。E66源保持仍损失目标收益、E68对称断源写入，尚没有证明latent正确关系存在，更不能用steering理论替代语义校验。
