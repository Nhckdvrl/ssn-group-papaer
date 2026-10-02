# E12 — Deterministic history vs belief under actionable aliasing

- **状态：** CONDITIONAL / requires E11
- **对应：** I07
- **问题：** E11确认的 actionable aliasing 中，point/history latent 何时失败，multi-hypothesis/belief representation是否提供真正的 planning增益？
- **第一轮方法族，不预设winner：**
  1. native deterministic LeWM/JEPA-WM；
  2. matched history/recurrent state；
  3. typed goal-comparable + dynamic state baseline（FIRM-like，如可复用官方实现则优先）；
  4. stochastic/belief baseline（先最简单可校准的 ensemble/distributional latent，不因“新颖”造复杂架构）。
- **任务轴：** aliasing strength × hidden-state persistence × observation recovery delay；最多两类 hidden factor。
- **读数：** candidate regret、uncertainty calibration、hidden-mode separation、closed-loop success/recovery；prediction/probe只作中间解释。
- **升级：** 若存在稳定 regime：history state足够 vs explicit belief必要，并可被可观察变量预测，再考虑新 method / planner rule。
- **最大 collision：** FIRM-WM / UWM-JEPA；任何方法必须说明比 state factorization 或 belief-prediction本身多出的 decision-level增量。
