# I01：RL 协同训练后的 cross-play landscape（2026-10-01）

- **状态：** SEED
- **角色：** G-family 的第一把行为测量尺；不是预注册的最终 RQ。
- **来源：** 近邻分歧——经典 MARL/ZSC 认为共同训练容易形成 partner-specific convention；prompted LLM collaboration 对陌生伙伴常较稳；SRPO 已在协作任务（含一个 LLM task）上直接指出 unseen-partner brittleness。
- **研究动作：** 引入成熟构念 + 系统测量（cross-play / ad-hoc teamwork）。

## Ownership 边界

**不能把“训练后换伙伴会掉点”本身写成我们的 novelty。** SRPO 已占这个宽 claim。I01 的价值在于建立主流 open-weight LLM multi-agent RL 的 cross-play landscape，并发现值得继续解释的条件、训练轨迹或例外。

最近邻：
| 近邻 | 已有 claim | 我们现在还不知道什么 |
|---|---|---|
| SRPO (2602.21515) | 普通 collaborative policies 对新伙伴脆弱；strategic risk aversion 改善 unseen-partner collaboration；含初步 LLM task | 主流 LLM RL 框架在 seed / size / family / training stage 等 partner shift 上的系统 landscape |
| ZSC / Other-Play / FCP | 传统 MARL 中 convention 与 partner generalization 的经典问题 | 语言模型预训练是否改变这些规律、在哪些任务改变 |
| prompted LLM coordination / Hanabi | 未共同训练的 LLM 对陌生伙伴可表现出一定鲁棒性 | RL co-training 后这种性质如何变化 |

## 最便宜的 pilot

复用 E01 的两个独立训练 team A/B：
- diagonal：S_A+V_A、S_B+V_B；
- off-diagonal：S_A+V_B、S_B+V_A；
- 保存多个 checkpoint 的同一矩阵；
- 未训练 team 作为 reference；
- **阳性对照**：人为引入 team-specific convention，确认 cross-play measurement 能测出兼容性下降。

Dr. MAS math 的 Solver→Verifier 角色语义非常固定，因此它只是 smoke test。这个环境 cross-play≈self-play **不能**否定 G-family；下一步必须转到更需要真实 coordination / multiple conventions / distributed information 的公开任务。

## 决策所需读数

- self-play 与 cross-play performance；
- partner directionality；
- checkpoint trajectory；
- CI / 重复评测波动；
- MIE：在跑 pilot 前写清多大差异才值得进入第 3 seed / 更强 coordination task；约 2×重复波动只作 heuristic。

## 分支

- **稳定且明显的 off-diagonal degradation** → 加第 3 seed；做 checkpoint trajectory 与受控 partner shift，定位“在哪种 shift / 训练阶段形成”；先更新 positioning，不直接宣布新 finding。
- **math 接近 0** → 转到真正 coordination substrate；不升级 claim。
- **cross-play > self-play 或强方向性反转** → 优先审计 role alignment / harness；若控制后仍在，作为 measurement anomaly 新建 idea。
- **只有 SRPO 已知模式、无新 structure/consequence** → I01 仍作为论文公平性/可靠性 measurement，主故事从其他 pain 生长。

## Information gain

无论结果方向，I01 都应该改变我们对下一步 substrate / partner axis / mechanism 的选择；**不要求正反两边都能单独写成论文。**

- **排序：** 最高优先级（E01 复现后立刻跑）。
