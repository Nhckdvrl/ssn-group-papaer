# 主张账本（CLAIMS）

证据等级见 `../EXECUTION.md`。当前没有成立的 scientific claim；baseline reproduction 不自动升级为 claim。

| ID | 主张（一句话，可证伪） | 等级 | 证据（实验卡 E##、结果文件） | 已知威胁 / 未控制混杂 | 最近更新 | 校对 |
|---|---|---|---|---|---|---|
| C01 | 在 10 个独立训练的 Pythia-70M（PolyPythias）中，induction 行为由同一因果角色结构实现：单一 previous-token 瓶颈头 + 依赖它的 induction 头（K-composition）；头身份不可复现，层位置 8/10 可复现，相对层序 10/10 可复现 | L1（10 seed × 12 post-emergence checkpoint；单一任务、单一尺寸） | E02；`results/e02/summary.json` | 只在 70M、只在重复随机序列上；角色阈值（S_prev ≥0.5、S_ind ≥0.2）为预注册选择；未做 zero 消融的角色级复核 | 2026-10-02 | 未校对 |

## 作废 / 降级记录

暂无。
