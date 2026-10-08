# Latent World Model Planning｜紧凑隐空间世界模型工作台

**状态：主问题 = I16（人 2026-10-07 同意）；论文级实验 E23 已基本跑完，2026-10-07 22:30 按人要求暂停全部实验。科学主张尚未登记（待独立校对）。**

## 一页结论（2026-10-07 下午）

1. **原方向不值得继续。** LeWM / JEPA 隐空间规划子线 2026-09 约 30 篇/月；前任做过的角度均有同期工作。结构性复盘见 [logs/2026-10-07.md](logs/2026-10-07.md)。
2. **找到的 idea（[I16](ideas/I16-latent-bandwidth.md)，证据见 [E21](experiments/E21-scaling-planning.md)、[E22](experiments/E22-latent-bandwidth-law.md)）：越大的 latent 世界模型，latent 距离越短视。**
   - 同一配方、同一规划器：导航任务随模型变大而变差（TwoRoom offset 50：XXS 72% → M 53%；offset 75：47% → 29%，所有搜索预算一致），操作任务随规模变好（PushT offset 25：17% → 87%）。
   - 机制：失败来自 latent 几何而非预测误差（真实动力学代价同样随规模变差）；L2 度量的带宽随模型规模与训练单调缩短，与 SIGReg 优化程度强相关（Spearman 0.82 / 0.77）。新诊断量“度量视野”：完整 L2 在 TwoRoom / 迷宫约 10 步饱和，PushT 约 35 步，Reacher 约 25–35 步；短于规划视野（25 步）时 L2 规划失败。
   - 修复（不训练）：在 latent 的慢特征子空间里算代价——TwoRoom M 53%/29% → 98.5%/94%；OGBench 视觉迷宫 20% → 88.5%（offset 50）、77.5%（offset 100）。同一 latent 上的 GC-IDM 在导航上 100%，在 PushT 上随规模变好并远超 CEM。
   - 撤回 / 未成立：跨房间切分（坐标轴错）；指数 = −1/状态维数；压低 latent 维度无效；慢特征对 PushT 有害（与方块姿态不对齐）。
3. **还缺：** SIGReg 权重因果干预（在跑）；切换规则的留出验证（Reacher 已一致，Cube / 大迷宫待做）；每格 ≥3 种子；224px 锚点；形式化命题。

## 论文级实验 E23 结论（2026-10-07，详见 [E23](experiments/E23-paper-grid.md)、[日志](logs/2026-10-07.md)）

| 检验 | 结果 |
|---|---|
| 规模 × 3 种子（TwoRoom） | CEM + L2 每十倍参数 −9.3pp（off50，CI [−10.4, −8.0]）；慢特征 / auto 斜率 +1 ~ +4pp，成功率 92–99% |
| 官方发布 LeWM（224px） | 度量视野 TwoRoom 10 / PushT 35 步；TwoRoom 远目标 L2 32.5% → auto 90%；PushT 规则保持 L2 |
| SIGReg 因果（3 种子） | λ=0.01 → off50 80.7%、off75 60.3%（默认 63.2 / 37.7）；λ=0.003 坍缩；λ 减小抬高水平但规模效应仍在 |
| 统一变量 | 规模与 λ 都推高 D_eff；26 个检查点上 L2 成功率对 log D_eff 的 R² 0.83–0.89；E[K²]=1/D_eff，P(K≥0.5)·D_eff 为常数 |
| 留出环境（冻结规则） | PointMaze-large L2 15–20% → auto 82–83%；Cube、visual-antmaze 不伤害（antmaze 上所有方法都失败，控制瓶颈） |
| 迷宫修复随规模 | 补齐种子后 auto 斜率 ≈ 0（−0.2 ~ +2.4pp）；慢特征近似直线距离，需绕墙远目标约 40% |
| 局限 | λ×规模：各向同性压力只解释部分规模效应；DINOv2 冻结特征度量视野不随编码器变大缩短（现象限于各向同性训练） |

**暂停时未完成：** TwoRoom L 种子 2（53.5k 步）；E24 VICReg 推广检验（[卡](experiments/E24-vicreg-generality.md)，刚启动无结果）。恢复步骤见 [日志 22:30 节](logs/2026-10-07.md)。大文件（检查点、数据）在 `/tmp/latent-wm-runs/scaling/`（fvcrc20）与 `/home/xiang/.cache/latent-wm-results/scaling/`（共享盘）。

## 入口

| 要做什么 | 去哪里 |
|---|---|
| 领域画像、谱系、角度所有权、热度数据、深读卡 | [library/themes/latent-world-models/](../../library/themes/latent-world-models/README.md) |
| 当前 idea 与实验卡 | [I16](ideas/I16-latent-bandwidth.md)、[E21](experiments/E21-scaling-planning.md)、[E22](experiments/E22-latent-bandwidth-law.md)、[E23](experiments/E23-paper-grid.md)、[E24](experiments/E24-vicreg-generality.md) |
| 资产（环境、数据、权重、venv） | [ASSETS.md](ASSETS.md)；MuJoCo 依赖隔离在 `/home/xiang/.cache/latent-wm-pydeps/`（PYTHONPATH，不改 venv） |
| 前任的研究计划、实验、主张账本（历史） | [RESEARCH_PLAN.md](RESEARCH_PLAN.md)、[experiments/](experiments/README.md)、[CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md) |

## 需要人决定的事

- 是否把本工作台的主问题正式改为 I15（规模科学 + “学习目标”），并在证据成熟后申请 ACTIVE 名额。
- Cube（3D 操作）是否作为第四个环境纳入（数据已下载解压中，接入需要约半天工程）。
