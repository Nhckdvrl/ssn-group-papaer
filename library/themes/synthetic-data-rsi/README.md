# synthetic-data-rsi：data-centric RSI 与合成数据文献

2026-11-27 为重拾 [data-centric-rsi](../../../workbench/data-centric-rsi/) 做的扫描。范围：ICLR 2027 投稿、NeurIPS 2026 接收论文、2026-09 至 11 的 arXiv，以及 blog、awesome 仓库和综述。每份笔记开头都写了读取深度。OpenReview 读不到，没有 arXiv 版的 ICLR 2027 投稿只读了摘要。

| 文件 | 内容 |
|---|---|
| [SCAN_2026-11_A_self_improvement_loops.md](SCAN_2026-11_A_self_improvement_loops.md) | self-play、proposer–solver、自进化 agent、RSI 审计 |
| [SCAN_2026-11_B_synthetic_data_science.md](SCAN_2026-11_B_synthetic_data_science.md) | 合成数据科学，偏重闭环迭代生成 |
| [SCAN_2026-11_C_curation_and_data_agents.md](SCAN_2026-11_C_curation_and_data_agents.md) | 数据选择、配比、归因、数据研究 agent |
| [SCAN_2026-11_D_task_env_synthesis.md](SCAN_2026-11_D_task_env_synthesis.md) | 任务与环境合成 |
| [SCAN_2026-11_E_blogs_awesome_surveys.md](SCAN_2026-11_E_blogs_awesome_surveys.md) | awesome 仓库、blog、综述、workshop、测量工作 |
| [VERIFY_2026-11.md](VERIFY_2026-11.md) | 12 条关键数字的原文核对 |
| [CROSS_A_iterated_learning_performativity.md](CROSS_A_iterated_learning_performativity.md) | 跨领域：迭代学习、文化演化、performative prediction |
| [CROSS_B_coevolution_openendedness_ued.md](CROSS_B_coevolution_openendedness_ued.md) | 跨领域：协同进化、开放式演化、无监督环境设计 |
| [CROSS_C_teaching_learning_replay.md](CROSS_C_teaching_learning_replay.md) | 跨领域：机器教学、学习科学、记忆回放 |
| [CROSS_D_synthetic_other_modalities.md](CROSS_D_synthetic_other_modalities.md) | 跨领域：图像、机器人、科学设计、语音、形式数学中的合成数据与闭环 |
| [CROSS_E_verification_selection_stats.md](CROSS_E_verification_selection_stats.md) | 跨领域：自适应过拟合、回归均值、相关错误、奖励过度优化 |
| [CROSS_F_synthetic_data_wider.md](CROSS_F_synthetic_data_wider.md) | 合成数据第二轮：累积与崩溃、合成预训练、知识与格式、理论 |
| [READ_passk_yue2025_and_2606.15455.md](READ_passk_yue2025_and_2606.15455.md) | Yue 2025 与 2606.15455 全文笔记：pass@k 边界、评测协议 |
| [scripts/frontier_null_model.py](scripts/frontier_null_model.py) | 前沿准入的二项噪声零模型（纯 Python） |
| [READ_better_at_improving.md](READ_better_at_improving.md) | Better at Improving?（主笔亲自全文精读）：child/successor quality、nested replay、继承主导 |
| [READ_why_rsi_hard_to_verify.md](READ_why_rsi_hard_to_verify.md) | Why Is RSI Hard to Verify?：RSI 判据、统计检验、17 家族编码 |
| [READ_memory_full_loop_audit.md](READ_memory_full_loop_audit.md) | 自进化记忆系统的全环审计：评测抖动、修复与退步、保留 |
| [READ_capability_loss_embodied_rsi.md](READ_capability_loss_embodied_rsi.md) | 具身 RSI 的隐性能力损失：名义成功升而尾部与恢复能力降 |
| [READ_evaluation_free_rsi.md](READ_evaluation_free_rsi.md) | 不用任务分数选择的编码 agent RSI（ELITE） |
| [READ_asset_or_expense.md](READ_asset_or_expense.md) | 自进化 agent 的冻结资产记账：12 轮无资产确认 |
| [READ_to_bias_or_not_to_bias.md](READ_to_bias_or_not_to_bias.md) | 合成数据学生能否超过教师的相变（高斯理论） |
| [READ_rsi_arxiv_batch_2026-11.md](READ_rsi_arxiv_batch_2026-11.md) | arXiv 9 篇：证据审计、自改进不可能定理、先升后崩、验证器自训练、遗忘、plasticity、RRSI 等 |
| [CHECK_passk_and_checkpoints.md](CHECK_passk_and_checkpoints.md) | 存在性检查：自我改进闭环的 pass@k 上限、各闭环公开 checkpoint |

汇总的讨论材料在 [workbench/data-centric-rsi/DISCUSSION.md](../../../workbench/data-centric-rsi/DISCUSSION.md)。第一轮工作时的旧论文卡见 [RSI_PAPER_CARDS.md](../training-post-training/RSI_PAPER_CARDS.md)。
