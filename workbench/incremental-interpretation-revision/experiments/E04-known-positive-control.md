# E04：已知阳性模型的独立本地校准（2026-10-05）

- **状态：** PLANNED
- **类型：** REPRO / instrument validation
- **对应：** C00 / P03
- **问题（一句话）：** 同一 harness 能否在上游已经给出稳定预期方向的固定 Qwen3-1.7B 上复现 GP-specific deficit，并满足 simple/nonGP 与 prompt 波动检查？
- **选择依据（推理之前）：** upstream `qwen_small_results.csv` regular GP-question P(correct) 的 nonGP−GP 在 Qwen3-1.7B 全 16-prefix 均为正，平均 +18.56 pp，范围 +4.33 到 +32.69 pp；Qwen3-8B 上游与本地均顺序反转。不是依据新增本地结果选择幸存模型，也不是跨模型 scientific claim。
- **与 E00 的关系：** E00 Qwen3-8B 全量结果与 gate B 保留。E04 是 calibration model 的显式调整，不倒替 E00。C00 的范围是“本地 harness 能在公开 GP 数据复现已知 deficit”，不是“Qwen3-8B 稳定存在 deficit”。首次要求的 Qwen3-8B 已执行；这里只加一个有上游证据的 positive control，不扫模型。
- **设置：** upstream extended_gardenpath_experiments.csv 276 原题 / 69 sets；同 E00 全 16 raw prefixes + 2 native chat + 2 generic revise + identical raw_reg0 repeat；所有 prompt 报告、不改 gold、不挑题。Qwen/Qwen3-1.7B HF revision 70d244cc86ccca08cf5af4e1e306ecf908b1ad5e；hf-mirror.com 直连，逐文件 hash；复用 venv；full FP32、TF32 off、frozen。
- **至少两个解释及预测：**
  1. instrument broken：上游已知稳定阳性模型也不能测到注册方向，或 simple 同崩；继续修 scorer/protocol。
  2. Qwen3-8B calibration mismatch：1.7B 重现稳定 deficit，而 8B 反转可对上上游；将失败限定到模型/协议组合，不能说 benchmark 都不可靠。
- **读数：** 和 E00 完全相同的 accuracy / P(correct) / choice mass，GP/nonGP × simple/GP-question，69-set paired 10,000 bootstrap；reg/rev 各 8-prefix 汇总与每 prefix 效应；generic revise 单独报告，明确 prompt behavior vs 能力。
- **阳性对照：** simple 基本正常、nonGP GP-question 高于 GP，正效应不能只来自筛 prompt；与 upstream 已发布各 cell 对比。
- **噪声地板 + MIE：** identical prompt repeat 与 order/bundle 波动；只有 pooled CI 清楚为正、两种 order 都支持方向、且波动不颠覆决策，才可视为 gate 通过。不用任意固定百分点。若 borderline 就保留未通过，不扩大模型 sweep。
- **混杂审计：** question type/Yes-No 极性混杂仍在，主检验同题 condition；同样 logprob normalization；不把模型缩小算 novelty；污染未排除，绝对分数不作泛化能力证据；原题一字不改。
- **决策表（跑之前写）：**
  - 稳定阳性对照通过 → C00 仅按本地 instrument validation 升 L1，立即建立 E01；E01 默认此 positive-control model，Qwen3-8B 后续仅作针对性解释对照。
  - 方向有但 order/bundle 波动同量级 → 仍未通过，追具体敏感因素；不选正 prompt、不进入 E01。
  - simple/nonGP 同崩或上游差距大 → scorer/protocol audit；停止扩模型。
- **算力预算：** 空闲 GPU2 单卡，估计 <0.1 GPU·h（full FP32）；无训练、无 SAE/probe。

## 结果（跑完后填写；不改上面的内容）
- 数字（含 CI / 波动）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
