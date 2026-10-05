# E05：响应标签与 No 的语义校准（2026-10-05）

- **状态：** DONE
- **类型：** DIAG / measurement validity
- **对应：** C00 / P01 / P03 / P04
- **问题（一句话）：** E04 nonGP 的 GP-question floor 是 Yes/No 响应偏置、把未明说的宾语作语用补全，还是特定句法修订困难？
- **触发：** E04 正方向 +19.84 pp [14.04, 25.82]、16-prefix 全正，但 nonGP lingering accuracy 30.71%、GP 10.87%；simple condition 差 +15.40 pp；raw specificity DiD +4.44 pp [−2.99, 11.96]。不能仅看方向就宣布严格 calibration 通过。
- **设置：** 保留原 276 sentence/question/gold，一字不改；fixed upstream reg0 examples；native chat、thinking off、full FP32。当前 query 句先/题先 × 3 response modes：original Yes/No；A/B 分别代表 Yes/No；A/B 分别代表“明确断言此关系”/“没有明确断言（不意味着事件不可能）”。后两模式 A/B mapping 都跑并配对平均，总 10 prompts × 276 = 2,760 evaluations/model。
- **模型：** 固定已用 Qwen3-1.7B 和 Qwen3-8B；目的区分 E00/E03/E04 的 competing explanations，不增加新模型/数据/训练。
- **至少两个解释及预测：**
  1. surface No/token/position bias：仅换 A/B label 就大幅改变 No gold 正确率；mapping A/B 相反时显著不对称。
  2. pragmatic event completion / task meaning：单换 labels 无法解决，而把 No 明确为“不被句子断言”后 nonGP floor 恢复；语义变化的影响超过 label mapping。
  3. syntax revision deficit：明确 task meaning 后 nonGP/basic simple 有效，但 GP 问题仍稳定落后，且 paired difference 超过 query/label 波动。
  4. generic comprehension loss：simple 与 GP-question 的 condition gap 同样大，specificity 不成立；不解读成 revision-specific deficit。
- **读数：** GP/nonGP × simple/lingering accuracy、P(correct)、choice mass；same-set nonGP−GP 与 specificity DiD；query-order interaction；A/B mapping difference，69-set paired bootstrap 10,000、seed 20261005。不把 literal-mode 正确率倒替 E00 原协议。
- **阳性对照：** original native chat 与 E00/E04 对应 cell 方向吻合；两种 mapping 在非歧义/简单问句上可回答，choice mass 不塌陷。
- **噪声地板 + MIE：** FP32 repeat 已 0 flips / max probability drift 2.01e−5；用 query/label 对效应的影响作任务波动读数。只有 GP-specific contrast 清楚、basic/nonGP readout 可用、两种 query order 与 mappings 不颠覆解释，才进入 E01。
- **混杂审计：** 句子与题目未改；mode intentionally changes answer ontology/task specification，是 measurement intervention，不是模型能力提升；few-shot 保持相同原 Yes/No examples，current-option task 明确要求字母；保存全部 input hashes。No 不是显式否认事件；原 gold 基于“句子未断言”，避免把未知标为现实不可能。绝对分数/污染仍不作泛化主张。
- **决策表（跑之前写）：**
  - labels 解救 floor、task meaning 不再有额外效应 → 优先追 response interface；不升级能力 claim。
  - explicit assertion meaning 解救 nonGP、GP-specific paired gap 稳定 → 将新 measurement protocol 明确登记，再接 E01；E00 原数据不作废。
  - 两条件均恢复到饱和 → 证明该 readout 下 deficit 可被任务澄清恢复；不声称 persistent inability，不强行进入原 deficit gate。
  - baseline/floor/顺序仍坏 → 暂不进入 E01；带完整结果做 residency 人审，不扩模型、不机械加 sweep。
- **算力预算：** GPU0（8B）、GPU2（1.7B）两独立单卡，估计合计 <0.3 GPU·h，复用已下载权重和 venv。

## 结果（跑完后填写；不改上面的内容）
- 数字（含 CI）：8B standard 句先 lingering paired difference +26.09 pp [13.04, 39.13]、题先 −34.78 pp [−49.28, −20.29]；asserted 句先 +30.43 pp [20.29, 40.58]、题先 −23.91 pp [−36.23, −12.32]。specificity DiD 分别 +19.57 pp [8.70, 31.16] / −57.97 pp [−73.91, −42.75]。反转仍未消除。
- 8B nonGP lingering：standard 句先/题先 49.28%/43.48%；letter 47.10%/21.74%；asserted 63.77%/33.33%。asserted−letter 的 nonGP accuracy 改变 +16.67 pp [9.42, 24.64] / +11.59 pp [4.35, 19.57]，但不足以恢复稳定测量。
- 1.7B nonGP lingering：standard 36.23%/43.48%、letter 26.81%/26.09%、asserted 13.04%/6.52%；asserted−letter −13.77 pp [−21.01, −7.25] / −19.57 pp [−28.26, −11.59]。单换标签或加入此语义说明没有解救 floor。
- 解释边界：pure label explanation 不足；该 assertion wording 未解决 task meaning，不能据此排除所有语用解释。条件分数强依赖 query order，不作能力/修订机制结论。两模型结果不合并。最大 mapping P(correct) 差：8B 28.97 pp、1.7B 18.52 pp（完整 CI 见 summary）。
- 实际算力：2,760 evaluations/model；8B 350.58s、1.7B 86.02s，合计约 0.1213 GPU·h。
- 结果文件：[8B summary](../results/E05-8B-summary.json)、[1.7B summary](../results/E05-1.7B-summary.json)；对应 scores.csv / config.json；大 predictions 留本地 cache。
- 按决策表执行了什么：baseline/floor/顺序仍坏 → 不进入 E01，不扩模型；整理 [人审](../logs/review-2026-10-05.md)，继续完成独立的数据审计。
- 主张变化：C00 仍 L0，C01/C02 尚无推理结果；不制造 novelty。
- POST-HOC：无结果驱动的筛题/选 mapping；mode contrast 是上半部分预先要求的同 set 比较。
