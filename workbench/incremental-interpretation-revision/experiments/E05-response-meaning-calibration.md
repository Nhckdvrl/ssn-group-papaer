# E05：响应标签与 No 的语义校准（2026-10-05）

- **状态：** PLANNED
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
- 数字（含 CI）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
