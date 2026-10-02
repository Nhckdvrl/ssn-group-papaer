# E18｜Utility-Gated Recovery：更新、反馈、重规划还是保持不动？

- **状态：** PLANNED；未运行。
- **对应：** I11 / R5。
- **来源：** S19–S20；这是第二波方法线。
- **阳性对照：** no-shift / in-distribution条件下HOLD应有竞争力；明显shift下至少一种干预应优于HOLD，否则recovery set本身无效。
- **噪声地板：** deployment start/state、shift instance、train seed、router split分开；同一fork使用common random numbers或尽量相同随机性。
- **决策表：** utility router优于固定策略→扩task/shift；某固定策略统治→保留简化结论；fork labels噪声过大→增加重复或缩小intervention set；未来信息泄漏→作废该router。

## 核心问题

world model出现异常时，哪种intervention真的提高未来closed-loop utility，而不只是降低instant prediction error？

## Stage 0｜Fork ledger

在可重置环境选择预注册decision points。对同一个model checkpoint与environment state建立matched continuations：

- `HOLD`：不更新，按原planner继续；
- `FEEDBACK`：只更新latent feedback / observer state，不改参数；
- `SHORT-UPDATE`：用最近真实transition做1–K步轻量梯度更新；
- `EXTRA-REPLAN`：不改模型，只增加candidate/horizon/replanning compute；
- `FALLBACK`：若已有简单policy/short-horizon controller则加入。

每个fork记录未来H_eval steps / episode return / success / failure，并计算相对HOLD的 `ΔU`。

第一轮只需HOLD + 2种最容易实现干预，不要求全五类。

## Router features：只允许部署时可见

候选：
- recent prediction residual；
- ensemble / bootstrap disagreement；
- CEM elite margin；
- candidate rank instability；
- goal progress / stagnation counter；
- support/OOD proxy；
- previous intervention response；
- remaining compute / interaction budget。

禁止：
- fork未来return；
- privileged hidden state；
- “哪种干预后来最好”的真实标签直接在线输入。

## Baselines

1. ALWAYS-HOLD；
2. ALWAYS-FEEDBACK；
3. ALWAYS-UPDATE；
4. ERROR-THRESHOLD；
5. CHANGEPOINT detector（适用时）；
6. ORACLE-FORK（只作上界）；
7. learned / rule-based utility router。

## 训练方式

先把fork ledger当监督集：
- binary：best intervention vs hold；
- 或multi-class：HOLD/FEEDBACK/UPDATE/REPLAN；
- 或直接回归每种intervention的 `ΔU`。

第一版优先浅层模型，避免router本身成为主要算力/容量来源。

## 主读数

- closed-loop success / task cost；
- intervention count；
- extra model calls / gradient steps / wall-clock；
- real-environment extra transitions；
- utility gain per intervention；
- false-positive update cost：本来HOLD更好却触发干预；
- false-negative cost：需要干预却没触发。

## 确认范围

至少包含：
- no-shift ID；
- 一个dynamics shift（friction/action scale/layout等）；
- 一个model-error/stagnation自然失败子集。

如果router只在人工shift有效、自然失败不泛化，就明确限制，不包装成通用trust mechanism。

## 最近邻压力

- Feedback WM已经证明feedback-state correction有价值；
- WorldAgen / AdaJEPA类工作已做test-time update；
- CAWM做shift detection + replay forgetting；
- Counterfactual Utility Protocol已经证明“update本身可能伤return”，并提供update-vs-hold fork measurement。

因此E18的潜在新点是**从fork utility学习intervention selection**，而不是再证明某一种adaptation有用。

## 结果
未运行。
