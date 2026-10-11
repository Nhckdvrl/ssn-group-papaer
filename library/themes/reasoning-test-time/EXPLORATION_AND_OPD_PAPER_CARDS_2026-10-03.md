# 主动探索与 OPD：定向论文卡（2026-10-03）

本轮是领域定位，不是本仓库实验；数字均为作者报告。全文定向阅读覆盖动机、方法、主实验与相关关键附录，不声称重算每张表。公开评审未读完的条目不推断接收/拒稿原因。

## 1. Reasoning aligns language models to human cognition

[arXiv2602.08693v1](https://arxiv.org/html/2602.08693v1)；证据：全文定向阅读。相关题名 *Active Probabilistic Reasoning in Humans and LLMs* 出现在NeurIPS2026官方目录；最终题名、版本与分轨尚未逐项核实。旧ICLR2026记录为Withdraw、3.50，不把旧分数当最终工作质量。

1. **形态：** 成熟认知范式 + 人机行为测量 + 可解释统计模型。
2. **背景/改变的前提：** 静态题目把证据预先给齐，难以区分不会选信息还是不会利用信息。任务让参与者主动选按钮获得带噪声证据，再判断哪个按钮特殊。
3. **idea 来源：** DOCUMENTED：主动概率推理拆分 sampling/inference；RECONSTRUCTED：把主动学习/心理物理观察者模型迁入LLM评测，避免单一正确率掩盖策略差别。
4. **方法/数据/基线：** 四按钮，一枚偏置硬币与三枚公平硬币；改变回合数及遮挡。人类、不同LLM/推理模式与Bayesian参照；用记忆、采样策略、选择偏置等参数拟合行为。原文报告推理增强对证据整合帮助大于对采样的帮助。
5. **最近邻距离：** 相比 *Can LLMs explore in-context?* 的bandit回报，增加人类匹配与认知分解；相比 *CogBench* 多任务摘要，聚焦可分解的主动任务；相比 LLF-Bench 的反馈学习，主要操纵证据选择与观察条件。此三者在这里是对象/证据距离，非作者逐条证明的历史起源。
6. **证据边界：** 参数拟合不是内部神经机制的因果证据；有限按钮任务不能独自支持开放世界agent结论。训练数据/任务描述、记忆摘要和推理token预算都可能改变结果。
7. **资产：** §11链接[Drive代码与数据](https://drive.google.com/drive/folders/17tQxO02lLN1VpwbOF_IIiM9oSm8DmRik)，本轮未取得可检查文件；不称已可完整复现。LLF-Bench可作另一个独立成熟入口，不能替代本文人类数据。
8. **可迁移动作：** 把一项成绩拆成可独立操纵的“拿到什么证据”和“如何据此决定”；先确认现实失败，再连接游戏/交互。仅重现“选择信息比回答难”没有新意。

## 2. Rethinking On-Policy Distillation: Phenomenology, Mechanism, and Recipe

[arXiv2604.13016v2](https://arxiv.org/html/2604.13016v2)；[代码](https://github.com/Thinking-Space/Rethinking-OPD)。证据：正文及训练/机制附录；会场未独立核准。

1. **形态：** 失败条件 → token级分析 → 干预与配方。
2. **背景/改变的前提：** 学生采自己的轨迹、教师给密集监督，不意味着高分教师一定有可利用信号。
3. **idea来源：** DOCUMENTED：更强教师有时失败促使分析训练轨迹；RECONSTRUCTED：用teacher训练经历/相容性替代单一参数量轴，再用reverse distillation检验解释。
4. **近邻距离：** 对off-policy KD改变状态分布；对Qwen3式OPD关注失败条件；对privileged-information self-distillation区分教师角色；对传统capacity-gap解释增加训练经历与token支持集证据。
5. **方法/实验：** 1.5B/1.7B学生及1.5B/4B/7B教师等；top-16、batch64、rollout4；原配置最大生成7168，评测更长。对齐共享高概率token、逆向蒸馏、cold-start、prompt选择。作者报告共享top-k集中97–99%概率质量；只优化共享部分能接近完整top-k。
6. **短板：** 这些配置不证明所有OPD只传思考模式、不传知识。GPU总时长未核；不能据模型小就称探索便宜。
7. **可迁移动作/压力：** 从稳定失败拆条件，再做能区分解释的干预；“强老师未必好”已归近邻，不拿它直接开新题。

## 3. Rethinking OPD II: One Training Example

[arXiv2609.04172v1](https://arxiv.org/html/2609.04172v1)；证据：正文/状态覆盖/限制及训练附录；本轮按预印本处理。

1. **形态：** 极端输入缩减的系统测量与解释。
2. **背景/前提：** 输入数量不等于训练中访问的状态数量；学生重复rollout与教师分布本身提供大量监督。
3. **idea来源：** DOCUMENTED：检验OPD对prompt数据多样性的依赖；RECONSTRUCTED：把样本效率拆成prompt、状态、dense targets，避免拿一条query误当一条label。
4. **近邻距离：** 对Rethinking I转向输入覆盖；对one-shot RL区别外部结果奖励与教师密集分布；对常规多prompt OPD控制query多样性；对data-free KD仍使用真实输入与已有teacher，不能归为真正无数据。
5. **实验/边界：** 数学、代码、指令、工具四域，Qwen/Llama/OLMo家族；batch64，数百至千步。数学300步例68.5对69.8，约保留87%增益；1000步68.4对72.1，约72%，两者须一起看。K=200的teacher表征聚类衡量state覆盖，不等于证明覆盖全部知识。
6. **资产/启发：** 可借鉴匹配监督预算的拆解；一步都不训无法检验其核心动态主张。不要把标题当低成本保证。

## 4. When EOS Tokens Disagree: Understanding Length Inflation in OPD

[arXiv2609.20511v1](https://arxiv.org/html/2609.20511v1)；证据：正文、修复对照及模型阶段附录；按预印本处理，未确认NeurIPS接收。

1. **形态：** 实现/语义接口不一致 → 训练失效 → 最小目标修正。
2. **背景/改变的前提：** tokenizer或generation config宣称的EOS相同，不代表teacher/student把同一终止token赋予相同概率语义。
3. **idea来源：** DOCUMENTED：跨checkpoint的终止行为失配与生成膨胀；RECONSTRUCTED：把“推理越来越长”先还原成可测试的停止决策，而非直接解释为思考能力。
4. **近邻距离：** 对标准reverse-KL OPD检查token语义对齐；对解码stop-set修复证明仅改生成端不等价于改loss；对模型post-training阶段比较指出终止偏好随阶段变；对其他长度控制策略先识别造成膨胀的具体来源。
5. **方法/实验：** Qwen/Llama/Gemma等及K2Horizon阶段checkpoint；对停止概率作语义聚合，对比仅修解码。修复后仍有部分后期collapse，所以不能把所有OPD不稳定归于EOS。
6. **可迁移动作：** baseline有异常时核对数据、token、loss、decoder契约并分开干预；有科学后果的实现归因可以有价值。我们的探索需小训练闭环，不属于首选training-free驻留。

## 5. Do Composed Image Retrieval Benchmarks Require Multimodal Composition?

[arXiv2605.14787v1 / CIRCUS](https://arxiv.org/html/2605.14787v1)；证据：正文与方法/实验，项目资产未完整验证；最终会场未核准。

- **形态/压力：** 检索系统看似同时使用参考图和文字修改，标准成绩却可能来自只用一种模态。将构念有效性落实到可执行强基线与人类可回答性。
- **来源：** DOCUMENTED：用unimodal控制审计组合需求；RECONSTRUCTED：由benchmark目标反推必须排除的快捷路径，而非先造复杂模型。
- **最近邻：** 对CIRR、CIRCO、FashionIQ等原benchmark，从测排名转为测任务到底需要什么信息；CIRCUS是审计后构造的新测量对象，不只是换encoder。
- **实验/资产：** 四benchmark、11embedding模型；作者报告32.2–83.6%可由单模态捷径解决。4,741项经人审、1,689项验证有效。项目站本轮访问失败，不能把新benchmark列为已可立即跑。
- **对我们：** 可以迁移“先检验任务是否真的要求目标能力”的研究动作；不能重复其headline。多做几种消融不自动等于新构念。
