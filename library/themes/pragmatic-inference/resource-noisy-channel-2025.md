# Resource-Rational Noisy-Channel Language Processing（EMNLP2025 main）

来源：[最终论文](https://aclanthology.org/2025.emnlp-main.1207/) · [原代码](https://github.com/thomashikaru/noisy_channel_model)。评审未核对。

1. **阅读：** 全正文/limitations；附录A–C与B算法解释已读，末页伪代码亦已读；公式文本顺序需以视觉/代码继续核对，未独立实现。README、config.jl、gen_model.jl核心generative model已读；完整proposal/Gen执行未复现。14页PDF SHA 670ba256a84ccf42d1992325538b3de123992d39a9ec16da26d2d5c5fd64eac8。
2. **背景压力与idea来源：DOCUMENTED。** 人类在有限计算中处理开放空间的损坏表达，理想Bayesian解码不说明算法如何实现。问题从既有人类行为和计算限制长出，不是“大模型会不会错”。
3. **改变前提：** 把LM当意义prior、独立错误模型当channel，用有限particle SMC/rejuvenation近似推理；计算预算成为解释变量。不是测原生LLM本身是否估计正确channel。
4. **实验/数据：** GPT2、六种错误动作；504 Ryskin四条件材料与120 Qian agreement材料。不同粒子/第二遍rejuvenation/lookback产生非单调的人类对应性。后者只用更强human reanalysis的子条件，有明确资产选择，不能当全面语言覆盖。
5. **最近邻距离：** 继承Gibson的意义/信号分解，加入具体有限算法与在线读数；继承Levy重分析，把资源约束变为可操作参数。Cai原生ChatGPT行为不等于这个外部结构模型。
6. **证据/局限：** restricted-vocabulary LCD与原GPT2 surprisal相关.95并非一致；错误prior固定normal alpha10/error1，不是自然错误率估计。不能移动词序/skip连续多词，nonword和词尾形态支持有限。模型自身候选空间/算法可造成literal偏好变化，无需假定policy变了。公开config默认动作拼写与README示例不同，尚未执行校对，不宣布bug。
7. **对我们：** 新读数需把候选可达性、意义prior、channel识别和最终回答区分；E57只是原exposure响应，未独立识别机制。该parent已有“资源影响修复”的claim；有实质增量的动作是让来源特有的预测约束训练前后解释与独立材料中的泛化。
8. **研究动作：** 为自然tension建立竞争算法账户，扫描边界/反转；不能只借术语或加CoT换分数。代码/材料可用，未运行Julia，未把clone当复现。
