# E15：原14B checkpoint跨Hu与Wavelength原任务（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1 frozen boundary measurement
- **对应：** C01、C02、P02；补充强于当前3–4B规模的公开parent权重读数。
- **问题（一句话）：** Multi原14B模型在不同natural parent任务及human分布上是否仍占优，能否把某任务排序误当统一语用能力？
- **设置：** Qwen1.5-14B-Chat SHA9492b22871f43e975435455f5c616c77fe7a50ec；Hu原1,365 numeric readouts，无chat/无special tokens；Wavelength原100clues、21值完整assistant likelihood inclEOS，paper关闭thinking。同FP32/TF32关闭，batch8。与已完成Qwen2.5-3B/Qwen3-4B/Flan原读数相比；不同代模型不是干净scale causal pair，也不声称14B是Wavelength最强ceiling。
- **读数：** Hu各phenomenon human对齐与gold/五order差；Wavelength paper mean-MAE、argmax-MAE、human-mean相关及分布距离，50pair cluster CI。Hu no-story不当literal。
- **阳性对照：** Hu固定首末batch1/8概率门1e-3；Wavelength fullcompletion prefix逐项断言，首末batch1/8 logprob概率delta门1e-3（记录独立控制，未过门不解释）。原Flan发布选择完全匹配已建立。
- **噪声地板 + MIE：** deterministic，item/pair bootstrap2000 seed0；不预设大模型应更好，无普适能力MIE。
- **混杂审计：** 权重代际/architecture/data/task不同；不能从新旧大小排名推出scale或post-training因果。仅补横向边界，不能通过多跑旧模型替代32B强ceiling。
- **决策表（跑之前写）：** A跨任务都较好 → 描述表现边界，普通更大更好不是finding；B跨任务/phenomenon反转 → 先审readout与human uncertainty，再考虑是否领域特有结构；C数值失败 → 隔离重跑，不救方向。
- **算力预算：** GPU3在E14后连续两任务，各单卡≤85GB，≤0.2GPU·时，现有28GB权重无新下载。

## 结果
跑前冻结。指标不作SDT；强ceiling未完成，完整阅读与后续解释继续。
