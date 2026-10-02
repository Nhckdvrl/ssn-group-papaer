# E01：强基线数值复现 + candidate / oracle logging（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** C00；为 I01/I02/I03/I04 提供共同 substrate
- **问题（一句话）：** 能否在不改原生 protocol 的前提下复现至少一个 LeWM 正式任务，并把 planner candidate、真实执行、随机性和资源读数完整记录下来？
- **设置：** E00 通过后执行。优先 LeWM 原生 TwoRoom + 一个 contact-rich task（PushT 或 Cube）；代码/数据/checkpoint 版本见 `ASSETS.md`。先官方 checkpoint 原生评测，再 1 次从头训练；正式方差实验另立卡。候选 logger 只旁路记录，不改变 planner 选择。
- **读数：** 官方 success/task-native metric；checkpoint load keys；candidate 数/iteration；selected action；planner/model calls；episode wall-clock；peak VRAM；data wait；train step/s；候选 action/score hash；可重放 episode 的真实 terminal task cost。
- **阳性对照：** 关闭 logger 后与打开 logger 后，在相同 checkpoint + env/planner seed 下 selected actions / success 应一致（允许明确记录的浮点 tie）；官方 checkpoint 结果应落入作者公开 protocol 的合理范围，若不能则先定位 protocol drift。
- **噪声地板 + MIE：** 相同 checkpoint、相同 seed 重放若干 episode，量化 renderer/env nondeterminism 与 logger overhead；正式 success MIE 不在 smoke 阶段拍脑袋设，先由重复波动与作者 reported variation 决定。
- **混杂审计：**
  - 模型版本：固定 commit/checkpoint hash；
  - 数据：固定 revision/episode manifest；
  - planner：原生 samples/iters/horizon/action units；
  - 随机性：train/eval/planner/env seed 分开；
  - logger：旁路、不得回写 planner；
  - 硬件：不同 GPU 不合并 wall-clock；
  - 评测：官方 goal source / success checker 不改。
- **决策表（跑之前写）：** 原生 parity + logger 无行为影响 → 建 E02 公共 decision audit；原生结果不对 → 先定位 config/checkpoint/environment，不启动 novelty 实验；logger 改行为 → 修成旁路后重跑；restore/replay 不稳定 → 标记 oracle audit 限制并改用 reset+replay/可复现环境。
- **算力预算：** E00 实测速率后填写；先单 GPU，先 checkpoint evaluation，再有限训练；不得直接占满节点。　**实际：** 待运行

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：未运行
- 结果文件：待生成
- 按决策表执行了什么：待运行
- 主张变化：无
- POST-HOC 分析：无