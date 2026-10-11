# Pragmatic Inference Calibration：旧项目终止与有效边界

原工作台于 2026-10-03 由用户明确要求终止。当前不保留 `workbench/pragmatic-inference-calibration/` 的实验缓存与源代码；可核验的原始实验卡及关闭审计见 [历史快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/81e319fdc3414b7b6d16c8950f0046646d198cb1/workbench/pragmatic-inference-calibration)。独立领域的 68 篇分级阅读卡仍留本主题。

- **E65：** 低维全局响应映射对 DPO 分布的来源外预测误差较直接沿用 SFT 下降 90.9%–96.2%；这不是“LLM 语用能力下降”的因果发现。
- **E66：** 人类资料 271 项、2285 个评分对应；网页隐藏 speech cue 与三态许可边界尚未裁决，不应直接报告完整 FPR/d′。
- **E67：** 同系列 OLMo2 SFT/DPO 实验的控制与顺序 gate 未同时通过，不能识别训练阶段造成的语用能力变化。
- **E68：** Qwen8B/14B 格式控制接近满分，但只可证实受语境调制的渐变反应，未发现足以构成独立论文的新增结构。

**最终判断：** 仅保留有界的测量教训；不重开原项目，不因文学邻近又把它加回 workbench。
