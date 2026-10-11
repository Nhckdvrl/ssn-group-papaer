# Mechanism Population Dynamics — 资产、体积与复现入口（2026-10-11）

## 仓库体积审计（清理前 Git 树的逻辑大小）

| 路径 | 文件数 | 未压缩约 MiB | 处理 |
|---|---:|---:|---|
| `results/` | 5,842 | 78.12 | 原始结果、JSON、pt、分析、部分日志：**全部保留** |
| `software-submission/` | 2,295 | 57.81 | 旧论文独立复现包：**保留自包含目录** |
| `paper-acl-v0/` / `v1/` / `v2/` / `v3/` | 138 | 5.76 | 四版 PDF、LaTeX、图表：**全部保留** |
| `scripts/` | 168 | 0.85 | 保留科研脚本，仅删 12 个 `.pyc` 与一个 NFS 临时副本 |
| `experiments/` / `logs/` | 77 / 10 | 0.39 / 0.11 | 保留所有原始实验卡、负结果及时间线 |

原来 **8,537 个文件、143.11 MiB**。本轮只删 **13 个缓存/临时文件**，并补充结项文档、版本索引；没有为了压缩体积改动实验测量。

### 为什么没有删除看上去重复的 37 MiB 数据？

通过 Git SHA 比较发现，旧 `software-submission/` 有 **1,247 个文件**与顶层 `results/` 某些文件内容完全相同，逻辑约 **37.21 MiB**。但该包 `code/common.py` 用**包内自己的** `results/`，`make_figures.py`、`make_tables.py` 也按其既定目录读取数据。删除重复文件或替成链接都会让旧提交的 standalone reproduction 变脆弱。**Git 对相同 blob SHA 早已共享存储，重复 checkout 路径不代表重复 Git 对象体积**。包因此保留。

### 历史论文版本

| 版本 | 论文标题 | 目前定位 |
|---|---|---|
| [v0](paper-acl-v0/) | *Born to Copy, Taught to Trust* | 初始叙事，已取代 |
| [v1](paper-acl-v1/) | *Which Head Takes Which Role?* | 对应早期独立软件包的题目，已取代 |
| [v2](paper-acl-v2/) | *When Do Mechanisms Correspond Across Pretraining Runs?* | 已取代 |
| [v3](paper-acl-v3/) | *Which Head Does the Work?* | 最终工作稿，已终止，不表示投稿或录用 |

## 关键实验路径

| 内容 | 实验卡 | 汇总结果 | 程序 |
|---|---|---|---|
| 初始化 × 数据 / 角色图 | [E35](experiments/E35-init-by-data-mechanism-census.md) | [e35 verified](results/e35_verified.json)、[e59](results/e59/analysis.json) | `scripts/e35_verified.py` / `e59_roles.py` |
| IOI 角色与因果承担者 | [E81](experiments/E81-carrier-inheritance.md) | [e81](results/e81/analysis.json) | `scripts/e81_carriers.py` / `e81_analyze.py` |
| 训练阶段与主力易位 | [E82](experiments/E82-when-carriers-are-fixed.md)、[E83](experiments/E83-carrier-chosen-at-emergence.md) | [e82](results/e82/analysis.json)、[e83](results/e83/analysis.json) | `scripts/e82_analyze.py` / `e83_analyze.py` |
| 原样重跑/遮蔽 | [E84](experiments/E84-relocation-vs-suppression.md)、[E85/E86](experiments/E85-candidate-gap-and-swaps.md) | [e86](results/e85/e86_analysis.json) | `scripts/e84_analyze.py` / `e86_analyze.py` |
| 审稿控制（未完成） | [E87/E88](experiments/E87-E88-review-checks.md) | 无完整结果 | `scripts/e88_review_checks.py` 不能当通过的验证 |

## v3 论文和代码

- [最新论文 PDF](paper-acl-v3/main.pdf)、[LaTeX](paper-acl-v3/main.tex)、[版本说明](paper-acl-v3/README.md)；正文引用的 `figures/`、`tables/` 继续保留。
- `scripts/figs_v3.py` 使用 `results/e35_verified.json`、`e81/e82/e83`、`e85` 等数据生成 v3 图表，部分函数还需要 `results/e81/*.npz`、`results/e83/*.npz`。**本次 HEAD 无跟踪的 NPZ**，因此仅有现存图表和 JSON 不等于 v3 全部 figures 可离线重算。不能虚构它们已备份/已复现。
- `software-submission/` 自带旧稿代码、测量和 requirements；其 README 只是那套历史包的运行说明，不是 v3 的复现指南。
- 原始完整模型权重不在 Git；外部 HF/服务器缓存未在本次审核或清理范围。

## 删除的确定无效文件

`scripts/__pycache__/`：12 个 Python 3.12 编译缓存。  
`scripts/.nfs0000000b8eff2197000319bd`：NFS 临时残留，与保留的 `scripts/gpu_scout.sh` **Git SHA 完全相同**。  
`.gitignore` 增加 `__pycache__/`、`*.pyc`、`.nfs*`，防止再次提交。

旧 `run_*.sh`、实验卡中的 RUNNING、旧论文计划均为可审计历史，**不可据此自动启动 GPU**。
