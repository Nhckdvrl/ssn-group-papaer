# synthetic-data-rsi：data-centric RSI 与合成数据文献库

为重拾 [data-centric-rsi](../../../workbench/data-centric-rsi/) 整理的文献。所有内容的汇总和讨论在 [workbench/data-centric-rsi/DISCUSSION.md](../../../workbench/data-centric-rsi/DISCUSSION.md)；本目录放逐篇和逐批的原始笔记。笔记里只写文献说了什么，猜想都单独标出。

## 目录结构

| 目录 | 内容 |
|---|---|
| `scans/` | 2026-11-27 对 ICLR 2027 投稿、NeurIPS 2026 接收论文、2026-09 至 11 的 arXiv 的分主题扫描（A–E） |
| `cross/` | 跨领域扫描（A–J）：其他领域对“闭环”“自生成训练材料”已经知道什么；G 为 PowerPlay、Go-Explore、MCC，H 为 DreamCoder、Decompiling Amortized Knowledge、Epiplexity，I 为学到的环境生成器的失败与修复（Stabilizing UED、ADD），J 为非对称自我对弈 |
| `papers/` | 单篇或小批全文精读 |
| `checks/` | 关键数字的原文核对、存在性检查（pass@k、公开 checkpoint） |
| `prior-2026-10/` | 第一轮（2026-10）的领域地图、近邻定位表、文献账本、10-04 外部审计报告 |
| `scripts/` | 前沿准入的二项噪声零模型 |

## 按问题找笔记

| 问题 | 主要笔记 |
|---|---|
| 闭环能走多远、新信息从哪里来 | `cross/CROSS_A`（迭代学习、performative prediction）、`cross/CROSS_F`（合成数据：累积与崩溃、锐化理论、知识与格式）、`scans/SCAN_2026-11_B`、`papers/READ_to_bias_or_not_to_bias`、`papers/READ_passk_yue2025_and_2606.15455`、`checks/CHECK_passk_and_checkpoints`、`papers/READ_rsi_arxiv_batch_2026-11`（STV、Self-Regress）、`papers/READ_rethinking_diversity_rlvr`（解题侧语义覆盖）、`cross/CROSS_H`（Epiplexity：可学结构 vs 新颖） |
| 闭环为什么先升后平再降 | `scans/SCAN_2026-11_A`（R-Zero 系列、Survive or Collapse、R-Quest、ATRI）、`papers/READ_memory_full_loop_audit`、`papers/READ_rsi_arxiv_batch_2026-11`（Self-Regress）、`cross/CROSS_A`、`cross/CROSS_B` |
| 选进来的不等于学到的 | `scans/SCAN_2026-11_A`（Selection Is Not Learning）、`cross/CROSS_E`（回归均值、自适应过拟合）、`cross/CROSS_B`（UED、Graves）、`scripts/frontier_null_model.py` |
| 改进器本身有没有变好 | `papers/READ_better_at_improving`（主笔精读）、`papers/READ_why_rsi_hard_to_verify`、`papers/READ_rsi_arxiv_batch_2026-11`（Auditing the Product、Agent Plasticity、The Self-Improvement Problem）、`scans/SCAN_2026-11_A`、`scans/SCAN_2026-11_D`（SPADE、PROPEL）、`cross/CROSS_B`（协同进化的进步测量）、`cross/CROSS_D`（DreamCoder、Minimo）、`papers/READ_skill_policy_coevolution_trap`（技能库与策略共同特化）、`cross/CROSS_G`（开放式演化：积累什么、怎样判新任务）、`cross/CROSS_H`（程序库与摊销） |
| 看不见的损失：持久保留 | `papers/READ_capability_loss_embodied_rsi`、`papers/READ_asset_or_expense`、`papers/READ_memory_full_loop_audit`、`papers/READ_rsi_arxiv_batch_2026-11`（Do Self-Evolving Agents Forget?） |
| 测量、噪声、数据方法的真实效应 | `scans/SCAN_2026-11_C`（DataFlex-RL、AutoData、ADE 等）、`cross/CROSS_E`、`checks/VERIFY_2026-11` |
| 生产者强弱与数据价值 | `cross/CROSS_F`、`cross/CROSS_C`（learnability gap、教学理论）、`cross/CROSS_D`（TTS、SynthCLIP） |
| 任务与环境合成 | `scans/SCAN_2026-11_D`、`papers/READ_benchevolver`（冻结生成器、只演化产物）、`papers/READ_automated_conjecturing`（随机扰动 vs 学到的猜想者）、`cross/CROSS_I`（学到的生成器 vs 随机生成加筛选）、`cross/CROSS_J`（非对称自我对弈） |
| 领域全貌、blog、awesome 仓库、综述 | `scans/SCAN_2026-11_E` |
| 安全 | `scans/SCAN_2026-11_A`（RSI Control）、`scans/SCAN_2026-11_B`（Progressive Misalignment） |

## 阅读深度

- 子 agent 多数通过 WebFetch 或 pdftotext 读，每篇看得到的约前 10 万字符，附录与证明大多没读；图多数只读了图注。各笔记开头写了具体读到哪里。
- 主笔亲自通读的：Better at Improving?（27 页全部）。
- 第一批 12 条关键数字已对照原文核对（`checks/VERIFY_2026-11`），修正了 4 处措辞。
- 数字使用前，以原文为准。

## 尚未读的 OpenReview 论文

已读、从清单移出的四篇：Skill–Policy Co-evolution Trap（`papers/READ_skill_policy_coevolution_trap`）、BenchEvolver（`papers/READ_benchevolver`）、Rethinking diversity in RLVR（`papers/READ_rethinking_diversity_rlvr`）、Automated Conjecturing（`papers/READ_automated_conjecturing`）。

OpenReview 对自动访问有机器人检测，不能绕过。需要时请在浏览器下载，放进 `workbench/data-centric-rsi/papers_in/`（已设为不进 git）。

| 论文 | 会议 / 审稿分 | PDF |
|---|---|---|
| Information-Constrained Memory Evolution for Self-Improving Language Agents | ICLR 2027，3/3/4 | https://openreview.net/pdf?id=6co6OsqoT3 |
| Do LLM Agents Still Need to be Told How to Self-Improve? | ICLR 2027，2/3/4 | https://openreview.net/pdf?id=G2nWulnSp3 |
| Task Arrival Order Shapes Experience Accumulation in Memory-Based Self-Evolving Agents | ICLR 2027，2/3/4 | https://openreview.net/pdf?id=I51UbJS8ql |
| SUADS: Sampling-Uncertainty-Aware Data Selection for LLMs | ICLR 2027，3/3/3/3 | https://openreview.net/pdf?id=Oj94zxxkDK |
| Synthetic Pre-pretraining Survives Scale, but Not as a Grammatical Prior | ICLR 2027，3/3/4 | https://openreview.net/pdf?id=P8cMuhbbfz |
| Model Collapse is a Singular Complexity Trajectory | NeurIPS 2026 poster | https://openreview.net/pdf?id=v3gGLfZguI |
| A Computational Perspective to Data Ablation Experiments | NeurIPS 2026 poster | https://openreview.net/pdf?id=7jrxR7M4di |
| Stability and Diversity of Networked Self-Consuming Generative Ecosystems | NeurIPS 2026 poster | https://openreview.net/pdf?id=Mq8Ixa9IkT |
| Understanding the Challenges in Iterative Generative Optimization with LLMs | NeurIPS 2026 poster | https://openreview.net/pdf?id=uMQtAycESf |
| Coherence Mechanisms for Provable Self-Improvement | NeurIPS 2026 poster | https://openreview.net/pdf?id=fp0D7ypA3g |
| Verifier-Backed Hard Problem Generation for Mathematical Reasoning | NeurIPS 2026 poster | https://openreview.net/pdf?id=uuzIPLUUKL |

第一轮的论文卡在 [training-post-training/RSI_PAPER_CARDS.md](../training-post-training/RSI_PAPER_CARDS.md)，编号对应 `prior-2026-10/READING_LIST.md`。
