# chasing trends 科研选题搜索指南（Canonical）

最后系统整理：2026-09-19

这份文件定义 `chasing trends/` 的长期找题与审题流程。

当前阶段：

> **FRAMEWORK CALIBRATION ONLY — WAITING FOR USER APPROVAL**

在用户明确通过本规范以前：

- 不生成正式 CTxx；
- 不注册 candidate；
- 不开始 pilot；
- 不把任何文献中的 future work 直接变成题。

---

# 1. 目标

优先目标会议：

- ACL / EMNLP / NAACL Main
- ICLR / ICML / NeurIPS

持续观察：

- AAAI
- CVPR / ICCV / ECCV
- TACL

重点不再限定“纯科学机制论文”。

当前优先 paper archetype 是：

> **important trend**
>
> → **specific failure / inefficiency / mismatch**
>
> → **diagnosis / mechanism**
>
> → **design principle**
>
> → **small method**
>
> → **standard benchmark improvement**
>
> → **mechanism-aware ablation / analysis**

论文可以以方法为主要 contribution。

但不接受：

> 先拍脑袋发明一个模块 → 涨点 → 再补一个 plausible story。

---

# 2. 一篇目标论文的 contribution tuple

以后审题时，强制写清五个对象：

[
(F, C, P, M, R)
]

其中：

- **F — Failure / Pain**：现有主流方法到底哪里坏？
- **C — Cause / Operating mechanism**：为什么坏？
- **P — Principle**：这个原因推出什么设计原则？
- **M — Method**：最小实现是什么？
- **R — Regime**：在哪些模型 / 数据 /任务 / compute regime 下应该成立？

好的 project 应满足：

> (F ightarrow C ightarrow P ightarrow M)

是连续的。

如果：

- F 和 C 没关系；
- C 不约束 P；
- P 不自然推出 M；
- M 的收益和 C 的强弱无关；

说明 story 是拼出来的。

---

# 3. “机制”在这里是什么意思

本路线的 mechanism **不等于 mechanistic interpretability**。

以下都可以是 mechanism：

- reasoning step 的信息流断裂；
- error 在 trajectory 中的传播；
- policy gradient 集中在少数 branching tokens；
- easy/hard samples 获得不合理的 rollout budget；
- reward / advantage estimator 的系统偏差；
- policy/reference probability mismatch；
- entropy collapse；
- diversity collapse；
- train–test mismatch；
- supervision distribution 与 student distribution 不匹配；
- score 被 sequence length / confidence / exposure 等 nuisance confound；
- compute 被浪费在已经 mastered 的 sample；
- 某个 intermediate representation 出现 bottleneck；
- early/late computation 承担不同功能；
- search/pruning/routing 在错误位置做决定。

优先选择：

> **可以被直接测量、干预、并且能指导算法设计的 mechanism。**

低优先级：

- 某层能 decode 某信息；
- 某 head 看起来重要；
- 某 vector 可以 steering；
- 某 SAE feature 和现象相关；

除非这些内部发现直接给出有效的新方法。

---

# 4. Positive taste：应该学习什么论文

不要把强论文只当 citation database。

每一篇 exemplar 都要做以下 autopsy：

1. **Trend**  
   它为什么处在一个社区真正关心的方向？

2. **Pain**  
   prior 到底哪里不够？

3. **Diagnostic observation**  
   作者先看到了什么可重复事实？

4. **Competing explanations**  
   是否真的排除了最危险的简单解释？

5. **Design principle**  
   diagnosis 具体限制了什么方法设计？

6. **Method minimality**  
   方法是不是对症，而不是 module stacking？

7. **Benchmark closure**  
   为什么这些 benchmark 能证明 method 有价值？

8. **Ablation closure**  
   哪个实验证明 gain 来自被声称的机制？

9. **Compute story**  
   gain 是否来自更多 token / sample / FLOPs / parameters？

10. **Reviewer compression**  
    最弱表述是什么？为什么仍然新？

11. **Growth pattern**  
    这篇 paper 是怎样从“小 failure”长成 Main story 的？

12. **Transferable primitive**  
    可以迁移的到底是哪个 causal structure，而不是哪个名词？

---

# 5. 文献搜索必须足够广

每轮不得只看一个 conference、一个 subfield 或一个热点。

最少覆盖：

## NLP / LLM

- reasoning / test-time scaling
- SFT / distillation
- RLVR / RLHF
- reward / verifier / PRM
- post-training dynamics
- inference-time search
- model compression / efficient inference
- multimodal reasoning

## CV / Generation

- diffusion / flow matching
- image / video generation
- image editing
- multimodal generation
- efficient sampling
- distillation
- representation alignment
- reward fine-tuning

## General ML

- optimization
- adaptive sampling
- curriculum
- credit assignment
- uncertainty
- distribution shift
- information bottlenecks
- control
- dynamical systems

PaperNotes 可以用于：

> **高吞吐 discovery / taxonomy / cross-conference browsing。**

但正式依赖的关键 claim 必须尽量回到：

- ACL Anthology
- OpenReview
- PMLR
- NeurIPS proceedings
- CVF / ECCV official
- paper PDF / official project page

---

# 6. 最优先的 generator

这一节定义下一轮真正开始搜题时，优先寻找什么 pressure。

## G1 — Failure transition / error propagation

问：

> 模型什么时候从“还可恢复”进入“基本失败”？
>
> 错误是在哪一步产生，之后如何传播？

适合：

- reasoning；
- tool use；
- generation；
- planning；
- multimodal chain。

方法机会：

- selective correction；
- branching；
- rollback；
- targeted resampling；
- local steering；
- early rescue。

典型成功结构：

> GUARD / StepFlow 一类。

---

## G2 — Credit assignment mismatch

问：

> 最终 reward / label 到底应该分给哪些 token、step、sample、trajectory？

尤其关注：

- 高影响 token vs 普通 token；
- planning token vs execution token；
- successful trajectory 中的 accidental steps；
- negative vs positive signal；
- tool feedback 前后的 credit；
- partial correctness。

方法机会：

- selective loss；
- adaptive advantage；
- token/segment weighting；
- step-level redistribution；
- selective replay。

---

## G3 — Resource allocation mismatch

问：

> 固定 compute / rollout / sampling budget 是否被均匀花在价值完全不同的位置？

例如：

- easy sample 已经 mastered；
- impossible sample 基本没有正确 rollout；
- uncertainty 集中在少数 branch；
- 不同 patch / timestep / token 需要的 compute 不同。

方法机会：

- adaptive rollout；
- adaptive sampling；
- early stopping；
- difficulty-aware allocation；
- conditional compute；
- curriculum / resampling。

这类题尤其适合当前算力约束，因为：

> **方法目标本身通常就是少花 compute。**

---

## G4 — Objective / estimator mismatch

问：

> 我们优化的 surrogate 真正在优化想要的 quantity 吗？

典型：

- group-relative advantage 与 calibration mismatch；
- reward margin 上升但 winner/loser 都变差；
- average log-prob 被 step length confound；
- training loss 混入 irreducible component；
- reward model 随 search scale 失真。

方法机会：

- corrected objective；
- debiased estimator；
- normalized score；
- constrained optimization；
- robust reward shaping。

---

## G5 — Entropy / diversity collapse

不要泛泛问：

> RL 会不会 entropy collapse？

而要问：

> collapse 从哪一种 update 进入？
>
> 哪些 token/sample/trajectory 真正贡献 collapse？
>
> diversity 是不是和 accuracy 的同一个控制量？

方法机会：

- adaptive entropy target；
- selective entropy regularization；
- group/quantile baseline；
- replay / sampling adjustment；
- negative-signal reweighting。

---

## G6 — Train–test mismatch

这是从 diffusion/CV 最值得迁移的 generator 之一。

找：

> 一个训练时严格绑定的 quantity，在推理时被 solver/search/sampling 打散。

或者：

> 训练 objective 隐含假设 A，但 deployment 实际满足 B。

方法机会往往非常干净：

- calibration；
- rescaling；
- schedule correction；
- distribution matching；
- inference-time adjustment。

这类论文非常适合：

> **analysis → formula → tiny fix → broad gain。**

---

## G7 — Student / data / feedback distribution mismatch

尤其适合：

- distillation；
- SFT；
- rejection sampling；
- synthetic data；
- iterative self-training。

问：

> “高质量”数据为什么反而不适合当前 learner？
>
> teacher 的 style / difficulty / entropy / strategy 和 student 是否错配？

方法机会：

- student-aware refinement；
- difficulty matching；
- style alignment；
- adaptive curriculum；
- selective distillation。

---

## G8 — Hidden confound in a popular heuristic

找：

> 当前社区非常常用一个 score / selector / proxy，
> 但这个 quantity 被一个 surface factor 系统污染。

例如：

- length；
- formatting；
- confidence；
- number of samples；
- first-token likelihood；
- verbosity；
- positional effects。

最强形式不是：

> “metric 不完美”。

而是：

> **confound 会改变训练数据 / gradient / search choice，因此直接伤害下游方法。**

然后修 selector。

---

## G9 — Internal bottleneck with direct utility

适合少量 interpretability。

要求：

> 找到内部 bottleneck 后，立刻能用来做 routing / editing / pruning / conditioning / correction。

不接受：

> 只有 representation geometry 图很好看。

跨 diffusion / VLM 很多这类 paper 值得学。

---

## G10 — Constraint-derived method

从 architecture / optimization / information theory 出发：

> 现有 operator 有一个硬 constraint；
> failure 是这个 constraint 的直接后果；
> 改变或绕开 constraint 后，failure 应消失。

这是最“科学”的方法论文结构之一。

但是必须先 audit：

> obvious constraint 是否早已被 literature 挖完。

---

# 7. Changed-premise 在新路线里的用法

老问题仍然可以重做。

但必须满足：

> **旧 failure 的主要原因 P 在新范式中确实被改变；因此旧方法/解释不再直接适用。**

可接受例子：

- 从 single-pass CoT 变成长 reasoning；
- 从 sequence-level RL 变成 group-relative RL；
- 从 fixed inference 变成 test-time search；
- 从 offline generation 变成 tool-interactive feedback；
- 从 multi-step diffusion 变成 one/few-step flow；
- 从 uniform compute 变成 adaptive compute。

不接受：

- Qwen2 → Qwen3；
- Llama3 → Llama4；
- 新 benchmark；
- 新语言；
- 更大模型。

---

# 8. 跨领域迁移规则

允许大量迁移，但每次强制完成四步。

## Step 1 — 抽象掉领域名

不要记：

> “diffusion 有 SNR-t bias”。

记成：

> **训练时一个 nuisance/control variable 与过程状态一一绑定，但推理算法改变了状态轨迹，使绑定关系破坏。**

---

## Step 2 — 找 LLM 中独立存在的 homologous pressure

不能因为结构“像”就移植。

必须问：

> LLM / reasoning / post-training 中是否真的有同样的约束？

---

## Step 3 — 导出 prediction

如果迁移是真的，应出现：

> condition A 下偏差强；
> condition B 下偏差弱；
> correction C 应特异性修复。

---

## Step 4 — 再谈方法

如果没有独立 prediction：

> 只是 analogy，不能立题。

---

# 9. 完整工作流

## Phase 0 — Restore

开始每轮前：

- 读 `chasing trends/README.md`
- 读本文件
- 读 `PAPER_AUTOPSIES_*.md`
- 读 `LESSONS_FROM_SSN_TASTE.md`
- 读 chasing-trends 的 FAILED ledger（建立后）
- 看最近 commits

同时只把 `ssn-taste` 当：

- anti-duplication；
- execution-risk；
- process lessons。

不要把 S04–S08 当新路线正向模板。

---

## Phase 1 — Trend map

先画 4–6 个活跃 lineage，不起题。

每个 lineage 记录：

- 最近 1–2 年核心方法；
- 最近 6–12 个月发生了什么 premise shift；
- 当前 common baseline；
- 大家反复报告什么 pain；
- 哪些 benchmark 已成熟；
- 代码/训练成本；
- 哪些方向已经过度拥挤。

不要因为 paper 数多就选。

---

## Phase 2 — Failure mining

只收集：

> **具体可测的 failure。**

每条写：

- F 是什么；
- 谁已经观察；
- 是否稳定；
- 是否重要；
- 它影响 accuracy / efficiency / stability / generalization 中哪个；
- 是否存在便宜的 reproducer。

不想方法。

---

## Phase 3 — Diagnosis map

对最有价值的 failure，写 2–4 个 explanation。

注意：

> 不是为了做纯 possible-world science。

而是为了判断：

> 哪个 explanation 如果成立，会导出不同修法？

如果所有 explanation 都对应同一种 heuristic：

> diagnosis 没价值。

---

## Phase 4 — Lock one failure

不要 dump 20 个题。

锁住当前最强的一条，开始深审。

---

## Phase 5 — Nearest-prior audit

真正危险 prior 至少看：

- abstract；
- intro；
- method；
- main tables；
- diagnostic figure；
- ablation；
- discussion / limitation。

强制写：

> Prior knows X.
>
> Existing fixes do Y.
>
> They still fail / remain unclear under R because Z.
>
> We diagnose C.
>
> C predicts principle P.
>
> P yields method M.

如果写不出来：

> KILL。

---

## Phase 6 — Cheap diagnosis gate

在训练新 method 前，先证明：

> F 和 C 不是幻觉。

首个 pilot 尽量：

- 1 个主模型；
- 1–2 个辅助模型；
- 1–3 个已有 benchmark；
- inference/logprob/gradient/rollout 分析；
- 少量 SFT/RL steps；
- 无人工大规模标注；
- 无新 environment。

目标不是出最终数字。

目标是：

> **决定是否值得进入 method stage。**

---

## Phase 7 — Mechanism-to-method derivation

强制写：

> If C is true, then an effective method should do P.

然后再写具体实现 M。

最好：

> 一个核心 knob。

最多：

> 两个强相关组件。

如果出现：

- filtering + curriculum + contrastive loss + memory module + verifier + special decoding；

通常说明：

> 没有一个清楚的 design principle。

KILL 或简化。

---

## Phase 8 — Minimum method pilot

先验证：

1. M 是否真的改变 target mechanism；
2. benchmark 是否有方向一致的 gain；
3. gain 是否不是更多 compute 造成；
4. failure-heavy subset 是否比 easy subset 改善更多。

如果 mechanism 没变但分涨：

> story 错了，需要重新解释，不能硬写。

如果 mechanism 变了但分不涨：

> method 价值不足；考虑一次最直接修正，不无限调参。

---

## Phase 9 — Benchmark plan

full paper 通常应包含：

- 2–4 个公认 benchmark；
- 至少一个强 current baseline；
- compute-matched comparison；
- general benchmark；
- mechanism-heavy / failure-heavy slice。

不要求：

> 所有 benchmark SOTA。

更重要的是：

> gain 与 paper claim 对得上。

---

## Phase 10 — Ablation closure

不是机械：

> 去掉 A / B / C 看掉几点。

优先做：

### Mechanism-strength test

当 failure quantity 变强时：

> baseline gap 是否更大？
>
> method gain 是否也更大？

### Targeted intervention

只改变我们声称的原因：

> gain 是否按预测改变？

### Compute-normalized test

确保不是：

- 更多 tokens；
- 更多 rollouts；
- 更多 samples；
- 更大 batch；
- 更长 training；
- 更多 parameters。

### Boundary test

在哪个 regime：

> method 不应该有效？

能正确失败，往往比再多一个 benchmark 更有说服力。

---

## Phase 11 — Compute / engineering audit

高优先：

- inference-time；
- training-free；
- lightweight SFT；
- LoRA；
- 小规模 RL；
- selective update；
- existing rollout infrastructure。

中优先：

- 2B–8B RLVR；
- distillation；
- reward / verifier training；
- moderate multimodal fine-tuning。

低优先：

- full pretraining；
- 30B+ repeated RL sweeps；
- large agentic environments；
- long-horizon tool simulators；
- new robotics environment；
- architecture from scratch。

如果核心 idea 必须等 expensive full run 才能知道真假：

> 默认 KILL。

---

## Phase 12 — Main story audit

普通 reviewer 应能在 30 秒内回答：

1. 现有热门方法有什么具体问题？
2. 为什么以前的 fix 没解决？
3. 我们发现真正原因是什么？
4. 我们的方法如何直接针对这个原因？
5. 提升在哪里？
6. 为什么相信提升来自这个原因？

如果第 3→4 句不自然：

> story 不成立。

---

## Phase 13 — Final verdict

不保留正式 “SERIOUS”。

锁定候选后最终必须：

### PILOT-AUTHORIZED

或者：

### KILL

允许整轮 0 survivor。

---

# 10. PILOT-AUTHORIZED 门槛

必须同时满足：

- trend / task 当前重要；
- failure 真实而非人为造；
- nearest prior 没完成同一 F→C→P→M；
- cheap reproducer 可行；
- diagnosis 有 discriminative prediction；
- diagnosis 对 method 有约束力；
- method 足够简单；
- benchmark 已存在；
- strong baselines 可跑；
- compute 可承受；
- 不依赖大规模新数据；
- 不依赖 model zoo；
- 不依赖巨型 recipe sweep；
- paper 的增益不是隐藏 compute；
- ablation 可以闭合 claim；
- reviewer compression 后仍有清楚 novelty。

---

# 11. KILL 条件

出现以下任何一条，应直接杀：

- same failure + same diagnosis + essentially same fix 已被做；
- failure 只在很人造的 setting 出现；
- diagnosis 只是 correlation；
- diagnosis 不约束 method；
- method 是任意 module stacking；
- 只有大量调参才涨；
- gains 来自更多 compute；
- benchmark path 不清楚；
- 需要先造大 benchmark；
- 需要大量人工标注；
- 需要 expensive model zoo 才能判断真假；
- training story 对 optimizer/budget 极不稳定；
- agent environment 成本成为论文主体；
- RAG pipeline 工程量大于 scientific/method contribution；
- reviewer 可压成 “existing method + one heuristic”；
- cross-domain 只有术语相似；
- 一旦强 baseline 加上就没有空间。

---

# 12. Reasoning / RLVR 的特别纪律

这是当前高产区，但也最容易卷。

不要泛泛做：

- 新 GRPO variant；
- 新 advantage formula；
- entropy bonus；
- difficulty curriculum；
- token weighting。

必须先有一个具体 diagnosis。

例如：

> group-relative baseline 为什么在某种 uncertainty 结构下偏？

> 哪些 token 的 entropy 真的对应 branching decision？

> 哪种 successful trajectory 会产生 harmful gradients？

> tool feedback 如何改变 rollout distribution？

> test-time scaling 为什么在增加 sample 后 verifier 反而变差？

然后方法才有资格出现。

---

# 13. Agentic RL 的特别纪律

默认低优先。

只有满足以下条件才考虑：

- 可复用现成 environment；
- 任务 reward 自动计算；
- rollout 不需要昂贵 API；
- horizon 不长；
- failure 可以先 offline/inference 分析；
- method 不要求新 simulator；
- pilot 小模型几小时级即可看方向。

否则：

> 即使题很潮，也不适合当前搜索。

---

# 14. RAG 的特别纪律

默认不做。

除非：

> 有一个非常干净、非工程化的 learning / inference mechanism，
> 并且方法主要改模型行为而不是搭 retrieval pipeline。

普通：

- chunking；
- reranking；
- query rewrite；
- memory store；
- hybrid retrieval；

不进入主搜索池。

---

# 15. Training / pretraining 的特别纪律

可以做，但吸取 S03/S09。

优先：

- within-run measurable quantity；
- data/gradient allocation；
- objective correction；
- sample weighting；
- representation alignment；
- loss decomposition；
- curriculum with observable state。

谨慎：

- “什么时候学会能力”；
- “checkpoint 中机制如何形成”；
- “不同 stage 为什么产生某能力”；
- “memory age / training history”。

除非 causal variable 可以干净定义，否则容易 recipe explosion。

---

# 16. 新的 reviewer compression 模板

每个 candidate 必须完成：

> **Current approach X** is widely used for Y, but systematically fails under **regime R**.
>
> Existing work observes/mitigates **F**, but does not isolate **cause C** (or assumes the wrong cause).
>
> We show that **C** is the operative bottleneck through **diagnostic E**.
>
> This implies design principle **P**, leading to **method M**.
>
> Under matched compute, **M** improves **benchmarks B** and its gains scale with the strength of **C/F**, supporting the proposed mechanism.

如果只能写成：

> X 不够好，所以我们提出 M，实验显示更好。

KILL。

---

# 17. 下一轮 candidate 输出模板

用户通过本规范后，每个锁定 candidate 最终报告：

- **Trend / lineage**
- **Current method**
- **Concrete failure**
- **Why it matters**
- **Nearest prior**
- **Reviewer compression**
- **Diagnostic hypothesis**
- **Alternative explanation(s)**
- **Cheap reproducer**
- **Design principle**
- **Proposed minimal method**
- **Why this method follows from diagnosis**
- **Benchmarks**
- **Strong baselines**
- **Compute estimate**
- **Mechanism-aware ablations**
- **Failure-heavy slice**
- **Expected main figure**
- **Novelty sentence**
- **Kill conditions**
- **Verdict**

最终只有：

> **PILOT-AUTHORIZED — register CTxx**

或：

> **KILL**

---

# 18. 当前硬停止线

现在不要开始 CT01。

必须等用户先审：

- `README.md`
- `LESSONS_FROM_SSN_TASTE.md`
- 本 `SEARCH_GUIDE_ZH.md`
- `PAPER_AUTOPSIES_2026-09-19.md`

用户通过以后，再开始真正搜题。

不为“赶快出题”跳过这一步。
