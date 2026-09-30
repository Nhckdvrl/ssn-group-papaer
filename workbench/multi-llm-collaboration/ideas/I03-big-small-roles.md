# I03：异构大+小团队中的 collaborative role utility（2026-10-01）

- **状态：** PARKED
- **重开条件：** 至少一个 open-weight 异构 team（不同尺寸或家族）按官方/强 baseline 正常训练并达到可解释性能；随后出现稳定 contribution / role anomaly，或 territory 的 R-family 被人审升为前两优先级。
- **来源：** Lazy Agents、Teams Hold Experts Back、heterogeneous team / weak–strong collaboration 等 lineage 表明 global model strength 不一定等于团队中的实际贡献。
- **研究动作：** 定位 + 反事实干预。

## 不预设的故事

不预注册：
> “大模型包办，小模型偷懒。”

Lazy-agent / expert-underuse 已经有强近邻。真正值得做的是：**异构性是否产生它们没有解释的 role-dependent utility / capability ordering inversion，以及什么条件决定这种结构。**

## 触发后先做的最小 measurement

对训练 checkpoint 做 member intervention：
- replace 某成员为其未训练版本；
- replace 为能力相近但未共同训练的模型；
- mask / bypass message；
- role swap（只有协议允许时）。

读数是下游团队 outcome，而不是只看消息数量或说话长度。

## 升格条件

只有出现：
1. 可重复、明显超出“强模型更强”的 trivial ordering；
2. 在至少一个 partner/task shift 下有 consequence；
3. 最近邻不能简单压缩为 Lazy Agents / expert-underuse；

才从 PARKED → PILOT/PROMISING。否则它只是 I01/I02 的辅助分析。
