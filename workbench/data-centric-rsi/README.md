# Data-Centric RSI — 可迁移的数据改进策略

## 状态（中文进度页）
**状态：** PROPOSED
**territory / 领域地图：** [FIELD_MAP.md](FIELD_MAP.md)
**目标会议 / 截稿：** ICML / ICLR / NeurIPS；若贡献偏 NLP 数据学习则 ACL / EMNLP 主会；届次未定，截稿 —。
**上次人审：** 尚无实验人审；2026-10-02 用户明确授权调研并注册，不等于批准替换现有 ACTIVE 线。
**一句话（当前版本）：** 从强数据系统的真实训练行为中找值得发展的选择、生成与策略更新问题；数据改进器的可迁移能力是候选方向，不把RSI标签当选题边界。

**已完成：** 关键文献分级阅读、主会近邻定位；E00 已建立 MATH→单卡 LoRA 训练→官方 scorer 的本地改造闭环。E08 统一确定性推理协议后，完整留出 1668 题上静态 120 条真实标注的三个 seed 比 base 高 3.66–4.20pp，E04 错误检索再高 0.78–1.32pp，低于预写的 2pp 追进门槛。E06/E07 的 Qwen2.5 本地教师质量 gate 失败；E09 Qwen3-32B thinking 20 次调用按严格格式仅 1/20 通过，事后诊断 13/20 完整可训练。E10 同卡重评的静态120比 base 高 4.26pp；嵌套静态960反比120低 0.96pp，且两状态错误检索动作 110/120 相同，未通过扩大状态/动作区分资格门。
**当前收尾（2026-10-04）：** [E12](experiments/E12-curationbench-strong-policy-utility.md)强静态校准已完成：base **28.956**，random/均衡/ICONS公开池复用/ARDS **32.299/33.443/32.814/32.951**；同checkpoint唯一复跑 **32.247**（−0.052），八项全齐/无fallback。四SFT及六评价 **7.363 A100分配小时**，judge另计；ICONS臂是公开池复用，非原算法针对10K重新投票。
[E13](experiments/E13-reuse-replenishment-action-pilot.md)六支和[E14](experiments/E14-source-only-replenishment-baseline.md)两支均已成功完成625窗口、保存终点，训练含前检/失败合计 **11.006 A100分配小时**。原E14 judge启动超时且清理遗漏子进程，成本已[纠正并保留](results/E14_judge_startup_failure_audit.json)，不能算方法负结果。用户要求仅补完这八支原定终点评分再上传；相同judge权重本地SHA校验完成，冻结八任务协议已在13/10号空闲单卡接续，[启动身份](results/E13_E14_closeout_launch.json)。尚未完成评分前不报告策略排序；不增加训练、seed或新实验。
**未完成：** 官方 GPT-4o 反馈数据生成原版复现、跨任务/学生状态验证、生成式数据动作的真实训练效用、论文主张验证。所有本地科学主张仍为 L0。

## 阅读入口
- [领域整体、谱系、真实压力与选题尺度](FIELD_MAP.md)
- [逐篇阅读范围与未完成债务](READING_LIST.md)
- [关键论文卡：idea 怎样从近邻中长出来](../../library/themes/training-post-training/RSI_PAPER_CARDS.md)
- [新颖性定位与不能冒领的贡献](POSITIONING.md)
- [开源资产、单节点资源与完整成本](ASSETS.md)
- [本地 agent 的接手边界](LOCAL_AGENT_BRIEF.md)

## 论文形态卡
当前形态是候选空间，不是冻结的 paper story。

- **最有价值的目标**：识别数据闭环在复用/干预决策上的真实瓶颈，建立有训练收益证据的改进方法。
- **C01/C02**：跨学生状态的数据策略效用与低成本再适配；均 L0。
- **C03**：训练干预证据能否改善数据研究动作；L0。
- **C04**：短程代理何时造成长期课程决策错误；L0，初期是公共测量轴。
- **主图候选**：等成本训练收益曲线；学习状态×数据动作的增益而非解题率；留出学生上的改进器收益；包含生成/探测成本的 Pareto frontier。没有结果前不承诺图形方向。
- **强基线**：DataEnvGym 原结构＋强静态配方；有/无反馈；静态/动态生成；常规搜索；与所选方法对应的 LESS/DoGE/ADO/PAC、EEM/AutoLLMResearch 适配对照。不是一开始全部实现。
- **证据目标**：发展成 candidate 前覆盖不止一个模型家族和一个自然任务；独立训练 seed、任务级置信区间、private eval、学习者留出；具体规模按 E00 资源和噪声审计确定。
- **风险**：被“普通数据选择/超参优化”吸收；昂贵内循环；输入反馈泄漏；短程 proxy 误读；不同候选继承不同 optimizer state；只做 toy arithmetic；资产不齐导致重写整个系统。
- **目标会议**：以最终贡献形态选择，不宣称已达到主会门槛。

## Idea 组合
| ID | 一句话 | 来源 | 研究动作 | 状态 | 等级 |
|---|---|---|---|---|---|
| I01 | 数据策略能否成为可复用资产，并只做必要的再适配 | P01/P02/P11/P15/P21 | 固定/交换课程→真实训练增益→学习者 response-conditioned 复用 | SEED | L0 |
| I02 | 从追随错误转向选择有效训练干预 | P03/P04/P05/P12/P14/P15 | 受控干预与自然失败→状态—动作—收益→跨学生策略 | SEED | L0 |
| I03 | 便宜的课程奖励何时需要更长时域校准 | P01/P02/P16/P20/P22 | 等续训条件的多时域收益→校准/信用分配 | SEED | L0 |

E00–E10 曾优先用 DataEnvGym 的本地学生闭环；其静态训练/评估资产保留，但本地生成教师未产出质量合格的训练数据、词面反馈动作跨状态重合过高，故不在该窄动作空间继续堆实验。当前 E12 转向 Curation-Bench 的固定训练契约，用真实训练收益验证可区分的强数据动作；这仍只是下一科学问题的底座。I01/I02 仍为待检验种子，共享可用资产；I03 暂只作测量轴。P01 公开 learner/scorer 可独立用于低耦合测量，但完整生成训练环路尚不可从发布包直接恢复。

## D1–D6
| 交付 | 当前状态 |
|---|---|
| D1 强基线复现 | E00 单卡闭环已运行；是改造版，训练收益对评测提示敏感，反馈策略/官方分数未复现 |
| D2 可复用运行资产 | 数据冻结、单卡训练、vLLM 评估、配对分析脚本可运行；原始大文件在外部缓存 |
| D3 痛点日志 | 已记录反馈题面丢失、输出协议、生成数据正确性与贪心评估重复性问题 |
| D4 系统测量 | E00/E04 各三训练 seed、E05 一个 seed；E08 完整留出 1668 题及确定性复跑完成，强静态收益成立而词面检索增量较小；E10 扩大静态集单 seed 不增益且动作高度重叠；E06/E07/E09 两套本地教师质量 gate 均未过；E12 数据/模型审计及四条10k/625步SFT完成，base/random/ICONS八项均值 **28.956/32.299/32.814**，均衡/ARDS八项 **33.443/32.951**，唯一复跑 **32.247**、单seed训练方差未估；生成分支尚无真实学生效用结果 |
| D5 定位表 | 初稿；近期接收语料/公开评审全面审计未完成 |
| D6 论文形态/idea 组合 | 初稿；没有经验性贡献被确认 |

## 主张与痛点
见 [CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md)。文献已报道的“难度不等于效用”“真实锚定有帮助”“跨配对会变化”“先跑 pilot”不记为我们的新主张。

## 决策记录
- **2026-10-02 · 用户授权调研并注册**：建立本 PROPOSED workbench；不改变任何已有线的状态/优先级，不启动多节点大训练。依据：本轮明确请求及 [RESOURCES.md](../../RESOURCES.md)。
- **本轮执行者建议**：先建设一套能产生可审计训练收益的本地闭环，在同一领域中比较 I01/I02；不是要求用户现在押注某个猜想。

## 资产位置
本地运行资产和重建入口见 [ASSETS.md](ASSETS.md)、[results/E00_manifest.json](results/E00_manifest.json)、[results/E00_dev_analysis.json](results/E00_dev_analysis.json)、[results/E12_full_arrow_audit.json](results/E12_full_arrow_audit.json)。E12 大资产与运行目录在各节点 `/var/tmp/xiang-data-rsi/e12/`。E13在fvcrc13的`/var/tmp/xiang-data-rsi/e13/{train_queue,train_runs}/`，fvcrc10的`/var/tmp/xiang-data-rsi/e13/{eval_batch_v2,eval_runs}/`；[训练队列溯源](results/E13_cpu_dryrun_and_train_queue.json)、[评估接续方案](results/E13_eval_batch_plan.json)和[v2真实启动](results/E13_eval_v2_launch_provenance.json)记录冻结代码与父模型身份。E14在fvcrc12的`/var/tmp/xiang-data-rsi/e14/`，CPU动作/启动/失败接续记录见对应E14 results与实验卡；复用两父和本地evalenv，不新建训练框架。仓库不存 checkpoint、rollout、私有数据或凭证。运行时必须记录源码 SHA、数据 hash、模型 revision、模型/优化器状态、预算和失败记录。
