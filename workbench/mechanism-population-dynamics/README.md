# Mechanism Population Dynamics

**状态（2026-10-25）：** 人明确要求继续投入 **MoE 专家分工的跨训练可重现性**。头线已结项（10-11 论文线终止；10-17 修复线停止），不恢复。当前处于探索初期，C06仅为单模型L1测量，尚无跨种子数据或主张。**先读 [HANDOFF_MOE_2026-10-25.md](HANDOFF_MOE_2026-10-25.md)，注意其中的接手校正。**

**当前问题：** 固定输入表示、下游与语言建模目标后，独立训练是否重复形成相同的专家组织与计算职责？路由边界不同不自动等于职责不同。
- **本次读数（E122/C06，L1）：** L9路由/输出相似偏ρ约0.46，但路由距离与held替换ΔNLL偏ρ仅0.027 [−0.036,0.087]；不能只用路由代表职责。POS正确置换复核保留组织效应：L9 δ_D=.206 [.181,.228]。
- **E122已完成：** 16层路由→替换ΔNLL偏ρ均在−.031–.027，95%词形CI均含0；[全层图](results/e122/routing_function_bridge.png)。
- **E123恢复检查未通过：** L9置零/均值损伤.182/.114；随机MoE固定32M终点NLL=2.736（dense2.494），中途最低2.624也未恢复。保留完整失败曲线，不选最佳点，未启动跨种子网格。
- **128M控制已完成：** [E125](experiments/E125-frozen-moe-data-coverage-control.md) small/cover MoE与cover dense NLL=3.265/2.574/2.591；覆盖改善−.691（95%文件CI[−.785,−.566]），仍未恢复原dense2.494。[E126](experiments/E126-equal-capacity-moe-granularity-control.md)同容量8×8192/top1为2.590，未提供恢复。当前不做跨seed自由度结论。
- **在推进：** [E128](experiments/E128-adequate-ce-epoch-recovery.md) 原CE目标512M无放回覆盖继续运行。[E129](experiments/E129-teacher-distribution-feasibility.md) 同128M教师分布诊断已完成：NLL2.564，距原dense+.0703（95%文件CI[.0500,.1046]），仍未恢复；KL=.0706。较同预算CE的KL改善.0191，但不替代CE主线。[E124](experiments/E124-frozen-moe-functional-reproducibility.md)工具已就绪；恢复后回核心。
- **校对备注：** E121旧置换p值撤回待重算；R4未扣词形身份；swap9/drop的1.10–1.42是KL比，不是NLL比。详见[P15/P16](PAIN_LOG.md)、[独立证据审计](knowledge/research/MOE_EVIDENCE_AUDIT_2026-10-25.md)。
- **定位：** 冻结骨干+插入MoE+多初始化已有LMC-MoE先例，增量须落在计算职责与跨训练证据。见[独立研究审计](knowledge/research/MOE_INDEPENDENT_AUDIT_2026-10-25.md)。

## 从这里读
| 想知道 | 读 |
|---|---|
| 接手当前方向：研究问题、已知事实、测量合同、下一步实验 | **[HANDOFF_MOE_2026-10-25.md](HANDOFF_MOE_2026-10-25.md)** |
| 主问题、论文贡献尚缺什么、如何避免停在代理指标/平台修补 | [PAPER_SHAPE_MOE.md](PAPER_SHAPE_MOE.md)（问题形态，未成稿） |
| 我们做过什么、发现了什么、为什么停 | [RESEARCH_HISTORY.md](RESEARCH_HISTORY.md)（历史总档） |
| MoE 方向的讨论过程（已被交接文档吸收） | [ADVISOR_2026-10-23_MOE.md](knowledge/research/ADVISOR_2026-10-23_MOE.md)、[MOE_DISCUSSION_2026-10-23.md](knowledge/research/MOE_DISCUSSION_2026-10-23.md) |
| 每条主张的证据等级与作废记录 | [CLAIMS.md](CLAIMS.md) |
| 踩过的坑（代码、统计、公开模型数据完整性） | [PAIN_LOG.md](PAIN_LOG.md)、[knowledge/heritage/FAILURE_MODES.md](knowledge/heritage/FAILURE_MODES.md) |
| 读过的论文 | [knowledge/PAPER_CATALOG.md](knowledge/PAPER_CATALOG.md) |

## 目录
- `experiments/`：实验卡 E01–E119、混杂审计 A01（原始记录，不改动）；10-23 起 MoE 方向：E120（测量工具合成验证）、E121（OLMoE 路由组织与专家差异）。
- `results/`：全部结果（大文件只在本机）。
- `scripts/`：全部代码。主要入口：
  - `e46_train.py`：受控预训练；
  - `e59_roles.py`：头角色图；
  - `e89_labor.py`：多任务因果分工；
  - `e93_lesion.py`：损伤 + 继续训练；
  - `e105_unlearn.py`：参数子集遗忘；
  - MoE 方向：`moe_measure.py`（测量工具库）、`e120_synth.py`、`e121_data.py`、`e121_olmoe.py`、`e121_analyze.py`。
- `paper-acl-v0`–`v3/`：四版论文（PDF + LaTeX），均已被取代，v3 为最后一版。
- `logs/`：每日记录。
- `knowledge/`：论文卡、方法教训、概念工具、当前分析。

## 资产提醒
- 本地缓存 `~/mechpop_cache`：头线的 Pythia 检查点与 Pile 分词数据已不存在；现有 `hf_olmoe/`（4 个 OLMoE 检查点，约 52 GB）、`e121/`（采集数组，约 21 GB）、`lingdata/`（UD EWT、SemCor）。
- E123新资产准备：`~/mechpop_cache/hf_olmo_dense/main/`；下载脚本与固定版本见 `scripts/e123_prepare_assets.py`，小型manifest在 `results/e123/`。大权重、token文件、逐样本数组不进Git。
- 覆盖池 `~/mechpop_cache/dolma_e125_512m/`（512M tokens，按`e125_prepare_data.py`重建）；E123失败终点归档`~/mechpop_cache/e123_seed0_32m/`。E128在途模型/队列在`/tmp/xiang-moe-20261025/e128_seed0`；E129固定终点归档`~/mechpop_cache/e129_teacher_KL_seed0_128m/`，SHA见`results/e129/assets.json`。
- E128重新从clone启动时可显式传`--initial-reference results/e128/initial_reference.json`；当前在途run使用E125原完整参考文件，该文件保留在本机，不能在运行中删除/替换。CE512M与KL128M均已过真实GPU梯度/冻结/输入检查。
- E128一次性后处理`e128_finalize.py`已启动：仅完整62500步/512M且训练退出后核验、评估、归档；物理GPU2忙时只归档并标记延后评估。状态写`results/e128/finalization.json`，不改训练、不自动开种子群。
- 旧的独立复现包与过程文档已于 10-23 删除，可从 Git 历史恢复（见 [RESEARCH_HISTORY.md §11](RESEARCH_HISTORY.md)）。
