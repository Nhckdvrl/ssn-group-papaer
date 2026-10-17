# Bisimulation Makes Analogies in Goal-Conditioned RL — ICML2022

- 主源：[论文与正文PDF](https://proceedings.mlr.press/v162/hansen-estruch22a.html)。已读§4功能等价定义、§6适用范围、§7任务／基线设置及Appendix D.1–D.3与环境参数表3／4；未全证明校对／作者代码复现。
- **正文事实：** 对state–goal pair用奖励与转移定义功能等价；学习成对表征后，再构造可作向量类比的单state表征。原Eq4包含即时reward差和转移分布距离，不能用我们的单步reward向量直接冒称完整bisimulation。
- **实验事实：** Drawer及Button等视觉操作任务，目标／初态重组、背景与物体扰动；对照CPC／CURL／VAE／RAD及GC-DBC，另比较composition vectors。附录显示goal-point grounding有益，latent维数不是唯一解释。
- **idea来源：** 科学增量应追问表示保持什么功能，而不只看向量是否接近。E37把persona编辑对原生利益方向的作用与动作JS分开，可从此获得更严格的解释工具。
- **距离与竞争解释：** 人格并非单一目标，NPC还涉及角色规范／身体需求／同伴响应；本轮不把“功能等价”改名为NPC新理论。需要实际跨角色／场景预测与控制证据，这篇提供可复用的原则和强基线。
