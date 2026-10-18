# Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork

规范记录：`jing_2026_icrl4aht`；ICML 2026, PMLR 306:54278–54319; official proceedings identity verified。实际版本：Official PMLR ICML 2026 PDF, 42 pages; arXiv 2605.24423 not substituted for official text。

**实际阅读范围：** Complete main text §§1–6, PDF pp.1–9; Tables 1–7 and all main diagnostic figures; Appendices A–B and C.1–C.2 pp.15–26: environments, teammate families, source RL setup; Appendices E–G plus batch formats pp.31–42: architecture, expert action relabeling, scale/budget, all additional diagnostics and limitations; Source/data infrastructure remainder pp.27–30 not fully read; code not executed; no real-human study in paper

[原文](https://raw.githubusercontent.com/mlresearch/v306/main/assets/jing26d/jing26d.pdf) · [发表／主源信息](https://proceedings.mlr.press/v306/jing26d.html)

**稳定 ID：** `jing_2026_icrl4aht`。ICML 2026，PMLR 306:54278–54319正式42页PDF。**实际阅读：** 完整主文§§1–6（1–9），A–B/C开头（15–26）、E–G及batch格式（31–42）；27–30数据基础设施部分未完整读，未执行代码。作者名单以正式PDF为准，与后来arXiv索引存在差别，未混写。

ICRL4AHT将搭档泛化与布局泛化拆为两轨。OvercookedV2每人仅5×5结构局部视野，起点随机、配方交付后改变，正确+20错误−20，某些地图需付−5按按钮看10步配方。训练伙伴每图80个来自FCP/BRDiv/LBRDiv/CoMeDi检查点，测试四类规则搭档各5实例：配方感知、区域领地、流水线和贪心实用。搭档在整段测试固定，不与ego同时学习。六个已见布局测未见伙伴；另两组地图对将信息指示器或锅/交付位置改变，同时仍用未见伙伴。

每布局约11.96亿原始转移筛成1.495亿，记录PPO从差到好的完整学习史。AD仿动作提升轨迹；DPT用最终PPO重标专家动作、context推断后预测响应。默认4层256维、500步context、20k更新；扩至12层768维/100k、context 10k、加队友真值动作、CNN+GRU、AMAGO离线目标等。测试每伙伴100回合，表误差是5个伙伴实例均值间标准差，**不是五训练种子**。困难test_wide H1上AD−18、DPT−23.4、随机0，很多简单地图H4下大家都近40，主要由有能力伙伴独自推进。后20回合减前20回合增益普遍小；已见族的保留RL伙伴较好但仍无明显适应。没有真人实验、没有预训练商业LLM基线，LLM扩展明确列未来工作。

该负结果的重要性在反对“历史更长就会学会合作”的宽泛假设，并提供可控分布变化。它不能证明一切ICRL/Transformer本质失败，或已排除感知、数据覆盖、目标标签和任务能力耦合：增加伙伴动作信息仍不是补全全局隐状态；Hamming距离高也不证明必须显式推断、不能通过稳健规则成功。正文个别数字解释有错误，§5.1称DPT/AD/随机总体为12.4/9.1/5.5，与表3分布局及表7全图总均值对应不符；§5.3 +TA改进/退化方向亦与表5不符。因此记录表格具体条件，不照抄作者因果措辞。

CooT不能直接反驳此文：前者在全状态旧环境与偏好池用专门伙伴最佳响应训练，后者局部观察、新配方、强RL→规则外推，还有新布局；两篇没有同接口同数据的直接比较。真正领域问题是何种训练/观察/反馈足以学到可外推的响应结构，以及表现提升何时来自伙伴、稳健静态策略或真实在线适应。

**主源：** https://proceedings.mlr.press/v306/jing26d.html ； https://arxiv.org/abs/2605.24423

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [CooT: Learning to Coordinate In-Context with Coordination Transformers](WANG_2026_COOT.md) | CooT 用专门伙伴最佳响应监督并有真人实验；ICRL4AHT 的离线学习史、局部观察和规则伙伴外推暴露了另一组边界。 |
| [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](WANG_2024_ZSC_EVAL.md) | ZSC-Eval 的静态跨伙伴分布分数不直接证明在线适应；ICRL4AHT 另看连续回合前后提升及伙伴自身贡献。 |
| [Building Cooperative Embodied Agents Modularly with Large Language Models](ZHANG_2024_COELA.md) | CoELA 使用预训练商业语言模型与高层合法工具；ICRL4AHT 没有商业 LLM 对照，不能把其负结果扩展到这些模块化系统。 |
