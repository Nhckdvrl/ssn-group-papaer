# Human-level performance in 3D multiplayer games with population-based reinforcement learning

规范记录：`jaderberg_2019_quake`；Science 364(6443):859–865, 2019-05-31; DOI 10.1126/science.aau6249。实际版本：Published Science typeset paper (7-page mirror, 6 article pages plus metadata); 2018 arXiv v1 used only for selected earlier methods。

**实际阅读范围：** Complete 2019 published main text, PDF pp.1–5, references/acknowledgements on p.6; DOI/title/authors/acceptance date cross-checked against UCL institutional record and publisher-formatted PDF; 2018 arXiv:1807.01281v1 first four pages and supplementary pp.20–22, 27–31 for training setup, earlier human tournament and ablations; not treated as 2019 supplementary or separately counted work; Authors 2019-05-30 DeepMind research report read to verify 40-human tournament and scope; 2019 official supplementary not acquired/read; later response-delay human sample composition not independently recovered beyond main text; videos not watched

[原文](https://gwern.net/doc/reinforcement-learning/exploration/2019-jaderberg.pdf) · [发表／主源信息](https://doi.org/10.1126/science.aau6249)

**稳定 ID：** `jaderberg_2019_quake`。Science364(6443):859–865，2019-05-31，DOI10.1126/science.aau6249。**实际阅读：** 2019正式排版论文完整正文（PDF1–5）和参考/数据说明6；公开镜像原论文与UCL正式身份核对。UCL接受稿PDF返回403。2018 arXiv v1只补读1–4、20–22、27–31的方法，**不冒称读过2019完整补充材料**；两版本计一个work。作者2019研究发布全文补核40人人类比赛。

FTW让30个独立学习策略在随机室内/外地图上重新配队竞争夺旗；每人像素第一视角与得分输入、模拟手柄输出，无场外通信或其他玩家真值状态。慢/快时间尺度RNN加外部记忆产生时间上连贯行为，内部奖励把13类得分事件映到稠密反馈，种群进化又按实际胜负优化这些奖励权重/超参与选择策略。这说明环境/队友/对手共同形成的训练变化和时间抽象，能涌现跟随、守家、敌营等旗的战术；“学习自己的奖励”是优化赢率的中间机制，不等于人物价值观或自主剧情目标。

比较包含奖励只有胜负的self-play、手工奖励塑形、PBT、去掉时间层级，以及Quake原生不同等级规则bot。2018补充的人类协议是40名FPS经验者、5场各8人的小比赛，2练习+7轮随机人机队伍、无通信；2019作者发布仍确认N=40。正式正文另报告专业游戏测试员可连续12小时找漏洞，随机地图面对FTW仅25%胜；**固定地图漏洞可利用**在2018方法中写得更清楚，不能把随机地图强度写成永不被利用。学习曲线到每个体450k局，训练靠大规模并行，不是几次在线游玩就自适应。

2019新增267ms观察延迟模型需RL与跨时间蒸馏微调，强人+延迟agent队对全延迟agent队平均胜21%；这有助排除“全靠瞬时瞄准”，仍不是完全相同人类感知/动作条件。未取得2019补充材料，新增延迟实验人数/全部配置保留欠账，不用初始40人自动替代。神经元线性可解码游戏状态及无监督行为聚类是表示/行为证据，不等于模型有显式可编辑的策略知识。

对游戏NPC领域的价值是可通用到陌生地图和陌生队友的真实低层战术能力，特别适合训练伙伴/替补队友/对手；玩法设计还要求读得懂的难度、可预期的失误、玩家参与空间。原论文主要最大化胜率，不能直接推出好玩或合作体验在所有玩家上提升。与MLMove的对照很清楚：FTW从奖励探索学强策略，MLMove在固定地图专家日志和规则瞄准下学可信移动，两个目标和成本模型应并存。

**主源：** https://doi.org/10.1126/science.aau6249 ； https://discovery.ucl.ac.uk/id/eprint/10076318/ ； https://deepmind.google/blog/capture-the-flag-the-emergence-of-complex-cooperative-agents/ ； https://arxiv.org/abs/1807.01281

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Learning to Move Like Professional Counter-Strike Players](DURST_2024_MLMOVE.md) | FTW 的奖励学习优先比赛能力；MLMove 的专家模仿优先可信移动和实时部署预算，不能用单一胜率排序两者价值。 |
| [Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot](LEIBO_2021_MELTINGPOT.md) | FTW 训练/测试团队竞争的像素策略，Melting Pot 系统改变背景群体和收益结构以检验社会泛化。 |
| [Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination](CEC_2025.md) | 两者都用环境与组合变化削弱固定约定，但 CEC 是共享奖励厨房协调，FTW 同时含敌对团队、低层射击和大规模 PBT。 |
