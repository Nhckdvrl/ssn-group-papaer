# I04：共同训练消息的 functional portability（2026-10-01）

- **状态：** PARKED
- **重开条件：** I01 出现稳定 cross-play signal，或 PAIN_LOG 出现明确 message-level incompatibility / private-convention 迹象。
- **来源：** emergent convention / language lineage 与 partner-generalization pressure。
- **研究动作：** 反事实 transplant + functional evaluation。

## 核心修正

不再把“新伙伴读不读得懂文本”作为主要 capability measure。probe/human-readable 可能与 downstream usability 解耦。

需要分两层：

1. **semantic recovery**：receiver 能否恢复 message 中 task-relevant state；
2. **functional transfer（主读数）**：把同一条 message/state transplant 给新 receiver 后，它能否继续完成任务、提高下游 outcome。

有趣的情况反而可能是：
- 文本看起来完全可读，但 functional transfer 差；
- 文本表面很压缩/私有，却能跨模型有效使用。

## 最近邻边界

GlossoGen / When LLMs Develop Languages 已占“训练中形成语言/约定”的宽故事；C2C/LatentMAS 等占不同通信媒介。我们只有在 portability 与 team reliability 形成 load-bearing link 时才值得继续。

## Pilot（触发后）

固定同一 task state，把训练前后 sender message 交给：
- 原配 receiver；
- 同尺寸未共同训练 receiver；
- 另一 family receiver。

同时测 semantic recovery 与 downstream completion/change in reward。人为删去关键 task state 作为阳性对照。

## 分支

- semantic recovery≈高、functional transfer 明显差 → 很强的“理解不等于可继续使用”measurement anomaly；
- 两者都差 → private convention 候选，但需排除简单信息缺失；
- 两者都稳 → PARKED，不继续 fishing；
- 只有 surface statistics 漂移 → 不升级 claim。
