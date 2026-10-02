# 实际痛点与成功记录

已有 E00/E13/E16 工程测量，尚无科学贡献确认。旧版R01–R15是文献/代码风险；完整保存于[历史账本](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/PAIN_LOG.md)。

## 执行前需注意

- 配置/平台API、checkpoint加载、时间单位和任务信息差异：见[ASSETS](ASSETS.md)。
- 时序标签、negative和latent距离的语义不能自动当作真实最短路、不可达性或物理误差。
- 更换数据同时改变coverage、动作激励等因素；记录并在解释需要时拆开，不把它们作为禁止做方法的门槛。
- 同信息的模型不能被要求恢复不可辨的隐藏状态；完整状态oracle是上界。
- 当前研究问题只由[RESEARCH_PLAN](RESEARCH_PLAN.md)定义；历史“被占/红区/只剩残差”判断不是执行规则。

## 实测记录格式

`P编号｜实际失败或成功｜任务/模型/config/seed｜量级与结果路径/hash｜关联E编号｜解释与下一步`

同时记成功案例、方法无效、简单基线出乎意料地强。不能只收集符合最初叙事的输出，也不要把重复日志当新增科学贡献。

## P01｜调用比例与真实 latency 不成比例（工程测量）

TwoRoom / Fast-LeWM / N=300,K=30,β=1,[2,3],seed=0。8 个 held-out generated episodes 的首/中/末 24 个 bank，3 次实际 GPU timing：FULL-REFINE 平均 57.90 ms；30% TOP-M-SCREEN 58.89 ms；LOWER-BOUND/batch16 用 43.4% 重评却耗时 201.80 ms。wrapper/native scoring 最大差为 0。[E13](experiments/E13_explicit_implicit_matched_pilot.md)、[结果/episode CI](results/E00_E13_E16_20261002_tworoom_engineering.json)。

解释限于工程 bank/此硬件：batch dispatch、CPU selection 和重复 encoding 不能忽略；call fraction 不能写成 speedup。DeepJEPA Appendix D 已明确同类限制，这不是新发现。

原生 TwoRoom、所有方法共享 encode-once cache 后：FULL 35.02 ms、TOP20% 35.00 ms、INTERVAL20% 54.05 ms；问题仍在。[原生结果](results/E00_E13_E16_20261002_tworoom_native.json)。下一步第二任务族与整体搜索预算比较，不凭此关闭 R2。

## P02｜same-state 分支工程接通，公开 setter 精度须另测

两 task 各 64 条分支、88 次 reset、2200 branch/replay controls；8 anchors × 3 replay/task，state 最大绝对误差和 pixel MAE 均为 0。生成数据使用 fresh reset + factual prefix replay，不能据此宣称 dataset setter 恢复完整 physics memory。[E16](experiments/E16_equal_budget_data_value.md) 后续单独做官方 factual-suffix audit。没有 acquisition-effect evidence。

原生 TwoRoom 单独完成：12 factual suffix 误差0/成功12，64 branches与24重复控制误差0；public proxy selector 隔离检查通过。PushT 原生 physics-memory 恢复尚未测，不外推。

## P03｜恢复模型 elite 尚未转化为控制收益（单 seed 小样本）

原生 TwoRoom / Fast-LeWM：20% TOP-M-SCREEN 离线 recall=96.86% [90.58,100]，但8 paired episodes 中与 FULL/CHEAP-300 同为7/8；CHEAP-900为8/8且 decision time仅0.523 s，FULL为1.230 s。7/8的Wilson CI=[52.9,97.8]%，不能声称等价；也不能以8/8宣称CHEAP-900确定更优。[E13](experiments/E13_explicit_implicit_matched_pilot.md)、[结果](results/E00_E13_E16_20261002_tworoom_native.json)。

这说明 offline 模型参照 recall 不足以建立方法价值；下一步保留全部 seed/起点与强 cheap-search baseline，测原生 PushT 后再决定 refinement/search/update 如何分配计算，不局部优化选择器来硬救预设故事。
