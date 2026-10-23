# 矿区D脚本入口

脚本在本目录维护；冻结输入、完整raw、权重和vendor均在[ASSETS](../ASSETS.md)指定的仓库外资产根。历史run保存当时runner源码/配置，当前脚本修改不会覆盖历史记录。本文是导航，不是要求重启所有队列。

## 工作流与文件职责

| 环节 | 入口 | 输入→输出 |
|---|---|---|
| 官方资产库存 | `audit_assets.py`、`inspect_training.py`、`inspect_timelines.py` | 固定vendor/HF资产→来源、训练/正式评测/时间结构清单 |
| 补充互动资产 | `inspect_interaction_release.py` | MiniMax固定发布parquet→来源hash、角色/轨迹/评分连接及结构覆盖；不调用模型、不重评分 |
| EW来源连接 | `index_update_provenance.py`、`inspect_update_supervision.py`、`index_role_interactions.py` | 公开混合任务→作品/角色/连续出场/原生下一turn索引 |
| 可复用连续经历入口 | `experience_store.py` | 整个发布训练文件→只读字节偏移/哈希索引，连接同一出场的动机/互动/更新与下次出场；不新增场景/标签或改训练划分 |
| 适应学习资料视图 | `build_adaptation_views.py` | 来源索引＋冻结作品划分→全部更新的输入/监督hash、后继任务与接续资格；可显式导出原生SFT数据，不调用模型或训练 |
| 学习输入预算 | `inspect_adaptation_budget.py` | 原生SFT导出＋固定本地tokenizer→全部输入/监督token数量及上下文预算覆盖；不截断、不筛选或训练 |
| 训练基线 | `prepare_adaptation_training.py`、`train_adaptation_sft.py` | 原生三任务→固定token缓存→完整更新SFT/等forward-token多任务SFT；只对completion训练，保留检查点/优化器/RNG |
| 完整对话训练 | 上述prepare加`--all-assistant-turns`、`training_targets.py`、`run_fullturn_study.py` | D-E12完整assistant spans、同预算SFT→同一冻结后续评测；不覆盖D-E10，逐任务验证/最终checkpoint/盲评分开记录 |
| 后续互动冻结与消费 | `adaptation_protocol.py`、`prepare_adaptation_evaluation.py`、`run_adaptation_pipeline.py` | 固定经历→新态→生成动机→多个原生后续context；同场景已发生行为不当作未来评价 |
| 原生连续互动 | `run_native_rollouts.py`、`queue_native_rollouts.py`、`score_native_rollouts.py` | D-E11官方模拟器＋本地传输；生成互动/反思/后续场景，最终SFT自动接入，全部完成后独立原生角色分项评分 |
| 学习后的评价与交付 | `score_adaptation_quality.py`、`summarize_adaptation_study.py`、`finish_adaptation_study.py` | 本地盲评/共同消费者NLL→作品层区间；只对全量完成生成主表，完成后可按授权提交两份结果至main |
| ArcANE冻结 | `prepare_arcane.py`、`prepare_summary.py`、`prepare_state_summary.py` | 官方probe/来源→D-E01/03/07冻结messages和独立references |
| LongEvo冻结 | `prepare_phase.py`、`prepare_phase_judge.py` | 选定对话→四文本条件及原生评分输入 |
| 状态更新冻结 | `prepare_updates.py`、`prepare_closed_loop.py`、`prepare_closed_actor.py` | 原生单步或连续更新→状态输入与后续角色输入 |
| 完整前缀冻结 | `prepare_prefix_memory.py` | 原生叙事单元→固定窗口、查询截断边界及actor模板 |
| 源纠正 | `repair_arcane_source.py` | Monte原生14单元→完整覆盖的分片/归并任务；旧117章错误记录不覆盖 |
| 源文件资格 | `inspect_source_bindings.py` | EW冻结训练场景与单独发布场景逐字对照；只记录不同命名空间，不重排、替换输入或重评分 |
| 本地生成 | `run_local_arcane.py`、`run_local_text.py` | 冻结任务→逐条raw、token IDs、usage、配置/源码快照 |
| 本地权重缓存 | `cache_local_weights.py` | 固定HF snapshot从共享盘复制到NVMe；逐文件及LFS SHA核对后才启用，推理/NLL记录实际路径与缓存manifest |
| 本地运行依赖 | `cache_local_runtime.py` | 对现有依赖逐文件复制/校验，完成后为隔离venv启用NVMe overlay；不升级版本、不改正在运行的训练 |
| 连续生成 | `run_closed_updates.py`、`run_prefix_memory.py` | 连续冻结经历＋上一提交态→全部尝试及提交态；统一恢复/承接规则 |
| Token Plan | `run_judge.py`、`run_plan_state.py`、`run_plan_compiler.py` | 预登记输入→完整供应方回包/usage；禁止现金fallback |
| 来源句前向 | `score_target_likelihood.py`、`score_role_likelihood.py` | 冻结参考回复→条件token损失；不是生成或LLM裁判 |
| 评分输入 | `prepare_arcane_local_judge.py`、`prepare_update_quality.py`、`prepare_plan_quality.py` | 完整actor输出＋原生rubric→冻结judge任务 |
| 聚合 | `summarize_results.py`、`summarize_updates.py`、`summarize_state_quality.py`、`summarize_likelihood.py`、`summarize_closed_behavior.py` | 已保存记录→表/配对区间/覆盖；不调用模型 |
| 未完成前缀覆盖 | `summarize_prefix_coverage.py` | 两worker结束后核对原始尝试、提交态、问题覆盖与成本；不评分完成者子集 |
| 复算编排 | `recompute_arcane.py`、`recompute_continuation.py`、`recompute_prefix_results.py` | 已结束依赖→主/严格表、图；未结束会等待，不会代替模型运行 |
| 图 | `plot_arcane.py`、`plot_baselines.py`、`plot_closed_behavior.py` | 聚合JSON→PNG/PDF；不同任务/样本不混分 |
| 审计与成本 | `verify_measurement.py`、`compare_judges.py`、`summarize_runs.py`、`collect_continuation_costs.py` | 原始输入/输出/metadata→来源核验、独立调用账与评分比较 |
| 事后描述 | `describe_update_context.py`、`audit_update_subjects.py` | 输入结构统计、已完成审阅记录导出；不是新增模型评价 |
| 学习监督审计 | `audit_adaptation_learning.py` | D-E10训练顺序、原生多轮源及全部生成→目标覆盖/输出长度；离线事后描述，不重评分 |
| 持久归档 | `archive_runs.py` | 已结束/有中断说明的run与冻结输入→仓库外tar.gz＋逐成员SHA清单 |
| 学习与互动持久归档 | `archive_adaptation_study.py` | 等D-E10/D-E11注册结果完成，保存原始证据和最终LoRA/优化器，逐成员核验后仅同步轻量manifest |

## 队列归属

队列会启动本地推理或API，**不是离线复算命令**。它们是特定实验当时的资源编排；硬件槽位与依赖须按实验卡及当前运行状态确认，不直接重复执行已完成队列。

| 实验 | 编排脚本 |
|---|---|
| D-E01–03（首夜历史） | `queue_judges.py`、`queue_local_judges.py`、`queue_summary_actors.py`、`queue_capacity.py` |
| D-E04/05 | `queue_identity_control.py`、`queue_update_quality.py`、`queue_plan_quality.py` |
| D-E06 | `queue_evidence_state_behavior.py`、`queue_closed_behavior.py`、`queue_strong_consumer.py` |
| D-E07纠源/评分 | `queue_corrected_summary.py`、`queue_corrected_judges.py` |
| D-E08 | `queue_strong_compiler.py`；`handoff_gpu3.py`为本次已有队列的一次交接 |
| D-E09（已预算停止） | `queue_prefix_memory.py`；原定后续角色/评分未启动，不自动重启 |
| D-E10（运行中） | `queue_adaptation_evaluation.py`按训练完成标记接最终checkpoint；`score_adaptation_quality.py`等strong32释放GPU后评分；`finish_adaptation_study.py`等全部系统/评委完整后复算与提交 |
| D-E11（运行中） | `queue_native_rollouts.py`现于GPU1顺序执行三路径；全生成结束后`score_native_rollouts.py`在GPU1评分，避免与GPU3新训练争用 |
| D-E12（运行中） | `run_fullturn_study.py`在GPU3训练，之后按依赖接固定评测与结果同步；D-E11生成及其后续评分已移交GPU1 |

旧`queue_judges.py`的Plan评分路径已资源中止，不因其文件存在而恢复。`handoff_gpu3.py`不是通用清理工具；不用于终止其他项目进程。D-E09冻结窗口、提示、恢复或抽样政策保留历史，不靠修改它们补造完成状态。

## 常用离线操作

在仓库根执行；示例复算至`/var/tmp`，避免覆盖Git中的历史结果。用`--help`查完整参数。stdlib分析可用`python3`；模型/官方包依赖使用[已记录解释器](../ASSETS.md)。

```sh
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/summarize_closed_behavior.py --asset-root /var/tmp/ssn-game-npc-d --consumer qwen3_8b --out /var/tmp/D-E06-recomputed.json
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/summarize_results.py --asset-root /var/tmp/ssn-game-npc-d --experiment D-E08 --out /var/tmp/D-E08-recomputed.json
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/collect_continuation_costs.py --asset-root /var/tmp/ssn-game-npc-d --include-strong-compiler --require-complete --out /var/tmp/D-E06-08-costs.json
python3 -m unittest discover -s workbench/game-npc-agents/mine-d-affect-relationships/tests -q
```

严格JSON加`--strict-native-json`，但其非均匀轨迹缺失必须连同分数汇报。D-E09完成后才使用包含`--include-prefix --require-complete`的完整续测成本账。重新生成任务或跑模型须遵守实验卡，不将“可运行”视为新实验的科研理由。

D-E09如存在`transport_stopped.json`，`recompute_prefix_results.py`明确报未完成，不生成APF/PTF表。预算停止后使用`summarize_prefix_coverage.py --asset-root <根> --out <覆盖报告>`及**不带**`--require-complete`的含前缀成本账，保留未完成状态。
