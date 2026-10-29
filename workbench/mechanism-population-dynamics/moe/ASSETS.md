# 实验资产与恢复

当前主线见[README](README.md)，所有实验的结果/状态由[实验索引](experiments/INDEX.md)进入。本次清理不删除模型、checkpoint、当前MoE原始数组或科学结果。大资产在`/home/xiang/mechpop_cache`，不进Git；摘要/plan/manifest留在各`results/eNN/`。

## 环境与当前成熟模型

使用已有`/home/xiang/.venvs/mechpop/bin/python`；精确Python/torch/transformers/numpy版本及native源码SHA以E164–E166各`plan.json`为准。CPU复算不加载模型、不下载、不占GPU。GPU研究仍遵守总并发最多4卡，启动前重新核对占用。

| EMO端点 | HF仓库与固定revision | 耐久snapshot |
|---|---|---|
| P | `allenai/StdMoE_1b14b_1T_Preanneal@d2a4949c9d4ad6cf47fbac131f7e020077332b21` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T_Preanneal/snapshots/d2a4949c9d4ad6cf47fbac131f7e020077332b21` |
| A | `allenai/StdMoE_1b14b_1T@b82073bb43aaaddc0f71d5ce139ad291a3948b32` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T/snapshots/b82073bb43aaaddc0f71d5ce139ad291a3948b32` |
| B | `allenai/StdMoE_1b14b_1T_EmoAnnealed@d18c640b39e67f89669f38c5db8b5ed22a6927ca` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--StdMoE_1b14b_1T_EmoAnnealed/snapshots/d18c640b39e67f89669f38c5db8b5ed22a6927ca` |
| F | `allenai/Emo_1b14b_1T@007852b1e3d22222f8ee03c6a53fa30e47898dcb` | `/home/xiang/mechpop_cache/hf_emo_mature/models--allenai--Emo_1b14b_1T/snapshots/007852b1e3d22222f8ee03c6a53fa30e47898dcb` |

上述四模型均13,568,641,024参数，原公开FP32权重11片/约54.28GB。原生评测先CPU载入FP32再转BF16，包括buffers；不能随意替换为另一加载程序。逐片公开LFS SHA见[E150](results/e150/asset_manifest.json)、[P父状态](results/e154/asset_manifest.json)、[F](results/full_course_assets_2026-10-28/asset_manifest.json)。冻结加载实现可用`reproduce.py sources --name e156_loading.py`查询。

OLMoE两成熟端点均来自`allenai/OLMoE-1B-7B-0924`，6,919,161,856参数、BF16分片：

| 端点 | revision / 训练位置 | 耐久视图 |
|---|---|---|
| P | `b99743a400844e532bec7ce4575d97a3a39dcd4d`，step1200000 / 5.033T | `~/mechpop_cache/hf_olmoe_mature/view_P_b99743a4/` |
| A | `6d84c48581ece794365f2b8e9cfb043c68ade9c5`，普通100B退火终点 | `~/mechpop_cache/hf_olmoe_mature/view_A_6d84c485/` |

视图的小文件为实文件，权重可能链接到耐久HF blob或`~/mechpop_cache/hf_olmoe/main/`；两处源均保留。[E165公开分片清单](results/e165/asset_manifest.json)记录路径、大小、SHA与LFS ID。旧20B/419B/2.516T原生窗口及完整Qwen3-30B-A3B等缓存清单见`~/mechpop_cache/cross_lineage_inventory_20261029.json`；同NFS被多个节点看到不算多个训练重复。

## 当前论文的原始数据

| 实验 | 耐久目录 | manifest / plan / summary |
|---|---|---|
| E156 | `~/mechpop_cache/e156_common_parent_cross/` | [结果与来源](results/e156/) |
| E158 | `~/mechpop_cache/e158_factual_role_interchange/whole_path/` | [结果与来源](results/e158/whole_path/) |
| E159 | `~/mechpop_cache/e159_unchanged_function_partner_role/` | [结果与来源](results/e159/) |
| E160 | `~/mechpop_cache/e160_shared_signal_context_cross/` | [结果与来源](results/e160/retry_1/) |
| E161 | `~/mechpop_cache/e161_crossed_entity_relation/` | [结果与来源](results/e161/) |
| E162 | `~/mechpop_cache/e162_full_course_native/` | [结果与来源](results/e162/) |
| E163 | `~/mechpop_cache/e163_message_geometry/` | [结果与来源](results/e163/) |
| E164 | `~/mechpop_cache/e164_runtime_routing/` | [结果与来源](results/e164/) |
| E165 | `~/mechpop_cache/e165_mature_olmoe_transport/` | [结果与来源](results/e165/) |
| E166 | `~/mechpop_cache/e166_gain_transport/` | [结果与来源](results/e166/) |

manifest给完整raw绝对路径、bytes和SHA；`plan`绑定输入、selector与冻结源码。E158只完成`whole_path`，E160正式结果为`retry_1`。E163包含继承的P/A/B与独立F/native/cross；旧worker终态未观测的边界仍在原卡。E166按两个family manifest和`execution_complete.json`确认成功，原CPU-only中断链仍保留失败事实。

E164新55科文本与选择器是E165/E166的来源；不同tokenizer分别编码，不跨模型相减NLL。E166 raw分别为198730/121042 B，完整SHA在[EMO manifest](results/e166/emo_manifest.json)与[OLMoE manifest](results/e166/olmoe_manifest.json)。原raw、全部失败与精确源码均保留。

## 可解包的源码、输入与结果封存

| 实验 | 耐久包 | bytes | 核验入口 |
|---|---|---|---|
| E163 | `/home/xiang/mechpop_cache/e163_message_geometry/run_metadata_44b9e1ed.tar.gz` | 60388837 | [完整SHA与逐文件清单](results/e163/artifact_seal.json) |
| E164 | `/home/xiang/mechpop_cache/e164_runtime_routing/run_metadata_48f30265.tar.gz` | 37164702 | [完整SHA与逐文件清单](results/e164/artifact_seal.json) |
| E165 | `/home/xiang/mechpop_cache/e165_mature_olmoe_transport/run_metadata_5ba79500.tar.gz` | 4429405 | [完整SHA与逐文件清单](results/e165/artifact_seal.json) |
| E166 | `/home/xiang/mechpop_cache/e166_gain_transport/run_metadata_f5d4040e.tar.gz` | 71616234 | [完整SHA与逐文件清单](results/e166/artifact_seal.json) |

封存包含实文件源码、输入、raw、必要公开/native代码及原运行/失败记录，不含大权重；包内逐文件SHA已核对，无依赖原HF cache才能解开的源码符号链接。封存中的旧文档是当时快照，当前说明以后续Git版本为准。

日常CPU复算：`python -B moe/scripts/reproduce.py E166 all`（使用上面的已有环境）。历史程序已退出日常目录，固定来源在[源码索引](scripts/frozen_sources.json)；统一入口仅在运行期间按原路径临时恢复原字节，数值guard和plan均不改。查阅/导出见[scripts说明](scripts/README.md)。GPU重放需从原卡/封存及独立checkout恢复，不覆盖完成目录。

## 原生运行的节点副本

| 节点路径 | 耐久替代与核验 | 当前用途 |
|---|---|---|
| fvcrc21 `/tmp/xiang-moe-20261029/e166_emo/{P,B}/` | 上表EMO P/B；[逐片来源/SHA](results/e166/emo_local_staging.json) | 已核验108,571,271,688 B的FP32实文件，精确重放与后续研究缓存 |
| fvcrc21 `/tmp/xiang-moe-20261029/e165_mature/{P,A}/` | 上表OLMoE；[逐片来源/SHA](results/e165/local_staging.json) | P实文件；A复用旧`/tmp/xiang-moe-20261025/olmoe`权重，不能盲删其链接目标 |

模型加载/路径适配的代码也在固定源码索引与原包中。E166首次NFS CPU读取中断无cal/预测、0GPU；随后stage636.891秒、新CPU装载121.235秒，数值27文件不变。完整费用/退出记录留在原结果，不因整理追认为原链成功。

## 更早的唯一研究资产

- E148：`~/mechpop_cache/e148_native_order_forks/`，原记录72文件/237,114,164,566 B，含唯一parent、optimizer/RNG、pulse/final/thin及更新链。[archive](results/e148/archive.json)及其耐久manifest是恢复入口，未清理。
- E123/E128/E130–E142的学生权重、训练状态、cal缓存和充分统计仍在原耐久目录。逐实验精确路径及当时大小见[完整历史资产清单](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b/workbench/mechanism-population-dynamics/moe/ASSETS.md)和各`results/eNN/`的archive/manifest；旧NVMe表是历史快照，不当作当前存活声明。
- E144–E147的分批raw和执行源码见各manifest及[2026-10-26封存记录](results/execution_2026-10-26_artifacts.json)；E149–E155的耐久目录由原卡与manifest定位。
- 早期已释放的约222.47GB重复临时副本见[原清理凭证](results/cleanup_2026-10-28.json)。恢复工具如`restore_mature_staging.py`从固定源码查询/导出，不恢复过期自动任务队列。
- 阅读PDF与文本在`~/mechpop_cache/moe_*reading*/`；版本/SHA/全文覆盖见[notes阅读凭证](notes/README.md)。导师会议原文保存在[MEETING_10-22_JA](notes/MEETING_10-22_JA.md)，不归为临时缓存。

## 本轮目录清理的恢复

[清理凭证](results/directory_cleanup_2026-10-29.json)中的`source_and_asset_reorganization`记录固定源码、移出对象、原路径、保留替代及验证。历史源码可离线从Git恢复，当前结果和原卡未删；结项头线本地数据及结束实验console的外部归档以该凭证中的archive/manifest为准。没有清理公共HF缓存、唯一checkpoint或其他workbench。

本轮已核验外部归档：`~/mechpop_cache/workbench_cleanup_20261029/legacy_local_assets.tar.gz`，3,010,576,960 B，SHA `b1f34436d31001cd050e0107c7a1726164b8742a2c87304aa0bd4b4d02a743f0`。12,328个原路径/逐文件SHA在同目录`local_asset_manifest.json`（SHA `323656afe0756e4a949d1b83d0510a8ae2f1e9b1b6dc75517984752d67689723`），并收入包内。每个成员核对通过后才移除工作区副本；3,477,809,622 B数据/console完整保留，无变更文件被误删。可先用`tar -tzf`查看，再按原相对路径选择恢复到工作台或外部阅读目录。

既有本地详细/raw/provenance记录仍原地保留，按精确路径在Git中忽略，避免误把数据当源码提交；路径、bytes与SHA登记在同一清理凭证的`retained_local_detailed_records`（12项），包括旧失败信息，不删除或改写其内容。头线旧Pythia checkpoint与Pile缓存早已释放，v3部分图的原NPZ也不完整；本轮归档只覆盖实际存在的数据，不宣称可从纯clone完整重建头线。
