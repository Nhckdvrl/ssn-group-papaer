# Latent World Model Planning｜紧凑隐空间世界模型工作台

**状态：PROPOSED（不占 ACTIVE 名额）。2026-10-07 接手后转向“规模科学”层（I15 / E21），探索中，科学主张 0。**

## 一页结论（2026-10-07 下午）

1. **原方向不值得继续。** LeWM / JEPA 隐空间规划子线 2026-09 约 30 篇/月；前任做过的角度均有同期工作。结构性复盘见 [logs/2026-10-07.md](logs/2026-10-07.md)。
2. **找到的 idea（[I16](ideas/I16-latent-bandwidth.md)，证据见 [E21](experiments/E21-scaling-planning.md)、[E22](experiments/E22-latent-bandwidth-law.md)）：越大的 latent 世界模型，latent 距离越短视。**
   - 同一配方、同一规划器：导航任务随模型变大而变差（TwoRoom offset 50：XXS 72% → M 53%；offset 75：47% → 29%，所有搜索预算一致），操作任务随规模变好（PushT offset 25：17% → 87%）。
   - 机制：失败来自 latent 几何而非预测误差（真实动力学代价同样随规模变差）；L2 度量的带宽随模型规模与训练单调缩短，与 SIGReg 优化程度强相关（Spearman 0.82 / 0.77）。新诊断量“度量视野”：完整 L2 在 TwoRoom / 迷宫约 10 步饱和，PushT 约 35 步，Reacher 约 25–35 步；短于规划视野（25 步）时 L2 规划失败。
   - 修复（不训练）：在 latent 的慢特征子空间里算代价——TwoRoom M 53%/29% → 98.5%/94%；OGBench 视觉迷宫 20% → 88.5%（offset 50）、77.5%（offset 100）。同一 latent 上的 GC-IDM 在导航上 100%，在 PushT 上随规模变好并远超 CEM。
   - 撤回 / 未成立：跨房间切分（坐标轴错）；指数 = −1/状态维数；压低 latent 维度无效；慢特征对 PushT 有害（与方块姿态不对齐）。
3. **还缺：** SIGReg 权重因果干预（在跑）；切换规则的留出验证（Reacher 已一致，Cube / 大迷宫待做）；每格 ≥3 种子；224px 锚点；形式化命题。

## 当前在跑

| 内容 | 位置 |
|---|---|
| 5 档尺寸（1.7M–285M）× PushT / TwoRoom / Reacher × 种子；latent 维度析因；数据缩放；规模 × 技巧 | fvcrc20（4×RTX PRO 6000）、fvcrc10（4×A100），`scaling/sched.py` 队列 |
| 闭环评测（n=200，offset 25/50/75，CEM 算力扫描 30×3 – 3000×30） | `scaling/eval_queue.py` |
| 候选库（模拟器真值）排序 / best-of-N / 真实动力学代价 | `scaling/bank*.py`、`scaling/oracle_bank.py` |
| 摊销策略 GC-IDM | `scaling/gcidm*.py` |

汇总：`python scaling/report.py` → `results/E21_scaling_table.json`。大文件（检查点、数据）在 `/tmp/latent-wm-runs/scaling/`（fvcrc20）与 `/home/xiang/.cache/latent-wm-results/scaling/`（共享盘）。

## 入口

| 要做什么 | 去哪里 |
|---|---|
| 领域画像、谱系、角度所有权、热度数据、深读卡 | [library/themes/latent-world-models/](../../library/themes/latent-world-models/README.md) |
| 当前 idea 与实验卡 | [I15](ideas/I15-scaling-planning.md)、[E21](experiments/E21-scaling-planning.md) |
| 资产（环境、数据、权重、venv） | [ASSETS.md](ASSETS.md)；MuJoCo 依赖隔离在 `/home/xiang/.cache/latent-wm-pydeps/`（PYTHONPATH，不改 venv） |
| 前任的研究计划、实验、主张账本（历史） | [RESEARCH_PLAN.md](RESEARCH_PLAN.md)、[experiments/](experiments/README.md)、[CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md) |

## 需要人决定的事

- 是否把本工作台的主问题正式改为 I15（规模科学 + “学习目标”），并在证据成熟后申请 ACTIVE 名额。
- Cube（3D 操作）是否作为第四个环境纳入（数据已下载解压中，接入需要约半天工程）。
