# Semantic Gravity Wells: Why Negative Constraints Backfire（arXiv2026；primary正文部分）

[primary v1](https://arxiv.org/html/2601.08070v1)。实际读§1–3和§4.1、4.2、4.4、5–6；机制细节未复现，会议接收/数据代码未核对、未下载PDF。

- **形态/来源：** Qwen2.5-7B-Instruct的负面词禁令，作者报告2500单词问题、每题16采样；按baseline目标概率研究违规，补attention/logit-lens/patching。单纯点名禁止词的priming和促进/抑制竞争已有这一preprint claim。
- **证据校对：** §6.2例子同时给ΔP=.92和P_constrained=.82，按§3.2定义ΔP=P_baseline−P_constrained意味着baseline=1.74，不可能；pressure最低.20的gating与.10区间解读也不清晰。只登记作者ownership，不把其机制/比例当已验证事实。
- **对I01：** 不销售泛化“不许X使X更可及”或并存双机制；本线词可合法出现，受约束的是旧event中的角色关系，测新事件患者预测的方向/身份边界。普通实体可及性已有neutral对照，但focus/词面关系依旧竞争。
