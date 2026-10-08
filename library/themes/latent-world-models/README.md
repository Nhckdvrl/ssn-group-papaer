# Latent world models（紧凑隐空间世界模型）知识库

建立：2026-10-07（接手 `workbench/latent-world-model-planning/` 时重建）。旧的逐篇笔记在该工作台 `literature/CORE_READINGS.md`（75KB，按实验回读写成，不是领域画像）；本页是领域画像 + 谱系 + 角度“所有权”表 + 热度数据 + 开放问题。原始材料：
- [`NEURIPS2026_WM_ABSTRACTS.txt`](NEURIPS2026_WM_ABSTRACTS.txt)：NeurIPS 2026 官方目录中标题含 world model / JEPA / latent dynamics / model-based / latent action 的 144 篇摘要。
- [`ARXIV_LEWM_LINE_2026-10-07.txt`](ARXIV_LEWM_LINE_2026-10-07.txt)：arXiv 上 LeWM / DINO-WM / JEPA+world model+planning 的 120 篇（按时间倒序）。
- [`PAPER_CARDS.md`](PAPER_CARDS.md)：深读卡（idea 来源、与最近邻的距离、我们能借什么）。

## 1. 一句话画像

“从像素学一个隐空间里的动作条件预测器，再在隐空间里做规划（CEM/MPPI/梯度）”这一范式，由 DINO-WM（2024.11，冻结 DINOv2 特征）→ PLDM（2025.02，JEPA 动力学 + 数据质量研究）→ V-JEPA 2-AC（2025.06，真实机器人）→ JEPA-WMs（Meta，2025.12，设计空间研究）→ **LeWorldModel（2026.03，15M 参数、单卡、端到端、SIGReg）** 推到了小组可复现的尺度。LeWM 发布后，这条线在 arXiv 上从每月约 5 篇涨到 **2026 年 9 月约 30 篇/月**（见 §4），几乎全部是“在 LeWM 的 TwoRoom / PushT / Cube / Reacher 四个玩具环境上加一个辅助损失或诊断指标”。

## 2. 问题地图与“所有权”

| 角度 | 领域关心的具体问题 | 已有工作（谁已经占了这个角度） | 状态 |
|---|---|---|---|
| 训练稳定 / 防坍缩 | 端到端 JEPA 不靠 EMA/冻结编码器能否稳定 | LeWM（SIGReg）；Perception for Action（逆动力学防坍缩，NeurIPS26）；Sub-JEPA；QQWorld；No Gaussian Required | 饱和 |
| 隐空间几何 vs 规划 | 欧氏距离不是可达性；预测好≠可规划 | RC-aux（NeurIPS26）；Temporal Straightening（ICML26）；Control-Geometry Straightening；Commute-time；How Long Not How Close；AnisoWM；Traj-LeWM；Temporal-Distance JEPA；ProWorld | 饱和 |
| 代价函数是瓶颈 | 终点 L2 代价使长目标失败 | The Objective Is the Bottleneck；Aim Short to Reach Far；Planning Limits（真模拟器下仍失败）；Ordinal Geometry（NeurIPS26） | 饱和 |
| 动作敏感性 / 动作可辨识 | 隐空间对动作不敏感、预测≈复制 | Keeping Plannable When Little Moves；Delta-JEPA；ATM；AVL-JEPA；MotionJEPA；Velocity Blind Spot；Why Latent Actions Fail（NeurIPS26） | 饱和 |
| 反事实 / 干预保真 | 离线行为数据学不到干预后果 | FIRM-WM；AD-WM；Do-JEPA；Intervention Gap；Low-rank carriers；Causal retention | 饱和 |
| 诊断指标 / 欠约束 | 验证损失不预测规划；同配置不同种子差很大 | VIScore（种子间损失差 ±8%，PushT 成功率 78–92%）；ATM；Control Theory of Predictability；Decision-Metric Alignment；ARC-Bench（重规划掩盖排序错误）；When Low Prediction Error Misleads；Evaluation Protocol Determines the Result | 饱和 |
| 搜索 vs 摊销 | 搜索到底有没有用 | Latent Geometry Beyond Search（GC-IDM 在 8 个设定里 7 个追平或超过 CEM）；RP1 学规划器；INTACT；Surprising Difficulty of Search in MBRL（ICML26） | 正在变热 |
| 搜索被利用（Goodhart） | 候选越多越容易选到模型错的动作 | Imperfect WMs are Exploitable（理论，NeurIPS26）；ASAR proposal overgeneration；RENEW；PROWL | 有人做，未系统 |
| 长时域 / 分层 | 多阶段任务 | HWM（Meta）；H-JEPA（LeCun/Balestriero, 2610）；FF-JEPA；Mind the Gap；Implicit-HWM（NeurIPS26）；Jumpy WMs（ICML26） | 大组占据 |
| 随机性 / 部分可观 | 确定性 JEPA 无法表示多未来 | EpicWorldModel（NeurIPS26）；VJEPA；Var-JEPA；UWM-JEPA；Flow-JEPA | 变热 |
| 测试时适应 / 持续 | 世界改变后如何修正 | JEPA-TTT；Sandwich-Residuals；AdaWM（NeurIPS26）；NeurIPS26 Continual World Models workshop | 新兴 |
| 理论 | 可辨识性、泛化界、各向同性 | When does LeJEPA learn a WM；On JEPA Isotropy；Beyond Isotropy；Generalization theory for JEPA WMs；Identifiability of controlled WMs | 新兴，偏理论组 |
| **规模（模型 × 数据 × 规划算力）** | **规划能力是否随规模提升；训练算力与测试时搜索如何交换** | JEPA-WMs 附带发现：仿真里更大编码器不提升、predictor 深度 >6 变差；Planning Limits：predictor 放大 81× 不扩大可规划范围；World-in-World 有视频 WM 的数据缩放；Pearce 2024 只测 WM 损失缩放 | **无系统研究**（本工作台当前探索方向，见工作台 logs/2026-10-07） |

## 3. 这个范式的“顶会尺度”是怎么长出来的（谱系）

- **换表示**：DINO-WM 把“世界模型是否需要重建像素”改写为“用冻结的预训练特征就够”。
- **换问题**：PLDM 把“哪个算法强”改写为“什么数据条件下 model-based 更好”。
- **换可行性**：LeWM 把端到端 JEPA 从脆弱变成单卡几小时可训，造出公共底座 → 引发 2026 年的论文洪水。
- **换使用接口**：RC-aux 把可达性监督与规划器耦合分开验证；GC-IDM 证明在这些基准上可以不用搜索。
- 共同规律：方法通常不大，增量来自**改写一个设计决定**并用决定性对照证明。洪水中的大量论文只做了“加一个损失 + 四个玩具环境涨点”，没有改写任何决定。

## 4. 热度数据（arXiv，LeWM / DINO-WM / JEPA+WM+planning）

| 月份 | 2026-01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10（前 6 天） |
|---|---|---|---|---|---|---|---|---|---|---|
| 篇数 | 2 | 8 | 5 | 1 | 10 | 9 | 13 | 22 | 30 | 10 |

NeurIPS 2026 目录中与 world model 相关的约 144 篇；与紧凑隐空间规划直接相关的约 20 篇。**结论：工作台 2026-10-02 建立时把它当作“热度偏中低”的领域，而 LeWM 发布后这条子线已经变成滚雪球式的红海。** 按 `search/README.md` 不能据此“桌面判死”领域，但不应再在“LeWM + 玩具环境 + 一个辅助损失”的层面上投入。

## 5. 仍然开放、且我们有比较优势的问题（2026-10-07 判断）

1. **规模科学**：模型规模、数据量、测试时规划算力三者与规划成功率的关系；是否存在“预测随规模提升、规划不随规模提升（甚至反向）”的解耦；训练算力与搜索算力的交换率（类比 Jones 2021 棋类、Gao 2023 过度优化）。需要上百次独立训练，正好用我们“多卡弱互联”的资源结构；小组做不了，大组没做。
2. **摊销 vs 搜索随规模的变化**：GC-IDM 在固定 15M 模型上追平 CEM；随规模/数据增加，搜索的边际价值是增是减？
3. **世界改变后的修正（continual / editing）**：新兴，热度中低，但已有 4–5 篇近邻。备选。

## 6. 资产入口

LeWM 代码与发布权重、stable-worldmodel 环境与专家策略、TwoRoom（10k episodes）/ PushT（18.7k episodes）数据见 `workbench/latent-world-model-planning/ASSETS.md`。64px 低分辨率 GPU 常驻训练管线见 `workbench/latent-world-model-planning/scaling/`。
