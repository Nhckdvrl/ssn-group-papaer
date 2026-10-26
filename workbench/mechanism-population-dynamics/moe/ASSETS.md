# MoE asset index (E120–E142, 2026-10-26)

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
