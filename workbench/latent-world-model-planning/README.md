# Latent World Model Planning｜紧凑隐空间世界模型工作台

**状态：PROPOSED（不占 ACTIVE 名额）。2026-10-07 接手后转向“规模科学”层（I15 / E21），探索中，科学主张 0。**

## 一页结论（2026-10-07）

1. **原方向不值得继续。** LeWM / JEPA 隐空间规划这条子线在 arXiv 上从 2026 年初约 5 篇/月涨到 9 月约 30 篇/月；前任做过的每个角度（反事实分支、误差分解、代价函数、规划视野、反馈与测试时训练、目标策略）都有 2–5 篇同期工作。结构性复盘见 [logs/2026-10-07.md](logs/2026-10-07.md)。
2. **新的开放问题：规划能力是否随规模提升？** 120 篇后续论文几乎都固定在一个 15M 模型上，没有人系统测过模型规模 × 数据 × 测试时规划算力与规划能力的关系。[I15](ideas/I15-scaling-planning.md) / [E21](experiments/E21-scaling-planning.md)。
3. **中期读数（未完成，不升级主张）：**
   - PushT（offset 25，n=200）：XXS 18/15/17% → XS 47/52/60% → S 84%（三个/一个种子）；规模效应大、种子方差小。
   - TwoRoom：近目标饱和（约 90%）；远目标（offset 50）随规模**下降**：XXS 均值 72% → XS 66% → S 62% → S（768 维 latent）57%。
   - 机制（TwoRoom）：把预测器换成真实模拟器，latent 距离对候选的排序一样差，且大模型更差 → 问题在 latent 几何，不在预测误差。latent 距离只在真实距离约 25px 内有信息，之后饱和（距离集中），有效维度随规模与训练上升。
   - 同一 latent 上的摊销策略 GC-IDM：TwoRoom offset 25/50/75 全部 100%（XS），而 CEM 在 offset 75 只有 40%。
4. **正在形成的 idea（待证据）：** “放大模型，学习目标”——规模提升世界模型的局部保真度，但手工的 latent 距离规划目标不随规模变好、远目标甚至变差；学出来的目标 / 摊销策略能吃到规模红利。另一条并行主轴：2026 年 LeWM 后续的代表性技巧（逆动力学、时间拉直、多步预测）的增益是否小于放大一档模型（E21b）。

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
