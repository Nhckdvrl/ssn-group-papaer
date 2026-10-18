# CitySim: Modeling Urban Behaviors and City Dynamics with Large-Scale LLM-Driven Agent Simulation

规范记录：`citysim_2025`；EMNLP 2025 Industry:215–229。实际版本：ACL Anthology正式15页PDF。

**实际阅读范围：** 全文15页；正文§1–7、App A–D全部，配置/表1–5/评价与负例齐读

[原文](https://aclanthology.org/2025.emnlp-industry.15.pdf) · [发表／主源信息](https://aclanthology.org/2025.emnlp-industry.15/)

**来源与范围：** 2025；EMNLP 2025 Industry:215–229；ACL Anthology正式15页PDF。全文15页；正文§1–7、App A–D全部，配置/表1–5/评价与负例齐读。[CitySim: Modeling Urban Behaviors and City Dynamics with Large-Scale LLM-Driven Agent Simulation](https://aclanthology.org/2025.emnlp-industry.15.pdf)。阅读标记：first_full_body_after_existing_partial_card。

CitySim将大城市生活模拟分成分层日程、需求、长期目标、地点信念和社会关系。必做事项先排入时间块，自由时间在线生成并评价3个候选活动；饥饿、安全、能量和社会需求有阈值优先级，目标每月或重大事件后重估。地点评价由LLM产生，再经Kalman更新与衰减进入空间记忆；亲密、信任、熟悉度影响社交对象并随对话改变。这是混合计算架构，不能概括为单一persona提示。

默认1000个东京代理、GPT-4o-mini，与GeAn/AGA/HumanoidAgent/AgentSociety/MobileCity比较；时间分配模拟2个月，幸福度实验依据1200份日本私有调查并模拟3周。五分类macro-F1为0.36±0.02，优于这些代理基线但低于GBDT的0.45±0.04。§4.2虽题为“Human Preferences”，实际是GPT-4o评价，每方法15次；App C的2万输出人类相似度及模块消融也为LLM评分，App D用Gemini复核。百万规模表是设置/获取查询1:999的仿真负载测试，不能直接当百万LLM角色全天思考速度。

它扩展了长期动机、空间与社会反馈，但目标是城市行为仿真，未验证玩家玩法。宏观分布吻合也不等于个人心理机制正确：POI热度以Google Maps评分做代理，存在品牌偏差，部分真值私有。本文显示具状态的日常生活可有规模化证据，仍需将描述真实性、预测效度和可玩角色能力分别评估。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](../../../../library/themes/game-npc-social/papers/AGENTSOCIETY_2025.md) | 后者专注城市基础设施与并行模拟速度，CitySim更多报告日程/幸福感与POI行为预测。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](../../../../library/themes/game-npc-social/papers/CONCORDIA_2023.md) | Concordia提供通用GM与组件框架，CitySim选定城市活动和需求状态实现。 |
| [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](MMOAGENT_KDD2025.md) | MMOAgent用游戏经济账本与五类消费画像，CitySim对齐真实城市时间和地点行为。 |
