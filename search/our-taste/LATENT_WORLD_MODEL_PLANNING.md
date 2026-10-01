# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：**PROPOSED / literature-hardened / execution-ready，不替换现有 ACTIVE 线，不是 candidate。**

工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)；资源：[RESOURCES](../../RESOURCES.md)。  
领域 authority：[PAPER_LINEAGE](../../workbench/latent-world-model-planning/PAPER_LINEAGE.md) · [PROBLEM_METHOD_MAP](../../workbench/latent-world-model-planning/PROBLEM_METHOD_MAP.md) · [POSITIONING](../../workbench/latent-world-model-planning/POSITIONING.md)。

## 1. 为什么保留这个 territory

不是因为“没人做”——恰恰是一个很活跃、已经有 ICML/NeurIPS/ICLR precedent 的谱系。保留原因是：

1. 母问题足够大：什么 representation / dynamics / planning interface 才真正支持 decision，不是小 benchmark bug；
2. 直接近邻给出**不同甚至竞争的解释**：geometry、reachability、recursive propagation、proposal/search、temporal abstraction、data structure；
3. 小型开源模型、offline data、可重置 simulator 和 candidate-level planner 内部使强 identification 成为可能；
4. 单个训练/评测大多可独立单卡，正适配“卡多、弱互联/弱 I/O”的资源结构；
5. 一套共享 harness 可连续换研究问题，不需要每个 lead 从头搭系统。

## 2. 第二轮 hardening 后的红区

以下不能再当 headline：prediction≠planning；latent L2≠progress；finite-horizon reachability；generic multi-step；inverse dynamics/action consistency；generic learned proposal/subgoal/hierarchy；long-horizon failure；generic OOD robustness；decision-centric evaluation。

它们全部作为 baseline/diagnostic。claim ownership 见 POSITIONING。

## 3. 当前矿层

**I01 / R-A（第一优先）：behavior-policy geometry contamination。**  
直接来源于 trajectory-supervised planning objective（RC-aux/TD-JEPA）与 offline GCRL quasimetric 对 behavior-statistics vs optimal-distance 的张力。要求在 environment/local transitions/one-step samples 被控制时只改变 behavior path/episode organization，并连接 learned geometry → candidate ordering → environment decision。不是普通 data ablation。

**I02 / R-B：optimizer-induced support drift。**  
只有 `CEM iteration → support drift → model optimism → false elite → real regret` 的链在强 controls 后成立，才超过经典 offline model exploitation。

**I03 / R-C：bottleneck relocation。**  
只有 goal distance / candidate margin / support 等少数变量能跨任务预测 representation/dynamics/proposal/horizon ceiling，并预测 intervention ranking，才超过普通 method benchmark。

I04 是 DA-LeWM alignment replication；I05 history/POMDP 已 PARK。

## 4. 现成执行程序

```text
E00 resource/native smoke
→ E01 baseline parity + logger + replay/oracle
→ E02 decision-audit calibration
   ├─ E03→E04 I01
   ├─ E05     I02
   └─ E06→E07 I03
```

实验卡、阳性对照、MIE、混杂和 stop/go 条件均已登记：[EXPERIMENT_PROGRAM](../../workbench/latent-world-model-planning/EXPERIMENT_PROGRAM.md)。

## 5. 顶会尺度标准

可升级的结果必须至少形成：新 distinction / 新 failure law or regime / 由机制推出的 minimal intervention / validated identification protocol 之一，并最终有真实 planning consequence。只换 benchmark、更多 seed、普通 correlation、一个小 loss 涨点都不够。

本 workbench 的目标会议仍是 ICLR / ICML / NeurIPS；视觉贡献足够时 CVPR。具体 manuscript 主旨要由本地实验长出来，不提前锁题。

## 6. 容量

保持 PROPOSED。用户给本地 agent 分配本 workbench 时，agent 按 [LOCAL_AGENT_PROMPT](../../workbench/latent-world-model-planning/LOCAL_AGENT_PROMPT.md) 自主执行；是否改为 ACTIVE 仍按全局规则由人决定。