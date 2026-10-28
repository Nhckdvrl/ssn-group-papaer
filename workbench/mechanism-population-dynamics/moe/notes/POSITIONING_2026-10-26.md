# MoE文献定位：历史选择的分担与计算重用

当前版：2026-10-28。主问题与实际结论见[RESEARCH_DIRECTION](../RESEARCH_DIRECTION.md)，不把旧检索时的“下一步”当执行队列。本文集中保留具体定位；各论文的细节、idea来源、假设与读后校正在根library论文卡，逐版PDF/SHA在[10-27](PRIMARY_READING_2026-10-27.json)、[10-28](PRIMARY_READING_2026-10-28.json)清单。已完成11篇251页及5篇178页全文文字阅读，包含附录和参考；关键图另有查看记录，不声称所有图逐像素审计。

## 自己的主线

任务约束允许哪些实际分担、学习历史选择了哪一种，以及哪些分担关系能随组件重用，是一个完整的组织问题。现有证据已连接三个层次：成熟历史下相同成功决策的依赖变化；预算性质与完整能力的不同函数载体；固定函数乃至固定信号后仍存在的伙伴作用。贡献由这些具体识别构成，不靠宣称“首次发现专家合作”或寻找相邻工作没用过的小指标。

## 最近的已全文工作：共同问题与实质区别

| 工作与固定来源 | 已有实质贡献 | 我们的连接与待主张的区别 |
|---|---|---|
| [EMO v2](https://arxiv.org/abs/2605.06663v2)，25页；v1全文+v2全文diff及首页复核 | 文档专家池、域级选择、子集部署与§6微调子集再整合，另发布成熟路径资产 | 自模型选择和再整合提供积极路线。我们直接识别不同成熟路径下性质来源、必要伙伴及跨来源重用，不能重新认领选择部署或泛称“首次回插” |
| [MirrorMoE v1](https://arxiv.org/abs/2610.22353v1)，20页 | 共享专家与路由探索的训练机制，有真实必要性/路由干预；主要实验也用1个shared | 同shared架构中，历史仍能留下不同作用关系；接口相近是可连接的科学基础，不是自动重复或自动反驳 |
| [Training-Free Halving v1](https://arxiv.org/abs/2609.04575v1)，9页 | 将选择与归一化分开，用真实任务检验推理规则 | E152的两分母是必要的解释控制。我们的问题是控制推理规则后学到的函数/背景来源，不认领分母影响本身 |
| [OptEP v1](https://arxiv.org/abs/2610.27123v1)，23页 | 联合选择、函数补偿与固定其他部分的R适配 | 支持函数可塑性。跨历史已经学出的性质由谁携带、与哪些系统作用相容，是不同识别问题 |
| [Myth v1](https://arxiv.org/abs/2604.09780v1)，31页；[MoE Lens v1](https://arxiv.org/abs/2603.05806v1)，15页 | 前者连接usage与表示几何，后者同时有局部读出及改变全网top-k后的真实PPL | usage、局部表示和全网作用要分别测。Lens保留shared/残差；Myth的轨迹重放细节未完全确认，不能借不确定实现制造差异 |
| [Sparsity Moves Computation v2](https://arxiv.org/abs/2605.09403v2)，33页 | 受控算法任务中，架构/稀疏分配改变attention–FFN实际分担，含干预和多seed | 架构可用路径与训练后实际依赖有区别；我们固定架构/active k，研究成熟历史选择及已有函数重用 |
| [Beyond Routing v1](https://arxiv.org/abs/2605.20610v1)，21页 | 视觉MoE跨实例的expert表示几何与motif，包含约10独立训练/配置 | 保留跨初始化结构可重复的正面可能。我们的实际预测依赖与合法来源交叉不等于RDM结构，也不冒充更多独立初始化 |
| [Basic-Refinement，ACL 2025](https://aclanthology.org/2025.acl-long.1093/)，16页 | shared/routed、head合作以及真实关系任务干预，已有shared+top1结果 | 合作有直接先例。E155的相同成功、E156/E159的固定接收者干预研究合作如何随历史/伙伴变化，非一般合作首证 |
| [LRE，ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/2b6d7285306fe896fca9b2e9a02ff6ec-Paper-Conference.pdf)，23页；[ROME v5](https://arxiv.org/abs/2202.05262v5)，35页 | 关系读出及因果定位/编辑有成熟识别与任务证据 | 帮助将loss作用落实到内容区别。E158/E161的末位置流交换不能自动定位知识存储，E161未支持跨实体纯关系操作 |
| [Hydra v1](https://arxiv.org/abs/2307.15771v1)，21页；[Self-Repair，ICML 2024](https://proceedings.mlr.press/v235/rushing24a.html)，20页 | 真实补偿、冻结、归一化/anti-erasure及信号回插，跨模型测量 | 条件作用与冻结干预不是新方法。E160的对象是成熟伙伴背景与相同S函数/信号的产生及使用，而非再发现一般非线性 |
| [CoAx v3](https://arxiv.org/abs/2607.01940v3)，41页 | 指定失效下的条件完备性、实际冻结/补位/knockout与多机制实例 | 借鉴对竞争解释的干预。正常成功系统中不同历史分担，以及可转移性质与必要伙伴的分离，是我们的对象；该v3 PDF与摘要数字不一致已在卡中区分 |
| [Every Ablation Is a Dose v1](https://arxiv.org/abs/2610.02173v1)，61页 | 连续剂量、嵌套干预、类对比耦合，含base/instruct比较和强替代拟合 | 训练前后角色比较也非无人做过。其§I.7的重新表达/下游使用问题与E160相接；我们的交叉不给唯一中介百分比或普遍剂量律 |
| [WISE v1](https://arxiv.org/abs/2610.04017v1)，35页 | 集合效应、见证固定、交互敏感排序与必要性/保持/旁损实测 | 正常学习组织的来源与重用问题不同于自动电路发现；不将其缩成相关性，也不重复认领集合必要性指标 |

细节分别见[历史/功能近邻卡](../../../../library/themes/moe-routing/HISTORY_FUNCTION_NEIGHBORS_2026-10-27.md)、[分担/表示/合作卡](../../../../library/themes/moe-routing/FUNCTIONAL_ROLES_FULL_READING_2026-10-27.md)、[LRE/ROME全文卡](../../../../library/themes/moe-routing/LRE_ROME_FULL_READING_2026-10-27.md)、[五篇上下文作用全文卡](../../../../library/themes/moe-routing/CONTEXTUAL_ROLES_FULL_READING_2026-10-28.md)。10-27早期局部阅读卡仍为历史过程，随后全文覆盖以清单为准。

## 最强竞争解释与压缩风险

- 如果只有一张来源交叉NLL表，容易退化为一般模型拼装敏感性。现有证据还包含同任务成功的不同依赖、性质转移而完整能力不迁移、固定未改函数/实际信号的伙伴干预，必须联合论证。
- 如果只说“shared更重要”，会遗漏R仍必要、有用选择与一般鲁棒并存、R_B携带低预算性质、S作用依生产者而异。应清楚展示这些可区分预测，而不将多个读数强压成一个标量。
- E160原配信号更好可能包含普通上下文失配；单独它不足以命名新语义单位。与历史来源、自然/固定信号作用及完整质量联合，才回答学习组织的实现与重用条件。
- 同父公开声明不是批次/optimizer字节链；F/B同最终配方不是时机单变量。更广初始化总体与完整形成过程仍开放，但不是否定现有直接干预的理由。

## 早期近邻、检索与未读项怎样保留

可识别性P2、NTK、LMC-MoE、router–expert几何、Fisher merging、FlexOlmo/BAR等较早定位，以及FLEx、RRD、RouterInterp、DeepSeek等局部阅读范围，保存在[整理前固定版本](https://github.com/Nhckdvrl/ssn-group-papaer/blob/9815fbf0/workbench/mechanism-population-dynamics/moe/notes/POSITIONING_2026-10-26.md)与既有论文卡。未读全文的条目仍未读，不能据标题升级成精确撞车。数学与接口边界见[研究方向](../RESEARCH_DIRECTION.md)及[可识别性说明](IDENTIFIABILITY_SCOPE_2026-10-26.md)。

最近已实际执行venue corpus nearest，ExpertWeaver、CartesianMoE、Coupling Experts and Routers等新命中只作检索线索；Basic-Refinement另有全文阅读，其余不作新颖性裁决。awesome/DailyArXiv的覆盖和日期滞后记录保留在旧定位，不把镜像未命中当无人研究。

**本批决定：完成E162后集中形成现有论证并整理，不自动扩大消融矩阵。** 相邻工作帮助提出完整科学问题；结果决定哪些解释更有力，不能为保持新颖性不断缩成一小块，也不能为了故事忽略已有直接证据。

## 2026-10-28用户授权后全局再定位

新增8篇全文204页（含LMC完整86页、stitching独立附录），与此前16篇的具体主张重新对照。[当前论文形态/价值判断](../PAPER_SHAPE.md)与[新全文卡](../../../../library/themes/moe-routing/GLOBAL_POSITIONING_FULL_READING_2026-10-28.md)明确：当前正面增量在成熟历史、性质载体/必要伙伴及消息重用的连接，不认领一般conditional importance或模块删除。下一E163针对低维几何与方向结构的竞争解释，仍无新结果，不沿旧卡号自动排队。
