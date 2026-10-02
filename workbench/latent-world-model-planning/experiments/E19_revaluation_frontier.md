# E19 — Revaluation frontier pilot

- **状态:** PLANNED / R2 secondary seed
- **对应:** I13 / R2
- **目标:** 测 modern predictive objects 在 reward/goal vs localized transition revaluation 下，需要多少 recomputation / adaptation 才恢复决策质量。

## Substrate

首选 topology/navigation 环境，要求：
- 可固定 start/goal；
- 可局部改 connectivity/obstacle；
- 可 reset/replay；
- 真实 shortest path / task utility可算。

TwoRoom若能稳定控制 door geometry可优先；否则 OGBench PointMaze / AntMaze。

## Methods — first wave

只取 2–3 个：
1. explicit LeWM/JEPA-WM；
2. Bagatella TD-JEPA / successor-like implicit；
3. 一个中间/hybrid方法仅在前两者显示清楚差异后加入。

## Change types

### R0 — reward/goal revaluation
dynamics不变：
- same state graph；
- new goal / reward。

### R1 — localized transition revaluation
只改一个局部 transition structure：
- close/open one door；
- obstacle relocation；
- local action-effect perturbation。

记录 change locality / affected-state set。

### R2 — optional broader dynamics shift
只有 R1有稳定结果后加。

## Evidence budget after change

统一提供：
- B0: zero new transition；
- B1: tiny local evidence；
- B2: matched small update set。

对每个method记录：
- 是否需要 gradient update；
- update samples；
- update wall-clock；
- test-time planning compute；
- task/reward inference data。

## Measurements

- immediate post-change candidate regret；
- closed-loop success；
- adaptation sample efficiency；
- prediction / successor / occupancy error by graph-distance from changed region；
- stale-policy / stale-occupancy propagation；
- recomputation footprint；
- total train+adapt+deployment compute。

## Decisive analysis

核心不是平均分，而是：

[
	ext{distance from changed transition}
ightarrow
	ext{error / policy recovery curve}
]

以及：

[
	ext{change locality}
	imes
	ext{predictive object}
ightarrow
	ext{adaptation / recomputation cost}
]

如果 successor-like representation在远处也需要全局修正，而 explicit local dynamics的影响更局部，必须量化而不是靠直觉。

## Controls

- task-information budget分开；
- same post-change evidence budget；
- same success checker；
- native protocol + common audit分表；
- zero-shot vs adapted明确区分；
- 不把“一个方法根本没暴露update API”当科学结论；
- 如果method理论上应full retrain，记录其 structural limitation但不要做不公平wall-clock排名。

## Gate

- 只有 reward-vs-transition已知经典差异 → 不升级；
- 出现 spatial/locality-dependent recomputation law → 升；
- hybrid能用局部 explicit update修复 stale implicit tail → 方法候选；
- second topology/contact task确认后才大铺。

## 结果
未运行。
