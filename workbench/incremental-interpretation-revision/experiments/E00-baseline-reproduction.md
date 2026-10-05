# E00：公开 Garden-Path 行为基线复现（2026-10-05）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** C00
- **问题（一句话）：** 本地 frozen-model harness 能否在 Amouyal 公开数据上复现已知的 GP-specific comprehension deficit，而 simple comprehension 保持基本正常？
- **设置：** 首先只用 1 个已经本地可用的 7B–14B open-weight instruction model；优先 Qwen3-8B。数据固定为 upstream `extended_gardenpath_experiments.csv`，不改题、不筛题。deterministic / logprob 方案优先；若模型 API 不给稳定 logprob，则固定 temperature=0 的 forced-choice，并重复 prompt-order/control。
- **读数：**
  1. within-`set_id` GP vs non-GP accuracy / P(correct)；
  2. `GP_question` 与 `simple_question` 分开；
  3. 主要效应为 GP-specific question 上的 paired difference，不用 overall accuracy 代替。
- **阳性对照：** simple questions 应显著好于 GP-targeted lingering-misinterpretation questions，且 non-GP 不应出现同量级塌陷；上游论文提供参考方向，但不要求逐点复刻闭源模型数字。
- **噪声地板 + MIE：** 对 item 做 paired bootstrap 95% CI；在改 prompt 前先报告原协议；若 prompt-order 变化导致的波动接近 GP effect，则判定 harness 尚不稳定。MIE 在首轮用“effect 明显大于 prompt-order / repeat 波动并改变下一步是否进入 E01”为标准，不用任意固定百分点。
- **混杂审计：**
  - 噪声地板：PLANNED；
  - 工具有效性：由 simple/non-GP positive controls 检查；
  - 选样耦合：使用全量公开切片，不筛题；
  - prompt 默认值：固定并记录，若复制上游 prefix 则保留其版本；
  - 输入一致性：保存规范化后的每条 prompt hash；
  - 幸存种子：不适用（frozen inference），但不得挑 prompt；
  - 数据污染：作为 psycholinguistic process probe，不把绝对分数解释成泛化能力；
  - 多重比较：E00 只检验注册的主对照；
  - 饱和/地板：分别报告 simple/GP/non-GP；
  - 系统特有：E00 只做 instrument validation，不做跨模型 claim。
- **决策表（跑之前写）：**
  - A：positive control 清楚通过 → 建 E01，接 Jurayj component generator 做 cue timing/strength map；
  - B：simple 与 GP 一起崩 / prompt 波动与 effect 同量级 → 修 harness，不进入机制/新主张；
  - C：模型在 GP 上接近饱和但 simple 正常 → 换第二个开放家族作 instrumentation check；仍不声称“新模型消除了 GP”。
- **算力预算：** < 1 GPU·h 量级；先单模型全量，禁止为了“更完整”一开始并行很多模型。

## 执行细化（2026-10-05，首轮推理之前）
- 固定切片为 276 rows / 69 set_id，每组 GP/nonGP × simple/GP question，不筛题。GP question gold 全 No、simple 全 Yes；question-type 对照有极性混杂，不能独立支撑能力差异。
- 原协议优先：完整 upstream `prefixes.json` 和 `prefixes_rev.json`，各 8 个 prefix；保留 raw continuation `system + "\n\n" + question + "\n\n" + suffix`，不套 chat template。报告全部 16 个 prefix，不选赢家。
- logprob：FP32 softmax 下汇总上游 clean_word 匹配的 Yes/No token variants；P(correct) 在两类 token mass 内归一化，accuracy = P(correct)>0.5。额外保存两类 mass，不能把低 mass 的 forced accuracy 当自然输出有效性。
- 原生 Qwen chat 单独作为 instrumentation contrast：enable_thinking=False，固定 prefix 0，sentence-first / question-first 各一；再加一句 `Read the whole sentence and revise any initial interpretation before answering.`，单独标记为 instruction control。先报告原协议结果，不事后改主读数。
- bootstrap：先在每 set/condition/question_type 内平均固定 prompt 的结果，再按 69 set_id cluster 重采样 10,000 次（seed 20261005）；主要差异 nonGP−GP on GP questions，另报 simple 差异、difference-in-differences 与 subtype。prompt 波动报各 prefix effect 的 min/max、SD 和配对 order delta，不只报 pooled CI。
- 完全相同 raw_reg_0 prompt 全量重复一次，报告概率漂移和 accuracy flips，不择 prompt。
- 固定模型 Qwen/Qwen3-8B（HF revision b968826d9c46dd6066d109eabc6255188de91218；若直连镜像需另记镜像 revision 和逐文件 hash）。复用已有 venv torch 2.7.1+cu126 / transformers 4.51.3；单卡 BF16 eval/inference_mode，无训练。
- 若原协议 positive control 通过，进入 E01；若 chat 恢复，结论限定为协议/默认行为，不升级成不可恢复能力缺损。预算估计保留原 <1 GPU·h，实际记录。

## 结果（跑完后填写；不改上面的内容）
- 数字（含 CI / prompt-order 波动）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
