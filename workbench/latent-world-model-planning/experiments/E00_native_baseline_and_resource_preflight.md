# E00｜原生闭环与成本

- **状态：** RUNNING；TwoRoom 原生测量完成，PushT 原生批次接续。
- **对应：** 建设C00；全工作台
- **来源：** ASSETS中的LeWM-family原生入口。
- **阳性对照：** 用官方checkpoint/样例或简单可达目标检查控制接口；同seed重复应能解释差异。
- **噪声地板：** 区分加载失败、随机波动与计时warmup；不把一次episode成败当科学效应。
- **决策表（跑之前写）：** 闭环可用→供E01和方法实验复用；接口错误→修环境；成本高→改并发/缓存/任务，不宣布领域不适合。

## 问题
当前授权机器能否可靠加载、训练、规划与执行，成本是什么？

## 首轮方案（可在运行前修订）
继承已有环境/权重，选一个最成熟任务。核对checkpoint键和resolved config；跑一批数据、若干训练步和完整规划episode；记录env reset、动作范围、目标与success checker。训练和评测均明确设备，不让auto占满节点。

## 读数与资源
峰值显存、I/O等待、训练步/完整episode/planner时间、checkpoint读取；先单卡/单节点，再测试节点并发。

## 结果与修订
2026-10-02：Fast-LeWM 两任务工程运行完成；原生 TwoRoom checkpoint 加载 12.29 s，warm planner 约 1.72 s/decision，完整单 episode 成功（10 env steps）；5 warmup 后 20 训练步，batch16 compute 中位数 0.1235 s、内存 batch 准备/H2D 0.1772 s。后者不是磁盘 I/O。训练是副本上的吞吐测量，未称 baseline 复现。12 条原生 factual suffix 重放误差全部为 0、阳性控制 12/12。版本、显存、每步数据与 hash 见 [原生结果](../results/E00_E13_E16_20261002_tworoom_native.json)；单 episode 不估性能。PushT 初次工程错误与同 seed 修复均保留。

1→2→4 并发 I/O 尚未量测；完整独立训练与论文评测也未完成。

## 2026-10-02 执行批次（运行前）

- 推进 C00；用户明确授权实验与空闲 GPU，登记状态不变。
- 先盘点现有 venv / conda，缺少兼容组合才建专用 venv；模型下载到标准 HF cache。原生代码存本目录 git-ignore 的 `vendor/`。
- 首批 TwoRoom 导航 + PushT 操作，优先 Fast-LeWM 已发布 checkpoint；code commit、checkpoint revision/hash、完整 config 写入结果。
- seed=0；每任务一次加载、5 个 warmup + 20 个测量训练步、一个完整原生 goal episode。训练步只测接口/成本，不称为 reproduction 或新方法训练。
- 初始独立单卡任务，显式 CUDA device；已有占用不抢卡。节点数据优先 stage 到本地临时盘。之后以相同 batch 量测 1→2→4 并发，只有实际空卡与 I/O 允许才启动。
- 必报 checkpoint 键匹配、加载时间、训练 loss/step time、planner wall-clock、episode steps/success、峰值 VRAM、batch读取时间与缓存路径；失败原样保留。单 episode 不给性能结论或训练 seed CI。

### 下载期间的先行工程运行（scoring 前修订）

原生 TwoRoom 压缩数据约 3.43 GB、PushT 约 13.14 GB，尚未本地缓存。完整下载继续；同时可用同一发布 simulator 生成真实 50-step trajectories 接通加载、CEM、branch replay 和训练步。源标记 `simulator_generated_engineering`，action normalization 来自这些新轨迹，**不称为官方数据数值复现，也不以其闭环分数确认科学贡献**。原生数据到达后换回完整数据 statistics 和未筛选 episode anchors 重跑。

### 节点本地 I/O 并发（运行前）

TwoRoom/PushT 各测1→2→4 CPU读取worker；两轮顺序分别1/2/4与4/2/1，固定seed。每worker读8 batches×16 clips，每clip4原生frames@0/5/10/15；先4 clips warmup，同步barrier后计时，实际解压/输出bytes/checksum留存。文件均为node-local HDF5，不drop系统cache；报告warm/cache-uncontrolled条件、各worker延迟与aggregate frames/s，不能推断冷盘吞吐或4 GPU训练线性加速。GPU训练只在开始时加载本地像素，随后内存采样；I/O benchmark与这种完整训练成本分别报告。当前其他进程活动如实列为ambient负载限制。
