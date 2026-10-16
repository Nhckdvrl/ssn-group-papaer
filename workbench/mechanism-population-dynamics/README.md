# Mechanism Population Dynamics

**状态（2026-10-17 00:20）：探索中，只有一条主线。** 主线定义、领域意义、平凡与不平凡的严格自评与下一步见 [knowledge/research/MAINLINE_2026-10-17.md](knowledge/research/MAINLINE_2026-10-17.md)；证据汇总见 [knowledge/syntheses/REPAIR_FOLLOWS_COUPLING.md](knowledge/syntheses/REPAIR_FOLLOWS_COUPLING.md)。不是已录用论文。下面“核心入口”以下的内容是 2026-10-11 结项时的历史记录。

## 当前主线
**问题：** 训练好的 transformer 中一个组件被破坏后继续训练，什么决定了原来的解被恢复、被另一个组件接替，还是能力一直丢失（而损失照样恢复）？一个学到的“角色”存放在哪里？

**目前的答案（Pythia-160M，受控损伤 + 配对对照）：**
- 角色存放在下游读者对该组件输出方向的对准中。保留输出、只重置注意力，原头会回来；输出旋转后（权重“完好”）等于完整重置；只保留注意力也不够。
- 权重距离在组件层面与结局脱钩（Siddiqui 2025 的规律来自视觉整模型，不直接冲突）；与 Guo 2024“改写入端比改抽取头更难重学”同构，我们的增量是同一组件内 QK / OV / 方向的干净拆分。
- 恢复时回到整个旧配置，已在工作的替补会被挤回。
- 无接口的头不会被招募，而是被推成注意力汇。
- 没有已耦合的候选时，能力停在部分恢复（IOI 0.40），损失却照样恢复。

**最大弱点：** 窗口短、学习率低；只有 160M（410M 在跑）；人为损伤，与真实遗忘之间的桥梁还没检验。

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
| [E102](experiments/E102-coupling-law-across-functions.md) | 规律在另外 4 个功能上的事先预测 | 9 / 12 组完成；旋转 3 / 3，原头回归 1 / 2，孤立头变注意力汇 |
| [E103](experiments/E103-regrowth-lag-coupling-gain.md) | 停滞长度是否由耦合幅度决定 | 运行中；早期与预测相反 |
| [E104](experiments/E104-coupling-law-at-410m.md) | 410M 规模复现 | 运行中（预计 05:30） |

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
