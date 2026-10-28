# MoE asset index (E120–E142, 2026-10-26)

**当前资源约束（用户2026-10-28最新指示）：本研究总并发最多4张GPU，覆盖此前8卡授权。** E160 retry已完整结束；E162权重23文件已核验并耐久保存，当前单卡执行，完成本批后先整理再决定新增。历史费用和原实验卡当时的上限记录保留。

Read-only inventory of durable NFS assets, workspace results, and named node-local NVMe paths. Sizes come from existing manifests or `du/stat`; large files were not rehashed. No files were moved or removed.

## Storage snapshot

- Durable root: `/home/xiang/mechpop_cache` on `192.168.0.25:/data/home` (131T total / 98T used / 34T free at snapshot).
- `fvcrc20` NVMe: 894G total / 545G used / 349G free. `fvcrc21` NVMe: 894G total / 279G used / 615G free.
- The workbench `results/` directory is on `/home` NFS. NVMe paths are explicitly marked temporary and may not survive node cleanup.

## Experiment assets

| ID | Durable assets and size | NVMe-only assets | Manifest/seal and recovery entry |
|---|---|---|---|
| E120 | `results/e120` (39,983 B) | — | workspace summaries only; `scripts/e120_synth.py` |
| E121 | `/home/xiang/mechpop_cache/e121` (21,620,723,929 B); `results/e121` (10,357,855 B) | — | NFS data/results present; no archive manifest; `scripts/e121_data.py`; `scripts/e121_analyze.py`; `scripts/e121_olmoe.py`; `scripts/e121_pos_audit.py` |
| E122 | `results/e122` (3,432,350 B) | — | workspace matrices/audits present; `scripts/e122_function_bridge.py`; `scripts/e122_summarize.py`; `scripts/e122_independent_c06_audit.py` |
| E123 | `/home/xiang/mechpop_cache/e123_seed0_32m` (4,833,861,625 B); `/home/xiang/mechpop_cache/dolma_e123` (66,008,576 B); `results/e123` (3,116,560 B) | — | checkpoint and token manifest present; no archive_manifest; `scripts/e123_prepare_dolma.py`; `scripts/e123_prepare_assets.py`; `scripts/e123_frozen_moe.py` |
| E124 | `/home/xiang/mechpop_cache/e124_kmeans` (3,019,482 B); `results/e124` (361,858 B) | — | k-means/reference NPZs present; no archive_manifest; `scripts/e124_kmeans_reference.py`; `scripts/e124_make_permutation.py`; `scripts/e124_functional_capture.py`; `scripts/e124_compare.py` |
| E125 | `/home/xiang/mechpop_cache/e125_M-cover_128m` (30,161,460 B); `/home/xiang/mechpop_cache/dolma_e125_512m` (1,024,004,352 B); `/home/xiang/mechpop_cache/dolma_e123` (66,008,576 B); `results/e125` (33,745,223 B) | — | cover/small manifests and model assets present; `scripts/e125_prepare_data.py`; `scripts/e125_stage_tokens.py`; `scripts/e125_coverage_control.py`; `scripts/e125_summarize.py` |
| E126 | `results/e126` (11,901,781 B) | — | workspace results only; `scripts/e125_coverage_control.py` |
| E127 | `results/e127` (893,596 B) | — | workspace results only; `scripts/e127_predictive_fidelity.py` |
| E128 | `/home/xiang/mechpop_cache/e128_seed0_512m` (4,848,708,828 B); `results/e128` (55,307,501 B) | fvcrc20: `/tmp/xiang-moe-20261025/e128_seed0` (size not recorded) | complete; checkpoint archive manifest present; `scripts/e128_epoch_recovery.py`; `scripts/e128_finalize.py` |
| E129 | `/home/xiang/mechpop_cache/e129_teacher_KL_seed0_128m` (4,868,640,508 B); `results/e129` (11,743,049 B) | fvcrc21: `/tmp/xiang-moe-20261025/e129_teacher_KL_seed0` (size not recorded) | complete asset pointer; no standard archive manifest; `scripts/e129_teacher_distribution.py`; `scripts/e129_summarize.py` |
| E130 | `/home/xiang/mechpop_cache/e130_initial_seed0` (78,364,623 B); `/home/xiang/mechpop_cache/e130_initial_seed1` (78,364,620 B); `/home/xiang/mechpop_cache/e130_seed0_anchor_functions` (156,590,888 B); `/home/xiang/mechpop_cache/e130_seed0_order1_512m` (4,927,405,086 B); `/home/xiang/mechpop_cache/e130_seed0_repeat_512m` (4,927,401,188 B); `/home/xiang/mechpop_cache/e130_seed1_order0_512m` (5,005,696,644 B); `/home/xiang/mechpop_cache/e130_seed2_order0_512m` (5,005,696,118 B); `/home/xiang/mechpop_cache/e130_seed3_order0_512m` (5,005,696,427 B); `/home/xiang/mechpop_cache/e130_seed4_order0_512m` (5,005,696,437 B) | fvcrc20: `/tmp/xiang-moe-20261025/e130_analysis` (1,051,474,889 B); fvcrc20: `/tmp/xiang-moe-20261025/e130_analysis/Hcal.npy` (67,108,992 B) | all seven model/readout runs complete; per-run NFS manifests verified, no single consolidated archive; `scripts/e130_cross_seed.py`; `scripts/e130_finalize.py`; `scripts/e130_predictor_compare.py`; `scripts/e130_capture_anchor.py`; `scripts/e130_routing_batch.py` |
| E131 | `/home/xiang/mechpop_cache/e131_ordered_512m` (9,955,138,341 B); `/home/xiang/mechpop_cache/e131_permuted_512m` (9,955,138,470 B); `/home/xiang/mechpop_cache/e131_parent_and_plan` (4,967,720,204 B); `/home/xiang/mechpop_cache/e131_common24576_functions` (313,191,627 B); `/home/xiang/mechpop_cache/e131_predictor_comparison` (427,559,386 B); `/home/xiang/mechpop_cache/e131_analysis_complete` (215,253,871 B) | fvcrc20: `/tmp/xiang-moe-20261025/e131_ordered and e131_permuted` (size not recorded); fvcrc20: `/tmp/xiang-moe-20261025/e131_predictor_compare` (size not recorded) | complete; branch/readout/analysis manifests verified; `scripts/e131_order_history.py`; `scripts/e131_finalize.py`; `scripts/e131_predictor_compare.py`; `scripts/e131_plot_trajectory.py` |
| E132 | `results/e132` (3,406,909 B); `/home/xiang/mechpop_cache/e132_bank_graft_assets` (8,057,766,504 B) | fvcrc20: `/tmp/xiang-moe-20261025/e132_banks` (8,056,033,472 B; source retained) | five bank SHA values verified against staging metadata; sealed by `results/e132/asset_archive_manifest.json`; `scripts/e132_bank_grafting.py` |
| E133 | `results/e133/output_alignment.json` (3,030,865 B); `/home/xiang/mechpop_cache/e133_output_alignment_assets` (1,358,451,717 B) | fvcrc20: `/tmp/xiang-moe-20261025/e133_output_alignment` (1,353,278,770 B; source retained) | five cal-cache arrays, metadata and sequence/calibration SHA verified; sealed by `results/e133/asset_archive_manifest.json`; `scripts/e133_output_alignment.py` |
| E134 | `/home/xiang/mechpop_cache/e134_necessity` (1,553,603,695 B); `/home/xiang/mechpop_cache/hf_olmoe/main` (13,841,130,907 B) | fvcrc21: `/tmp/xiang-moe-20261025/olmoe` (13,841,130,907 B); fvcrc21: `/tmp/xiang-moe-20261025/e134_necessity` (size not recorded) | complete; raw/calibration/source-proof archive sealed; `scripts/e134_uniform_necessity.py`; `scripts/e134_component_variation.py` |
| E135 | `/home/xiang/mechpop_cache/e135_student_33554432` (6,452,038,109 B); `/home/xiang/mechpop_cache/e135_cache_recipe` (840,239,327 B); `/home/xiang/mechpop_cache/e135_readouts` (727,867,212 B); `/home/xiang/mechpop_cache/dolma_e125_512m` (1,024,004,352 B) | fvcrc21: `/tmp/xiang-moe-20261025/e135_cache` (71,707,179,838 B); fvcrc21: `/tmp/xiang-moe-20261025/olmoe` (13,841,130,907 B) | complete; student/readout/recipe archives sealed; H/Y cache is NVMe-only; `scripts/e135_prepare_cache.py`; `scripts/e135_train.py`; `scripts/e135_capture.py`; `scripts/e135_readout.py` |
| E136 | `/home/xiang/mechpop_cache/e136_assignment_oracle` (6,914,295,779 B) | fvcrc21: `/tmp/xiang-moe-20261025/e136_oracle and e136_readout` (size not recorded) | complete; assignment-oracle archive sealed; `scripts/e136_train.py`; `scripts/e136_readout.py`; `scripts/e136_capture.py` |
| E137 | `/home/xiang/mechpop_cache/e137_support_components` (21,122,182 B) | fvcrc21: `/tmp/xiang-moe-20261025/e137_components` (size not recorded) | complete; sufficient-statistics archive sealed; `scripts/e137_components.py`; `scripts/e137_plot_components.py` |
| E138 | `/home/xiang/mechpop_cache/e138_fixed_cohort` (13,372,413,430 B) | fvcrc21: `/tmp/xiang-moe-20261025/e138_seed0/2 and e138_readout` (size not recorded) | complete; fixed-cohort archive sealed; `scripts/e138_train.py`; `scripts/e138_components.py`; `scripts/e138_readout.py`; `scripts/e138_plot_cohort.py` |
| E139 | `/home/xiang/mechpop_cache/e139_matched_free_cohort` (13,401,084,624 B) | fvcrc21: `/tmp/xiang-moe-20261025/e139_seed0/2 and e139_readout` (size not recorded) | complete; matched free/fixed archive sealed; `scripts/e139_train.py`; `scripts/e139_components.py`; `scripts/e139_readout.py`; `scripts/e139_plot_cohort.py` |
| E140 | `/home/xiang/mechpop_cache/e140_native_router_warmstart` (19,824,000,238 B) | fvcrc21: `/tmp/xiang-moe-20261025/e140_seed0/1/2 and e140_readout` (size not recorded) | complete; warmstart archive sealed; `scripts/e140_train.py`; `scripts/e140_components.py`; `scripts/e140_readout.py`; `scripts/e140_plot_warmstart.py` |
| E141 | `/home/xiang/mechpop_cache/e141_support_partition` (71,765,029 B) | fvcrc21: `/tmp/xiang-moe-20261025/e141_support_partition` (size not recorded) | complete; support-partition sufficient-statistics archive sealed; `scripts/e141_support_partition.py`; `scripts/e141_independent_audit.py`; `scripts/e141_plot_support_partition.py` |
| E142 | `/home/xiang/mechpop_cache/e142_shared_random_router` (12,954,858,397 B; manifest SHA fc070c957126d49e765e1265085c9ac935f1856030768c8689869a8e11b24d2d) | fvcrc21: `/tmp/xiang-moe-20261025/e142_seed0/2 and e142_readout` (size not recorded) | complete; shared-random-router archive sealed; `scripts/e142_train.py`; `scripts/e142_components.py`; `scripts/e142_readout.py`; `scripts/e142_plot_warmstart_compare.py` |

## Shared large inputs

- **Public OLMoE-1B-7B-0924 model**: `/home/xiang/mechpop_cache/hf_olmoe/main` (13,841,130,907 B); checksum/recovery proof: `E122 provenance; E134/E135 preflight verified existing shard/config pins`.
- **E123 token source pool**: `/home/xiang/mechpop_cache/dolma_e123` (66,008,576 B); checksum/recovery proof: `results/e123/manifest.json`.
- **E125 cover token pool**: `/home/xiang/mechpop_cache/dolma_e125_512m` (1,024,004,352 B); checksum/recovery proof: `results/e125/cover_manifest.json`.
- **E135 H/Y training cache**: 71,707,179,838 B at `fvcrc21:/tmp/xiang-moe-20261025/e135_cache`; not copied into durable archives. Rebuild entry: `scripts/e135_prepare_cache.py` using durable E135 recipe and E123/E125 token sources.
- **E130 dense base model cache**: E130 preflight recorded local copies on both nodes; no canonical durable NFS path/checksum pin found in this asset inventory. Paths: fvcrc20 `/tmp/xiang-moe-20261025/olmo_dense`, fvcrc21 `/tmp/xiang-moe-20261025/olmo_dense`; shard byte sizes `[4707070632, 412090496]`. No canonical NFS archive is recorded.

## Recoverability and manifest notes

- E120–E127 are represented primarily by workspace results and durable E121/E123/E124/E125 source assets; several older results have no centralized archive manifest.
- E130 has seven complete run-level NFS assets with per-run archive manifests, plus initial captures and anchor functions. There is no single consolidated E130 archive; `/tmp/xiang-moe-20261025/e130_analysis` and derived Hcal are staging only.
- E131 final ordered/permuted branches, parent/plan, diagnostic functions, predictor comparison and analysis are durably manifested. The N1 Hcal is referenced by path/SHA and can be recovered from the archived anchor functional capture.
- Correction from the recorded 2026-10-26 archival action: E132's five banks and E133's output-alignment assets were copied to the durable roots listed above and checked against the existing SHA values; original NVMe sources were retained. See [E132 manifest](results/e132/asset_archive_manifest.json), [E133 manifest](results/e133/asset_archive_manifest.json), and [the dated log](../logs/2026-10-26.md). The earlier “NVMe only” statement was superseded; this document edit is not a new filesystem availability check.
- E135’s ~71.7GB H/Y cache is fvcrc21 NVMe only. Its durable cache recipe and E123/E125 token pools are the rebuild path. E134–E142 experiment archives are sealed; old pilot/cohort weights are references, not duplicated assets.
- Per-run E130 finalization pointers and manifest SHA values are in `results/e130/finalization/`; the machine-readable run list is in `results/asset_inventory_2026-10-26.json`.

Machine-readable companion: `results/asset_inventory_2026-10-26.json`.

## 2026-10-26：首轮设计的实际依赖

- [E144](experiments/E144-fixed-gate-recombination.md) 与条件后续 [E146](experiments/E146-grouped-recombination.md)：E138 seed0/2 与 E136 seed1 的 step4096 专家、共同 teacher gate、公共模型、旧 held token/元数据；分组另需 training Hcal8192。
- [E145](experiments/E145-history-gate-bank-cross.md)：E135 seed1 共同接收者、E139 seed0/2、E142 seed0/2，以及既有 final Hcal→seed1 对应。R/S 共享的 seed1 只是一份模型，不能按两份独立模型计算资产或重复数。
- 原训练归档包含 initial 与最终 checkpoint；九次 evaluation 是标量日志，不是九份中间参数快照。首轮只读推理不依赖整份约 71.7GB 训练 H/Y cache；缺少派生 H 时可由固定 prefix 重放有来源与哈希的 token。
- 本轮只核对仓库清单与脚本，未访问计算节点验证资产可读性。新 driver、E144 selected/source maps、E145 交叉配置、E146 分组及新结果尚不存在；不能把设计文档当执行完成证明。执行端按 manifest 核验来源，再登记自己的实际资源和恢复动作。

## E144–E147：本轮实际核验与新读数（2026-10-26）

- **实际访问，不是旧清单推断：** fvcrc20核验了8份唯一step4096终点的文件/tensor/gate SHA、原cache identity；F0/F1/F2与A/R0/R2/S0/S2的耐久来源仍为上表E135/E136/E138/E139/E142。公共OLMoE分片/config/tokenizer逐文件SHA复核，冻结prefix/teacher加载前后检查通过。机器可读证明见`results/e144/asset_preflight.json`。
- **临时只读权重提取：** fvcrc20 `/tmp/xiang-moe-20261026/e144145/sources/{F0,F1,F2,A,R0,R2,S0,S2}.pt`，共约12.9GB，保留原FP32学生参数。可以从原耐久checkpoint重新提取；不依赖这份NVMe作为唯一备份。
- **环境：** `~/.venvs/mechpop/bin/python`，torch2.8.0+cu128、transformers4.57.6；未新建环境或下载模型。CUDA visibility必须在库导入前设置，driver同时核对物理UUID。

| 新实验 | 耐久raw（均已实际生成） | 追溯入口 |
|---|---|---|
| E144 | `~/mechpop_cache/e144_prediction_recombination/batch00–03.npz` | `results/e144/manifest.json`：24来源+3学生+μ/teacher/zero的逐token读数、层风险与C/V |
| E145 | `~/mechpop_cache/e145_history_cross/batch00–03.npz` | `results/e145/manifest.json`：14变体、双向KL、四格/共同gate/支持外调用 |
| E146 | `~/mechpop_cache/e146_grouped_recombination/` | `results/e146/manifest.json`：4×12组装，`cal_gamma.npy`/`held_gamma.npy`完整64×64矩阵；定组轨迹在Git摘要 |
| E147 | `~/mechpop_cache/e147_gate_group_control/` | `results/e147/manifest.json`：gate-only的12组装和`training_gate_affinity.npy`；强对照原始来源保留 |

以上NFS路径可在授权SSH节点直接读取；需取回时使用如`scp -r fvcrc20:/home/xiang/mechpop_cache/e147_gate_group_control <本地目录>`。逐文件SHA及全批次封存见`results/execution_2026-10-26_artifacts.json`。四项raw和全部source proof足以重算统计；大数组不入Git。Git包含源码、冻结输入/来源/组、结果摘要与PNG/PDF。

本轮只重放既有token/prefix与所需MoE块，未重建约71.7GB训练H/Y cache，未训练新模型。E144/E145预算包含两轮预检，首次CUDA物理卡放置问题及旧对照在`results/e145/device_visibility_audit.json`中保留；新held在修复后完成，无丢弃条件。

## 睡前约束后的成熟资产核查（E148运行期间）

| 资产 | 实际核查 / 阅读范围 | 可回答的层次与限制 |
|---|---|---|
| OLMoE 0924四个checkpoint | 目录/配置存在；step5000分片、config、tokenizer逐字节核验，E148 parent已实际运行；其他原路径见上表 | 公开真实训练谱系；同父继续学习干预。纵向checkpoint不是独立seed，也不把20B时刻当未分工初始化 |
| 缓存Qwen3-30B-A3B | snapshot `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`；16个分片实际共61066575648B。config：48层、128专家、top8、dim2048、expert768、norm_topk_prob=True；未运行新模型推理 | 缓存README明确Pretraining & Post-training、base_model为Qwen3-30B-A3B-Base；不能作为同目标/同配方独立seed。成熟异构原生模型可提供边界验证；本轮尚未声称评测接口已通过 |
| [Equifinality](https://arxiv.org/html/2604.14419) | 只重核§3.7资产发布说明，仍写code/checkpoints待发表后释放；没有确认可下载权重 | 不把论文里有多seed图表等同已有可复用成熟checkpoint；也不由未找到判定领域不可行 |
| [Data Scarcity](https://arxiv.org/html/2609.11917v2) | 已有阅读之外，本轮检索全文code/checkpoint/release入口，未确认本工作可直接下载的seed权重 | 作者训练过多个seed不等于资产已可获取；现阶段不将其当现成cohort，不触发自训补齐 |
| [Three Phases公开仓库](https://github.com/Cmouzouni/three-phases-moe) | 通过GitHub工具读README与results列表，发布内容为代码及聚合JSON，使用原始OLMoE/OpenMoE公开checkpoint | 可核对纵向组织先验与复用统计定义，不是独立seed套件；cached aggregate不是per-token原始capture或新模型权重 |

模型资产不足时优先重述为可由成熟模型识别的问题，保留需要独立初始化总体的未决问题；不通过小模型低成熟度训练或输入bootstrap伪造跨seed证据。E148后先看其实际识别结果，再选少量能区分竞争解释的成熟资产干预，避免为了保持GPU繁忙自动排新训练。

## E148/E149实际完成与耐久资产（2026-10-27）

- E148原生来源：`/home/xiang/mechpop_cache/hf_olmoe/step5000-tokens20B`，已逐文件SHA验证；源码、软件和tokenizer同一性锁定在`results/e148/plan.json`、`model_assets.json`，不是原始optimizer续接。
- **完整耐久位置：** `/home/xiang/mechpop_cache/e148_native_order_forks`，72个文件、237,114,164,566 B，包含唯一parent32、A/B/A-repeat完整FP32 pulse160/final672（含optimizer、全部buffer、RNG）、thin288/608、所有预测/路由、更新链与4个移植raw。每个文件在复制时对源/目的SHA核验；`results/e148/archive.json`及耐久`archive_manifest.json`给路径、size、SHA、验证时间。临时源仍保留，没有删除恢复所需内容。
- **恢复入口：** 在目标节点建立`/tmp/xiang-moe-20261026/e148`，将上述耐久目录内容`rsync -a`到其中，再将公开`step5000-tokens20B/`内容复制到其`model/`。固定源码/HF4.57.6/torch2.8.0+cu128后，`e148_readout.py analyze`可CPU复算，`e148_analyze_gpu.py --physical-gpu N`是同公式GPU适配；原实验预算账本已结清，复算须单独计资源，不悄悄覆盖原账本。
- E149无新训练，直接使用E148终点；raw `/home/xiang/mechpop_cache/e149_native_source_cube/cube_metrics.npz`，5,114,827 B，SHA `fbd55f0641c20a6044a7f0fe5fecc4f142f9428e39d6d553ef9c109ffd28ecac`。`results/e149/manifest.json`绑定源码、源checkpoint和输入；`e149_source_cube.py analyze --physical-gpu 0`仅CPU重算。
- 同研究者从raw独立实现点值/角点/交互代数一致性检查：`scripts/e148149_verify_results.py`，结果`results/e148149_raw_verification.json`；不冒称独立L3校对。
- [E148/E149封存](results/e148149_artifact_seal.json)绑定源码提交`2f492784`、完整耐久manifest、全部结果proof与实际资源。耐久`run_metadata_2f492784.tar.gz`（903,189 B）是该精确提交的源码/小型结果包，可配合独立大资产恢复；不是新增模型或科学重复。

## E150公开成熟分叉：最初核查与后续完成记录

- [作者发布清单](https://github.com/allenai/EMO#midtraining-ablation-models)与两训练脚本共同指向成熟1T parent `step238419`，之后标准/文档pool协议各退火50B；声明谱系、尚未取得的原始起点/batch/optimizer证据分开记录。HF commit/file metadata已实际读取，见`results/mature_assets_2026-10-27/emo_repo_pins.json`。
- 标准终点`allenai/StdMoE_1b14b_1T` pin `b82073bb43aaaddc0f71d5ce139ad291a3948b32`；协议终点`allenai/StdMoE_1b14b_1T_EmoAnnealed` pin `d18c640b39e67f89669f38c5db8b5ed22a6927ca`。两份FP32权重各54,275,336,216 B，总新增下载108.55GB，写NFS HF缓存`/home/xiang/mechpop_cache/hf_emo_mature`，不在NVMe重复存两份。
- 两份小型code/config/tokenizer已下载且与公开Git blob/LFS核验，native代码只差额外assert/logging类型保护；源码不能标为逐字节相同。实际配置128总expert/top8含末槽1共享，**127选7+1**；共享softmax单槽权重1，路由部分对127独立softmax。四因素操作必须沿真实接口，不复用OLMoE64选8的假设。
- 原生custom code针对HF4.57.1；当前4.57.6的CPU tiny两层16格全部参数来源/native角/只读检查已通过，无新环境安装。64旧语言窗口decode后新tokenizer重编为30,994个真实target（uint32，非uint16），input CI仍20文件簇、探索性；不跨tokenizer比较绝对NLL。新GPU预检/科学读数尚未运行。
- **实际校准更新：** A全部11分片完整LFS SHA已验证，13.5686B参数原生FP32/BF16单卡cal通过，峰值54.822GB，重复/全mask差0、keys严格匹配；用时.18982 GPU·时。`results/e150/preflight.json`当前仅source0、明确partial，B和主held未运行；校准logits/日志耐久位于`~/mechpop_cache/e150_native_protocol_cube/`。冻结核心9cd5ba33；normalizer只读observer另存源SHA，不改前向。

### E150完整完成后的耐久资产

两终点全部44个权重/小型文件已核验，FP32权重实际合计108,550,672,432 B；`results/e150/asset_manifest.json`为complete，不再依赖上面的阶段partial说明。两source cal均通过，全部48主条件已完成；新代码未训练参数。

| 大资产 | 位置 / size | 证据 |
|---|---|---|
| 模型A/B原始权重、代码、tokenizer | `~/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T{,_EmoAnnealed}/snapshots/<各pin>/` | `asset_manifest.json`逐文件公开Git/LFS及实际SHA；无需复制另一份权重 |
| E150主矩阵 | `~/mechpop_cache/e150_native_protocol_cube/cube_metrics.npz`，23,911,964 B | SHA `83577a3343aa7366216029ab0b4a02a75f513d39e18c6a66d0b8b0e0cb3f1d83` |
| normalizer侧记录 | 同目录`normalizer_observations.npz`，229,605 B | SHA `12f1209ef42c8647ccd3584bc0388ba1d360d95b528d6d0e8cc9e8ce7f8413a7` |
| 新token输入/文本/cal位模式 | 同目录`plan.npz`、`text_windows.jsonl`、`cal_source_0/1.npz` | `results/e150/plan.json`、`preflight.json`全部实际path/SHA；30,994 full及22,866 suffix targets/格 |

恢复统计：`~/.venvs/mechpop/bin/python moe/scripts/e150_analyze.py`，再`e150_verify_results.py`与`e150_plot.py`。重新跑模型另计资源，先恢复上述固定pins/source/input与既有环境；流程是`e150_execute.py evaluate --physical-gpu N`，不是漏掉normalizer observer的裸driver。源代码9cd5ba33、完整统计27050fad及之后封存摘要中的确切SHA是追溯入口。

[E150封存](results/e150/artifact_seal.json)：精确结果提交870f88cf的`run_metadata_870f88cf.tar.gz`已存同一耐久raw目录，761,274 B；6个科学raw/input/cal文件共88,515,567 B逐项重核SHA，公开108.55GB模型权重只引用原完整核验的HF缓存，避免重复复制。封存与后续E151新结果分开，不回写旧raw。

E151已完整完成，仍复用同两native权重/输入：`~/mechpop_cache/e151_native_selectivity_necessity/metrics.npz` 4,270,219 B，SHA `8c02187d75488219f82c20023382a0134495479f4586115a564a0602c6fb9ee7`；`random_masks.npz`的3份固定mask由`results/e151/plan.json`锁定，非训练seed。12条件全部保留，native逐token NLL与E150一致、源参数/buffer只读，CPU点复核误差0。实际.330641878 GPU·时、单卡81.857GB，无新训练或新模型下载。

E151复算：`~/.venvs/mechpop/bin/python moe/scripts/e151_native.py analyze --physical-gpu 0`，再`e151_verify_results.py`与`e151_plot.py`。原模型重新执行须另计资源；所有phase budget已结清，不能把已有raw恢复算成新实验或独立复现。

E152全部22条件完成，仍复用同两权重、输入和旧5套mask。耐久`~/mechpop_cache/e152_native_normalizer_counterfactual/{metrics,masks}.npz`共8,367,550 B；raw 8,272,343 B，SHA `75e4315b05a867d45d298c9c835a6b2aa7cbca4432249b8e766e6685fcf41b8b`。`.486391099 GPU·时`单卡81.857GB，零训练；`e152_normalizer.py analyze --physical-gpu 0`、`e152_verify_results.py`与`e152_plot.py`只从raw复算。所有pool逐token NLL重现E150/E151，不能计新模型重复。

[E152封存](results/e152/artifact_seal.json)绑定精确结果提交`b9d1a4f6`，源driver `0f77a1b3`、原生核心`9cd5ba33`；耐久`run_metadata_b9d1a4f6.tar.gz` 40,446,111 B含该提交workbench源码/小型结果/历史资产指针，不含大权重。raw与mask、主要proof的size/SHA均重核；E153新任务数据/读数另行管理，不覆盖E152。

[E151封存](results/e151/artifact_seal.json)绑定精确结果提交`e12e82e4`；耐久`run_metadata_e12e82e4.tar.gz` 593,915 B，两份raw/mask共4,327,515 B逐项SHA复核。其原生source与E150逐token NLL完全相同，作为新干预而非新模型重复；源码/数据/结果层次在封存中分开。

## E153/E154完成资产（2026-10-27）

- E153固定任务raw/题目/文本/cal控制/mask共463,517 B，耐久目录`~/mechpop_cache/e153_mmlu_source_transfer/`；scores 42,960 B，SHA `a63ec36d13625c9980cf62f269c774939036dde024cf80679d7acaaa05539ec7`。源码f98566c2、精确结果提交c16fc09f，`run_metadata_c16fc09f.tar.gz` 40,627,106 B；[封存](results/e153/artifact_seal.json)给全部SHA/路径。统计复算`e153_run.py analyze --physical-gpu 1`，再`e153_source_effects.py`、`e153_verify_results.py`与`e153_plot.py`。实际1.092476982 GPU·时，单卡81.857893GB。
- 成熟父P `allenai/StdMoE_1b14b_1T_Preanneal` pin `d2a4949c9d4ad6cf47fbac131f7e020077332b21`，公开FP32权重54,275,336,216 B已取回原NFS HF缓存一份、11分片及小型文件逐项公开Git/LFS SHA核验；`results/e154/asset_manifest.json`。三个成熟模型权重总计162,826,008,648 B，无新训练。12个张量近邻仅为资产检查，不替代原始训练状态链。
- E154新raw `~/mechpop_cache/e154_native_parent_boundary/metrics.npz` 3,315,828 B，SHA `f36eb7b39c7932336aadba97ee2a3e020b91c6fc7e3250c4c88096385bbe54f5`；同目录保留`inherited_masks.npz`、`cal_native_bf16.npz`。9条件全部完成，原生代码bea72824；`e154_analyze.py analyze`、`e154_verify_results.py`、`e154_plot.py`从raw复算。实际.329929935 GPU·时、54.821924GB峰值；A/B只继承旧raw，不算重复实验。
- 四篇完整一手PDF/文本/阅读记录在`~/mechpop_cache/moe_primary_reading_20261027/`，EMO25页、MirrorMoE20页、Training-Free Halving9页、OptEP23页；仅small manifest/论文卡/比较入Git，全文PDF留缓存。

E155已完整完成：`~/mechpop_cache/e155_native_task_branch_necessity/scores_{P,A,B}.npz`分别15,965/15,929/15,803 B，SHA/原生fingerprint在`results/e155/manifest_{P,A,B}.json`。统计`e155_native.py analyze --physical-gpu 0`，再`e155_verify_results.py`、`e155_plot.py`；独立Terra报告与POST-HOC common-success分开存档。实际1.343426979 GPU·时，每卡54.685606GB峰值，预算均complete。

[E154封存](results/e154/artifact_seal.json)绑定70b2ec6f源码/结果包，`run_metadata_70b2ec6f.tar.gz` 40,813,419 B，raw/mask/cal共36,227,755 B，SHA逐项复核。E156重用同三公开模型，CPU先BF16后同卡驻留，真实匹配所有native权重/buffer/输出身份才进入新条件。

**2026-10-27资源复核（非新实验）：** 限定常规HF与`hf_olmoe`两缓存根，OLMoE 0924 base main/20B/419B/2516B均有完整3分片，未找到Instruct权重；64选8、无shared、`norm_topk_prob=false`。公开卡声明base→SFT→DPO谱系不等于已核验训练字节链，plain/chat评测格式也需区分。[只读核查](results/mature_olmoe_asset_check_2026-10-27.json)供未来有实质科学动机时复用，本轮没有另开模型实验。

E156评测期间，全文缓存增至9篇193页，新增Sparsity Moves Computation v2、Beyond Routing v1、Basic-Refinement官方ACL版；PDF/文本仍在`~/mechpop_cache/moe_primary_reading_20261027/`，版本/SHA/阅读覆盖见[统一manifest](notes/PRIMARY_READING_2026-10-27.json)，小型论文卡和接口核对进Git，无作者模型运行。

E156全部22条件已完成，`~/mechpop_cache/e156_common_parent_cross/scores.npz` 101,431 B，SHA `17febe351a8f8e4136b4e79ed75fd88792281970c45f2b4ac9a7eceb697f67b6`；同目录`native_references.npz`、`receiver_task_masks.npz`由plan/selectors锁定。源码8ec5add4，所有三模型canonical BF16参数/buffer/cal及128题native候选LL精确一致、只读hash通过。复算`e156_analyze.py analyze`、`e156_transfer_contrasts.py`、`e156_plot.py`；独立审计`results/e156_independent_audit/audit.py --raw <scores路径> --summary moe/results/e156/summary.json`。实际2.255563879 GPU·时、单卡81.837203GB，预算complete、GPU释放，无新训练/模型下载。

[E156封存](results/e156/artifact_seal.json)绑定结果提交`0aa2a561`；耐久`run_metadata_0aa2a561.tar.gz` 41,935,765 B，三个raw/reference/mask文件共141,847 B。13个Git数值源码逐一匹配冻结提交`8ec5add4`和运行manifest，11个HF源码/config/tokenizer另按固定snapshot核SHA，不复制162.8GB权重。

E157完成：`~/mechpop_cache/e157_task_subbank_reintegration/scores.npz` 58,379 B，SHA `ab4543351a4beb85c4e5d543f75f3e124782b9972c972e028d75c200b902449e`。source `ef3e70ec`、12新full/3native重放、30结构控制及参数buffer只读通过；`e157_analyze.py analyze`、`e157_plot.py`复算，POST-HOC direct shared差另由`e157_shared_effects.py`生成。实际2.056491230 GPU·时、单卡81.836793GB；受限值只继承E156 on-domain，不算新测量，off-domain受限未取得。

[E157封存](results/e157/artifact_seal.json)：结果提交d8af3818精确包42,531,015 B，15个Git数值源匹配冻结ef3e70ec及运行manifest，11个外部HF代码/config/tokenizer逐SHA匹配；大权重不复制。

E158的v2/v3工程预检已封存：`~/mechpop_cache/e158_factual_role_interchange/{baseline,component_cache}.npz`及`full_forward/{baseline,component_cache}.npz`保留实际原生读数/uint16承载BF16分量。v2缓存数值失败，v3全前缀数值通过但原单层网格超时估计，不含内容干预；费用6532.765952秒永久记入累计4h。v4源码1cdcb1a8的完整路径测量复用v3缓存，原始目录`.../whole_path/`，已完成；manifest/完整职责结果见下方完成条目。

E159源码050fd41f在GPU1运行，`~/mechpop_cache/e159_unchanged_function_partner_role/references.npz`仅含已封存E155/E156参考；四未知零化端点的新scores尚未完成。`results/e159/known_{border,lm_border}_posthoc.json`是旧端点组合，零新增前向；两个独立校对和已查看的`figures/e159_known_context`随Git追溯。新端点完成后再封存，不把运行中预算当完整结果。

E159新端点已完成：`~/mechpop_cache/e159_unchanged_function_partner_role/scores.npz` 76,551 B，SHA `7c76a0702acbbc9018295c5c993db1f4b98fbbbab7a1961c38ee71ab988a9a76`。source050fd41f，512未知条件题读数+512 P重放、36额外来源控制；其余完整格继承E156。`e159_analyze.py --analyze`、独立audit.py `--output <report> --compare-summary <summary>`、`e159_plot.py`从raw复算。实际1.365762829 GPU·时，单卡81.835589GB，已exit0/budget complete；事前/事后source hash均通过。完整封存包在结果提交后补入。

E158 v4完整路径已完成：`~/mechpop_cache/e158_factual_role_interchange/whole_path/scores.npz` 379,526 B，SHA `317dd4d6a64d3f145838cdf933c840c603362ad9ab437b1f49b08215da2c4234`；source1cdcb1a8。`e158_whole_analyze.py --analyze`、`e158_whole_independent_audit/audit.py --audit --output <report> --summary <summary>`、`e158_whole_plot.py`复算；关键内容图为content_control。新attention位缓存native_attention.npz连旧R/S缓存、输入、失败预检由plan绑定。v4 1.454306872 GPU·时，连两次失败3.268964081 GPU·时；独立26357元素误差0，过程exit0/budget complete，旧单层矩阵没有科学结果。

**后续复用的临时NVMe（2026-10-28）：** fvcrc20 `/tmp/xiang-moe-20261028/mature_emo_pab/{P,A,B}/`，66文件162,856,907,242 B，逐文件源流SHA与本地独立重读SHA一致；本地复制耗时4771.658秒、0 GPU，原NFS/HF资产保留。详细清单 `~/mechpop_cache/emo_local_staging_20261028.json` SHA2092d5f6a0b2d2d7b5233280db6a936fdaecca4125815bba6764b1f198c42a06；repo简报native_local_staging_2026-10-28。此目录可被节点清理，恢复运行stage_mature_local.py；不把它当唯一耐久权重。新loader还须核所有实际参数/buffer和旧cal，避免将文件复制等同原生身份。

E158结果提交37b68280的精确NFS包 `whole_path/run_metadata_37b68280.tar.gz` 44,778,149 B；23 Git数值源/11外部小文件及全部输入、组件、两失败记录已核验，见whole_path/artifact_seal.json。E159结果32c358e6的精确包43,935,452 B，15 Git源/11外部源及输入/raw/参考/cal核验通过，见e159/artifact_seal.json；大权重只引用既有LFS完整清单，不重复存档。

E161已完成：`~/mechpop_cache/e161_crossed_entity_relation/scores.npz` 124415B，SHA `fc9135be853d3c99dd3bed59711061af994e29e96484bf481d282942cb4ae08e`，source55960d57；576交换/144正控/588身份、全部原生重放与事后参数buffer恢复通过。实际.532431455h、峰值81.737187GB；ledger/manifest complete。`e161_analyze.py --analyze`与`e161_independent_audit/audit.py --audit --summary ... --output ...`复算，4049元素误差0。E160首轮无完整raw且进程消失，原budget/log不修改，recovery.json记至少2100.608秒与未知精确成本；同源重跑的完整plan/budget/manifest/summary独立位于`results/e160/retry_1/`，不以旧running账本作为完成证据。

E160 retry_1已完成：`~/mechpop_cache/e160_shared_signal_context_cross/scores.npz` 75474B，SHA `b53dfe574a649fd6900634671843798ac4a3b3ee88faab35058f72f0afac2a42`。source55960d57、恢复器967e0dfc；2560常规调用及12额外控制、三源原生cal/参数/buffer、128题自然/零化和全对角分布重放通过。6283.367706142秒=1.745379918h，峰值82.209380864GB，独立监督退出码0；首轮原样保留至少2100.608秒、精确总成本未知。复算入口见E160卡；4524数字/2869计数≤7.11e−15。S轨迹仅保存逐题BF16 SHA，不保留全大轨迹，可由固定inputs/pins重算；小raw与plan足以复算所有统计。

## 2026-10-28完成结果的精确源码封存

E160完整retry的源码/结果与小raw封存在`~/mechpop_cache/e160_shared_signal_context_cross/run_metadata_09903add.tar.gz`（1,184,987 B）；E161对应`~/mechpop_cache/e161_crossed_entity_relation/run_metadata_caff4266.tar.gz`（586,614 B）。逐项SHA、实际raw、输入引用和Git源码对应关系分别见`results/e160/retry_1/artifact_seal.json`与`results/e161/artifact_seal.json`。模型权重沿原始公开HF pin恢复，不重复打包。E160首轮中断和未知完整成本仍保留。CPU复现与统一校验入口见[scripts/README](scripts/README.md)。

E162公开F资产23文件（11权重分片54,275,336,216 B）已完成公共LFS/Git与独立副本SHA核验，来源见`results/full_course_assets_2026-10-28/asset_manifest.json`、提交e94efdec；耐久缓存`~/mechpop_cache/hf_emo_mature/models--allenai--Emo_1b14b_1T/snapshots/007852b1e3d22222f8ee03c6a53fa30e47898dcb`。fvcrc21临时NVMe只作为已核验执行副本；资产阶段未执行模型。plan冻结后在该节点GPU0单卡评测，全部结果尚未完成；CPU可见软件与引用SHA见`results/e162/plan.json`，数值源0bdb36e2。
