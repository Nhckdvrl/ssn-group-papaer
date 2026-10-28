# MoE资产与恢复入口（2026-10-28）

**当前：E162全部预定条件完成，0新成熟模型训练、0卡在运行，总并发上限4卡。** 本批不自动新增GPU实验；按用户要求整理重复副本与核心入口。科学结论只在[README](README.md)维护，本页负责位置、来源和恢复。

耐久根为`/home/xiang/mechpop_cache`（NFS）；节点`/tmp`是临时NVMe，不能当唯一资产。优先已有`~/.venvs/mechpop/bin/python`（Python3.12、torch2.8.0+cu128、transformers4.57.6、numpy1.26.4）；未另装环境。CPU复算统一见[scripts/README](scripts/README.md)。

## 当前成熟公开模型（全部保留）

四模型均13,568,641,024参数、11个FP32分片约54.28GB。下列原始HF缓存保留；公共LFS/Git SHA和逐文件路径分别在E154、E150、full_course_assets的asset_manifest中。

| 端点 | HF仓库与固定revision | 耐久snapshot |
|---|---|---|
| P | `allenai/StdMoE_1b14b_1T_Preanneal@d2a4949c9d4ad6cf47fbac131f7e020077332b21` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T_Preanneal/snapshots/d2a4949c9d4ad6cf47fbac131f7e020077332b21` |
| A | `allenai/StdMoE_1b14b_1T@b82073bb43aaaddc0f71d5ce139ad291a3948b32` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T/snapshots/b82073bb43aaaddc0f71d5ce139ad291a3948b32` |
| B | `allenai/StdMoE_1b14b_1T_EmoAnnealed@d18c640b39e67f89669f38c5db8b5ed22a6927ca` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T_EmoAnnealed/snapshots/d18c640b39e67f89669f38c5db8b5ed22a6927ca` |
| F | `allenai/Emo_1b14b_1T@007852b1e3d22222f8ee03c6a53fa30e47898dcb` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--Emo_1b14b_1T/snapshots/007852b1e3d22222f8ee03c6a53fa30e47898dcb` |

F=全程EMO 1T+50B，B=标准1T后EMO50B，A=标准1T+50B，P=标准1T退火前；原始初始化/优化链未核实。若恢复公共缓存，按上述repo/revision用现有huggingface_hub下载至`~/mechpop_cache/hf_emo_mature`，逐文件对照manifest SHA；不使用浮动main代替固定版本。

## 完成结果：耐久raw与冻结记录

| 实验 | 耐久读数 | 结果/来源与恢复 |
|---|---|---|
| E144–E147 | 全部分批raw在各manifest的`raw_batches`逐项给绝对路径/SHA | `results/e144`至`e147`的manifest/plan；`execution_2026-10-26_artifacts.json`封存，旧学生权重见下方历史资产表 |
| E148 | `~/mechpop_cache/e148_native_order_forks`，72文件237,114,164,566 B，含唯一parent、optimizer/RNG、pulse/final/thin及更新链 | `results/e148/archive.json`及耐久archive_manifest；不删除为“旧缓存” |
| E149 | `~/mechpop_cache/e149_native_source_cube` | `results/e149/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E150 | `~/mechpop_cache/e150_native_protocol_cube` | `results/e150/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E151 | `~/mechpop_cache/e151_native_selectivity_necessity` | `results/e151/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E152 | `~/mechpop_cache/e152_native_normalizer_counterfactual` | `results/e152/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E153 | `~/mechpop_cache/e153_mmlu_source_transfer` | `results/e153/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E154 | `~/mechpop_cache/e154_native_parent_boundary` | `results/e154/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E155 | `~/mechpop_cache/e155_native_task_branch_necessity` | `results/e155/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E156 | `~/mechpop_cache/e156_common_parent_cross` | `results/e156/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E157 | `~/mechpop_cache/e157_task_subbank_reintegration` | `results/e157/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E158 | `~/mechpop_cache/e158_factual_role_interchange/whole_path` | `results/e158/whole_path/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E159 | `~/mechpop_cache/e159_unchanged_function_partner_role` | `results/e159/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E160 | `~/mechpop_cache/e160_shared_signal_context_cross` | `results/e160/retry_1/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E161 | `~/mechpop_cache/e161_crossed_entity_relation` | `results/e161/`的plan/manifest/raw SHA；原实验卡给精确入口 |
| E162 | `~/mechpop_cache/e162_full_course_native` | `results/e162/`的plan/manifest/raw SHA；原实验卡给精确入口 |

E162新raw为4,584,469 B，SHA `89c83382c58ebb8ed864d1fa4cf73c47b86ed5ef71c830230b87e84db13394d3`；preflight/budget/summary及独立5114数字/133元数据报告都已完成。E160正式结果在`retry_1/`，父目录原running预算保存首轮中断与未知精确成本，不能拿它冒充完整结果。

共同输入继续保留：E150的plan/LM token数组；E153的questions.npz/questions.jsonl和task mask；E151随机mask；E158全前缀component_cache与native_attention；E160/E162继承references。F校准BF16 logits、原生日志和全部监督退出记录在E162耐久目录，清理不触及这些文件。E160完整S轨迹只保存逐题BF16 SHA，需按固定模型/输入重算，不能声称存有未保存的大轨迹。

## 精确源码封存与临时副本

E158–E161对应`artifact_seal.json`给精确Git源码、raw、输入及源结果包SHA。E160包为`~/mechpop_cache/e160_shared_signal_context_cross/run_metadata_09903add.tar.gz`，E161为`~/mechpop_cache/e161_crossed_entity_relation/run_metadata_caff4266.tar.gz`。不重复打包大模型权重。E162精确源码/结果包为`~/mechpop_cache/e162_full_course_native/run_metadata_e2ef1b82.tar.gz`（48,177,862 B），seal在`results/e162/artifact_seal.json`；包内raw/reference/calibration和公共代码已逐项SHA核对，HF符号链接落为实文件。

整理清单与依赖判断见`results/consolidation_inventory_2026-10-28.json`。只清理本批专用的可恢复重复副本；原始HF缓存、raw、原卡、唯一checkpoint及失败记录保留。F临时副本54,309,366,236 B、过期断点5,299,023,610 B及生成bytecode810,775 B已清理；P/A/B副本仍待耐久源新鲜SHA核对，最终数以receipt为准。

P/A/B临时路径在fvcrc20的`/tmp/xiang-moe-20261028/mature_emo_pab/`。未来确需GPU重放时，先在该节点运行`moe/scripts/restore_mature_staging.py --receipt ~/mechpop_cache/pab_restore_NEW_ID.json`，从保留公共源复制并独立哈希。**原冻结凭证`~/mechpop_cache/emo_local_staging_20261028.json`保持SHA2092d5…42a06不变**，新恢复记录另写；不修改旧plan以迁就新时间。CPU统计无需临时权重。

F临时执行目录是fvcrc21的`/tmp/xiang-moe-20261028/full_course_F/`；清理后E162 loader可回退到保留的耐久HF snapshot，不需要复制新的模型。旧数值源码的传递依赖继续保留，不能只凭无直接import删除旧文件。

## 早期唯一资产与历史快照（2026-10-26清单）

下面路径/大小保留该次盘点含义，不冒充今天全部重新哈希。尤其E135约71.7GB H/Y、E130 dense基模的节点副本未有同等耐久拷贝，本批不删；E132/E133及后续已封存资产按manifest恢复。旧初步传输/运行中快照已从本页移出，完整过程在原卡、日志与Git历史。

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

