# MoE论文形态与领域位置（2026-10-29：两成熟谱系与增益竞争解释）

本页记录C14已完成证据的价值、领域位置与论证中心，不改变正式状态或代替人的投稿品味。当前等级与运行阶段统一见[README](README.md)。目录整理、全文再定位、E164新55科实际路由交叉和E165成熟OLMoE扩展均完成。本轮另完整阅读7篇164页及OLMoE附录L两页；[英文论证稿](paper/main.pdf)及四幅关键图已连接两谱系的来源—使用分离。E166增益竞争解释已预注册，尚无新条件读数。

## 走到了哪里

| 阶段 | 已实际获得 | 在整条研究中的位置 |
|---|---|---|
| E120–E134 | 测量校准、路由/函数/替换区分、有限受控重复实现与必要性 | 解决如何测，暴露指纹不等于职责；不是最终论文全部叙事 |
| E135–E147 | 原生接口残差有预测作用；总计算较稳但分量可变；拆来源有预测代价；强gate-only解释 | 证明分解/配套可被测，尚未识别内容联盟；数学恒等式不是新机制 |
| E148/E149 | 原生短历史响应但无强配套断裂 | 区分预测变化与组织兼容；保留阴性，不追加剂量救结果 |
| E150–E162 | 成熟训练路径的R/S实际依赖重排，任务成功次集、性质载体转移，固定函数/信号的伙伴作用 | 已进入原生系统的因果解释研究；仍非完整形成动力学/独立初始化总体 |
| E163 | 同函数/同输入真实消息交叉，norm/Gram校正后仍保留大部分预测代价；四native方向代理全量保留 | 把消息配套推进到特征干预，削弱所测局部几何主解释；不是任意方向破坏即机制 |
| E164 | 全部55个新MMLU学科440题，函数来源×实际路由交叉；固定路由仍保留预算NLL收益与同函数伙伴作用差 | 排除这两份分离仅由诱发的路由变化实现，同时保留函数–轨迹交互；并非孤立expert自治 |
| E165 | 成熟OLMoE父→普通退火，native预算损伤+.105 [.002,.206]，但专家单独移入P在固定P路由下改善.223 [.146,.302]；D来源变化抵消改善 | 整机部署曲线可掩盖组件可迁移性质，另一无shared谱系复现来源—使用分离；P16准确率约22%，不作部署收益 |
| 更高层缺口 | 其他成熟训练谱系是否重复这些分离，真正分叉中关系何时形成 | 不用更多同端点importance、层或方向网格冒充一般性/形成过程 |

## 价值与可认领的增量

母问题：任务与学习历史怎样共同选择专家职责、协作及可重用计算。

已有三条可组合的正面论证，而非把所有历史卡拼成故事：

1. **相近成功有不同实际分担。** F/B完整raw同39.06%、文本NLL接近；F prefix损伤更低，却S移除文本代价额外1.851 [1.331,2.301]。四模型共同成功40题的共同必要8/10/20/24。任务S删除准确率F−B仍未区分；不把loss叫能力比例。
2. **必要伙伴不是性质载体的同义词。** 固定P D/G，R_B携带受限NLL改善.188 [.115,.264]，但完整品质不随之迁移，S_B单独未携带同样性质。它解释为什么选择部署的成功不能直接推出跨背景重用。
3. **历史选择的作用关系可以在函数不变时改变，且不只是所测局部幅度接口。** 固定S_P换R_B使S作用+.339；实际S轨迹交叉有.261 [.223,.298]NLL原配收益。E163保持消费者clean norm及对当前背景的投影后，仍有.245925 [.209580,.281916]代价，只改善.014602 [.004968,.024973]。实际消息方向与接收背景仍需配合；准确率校正差尚未区分，不把loss当能力恢复。

领域会因此多知道：**训练能让MoE更容易选择部署，同时形成更强的伙伴依赖；可迁移性质的载体又不必是原生预测中最必要的伙伴。** 这是同一套成熟系统中可以实测的分离：B/F选择更稳却更需要S；R_B能带走低预算性质，完整能力没有随之迁移；相同S函数的实际消息也没有因简单几何校正而通用。评价“模块化”若只测route、裁剪drop或单支重要性，会把这些不同关系混在一起。

我对价值的判断：已经超过工具搭建和某checkpoint微小异常的阶段，足以组织成一篇有清楚发现的机制论文。主贡献应是上述分离及其来源/消息干预证据，而非另造一个“专家有交互”的名字。E163是重要竞争解释的检验，增量有用，但不是单独的主发现；四模型任意方向替换的巨大损失也不应占据故事中心。

这不是已经完成“所有MoE的单专家语义职责规律”。当前单位多为16层R/S套件，单专家/最小组、独立预训练初始化总体仍开放。公开历史声明和输入CI不能代替严格训练分叉链或seed总体，但不取消已完成干预的因果信息。

## 放在领域整体的哪里

| 领域方向 | 一手工作已有答案 | 我们当前对应的对象和区别 |
|---|---|---|
| 可解释架构与语义可编辑性 | Monet有架构创新、真实域/语言删除；不是只有描述 | 固定成熟架构下，组织历史选择的分担与来源重用；不认领monosemantic新架构 |
| 路由/几何与核心组织 | Myth、Beyond Routing、Standing Committee有真实组织测量，后者也有mask干预 | 实际路由读数、功能性质与预测依赖分开；固定函数/消息测试伙伴作用 |
| 模块化训练和部署 | EMO有组织约束、选择部署和子集再整合；CartesianMoE/ExpertWeaver有真实性能方法 | 分析这些目标为何未唯一规定实际分担，以及不同训练来源可带走什么 |
| Router–expert耦合训练 | ERC有3B/15B真实预训练和任务收益，已讨论专业化–合作权衡 | 成熟模型中哪个函数套件带走性质、预测使用依赖哪些伙伴；载体识别与实际路由介导分开 |
| 跨训练表示与参数兼容 | Stitching研究低容量对齐后的功能兼容；LMC-MoE含末层/全层及shared变体 | 不从raw graft损伤断言根本不同；区分具体性质的载体、原配和局部消息接口 |
| 因果电路与条件作用 | Hydra/Self-Repair/CoAx/Dose/WISE与新MoE审计已有真实冻结/补位/集合干预 | 一般conditional importance非新点；成熟学习历史、正常成功系统与可重用消息结构是组合增量 |

前批新增9篇全文224页，连同更早16篇429页的定位；本次再核对5篇100页及AAAI补充源码，不把相邻工作当自动天花板。逐篇对象、方法、假设、idea来源与未核对项见[全文卡](../../../library/themes/moe-routing/GLOBAL_POSITIONING_FULL_READING_2026-10-28.md)及[ERC补读](../../../library/themes/moe-routing/ERC_FULL_READING_2026-10-29.md)。检索由venue corpus、最新arXiv与awesome/DailyArXiv交叉；最新镜像覆盖滞后，不声称穷尽。

ERC全文后更明确的界定：R_B在共同P gate参数下能带走选择性质，定位了受控干预中足够的参数包来源；其实际执行仍可能经过后续routing反馈。现有载体结论保留，不把它改写成“expert能力独立于真实路由”，也不因已有耦合训练方法就放弃对成熟实现与使用关系的识别。

## 论文形态与关键证据

- 本轮主图：[选择与依赖](paper/figures/01_selection_and_dependence.png)、[固定实际路由的性质与伙伴](paper/figures/02_property_and_partner_under_fixed_routes.png)、[实际消息重用](paper/figures/03_actual_message_reuse.png)、[整机趋势与组件迁移](paper/figures/04_native_trends_and_transport.png)，53项既有估计逐项绑定[JSON路径/SHA](paper/figures/figure_sources.json)。[英文论证稿](paper/main.pdf)是可审阅论证，不是投稿或候选状态。
- 历史总览：[四面板主图](results/e163/figures/research_spine.png)及[逐项来源SHA/JSON路径](results/e163/research_spine.json)。这是事后组织已预定估计及原CI，无新检验；各原实验保留完整来源/任务/正确率，不能用总览替代完整证据。
- 一句话主旨：MoE的可选择性、性质可迁移性与实际计算可重用性可以分离；训练组织与历史选择了不同的伙伴使用关系。
- 形态：机制发现与受控干预；不以新指标、协方差恒等式或普遍“专家有交互”为新贡献。
- Manuscript-critical：上述三条C14实证（L2），以及E163对局部norm/投影解释的直接检验；不把现有解释扩大为已识别最小语义单位或完整形成机制。
- 主图1：E151/E152/E155/E162，同架构成熟历史、完整品质、随机/两分母、相同成功分担；完整主样本与次集并列。
- 主图2：E156/E159，函数来源与必要伙伴的交叉，完整品质和受限性质分别画，不只展示有利格。
- 主图3：E160/E163，固定函数/实际消息的原配、norm/Gram校正后保留的代价；实际27格完整获得。分科NLL/choice CE及正确率并列，不能只画有利的宏NLL。
- 最强竞争解释：路由选择/一般鲁棒、局部幅度/投影、可学习坐标接口、原生共同适应。路由选择、实际路由响应、一般鲁棒和所测局部几何已有直接区分；更丰富的坐标对齐与任务计算差异仍未区分，不能把raw或Gram失败称固有不相容。实际路由响应参与、但不是性质迁移或伙伴作用变化的全部解释。
- 证据标准：两个公开成熟谱系，EMO另有全程路径扩展；64语言窗口/20文件簇、旧两学科128题，加新55学科440题；各项输入CI条件于模型，不是seed总体。全部条件、失败与来源只读保留。无shared的OLMoE不追认为全部R/S结论复现。
- 目标：优先ICML/ICLR/NeurIPS主会的机制/理解形态；语言计算内容若成为中心，可考虑ACL/EMNLP主会。不参考EACL、不投Findings，不据未核截止日排日程。

## 已有结果可支持的中心段落（英文草稿）

以下依据已完成E150–E164；其中新任务扩展和实际路由控制由E164提供：

> We ask how learning history shapes the division of computation in sparse MoE models. Using mature, architecture-matched checkpoints, we find that better selective execution can coexist with stronger dependence on shared computation, even at similar intact quality. Cross-source interventions show that the function package carrying a low-budget predictive advantage need not be the component most necessary in its native model. Holding shared-expert functions and then their realized messages fixed reveals that predictive roles depend on production and use, with substantial mismatch costs remaining after local geometric correction. On a predeclared panel of 55 additional subjects, both the low-budget probability-quality advantage and the increased reliance on unchanged shared functions persist when realized routes are held fixed, while route-source interactions further shape the advantage. These findings separate selective deployment, transportable properties, and reusable computation. Accuracy gains from the transported property remain unresolved.

## E163怎样改变判断，为什么此时收束

E159/E160同时允许“配套主要是幅度/残差投影关系”与“还需要输入条件的其余方向结构”。E163的真实消息交叉给出区别：norm/Gram有小幅NLL收益，但代价绝大部分保留；Gram相对norm的总体额外收益CI含0，生物改善、数学不改善，choice CE和正确率不提供同等恢复。支持剩余方向—背景约束，不支持把两标量当足够接口。

Native块同时保留全部模型、R/S/合计、mean与两个固定Gaussian，均未恢复原生预测；F合计Gram/mean有部分恢复而非“全都比zero差”。它防止把shared依赖直接化成所测局部几何代理，但不单独回答语义内容。所有见证仍包含原计算；没有免计算压缩/维数或跨训练seed总体主张。

现在增加更多方向、层、相似性或donor不会显著提升核心解释。当前优先把三条论证写清、给出可追溯主图与复现入口；E158/E161作为内容组合的真实边界，E144/E147作为受控分解及强对照，放在支持位置，不强行把所有历史卡拼成同一机制。

## E164后的论证中心与下一决定

**最强的新陈述：在固定实际路由的共同接收者中，迁入的R_B既携带更稳健的低预算预测，又提高对未改共享函数的依赖。** 更容易选择部署和更依赖伙伴可以在同一受控系统中共存，不只是比较两个checkpoint的重要性分数。

55个新MMLU学科全部440题中，P32答案NLL自然改善.420699 [.322082,.523391]；固定P/B实际路由后仍改善.293673 [.202723,.390380] / .382397 [.290367,.474614]。因此该性质不要求R_B先改变后续实际路由才能实现。与此同时，同S_P的移除代价差自然为+.362754，固定P/B路由仍为+.289102 [.210363,.364510] / +.183971 [.116895,.246087]。不能再用“只是gate选了不同expert”解释全部伙伴作用变化。

路由并非无关或天然通用：B轨迹在R_B上额外改善P32 NLL .127026 [.087709,.166712]，在R_P上改善.038302 [−.004178,.081169]；交互−.088724 [−.124167,−.050014]。完整质量的自然NLL反而增加.174602 [.119613,.232475]。性质载体、完整品质与伙伴关系仍是不同对象。固定路由仍允许S、attention和hidden-state响应改变，不把剩余效应单归孤立expert或换算唯一中介比例。

P32 choice CE改善1.138554 [.843067,1.467601]，表明不只是真实答案绝对似然读数；raw准确率+1.14pp [−2.27,4.55]、per-char+1.36pp [−2.50,5.23]均未区分优势。主张围绕预测概率质量、选择部署和依赖关系，不写成已经提升任务准确率。所有逐科反向结果保留；新旧面板同时改变任务和cal样本数，不能把效应幅度变化单归于任务。

### 与最近邻的具体距离

[五篇完整比较](../../../library/themes/moe-routing/FUNCTIONAL_TRANSFER_AND_ROUTING_2026-10-29.md)确认：stitching确有特征迁移/steering/任务表现，直接匹配与invariance约束确有强反例，router–expert训练耦合也已有方法与性能证据。我们不认领这些一般概念。增量是**在同一成熟MoE研究中，识别选择性质的参数来源、未改函数的伙伴作用，以及实际路由/消息使用怎样实现二者的分离**。E164无需训练adapter，改变的是已运行通路；它补的是现有参数移植不能识别的环节，而非另造对齐方法。

同S_P的写入基底已经固定，学习任意补偿映射可以回答可对齐/可利用性，却不单独解释原职责；这不否定对齐本身的科学价值。一般共同适应已有先例，我们的可检验论证是成熟组织目标下这些性质怎样分离、哪些分离经控制实际路由后保留。

### 当前优先级

1. **形成紧凑论文论证与主图。** 用E162的选择–依赖、E156/E164的性质来源–运行通路、E160/E163的实际消息重用构成主干。三个预定指标层次并列，完整矩阵及失败放可复核附录；不把每张历史卡都升级为独立贡献。
2. **检验一个能简化整篇解释的竞争模型。** E165的native/组件反向趋势与旧native几何共同提示幅度重分配。E166在两谱系只用预定cal的同输入响应，闭式匹配16个统一R增益，比较真实预算性质与EMO同policy的S作用；不优化预测损失，不扫增益。E163检验S消息校正，不等于已经排除R的增益解释。
3. **该批后集中形成论证。** 不自动增加层、方向、selector或adapter容量网格。真正分叉/中间快照仍是形成机制的重要后续，不用同端点局部扫描冒充一般性，也不默认自训多seed。

[完整E164协议/结果](experiments/E164-runtime-routing-property-transport.md)、[来源主图](results/e164/figures/source_effects_NLL.png)、[固定路由伙伴图](results/e164/figures/shared_partner_role.png)及[独立复算](results/e164/independent_audit.json)均完成；1.444648 GPU时，最多1卡、0新训练，C14保持L2。真正形成分叉与独立初始化总体尚未获得，端点不反推完整动力学。正式候选、投稿与工作台状态仍由人决定。

## 本轮尺度选择与跨谱系决策

最合适的尺度是**成熟MoE中，可选择的函数怎样通过伙伴关系实现预测，以及哪些性质/计算可以跨历史重用**。以训练历史为入口，以参数来源、实际路由和消息为逐步识别通路；既不只讲一般交互，也不提前认定单专家语义单位。三条实证是递进论证，不是三种互斥“模块化分数”。

新增全文HOPE/CD-MoE/SD-MoE及AoE、Super Experts、Massive Activations、ME Layer共164页的[具体距离](../../../library/themes/moe-routing/SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29.md)强调：合作能帮助部署、早层大激活及全局条件信号已有真实预测干预证据。我们的增量是成熟历史下识别性质载体、未改函数角色改变和实际使用通路。E164中S作用在full测、预算优势在P32测，不能补造“shared补偿造成预算收益”的因果连接；E166会直接填这一逻辑缺口。

已完成的[E165](experiments/E165-mature-olmoe-selection-transport.md)选择另一明确成熟父→普通退火、无常驻shared，优于Qwen3仅一个成熟端点，也优于跨2.5T大跨度的原样移植。OLMoE0125只核实同first-stage data mix，精确共同父未核实，不称控制分叉。结果不是“所有迁移都更差”：完整D×MoE原配NLL代价.027 [.021,.034]，P16匹配代价CI含0；专家低预算性质可迁移而整机趋势变差，支持来源与运行背景分别识别。该项含预检.953168 GPU时、最多1卡，0新训练。
