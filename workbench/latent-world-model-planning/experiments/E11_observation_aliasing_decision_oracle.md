# E11 — Observation aliasing must change a decision

- **状态：** PLANNED
- **对应：** I07 / M1
- **目的：** 在训练任何新方法前，验证 partial observability 是真实 planning problem，而不是 probe问题。
- **核心 intervention：** 寻找/构造同一或受控近似 RGB observation，但 hidden dynamic state 不同（首选 velocity/momentum；第二类可选 contact/friction/regime）。
- **oracle：** 从同一隐藏状态分别执行固定 candidate action set，得到 environment utility / success / regret；记录最优action是否随hidden state改变。
- **baseline diagnostics：** single-frame latent、native history/context latent、简单 frame-stack/recurrent baseline（若已有）；只在已有checkpoint可用时跑，不先开发新模型。
- **关键读数：** observation similarity、hidden-state distance、candidate utility vector、best-action flip rate、oracle regret from state aliasing、baseline selected-action regret。
- **阳性对照：** fully-observed/velocity-visible版本应显著降低 aliasing regret；随机隐藏变量若不影响dynamics不应制造action flip。
- **gate：**
  - action flip/regret 很小 → I07 park；
  - hidden state load-bearing，但短history完全消除 → 问题收敛到 history sufficiency，不直接做 belief method；
  - history后仍有 multi-hypothesis decision ambiguity → E12。
- **禁止：** 用 latent probe显著性代替 decision consequence。
