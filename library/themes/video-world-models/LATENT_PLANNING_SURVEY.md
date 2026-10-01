# 紧凑潜在世界模型与规划：系统调查及驻留地图

调查日期：2026-10-02。用途：选择一个能持续建设和实验的 workbench，不是宣布论文 idea、新现象或 SOTA。资源条件见 [RESOURCES](../../../RESOURCES.md)；登记对象见 [workbench](../../../workbench/latent-world-model-planning/README.md)。

## 0. 结论与证据边界

建议登记 **latent-world-model-planning：紧凑世界模型的表示、动力学与决策可靠性**。以 LeWM 原生复现环境和 stable-worldmodel 的公共接口为底座，保留冻结视觉特征、端到端表示、结构化动力学、不同规划器及 goal-conditioned RL 对照。

选它不是因为“预测准不等于规划好”还没人研究，恰恰相反：这已成为明确谱系。价值在于这里有可访问的模型内部、可重置的仿真环境、训练数据、成功判定和多个不同设计假设，可以在同一底座上反复建设、比较、修复和理解。

本轮完成了主要谱系与近期近邻的文献调查、关键实验协议阅读、部分官方仓库和配置核对；**没有运行 GPU 训练／规划，没有下载验证全部权重，也没有逐条核验全部理论证明。** 文末逐篇标记阅读范围。不能把本轮写成“已复现”或“全领域所有论文已读完”。

旧主题页的 world-model/video-generation 热度数字是宽切片，不是 latent planning 的接收率。本轮没有运行本地 venue corpus，因此不编造窄切片热度、完整 10 篇接收＋5 篇 near-miss 统计。该项保留为驻留 D5 的定位补充，不妨碍先登记可建设的领域。

## 1. 先比较研究平台，而不是猜现象

以下是基于文献和资产的**研究配置建议**，不是性能排名。

| 可驻留领域 | 现成支点 | 能独立铺开的实验 | 资源／科学边界 | 本轮处理 |
|---|---|---|---|---|
| 紧凑 offline latent planning | LeWM、stable-worldmodel、JEPA-WMs、RC-aux | 同模型换 planner；同数据换表示／动力学；多训练种子；目标与环境条件 | 图像数据和 CEM 评测仍可能昂贵；已有直接后续工作 | **选为一个 workbench** |
| Offline goal-conditioned learning | OGBench 的环境、数据、GCBC／GCIVL／GCIQL／QRL／CRL／HIQL | 数据覆盖、goal stitching、状态／像素对照 | 换成 RL 并不能自动解决数据覆盖或得到“正确 oracle” | 作为同一平台的数据与非 WM 对照，不另开线 |
| Online reward-driven world models | TD-MPC／Dreamer 系谱；SWM 有相关接口 | 交互数据量、重规划、任务表征 | 环境交互、replay 与训练耦合更强；与 reward-free 离线结果不可直接排名 | 保留扩展，非首轮依赖 |
| 大型机器人／视频预训练模型的局部适配 | JEPA-WMs 发布的大模型与小模型路径 | 冻结模型的局部头、任务迁移 | 数据、视觉 token 和评测成本增加；部分与现有视频主线重叠 | 小平台有明确需要时再引入 |

支点出处：[P03][P05][P06][P13]。不要求同时实现所有分支。首先建设共享资产，让不同研究动作能复用，而不是同时新建四个 workbench。

## 2. 五条谱系，以及 idea 如何从前提改变中长出来

这里的“生长路径”是 **RECONSTRUCTED：根据论文论证重建**，不是声称知道作者真实产生想法的过程。论文自己的实验、方法和明确局限才是 DOCUMENTED。

### A. 从未来特征预测到可训练、可控的表示

DINO-WM → PLDM／LeWM → SMWM。

冻结视觉 encoder 使预测目标稳定，但继承的视觉表示未必针对动作；端到端学习可以调整表示，却必须避免塌缩。LeWM 用简化的预测＋分布正则训练；SMWM 则用动作反推约束表示应保留什么。[P01–P03][P08]

**可迁移研究动作：** 把“有信息”“能预测”“被 planner 用到”拆开，而不是看到一个线性 probe 高分就说表示足够。不要把 SMWM 已做的 inverse-dynamics/action-relevance 当作新空白。

### B. 从欧氏接近到任务相关几何

终点 latent distance → value-guided／Temporal Straightening → RC-aux／ATLAS。

几篇工作改变的不是同一东西：价值距离、局部轨迹曲率、有限预算可达性、边际分布与关系几何分别施加不同约束。[P04][P07][P12][P14]

**可迁移研究动作：** 对照这些约束在什么条件下等价、互补或冲突。不是再泛泛证明“L2 不好”，而是从实际任务、训练分布与下游选择中找出哪个约束有用，以及原因。

### C. 从局部预测到递归动力学

单步监督 → 多步 rollout／系统配方分析 → SALT。

多步训练在推理时匹配递归输入，但不等于“步数越多越好”；JEPA-WMs 已系统研究这一选择。SALT 再改变 transition family，使对当前状态的误差传播具有显式结构。[P06][P11]

**可迁移研究动作：** 将状态信息、预测残差、传播结构、历史输入和重规划分开；不能将只针对当前 latent 的 Jacobian 结论直接扩成完整有记忆系统的稳定性结论。

### D. 从低预测成本到可信的候选动作

终点成本搜索 → RC-aux 可达性打分／ACID 动作一致性 → LeFlow 生成候选与再验证／HWM 多尺度搜索。

这些方法分别改变 scoring、候选产生方式或时间层级。[P04][P09][P10][P15] 相同 forward model 给自己的候选再次打分，不等于外部环境认证。

**可迁移研究动作：** 固定候选集合查 scoring，固定 scoring 查 proposal，再查闭环执行。这是诊断接口，不是提前宣称某个 verifier 必然失败。

### E. 从一条示范的未来到覆盖、拼接和迁移

离线轨迹目标 → OGBench goal stitching／SWM 标准化变因 → 新的表示与规划可靠性研究。[P05][P08][P13]

**可迁移研究动作：** 同轨迹的未来目标、跨轨迹组合、视觉扰动、动力学变化、缺失历史，不能统称为一个 OOD 难度。小平台可以分别操纵这些变量，再观察方法是否真的改变了边界。

## 3. 核心论文卡与 claim ownership

### P03 — LeWorldModel

- 原文：稳定、端到端的 JEPA；预测损失与 SIGReg；公开小模型、控制数据和评测入口。原论文约 15M 的模型计数，不能与 RC-aux 的 scoring-module 18M 计数混用。
- 形态：训练设计简化＋广泛任务验证；它是实验底座，不是我们的正结果。
- 研究动作：先复现强配方，检查它成功解决了哪些旧问题；不预设需要更复杂的 loss。

### P04 — RC-aux

- 原文：multi-horizon open-loop prediction＋预算条件 reachability；规划时可选软折扣。轨迹时间差是代理标签，不是真实最短可达时间；跨轨迹负例也不是环境不可达证明。
- 证据边界：5 个固定评测组不是 5 个训练种子；LIBERO action-head 迁移不是 CEM 规划实验；cost-call timing 不是完整 episode／训练耗时。
- 已占叙事：有限预算可达性校正与训练／规划两端使用。简单“再加可达头”不构成新定位。

### P05 — stable-worldmodel

- 原文与代码：统一数据收集、训练、模型预测控制评测；支持多种模型、solver 和环境变因。
- 重要近邻：平台本身已经比较预测误差、任务成功和分布变化。只做“预测误差不相关”散点图或重做通用平台，不是尚未有人触碰的贡献。
- 对本仓库：优先复用接口和标准协议，区别“搭工作台的必要工程”与“需要论文 claim 的贡献”。

### P06 — What Drives Success in Physical Planning with JEPA-WMs?

- 原文：系统比较预测训练、动作条件、上下文、视觉 encoder、proprioception、规划优化器及规模；公开模型／数据。
- 证据：最终模型有训练重复；不同任务目标生成与指标不完全相同，不能用一个平均数替代设定核对。
- 已占叙事：配方选择的广泛经验研究。新增少量 sweep 需要解释增量，而不是因“我们也测了”宣布发现。

### P07 — Temporal Straightening

- 原文：通过局部时间曲率塑造 latent trajectory；有线性动力学条件下的分析及不同表示／规划设置。
- 代码证据：官方 UPDATES 记录过 global-projector 因果 mask、配方与 baseline 更新。作者报告修正后趋势保持；不能据此声称论文整体失效。
- 已占叙事：轨迹几何与规划优化的联系。我们的机会要来自实际比较中的新边界，不是换一种曲率指标。

### P08 — SMWM

- 原文：前向预测与单步逆动力学共同学习感知；受控环境与多任务验证。局限涉及动作非唯一、缺失动态信息、行为相关的外生因素和未来任务需求。
- 形态：成熟训练信号重新承担表示学习作用＋受控诊断。
- 研究动作：研究何时“动作可识别”与“任务状态充分”分离，但首先核对已有局限与实验，不能直接改名为新问题。

### P09 — ACID

- 原文：给既有 world model 配逆动力学一致性信号，在规划中纠正候选；跨模型与任务验证。
- 已占叙事：动作一致性 verifier／reranking。单纯再训练一个 inverse head 不新。
- 我们的分析：循环一致性与真实可执行性应作为两个可分别测量的量，而不是相互定义。

### P10 — LeFlow

- 原文：在冻结 LeWM 的 latent 空间生成候选路径，利用逆动力学得到动作，并用 world model 再 rollout 筛选。
- 已占叙事：生成式候选＋模型验证；不能把 proposal/search 路线当成尚未存在。
- 研究动作：相同候选池上比较评分、相同计算预算下比较提案；区分内部验证和仿真执行。

### P11 — SALT（2026-09-27）

- 原文：state-affine transition＋递归训练；四任务，自己的实验使用单 H100 80GB。主表受控比较是一套训练模型、多评测种子，不代表完整多训练种子可靠性。
- 理论边界：当前状态 Jacobian 诊断省略了历史输入通道，原文明确承认。
- 已占叙事：一步准确性之外的传播结构与轻量 transition 改造。必须纳入新近邻，不能停在 5 月 RC-aux。

### P12 — ATLAS（2026-09-28）

- 原文：边际 Wasserstein 匹配＋以 encoder patch 表示为锚的关系几何保持。
- 边界：定理中的 regret 是 anchor-geometry regret；不附加条件就不能换成环境真实回报。其实验 OOD 划分也不能直接等同于新视觉／新物理环境。
- 已占叙事：分布正则与关系结构的区别及其规划用途。这里只登记近邻风险，不据此关闭领域。

### P13 — OGBench

- 原文／官方实现：offline goal-conditioned RL 的多环境、多数据与六种 reference algorithms；支持像素和状态输入；明确研究 goal stitching。
- 对本工作台：提供非 WM 竞争基线及任务生成选择，防止把所有失败都归因于 latent world model。
- 边界：学到的 Q/value、有限离散图距离和示范时间差都不是任意连续控制任务的 ground-truth 最短路径。

## 4. 可以持续探索的压力地图

下表是**有来源的探索入口，不是观测结论，也不是六个必须完成的新算法**。第一入口无产出，可以在同一资产上移动。

| 分支 | 文献压力 | 先建设的测量／对照 | 能长出的论文形态（尚未形成 claim） |
|---|---|---|---|
| 表示与任务信息 | P03/P08/P12 对“什么必须保留”答案不同 | 已编码真未来的目标排序；probe 与实际选动作分开；冻结/联合学习 | 表示设计＋边界解释；充分性构念＋干预 |
| 动力学与递归 | P04/P06/P11 对训练步长与模型结构做不同修正 | 相同动作下开环误差；匹配物理时间的 horizon；历史、重规划拆开 | 结构化预测方法；误差归因＋修复 |
| 候选产生与打分 | P04/P09/P10 已有不同 verifier/proposal | 记录候选池；分别比较 score、proposal、selected rollout 的实执行 | 搜索方法／校准；选择错误的识别方法 |
| 数据与目标组合 | P04 代理标签、P13 goal stitching | 固定样本量改变覆盖／轨迹连通；WM 与 GCBC/QRL/HIQL 的配对任务 | 数据机制与训练设计；目标泛化边界 |
| 历史与控制接口 | P06 上下文、P08 单帧局限、P11 历史通道 | 帧跳、action block、历史可见性明确；真状态对照 | 信念状态／接口训练；可识别性与失败修复 |
| 分布变化 | P05 FoV 与 P12 距离划分不是同种 shift | 外观、物理参数、目标位置分别操纵；禁止同时改变所有变量 | 鲁棒表示／适配；有解释力的跨域评价 |

关于方法：不是必须先发现“反常大效应”才允许改训练。可以复现一个成功方法、发现它在新测量上的优点，再设计更简单或更普适的实现；需要实际证据支持每一步，而不是禁止动手。

## 5. 科学规模与投稿定位

本轮只判断有建设空间，不承诺题目已经达到顶会标准。优先考虑的最终形态是：

- **失败／边界＋可验证修复**：不是一个小环境涨点，而是清晰地区分失效原因，方法在不同模型或任务条件下解决同一瓶颈。
- **表示／动力学设计＋解释性证据**：强基线、相同资源、简单结构，解释哪些信息或几何性质改变了决策。
- **新的识别／测量问题**：指标必须经过受控阳性／阴性对照和真实任务后果验证；相关性散点图不足以支撑因果结论。

只换 benchmark、只扩大一个已知现象的 n、只给 RC-aux 多加一项损失，都有 compression risk，但不是研究领域的自动死亡理由。目标会议以 ICML／ICLR／NeurIPS 为主，视觉贡献足够时考虑 CVPR；尚无确定稿件，不填写未核实截稿日。

## 6. 阅读范围与可追溯来源

标记：**A** 主文方法／实验并核对关键协议或局限；**B** 针对性章节／接口阅读；**C** 导航／背景，尚不计精读。A 不等于所有附录证明逐字验证。会议状态未经官方核实时不升级为“已接收”。

| ID | 论文／材料 | 本轮范围与定位 |
|---|---|---|
| S01 | [World Model for Robot Learning: A Comprehensive Survey](https://arxiv.org/html/2605.00080v1) | B，taxonomy；不作为方法有效性证据 |
| S02 | [World Models for Robotic Manipulation: A Survey](https://arxiv.org/html/2606.00113v1) | B，任务与模型分类 |
| P01 | [DINO-WM](https://arxiv.org/abs/2411.04983) | C，谱系；代码入口经 P03/P06 核对 |
| P02 | [Learning from Reward-Free Offline Data: A Case for Planning with Latent Dynamics Models](https://arxiv.org/abs/2502.14819) | C，PLDM 谱系；不声称完整复现 |
| P03 | [LeWorldModel](https://arxiv.org/html/2603.19312v1) | A，主文＋训练／评测附录；官方 README/config |
| P04 | [RC-aux](https://arxiv.org/abs/2605.07278) | A，用户上传 v1 主文与实验附录；官方 README/config |
| P05 | [stable-worldmodel](https://arxiv.org/html/2605.21800v1) | A，平台、实验及研究接口；官方 README |
| P06 | [What Drives Success…](https://arxiv.org/html/2512.24497v4) | A，方法与主实验；指标相关附录为针对性阅读；官方权重表 |
| P07 | [Temporal Straightening](https://arxiv.org/html/2603.12231v2) | A，方法／实验／理论适用条件；官方 README、UPDATES |
| P08 | [Sensorimotor World Models](https://arxiv.org/html/2606.20104v1) | A，方法、实验、limitations |
| P09 | [ACID](https://arxiv.org/html/2607.02403v1) | A，主文方法与实验；未完成全部训练成本审计 |
| P10 | [LeFlow](https://arxiv.org/html/2608.24855v1) | A，主文；附录和 checkpoint 仍需接入审计 |
| P11 | [SALT](https://arxiv.org/html/2609.33595v1) | A，主文、比较协议与关键理论限定；非本地复现 |
| P12 | [ATLAS](https://arxiv.org/html/2609.36333v1) | A，主文与定理／OOD 定义；匿名代码未执行 |
| P13 | [OGBench](https://arxiv.org/html/2410.20092v2) | B，goal stitching／评测与官方 README；[ICLR 2025 proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ecd92623ac899357312aaa8915853699-Abstract-Conference.html) |
| P14 | [Value-Guided Action Planning with JEPA World Models](https://arxiv.org/abs/2601.00844) | C，几何支线；恢复此支线时先完整阅读 |
| P15 | [Hierarchical Planning with Latent World Models](https://arxiv.org/abs/2604.03208) | C，层级支线；公开的小型实现与完整论文覆盖不可等同 |
| P16 | [Causal-JEPA](https://arxiv.org/abs/2602.11389) | C，object masking 支线；mask 不是自动获得真实因果干预 |

[P01]: https://arxiv.org/abs/2411.04983
[P02]: https://arxiv.org/abs/2502.14819
[P03]: https://arxiv.org/html/2603.19312v1
[P04]: https://arxiv.org/abs/2605.07278
[P05]: https://arxiv.org/html/2605.21800v1
[P06]: https://arxiv.org/html/2512.24497v4
[P07]: https://arxiv.org/html/2603.12231v2
[P08]: https://arxiv.org/html/2606.20104v1
[P09]: https://arxiv.org/html/2607.02403v1
[P10]: https://arxiv.org/html/2608.24855v1
[P11]: https://arxiv.org/html/2609.33595v1
[P12]: https://arxiv.org/html/2609.36333v1
[P13]: https://arxiv.org/html/2410.20092v2
[P14]: https://arxiv.org/abs/2601.00844
[P15]: https://arxiv.org/abs/2604.03208

## 7. 尚未完成，而不是默认为完成

强基线数值复现；数据／权重实际下载与哈希；完整版本兼容矩阵；本地单任务显存和 wall-clock；窄切片 venue-corpus 查询与 near-miss 校准；扩展论文 P14–P16 全文阅读。它们进入后续资产和实验账本，不伪装成本轮已有结果。
