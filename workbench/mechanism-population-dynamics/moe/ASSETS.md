# MoE资产与恢复入口（2026-10-29）

**当前：E144–E166全部预定数据已得；E164新55学科/旧精确guard、14条件实际路由交叉及独立复算完成，0新训练/权重下载。** 实时资源及下一决定见[README](README.md)，总上限4卡。全部原始源、失败与继承范围保留；本页负责位置、来源和恢复。

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

## E165新增成熟谱系资产（全量已完成）

`allenai/OLMoE-1B-7B-0924`成熟父pin b99743a400844e532bec7ce4575d97a3a39dcd4d（step1200000-tokens5033B）与退火终点6d84c48581ece794365f2b8e9cfb043c68ade9c5。`results/e165/asset_manifest.json`逐片核对公开LFS；父新增BF16分片逻辑13,838,721,960 B，终点复用原`~/mechpop_cache/hf_olmoe/main/`。耐久视图在`~/mechpop_cache/hf_olmoe_mature/view_{P_b99743a4,A_6d84c485}/`；权重为指向耐久源的链接，没有另复制A权重，metadata是实文件。源码封存时需物化小文件，权重仍依manifest恢复。

新全7节点cache/config清单在`~/mechpop_cache/cross_lineage_inventory_20261029.json`；它确认完整Qwen3-30B-A3B、OLMoE四旧端点及EMO，跨节点同NFS副本不算多个训练重复。范围为已查用户HF/研究缓存，不声称全机器文件系统无其他模型。E165原始输入在`~/mechpop_cache/e165_mature_olmoe_transport/questions.npz`，同E164的55科文本重新编码；全部440题/440cal保留，最大2736、不截断。完整26×440结果、终态、独立24940数字/25383元数据已完成；raw为`~/mechpop_cache/e165_mature_olmoe_transport/scores.npz`，529224 B，SHA85b101dd74248dfe95d8629e40eeafb5102e8e155440123eb588c10fa0de8ce3。数值源0fb295d6、plan9570789c…e25a2；含预检.953168332 GPU时、torch峰值32.875388GB、最多1卡、各阶段exit0。CPU/NFS→NVMe适配单列SHA，不改数值18文件。下一实验状态见唯一README。 [E165封存凭证](results/e165/artifact_seal.json)绑定`~/mechpop_cache/e165_mature_olmoe_transport/run_metadata_5ba79500.tar.gz`，4,429,405 B，SHA10f6b80e612258b3b742ce1a9e2caa4b669e7b4471475d0f7f5adfff681254ed，110个实文件，源码/输入/结果/原生安装源码与公开小文件均逐项核SHA，无大权重。

## 耐久raw与冻结记录（按状态）

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
| E163 | `~/mechpop_cache/e163_message_geometry/`：F为`native_F.npz`，P/A/B在`attempt_3_hash_schema/native_{P,A,B}.npz`，真实消息为`cross.npz` | 五raw绝对路径、SHA/bytes见`results/e163/manifest.json`；summary/独立29650数值/1376元数据完成。原设计19f6f3a5，数值源c31e4b0e，plan SHA7493cb82…4870cb；含失败2.109199484 GPU时、峰值79.318603GB、各组末次退出0 |

**E164完成资产：** 数值源43aee97a、21份源码及公共P/B代码/config/index冻结，plan43877611…048a7。耐久根`/home/xiang/mechpop_cache/e164_runtime_routing/`保存输入`questions.npz/jsonl`、旧参考`references.npz`、冻结57套`selectors.npz`及完整`scores.npz`（988220 B，SHA36bd41e3443bfbe0a9ee13254928fa929aff6cfa0caece6b96fb272760e2b0a3）。完整manifest/summary/independent_audit/execution_complete已得，13238数字/13548元数据最大7.99e−15；preflight/run/chain均exit0，含预检1.444647881 GPU时，峰值55.112093GB，最多1卡。CPU `reproduce.py E164 all`成功；P/B原始HF权重仍用上表，未新增模型副本。gate完整轨迹只在单题内存，保存整体/首层指纹和代码/输入，未声称持久保存全部轨迹；partial_scores只保留在途取证含义。


E162新raw为4,584,469 B，SHA `89c83382c58ebb8ed864d1fa4cf73c47b86ed5ef71c830230b87e84db13394d3`；preflight/budget/summary及独立5114数字/133元数据报告都已完成。E160正式结果在`retry_1/`，父目录原running预算保存首轮中断与未知精确成本，不能拿它冒充完整结果。

E163五份raw共26,716,419 B；cross为692,158 B，SHA `225cacd46f041430219e0f4aecc6bd60a7114b150a8cdf31deb5887e31d1e722`。P/A/B原native worker在指纹命名guard后退出、原终态hash未观测；fresh cal/全部16条件抽样/完整cross与新worker终态均通过，具体继承边界在`results/e163/native_inheritance.json`，不是伪称原worker终态完成。cal/proposal、原19源码及两次失败和CPU等待/中断记录全部保留；CPU重算不需要加载模型。

共同输入继续保留：E150的plan/LM token数组；E153的questions.npz/questions.jsonl和task mask；E151随机mask；E158全前缀component_cache与native_attention；E160/E162继承references。F校准BF16 logits、原生日志和全部监督退出记录在E162耐久目录，清理不触及这些文件。E160完整S轨迹只保存逐题BF16 SHA，需按固定模型/输入重算，不能声称存有未保存的大轨迹。

## 精确源码封存与临时副本

E158–E161对应`artifact_seal.json`给精确Git源码、raw、输入及源结果包SHA。E160包为`~/mechpop_cache/e160_shared_signal_context_cross/run_metadata_09903add.tar.gz`，E161为`~/mechpop_cache/e161_crossed_entity_relation/run_metadata_caff4266.tar.gz`。不重复打包大模型权重。E162精确源码/结果包为`~/mechpop_cache/e162_full_course_native/run_metadata_e2ef1b82.tar.gz`（48,177,862 B），seal在`results/e162/artifact_seal.json`；包内raw/reference/calibration和公共代码已逐项SHA核对，HF符号链接落为实文件。

E163结果提交`44b9e1ed`，数值源c31e4b0e；封存包`~/mechpop_cache/e163_message_geometry/run_metadata_44b9e1ed.tar.gz`为**60,388,837 B**，SHA `068c7d0356fbac2d8d6ff4d146e36f4257101a77378f997cef5c76328a5ba155`。[artifact_seal](results/e163/artifact_seal.json)逐项记209个实文件SHA：五raw、cal/proposals、原/修订源、监督/失败、配置/任务/LM输入、public P/A/B/F代码与config/index、领域定位和主图来源。包内全部文件已独立读取比对，不含失效HF符号链接，不重复大模型权重；公开pin和耐久原源仍保留。

E164结果提交`48f30265`，数值源43aee97a；[artifact_seal](results/e164/artifact_seal.json)对应`/home/xiang/mechpop_cache/e164_runtime_routing/run_metadata_48f30265.tar.gz`，**37,164,702 B**，SHA `ed5bbbb3d96feefdf0aa1f084ecc6219639ab9ead52543bed58be9c0ea01dbdf`。90个实文件已逐项读包核SHA，包含21份冻结源码/依赖、执行/作图/封存/复现入口、输入与raw、cal/selector/监督/费用、公共P/B物化代码/config/index、论文定位及文档快照；不复制权重。冗长CPU准备过程记录只保留本地与包内，Git中的manifest保留完整终态来源，避免重复机器账本。

整理清单与依赖判断见`results/consolidation_inventory_2026-10-28.json`。只清理本批专用的可恢复重复副本；原始HF缓存、raw、原卡、唯一checkpoint及失败记录保留。F临时副本54,309,366,236 B、过期断点5,299,023,610 B及生成bytecode810,775 B已清理；P/A/B临时副本162,856,959,052 B也已在66个耐久文件新鲜SHA核对后清理。累计删除逻辑文件222,466,159,673 B，具体分配块与源码/receipt见[清理记录](results/cleanup_2026-10-28.json)。清理后E160作者统计逐字节复现、E160/E161独立核对与E162完整CPU复现通过，59项冻结源码引用仍匹配。

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


## E166：两谱系增益与伙伴干预（全量完成）

复用上述E164/E165的输入、selector与完整旧分数，来源指纹不变。冻结source ef8f58c8、27文件，plan ae9d5cc6983f8d2dcc9575f893ca011200cbe90990d414fd1627c3f3f60102fc；[plan](results/e166/plan.json)给所有绝对路径/SHA。新cal系数和预测位于`~/mechpop_cache/e166_gain_transport/{emo,olmoe}/`，[完成凭证](results/e166/execution_complete.json)及两个family manifest确认全矩阵、来源终态/独立复算和恢复监督exit0。fvcrc21/1顺序执行，CPU/NFS准备不计占卡，累计cap4 GPU时，总并发≤4；当前实时进度只见README。

E166的EMO节点副本在fvcrc21 `/tmp/xiang-moe-20261029/e166_emo/{P,B}/`，108,571,271,688 B，均为原公开FP32源的实文件；`results/e166/emo_local_staging.json`逐文件SHA，stage636.891秒/0GPU。第一次NFS CPU读取中断的worker/chain失败及648.2秒CPU费用保留；0EMO校准/预测、0GPU。新CPU装载121.235秒，P/B参数/buffer指纹与旧canonical相同，再取得物理1卡。`e166_emo_local.py`只替换locator，原数值27文件保持ef8f58c8；恢复由`e166_resume.py`及`supervision_resume_chain.json`监督，不重跑已完成OLMoE。副本当前仍用于精确重放，耐久HF源保留。

E166完成：GPU工作计时3866.130493秒=1.073925137 GPU时，max1卡，峰值EMO55.024348GB/OLMoE31.920098GB。独立16356数值/16938元数据最大差1.0658e−14。source ef8f58c8、plan ae9d5cc6…102fc和27文件未变；资源源码0fe1553c。完整CPU入口`reproduce.py E166 all`已通过。

- emo raw：`/home/xiang/mechpop_cache/e166_gain_transport/emo/scores.npz`，198730 B，SHA `e50c24cd4f6e0e222d6f3e596ffb33a2537a1115538b547815fc27573fda86a1`；[summary](results/e166/emo_summary.json)、[manifest](results/e166/emo_manifest.json)。
- olmoe raw：`/home/xiang/mechpop_cache/e166_gain_transport/olmoe/scores.npz`，121042 B，SHA `66b1d82fdf3fd15bd6d1b887956caa29f0e7c86810e842cba7c375045078477a`；[summary](results/e166/olmoe_summary.json)、[manifest](results/e166/olmoe_manifest.json)。
