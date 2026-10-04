# E13/E14 本轮终点收尾与人审入口（2026-10-04）

**本轮已结束：8个既定训练终点×8个既定任务全部完成、复算与自有进程清理通过。按用户要求停在当前一步，不追加实验。C01–C04仍L0，没有新建I04或声称找到主会idea。**

## 主要读数

分数是跑前冻结的八任务规范化均值；init父分数28.955977，used父分数32.814492。used为E12 ICONS公开池10K复用模型，不是原ICONS按10K预算重新投票。

| 动作 | init均值 | used均值 | init相对父增益 | used相对父增益 |
|---|---:|---:|---:|---:|
| 旧集重放 | 33.337 | 33.506 | +4.381 | +0.691 |
| 策展池内补货 | 32.913 | 33.815 | +3.957 | +1.000 |
| 池外 source×监督量补货 | 33.118 | 33.581 | +4.162 | +0.766 |
| 池外 source-only 全新补货 | 32.784 | 33.497 | +3.828 | +0.683 |

| 预写对比（pp） | init | used | used−init交互 |
|---|---:|---:|---:|
| fresh_selected_minus_fresh_law | -0.206 | +0.234 | +0.440 |
| fresh_selected_minus_replay | -0.424 | +0.309 | +0.733 |
| fresh_law_minus_replay | -0.219 | +0.075 | +0.293 |
| source_only_fresh_minus_fresh_law | -0.334 | -0.084 | +0.250 |

完整八项向量与全精度差值见[JSON](E13_E14_seed29_terminal_summary.json)和[CSV](E13_E14_seed29_terminal_scores.csv)。不以均值接近宣布向量或训练效用等价：池内−池外在MathVista为+1.8/+2.0，MMVet为−2.018/−1.972；两状态同方向的任务取舍仍只是诊断线索，不能把相关父状态当独立重复。

## 当前科学判断：是否已有值得投入、明确novelty的好idea？

**目前尚未形成可以推荐作为主线重押的、增量清晰的成形idea。** 领域关心数据策展的实际训练收益、复用和成本，但本轮未暴露强方法中足够明确的决策瓶颈，也没有验证针对该瓶颈的新方法。关键缺口不只是再补seed或防御性control，而是从诊断读数走到有实际后果的问题和实质增量。

- **旧重放是强对照。** init四动作范围仅0.553pp，used仅0.318pp；池内补货在used比重放+0.309、在init−0.424。不能讲“学过的数据必然失效，必须刷新”的故事。E12同旧集init/seed17为32.814，E13 init/seed29为33.337（+0.522）；训练seed与评估部署同时改变，不能当纯训练方差估计，但也不宜把本轮约0.2pp排序翻转当稳定机制。
- **策展资格的大幅不可替代收益没有出现。** 池内−匹配池外为−0.206/+0.234；存在单seed排序变化，尚未体现需要router/动态再适配的重大决策损失。也不能因此证明廉价律等价或关闭母问题。
- **放松监督量约束未产生明显平均收益。** source-only−matched-law为−0.334/−0.084；E14同时改变监督量、anchors和内容，不能归因为标签长度或剂量。
- **最值得讨论的线索是任务收益的取舍。** 平均分较接近时，能力向量仍不同；但ICONS的多目标投票、Curation-Bench的任务向量、Critical Look的分池/预算解释均已有相关ownership。“均值掩盖取舍”“简单配方强”“学生状态影响效用”本身不足以成为我们的novelty。当前没有证据决定要以什么新增目标、状态变量或干预解决它。

因此，不建议自动把这一轮升级为论文故事，或沿同一匹配矩阵继续局部细化。交给人审的是完整证据与候选压力，不是预选论文答案；I01/I02/I03和workbench状态保持，未以近邻覆盖或本次小差判死领域。定位入口：[POSITIONING](../POSITIONING.md)、[关键原文/源码阅读卡](../../../library/themes/training-post-training/RSI_PAPER_CARDS.md)。

## 评分与运行完整性

- 八学生推理均rc0、八任务无缺项，原始结果独立复算；没有降为exact_matching评分策略。源码、任务、权重、训练终点与原协议身份沿[manifest](E13_E14_closeout_state.json)。Qwen3.5本地judge替代和并行节点部署均为明确偏离，不称原论文数值复现。
- 7116次chat请求全部HTTP200，abort/error各0；5301次stop、1815次length，任务原max_tokens不改。length不等同评分失败；缓存审计发现两次MMMU validation index10370原生三次解析失败后随机选项（init/fresh_law hit0、used/fresh_law hit1），原分数保留、不挑选重评；各臂均值最坏影响上限0.013889pp，交互0.027778pp。MMVet/MathVista无五次重试耗尽；全部480个LLaVABench score pair无负值/空值。见[metrics](E13_E14_judge_final_metrics_audit.json)、[13号缓存](E13_E14_judge_cache_audit_fvcrc13.json)、[10号缓存](E13_E14_judge_cache_audit_fvcrc10.json)。
- 外层浮点直接等号误拒三支，约1e−14差异在1e−12绝对容差内复核恢复；不重跑任何已完成评分。一次GPU-idle检查在launch前拒绝used/fresh_law，确认空闲后只补原终点。原协调器以failed结束的状态不覆盖；[明确标记的CPU复核](E13_E14_closeout_validation_reconciliation.json)生成最终accepted汇总，所有原worker状态分别保留。
- vLLM改写环境使token不可见，补充PID/start-ticks父子登记；九组件全部已退出，三个自有CPU守护已结束，8034端口关闭，见[清理登记](E13_E14_descendant_cleanup.json)、[实测资源释放](E13_E14_resource_release.json)。未触碰他人任务。

## 成本与边界

- E13训练含前检8.925 A100h，训练＋成功评分调度wall合计 **11.410 A100h**；E14训练含失败2.081 A100h，合计 **2.877 A100h**。两者合计 **14.287 A100h**。不是GPU kernel活跃时间；失败launch前CPU/hash/SSH wall未完整计量、另列未知，不用0冒充完整CPU成本。
- 此次judge恢复从启动到全部退出 **1.371 Blackwellh**；旧失败judge启动至退出日志 **12.501h**另保留，最后资源释放与kernel活跃未知，不将其称精确GPU allocation。API付费0。copy+SHA375.830s，judge内容核验217.068s；首次staging全wall未知。
- 一组配对训练seed29，训练置信区间/方差未知；八任务是已观察公共评估，非新private确认。E13每臂549,353监督token、46共同anchors，text-only刷新覆盖不足；E14 1,078,803监督token且anchors0。optimizer/scheduler均重置，LR/625步/父权重身份沿原卡。

## 交接与停止点

本次授权收尾已完成，不启动下一项实验、不变更ACTIVE分配、不给候选方向自动判决。同行可先看本页、完整向量、两实验卡、POSITIONING，再决定下一研究投入。latent-world-model-planning的当前文档/结果/源码随同共享main提交同步；其另线程仍在推进的任务不由本次RSI收尾接管。
