# 主题 4（副产品）：公开模型套件的数据完整性问题

在头的研究中（主题 1、2），用公开训练套件做“同初始化 / 不同初始化”比较时，陆续发现五个套件的发布检查点与标称不符。核查方法统一：按字节范围只读一两个权重张量，比较元素相关 / 余弦（几秒一个模型）。

| # | 问题 | 发现于 | 对外状态 |
|---|---|---|---|
| P09 | PolyPythias-160M 的 weight-seed 变体并没有换初始化（训练实际从标准版 step0 出发） | E44 | 已有他人报告（EleutherAI/pythia#203），未重复提交 |
| P11 | Pythia-2.8B-deduped 的终点检查点与标准版几乎是同一个模型（QKV 相关 0.993） | E58 | 已有他人报告（pythia#195、#205、#207），未重复提交 |
| P12 | DataDecide-1B 有 6 个 run 的发布 step0 不是同名 seed 的初始化（三对各共用一个） | 画图时发现，权重核实 | **已提交**（三个仓库各一帖） |
| P13 | OLMo-2-0425-1B 的 `main` 与 stage1 / stage2 检查点、Instruct 不同源（逐元素相关 ≈ 0） | E81 | **已提交**（作为证据补在已有讨论 #5 下） |
| P14 | PolyPythias-410M seed3 / seed4 在训练中途被重置回初始化，不是 loss spike | E90 / E95 | **已提交**（两个仓库各一帖） |

提交链接（2026-10-25，Hugging Face 账号 Nhckdvrl）：
- [pythia-410m-seed3 #2](https://huggingface.co/EleutherAI/pythia-410m-seed3/discussions/2) · [pythia-410m-seed4 #2](https://huggingface.co/EleutherAI/pythia-410m-seed4/discussions/2)
- [DataDecide dclm-baseline-qc-7p-fw2 #1](https://huggingface.co/allenai/DataDecide-dclm-baseline-qc-7p-fw2-1B/discussions/1) · [dolma1_7-no-math-code #1](https://huggingface.co/allenai/DataDecide-dolma1_7-no-math-code-1B/discussions/1) · [falcon-and-cc-qc-orig-10p #1](https://huggingface.co/allenai/DataDecide-falcon-and-cc-qc-orig-10p-1B/discussions/1)
- [OLMo-2-0425-1B #5（评论）](https://huggingface.co/allenai/OLMo-2-0425-1B/discussions/5)

GitHub 上未同步提交（`gh` 登录令牌失效）。

## 文件
- [reports/](reports/)：三份提交报告原文、[提交链接](reports/submitted_links.json)、DataDecide 复核数据。
- 早期核查输出留在头线结果目录 [../heads/results/](../heads/results/)（`audit_step0_1b.json`、`audit_outlier_runs.json`、`r0_hf_metadata_*.json`、`artifact_manifest_*.json`），因为头线公共代码直接读取它们。
- 核查脚本与头线共用代码，从 [历史源码入口](../heads/scripts/README.md)查询固定Git版本：`audit_polypythias_reset.py`、`audit_init_start*.py`、`audit_step0_all.py`、`audit_weight_retention.py`、`e95_reset_audit.py`、`e67_audit_sizes.py`、`r0_*.py`。
- 每个问题的发现经过与教训：[heads/PAIN_LOG.md](../heads/PAIN_LOG.md) P09–P14；E95 卡：[../heads/2-after-closure/experiments/E95-polypythias-reset-audit.md](../heads/2-after-closure/experiments/E95-polypythias-reset-audit.md)。
