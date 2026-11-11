# 分工重现：分别训练的 MoE 会不会自发分出同一套专家分工

- **状态（2026-11-11 16:30，主会话；按用户指令"主线确立即暂停"）：** 候选主线 **N4 达到预登记的确立标准，提议为 ACTIVE-MAIN 交人签字（R2）**：*MoE 里先定型、并携带来源记忆的是路由器的决策函数，不是它读的几何；已发表的"路由早饱和"曲线量的是后者。* 证据三块：训练轴两条公开轨迹（E189 OLMoE-0924 5T：R 到 .5/.8 用 381B/2.33T vs H 857B/4.18T；E191 FLAME-290M 11B：到 .8 用 3.79B vs 6.39B；第一个 MoE 层两模型都反向）、复制轴（E187 Qwen3：R .53 vs .15）、功能腿（E190 三模型：打断同 id 内上下文 +1.3 nat，占全局 22–26%，前一 token 收回 59–75%）。判断与待人决定的四件事见 [`DIRECTION_2026-11-06.md`](DIRECTION_2026-11-06.md) §26；叙事见 [`MAINLINE_NARRATIVE_2026-11-11.md`](MAINLINE_NARRATIVE_2026-11-11.md)；文献归属 `library/themes/moe-routing/POSITIONING_N4_ROUTER_FIRST_2026-11-11.md`；资产清单 [`ASSETS_2026-11-11.md`](ASSETS_2026-11-11.md)。机制开放（不是门饱和）。GPU 11-11 合计约 3.3 h。
- **状态（2026-11-10 12:00，主会话）：** 11-09 起本线改在**公开 MoE 上只做推理**（自训平台冻结，DIRECTION §17）：用同一隐状态上的随机路由器族（N_A / N_B / N_C）读训练路由器。已出：E185 路由方差分解图谱（§21）、E186 七家族 + OLMoE-0924 九个 checkpoint 的同格式采集与追加（§22，1.35 + 0.76 GPU h）、E187 Qwen3-30B-A3B 复制层的路由分歧分解（§21.1）、领域地图 [`FIELD_MAP_2026-11-09.md`](../../../library/themes/moe-routing/FIELD_MAP_2026-11-09.md)。一句话：训练路由器 = 几何读出 × 词表锐化 + 给定 token 后少量局部序列信息；语言 / 文字 / 词类 / 位置都不在训练新增里；模型依赖的只有中层跨语内容；训练轴与复制层两条线索都指向"路由器权重先于几何定型、并携带来源记忆"（候选叙事 N4，未锁）。主张 C24–C27（L1）。**11-10 全部文件因 NFS 故障未提交**；原始存储 160 GB 与 OLMoE 逐 token 隐状态 13 GB 在节点 /tmp（见各卡"资产位置"）。
- **状态（2026-11-06 06:50，主会话）：** E173（配方轴三对）、E174（零假设）、E175（D1 试探）、E176（已发表读数三级重现表）均已出首批结果；判断见 [`DIRECTION_2026-11-06.md`](DIRECTION_2026-11-06.md) §9–§11——候选主线改为 R-A 方法学（扣零假设阶梯 .56 / .45 / .20；冻结路由器 T_D ≈ 0 而 CE 不变；已发表结论 9/9 或 0/9、专家级不重现），锁定条件已达成，待人确认；主张登记 CLAIMS C15–C21。
- **E172 纯 CPU 三项读数（2026-11-05 夜，Opus 会话执行，主会话核对）：** [实验卡](experiments/E172-token-class-agreement-and-standard-readouts.md)、FINDINGS §4.9——词类与词频不是一致度的对比轴（内容词 .233 / 功能词 .229；各词类初始化÷重跑都≈ .5）；Antoine 式专精度的大头是负载集中（未训练已 +26 / 训练后 +32），其词类排序换 seed 只重现 .73（重跑 .97）；语法骨架两段式出现（词类 / 形态先，依存与上下文同档，2500 万 token 时最早共享的是体裁 / 位置、随后丢弃）。
- **面谈记录与解读（2026-11-05 16:00）：** [`MEETING_2026-11-05_RECORD.md`](MEETING_2026-11-05_RECORD.md)——导师：单个一致度数字不成论文，要"こういうモデルでは低い、こういうモデルでは高い"的对比轴 / 第二尺度 / token 类别 / 语言 / 借现成分析法看其结论的跨模型一致；偏好路由分配一致与几何，不偏好消融；作业 = 查清 MoE 专家分析史（我们当场答"几乎没有"是错的，已写 [`历史综述`](../../../library/themes/moe-routing/MOE_EXPERT_ANALYSIS_HISTORY_2026-11-05.md)）。行动项 A1–A5 按成本排，模型类型对比轴（2 seed × 若干配方，每 run 约 4 GPU 小时）是导师首选。
- **方向总规划（2026-11-06 起，主会话维护）：** [`DIRECTION_2026-11-06.md`](DIRECTION_2026-11-06.md)——主线命题"分工里哪些是模型属性、哪些是训练偶然"，对手命题 H_arch / H_run / H_skeleton 与已有判决，E173 决策表，各工作流的负责会话，不做清单与加实验前自检。
- **调研 v2：相邻领域与可行空间（2026-11-05 晚）：** [`SURVEY_V2_ADJACENT_FIELDS_2026-11-05.md`](SURVEY_V2_ADJACENT_FIELDS_2026-11-05.md)——v1 的"数据/配方/初始化各占多少"被人审否决（归因分解不可识别）；新读 41 篇相邻领域（训练早期决定论、普适性/欠定、涌现模块性、专精理论、神经科学、语言发育），从已有 checkpoint 读出"分工在第 100–200 步（训练 1%）被非确定性噪声定型、此后不变，数据决定的语法骨架随后慢长"，推荐研究空间改为"分工的早期锁定"（Frankle 式分叉实验，< 20 GPU 小时）。
- **调研与方向分析（2026-11-05）：** [`SURVEY_AND_DIRECTIONS_2026-11-05.md`](SURVEY_AND_DIRECTIONS_2026-11-05.md)——52 篇文献的领域地图、顶会主张尺度、我们结果的定位、5 个可挖方向与推荐（只读不跑；逐篇笔记在 `library/themes/moe-routing/SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md`）。
**状态（2026-11-04）：** 8 个 run + 1 个完全相同配置重跑训练完并读完；总结见 **[FINDINGS_2026-11-04](FINDINGS_2026-11-04.md)**（导师的问题、相关工作、实验、结论、自评、日文版）。一句话：扣掉自然一致后，深层分工跨初始化一致 .28，而完全相同配置重跑也只有 .50——训练本身只能重现一半；重现的那部分沿词类 / 依存 / 前后词类组织，具体由哪个专家在哪些 token 上实现连重跑都不重现。GPU 已释放（只差 I4D0 在 32 亿处的 R4 损伤指纹）；未登记主张；下一步由人与导师决定。

## 问题
同架构、同数据、只换初始化训练的 MoE 语言模型，扣掉“同一个词去同一个专家”（词知识一致）和“同样的隐状态几何怎么切都相似”（几何一致）之后，专家的语言分工是否仍跨 seed 重现？上限是什么？重现的是什么语言内容？

导师的问题是起点，不是要死守的题目；推进中若出现更有意思或更重要的现象，按信息量决定是否转向。此前一个月的弯路见 [RETROSPECTIVE_2026-10-31](../moe/notes/RETROSPECTIVE_2026-10-31.md)。

## 入口
| 内容 | 位置 |
|---|---|
| **总结（唯一的汇报文档）** | [FINDINGS_2026-11-04](FINDINGS_2026-11-04.md)；总图 `results/e167/prelim_figure_v4(_ja).png`（`scripts/prelim_figure_v4.py`） |
| **公开模型零模型审计（11-09 起）** | DIRECTION §17–§22；实验卡 [E185 图谱](experiments/E185-routing-variance-atlas.md)、[E186 广度采集](experiments/E186-atlas-capture-breadth.md)、[E187 复制层](experiments/E187-copied-layer-routing-divergence.md)；结果 `results/e185/`–`results/e187/`（`tables.md` 为完整表，不写判决表）；定位 `library/themes/moe-routing/{FIELD_MAP,POSITIONING_COPIED_LAYERS,RESIDUALS_E185}_2026-11-09.md` |
| 实验卡（自训平台，已冻结） | [E167 多 seed 训练与主读数](experiments/E167-multiseed-moe-division.md)、[E168 逐 token 因果角色 / 移植](experiments/E168-matched-expert-transplant.md)、[E169 簇零假设](experiments/E169-cluster-null-for-routing-agreement.md)、[E170 语言学分解](experiments/E170-linguistic-decomposition-of-reproducible-division.md)、[E171 完全相同配置重跑](experiments/E171-exact-config-rerun.md) |
| 模型与训练 | [moe_model.py](scripts/moe_model.py)、[train_moe.py](scripts/train_moe.py)、[launch_run.sh](scripts/launch_run.sh) |
| 数据准备 | [prepare_data.py](scripts/prepare_data.py)（Dolma v1.7，约 60 亿 token，`~/mechpop_cache/e167_dolma_6b`） |
| 结果 | `results/e167/`–`results/e171/`（小文件进 git；checkpoint 与分析缓存只在本地，见下） |
| 日志 | `../logs/2026-11-01.md`、`2026-11-03.md`、`2026-11-04.md` |

## 资产位置
- 训练数据：`~/mechpop_cache/e167_dolma_6b/{train,held}`（uint16 .npy，manifest.json 含逐文件 SHA），训练前复制到各节点 NVMe。
- checkpoint：`~/mechpop_cache/e167_runs/<run>/ckpt_<tokens>.pt`（bf16，不进 git）；run：I0D0–I5D0、I0D1、I1D1、I4D0R（重跑）、I0D0R（重跑，停在 4 亿）。
- 分析缓存：`~/mechpop_cache/e167_analysis/{routing,functional,token_roles,hidden,heads_attn}/<run>__ckpt_<tokens>.npz`。
- 补齐 R4 重跑分母：有空卡时 `CUDA_VISIBLE_DEVICES=<g> E167_BATCH=16 ~/.venvs/mechpop/bin/python scripts/functional_probe.py ~/mechpop_cache/e167_analysis/functional ~/mechpop_cache/e167_runs/I4D0/ckpt_3200000000.pt`（先把同名 `.npz` 挪开），然后 `scripts/e171_compare.py` 与 `scripts/prelim_figure_v4.py`。
