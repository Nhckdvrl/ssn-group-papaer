# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：**PROPOSED / literature+code-hardened / execution-ready；不是 candidate。**

工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)；资源：[RESOURCES](../../RESOURCES.md)。  
领域 authority：[PAPER_LINEAGE](../../workbench/latent-world-model-planning/PAPER_LINEAGE.md) · [LITERATURE_LEDGER](../../workbench/latent-world-model-planning/LITERATURE_LEDGER.md) · [PROBLEM_METHOD_MAP](../../workbench/latent-world-model-planning/PROBLEM_METHOD_MAP.md) · [POSITIONING](../../workbench/latent-world-model-planning/POSITIONING.md)。

## 1. 为什么保留

这是一个**活跃且已有顶会 precedent**的 territory，不是空白。保留原因：

1. 母问题够大：world model 为 decision 到底需要什么 representation / dynamics / planning semantics？
2. 2026 直接近邻给出不同承重点：geometry、reachability、recursive dynamics、counterfactual action effect、proposal/search、temporal interface、data semantics；
3. compact models + offline data + resettable simulator + candidate-level access，使受控 identification 成本远低于大型视频 WM；
4. 多独立 GPU 正适合 paired variants、train seeds、candidate audit、oracle replacement；
5. literature/code audit已经能淘汰错误实验，而不是见空白就跑。

## 2. 红区

不能再当 headline：
prediction≠planning；L2≠progress；representation有信息但objective不会用；generic reachability/temporal distance；generic multi-step；inverse/physical grounding；action discrimination；path-aware cost；CEM OOD/model exploitation；proposal/subgoal/hierarchy；long-horizon；closed-loop evaluation。

## 3. 当前第一矿层：I06 semantic negatives vs geometric regularization

TD-JEPA 把 cross-trajectory/batch goals作为 temporal-distance hinge negatives，**原文明确承认 reachable false negatives**，但 component ablation又显示去掉 hinge伤 planning。RC-aux也用 batch-permuted goals作 reachability 0-label，而同轨迹 temporal hard negatives已经负责 budget identifiability。CGCIVL (ICML 2025) 则明确指出 trajectory identity不能直接判 connected/unconnected。

因此真正的问题是：

> **plan-aware WM 的 heuristic cross-trajectory negatives 到底在教正确的 reachability/distance semantics，还是主要提供 global separation / scale / dispersion regularization？**

执行：
- E08：零训练 semantic audit；
- E09：FULL / no-negative / oracle-valid / count-matched / repulsion decomposition；
- E10：只有机制成立才做 oracle-free role separation。

这不是 generic false-negative paper；必须有 real planning consequence 和跨objective证据。

## 4. 第二矿层：I03 bottleneck regime law

用 oracle ladder拆 metric/representation、dynamics、action discrimination、search、H/K scoring interface、horizon/target。

只有 goal distance / candidate margin / planner-reachable fidelity / H-K ratio 等少数变量能**跨task预测 bottleneck与 intervention ranking**，才超过普通 benchmark。

## 5. 已降级

- I01 trajectory-factorization：PARKED。代码审计发现 pinned TD-JEPA/RC-aux 主要 temporal loss只看短 loaded windows；保持这些 windows不变只改长episode factorization，treatment结构上不可见。E03/E04 pre-run VOID。
- I02 support drift：PARKED；P40 + offline MBRL 已强占 broad story。
- I05 POMDP：PARKED。
- I04：E02 calibration only。

## 6. 执行程序

```text
E00 smoke
  ↓
dataset readable ─────→ E08 semantic-negative audit
  ↓
E01 baseline + logger + replay
  ↓
E02 decision calibration
  ├─ E09 → conditional E10    I06
  └─ E06 → conditional E07    I03

E03/E04 VOID
E05 conditional diagnostic only
```

详情见 [EXPERIMENT_PROGRAM](../../workbench/latent-world-model-planning/EXPERIMENT_PROGRAM.md) 与 [LOCAL_AGENT_PROMPT](../../workbench/latent-world-model-planning/LOCAL_AGENT_PROMPT.md)。

## 7. 顶会尺度标准

可升级结果至少形成一种：
- new distinction 且对decision load-bearing；
- new failure law/regime；
- mechanism-derived minimal intervention；
- validated identification protocol that changes method design。

更多seed、普通correlation、单个toy、一个小loss涨点都不够。

## 8. 容量

保持 PROPOSED；不替换现有 ACTIVE 线。用户把本 workbench 分配给本地 agent 后，可按卡片自主推进；状态变化仍由人决定。