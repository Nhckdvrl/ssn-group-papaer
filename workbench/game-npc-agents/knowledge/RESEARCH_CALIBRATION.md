# 顶会研究的贡献尺度：本轮定向阅读与逆向分析

2026-10-13。不是“已精读全部新顶会论文”。以下区分实际阅读范围、作者陈述与我们的研究设计重建；尚未运行这些论文的模型。较早工作用于恢复问题前史，而非以旧 baseline 代替当代竞争者。

## A. LIGHT → How to Motivate Your Dragon：角色目标与语言行动的共同基础

**原始来源：** [LIGHT 正式论文](https://aclanthology.org/D19-1062/)、[项目与人类数据入口](https://parl.ai/projects/light/)、[NAACL 2021 正式页](https://aclanthology.org/2021.naacl-main.64/)、[Dragon 正文/附录 HTML](https://arxiv.org/html/2010.00685v3)、[LIGHT 引擎](https://github.com/facebookresearch/LIGHT)。本轮读项目页、Dragon 的任务/方法与数据段、引擎 README/graph 说明/play_map 源码；未完成历史模型的全量代码追踪，不标 P4。

**DOCUMENTED：** 角色有动机，可与伙伴交谈并在游戏图上行动。Dragon 有 7,486 quests，过滤后 2,111 个人类示范；示范平均仅 2.18 个动作，不能误当长程任务。引擎决定动作后果，固定伙伴模型决定互动响应，另有 learned DM 给语言自然性分数。这三种反馈地位不同。

**RECONSTRUCTED：** 研究动作不是再加一个 persona prompt，而是把有自身动机的角色放进社会—物理耦合环境，分别检验说话和行动如何帮助目标。将背景预训练、任务学习及两类反馈拆开，使“哪一种能力在帮助完成任务”有了实验入口。对我们最重要的是问题与反馈结构，而不是原来的网络配方。

**不能继承的结论：** 原论文的固定伙伴、检索候选与短轨迹限制了它的范围；新 LLM 可能改变瓶颈。原角色扮演/DM 分数也不是人类喜欢 NPC 的完整证据。未知伙伴、新玩法或长关系应另行验证，不能由旧 benchmark 名字自动支持。

**下一阅读动作：** 从真实 quest 到完整交互查对象对应关系；检查数据/模型许可和任务拆分；区分文字宣称完成与真实 GraphEvent；确认旧模型与现代本地生成基线各自的输入优势。任务饱和后不靠随意加长/加干扰硬制造难度，应回看还有哪个领域问题尚不清楚。

## B. Direct Behavior Specification：把制作需求变成可学习目标

**来源：** [ICML 2022 正式页](https://proceedings.mlr.press/v162/roy22a.html)、[PDF](https://proceedings.mlr.press/v162/roy22a/roy22a.pdf)。本轮核查动机、§4–6、主要实验图页及作者/机构；不是完整代码复现。Ubisoft La Forge 参与，不是事后为算法套游戏应用。

**DOCUMENTED：** 作者用可解释的行为约束及 Lagrangian 方法，降低仅靠 reward shaping 指定 NPC 行为的困难；并处理多约束共同训练的稳定性和目标推进问题。论文对象是连续控制，而非 LLM 对话。

**RECONSTRUCTED：** 原瓶颈是“制作人员想要的行为怎样可靠地表达为优化目标”，不是 benchmark 分数低。先改变问题表达，再分析多个约束同时成立时的学习障碍，最后验证相应算法。贡献链条连接了生产需求、数学对象、训练行为和可验证结果。

**对我们校准：** “行为可控”本身早已被研究；自然语言约束也不是新事物。后续 LLM NPC 研究必须指出现有表达/控制方法在何种真实交互中不足，并有新的解释或可靠的改进证据，而不能把角色守则换成 JSON 就报创新。

## C. GAMMA：不要用同质伙伴替代真实玩家

**来源：** [NeurIPS 2024 正式页](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6e9f99809b6df59e8fe5c9ffe269bf40-Abstract-Conference.html)、[作者 PDF](https://liangyancheng.com/assets/pdf/NIPS2024OvercookedZSC.pdf)、[官方代码](https://github.com/lych1233/GAMMA-human-ai-collaboration)。本轮读问题/方法概览、附录实现、算力和人类评测段，并核查 README；未安装/复算。

**DOCUMENTED：** 用潜变量生成伙伴政策覆盖不同策略，训练能适应人的协作者；模型不是 LLM。论文有人类合作评测，附录说明训练与评估中人的适应问题。作者报告整套主实验约 3,600 GPUh，不能由政策网络小推出整套实验便宜。

**RECONSTRUCTED：** 从训练伙伴分布不能覆盖人类的失败出发，把“增加更多自博弈策略”改为可从人类和政策轨迹共同学习的生成分布；再检验对真实人的协作迁移。关键不是多样性图漂亮，而是它是否改善目标配对分布。

**对我们校准：** 同一模型扮演所有玩家/NPC 的循环容易遗漏问题，却不能据此再宣称“首次发现伙伴分布重要”。本地实验应有规则、学习型和不同模型伙伴，保留真正未参与挑选的伙伴。早期无需全量重训该论文；先核查检查点可取性与强评测入口。不能将模拟伙伴结果写成人类体验结论。

## D. Hypothetical Minds：思维模型必须接受互动预测检验

**来源：** [ICLR 2025 正式页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/12f483f624b378f9f3058d8ecd3c7ff5-Abstract-Conference.html)、[论文 PDF](https://arxiv.org/pdf/2407.07086)、[官方实现](https://github.com/locross93/Hypothetical-Minds)。本轮查问题、方法结构、§4.5 消融、局限、B.1 成本表及 README。未逐条核查所有40页提示词和后台分支，不标完整算法复现。

**DOCUMENTED：** 系统提出、评价、修正对其他代理策略的假设，并用于高层规划；论文区分仅提示、模块化提示、假设评价与精炼，原文也有 Llama-3-70B 而非全是闭源实验。成本表的1000-step RWS示例中 GPT-4 约 $10/局，Llama3 配置用4卡，不能把无训练当无成本。

**RECONSTRUCTED：** 从“让模型想一想别人如何想”转到可被未来动作检验的策略假设，再问哪一步改进带来了收益。它展示的是对推理过程提出预测性要求，而不是证明所有社会推理都需要一种统一 ToM 架构。

**对我们校准：** 新增伙伴记忆/反思器极可能只是复用既有思路。准备形成具体假说时，先问它能否解释已有强方法的成功/失败、是否超出额外调用和环境脚手架收益。默认不复制昂贵 API 配方；本地替换后重建对照，并明确它不是原论文数字复现。

## E. Proact-VL：有用内容与适当时机一起评价

**来源：** [ICML 2026 官方接收页](https://openreview.net/forum?id=k9PKgV0L4C)、[全文 v4](https://arxiv.org/html/2603.03447v4)、[官方发布](https://github.com/microsoft/AnthropomorphicIntelligence/tree/main/Proact-VL)。本轮读任务、decide-then-generate、§5.1、关键实现附录及完整资源/评估入口；未复算表格或运行模型。

**DOCUMENTED：** 面向流式解说/指导，区分响应时机与内容。当前 README 已标注并链接权重、训练数据及测试脚本；旧检索摘要中的未发布状态不再适用。论文主训练约200 H100 GPUh；质量指标和 PAUC 使用 GPT-5.1，另有 F1/TimeDiff 入口。

**RECONSTRUCTED：** 仅在固定时刻输出高质量回答不能解决主动伙伴的需求，因此把是否响应变成可调、可评估的决策。研究的尺度包括模型、时间读数和不同交互场景，不是改一个触发阈值就足够。

**对我们校准：** 开源推理可研究，评价链路仍须本地化/明确替代；解说者不等于可行动的 NPC。将文本状态替代视频可用作条件诊断，但不能据此声称复现视频理解。完整重训不是当前默认投入。

## F. 当前角色与体验近邻：范围不能借用

[Dynamic Persona Coherence / ACL 2026](https://aclanthology.org/2026.acl-long.1336/) 的官方摘要已明确区分稳定身份与历史依赖状态，本轮只重新核查正式身份和摘要，不能称全文精读。它的模型/critique 链不能默认本地低成本。

[Interactive Drama / ACL 2025](https://aclanthology.org/2025.acl-long.546/) 及其[正文](https://arxiv.org/html/2502.17878v1)把玩家能动性、沉浸感放入评价；本轮读引言/构念与评价设计入口，未重做人类实验。它提醒我们不要从语言自动分数跳到游戏体验；并非证明作者式剧情约束和所有玩家自由必然相冲突。

## 阅读之后真正改变的判断

CPDC 不再决定科学方向。原生角色行为、设计者控制、人类配合、长期连贯和及时主动性都有独立文献与行业需求；它们的证据标准不同。旧论文不足以证明今天仍有同一瓶颈，最新论文的标题也不足以替我们证明新颖性。下一步应从可本地运行的自然角色任务中获得观察，才值得提出具体的新认识。
