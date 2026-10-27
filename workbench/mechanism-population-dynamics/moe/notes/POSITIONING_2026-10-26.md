# MoE 近邻定位补充（2026-10-26）


## 2026-10-27全文复核后的当前研究判断

本轮已通读EMO 25页、MirrorMoE 20页、Training-Free Halving 9页、OptEP 23页、Myth 31页、MoE Lens 15页的正文、全部附录与参考，另查看关键图表、核对EMO实际选择/评测及Lens代码。PDF与逐页记录在NFS的moe_primary_reading_20261027，具体SHA见reading_progress.json与PRIMARY_READING记录。此前的标题/摘要定位表保留为检索快照，不能充当贡献天花板。

**我们的主线是解释学习如何组织实际计算。** 现有数据已经把历史、组织约束与功能后果接起来：固定接口中拆开训练来源会改变预测；成熟模型中预算稳定性、任务正确率和完整质量由不同参数配套承载；共同成熟父状态之后，两个退火终点的条件/共享依赖沿不同方向演化。这支持把职责理解为学到的函数与协作关系，并继续研究它们怎样形成、哪些计算需要共同保留才能重用。不是等相邻工作留下某个小空隙再定义问题。

| 完整阅读的工作 | 由全文建立的连接 | 我们现在能推进的科学问题 |
|---|---|---|
| [EMO](https://arxiv.org/html/2605.06663v1)，含A–D | 文档pool、选择部署、退火与§6微调子集再整合已经构成积极的模块发展路线；不能再说它只研究静态子集选择 | 独立执行、独立维护和跨历史重用需要哪些函数/上下游配套？来源交叉与父状态比较直接测这种组织，而不是改名争定义 |
| [MirrorMoE](https://arxiv.org/html/2610.22353v1)，含所有证明与B的对照 | 共享专家影响探索，训练路径改变最终标准routing下的性能；其主实验也用Z=1，和本窗口接口相近 | 在shared结构固定时，学习历史如何改变实际能力依赖和可组合性？R/S必要性、来源转移与任务读数提供不同于仅有无shared或门值熵的识别 |
| [Training-Free Halving](https://arxiv.org/html/2609.04575v1)，含A/B | 分开计算选择与增益、用实际能力验证推理配置；其结果说明部署行为包含计算规则影响 | 规则控制后仍存在的可用计算由什么学习变化携带？E152证明B优势在full分母下保留，E153继续给出任务层来源证据 |
| [OptEP](https://arxiv.org/html/2610.27123v1)，含A–D | 联合选择、函数补偿与固定其余部分的R更新有实测价值；可用职责并非不可调整 | 学习历史先形成了什么协作与依赖，使同容量子集表现不同？我们的目标是识别既有组织的来源与重用条件，同时吸收它关于函数可塑性的证据 |

**当前自己的叙事：** 任务约束并不直接规定每个命名expert独立承担什么；训练组织会选择一种实际计算的分担和配套。E153显示预算稳定性与完整质量可以部分分离，E154把明显依赖重排定位到成熟退火区间，E155证明这些差异进入能力所需的计算路径。同一44道共同成功题的事后逐题分析更具体：P原20道仅D+R可保持的题，在B有13道变为分别去R/去S都会失败、1道变为仅D+S可保持。选择部署变得有效的同时，成功决策可以更依赖协作。这把“角色”落到了同一语言决策的干预依赖，而不止专家编号、负载或知识标签。

E156已在固定成熟接收者中识别了可单独携带低敏感性的R函数：受限答案NLL改善.188177，同时full NLL增加.080179，准确率优势未同时迁移。原生shared必要性不能直接定位这项性质的载体；共源R/S配套有完整预测收益，却没有同样的子集收益。下一步把已有任务子集真正回插到保留其他专家的系统，检验可部署边界能否充当跨历史重用边界。关键图由成熟父状态/两后代、配对任务依赖和共同接收者来源矩阵组成；E148/E149的短程弱兼容性效应提供历史剂量边界，不必把所有旧实验串成每一步都必然成立的机制。

E157已完成该回插，保留P其余专家使B/P完整NLL比整bank改善.055469，shared的正确来源仍取决于接收背景，准确率保持尚未证实。于是更重要的下一问题是具体输入区别怎样在路径间分担：E158设计固定事实实体/属性互换、同末token与匹配标签对照，在相同成熟谱系里直接测内容中介。它吸收Basic-Refinement的积极问题，同时把历史、实际必要性和所传递区别分开；不是以更多来源/预算小网格补故事。完整EMO从头1T的同配置资产已只读确认，历史实际init未核实，暂不自动扩模型。

**证据与理论的关系：** 参数来源的因果干预不等于完整训练机制已识别；而尚未证明唯一单位，也不削弱已经测到的职责组织与任务后果。C14的本设定事实已完成12项混杂审计、升至L2。更广的任务/初始化规律是要积极推进的研究目标，不是因为相邻论文存在而提前放弃的主张。

**E156期间新增完整阅读：** Sparsity Moves Computation v2（33页）有真实消融/patching与active-width、random-routing强对照；Beyond Routing（21页）有跨初始化表示motif；Basic-Refinement（ACL2025，16页）有shared/routed的真实任务干预与head→expert干预。它们把架构压力、表征稳定和合作机制连接起来。我们的推进点是固定架构/每token激活数后的成熟历史可变性、同一成功决策的依赖转移、以及固定接收者下哪些函数可共同重用；不是再次认领一般“专家会合作”。全文后的具体区别与可借鉴动作见[论文卡](../../../../library/themes/moe-routing/FUNCTIONAL_ROLES_FULL_READING_2026-10-27.md)。原始全文与小型覆盖manifest共9篇193页，数据结论仍由实验给出。


## 本轮执行前检索补充

**2026-10-27更新（E152完成、E153运行中）：** 再跑venue nearest（training history / shared computation / pruning normalization），并回近期arXiv原文核对[Training-Free Halving](https://arxiv.org/html/2609.04575v1)与[OptEP](https://arxiv.org/html/2610.27123v1)；[阅读范围与距离](../../../../library/themes/moe-routing/RECENT_PRUNING_DISTANCE_2026-10-27.md)。归一化与激活选择分离、PPL和能力读数分离、子集联合重构均有明确ownership，不能当E152或Γ的新机制。当前增量仍是成熟历史来源下路由/函数/始终激活计算的性质转移与配套边界；这些近邻不等于已经回答它，也不触发关线。

本轮重跑 venue corpus nearest：`MoE expert router coupling component recombination training history`。召回 ERC、PASs-MoE、FURINA 等；回一手页面核对，不把分数/接收标签用于科学判决。最新 arXiv 另查到 10-20 的 NR-SAE。当前增量必须落在**同一个原生语言接口下，跨训练历史、合法来源重组与完整预测后果的连接**，不能认领一般的 router–expert 耦合、专家复用或逐专家重构。

| 近邻与本轮阅读范围 | ownership / compression risk | 与本轮的具体距离 |
|---|---|---|
| [ERC，ICLR 2026 官方摘要](https://proceedings.iclr.cc/paper_files/paper/2026/hash/79ff18412c1a5816f071a796375abc3d-Abstract-Conference.html)，只核对摘要 | router 表征与专家激活耦合的训练方法已有直接工作；高风险于泛称“让路由匹配能力” | 本轮不提出耦合损失；区分配对历史终点的 bank/gate 兼容性，不能据摘要断言它没有相关消融 |
| [PASs-MoE](https://arxiv.org/abs/2601.13020)，只核对原摘要 | 持续学习里 router/expert co-drift 与保留已有研究；高风险于一般“共同漂移破坏分工”叙事 | 对象为多模态 MoE-LoRA 的连续任务；本轮是同一总函数目标/接口的重复学习与交叉使用，不观测时间轨迹 |
| [The Router Already Knows](https://arxiv.org/html/2610.27421v1)，10-20 预印本，读 §1–2 与摘要限制 | 原生 expert identity 帮助分量重构已有直接结果；不能认领专家身份有重构价值 | 其明确未检验下游损失/因果忠实度；E144直接重跑下游，且问跨学生拆散来源，不是 SAE 效率或语义解释 |
| [MoRE](https://arxiv.org/abs/2609.18176)，只核对原摘要 | 跨层专家池复用属于成熟可用研究动作 | 不是不同训练来源的重组；仅作更大研究空间参照，不当最近的同主张先例 |

本轮重读 [Routers Learn the Geometry](https://arxiv.org/html/2605.12476v1) §2–3 后发现接口适用限制：其掩码先于激活的叙述不能直接用于 OLMoE 的完整 softmax 后截断/不重归一。具体梯度和 CPU 核对在[方向文档](../RESEARCH_DIRECTION.md) §4.1；这是推导适配，不是以论文差异认领新机制。

> **历史定位快照。** 用户经后续讨论已确认方向并授权整理与初步设计。本文保留原检索范围，当前母问题、补充近邻与 E144–E146 设计见 [研究说明](../RESEARCH_DIRECTION.md)；旧建议不自动构成运行队列。


**范围：** 按 E130 固定目标下的跨训练功能对应与 E132 bank readout 检索；用 venue corpus 最近邻、MoE awesome / DailyArXiv 镜像发现来源，再回原论文核对。以下是 claim ownership 与 compression risk 地图，不作新颖性裁决。

## 五个相关近邻

| 来源、日期与阅读范围 | 已占据的主张 | 对当前问题的 compression risk |
|---|---|---|
| [Beyond Routing: Characterising Expert Tuning and Representation in Vision Mixture-of-Experts](https://arxiv.org/abs/2605.20610)，2026-05-20，v1。读 §4 的跨初始化表示稳定性、附录 A.4 RSA。 | 视觉对比学习 MoE-CNN 的 E=4/8/16、top-2 配置各训练 10 seeds；对 THINGS 图像读出建 RDM、跨模型×专家做二阶 RSA，得到重复出现的 animate/inanimate 表征簇，即使 top-k 选择的专家对不同。 | **高**：笼统说“独立训练可重现组织但不重现专家编号”已被直接展示。距离在于视觉任务/表征几何；本项目读固定 LM 下一词任务中的 held 条件注入/移除效应，不把聚类结构直接称为计算职责。[原文](https://arxiv.org/html/2605.20610) |
| [On Linear Mode Connectivity of Mixture-of-Experts Architectures](https://arxiv.org/abs/2509.11348v2)，v2 于 2025-10-25 修订。沿用既有审计：读正文 §1–6、附录 E–G；本次复核 §6.1 与 G.2/G.3。 | 在预训练 GPT-2 / ViT 冻结骨干上用随机 MoE 替 FFN，只训练 MoE；每配置 3 个随机种子，置换匹配后测试低损失线性插值。占据冻结预训练骨干上插入 MoE、重复初始化及权重匹配/LMC 的实验设置与 claim。 | **高**：不能认领“冻住预训练体、插随机 MoE、多种子”本身。该工作回答解空间的损失连通性，不测固定语言读数上的专家函数/自然承担，也不说明低损失连通代表职责相同。[原文](https://arxiv.org/html/2509.11348v2) |
| [Expert Divergence Learning for MoE-based Language Models](https://arxiv.org/abs/2603.00054)，2026-02-10；ICLR 2026。读 §3.2、§4.1–4.3（路由分布损失与路由扰动）；未独立复核附录证明。 | 用语料 domain labels 最大化不同域平均路由分布的 Jensen–Shannon divergence，3B/8B/15B 从头训练；单模型内打乱 router rows 后看 ΔPPL，声称对领域路由与专家非互换性作训练时引导。 | **中高**：占据“显式目标可诱导专家差异/功能专化”与单模型路由扰动读数。检查范围未见独立初始化之间的职责对应；其领域分类路由目标也不等价于无标签 C07 重复数据或跨种子重现。[ICLR 页面](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0c8f0ede04b01a976bedd97cfc2df37d-Abstract-Conference.html) |
| [Expert Merging: Model Merging with Unsupervised Expert Alignment and Importance-Guided Layer Chunking](https://arxiv.org/abs/2509.25712)，2025-09-30；ICLR 2026。读 §3.2、§4 与附录 C.4。 | 冻结 base 与多个 task expert，用 5–10 个无标签 calibration 样本学习层/块系数，使合并模型的 hidden states 与 logits 对齐各专家。占据“少量校准输入可做多专家输出行为对齐”的一般方法主张。 | **中高**：E132 不宜把“用校准集读出/对齐多个专家行为”包装成普遍首创。差异需具体落在相同预训练目标、独立随机初始化的 MoE 子模块，以及预登记的共同输入功能量/held 验证合同；该论文合并的是分任务微调模型。[ICLR 页面](https://proceedings.iclr.cc/paper_files/paper/2026/hash/24dbe8babeca9f372712bbf19dd3584e-Abstract-Conference.html) |
| [FLEx: Personalized Federated Learning for Mixture-of-Experts LLMs via Expert Grafting](https://arxiv.org/abs/2506.00965v2)，v2 于 2025-10-07 修订。读 §4.2、§5.1/5.3。 | 在冻结预训练 MoE 中，按客户端本地数据选一个最能重构原专家集合输出的专家，作为个性化 graft，再联合训练新 gate 与个性化模块。 | **高（就 grafting 这个动作）**：校准/重构驱动的 MoE 专家 grafting 已有直接先例。其 claim 是联邦非 IID 个性化与知识保留，不是同一语言目标下跨训练 seed 的功能对应；venue corpus 将它列为 ICLR 2026 Withdraw near-miss，仅记录状态，不以状态作科学判断。[原文](https://arxiv.org/html/2506.00965) |

## 已有近邻复核与范围

- [Data Scarcity and Model Sparsity v2](https://arxiv.org/abs/2609.11917v2)，2026-10-07 修订；按既有卡读 §5.1–5.2、附录 A.5/B.1。作者报告重复数据下路由在早期稳定、专化读数随重复率变化，另报告 5 seeds 的训练/验证与任务指标方差；这些不是跨 seed 功能对应。对 C07 的任何普遍“重放必然造成某种功能记忆”措辞属**高 compression risk**，需限定本次等 token / 固定数据流与直接功能读数。[§5.1 HTML](https://arxiv.org/html/2609.11917v2)
- [When Are Experts Misrouted?](https://arxiv.org/abs/2605.07260)，2026-05-08 v1；按既有卡读 §3–5。固定单个模型，同 token 比较标准路由与等计算备选路由，并做 router-only probe；它占据“被路由专家未必是当下最有用专家”和反事实 route utility，不是跨训练专家职责重现。
- [RouterInterp](https://arxiv.org/abs/2610.11775)，2026-10-08 v1；按既有卡读 §3–5、§7。其 superposed-specialization 解释把专家看成细粒度特征包而非单一宽领域标签；它是代理标签/特征包 claim owner，不是跨 seed 功能因果读数。
- [DeepSeek-V3 Technical Report v2](https://arxiv.org/abs/2412.19437v2)，2025-02-18 修订；读 §2.1.2、§4.5.2–4.5.3、附录 C。此处 auxiliary-loss-free balance 是用动态 bias 控路由负载，并比较 domain-wise expert load；“专家负载分布更偏”属于路由频率/专化代理范围，不能替代函数、预测贡献或跨训练对应。

## 检索入口与输出

- 执行 `python3 ../../tools/venue_corpus/query.py nearest "MoE expert functional reproducibility training history expert bank grafting"`。返回的高相关已接收条目包括 *Expert Divergence Learning*；近错配中 *FLEx* 以 expert grafting 被召回。排序和接收状态只作定位。
- 按 [`AWESOME_LISTS.md`](../../../../library/sources/AWESOME_LISTS.md) 检查 SuperBruceJia / XueFuzhao 两份 MoE list：前者主题覆盖 expert merging、random assignment、balance；XueFuzhao README 仍以早期模型/基础论文为主。当前页面检索未找到上述 2026 arXiv ID，列表只作发现入口。
- DailyArXiv 镜像检查：zachysun README 标示最后更新 **2026-10-19**，zezhishao README 标示 **2026-10-23**；搜索其页面未命中 RouterInterp、Data Scarcity、Beyond Routing 等 ID。镜像有日期滞后且按关键词保留有限篇数，未命中不表示没有先例。

**读者边界：** 这些来源已占据若干一般设定、代理或方法动作；现有检索并未判定它们覆盖了 E130/E132 的固定 LM 目标、共享骨干、seed/顺序隔离、U/A/T 直接功能读数及 held 计分组合。是否足以形成论文增量仍由 root / 人审判断。


## E134必要性检查后的新增发现入口（2026-10-26）

按“uniform routing / averaging / expert redundancy”搜索后回原文核对两篇，详细阅读范围见根library同日论文卡。Rethinking Routing Exploration（2610.22353v1，10-15）已拥有显式共享专家影响占优、随机路由敏感性与探索障碍的诊断；Coherent Overlap（2607.28308v1，07-30）已用冻结路由增添/替换证明几何重叠不能判定预测价值。E134与前者的显式共享架构、后者的输入线性子空间不同；这种距离只是定位，不自动构成论文增量。若继续做随机路由或均匀分量检查，须作为当前跨训练问题的诊断，不再包装一般“路由/几何不等于功能”的发现。未做新颖性自动判决或改线状态。

## E139前的新主问题定位（2026-10-26；held新结果前）
- 当前主问题：固定表示、原生总函数目标与预算，总函数监督及额外输入分配信息分别把跨训练实际计算分解约束到何种程度。不是认领蒸馏、路由指导或匹配算法。
- 已运行venue corpus nearest检索 `Mixture of experts functional decomposition reproducibility across training fixed routing function matching expert identifiability`；出现Union-of-Experts（ACL2026 Main）、Expert Divergence Learning（ICLR2026 Poster）、The Illusion of Specialization（ACL2026 Main）等。检索相近不等于全文或精确撞车，具体跨seed功能内容尚未在本轮重读；热度/分数不作去留判决。
- 新近邻RRD：作者实验室官网列ICML2026 Workshop，官方代码README可读，含dense拆分MoE、teacher magnitude-topK路由指导、中间输出恢复、共享专家。论文PDF/新版本全文受403未核对、后续正式接收未确认。**Compression risk：** 若把E139写成“teacher routing helps recovery”，会被已有方法压缩。应检验配对free/fixed协议下共享teacher偏差、学生总Y变异与实际component变异的分离；是否形成足够增量仍待数据与人审，不自动判死。出处/边界见根library当日RRD卡。
- 经典可识别性近邻2402.02952v2、2309.13850v2已核对所记章节：dense确定性回归的strong-identifiability与topK条件混合密度并非当前finite-budget BF16 neural block的无条件保证。反之，也不能预设sum-only监督天然结构不可识别。自主充分条件推导及适用限制见`MOE_IDENTIFIABILITY_SCOPE_2026-10-26.md`，未认领理论新颖性。
- E139使用actual-component cal-MSE Hungarian仅为单一预定商置换工具，既有REAP/REAM/activation matching ownership保留；seed1锚定不穷尽所有对应、非三模型joint最优。所有matched free/fixed结果和函数差均报告，不做teacher恢复准入。

- DailyArXiv两入口检查：zachysun/main可读但更新止10-19；zezhishao/main README为404，不作完整最新覆盖声称。由前者发现2610.22127并回原arXiv摘要核对：个性化MoE/paired crosscoder/行为恢复与expert boost，全文未读。它约束一般“可干预专家功能”ownership，当前仅带边界定位，卡已记。

## E142前：初始路由因素的ownership边界
- 当前反事实是同expert/RNG/cache/总Y/预算，仅把各自随机gate改为同一份seed1随机gate；主读数是跨训练actual分解，而非首次研究初始化或提出新路由算法。
- 再读 [Routers Learn the Geometry of Their Experts](https://arxiv.org/html/2605.12476) v1的引言/§2–3：已拥有matched router/expert梯度沿输入方向累计历史、aux改变几何耦合及centroid routing的叙事。不能把一般“路由与内容共同演化/初态影响训练”当首创；本题增量只可能来自配对初态/固定原生函数需求下的跨训练功能分解、选择与维持的控制。
- [LibMoE OpenReview](https://openreview.net/pdf?id=PB2ju8tq0n)在primary检索摘要中声称分析轻量router初始化对early utilization/load balancing与训练regime稳定性的影响；正文受浏览器403未读，不据摘要断言是否有跨seed职责证据。其完整定位待可读正文，当前仅记录近邻与compression risk，不作精确撞车/去留判决。
- Drop-Upcycling/UpIT等已有专家或路由初始化/上采样方法，搜索命中不代表本轮已读全文；本项目不认领初始化方法创新。E142一个共同随机gate的结果也不自动推广所有gate、所有自然预训练或数学可识别性。

## E144–E147结果后的增量边界

本轮实际确认：固定gate拆散学生来源有真实预测代价，共同接收者下历史相关兼容性仍不同，保留特定组能优于随机同大小分组。但强gate-only组取得与Γ组相近收益，未检出Γ额外优势。因而不认领协方差聚类、共激活图、一般co-adaptation或天然语义模块发现；已有router–expert耦合、专家聚类/合并、可组合接口工作的ownership仍成立。

较具体的候选增量是把配对训练历史、同接口内的合法重组和完整预测后果接起来，并用较简单的gate结构竞争解释约束其边界。当前仍是单teacher层的受控pilot；需要自由gate/原生学习的前瞻证据才可能超出局部窗口，不因这项竞争解释吸收了一部分故事而自动关线。

## E148原生窗口的解释边界（分支完成之前）

本轮回原始[OLMoE报告§5.1–5.2](https://arxiv.org/html/2409.02060)重读，已有中间checkpoint路由饱和与共激活分析；5000步/20B的部分层对终点Top8保留已可达约60%。因此E148是在既有组织上检验继续学习的可塑性与历史响应，不能把它写成分工从无到有。候选增量需落在同父等曝光的次序处理、共同后缀与合法组件移植后果，而非首次发现路由稳定/共激活。我们的FA继续学习也不冒充原报告optimizer复现。阅读范围与idea来源见[本轮论文卡](../../../../library/themes/moe-routing/OLMOE_NATIVE_HISTORY_CARD_2026-10-26.md)。

## 2026-10-27：成熟协议资产与真正需要区分的模块性质

E148/E149已经显示：高于精确repeat的预测残留，并未自动成为稳定或不可组合的组织。下一步不靠自行加训练剂量产生损伤。新检索读到[EMO正文及Appendix B.4](https://allenai.org/papers/emo)、[发布代码](https://github.com/allenai/EMO)和实际HF集合，确认标准1T后不同50B退火协议的成熟权重确实已发布；原生GPU尚未运行。来源/pins及精确阅读范围见[论文卡](../../../../library/themes/moe-routing/EMO_MATURE_ASSET_CARD_2026-10-27.md)和E150卡。

| 近邻 / 阅读状态 | 已拥有的主张或资产 | 我们应区别的对象 |
|---|---|---|
| EMO，正文§1–3/B.4 + 官方代码实际读过 | 文档pool组织约束、原生域级选择、同模型内子集使用/组合；成熟标准及协议分叉 | 跨公开历史的来源兼容性；受限计算性质能否由router、routed expert、shared expert或dense接口分别转移。不能偷换其“组合”定义再宣称反驳 |
| Routers Learn the Geometry，前次已读 | router/expert共同演化、梯度几何与aux耦合 | 不认领一般耦合或初始化影响。必须是具体受控/公开历史下的功能后果 |
| 最新venue corpus nearest命中的Coupling Experts and Routers、Read-ME、Tight Clusters | 本轮仅检索标题/库记录，未新读原文；接收标签只是检索地图 | 一般耦合、解耦、聚类不是可直接认领的新点；不据标题或热度自动判定本题重复/关线 |

**Compression risk：** 仅展示16格完整NLL，容易退化为一般模型拼装敏感性。E150在任何原生GPU读数前补强了固定prefix预算下的suffix pruning损失，相对每格自身完整预测配对，并把shared单列。它直接区分完整质量与受限计算可用性；仍不自动识别语义封装，masked-softmax尺度适应与支持路径都须保留解释。若native性质本身没有出现，不以更换预算/任务救阳性。新颖性仍需具体结果与近邻全文校对，没有自动判决。

### E150/E151后重新核对的ownership

回读[EMO §3.2/4.1/A.2–3](https://allenai.org/papers/emo)：它已明确区分127 routed+1 shared，训练pool内重归一化、变pool大小与shared的益处都有作者证据；我们的接口核对与预算收益不能重新包装成发现。回读[Rethinking Routing §2.2](https://arxiv.org/html/2610.22353v1#S2.SS2)的个体专家零化、逐层随机routing和shared作用，已有一般shared重要性及routing不敏感性诊断。不能把E151泛化成首次发现共享路径或首次测专家必要性。

当前更具体的候选增量是：在**同shared架构、公开成熟协议历史**之间，通过dense/router/routed/shared来源交叉识别可转移性质与配套边界，并把完整质量、随机预算鲁棒性、输入选择价值及依赖配置分开。我们的B gate独移不转移预算收益，R/S/D配套与依赖配置变化比单看route集中更有解释力。结果只是一个声明同父协议包、语言窗口，尚未证明域级语义单元、普遍形成必要性或独立seed规律。

最强竞争解释仍是路由分母/尺度适应、一般删减鲁棒性与始终激活计算补偿；E151支持后两者参与，同时保留R实际作用和prefix选择优势。下一证据应检验原始任务/独立输入及normalizer保留门值操作，而不是靠新增相关性图或层扫描扩大故事。与EMO/MirrorMoE的差异需围绕这些具体识别方式，不据接近或热度关闭方向。

**2026-10-27接口再核对：** [MirrorMoE §2.2](https://arxiv.org/html/2610.22353v1#S2.SS2)的ExpertVar上界显式要求按selected概率质量归一化；本原生127全softmax后top7不满足这个条件，不能直接移用该界。若以缺失门值质量补一个零函数，才可重新写成凸组合，且必须把shared-only输出也纳入比较点；这只是数学接口检查，不能据层内界推出下游NLL或训练形成。[FURINA摘要](https://arxiv.org/abs/2509.14900)里的“merge”指MoE-LoRA折叠进骨干，并非跨训练终点组件互换；本次仅核摘要，不据标题把它当同一识别问题。

### 同一问题的另两条连接：完整阅读与代码核对

- [Myth of Expert Specialization](https://arxiv.org/abs/2604.09780v1)，31页全文：从线性router、表示几何、生成前后差异解释专家usage。Fig.6涉及60个生成模型写出的数学轨迹与3个MoE分面；“同一MoE重放所有轨迹”最符合设定，但具体实现原文未明确，不能写成已核实的跨独立权重对应或已核实重放。其几何关系与我们的任务/历史问题是共演化连接，不构成二选一；来源干预要进一步看函数与真实预测。
- [MoE Lens](https://arxiv.org/abs/2603.05806v1)，15页全文及作者notebook：PPL来自改变所有MoE层top-k后的整网前向，确有预测评测；局部LogitLens另行读出。整网保留shared与残差，当前公开native配置不重归一化；notebook未锁历史HF revision，历史版本未确认。它提示“少数R足够”应同时交代始终激活计算；E155用R/S/D完整因子直接测实际任务，E156继续检验历史形成的函数配套能否重用。

两者的明确接口、未确认项和源行号见[Terra只读代码核对](../results/reading_terra_code_check/NOTE.md)。此前将Myth重放说得过于确定已纠正。这里没有以标题的相近或“已有专家专化”否定母问题，也不把近邻简化成只有相关性/没有真实预测；我们的方向由自己已经取得的计算分担、共同成功任务和功能迁移证据推进。
