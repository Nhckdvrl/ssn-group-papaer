# LLM surprisal is necessary but not sufficient to capture English garden-path effects（Paape, Linzen & Vasishth 2026）

**阅读身份：MAIN_VERIFIED_THIS_PASS（作者arXiv v2 HTML，2026-10-12；模型§与结果§全读，附录与先验设定未核）。** [arXiv 2602.04489](https://arxiv.org/abs/2602.04489)。预印本，未核投稿/接收状态。

## 1. 什么未知促成它
**AUTHOR-STATED**：surprisal对GP阅读时间的低估是旧问题（van Schijndel & Linzen 2021等）。他们问的是更尖锐的一件事：阅读时间里究竟混了几种过程？把“是否走上花园路径”“撞到不相容续接的代价”“做重分析的代价”“重分析是否成功”分开后，surprisal还解释哪一部分？

**RECONSTRUCTED**：这是对“一个连续指标解释一个混合过程”的不满。思路来自多项式加工树（MPT）在记忆研究里的用法，被搬到句子加工；之前没人把四种阅读范式（眼动、单向/双向自定步速、Maze）放进同一个潜过程模型。

## 2. 设计与规模
- 五成分shifted-lognormal混合：不注意；注意但未GP；GP无隐重分析；GP有隐重分析；GP有回视。潜参数p_gp、gp_cost、reanalysis_cost、p_success（overt/covert）、p_infer（语用推断）等。
- 数据：七个实验，NP/Z与MV/RR（**无NP/S**）；SAP SPR n=2000；Timkey 2026眼动n=367；Huang & Ferreira 2021眼动n=120；Fujita 2025 Maze n=60；Paape & Vasishth 2022三组n≈100。surprisal来自GPT-2/Mamba/rwkv。

## 3. 关键结果
- p_gp（无歧义）.31–.33；歧义效应+.48到+.56；gp_cost只有6–10ms；**covert reanalysis_cost 202–227ms**；MV/RR比NP/Z的covert代价高82–117ms。
- 重分析成功率：covert .23–.25，overt .63–.70；MV/RR成功率高于NP/Z（overt +.51到+.62）。
- 结论：“NP/Z更容易被花园路径，MV/RR重分析更贵但更常成功”。
- surprisal：单独比类别基线还差；加到RT/gp_cost上有帮助，放到p_gp上有害。故“必要但不充分”；surprisal像“成功解析的理论”，不是恢复的理论。

## 4. 作者对LLM的猜想（原话要点）
LLM缺少“与人类缓慢、费力、有时有意识的句法重分析相平行的专用机制”；另一可能是LLM保持更多并行解析因此切换更容易，但Timkey 2026a发现减少并行度也不产生人类式困难。

## 5. 对本workbench的意义
- 人类侧已经把**重分析成功概率**和**重分析代价**分开，并且给出构式差异（MV/RR成功率高）。我们的E87分层（MV/RR替代依赖题GP下0–12%）是对应的LLM侧“成功率”读数，而且方向和人类相反：人类MV/RR成功最多，模型几乎不成功。这是可以直接对话的点。
- 他们的p_infer（语用推断）参数对应我们的“No≠not”问题，说明人类侧也把问句语用当潜参数处理。
- 借用动作：把最终理解结果也当作混合过程（拒绝旧读 / 建立新读 / 语用补全）建模，而不是一个准确率。

## 6. 没有做
无NP/S；无最终理解问句的替代依赖分层；LLM只作为surprisal来源，未测LLM的理解输出。
