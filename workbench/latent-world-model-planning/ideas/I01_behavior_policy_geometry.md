# I01：Trajectory-factorization / route imprinting（2026-10-02）

- **状态：** PARKED
- **原始来源：** RC-aux / TD-JEPA 的 trajectory-derived supervision 与 quasimetric GCRL 的 behavior-vs-optimal tension。
- **为什么降级：** 第二轮**代码级审计改变了识别判断**。当前 pinned TD-JEPA 与 RC-aux 都只在短 training clip/window 内构造主要 same-trajectory temporal supervision；TD-JEPA canonical 为 history 3 + num_preds 5，即 loaded window 长度 8，RC-aux 同样自动扩到短 horizon。更关键的是，两者 cross negative 都直接对 **batch rows 做 permutation**，loss 并不读取 episode identity/connectivity。因此，如果 E03 强行要求 raw transitions + full one-step/history windows 完全相同，而只改更长的 episode factorization，当前实现的主要 loss 在数学上几乎看不到这个 intervention；得到 null 是结构上预期的，不是有信息增益的科学结果。
- **研究动作结论：** 不再把“same local windows，只改 long trajectory factorization”当第一优先 experiment。E03/E04 对应计划作废，保留为过程证据。

## 仍可能重开的更窄问题

若后续遇到真正读取 full-trajectory/path structure 的方法（例如 Traj-LeWM 或 future long-pair objective），或者我们有一个 clean intervention 能在**保持 local transition statistics matched、但真实改变该方法实际读取的 pair distribution**时，才重开 route/factorization invariance。

届时必须：
1. 明确 intervention 进入了方法真实 loss；
2. 不是普通 dataset quality / behavior-policy shift；
3. 至少有 trajectory-supervised vs local-geometry controls；
4. 连接 fixed-candidate decision / closed-loop consequence；
5. 与 ICML 2026 Behavior-Invariant Task Representation、QRL/CGCIVL、Temporal Straightening 区分。

## 从 I01 学到的更重要线索

代码审计反而暴露了一个更强的问题：

> TD-JEPA / RC-aux 把随机 cross-batch/cross-trajectory pairs 当作 far / unreachable negatives，但 sampler 并不验证 environment reachability；TD-JEPA 原文甚至明确承认 reachable false negatives，而 ablation 又显示这些 negatives 对 planning 有贡献。

这产生了 **I06 Semantic Negatives or Geometric Repulsion?**，现在是第一优先 mining lane。

- **证据：** source/code audit，非 GPU result。
- **重开条件：** 真实 full-trajectory supervision方法成为主对象，或 I06 结果显示 route/factorization（而非 negative semantics）才是 load-bearing因素。