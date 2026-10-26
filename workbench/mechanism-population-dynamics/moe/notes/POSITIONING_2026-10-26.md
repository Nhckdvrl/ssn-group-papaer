# MoE 近邻定位补充（2026-10-26）

## 本轮执行前检索补充

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
