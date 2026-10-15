# Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling

- 主源：[正文](https://arxiv.org/html/2506.04699v1)、[KDD2025代码归档](https://doi.org/10.5281/zenodo.15526912)。读§3–5与表1–2、动作/画像附录入口；归档124339 bytes已下载，只读README、MMOAgent.py的背景/决策/议价提示与Bargain.component_step，不称完整源码审计/基线复现。
- **源事实：** 对象是MMO玩家的代理模拟，非全部为作者NPC角色。升级、采集、商城、充值、拍卖、P2P；画像来自真实玩家特征。记忆/反思有原消融，画像一致性主要由GPT-4并辅以部分人评。原议价提示直接比较价格、税与沟通劳动；成功议价字典触发资产/代币交换，聊天消耗Labor。
- **Idea来源/ownership：** 以语言代理补充RL经济模拟的社会互动和人群差异；角色偏好影响经济活动、沟通成本改变交易制度选择，已有系统性研究。
- **与I04的距离：** 源经济提供实际多步资产成本，但不能把玩家模拟自动叫NPC结果，也不能把重新接本地LLM当贡献。当前E63/E64不因读到该系统就扩新模型实验。
- **未核对：** 完整原论文配置、画像与utility权重的独立性、发布代码与原表精确对应；本轮不修其代码/跑其RL。归档SHA256 `ee82b807c38dd7b281467557c5960708eae3f02876a2e4e0acddc26ad6278182`，原文件在cache。
