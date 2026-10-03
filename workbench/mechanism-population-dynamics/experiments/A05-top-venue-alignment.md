# A05 — 对齐最新顶会（2024–2026）的同类论文：叙事宽窄、条数、novelty、展开顺序（2026-10-03 21:48）

人的目标（2026-10-03 /goal）：仔细对照顶会（尤其最新顶会）的同类论文打磨叙事；不为严谨收窄 claim；实验只为叙事服务。
来源：venue corpus（`tools/venue_corpus/query.py nearest`）+ 全文精读（scratchpad `papers/`）。

## 1. 最新的同类论文怎么写
| 论文（会议） | 一句话命题 | 贡献条数与写法 | 展开顺序 | Fig 1 |
|---|---|---|---|---|
| Mechanistic Data Attribution（ICML 2026 **Oral**） | 用影响函数把可解释头追溯到训练样本；删 / 加少量高影响样本会改变头的出现 | 4 条：框架 / 因果验证 / 机制洞见（含 4 个子发现）/ 实际应用 | 框架 → 验证 → 洞见 → 应用 | 三阶段流程图 + 干预曲线 |
| SeedPrints（ICLR 2026） | 初始化留下与生俱来、终生不变的指纹（Galton 比喻） | 4 条：指出旧方法的局限 / 发现初始化指纹 / 大量验证 / 真实场景 | 问题 → 发现 → 方法 → 验证 → 应用 | 旧方法在早期 checkpoint 失效、新方法从第一个 checkpoint 起就成功 |
| Attention-Head Stability（Bali，ICML 2026） | 同架构同数据重训，注意力头是否相同？ | 5 条粗体名词短语发现：中层不稳定 / 深度依赖 / 功能含义 / weight decay 的作用 / 残差流更稳 | 问题 → 度量 → 发现列表 | 逐层稳定性曲线 |
| Random Scaling of Emergent Capabilities（ICML 2026） | 突变来自 seed 之间结果分布的连续变化 | 一个核心命题 + 3 个场景验证 + 一个应用 | 命题 → 合成任务 → 真实 LM | seed 分布随规模变化 |
| Convergence and Divergence under Random Seeds（EMNLP 2025） | 不同 seed 的收敛呈四阶段；大模型重新收敛、小模型不会 | 一个四阶段模式 + 规模 + 语言学类别 | 定义 → 阶段 → 规模 → 细分 | 四阶段曲线 |
| Differentiation and Specialization of Attention Heads（ICLR 2025 Spotlight） | 用 rLLC 看头如何分化成不同角色 | 3 条：方法 / 头的分化与专门化 / 新发现的回路 | 方法 → 发育 → 新回路 | 头的 rLLC 发育曲线 |
| LLM Circuit Analyses Are Consistent Across Training and Scale（NeurIPS 2024） | 成分会变，算法稳定 | 3–4 条粗体发现句 | 任务 → 出现时间 → 算法稳定 → 图属性 | 跨规模的出现时间 |
| PolyPythias（ICLR 2025） | 资源 + 稳定性 + 离群 seed | 资源 + 3 条发现 | 资源 → 下游 → 表示 → 参数动态 | 50 个 run 的曲线 |
| From Shortcut to Induction Head（NeurIPS 2025 Spotlight） | 数据多样性决定学到 induction 头还是位置捷径 | 理论 + 相变 + 最优分布 + 验证 | 理论 → 预测 → 实验 | 相图 |
| Critical Periods in SSL（ICLR 2026） | 自监督学习也有关键期；关键期关闭时是 OOD 迁移的最佳点 | 发现 + 两种测量 + 两个应用 | 现象 → 关键期 → 应用 | 迁移性随 checkpoint 的权衡 |
| GD with Large Step Size Restores Symmetry（ICML 2026） | 多通路网络早期“赢家通吃”的对称性破缺，之后被 EoS 重新平衡 | 理论 | — | — |
| Do Deep Networks Forget Initialization?（2026 预印本） | Adam 类优化器抹去初始化对功能的影响；SGD 不抹去 | 3 条：相图 / 拟合 ≠ 遗忘 / 遗忘时间尺度 | 诊断量 → 相图 → 机制 | SGD 记得、Adam 忘记 |

## 2. 共同模式 → 我们的决定
1. **宽度：** 被接收的论文要么是“一个大命题 + 多条支撑发现”（SeedPrints、Random Scaling），要么是“一个问题 + 一组并列发现”（Bali、Tigges）。最新的高分论文（MDA Oral、SeedPrints）都把命题写在“LLM / 语言模型”层级，证据来自 1–2 个模型家族。→ **我们写在“语言模型的回路”层级**，主命题是 *The seed picks the slot, the data fills it*，下设 5 条并列发现。
2. **条数：** 3–5 条，每条用粗体名词短语开头加一句话，最好附章节号（Bali、Tigges、MDA）。→ **5 条发现 + 1 条框架 + 1 条应用**，引言中合并为 5 个要点。
3. **novelty 的写法：** 先指出领域的隐含假设或空白（MDA：“MI 仍是静态的”；SeedPrints：“现有指纹不是与生俱来的”；Bali：“电路很少接受跨重训的检验”），再说“我们第一次……”。→ **空白：** 稳定性研究只变 seed，数据研究（含 MDA）只变数据；没有人把机制的哪一部分来自 seed、哪一部分来自数据分开。**“第一次”：** 第一次对语言模型的机制做 seed × 数据的析因分解。
4. **展开顺序：** 框架 → 主发现 → 互补发现 → 机制（何时、为何）→ 边界与规模 → 应用（MDA、Critical Periods in SSL 都以应用收尾）。
5. **与最强近邻的关系写成互补，不写成对立：**
   - MDA：数据决定头的**出现与速度**（他们的“emergence dynamics：高影响样本主要调节速度”）；我们补上：数据**不决定是哪个头**，这由 seed 决定 → 做机制数据归因时，归因对象应是“出现”而不是“位置”。
   - SeedPrints：初始化在输出中留下身份信号（同一组权重的谱系）；我们：初始化决定兄弟模型的回路布局，而功能、权重忘记初始化。
   - Forgetting-Time：Adam 类优化器抹去初始化对功能的影响。我们的模型全部用 AdamW 训练：功能确实忘了（不存在幸运 seed），**布局却记得**。这给“weights forget, roles remember”一个文献上的锋利对照。
   - Tigges / Bali：成分会变、算法稳定；我们说明成分**为什么**变（seed），以及它跨数据被继承。
   - Multi-pathway 对称性破缺理论（ICML 2026）：早期赢家通吃；我们给出语言模型中的经验对应：赢家由 seed 决定，在关键期内确定。
   - From Shortcut to Induction Head：数据决定算法（合成极端分布）；我们：在自然预训练语料范围内，算法普适，数据决定强度与时间。
   - Biderman et al.（2026 立场论文，“AI 科学必须研究训练动态”）：引言动机；我们给出一个训练前 1–2.5% 决定持久结构、且可由 seed 预测的实例。
   - 涌现时间可按 seed 预测（2026）：同一数据配置下按 seed 预测 induction 出现时间；我们：跨语料时出现时间由数据决定（E54），二者互补。
6. **Fig 1 要一眼看懂：** SeedPrints 用“旧方法失败、新方法成功”的对比曲线；Forgetting-Time 用“SGD 记得、Adam 忘记”。→ 我们的 Fig 1：**左：** 3 个 seed × 5 个语料的 1B 模型，同一层的 previous-token 头得分条形图（同一行的模式相同、同一列的不同）；**右：** 决定因素地图的缩略版。

## 3. 定稿叙事（英文要点见 A03 / A04，按本节修订）
**标题：** *The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits*

**引言中的 5 个要点（粗体名词短语 + 一句话）：**
1. **A natural nature × nurture experiment.** 公开套件中隐藏的 seed × 数据析因结构（DataDecide 14 个尺寸、Pythia 到 12B），经审计；决定因素地图把 12 项机制性质分到普适 / seed / 数据 / 交互。
2. **The seed picks the slot.** 同层内由哪个头承担 induction、previous-token、检索等角色由 seed 决定，数据分量为 0；跨 2 个家族、所有尺寸、[E59：更多角色、只看权重的指标]；同 seed 的兄弟模型选中同一个头的比例达随机的 5 倍。
3. **The data fills it.** 回路强度、出现时间、表示内容、基准表现、知识冲突行为都由数据决定，seed 没有主效应（不存在幸运 seed）；1% 的指令数据装入由字面模板触发的开关。
4. **A critical period, then an attractor.** 槽位在训练的 1%–2.5% 内由对称性破缺决定；之后即使加入与权重同量级的噪声也回到原槽位；最终权重几乎不保留初始化（r = 0.04）——weights forget the seed, roles remember it。
5. **Inheritance follows corpus similarity and scale.** 两个语料的低阶统计越接近，槽位继承越强（DataDecide 300 个配方对 ρ ≈ −0.6，每个尺寸都成立；只用不共享数据源的配方对也成立 [E60]）；代码这样的远距离语料在关键期内重抽槽位；规模越大继承越强 [E57 / E58 / E46b2]。

**应用（第 6 节）：** 只看头的布局就能认出兄弟模型的 seed [E61]；成分级结论按 seed 迁移；机制数据归因与模型 diff 要固定 seed；配方比较中共用 seed 不降低噪声。

## 4. 实验只为叙事服务（在跑的与不做的）
- **在跑，直接服务第 2 / 5 条与应用：** E57（规模趋势何时形成）、E58（Pythia 到 12B）、E59（更多角色，广度）、E60 去混杂（共享数据源 vs 统计相似）、E61（解剖学 seed 识别）、E46b2（受控的规模检验）。
- **在跑，服务第 3 条：** E48b（线索替换干预）。
- **不做：** 不再为 C04 开新的机制实验（E52 / E53 已止损）；不追加新的模型家族；不做与主命题无关的探针。
- **可能做（视结果）：** 一个最小的“赛跑”模型（多个可交换的头在相同或不同统计的数据上竞争），用来在一页内解释 seed 选槽、语料距离、关键期三件事——相当于 Achille 的 Fisher 信息、MDA 的影响函数在各自论文中的角色。只有在主体结果定稿后、篇幅允许时才做。
