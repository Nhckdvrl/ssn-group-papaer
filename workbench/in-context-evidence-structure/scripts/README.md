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
