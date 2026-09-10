# L12 研究脉络与 Claim-Experiment Map

**用途：** 组内共享、讨论、接手实验和统一叙事。它不是论文正文，也不是新的 preregistration；正式数值、判定规则和复现入口仍以 `EXPERIMENTS.md`、`CLAIMS.md`、`PILOT_REPORT.md` 和各实验目录为准。

**更新：** 2026-09-10

## 一页版

### 我们现在到底在问什么

> 为什么 reasoning-oriented computation 会让模型对一些 presentation changes 近乎 invariant，却对另一些变化保持强烈 sensitivity？这种变化是否来自决策控制权从 prompt surface 转向自生成 reasoning trajectory，以及 trajectory 构造出的 pre-answer decision state？

当前最简洁的答案是：

> **Reasoning reallocates sensitivity from form to evidence.**

更完整地说：自然 reasoning trajectory 会在显式结论出现前逐步形成 decision direction，并把它凝结为一个能因果携带 choice 的 pre-answer state。Reasoning regime 下，最终答案更受这条 evidence-bearing trajectory/state 控制，更少受 prompt 的表面形式控制。这不是普遍“变钝”：当证据不变而形式变化时，模型更 invariant；当证据真正变化时，模型反而更敏感。

### 当前 paper identity

暂定标题：

> **Reasoning Changes What Models Are Sensitive To**
>
> *Causal Decision Control Shifts from Presentation Form to Evidence*

一句 reviewer 可以复述的话：

> Reasoning models do not simply become insensitive to presentation; reasoning shifts causal decision control toward a trajectory-built state that discounts form while tracking evidence.

直观说法“reasoning ignores the wrapper, not the evidence”很好记，但不能写成绝对事实：E21 中 form effect 仍非零，我们支持的是**比较意义上的 selective sensitivity**，不是 form information 被彻底删除。

### 最终只保留三个 major claims

| Claim | 通俗表达 | 决定性实验 | 角色 |
|---|---|---|---|
| **C1：Decision construction and consolidation** | 决策不是等到最后一句才突然出现；trajectory 逐步形成方向，并写入 pre-answer state。 | E07、E08、E11、E19 | 解释 decision 怎样在 reasoning 中形成 |
| **C2：Causal-control reallocation** | reasoning regime 的答案控制权从 prompt presentation 转向 self-generated trajectory/state。 | E09、E10、E12、E13；E17/E18 natural breadth | 把内部过程和 behavioral transition 接起来 |
| **C3：Selective sensitivity** | 新 controller 不是对一切都不敏感；它降低 form sensitivity，同时保持或增强 evidence sensitivity。 | E20、E20-C、E21、E22 | 全文皇冠，也是 E18 反例带来的 reconceptualization |

其余 checkpoint、probe、layer、模型结果全部是 support、triangulation 或 boundary，不再横向制造 C4/C5/C6。

---

## 1. 起点：parent phenomenon 和最初 competing accounts

### Parent 已经拥有什么

直接 parent 是 ACL 2026 Outstanding Paper [*Mind the (DH) Gap!*](https://aclanthology.org/2026.acl-long.479/)。它已经建立：

- reasoning 与 conversational models 在 risky choice 上存在系统性差异；
- description/history、gain/loss、option order 等 presentation 会改变选择；
- reasoning models 整体更接近 expected-payoff behavior，也更 presentation-invariant；
- mathematical reasoning training 是重要 differentiator。

因此下面这些不是我们的 claim：

- “reasoning models 更 rational / 更少 bias”；
- “reasoning models 在 risky choice 上更 invariant”；
- “description-experience gap 存在”；
- “gain/loss framing 会影响 LLM”。

### 最初真正的问题

Parent 告诉我们发生了什么，但没有解释：

> reasoning-oriented post-training 为什么会产生 behavioral invariance？

最初有四组合理 account：

1. **Representational canonicalization**：不同 presentation 被映射成相似的 payoff/probability/action representation，表面 framing 在 task-relevant computation 中被消掉。
2. **Policy/readout override**：frame information 仍存在，但一个更强的 EV/math decision policy 不再让它支配 final action。
3. **Inference-time deliberation**：不是 static weights 直接 canonicalize，而是模型生成 trajectory 后重新计算问题，覆盖较早的 presentation effect。
4. **Arithmetic specialization/boundary**：所谓 invariance 只在容易 arithmeticize 的 gamble 上成立，并非一般 contextual invariance。

现在的答案没有机械地选 A/B/C 之一。实验逐步显示：frame 没有全局消失；trajectory 承担 evidence integration；它建立的 late state 携带 decision；最终形成的是一种**选择性 canonicalization + trajectory-mediated policy control**。

### Checkpoint identification 从一开始就要说准

OLMo 对比是共同 base `allenai/Olmo-3-7B` 出发的两个 sibling SFT branches：

```text
Olmo-3-7B
├── Olmo-3-7B-Instruct-SFT
└── Olmo-3-7B-Think-SFT
```

不能写成 `Instruct-SFT -> continued training -> Think-SFT`。OLMo 能支持的是 matched common-base training-regime association，不是某一个孤立 optimization step 的严格因果归因。

---

## 2. 研究是怎样一步步转向的

## Stage 0：确认现象存在，但不把 parent 重做一遍

### E01 — 数据、stimulus、checkpoint audit

作用：确认 parent stimuli、prompt rendering、选项顺序、gold 和 checkpoint lineage。这里主要解决 provenance 与 identification，不承担新 claim。

### E02 — sibling branch behavioral substrate

在三个 parent prospects 上：

- OLMo Instruct-SFT frame consistency：**0.750**；
- OLMo Think-SFT：**0.992**。

早期汇报中出现过约 0.817 的另一聚合口径；当前 claim ledger 和最终 manuscript 统一使用 order-conditional consistency 的 **0.750 vs 0.992**。这不是我们的 novelty，只说明同家族中确实有值得解释的 transition。

### E03 — frame information 是否被“擦掉”

Early/middle prompt representations 中仍可线性恢复 frame identity。它削弱了最简单的 global erasure account，但只是一条 mechanism constraint：

- probe 能 decode，不代表模型用它决定答案；
- probe decode 不出，也不能证明 information 不存在；
- 因此 E03 永远不升级成 headline claim。

### E05/E06 — 从 full trajectory 因果效应找到 mechanism lead

完整自然 trajectory 的干预结果：

- own trajectory margin：**+9.34**；
- empty：**-0.08**；
- opposite-frame trajectory：**-9.07**。

短、answer-free arithmetic snippet 没有复制 full trajectory 的巨大效应。它排除了“只要塞一小段算术就行”的廉价解释，也告诉我们不要继续做五种 snippet、十种 truncation。

但是“reasoning trace 能改变 output”本身已经被 ACL 2026 [*Reasoning Traces Shape Outputs but Models Won't Say So*](https://aclanthology.org/2026.acl-long.1986/) 大规模覆盖。E05 的价值是把我们带向 trajectory takeover，不是独立 paper identity。

### Pivot 1

问题从：

> CoT 会不会影响答案？

推进为：

> 控制答案的信息是否分布在自然 reasoning process 中，而不是只有最后一句 explicit commitment？trajectory 最后是否建立了一个能携带 decision 的 internal state？

这一步的结构对齐 [*Racing Thoughts*](https://aclanthology.org/2025.naacl-long.155/)：明确 computational hypothesis，然后用相关/过程证据、因果干预和后果沿一条线推进，而不是堆解释性工具。

---

## Stage 1：从 trajectory text 到 decision construction

### E07 — conclusion-stripped trajectory takeover

关键 contrasts：

- own stripped vs empty：**+2.624 [2.008, 2.988]**；
- own stripped vs opposite stripped：**+4.863 [3.469, 5.773]**；
- terminal portion 额外贡献：**+7.047 [6.746, 7.402]**。

支持的结论不是“最后一句不重要”，而是：

> 决策控制在显式 commitment 前已经形成，且 distributed construction 与 terminal amplification 同时存在。

如果只讲“去掉 conclusion 还有 effect”，会把 claim 缩成一个 prompt trick；正确 scientific object 是 progressive decision construction。

### E08 — pre-answer state substitution

用 matched opposite-decision donor，只替换内部 residual state，不加入 donor reasoning text：

- layer 0–13 近零；
- 14–16 开始上升；
- layer 17 首次让平均 target margin 翻向 donor；
- final donor-directed shift：**+5.090 [3.766, 5.977]**。

这把 E07 的文本效应推进为 internal carrier：trajectory 构造出的 pre-answer state 已经能够因果转移最终 choice。不能 claim “layer 17 就是 mechanism”；真正对象是持续出现的 late-state mediation profile。

### E11/E19 — state mechanism 的 breadth

- E11：18 个 preregistered controlled decisions，final shift **+4.868 [4.056, 5.813]**，18/18 正向；
- E19：48 个自然 CPC18 decisions，平均 shift 在 layer 18 首次翻转，final **+7.094 [5.914, 8.276]**，45/48 正向。

这两步让 C1 不再只是三个 prospects 的局部 feature。证据结构与 NAACL 2025 [*The LLM Language Network*](https://aclanthology.org/2025.naacl-long.544/) 的核心要求相似：representation/localization 必须通过 causal intervention 建立功能角色，并扩到足够的独立 units。

### Pivot 2

到这里仍然可能被 reviewer 压缩为：

> behavior 上 Think 更 invariant；MI 上 trajectory/state 能改 answer；两件事并排放着而已。

所以接下来必须建立 mechanism–phenomenon bridge：Think branch 是否真的比 Instruct branch 更依赖 trajectory-built computation？

---

## Stage 2：从内部载体到 causal-control reallocation

### E09 — prompt × trajectory factorial

把 matched prompt presentation 与 conclusion-stripped trajectory 正交交叉，分别估计 prompt control 和 trajectory control：

- Think trajectory control：**+0.586**；
- Instruct trajectory control：**+0.012**；
- branch-level trajectory-minus-prompt difference：**+0.569 [0.026, 1.062]**。

这不是“某个 injected text 有效”，而是第一次直接显示 sibling training regimes 的 causal-control architecture 不同。

### E10 — 36 independent decisions 上的 behavior–mechanism bridge

- behavioral branch difference：**+0.299 [0.239, 0.357]**；
- causal-control difference：**+0.399 [0.337, 0.464]**；
- 36/36 units 为正。

注意：跨 item 的 behavior-change 与 control-change correlation 为 **rho = -0.001, p = .997**。这条 exploratory bridge 已永久降级，不能换过滤条件或 metric 抢救。支持 C2 的是 matched regime-level transition 在独立 units 上共同出现，不是 per-item monotonic mediation。

### E12 — OLMo DPO checkpoint persistence

- DPO Think-minus-Instruct control difference：**+0.472 [0.401, 0.555]**，36/36 正向；
- 相比 frozen SFT difference 的增加：**+0.073 [0.016, 0.133]**，只作 secondary result。

它说明 route shift 沿后续 checkpoint 持续，不说明 DPO 创造了最初差异。

### E13 — Qwen3 same-weight mode axis

同一套 Qwen3-8B weights 的 thinking/non-thinking 官方模式：

- behavioral difference：**+0.836 [0.757, 0.911]**；
- causal-control difference：**+0.604 [0.550, 0.661]**。

这是很强的互补 identification：OLMo 比不同 sibling weights，Qwen 固定 weights 比 native reasoning route。但官方 mode 同时改变 channel/position，不能说是不可见的纯 mode switch，也不能把差异归因于“只多了 token”。

### E14/E15 — Llama ecosystem 外部验证

`DeepSeek-R1-Distill-Llama-8B` vs `Llama-3.1-8B-Instruct`：

- gain/loss behavior difference：**+0.947 [0.913, 0.976]**；
- control difference：**+0.067 [0.037, 0.099]**；
- DeepSeek final state shift：**+1.222 [0.299, 2.181]**。

这是 external replication，不是 clean training attribution。两者 post-training、data、tokenizer/config 不完全匹配，且 state effect 明显弱于 OLMo，不能 claim 跨家族有相同 layer geometry。

---

## Stage 3：natural breadth 先确认 route shift，也暴露旧故事的问题

### E16 — CPC18 corpus audit

从真实 human decision experiment 中冻结自然 risky-choice units：

- calibration split 210 个 problems 中 **151** 个通过预设 audit；
- exact EV gold，不用 LLM judge；
- history 来自真实人类观察序列。

独立 scientific unit 始终是 base decision，不是 generation、history realization 或 layer。

### E17 — calibration description/history breadth

151 个 calibration decisions：

- OLMo reasoning-minus-standard `Delta_R - Delta_P`：**+0.202 [0.162, 0.244]**；
- Qwen：**+0.163 [0.121, 0.205]**；
- behavior OLMo **+0.225**，Qwen **+0.276**。

这说明 trajectory-relative control 可以从 gain/loss 扩到自然 description/history。预注册 random-slope MixedLM 未收敛，不能用于 confirmation；所有 inference 由预先指定的 base-decision cluster bootstrap 承担。

外部 unmatched Llama/DeepSeek axis 在这里形成真实 boundary：control **+0.019 [-0.005, 0.043]**，behavior **-0.225**。Llama 的高 consistency 同时伴随 chance-level EV choice，提醒我们：**invariance 绝不等于 rationality**。

### E18 — untouched competition confirmation

预注册 commit：`9e4a532`。60 个 competition problems 中 44 个通过冻结规则：

- route-control primary gate：OLMo **+0.097 [0.002, 0.180]**，Qwen **+0.219 [0.152, 0.288]**；
- behavior：Qwen **+0.163 [0.051, 0.268]**；OLMo **-0.013 [-0.095, 0.065]**。

E18 没有简单 implementation bug：4-cell factorial、order mapping、parser、manifest/hash 和每题 row count 均通过 audit。它确认 C2，却打破了旧的 blanket story：

> trajectory control 变强，并不自动保证 description/history behavior invariant。

### E18P — 排除 Monte Carlo precision

固定同一 44 problems、prompt、parser、metric，只将每 cell generation 从 3 提到 20：

- OLMo：**-0.011 [-0.089, 0.067]**；
- Qwen：**+0.121 [0.026, 0.215]**。

所以 OLMo null 不是三次采样过粗造成的。这里没有为了保故事换 metric 或筛 problem。

### Pivot 3：真正改变全文概念的一次失败

E18 之后的 model-independent audit 发现，旧 description/history comparison 混入了一个额外变量：

- explicit condition 给 true generating distribution；
- 20-trial history 给 finite sampled evidence；
- finite sample 的 empirical EV ordering 可能与 true EV ordering 相反。

也就是说，我们把“同样证据换个 wrapper”和“证据本身变了”混在一起了。事后 history-agreement correlation 和 subgroup 数字只能生成 hypothesis，**绝不能作为 confirmatory claim**。

旧的弱结尾会是：

```text
reasoning -> trajectory takeover -> route shift does not guarantee invariance
```

新的 account-discrimination 问题是：

```text
reasoning -> trajectory/state control
          -> same evidence, different form: same decision state
          -> different evidence, matched form: different decision state
```

这不是为了显著性找 moderator，而是修复原 manipulation 的 construct validity：把 form 与 evidence 正交拆开。

---

## Stage 4：E20-E22 把反例变成 selective-sensitivity story

### E20 — prospective Form × Evidence decomposition

E20 使用 **137 个已经出现在 CPC18 splits 中的 base problems**（104 calibration + 33 competition），不是 137 个全新 problem。新的地方是：从大量未用于模型 scoring 的真实 histories 中，在看到这些 cells 的输出前冻结 selection、prompt、metric 和 scoring。

每个 problem 客观选两条强度匹配但 empirical evidence direction 相反的真实 history；每条 history 有两种严格 evidence-equivalent form：

1. raw 20-trial sequence；
2. 由同一 observation multiset 精确计算的 empirical frequency summary。

因此得到两个干净 contrasts：

- **改 form、固定 evidence**：raw vs empirical summary；
- **改 evidence、匹配 form**：empirical-A vs empirical-B history。

每 cell 10 generations；主要 inference 以 137 个 base decisions cluster bootstrap。Behavior 总计 **43,840 generations**。

#### Behavior 结果

| Axis | Form change | Evidence change | Selective shift |
|---|---:|---:|---:|
| OLMo Think vs Instruct | -0.341 [-0.364, -0.317] | +0.888 [0.865, 0.911] | **+1.229 [1.195, 1.262]** |
| Qwen thinking vs non-thinking | -0.266 [-0.291, -0.241] | +0.443 [0.397, 0.491] | **+0.709 [0.638, 0.778]** |

Qwen component directions 对 sharp assignment 稳健。OLMo Think valid rate 较低，因此必须更谨慎：joint selective effect 的 sharp bounds 仍为正 **[0.269, 1.289]**，但 form-only component 的 sharp upper bound 跨 0。故 OLMo 的无条件 central claim 是**联合 selective shift**；不能把 OLMo form decrease 单独写成无条件事实。

### E20-C — selective behavior 的 causal route

在 raw 和 summary form 内分别做 evidence prompt × trajectory factorial：

- OLMo `Delta_control` difference：raw **+0.459 [0.401, 0.518]**，summary **+0.584 [0.532, 0.638]**；
- Qwen：raw **+0.563 [0.506, 0.621]**，summary **+0.749 [0.689, 0.808]**；
- prompt-control differences 接近 0。

这一步很关键：C3 不是“Think 更会根据证据选答案”这一条 behavior observation；变化具体落在 evidence-bearing trajectory 的相对控制增强上。

### E21 — selective pre-answer state mediation

32 个按 effect quartile 分层抽取的 decisions，cross donor form/evidence，在 layers 0/8/16/24/31 substitution：

- final donor evidence effect：**+0.763 [0.694, 0.828]**，32/32 正向；
- final donor form effect：**+0.174 [0.124, 0.227]**；
- state selectivity：**+0.590 [0.476, 0.704]**，30/32 正向；
- evidence effect 在 layers 0/8 近零，16 开始形成，24/31 很强。

首轮 E21 把 reversed-order 条件中的 displayed A 当成 underlying A，坐标定义错误；该 run 被明确标为 invalid、完全排除。修正后先加 synthetic direction test，再完成 2,560-row rerun，execution audit PASS。不能把错误 run 和正确 run 混合。

E21 支持：选择性不只存在于输出或插入文本，而是写进 C1 已识别的同一个 late pre-answer carrier。它不支持“form erased”：form effect 仍显著，只是远弱于 evidence effect。

### E22 — external-family crown replication

在相同 137 decisions 上比较 Llama-Instruct 与 DeepSeek-R1-Distill；它是 unmatched external axis，只验证 computation pattern：

#### Behavior

- form：**-0.139 [-0.159, -0.119]**；
- evidence：**+0.857 [0.839, 0.876]**；
- selective shift：**+0.996 [0.962, 1.031]**，137/137 正向；
- joint sharp bound：**[0.621, 1.076]**。

#### Causal control

- raw trajectory-relative evidence control：**+0.175 [0.131, 0.221]**；
- summary：**+0.143 [0.106, 0.180]**；
- prompt-control differences：约 **+0.0046 / +0.0021**。

它使 C3 不再是 OLMo-specific curiosity，同时仍不能承担 one-variable training attribution。

### E18L — 20 vs 100 supporting diagnosis

- history empirical direction 与 true EV agreement：**0.750 -> 0.847**；
- 100-trial reasoning 经常超出 generation budget，valid history cells 只有 OLMo 0.332、Qwen 0.343；
- conditional finite subset 上 OLMo **+0.271 [0.176, 0.367]**，Qwen **-0.004 [-0.089, 0.083]**；
- sharp bounds 均跨 0。

结论：**inconclusive appendix audit**。不抢救、不作 claim。它只说明 history length 后果值得未来用不同生成预算或更短 protocol 研究。

---

## 3. 最终 claim 逐条拆解

## C1 — Decisions are progressively constructed and consolidated

### Claim

> Natural reasoning progressively constructs a decision before explicit commitment and consolidates it into a pre-answer causal state.

### 为什么值得知道

它区分了“最后一句 self-commitment 决定答案”和“reasoning process 已逐步形成 decision”两种真正不同的 computation，也把 natural language trajectory 与内部 causal carrier 接起来。

### Evidence chain

1. E05：own/opposite natural trajectories 强方向性控制，提供 lead；
2. E06：short arithmetic snippet 不能替代完整 process；
3. E07：stripped trajectory 在显式结论前已有方向性，terminal 再放大；
4. E08：opposite donor state 可在无 donor text 时转移 choice；
5. E11：18 controlled decisions preregistered replication；
6. E19：48 natural CPC18 decisions replication；
7. E15：DeepSeek 上较弱 external triangulation。

### 不能写过头

- 不能说 terminal commitment 不重要；
- 不能把 layer 17/18 当单点 mechanism；
- 不能说所有 verbalized step 都 faithful 或同等 causal；
- 不能说 state substitution 证明 natural indirect effect。

## C2 — Reasoning reallocates causal control

### Claim

> Reasoning-oriented computation reallocates final-decision control from prompt-level presentation toward self-generated reasoning and the state it builds.

### 为什么值得知道

它回答 reasoning post-training 改变的不是只有 accuracy 或输出风格，而是**答案形成的 causal architecture**。这也是把 C1 与 parent behavioral transition 变成同一个故事的桥。

### Evidence chain

1. E09：OLMo sibling prompt × trajectory factorial；
2. E10：36 independent gain/loss decisions 上 behavior 与 regime-level control transition 共现；
3. E12：OLMo DPO continuation persistence；
4. E13：Qwen same-weight thinking/non-thinking route；
5. E14：Llama ecosystem external text-level replication；
6. E17/E18：151 calibration + 44 untouched competition natural decisions；
7. E08/E11/E19：state 是 trajectory control 的 internal carrier。

### 不能写过头

- `Delta_control` 不是 formal natural mediation estimand；
- injection intervention 不证明每个自然生成 token 都同样 causal；
- 不能声称 isolated training algorithm causes the shift；
- per-item behavior/control correlation 是 null，不能复活；
- route reallocation 本身不等于 invariance 或 rationality。

## C3 — The reallocation is selectively evidence-sensitive

### Claim

> The reorganization suppresses sensitivity to representational form while preserving or amplifying sensitivity to decision-relevant evidence; the same selectivity is carried by the trajectory-built pre-answer state.

### 为什么是皇冠

它把 E18 的反例变成概念上的推进，而不是一个尴尬 boundary：reasoning 不是普遍不听输入，而是在改变“什么变化值得影响答案”。这是比 `trajectory takeover -> invariance` 更反直觉也更完整的结论。

### Evidence chain

1. E18：blanket description/history invariance 在 OLMo held-out 上失败；
2. E18P：排除 generation precision；
3. model-independent post-hoc audit：发现 form/evidence confound，仅生成 E20 hypothesis；
4. E20：前瞻性、正交的 form × evidence behavior test；
5. E20-C：变化主要来自 evidence-bearing trajectory control；
6. E21：同一 late state 中 evidence effect 远大于 form effect；
7. E22：外部 Llama ecosystem 的 behavior/control replication。

### 不能写过头

- 不能说 reasoning 完全 ignores form；
- 不能把 sampling error 本身说成我们的发现；
- 不能把 E18 事后 subgroup/correlation 当 confirmation；
- 不能从 risky choice 直接外推所有 domain；
- OLMo form-only unconditional claim 要受 invalid-response sharp bounds 限制。

---

## 4. 哪些结果不是 claim

| 结果 | 正确角色 | 不应写成 |
|---|---|---|
| Think-SFT 比 Instruct-SFT 更 invariant | behavioral substrate | 我们发现 reasoning model 更 rational |
| frame 可 decode | erasure account 的约束 | 模型 uses frame / frame causes choice |
| full trajectory 改答案 | mechanism lead | CoT causally affects output 是我们的 novelty |
| layer 17/18 出现 margin reversal | late-state profile 的 landmark | 某层就是 decision module |
| Qwen same-weight modes 复现 | route-level triangulation | 纯粹 thinking flag 的隐变量效应 |
| DPO checkpoints 复现 | persistence | DPO 导致最初 takeover |
| DeepSeek/Llama 复现 | external breadth | 严格 matched training causal comparison |
| finite history sampling error | construct audit / decision-science parent | 我们首次发现 description/history information 不等价 |
| 20 vs 100 history | inconclusive diagnostic | history 越长就一定恢复 invariance |

---

## 5. 失败、作废和被降级的路线

这些内容要保留，因为它们决定了现在的 story 不是结果挑选。

1. **Arithmetic snippet 没复制 full trajectory effect。** 它排除 cheap explanation，之后停止 snippet zoo。
2. **E10 per-item correlation 为空。** `rho=-0.001, p=.997`，永久降级；不通过换 metric 抢救。
3. **E17 MixedLM 不收敛。** 预注册 cluster bootstrap 继续承担 primary inference，MixedLM 只留 audit artifact。
4. **E18 OLMo held-out behavior 为 null。** 这是推动 form/evidence reconceptualization 的关键反例，不能藏。
5. **E18P 仍为 null。** 排除了“3 samples 太粗”这条方便解释。
6. **E21 first run 坐标错误。** 完全作废，修 test 后重跑；不得合并结果。
7. **E18L 严重 truncation 且 bounds 跨零。** 明确 inconclusive，不救。
8. **Llama/DeepSeek 的 E17 natural description/history bridge 不成立。** 作为 invariance 不等于 rationality 的 boundary 保留。

---

## 6. 当前故事与旧故事的区别

### 最初假设

```text
reasoning training
-> presentation canonicalization or policy override
-> behavioral invariance
```

问题：容易把 invariance 写成模型普遍不受 context 影响，也无法解释 evidence-conflicting histories。

### 中期机制故事

```text
reasoning
-> distributed trajectory control
-> pre-answer causal state
-> control shifts away from prompt
```

优点：机制强。问题：如果和 behavior 只是并排出现，reviewer 会问“为什么这解释 invariance？”

### 当前完整故事

```text
reasoning-oriented computation
-> natural trajectory progressively integrates decision evidence
-> trajectory builds a causally sufficient pre-answer state
-> final control shifts from prompt form toward trajectory/state

same evidence + different form
-> similar decision state
-> greater invariance

different evidence + matched form
-> different decision state
-> preserved / amplified sensitivity
```

所以全文不是“一个 MI finding + 一个 benchmark result”，而是：

> **一个失败的 invariance replication 揭示了旧 construct 混淆；正交拆解后发现 reasoning 重新分配了 sensitivity 的对象，而 trajectory 与 internal state 提供了 causal explanation。**

---

## 7. Reviewer compression：最危险的说法与我们的回答

### “This is just Mind the DH Gap + probes.”

不对。Parent 拥有 broad phenomenon；我们从 mechanism 开始，并完成 natural trajectory construction、direction-specific state substitution、matched prompt × trajectory control、prospective form × evidence decomposition，以及 selective state mediation。

### “This is just Thought Injection / CoT affects outputs.”

不对。Generic trace causality 只对应 E05 lead。我们的对象是 training/route-associated control reallocation，以及 controller 对 form/evidence 的选择性。

### “This is sampling bias in description–experience.”

不对。Sampling error 是成熟 decision-science identification issue，也是 E20 的动机。我们的新结果是：reasoning regime 的 behavioral sensitivity、trajectory control 和 pre-answer state content 都沿 form/evidence distinction 系统性重组。

### “This is Persistent Latent Policy States on risky choice.”

[Persistent Latent Policy States](https://arxiv.org/abs/2607.18532) 已拥有 reasoning fine-tuning 后的 latent dynamics/state transplant 等一般图景；它不拥有 presentation form vs decision evidence 的选择性、生成 trajectory 的 factorial causal control，或 reasoning-induced invariance 的解释。

### “Patching late layers changes the answer. Obviously.”

如果只报 E08，确实会这样被压缩。C1 的科学单位是 progressive construction + late-state consolidation，C2 是跨 regime 的 control reallocation，C3 是 state 内容的 selective sensitivity。Layer 是测量坐标，不是标题。

---

## 8. Main-level 对齐：我们已经有什么，还缺什么

### 已经形成的深度

```text
established phenomenon
-> representation constraint
-> progressive natural process
-> text-free internal carrier
-> mechanism-phenomenon bridge
-> natural independent-unit breadth
-> held-out failure
-> construct reconceptualization
-> prospective account discrimination
-> internal selective mediation
-> external-family replication
```

这条链比横向加 probe/layer/model 更像成熟 Main work。对齐对象不是实验数量本身，而是：

- *Racing Thoughts*：一个 computational hypothesis 被多层证据连续推进；
- *LLM Language Network*：localization 后必须证明 causal role 和 breadth；
- [*What Makes a Good Reasoning Chain?*](https://aclanthology.org/2025.emnlp-main.329/)：结构规律要连接 failure explanation、后果和多任务/模型证据；
- *Mind the DH Gap*：自然现象必须有足够 independent-unit/model breadth，而不是三条 prompts。

### 当前最弱的维度

1. **严格 training attribution 仍有限。** OLMo 是共同 base sibling association；Qwen 是 same-weight route；DeepSeek/Llama unmatched。三条轴 triangulate computation，但没有 isolation 单一训练步骤。
2. **选择性 state surgery 只在 OLMo 做深。** E22 提供 text-level causal external breadth，没有复制完整 E21 layer factorial。
3. **domain scope 仍是 risky decision making。** 这是自然且重要的 domain，但不能直接写 universal reasoning law。
4. **invalid/truncation 需要正文透明。** 特别是 OLMo E20 component 与 E18L。

这些是诚实 scope，不应把 headline 压回“OLMo 某层现象”。当前三条互补 identification axes 和 137-unit prospective crown 已足以支持较大的 computation-level story；论文写作需要让边界服务叙事，而不是让边界吞掉叙事。

---

## 9. 数据与推断纪律

- base decision 是主要 scientific unit；generation、order、history 和 layer 都是 nested observations。
- primary uncertainty 使用 base-decision cluster bootstrap；不把几万 generations 当独立样本。
- E20 使用未被模型 scoring 的真实 history cells，但复用了 137 个已存在的 base problem；不能写“137 unseen decisions”。
- raw 与 empirical summary 使用完全相同的 observation multiset，保证 evidence identity。
- history selection 由 empirical EV direction/strength 客观完成，不看模型输出。
- OLMo/Qwen/Llama axes 识别内容不同，不能混成一种因果设计。
- invalid response 使用 sharp assignment bounds；bounds 不支持的 component 必须降级。
- 所有主实验 condition keys、row counts、prompt/raw hashes、factorial completeness 和 execution audits 均 PASS。
- 大型 raw continuations/state rows 保留在本地并由 `.gitignore` 排除；仓库跟踪 compact summaries、unit metrics、manifests 和 SHA-256，不上传大实验文件。

---

## 10. 讨论时最值得问的几个问题

这些是 paper framing / limitation questions，不是马上扩跑 model zoo 的指令。

1. `Selective sensitivity` 最好表述为“reasoning changes what models are sensitive to”，还是更机制化的“causal control shifts from presentation form to evidence”？当前建议主标题用前者，subtitle/claim 用后者。
2. C1 中“causally sufficient pre-answer state”是否会被理解得过强？state substitution 证明 carrier sufficiency under intervention，不证明完整 natural mediation；正文要把两层说法分开。
3. E20 的 OLMo invalid-rate boundary 放正文结果段还是 limitation？建议正文直接给 joint sharp bound，component qualification 紧跟结果，不留给 reviewer 挖。
4. 是否需要把“invariance != rationality”的 E17 external boundary 放主文？它能防止一个危险误读，但不应抢 C3 的高潮。
5. 最终 consequence 是 evaluation principle：presentation robustness benchmark 必须区分 form-preserving evidence 与 evidence-changing variation。它应作为 C3 的自然后果，不另立 claim。

---

## 11. 文件和结果入口

### 先读这些

- 当前完整研究报告：`PILOT_REPORT.md`
- 当前 claim ledger：`CLAIMS.md`
- 全部实验注册与状态：`EXPERIMENTS.md`
- 当前 manuscript narrative：`MANUSCRIPT_DRAFT.md`
- 对抗性 reviewer audit：`REVIEWER_AUDIT.md`
- 数据和 gold：`DATA_AND_GOLD.md`
- causal estimands：`CAUSAL_FRAMEWORK.md`
- related work ownership：`RELATED_WORK.md`

### Crown experiments

- E20 behavior/control：`results/cpc18_form_evidence_seed157/`
- E21 selective state：`results/cpc18_selective_state_seed173/`
- E22 external replication：`results/cpc18_form_evidence_llama_seed179/`
- paper-ready 图：`results/selective_sensitivity_story/selective_sensitivity_story.pdf`

### 关键 supporting experiments

- E18 untouched confirmation：`results/cpc18_competition_seed137/`
- E18P precision：`results/cpc18_competition_precision_seed149/`
- E18L history length：`results/cpc18_history_length_seed163/`
- calibration/confirmation synthesis：`results/cpc18_replication_summary.json`

---

## 12. 当前结论

**Verdict：GO。**

现在 L12 已经不再只是“OLMo Think 的 CoT 能改答案”，也不是“reasoning 模型更 invariant”的 parent replication。它有一条累计而非并列的解释链：

> 决策在自然 trajectory 中逐步形成，凝结为 pre-answer causal state；reasoning regime 把控制权从 prompt surface 转向这条 trajectory/state；这种 shift 不是普遍 insensitivity，而是让模型更少响应 presentation form、更强响应 decision evidence。

最重要的写作纪律是：保留 E18 失败带来的反转，不把 scope boundary 写成自我瓦解，也不把支持性 probe、layer 或额外 checkpoint 膨胀成新的 headline claims。整篇 paper 只讲一个问题：

> **Reasoning 到底改变了模型如何形成决策，以及它选择对什么保持敏感？**
