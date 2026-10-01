# 痛点与成功日志

更新：2026-10-02。**尚未本地运行，当前没有实测 P##。** 后续同时记录失败、不稳定、慢、读数不一致，以及强基线意外地成功；每条需要运行条件、粗略量级、关联实验卡／文件和替代解释。

## 待核对风险（R 前缀，不是实测痛点）

| ID | 来源已核对的风险 | 证据 | 执行时的处理 |
|---|---|---|---|
| R01 | LeWM 原生 API／默认配置与当前 SWM 接口并非自动兼容 | ASSETS §1/§3 的固定代码快照 | 原生复现与公共协议适配分开；保存 resolved config |
| R02 | 参数少不意味着图像数据和评测便宜 | SWM 官方存储 benchmark；RC-aux timing 定义 | E00 测 I/O、完整 episode、显存，而非按参数量推测 |
| R03 | 官方几何 baseline 有已公开的修正结果 | Temporal Straightening UPDATES | 标明论文版／修正版；不用弱旧配置制造增益 |
| R04 | reachability／consistency／anchor regret 的语义与环境真实量不同 | 调查 P04/P09/P10/P12/P13 | 保存变量定义；需要实环境验证时先核对 reset/replay |
| R05 | “多 seed”容易把训练、环境与规划随机性混在一起 | RC-aux、SALT 的具体评测协议 | train_seed / eval_seed / planner_seed 分字段 |

## 实测记录模板

`P## — 现象或成功模式 — 条件／量级 — E## + 结果文件 — 已排除的平凡解释 — 下一次最有区分力的比较`

文献压力地图见 [系统调查 §4](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md)。它用于扩展探索，不要求 agent 逐条证明为真。
