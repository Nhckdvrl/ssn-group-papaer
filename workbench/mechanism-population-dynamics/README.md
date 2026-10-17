# Mechanism Population Dynamics

**状态（2026-10-17 12:45）：本线已结项。** 结项判断见 [knowledge/research/CLOSEOUT_2026-10-17.md](knowledge/research/CLOSEOUT_2026-10-17.md)：可靠的经验结论保留，最有希望的统一图景（原分工是有清晰边界的吸引子）在 E119 中落空（回归随对准度线性渐变），按收尾规则停止。下面“当前主线”为结项前的记录。

## 当前主线
**问题：** 良性的继续训练为什么会撤回某些后加的修改（遗忘、损伤），而不撤回另一些？一个组件的角色由什么承载？

**目前的答案（Pythia-160M；受控损伤 + 梯度差遗忘；每项都有配对对照与事先预测）：**
- **受控损伤：**
  - 只要组件写出的内容仍被下游按原方向读取，被破坏的其余部分就会在原位长回，并且整个旧配置（搭档、替补）一起回来；
  - 写出方向被破坏（旋转、重置 OV、完整重置）就不再生（6 / 6 个头、5 个功能），功能只迁移到已经耦合的组件上，或者停在部分恢复（损失照样恢复）；
  - 联合训练中，被孤立的头变成注意力汇（冻结时不会）。
- **遗忘：** 不同参数路线的梯度差遗忘，在功能上都是改变读者头的注意力（E108）。
  - 若由读者自身的读取参数（QK）实现，被一般训练撤回 r ≈ 0.85；若由上游写出内容（OV / MLP）实现，r ≈ 0.47–0.49。与一般损失受伤、权重距离无关（E105c）。
  - 原因：读取侧修改在一般文本上的足迹宽（注意力扭曲大 11–14 倍，E111），一般梯度沿撤回方向的分量大（E110）。
  - 在事实回忆（首都）上，一般数据重学同样不对称（qk 0.77 vs ov 0.46，E109，深度匹配待复核）；**定向重学攻击能撤回所有路线**，不在主张范围内。
- **最大弱点：** 只有 160M（410M 在跑，IOI 上有反例候选）；窗口短、学习率低；遗忘方法只有梯度差；足迹机制尚无干预证据（E112 在排队）。

## 实验索引（主线）
| 卡 | 问题 | 状态 / 一句话结果 |
|---|---|---|
| [E93](experiments/E93-lesion-recovery-pilot.md) | 校准：对照不漂移、损伤可测、窗口内可见恢复 | 完成；SDPA + fp32，学习率 2e-5 |
| [E95](experiments/E95-polypythias-reset-audit.md) | PolyPythias 410M seed3 / 4 的“spike” | 完成；实为训练中途被重置回初始化（数据完整性问题） |
| [E96](experiments/E96-role-reassignment.md) | 3.2 靠什么保住 / 夺回角色（QK、OV、空缺，2×2） | 完成；保留 OV 时原头回归，有现任也夺回 |
| [E97](experiments/E97-who-takes-over.md) | 跨 5 个功能“谁接管” | 完成；登记的“第 2 名接手”不成立，接管大半是推理时自修复 |
| [E98](experiments/E98-capability-vs-loss-recovery.md) | 损失恢复而能力不恢复：慢还是卡住 | 完成；IOI 卡在 0.40，无人接替 8.9 |
| [E99](experiments/E99-where-role-memory-lives.md) | 记忆在头自身还是读者（输出旋转） | 完成；在读者；停滞与初始化尺度无关 |
| [E100](experiments/E100-de-novo-recruitment-vs-age.md) | 从头招募是否随训练阶段丧失 | 完成；不单调，取决于是否有已耦合候选（9.5） |
| [E101](experiments/E101-coupling-law-on-ioi.md) | 规律在 IOI 头 8.9 上的事先预测 | 完成；QK 回归（整个回路复原），OV / 旋转不回 |
| [E102](experiments/E102-coupling-law-across-functions.md) | 规律在另外 4 个功能上的事先预测 | 完成；旋转 4 / 4，替补被压低 4 / 4，原头达 50% 2 / 4（6 / 6 部分回归） |
| [E103](experiments/E103-regrowth-lag-coupling-gain.md) | 停滞长度是否由耦合幅度决定 | 完成；假说被否定（输出 × 2 更慢） |
| [E104](experiments/E104-coupling-law-at-410m.md) | 410M 规模复现 | 运行中；首都与预测一致，IOI 上 QK 组未回（反例候选），对照漂移 |
| [E105](experiments/E105-unlearning-bridge.md) | 真实遗忘：参数路线决定良性重学 | 完成（13 组）；qk 0.83–0.86 vs ov / mlp 0.47–0.51，与损失受伤无关 |
| [E106](experiments/E106-frozen-surgery.md) | 冻结其余部分，完整重置的头能否回来 | 完成；不能（B），但不变成注意力汇 |
| [E107](experiments/E107-dormancy-lock.md) | 休眠是否锁死（lr 5e-5） | 运行中；冻结的 3.2 开始长回 |
| [E108](experiments/E108-where-unlearning-lives.md) | 遗忘在功能上落在哪里 | 完成；都改变读者注意力，差别在实现位置 |
| [E109](experiments/E109-capital-unlearning.md) | 首都事实、定向攻击 | 运行中；一般重学不对称，定向攻击全部恢复 |
| [E110](experiments/E110-general-data-pullback.md) | 一般梯度的拉回分量 | 完成；预测重学比例（Pearson 0.94） |
| [E111](experiments/E111-footprint-breadth.md) | 修改在一般文本上的足迹 | 完成；读取侧足迹宽 11–14 倍 |
| [E112](experiments/E112-footprint-regularized-unlearning.md) | 压窄足迹能否抗良性重学（因果） | 排队中 |

## 模型、检查点与文件夹
- **基础检查点：** `~/mechpop_cache/ckpt/pythia-160m_step{8000,43000,100000}`、`pythia-410m_step100000`（HF Xet 会卡死，用 curl 下载）。
- **损伤后的权重：** `~/mechpop_cache/ckpt/e98`、`e100`、`e101`、`e102`、`e104`（只保留终点与 2500 步；400 / 1000 步与 e97 已删除——都可用 init_seed 1234 重新生成，因果图已存于 `results/`）。
- **脚本：**
  - `scripts/e93_lesion.py`：损伤 + 继续训练，可选 `--parts qk|ov|all`、`--rot_out`、`--init_scale`、`--ov_scale`、`--knockout`、`--save_at`。
  - `scripts/e89_labor.py`：每头因果图，`E89_LOCAL` 指定本地权重。
  - `scripts/e101_nameattn.py`：名字移动特征。
  - `scripts/run_e10x.sh`：卡位 worker。
- **结果：** `results/e93`–`results/e104`（JSON 轨迹与因果图 npz）。
- **知识库：** `knowledge/`（论文卡、`syntheses/`、`research/`）。
- **算力规则：** fvcrc10 / 12 / 13 / 15 / 20 / 21 的空卡；夜间 ≤ 16 张，09:00 后 ≤ 8 张。

## 核心入口

| 内容 | 文件 | 用法 |
|---|---|---|
| **研究知识库（2026-10-15新整理）** | [knowledge/](knowledge/) | 按问题组织的论文理解卡、实验全景、可信证据/撤回记录、度量审计与本地Agent指南；仅知识整理，不代表重启 |
| **结项科研判断** | [CLOSEOUT.md](CLOSEOUT.md) | 证据、反证、局限、终止理由 |
| **完整文件/复现索引** | [ASSET_INDEX.md](ASSET_INDEX.md) | 各版本、结果、程序与缺失资产 |
| **最终工作稿（v3）** | [PDF](paper-acl-v3/main.pdf) · [LaTeX](paper-acl-v3/main.tex) · [说明](paper-acl-v3/README.md) | 最新成稿，**不是投稿/录用证明** |
| 历史稿 | [v0](paper-acl-v0/) · [v1](paper-acl-v1/) · [v2](paper-acl-v2/) | 三次已被取代的论文叙事 |
| 原始科研账本 | [CLAIMS.md](CLAIMS.md) · [PAIN_LOG.md](PAIN_LOG.md) | 限定的 L1/L2 证据、撤回与审计 |
| 实验和脚本 | [experiments/](experiments/) · [results/](results/) · [scripts/](scripts/) · [logs/](logs/) | 完成/未完成按原始卡核对 |
| 早期独立复现包 | [software-submission/](software-submission/) | 对应 v1 时代同名稿，**不是 v3 包** |
| 历史研究判断 | [10/9 评议](REVIEW_2026-10-09.md) · [10/10 评议](REVIEW_2026-10-10.md) · [文献重选备忘录](LITERATURE_FIRST_RESELECTION_2026-10-10.md) | 历史文档，不代表新开题 |

## 有证据但必须限缩的认识

1. E35/E59：同初始化的不同语料模型在层内注意力角色上具有一定统计对应，而不同初始化时较弱。**这不是置换不变的科学事实**；头的编号可重排而不改变模型函数。
2. E81：同初始化、独立训练的兄弟，注意力角色图对应约 0.24–0.34，IOI 单头消融图对应约 0.02；经核实为**同一训练的后代**，主力承担者通常较稳定。统计范围只限所测模型和任务。
3. E83：在新 DataDecide 12 run 中，“任务行为一出现，最终主力承担者已经确定”的预测失败（只有 3/12 最强头保留），该发展规律已撤回。
4. E86：原样重跑已有 9/15 次发生最强 induction 头易主，随机屏蔽数据为 14/30；因此不能将单头易主直接归因于删数据。
5. E87 完整步数验证已按人指示停止、无结果；E88 部分分析代码仍有问题，不补称已完成。

项目的科学意义与新颖性受坐标对称性、强近邻结论、测量信度及因果归因限制。**人已决定结项，不因保留资源而自动重启。** 旧实验卡中的 RUNNING、PLANNED、旧计划和 `run_*.sh` 均只是历史记录。

## 清理原则

四版论文、全部科研结果、实验卡、源代码、独立历史复现包均保留。旧复现包中有 1,247 个 JSON 与主 `results/` 内容完全相同，但其脚本依赖包内目录，因此保留其独立性；Git SHA 已对相同文件对象去重。仅移除 12 个 Python 字节码缓存与一个同 `gpu_scout.sh` 完全相同的 NFS 临时残留。详见 [资产索引](ASSET_INDEX.md)。
