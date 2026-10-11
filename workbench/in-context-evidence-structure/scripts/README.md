# scripts — 数据构造、打分、分析、机制

环境：`/home/xiang/miniconda3/envs/verl-clean/bin/python`（下称 `$P`）。所有 `build_*.py` 以固定种子写 `data/<name>/rows.jsonl`；`run_lm.py` 把打分写到 `results/<name>/<model>.s<shard>.jsonl`；`analyze_*` 读这两者。

## 核心库
| 文件 | 作用 |
|---|---|
| `ices/oracle.py` | exact 层级 Bayes oracle：规则 = (属性, 极性)，HMM（变化率 λ × 噪声 ε 网格）；set / sequence / meta 三种 oracle；`all_oracles_fast` 为向量化版本 |
| `ices/oracle_perm.py` | K 类映射漂移的 exact oracle（全部 K! 个双射上的 HMM），E25 |
| `ices/generator.py` | nonce 属性规则 episode 生成与渲染（E00–E02a） |
| `ices/step5.py`、`ices/screen_lexicon.py` | StepFun step-5 审计客户端（Step Plan 接口，带 jsonl 缓存）与 nonce 词库筛选 |
| `tests/test_oracle.py`、`tests/test_oracle_perm.py` | oracle 单测（含路径穷举） |
| `analyze_common.py` | 读取、配对 bootstrap CI、格式化 |

## 打分与调度
| 文件 | 作用 |
|---|---|
| `run_lm.py` | 精确多 token log-prob 打分（左填充 + 显式 position_ids；`--ablate L:H,...` 头消融；按 uid 续跑，结束时一次写出） |
| `run_queue2.sh HOST GPU "DATA:MODEL[:SHARD:NSHARD] ..." [BS]` | 等卡空闲后顺序执行（同一张卡只放一条队列） |
| `launch.sh HOST GPU MODEL INP OUT [SHARD NSHARD BS]` | 立即启动一个打分任务 |
| `stage_model.sh` | 把模型暂存到 `/tmp/xiang_hf/hub`（绕过慢 NFS） |
| `run_think.py` | vLLM thinking 模式生成与答案解析（E09） |

## 实验 → 构造 / 分析脚本
| 实验 | 构造 | 分析 |
|---|---|---|
| E00–E02a 结构网格 | `build_e00.py`、`build_struct.py`、`build_dim.py`、`build_cue.py` | `analyze_struct.py`、`analyze_similarity.py`、`fit_models.py`、`summarize_models.py`、`analyze_groups.py` |
| E04 局部更新 | `build_local.py` | `analyze_local.py` |
| E05/E06 标签流与开关 | `build_switch.py`、`build_stream_nat.py` | `summarize_switch.py` |
| E07/E13 自然语言 | `build_nl.py` | `summarize_switch.py` |
| E08 长上下文 | `build_long.py` | `analyze_long.py` |
| E09 thinking | （复用 struct 数据）`run_think.py` | `analyze_think.py` |
| E10/E10b 游程头 | — | `attn_probe.py`、`analyze_attn.py`、`analyze_ablate.py`、`fit_hazard.py` |
| E11/E15/E16 确认版 | `build_task.py`、`build_task2.py`、`build_numcls.py`、`build_rel.py` | `summarize_switch.py --data <name> --formats ...` |
| E12 toy | `toy/train_toy.py`、`toy/eval_toy.py` | — |
| E17 任务向量 | — | `fv_patch.py`、`fv_patch2.py` |
| E18 LoRA | `lora_train.py`、`run_lora_pipeline.sh` | `summarize_switch.py` |
| E19 FV 任务 | `build_fvtask.py` | `summarize_switch.py` |
| E21 最近邻 | `build_local_nat.py` | `make_figs.py local` |
| E22 / E23 / E32 | `build_marked.py`（`MODE=marked / daystamp / nonce`） | `analyze_marked.py`（`DATA=...`） |
| E24 / E24b | `build_ctxmark.py`、`build_ctxmark2.py` | `analyze_ctxmark.py`、`analyze_ctxmark2.py` |
| E25 多类置换 | `build_mc.py` | `analyze_mc.py` |
| E26 删除影响 | `build_reset.py` | `analyze_reset.py` |
| E27 换任务 vs 翻映射 | `build_taskswitch.py` | `summarize_switch.py --data taskswitch` |
| E28 / E29 不均衡翻转 | `build_imbal.py`（`FMTS=condarith OUT=imbal_ca`） | `analyze_imbal.py`（`DATA=...`） |
| E30 / E34 主效应 vs 交互 | `build_ctxeffect.py`（`TAGPOS=far`） | `analyze_ctxeffect.py`（`DATA=...`） |
| E31 / E33 词表分离 | `build_vocabsep.py`（`VOCABSET=graded`） | `analyze_vocabsep.py`、`anchor_sim.py`、`analyze_vocabgrad.py` |
| E35 领域分离 | `build_domain.py` | `analyze_ctxeffect.py`（`DATA=domain`） |
| E36 逐头分解 | `mech_heads.py` | `mech_analyze.py`、`mech_analyze_imbal.py` |
| E37 锚点 value | `mech_values.py` | `mech_values_analyze.py`、`mech_values_ctx.py` |
| E38 因果修补 | `mech_patch.py`（`--pred`、`--mid`） | `mech_patch_analyze.py MODEL [patch|patchpred|patchmid]` |
| 图 | — | `make_figs.py`（`main`、`marked`、`local`） |

已放弃的分析（保留作记录）：`analyze_additivity.py`（饱和混杂）、`attn_probe2.py`（无诊断力）。

## 典型复现（以 E30 为例）
```bash
cd scripts && $P build_ctxeffect.py                                   # -> data/ctxeffect/rows.jsonl
bash launch.sh fvcrc13 0 Qwen/Qwen3-8B $PWD/../data/ctxeffect/rows.jsonl $PWD/../results/ctxeffect/Qwen3-8B.s0.jsonl
$P analyze_ctxeffect.py ../results/ctxeffect/Qwen3-8B.s0.jsonl
```

## E115–E119：完成的形成与功能机制复现（2026-10-12）

以下从workbench根目录运行，采用conda `verl-clean`、冻结FP32/eager；每个模型一个空GPU，设置`CUDA_VISIBLE_DEVICES`。写到新`--out`，不覆盖原始结果。正式卡/`run.json`是seed、model revision与源码SHA的依据。

| 卡 | 科学入口 | discovery → validation确认 |
|---|---|---|
| E115 Llama | `e115_llama_native_mechanism.py` | 16/115001 → 32/115101 |
| E116真实MHS | `e116_native_mhs_formation.py`，model参数选择家族 | 各16/116001 → 32/116101 |
| E117双方面 | `e117_criterion_feature_formation.py` | 各16/117001 → 32/117101 |
| E118正交criterion/code | `e118_criterion_code_feature_crossing.py`；Mistral确认`e118_mistral_materials.py` | 各16/118001 → 32/118101 |
| E11914B native | `e119_native_scale.py` | 16/119001 → 32/119101 |
| E11914B criterion | `e119_criterion_scale.py` | 16/119201 → 32/119301 |

Mistral E118确认独立入口只补可构造的新负词nasty/有限CPU guard；无评分CPU失败保留。原E118 discovery源码在41c22ffa，Llama确认CPU retry版本在a5321874，最终Mistral入口在7249439a；原hash均见卡。E119科学脚本与prospective方向observer在be96cd03、首评分前冻结。重建不选择contexts或改指标。

```bash
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e115_llama_native_mechanism.py --model /tmp/ices_models/Llama-3.1-8B --n 32 --seed 115101 --materials validation --out results/rebuild_e115_llama
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e119_criterion_scale.py --model /dev/shm/ices_models/Qwen3-14B --n 32 --seed 119301 --materials validation --out results/rebuild_e119_criterion
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e119_response_rotation.py --out results/rebuild_e119_criterion
```

最后一例在fvcrc10 RAM模型缓存存在时使用；易失缓存从官方HF snapshot revision40c069…重建。Qwen3-8B/14B是post-trained模型，本接口不生成thinking，不能称Base或完整reasoning测试。

完成原始批后，用以下报告脚本重建小汇总/图。它们核对完整行数和全部条件，不改变科学评分：

```bash
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e117_wave_summary.py --plot
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e118_wave_summary.py
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e119_response_rotation.py --out results/e119/criterion_discovery
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e119_response_rotation.py --out results/e119/criterion_confirmation
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e119_wave_summary.py
```

E117完整四点profile由`e117_complete_feature_profile.py`生成；探索标POST-HOC-DESIGN/PRE-RESULT，确认评分前冻结，不冒称两个阶段都是original primary。独立raw审计在`results/e117/`、`e118/`、`e119/`，读raw后才对作者汇总；无独立GPU复跑。JSONL/高维模型资产不进git。

## E120–E123：原生操作与整体功能复现

| 卡 | 科学入口 | discovery → confirmation | 每context评分 |
|---|---|---|---:|
| E120原生操作/有限恢复 | `e120_operation_necessity.py` | 16/120001 → 32/120101，`--materials validation` | 512 |
| E121真实SST形成/固定词关联 | `e121_natural_sentiment_mechanism.py` | 16/121001 → 32/121101，`--materials validation` | 344 |
| E122两个来源整体政策 | `e122_source_preserving_formation.py` | 16/122001 → 32/122101，`--materials validation` | 488 |
| E123真实文本政策×namespace | `e123_natural_source_function_policy.py` | 16/123001 → 32/123101，`--materials validation` | 680 |

每项四模型均固定执行两批；参数、revision、源码SHA见各`run.json`，运行在conda `verl-clean`（Python3.12/torch2.8.0+cu128/transformers4.57.6）。`--preflight-only`只验证材料/token几何，不加载主模型；`--analyze-only`重建既有raw汇总。E120–123全部完成；每项完整run与独立审计提供实际证据。

SST数据可在任意路径复现，不要求原作者HOME缓存。以下helper从pinned official JSONL下载，验证三个文件SHA、行数、顺序，然后仅在内存中指定冻结builder的CACHE。它不改材料选择或评分。相同Arrow writer环境下三个Arrow SHA亦与原运行完全一致。

```bash
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/reproduce_sst.py --cache-dir /tmp/ices-sst-rebuild --experiment e123 --model /tmp/ices_models/Llama-3.1-8B --out results/rebuild_e123_llama --n 32 --seed 123101 --materials validation --preflight-only
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/reproduce_sst.py --cache-dir /tmp/ices-sst-rebuild --experiment e121 --model /tmp/ices_models/Qwen3-8B --out results/rebuild_e121_qwen --n 32 --seed 121101 --materials validation
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e122_source_preserving_formation.py --model /tmp/ices_models/Mistral-7B-v0.3 --out results/rebuild_e122_mistral --n 32 --seed 122101 --materials validation
```

将python/model路径换成自己的已安装环境/缓存；下载revision不变。不要写入既有正式`--out`。仅需CPU数据重建时省略`--experiment`。完整后运行`e120_e121_report.py`、`e122_wave_report.py`和`e123_wave_report.py`重建小报告/图；报告同时披露指定candidate词表和full-vocabulary argmax，不改primary。作图使用matplotlib，原始行为/contexts JSONL不进git，科学source与报告source分开。


## E124：共享身份信息的形成/读取反事实

科学入口`e124_source_identity_coordination.py`，3模型(Qwen8/Mistral/Llama)全部16/124001→32/124101，确认`--materials validation`且Source姓名改Robin/Jordan。47条件×8/context，完整词表primary、候选分数/私人方向均保存。所有private监督跨Source形成禁读，F/R只改变无标签名单可达阶段；原position不复用。首评分前科学SHA ea65caf59d2b69ef5c14803fd1edbd7b227ad3813d2b4fa261c001faaaaea727。

```bash
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/reproduce_sst.py --cache-dir /tmp/ices-sst-rebuild --experiment e124 --model /tmp/ices_models/Llama-3.1-8B --out results/rebuild_e124_llama --n 32 --seed 124101 --materials validation --preflight-only
CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/reproduce_sst.py --cache-dir /tmp/ices-sst-rebuild --experiment e124 --model /tmp/ices_models/Llama-3.1-8B --out results/rebuild_e124_llama_scored --n 32 --seed 124101 --materials validation
```

沿用上表模型revision/conda/FP32/eager，不更改冻结builder。全部6批完整后`report_e124_identity_coordination.py`重建小报告/图并检查完整行数、预检上下文byte相等、47query与17prefix全层实际mask消费。不对已有out重写，raw JSONL留共享资产路径，不进git。


E125同portable入口`--experiment e125`，科学源`e125_public_output_schema_coordination.py`；n16/125001→n32/125101(确认validation)，63×8/context，Source→词集合的真实/无关/交换公共表×F/R。公开表提供关系监督，未提供私人评论–标签配对。科学SHA75f7566582cbaf7cf80dd130b409b32436df281a262884d8db381991437612b9首评分前a0a79918冻结。全部6批完整后`report_e125_schema_coordination.py`重建汇总/图并检查21prefix/63whole-query各层消费；同revision/FP32/eager，无训练或层/head搜索。

E126复现入口同样支持 `--experiment e126`，模型参数/seed126001→126101、materials discovery→validation保持冻结源；Llama32确认用已下载pin rebuild cache的上下文byte-identical，见 `results/e126/portable_reproduction_audit.json`。运行时Source缓存组合、全query schema遮罩与全部43条件由科学脚本固定。
