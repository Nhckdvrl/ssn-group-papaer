# 保留脚本与历史复现

本目录2026-10-08清理后保留126个Python科学/分析/共享脚本。141个历史实验流程、临时等待/封版/补包与画图脚本已从当前工作树退役；它们的内容、SHA与恢复提交保存在[资产清单](../results/ANALYSIS_ASSETS.json)。不把已经完成的等待器和历史“下一步”当运行队列。

完整清理前代码：`859e48c87cfbecaf017c0fd8e286ef18f59a61cd`。每个run附带的原源码快照、config、prompt、数据/输出SHA仍在外置目录。恢复历史代码时使用固定提交，避免拿最新模块混跑旧实验：

```bash
git show 859e48c87cfbecaf017c0fd8e286ef18f59a61cd:workbench/incremental-interpretation-revision/scripts/finish_native_revision_pool.py
```

## 共同资产与约束

外置根目录 `/data1/xiangding/work/incremental-interpretation-revision/`。数据/规范化版本/完整输出/LP/Step审计原包/失败/结果均保留；完整大统计的使用见[results/README](../results/README.md)。模型权重已清理；09:00资源截止已实际执行，当前没有GPU实验或API审计队列，不能自动下载/重载模型。

[env.sh](env.sh)配置无代理与国内HF镜像；推理必须离线。原评分环境 `/data1/xiangding/env/pragmatic-inference-calibration/`，当前模型环境 `/data1/xiangding/env/interpretation-current-models/`，E52生成环境 `/data1/xiangding/env/iir-e52-generation/`；具体torch/transformers/quantization以run config为准，不跨环境当纯模型尺度对比。

新标注/定点审计只允许Step Plan `step-5-preview`、每批≤5、全局共享≤8；凭证仅在仓库外私有配置。成熟自然数据不无差别重审。此次整理没有调用API。

## 保留入口

| 功能 | 入口 | 结果/协议 |
|---|---|---|
| 原源与统一输入 | `data.py`、`data_v2.py`、`stimuli.py` | 数据固定revision/字节/hash与资格版本；不把未知Gold补成No |
| 旧广面阅读/复述/源支持 | `run_panel.py`、`reading_map.py`、`paraphrase_map.py`、`source_scope_map.py` | E52/E53/E59；原生BOS纠正前后分开，E53科学范围仍PARTIAL |
| 语义、filler与新输出审计 | `step_gp_audit.py`、`audit_literal_contradictions.py`、`audit_reading_fillers.py`、`audit_paraphrases_role_v2.py`、`step_role_audit.py` | Step Plan固定协议；技术失败、语态与语义角色区别全部保留 |
| 白盒可见性/自然源状态/用途 | `prequestion_oracle_map.py`、`natural_cue_patching.py`、`shared_source_cross_use.py`及对应`analyze_*` | 完整三族/层/位置/双向图；干预不单独认证语法变量 |
| 原关系/目标/实际回答分析 | `analyze_goal_*`、`analyze_joint_relation_use.py`、`analyze_actual_answer.py`、`analyze_query_guidance_fidelity.py` | 原mapping/Gold/cap/unknown；旧forced-choice与当前actual分开 |
| 当前强模型与词义/frame | `current_open_baseline.py`、`run_lexical_semantic_recovery.py`、`run_predicate_frame_hint.py`、`run_frame_source_bank.py` | E82/E85/E89/E90；完整序列BF16评分分支，不冒称prefix一致 |
| 重建反馈与自然候选 | `run_reconstruction_reward.py`、`run_modern_native_belief_credit.py`、`run_native_revision_pool.py` | E91/E96/E103；未训练analogue，不冒充作者RL复现 |
| 前后credit/预算/自动规则 | `analyze_disambiguation_credit.py`、`analyze_revision_evidence_oracle.py`、`analyze_proposal_budget_credit.py`、`analyze_positive_innovation_credit.py` | E101/E102/E105/E106；冻结候选/位置/规则，不调cutoff |
| 关键依赖与条件候选 | `critical_dependency_audit.py`、`analyze_critical_dependency_commitment.py`、`analyze_dependency_credit_pairs.py` | E107双遍全243、严格/自然隐式支持与条件覆盖分开 |
| GPU截止与离线下载入口 | `gpu_deadline.py`、`download_panel.py`、`download_current_models.py` | 只保留入口，不代表授权重新占卡；下载仅国内镜像 |

其余保留分析器是各完整结果的消费入口，共享依赖经静态闭包核对。唯一原来依赖临时等待器的E79 `estimate`函数已逐字提取到其分析器，科学公式未改；其他保留科学脚本未改。

## 不在当前目录里的工作

旧E00–51材料/协议、一次性格式投影、失败补包、封版等待和全部`plot_*`在固定Git提交可恢复，已经生成的图仍保留。E108没有科学结果：原准备代码保存在固定提交，数据与CPU核验保留外置，当前工作树不留未授权运行入口。

历史卡里命令记录其当时版本；已删除代码的Markdown链接已指向固定Git历史，inline命令不是承诺当前目录可直接执行。执行旧协议前用原代码版本和config核对，不在整理阶段重跑。
