# Emergent social conventions and collective bias in LLM populations

规范记录：`norms_2025`；Science Advances 11(20), eadu9368。实际版本：Published 2025-05-14; institutional copy with cover, 11 pages。

**实际阅读范围：** 全部正文与Materials and Methods，PDF pp.2–9（期刊 pp.1–8）；引用与代码/数据声明 pp.10–11；另册Supplementary Text和S图表未取得，不宣称读过

[原文](https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf) · [发表／主源信息](https://www.science.org/doi/10.1126/sciadv.adu9368)

**来源与范围：** 2025；Science Advances 11(20), eadu9368；Published 2025-05-14; institutional copy with cover, 11 pages。全部正文与Materials and Methods，PDF pp.2–9（期刊 pp.1–8）；引用与代码/数据声明 pp.10–11；另册Supplementary Text和S图表未取得，不宣称读过。[Emergent social conventions and collective bias in LLM populations](https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf)。阅读标记：new_full_read。

该研究把社会惯例操作化为重复命名协调游戏：随机抽两人从字母池各选名字，相同+100、不同−50；每人只见自己最近H次经历，不知道总体群体目标。四种模型构成同质群体，常用24人、10个候选、记忆5次，各40个独立模拟运行（图2最终收敛分布部分模型仅27/20次）；还改变规模至200人。没有中心协调，仍出现全体共享词汇。更有价值的是单次空记忆选择未见显著偏差，历史状态中的不对称反应却被群体反馈放大，令某个等价字母更可能成为规范。作者对第三轮可能记忆分支做微观分析，使“涌现”具有可检验的动态解释。

稳定惯例可被始终输出另一名字的固定策略群体推翻；阈值依模型与具体标签而变，范围2%至67%，某模型的弱惯例甚至无外来者也会翻转。不能把25%当普遍社会常数，或把不显著的初始偏差检验说成证明绝对无偏。相互作用是匹配动作，无自由对话、处罚、道德理由、非对称利益或现实社会网络；“规范”在此主要指任意惯例，未证明现实伦理与制度已经涌现。论文也明确研究的是AI自身群体行为，不以LLM作人类代理。

对游戏邻接价值在于城镇、派系或经济文化会由局部行为循环塑形，单NPC一致性并不能保证群体可控；同时固定世界规则、交互网络、记忆长度和群体重复才是解释单位。要转为玩法仍需玩家可感知/影响的制度后果，不能从字母共识直接宣称丰富社会NPC。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](GOVSIM_2024.md) | 同属群体涌现，命名约定不等于有私利冲突的可持续公共资源治理。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](CONCORDIA_2023.md) | Concordia支持丰富语言社会情境，此实验以极简成对命名和局部历史隔离传播机制。 |
| [SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](SOTOPIA_2024.md) | Sotopia由评判器评分社会规范符合，本文直接观察群体如何形成约定而不预设其内容。 |
