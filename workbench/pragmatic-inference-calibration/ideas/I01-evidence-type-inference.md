# I01：模型如何归因交际证据，决定何时超越字面？（2026-10-03）

- **状态：SEED。** 不是已识别异常或预注册结果；workbench状态不变。
- **对应：C02 / P02。**
- **来源：** RECONSTRUCTED。ALTPRAG×PaCE提供训练增益与literal-side代价的初始压力；E41/E52显示自然材料中的方向/强度/读数不能归成单一criterion（且存在未排除混杂）。Gibson2013、Knowledge and Implicature2013及较新的RI/SAGE提供可产生不同预测的解释。不是“把两个概念拼起来没人做”。
- **研究动作：重新归因 + 受控干预 + 跨材料定位。** 检验模型是否把不同交际证据都当成泛泛的“更不确定”，还是分别更新信号可靠性、表达选择能力和候选意义的先验；再问post-training改变了哪一项条件关系。
- **值得知道的未知：** 模型什么时候是在合理修复收到的表达，什么时候是在替说话者补上没有证据的意图？这种边界是否随训练改变，而不只随任务平均分改变？
- **如果成立，可支持的主张：** 训练后的语用变化部分来自对证据来源的归因方式。具体方向未定，需原材料、独立识别控制、跨家族/现象证据。概念区别本身不是贡献。

| 最近邻 | 它拥有的解释/证据 | 要测的实质增量（尚未取得） |
|---|---|---|
| [Gibson2013](https://colala.berkeley.edu/papers/gibson2013rational.pdf)与后续semantic-prior研究 | 人类随channel noise、meaning prior、edit structure改变literal解释 | 同一训练谱系是否保留不同来源的条件关系；哪些已有模型“语用进步”结论因此被重新归因 |
| Knowledge and Implicature2013 / EPITOME | speaker knowledge约束备选排除；LLM识别knowledge与使用有缺口 | 把知识限制与表达受损的解释预测相互约束，避免仅再报告knowing-versus-using |
| RI2026 / SAGE2026 | partner-indexed channel理论、跨角色预测；灵活备选生成与模块检验 | 原source上的可检验训练变化及可迁移边界；不是首次提出来源分解/角色统一/新框架 |

**不同结果的信息增益：**

1. 模型保留来源特有的关系，训练又改善这些关系：回到真正的辨别提升解释；测它能否预测独立材料中的合理修复/撤回。成功也必须记录，不转向寻找失败。
2. 证据来源识别控制通过，却在解释中出现共同偏移：优先排除readout、world prior、回答规范和任务难度；若跨材料/家族仍在，再检验来源归因与最终policy两个账户。
3. 关系只随dataset、prompt或候选terminal改变，或人类norm/控制不可用：记录未识别，回到territory选择下一未知；不逐步加限定保护这个seed。

**最便宜的pilot：尚未开跑。** 先审计原noise/semantic-prior材料与human norms；不能拿论文示例充当完整dataset。正式实验卡需在运行前冻结，以下是设计要求而非已完成协议。

- 各来源内固定目标utterance、解释候选与问题，变化原实验的交际证据；跨source的effect不能直接当同一构念的因果差。
- 阳性对照：原人类关键趋势可核对；模型的无歧义理解、证据来源识别和完整候选读数分别可用。全部item保留，不筛模型做对的材料。
- signal fidelity、事实真实性、epistemic access、world prior分别记录；partial knowledge仍可能许可某个推断，不造全局yes/no gold。
- 噪声地板/MIE：取决于原human分布、source数量与重复读数；取得资产后写进实验卡，当前不虚构数值。优先cluster CI与原条件内比较，若无法区分解释则不启动GPU。
- A/B/C分别按上方分支推进；缺资产先补资产，不以更多采样代替识别。

- **预期论文形态：** 重新归因 / 条件结构finding，尚未选择；不把仪器修复或平均分表作为贡献。
- **排序（1–3，仅用于资源顺序）：** 证据1 · 增量清楚度2 · 形态匹配3 · 成本2 · 可完成性2 · 不同结果信息增益3。0成熟贡献，不升C02。
- **当前优先级：** 完成E51真实dense四stage的自然parent边界；并行取得下一source。没有因为新近邻把对象缩到单模型/单prompt，无新的权限缺口。
