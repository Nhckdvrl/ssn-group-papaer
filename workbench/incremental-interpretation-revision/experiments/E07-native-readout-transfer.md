# E07：发布问答在原生回答边界下的迁移（2026-10-05）

- **状态：** DONE
- **类型：** MEASUREMENT / P03诊断，与E01独立审计并行
- **对应：** P03 / P06 / C01
- **问题（一句话）：** E03巨大的query-order反转是否依赖人为assistant prefill，而不是后续语言证据的使用？
- **设置：** Qwen3-8B固定revision，FP32 frozen thinking off；全部276上游原句/原题/原gold不改，69sets；native boundary / upstream My answer is suffix × 两query orders × neutral/upstream reg0 system × 无/一句generic revise，16配置4416评估。仅程序构造prompt，不生成新语义gold；数据与源题异常原样保留。
- **至少两个解释：** 回答continuation/prefill倾向导致反转，预测去掉prefill后交互减弱；reading-task/evidence-use解释预测去掉prefill仍保留顺序交互。若neutral/upstream不同，则第三个demo-task依赖解释存活。结果不能单独证明内部parse机制。
- **读数：** GP/nonGP×simple/lingering的accuracy、PYes、choice mass；nonGP−GP gap、order interaction、native−prefill，69-set配对bootstrap10000次seed20261005；预定67-set源题clean sensitivity（hyp5_14/hyp5_18），prob/reflexive分项；全配置报告。
- **阳性对照：** nonGP simple与两种任务极性分项；一句revise对照；不设停止E01的门槛，不选择prompt赢家。
- **噪声地板 + MIE：** FP32现有重复0flips/max probability drift约2.6e−5；CI/效应量决定解释，未定义任意accuracy通过线。
- **混杂审计：** 全部同题同gold配对；suffix独立于query order；固定system demos reg0，不混用demo order；所有16配置先登记，不根据观测删行。Yes/No受限概率不是自然生成准确率，choice mass另报。旧source gold语用限制依旧，不将No正确率等同旧解释消失。
- **决策表（跑之前写）：** 去掉prefill消除反转→把P03主要作为接口异常，E01专注cue/extension；反转保留→E01检查语言操作×query order；只有demo变化→区分示例任务诱导与语言内容效应；choice mass低→报告greedy token，不能把受限选项默认值讲成能力。
- **算力预算：** GPU0 neutral、GPU1 upstream，两独立单卡，合计<0.2 GPU·h；复用现有venv/权重，无训练、无下载。实际待记录。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：neutral/base/native，句先nonGP−GP lingering +21.74 pp [11.59,33.33]，题先−39.13 pp [−52.17,−26.09]；交互+60.87 pp [44.93,76.81]。upstream/base/native交互+59.42 pp [43.48,76.81]。全部8个system×repair×boundary组合交互43.48–66.67 pp，CI均正；67-set sensitivity同方向。neutral/native的GP simple句先95.65%→题先62.32%，lingering正确率17.39%→81.16%；nonGP simple保持98.55%/97.10%。choice mass接近1，反转不依赖低选项mass。
- 结果文件：[summary](../results/E07-summary.json)、[scores](../results/E07-scores.csv)、[config](../results/E07-config.json)、[paired CI figure](../results/E07-boundary-order-effects.png)。4416完整任务，GPU0/1独立，合计0.11269 GPU·h。13-qa E01外审子集与E07原始问题不同，不能混合计数。
- 按决策表执行了什么：prefill-only解释不够；保留query/evidence-use与回答倾向竞争，E01检查语言操作×query order。不再寻找一个“通过”的模板。源码预检发现源set ID需带set_前缀，运行前修正，不是结果后筛样本。
- 主张变化：C00/C01/C02保持原等级；E07支持P03的跨boundary行为事实，不声称新parse机制或novelty。
- POST-HOC：无。
