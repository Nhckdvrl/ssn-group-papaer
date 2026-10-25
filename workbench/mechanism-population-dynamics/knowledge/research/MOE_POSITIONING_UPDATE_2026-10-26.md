# MoE 近邻定位补充（2026-10-26）

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
- 按 [`AWESOME_LISTS.md`](../../library/sources/AWESOME_LISTS.md) 检查 SuperBruceJia / XueFuzhao 两份 MoE list：前者主题覆盖 expert merging、random assignment、balance；XueFuzhao README 仍以早期模型/基础论文为主。当前页面检索未找到上述 2026 arXiv ID，列表只作发现入口。
- DailyArXiv 镜像检查：zachysun README 标示最后更新 **2026-10-19**，zezhishao README 标示 **2026-10-23**；搜索其页面未命中 RouterInterp、Data Scarcity、Beyond Routing 等 ID。镜像有日期滞后且按关键词保留有限篇数，未命中不表示没有先例。

**读者边界：** 这些来源已占据若干一般设定、代理或方法动作；现有检索并未判定它们覆盖了 E130/E132 的固定 LM 目标、共享骨干、seed/顺序隔离、U/A/T 直接功能读数及 held 计分组合。是否足以形成论文增量仍由 root / 人审判断。
