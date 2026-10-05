# How Language Models Process Negation（ICML 2026主会；全文部分）

[正式proceedings](https://proceedings.mlr.press/v306/zhou26bq.html)、[arXiv v2正文](https://arxiv.org/html/2605.03052v2)、[代码/数据](https://github.com/Ja1Zhou/LM_Negation)。实际读取§1–4、5.1–5.4、结论/limitations、A.2；5.5与因果图只阅读定义和流程，全部附录未核对。

- **形态/idea来源：** 理论竞争+受控测量+因果解释；从negative-mover与组合表示的两种解释出发，而非从“模型不会否定”出发。
- **数据/动作：** 162概念对×4模板；比较静态属性肯定/否定的候选logit；因果attention sinking与path patching，读中间attention输出的促进/抑制。数据CC BY 4.0、代码Apache2（作者repo声明，尚未download审计）。
- **ownership：** 否定敏感却选错、语义排除与共现捷径并存、construction/suppression竞争已由该工作主张；不能把这些宽叙事当我们novelty。最优层sweep结果不能照搬作普适干预效果。
- **距离/迁移动作：** 其问题是静态类别排除；我们的候选是先前解释历史如何调节同一角色纠正的后续关系利用，须有GP/cue×关系/实体控制及独立材料预测。E22目前是局部概率测量，未建立其机制外的新机制，也不因阅读开始probe/SAE。

PDF v2 21页、1,115,456 bytes，SHA256 `f865969d94eeb13c955511dae2274543fbd82adb706390c258cad436d65a05c0`；无代理下载、全文留cache。公开评审未读，不编分数。
