# Mechanism Population Dynamics

**状态（2026-10-26）：** 人明确要求继续投入 **MoE 专家分工的跨训练可重现性**。头线已结项（10-11论文线终止；10-17修复线停止），不恢复。E130完整五初始化/17对测量形成限定C07=L2；E132/E133使用后果完成，E131共同后续继续，E134均匀分量必要性检查准备中。用户要求本轮持续执行、不退出。**先读 [HANDOFF_MOE_2026-10-25.md](HANDOFF_MOE_2026-10-25.md)，注意接手校正。**

**当前问题：** 固定输入表示、下游与语言建模目标后，独立训练是否重复形成相同的专家组织与计算职责？路由边界不同不自动等于职责不同。
- **解释校正：** 先前+.02 NLL是复现原dense的工程参考，不是开展跨训练研究的必要门槛。旧范围/数字保留；后续按共同任务和预算报告质量、功能与自身训练变化，不因未达该参考值自动延后核心测量。详见E124末尾校正。
- **核心实验E130：** [固定预算专家可重现性](experiments/E130-fixed-budget-expert-reproducibility.md)：相同512M CE协议，5个初始化（seed0复用E128），另同初始化重跑/换顺序；新增6个run在本地GPU1/3与fvcrc21四卡启动。直接测U/A作用并与末期自身变化比较，全部结果保留，不以原+.02筛seed。
- **参照数据已收齐：** seed0末期61440→62500的U/A条件对应均值.9988/.9503；初始seed0/1为.0156/.0042。均为固定探针参照，不能替代训练后跨seed比较；结果与原始数组已归档。
- **完整E130/C07：** 5个init的NLL为2.558987–2.559467；10个跨init对cal-U映射held U=.0161–.0465、A=−.0107–.0068，自身末期U≈.9988/A=.9300–.9503、重跑1；N1残差T跨init=−.0014–.0721。全部17对及原始输入/曝光经独立审计，CI为held测量误差，不把共享pair当独立seed。[全图](results/e130/figures/functional_batch.png)。
- **解释边界：** order1还改变.4041%曝光多重集合，不能称纯次序因果；两对模型KL约.017–.019、top1约94%，不称同函数。C07只陈述既定cal-U对应/指定N1读数，不意味着所有语义职责或对应不存在。
- **E131已启动：** 同父4096、完全相同的1024个minibatch只重排先后，随后共同后续至62500；两臂GPU运行正确性检查通过。它隔离纯次序的持续后果；不设性能/相关准入线。
- **当前进展：** E131撤除时U/A对应=.690/.230，19456次完全相同的共同更新后（step24576，补充诊断）为.012/.001，仍待原62500终点。E132五环使用损失均值U匹配+.011742、router+.009243、zero+.117107；E133计算输出匹配+.008227、支持加权+.011264。低指纹对应不能直接称不可重用，也不继续换权重追收益。
- **下一检验E134：** 直接移除相对逐输入专家均值的native加权偏差，保留输入相关均匀分量与原门值总量；全部5受控模型与原生OLMoE L9各自内部测预测后果。不是新共享知识概念、压缩方法或固定稀疏算力替代。
- **本次读数（E122/C06，L1）：** L9路由/输出相似偏ρ约0.46，但路由距离与held替换ΔNLL偏ρ仅0.027 [−0.036,0.087]；不能只用路由代表职责。POS正确置换复核保留组织效应：L9 δ_D=.206 [.181,.228]。
- **E122已完成：** 16层路由→替换ΔNLL偏ρ均在−.031–.027，95%词形CI均含0；[全层图](results/e122/routing_function_bridge.png)。
- **E123恢复检查未通过：** L9置零/均值损伤.182/.114；随机MoE固定32M终点NLL=2.736（dense2.494），中途最低2.624也未恢复。保留完整失败曲线，不选最佳点，未启动跨种子网格。
- **128M控制已完成：** [E125](experiments/E125-frozen-moe-data-coverage-control.md) small/cover MoE与cover dense NLL=3.265/2.574/2.591；覆盖改善−.691（95%文件CI[−.785,−.566]），仍未恢复原dense2.494。[E126](experiments/E126-equal-capacity-moe-granularity-control.md)同容量8×8192/top1为2.590，未提供恢复。当前不做跨seed自由度结论。
- **E128已完成：** 原CE512M终点NLL2.559310，距原dense+.065497（95%文件CI[.047944,.094528]），KL=.077889；5.345 GPU·时，实际窗口重复0.3013%，评估/归档与seed0末期两份功能采集均完成。[E129](experiments/E129-teacher-distribution-feasibility.md) 同128M教师目标NLL2.564、KL=.0706。核心E130的新增6run继续正常训练；不追加性能修复网格。
- **校对备注：** E121旧置换p值撤回，E122已正确重算；R4未扣词形身份；swap9/drop的1.10–1.42是KL比，不是NLL比。详见[P15/P16](PAIN_LOG.md)、[独立证据审计](knowledge/research/MOE_EVIDENCE_AUDIT_2026-10-25.md)。
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
- 覆盖池 `~/mechpop_cache/dolma_e125_512m/`（512M tokens，按`e125_prepare_data.py`重建）；E123失败终点归档`~/mechpop_cache/e123_seed0_32m/`。E128完成并归档`~/mechpop_cache/e128_seed0_512m/`，seed0功能参照在`~/mechpop_cache/e130_seed0_anchor_functions/`；E129固定终点归档`~/mechpop_cache/e129_teacher_KL_seed0_128m/`。本机NVMe原件均保留。
- E128重放时可显式传`--initial-reference results/e128/initial_reference.json`；已完成run使用的E125原完整参考仍在本机保留。E130使用提交的initial_reference.json；所有在途训练源码、输入和资产均保持。
- E128一次性后处理与seed0功能采集均complete：状态见`results/e128/finalization.json`及`results/e130/seed0_anchor_functions.json`。两张卡已释放，可用于原卡登记的初始功能参照。
- E130每run的一次性后处理已启动：训练退出后在原卡测固定终点KL及U/A（独立init另采61440自身参照），保存至`results/e130/{fidelity,functional,finalization}/`，大资产归档`~/mechpop_cache/e130_<id>_512m/`。E128旧后处理退出后，另用GPU2采seed0同协议功能；GPU被占则明确延后评分，不抢其他卡。全体尚无终点功能结论。
- 旧的独立复现包与过程文档已于 10-23 删除，可从 Git 历史恢复（见 [RESEARCH_HISTORY.md §11](RESEARCH_HISTORY.md)）。
