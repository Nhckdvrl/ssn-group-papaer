# E18｜Utility-Gated Recovery：更新、反馈、重规划还是保持不动？

- **状态：** RUNNING；首轮fork ledger已写卡，等待授权空卡，不训练router。
- **对应：** I11 / R5。
- **来源：** S19–S20；这是第二波方法线。
- **阳性对照：** no-shift / in-distribution条件下HOLD应有竞争力；明显shift下至少一种干预应优于HOLD，否则recovery set本身无效。
- **噪声地板：** deployment start/state、shift instance、train seed、router split分开；同一fork使用common random numbers或尽量相同随机性。
- **决策表（跑之前写）：** utility router优于固定策略→扩task/shift；某固定策略统治→保留简化结论；fork labels噪声过大→增加重复或缩小intervention set；未来信息泄漏→作废该router。

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

### 2026-10-02 无训练fork pilot（运行前）

动机：E13在两任务远goal上的self-consistency refinement没有收益；E16固定bank的regret也未支持“排序修正”解释。下一步改变**反馈/重规划设计**，不再局部调selector。

复用E13 A2锁定的75-step goal anchors，各task前32个预定episode，不按失败或结果筛选。使用同released Fast checkpoint、β=0、native macro rollout(3×25steps)与CEM N300/K30/30，先规划完整75动作，执行共同25步prefix。fork点在step25；若此前已成功，完整保留并标无需干预。

同fork比较HOLD（原剩余50动作）、FEEDBACK（真实当前pixel替换预测state，重新规划2×25剩余动作，N300）、EXTRA-REPLAN（同feedback，N900）；三者不改参数，剩余environment budget均50。这是feedback+replan组合，不把差值单独归因observer correction；首轮不训练router、不称新颖feedback方法。追加一种对照 PREDICTED-REPLAN（用预测step25 latent重新规划N300，不使用真实当前pixel），分开搜索更新与真实反馈。

跨两个conditions：no-shift action gain1.0与共同prefix第10步起gain0.7（fork前已有可见作用）；PushT使用relative action接口才允许action gain，否则拒绝此shift。所有干预面对相同gain/同prefix commands；selector/features不可输入真实gain或future utility。每task32×2conditions×4continuations，环境最多约25,600steps+prefix重放controls；模型不训练，单GPU。

公共prefix在fresh reset/public setter后执行；各continuation用同reset seed+完整prefix replay恢复fork的完整**本次生成**physics memory，state/pixel一致性需控制。不能声称恢复原dataset完整memory。部署features：step25 prediction/observation latent residual、可见goal progress、初始elite margin；future utility与特权state只用于离线标签。对已成功prefix与所有失败均保留。

主读数：native success、剩余50步的native task distance/return、对HOLD的配对help/harm与episode bootstrap CI；condition/task分开。另报重规划calls/candidates和fork replay开销，GPU非独占则降级timing。native-cached cost需H1/H2/H3一致性控制；动作长度必须75=3×25、remaining50=2×25。若fixed FEEDBACK普遍更好，先沿固定策略发展；若compute/feedback只在部分state值得，再扩ledger/shift或utility controller。不能因为firstpilot无utility异质性而关闭R5。

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

2026-10-02首轮native cost正控因missing candidate axis在模型接口处停止，尚未执行fork/candidate银行；failure与源码留存。修复直接native scoring的显式candidate axis，保持全部seed/inputs/主读数，以s0-retry1重跑。该接口失败不是科学null，不覆盖原run。
