# I10 — Query placement × specialization–reuse frontier

- **Program:** R3 — specialization vs reuse
- **状态:** SEED
- **目的:** 不问“query conditioning有没有用”，而问 **query information放在哪一层，什么时候提高当前task决策效率，什么时候伤害对unseen query/planner的复用。**

## Mother question

同一 compact visual world-model stack 中，query/task information可以进入：

1. encoder / state representation
2. dynamics
3. planning metric / cost
4. proposal
5. verifier
6. action head

这些设计都已有先例。真正未闭合的是：

> **哪些 predictive distinctions 应保持 task/query-independent，哪些部分值得 specialization？**

## 直接近邻

- P38 What Must a WM Distinguish?：query/candidate/planner决定 sufficiency；joint query-conditioned model seen-task强，unseen objective优势缩小；modular query-guided proposal是一个答案。
- TC-WM：foundation semantics → compact task-centric physical latent，证明 representation-level specialization本身可以显著改善 planning。
- SR-WM：task-conditioned functional roles进入 state semantics，并直接驱动proposal/reranking/resampling。
- World Action Planner：VLM承担task reasoning/proposal、WM保physical outcome prediction，是 modular specialization/reuse 的系统实例。
- Value Equivalence / Goal-Aware Prediction：task-aware prediction可只保留decision-relevant信息。
- Task-Sufficient WMs：主动收集 task-relevant factors。
- WorldTest：general WM应支持 diverse environment-level queries。
- Grounded WM：language goal/query进入 planning representation。
- Physically Viable WM：physical abstraction依 query。

这些不是 kill；它们定义了 R3 的设计轴。

## First scientific seed

在同一 compact model / same data 下，控制 query injection：

- Q0: query-independent encoder+dynamics，query只进test-time cost；
- Q1: query进metric / verifier；
- Q2: query进proposal，dynamics保持 reusable；
- Q3: query进入 dynamics / representation（matched capacity）。

然后测：
- seen-query planning efficiency；
- unseen goal/reward/query；
- planner/candidate-generator change；
- same predicted trajectory 能否被新 query reuse；
- capacity matched 情况下的 in-query vs cross-query frontier。

## 升级条件

不是“Q2平均最好”。

需要至少一个：
- stable specialization–reuse frontier；
- query family complexity / capacity / candidate distribution 能预测最优 injection layer；
- modular design在 seen task几乎不损失，同时显著提高unseen reuse；
- query-dependent method ranking在 second task structure复现。

## 最大 compression

“P38已经做 query-conditioned vs modular。”

所以 exact delta 不能只是再复制 seen/unseen objective，也不能只是“task-conditioned representation更强”。必须在 **query placement × query complexity × capacity × planner reuse** 上形成可迁移 regime law，最好解释为什么 TC-WM/SR-WM/P38/WAP 这些不同设计在各自setting都合理。

## 对应实验
E17。
