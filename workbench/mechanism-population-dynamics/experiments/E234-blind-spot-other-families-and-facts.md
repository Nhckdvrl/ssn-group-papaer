# E234：结论是否只属于 OLMo、只属于算术？——Qwen2.5 与 Granite-3.3，加事实知识纠错（2026-11-25）

- **状态：** PLANNED
- **类型：** PILOT（[提案](../TOPIC_PROPOSAL.md) 第 8 节检验 3；不推进主张）
- **对应：** Q1–Q3 的泛化。前置 E229–E231。用户 11-25：“跑，多卡并行”。

## 问题

E229–E231 只测了 OLMo-3 一个家族，任务只有算术（SCLI5）和多步算术（GSM8K）。本卡在两个独立家族的 base / instruct 对上，加一类非算术任务（事实知识），用同一套设置复现三个核心结论：
1. 接着写（C）比回复别人（O）更少看出错（H − F 更低），新一轮（S）接近 O；
2. base 已有这个不对称；
3. 自己答案后加 “Wait,” 时，正确答案也被大量推翻（误报高），回复别人时不会。

其中 Qwen2.5-7B-Instruct 属于 Tsui 测过的家族，可以直接检验“Wait 主要在移动门槛”是否适用于 Tsui 的模型。

## 设置

- **模型：** `Qwen/Qwen2.5-7B` 与 `Qwen/Qwen2.5-7B-Instruct`；`ibm-granite/granite-3.3-8b-base` 与 `ibm-granite/granite-3.3-8b-instruct`。base 用 F1，instruct 用 F2（chat；instruct 的 F1 本卡不跑）。
- **数据：**
  - SCLI5 286 题、GSM8K-SC 前 300 题（同前）。
  - **事实知识 302 题（新）：** 取自 CounterFact（ROME，`azhx/counterfact` 前 6000 条），8 种关系（首都、大洲、所在国、官方语言、母语、生产商、来源国、国籍），每种约 38 题，按关系写成问句（如 “What is the capital of {主语}?”）。错答案版：“The answer is {target_new}.”；正确答案版：“The answer is {target_true}.”。文件 `data/factual300_counterfact.json`。CounterFact 有少量标注错误，由知识门排除（模型在干净问法下答不出 target_true 的题不进分析）。
- **条件：** 干净问法（知识门）；C / S / O × 错 / 对 × 检查语 N / V / W。
- **跑前修改（11-25）：** 去掉 GSM8K（其长生成占约七成算力，而决策表本来以 SCLI5 与事实题为主），只跑 SCLI5 与事实题。
- **读数：** 同 E231：三选一结论评判 + 认可规则 → 命中率 H、误报率 F、H − F。
- **评判校验：** 事实题是新任务，另抽 40 条人工核对；SCLI5 / GSM8K 抽 20 条。
- **命令：** `scripts/e229_blind_spot.py`（干净问法）、`scripts/e230_check_frame.py`（`--frames N V W`，错答案版与 `--correct` 各跑一次）；fvcrc13 GPU2–3 及其它空卡。

## 读数与判定

- 每个模型 × 数据 × 检查语：H、F、H − F（C / S / O），(H − F)_O − (H − F)_C 与 (H − F)_S − (H − F)_C 的配对 bootstrap 区间。
- W：F_C 与 F_O。

## 阳性对照与噪声

- 阳性对照：instruct 在 V、O 条件下的 H − F 应 ≥ 0.5；不满足的模型 × 数据不解释。
- 噪声同前；事实题过知识门后 base 可能只剩 100–150 题。

## 决策表（跑之前写）

| 结果（V 下，主看 SCLI5 与事实题） | 决定 |
|---|---|
| 两个家族的 instruct 与 base：(H − F)_O − (H − F)_C ≥ 0.15，区间不含 0 | 结论 1、2 跨家族成立 |
| 某家族不成立 | 如实报告，写明是哪一家族、哪一任务 |
| 事实题成立、与算术方向一致 | 不限于算术 |
| 事实题不成立或方向相反 | 任务依赖：算术是“接着写”，事实可能是别的机制；作为对比轴写进提案 |
| W：两家族 instruct 的 F_C 明显高于 F_O（差 ≥ 0.15） | “Wait 主要在移动门槛”跨家族成立，包括 Tsui 测过的 Qwen |

跑完回到讨论。

## 混杂审计

- 事实题的错答案（target_new）有时明显荒谬（如首都写成另一大洲的城市），对三种放法一致；主比较是放法之间的差。
- Granite 的分词器默认不加 BOS（E228 教训）：按分词器默认处理，脚本已如此。
- 其余同 E229–E231。

## 算力预算

每个 instruct 约 888 题 × (1 + 2 版 × 3 检查语 × 3 放法) ≈ 1.7 万次生成，每个 base 同量；4 个模型合计约 6.7 万次生成 + 评判，约 4 GPU·时，分片到空卡。下载 granite-3.3-8b-instruct 约 16 GB（到 fvcrc13）。**实际：** 待填。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI）：
- 结果文件：`results/e234/...`
- 按决策表执行了什么：
- 主张变化：无（PILOT）
- POST-HOC：
