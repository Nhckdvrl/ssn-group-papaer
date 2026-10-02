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
| R06 | candidate ranking / Plan-Real alignment 已有直接近邻，不能把 logger 本身当 novelty | Decision-Metric Alignment / DA-LeWM | E02 只作校准；只有新的 hidden variable + real regret consequence 才升级 |
| R07 | trajectory offset / same-trajectory supervision 会同时反映 behavior path 与 environment reachability | RC-aux 自限；TD-JEPA；QRL/quasimetric | E03/E04 固定 local transitions/support，直接操纵 behavior organization；不把 \(\Delta\) 叫 shortest path |
| R08 | goal distance、rollout horizon、replanning 与 candidate budget 可共同制造“模型失效” | Planning Limits；SAGE/IMWM | E02/E06 分层记录 goal distance；true-dynamics / candidate / subgoal oracle 分开 |
| R09 | 2026 方法使用不同 goal source、horizon、action block、planner budget，主表数字不可直接排名 | PAPER_LINEAGE / ASSETS | native reproduction 与 common audit 分表；转换到真实 env steps |
| R10 | 直接近邻仍高速更新，预印本版本/代码可能变化 | 2026-09 SALT/ATLAS/Planning Limits 等 | 每次 C##→L2/进 candidate 前重扫 arXiv/官方 repo；pin 用到的版本，不引用旧摘要冒充最新 |
| R11 | “cross-trajectory” 在实现中可能只是 cross-batch-row，不等于 original episode不同，更不等于 environment unreachable | TD-JEPA/RC-aux pinned code audit；stable-worldmodel clip sampler | E08恢复 episode/step provenance并做semantic audit；论文/代码术语分开 |
| R12 | false negatives 已被 TD-JEPA 原文承认，单纯发现它们没有 novelty | TD-JEPA Eq.6 限定；CGCIVL ICML 2025 | I06必须做 role reattribution + planning consequence + role-separated repair |
| R13 | oracle-filter negative 变好/变差都可能只是 negative count / gradient scale变化 | I06 experimental design | E09加 COUNT-MATCHED VALID 与预注册 repulsion control；报告 gradient/dispersion |
| R14 | H/K/scoring-index mismatch能制造巨大 apparent model failure | Hidden Failure Modes / LeWMRO | E02/E06记录H/K并跑prefix/running control，不能把protocol bug归因表示/动力学 |
| R15 | “same local transitions, only long episode factorization”对 pinned short-window objectives结构上不可见 | TD-JEPA/RC-aux source audit | I01 PARKED；E03/E04 pre-run VOID，避免GPU验证结构性null |

## 实测记录模板

`P## — 现象或成功模式 — 条件／量级 — E## + 结果文件 — 已排除的平凡解释 — 下一次最有区分力的比较`

文献压力地图以 [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md) 与 [POSITIONING](POSITIONING.md) 为当前 authority；第一轮 [系统调查](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md) 保留作来源索引。R## 仍不是实测 P##。
