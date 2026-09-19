# Research-Question Formation & Paper-Growth Paradigm Atlas

> **定位：calibration atlas，不是 canonical search guide，也不是 idea menu。**
>
> 正式找题流程以 `../SEARCH_GUIDE_ZH.md` 为准。这里保留不同论文如何形成问题与长成完整 story 的案例，供阅读时反向校准。

日期：2026-09-19  
状态：**V2 taste calibration — waiting for user approval before candidate search**

这份文件是 `chasing trends/` 的核心校准文件。

它不是“优秀论文类型列表”，也不是“以后照着套的模板”。

它试图回答的是：

> **优秀 AI 论文的问题到底是从哪里长出来的？**
>
> **它与 related work 的关系，究竟是怎样从“已有很多工作”变成“这里还有一个值得做的东西”？**
>
> **一个最初很小的 observation / contradiction / mathematical fact / engineering pain，怎样一步步变成一篇 Main-level paper？**

---

# 0. 最重要的纠偏：不要把 paper shape 当成 idea generator

上一版 `chasing trends` 过度强调：

> failure → diagnosis → design principle → method → benchmark

这确实是一类很强的论文，但**它只是一种 paper-growth pattern**。

如果把它当成统一搜题方法，下一轮 agent 会机械地：

1. 找一个热门方法；
2. 找一个 failure；
3. 强行分析；
4. 强行提出一个方法。

这和过去：

> phenomenon → mechanism

的机械化问题完全一样。

因此本文件明确区分三个层次：

## Layer A — Question provenance

问题**从哪里来**？

例如：

- 两篇 paper 的结论互相冲突；
- 一个社区长期默认的 assumption 在新系统里不成立；
- 一个很强的方法有效，但真正起作用的部分不清楚；
- 一个已有方法越来越复杂，但没人验证复杂度是不是必要；
- 一个理论在邻域领域已经成熟，却恰好解释当前模型的 unexplained failure；
- 一个常用 observable 把两个量混在了一起；
- 一个新 regime 让旧问题第一次可以被识别；
- 一个新的 scaling axis 出现，社区还不知道怎么分配资源。

## Layer B — Related-work relation

新论文相对于 prior 到底新增了什么？

可能是：

- unify conflicting results；
- isolate a hidden variable；
- remove a confound；
- change the unit of analysis；
- show a previously assumed mechanism is not necessary；
- prove a structural limitation；
- discover a boundary/regime change；
- replace an opaque recipe with a minimal principle；
- exploit a newly available intervention；
- convert a descriptive observation into a causal/control primitive。

## Layer C — Final paper form

最后论文可以长成：

- pure scientific analysis；
- theory + empirical validation；
- mechanism paper；
- analysis → method；
- method paper；
- simplification / minimal recipe；
- unification study；
- scaling-law / allocation paper；
- benchmark paper（通常不是当前用户偏好，但有时会出现）；
- architecture / objective paper；
- cross-domain transfer。

**A/B/C 不得混为一谈。**

---

# 1. 如何做“论文反向工程”

我们不可能知道作者真实脑内的完整创作历史。

因此以后所有 “idea 怎么形成” 都必须写成：

> **Reconstructed formation path**

而不是：

> “作者当时就是这么想的。”

每篇强论文至少读：

- Introduction；
- Related Work；
- 第一组关键 observation / motivating experiment；
- 核心 method / theorem；
- main table / main figure；
- ablation；
- limitation / discussion（如果有）。

然后回答：

1. **Before this paper, community believed/used what?**
2. **What pressure makes that state unsatisfactory?**
3. **What exact prior results are in tension?**
4. **What hidden assumption links those priors?**
5. **What new quantity / decomposition / unit did the paper introduce?**
6. **What decisive experiment or theorem made the new framing real?**
7. **Why could this not be reduced to “new model / new benchmark / cleaner experiment”?**
8. **How did the paper grow from its seed into a broad story?**
9. **What part is generalizable as a search move?**
10. **What part is dangerously specific and should NOT be copied?**

---

# 2. Paradigm A — Literature conflict → hidden axis → unification

## Exemplar

**ACL 2026 — What Makes a Good Curriculum? Disentangling the Effects of Data Ordering on LLM Mathematical Reasoning**

### What related work looked like before

Curriculum learning 已经很成熟。

已有 paper：

- 有的 easy→hard；
- 有的 hard→easy；
- 有的用 task difficulty；
- 有的用 model confidence / uncertainty；
- 有的 online dynamic sampling；
- 有的 RL-based curriculum。

如果机械做 novelty audit，很容易说：

> “curriculum 早就有人做了，kill。”

### 真正的 scientific pressure

问题不是：

> “再提出一个 curriculum。”

而是：

> **为什么 prior 在“什么 curriculum 好”这件事上根本没有一致答案？**

论文 Introduction 明确指出，prior 在：

- difficulty metric；
- training protocol；
- evaluation；
- forward vs reverse direction；

上都不同，因此结论不可直接比较。

这不是一个 exact gap。

这是一个：

> **literature-level inconsistency。**

### Reconstructed formation path

最 plausible 的 idea growth：

1. 发现 curriculum paper 越来越多；
2. 不同 paper 都声称自己的 ordering 有效；
3. 但“difficulty”这个词其实混了不同 quantity；
4. ordering 又和 online optimization / reward shaping 混在一起；
5. 因此先不造新 curriculum；
6. 把已有 difficulty definition 拆成多个 axes；
7. 固定其它因素；
8. 问“哪一种 metric × model × task regime 下什么 ordering 有效？”
9. 最后得到的不是一个 winner，而是**条件化规律**。

### 为什么 Main-sized

因为它重新组织了一个已经拥挤的 literature。

知识增量不是：

> metric M 比 metric N 好。

而是：

> “good curriculum” 不是单一 ordering；它依赖 difficulty 的定义、模型能力和任务复杂度。

### 可迁移 search move

当一个方向里出现：

> Paper A 说 X，
> Paper B 说 not-X，
> Paper C 又依赖另一种定义，

不要马上选边站。

先问：

> **这些 paper 是否其实在测不同 latent axis？**

### 危险模仿

不要做：

> “把 5 个 metric 全测一遍。”

必须先有真实 conflict。

---

# 3. Paradigm B — Opaque frontier success → minimal ingredients

## Exemplar

**EMNLP 2025 — s1: Simple test-time scaling**

### Before

OpenAI o1 证明了 test-time scaling 很强。

但方法不公开。

随后社区产生：

- tree search；
- MCTS；
- multi-agent；
- RL；
- complex verifier；
- long reasoning recipe。

### Pressure

真正的问题不是：

> “我们也做一个 reasoning model。”

而是：

> **这么复杂真的必要吗？**

这是典型的：

> **complexity challenge / minimality question。**

### Reconstructed formation path

1. frontier result 改变了社区 belief：test-time compute 有价值；
2. 但复现路线越来越复杂；
3. 最强的科学压力变成：
   > 哪些 ingredient 是 necessary，哪些只是 implementation baggage？
4. 作者反过来追求最小 recipe；
5. 用少量高质量数据 + budget forcing；
6. 再通过 ablation 验证：
   - quantity；
   - diversity；
   - difficulty；
   - test-time control；
7. 论文价值来自：
   > “原来并不需要大家以为的那么复杂。”

### Related-work relation

不是：

> 比已有方法再涨一点。

而是：

> **把一个 opaque, high-complexity frontier capability 压缩成一个透明、可复现、可研究的 minimal recipe。**

### 可迁移 search move

当一个热点里：

- 新系统越来越复杂；
- 大家默认复杂 pipeline 是必要条件；
- 但没有 component necessity audit；

可以问：

> **what is the minimal sufficient recipe?**

### 危险模仿

“简单”本身不是 novelty。

必须存在：

> 一个社区真实相信复杂度必要的背景。

---

# 4. Paradigm C — Desirable behavior is known to fail → baseline autopsy → new training paradigm

## Exemplar

**ICLR 2025 — Training Language Models to Self-Correct via Reinforcement Learning (SCoRe)**

### Before

self-correction 不是新问题。

已经有：

- prompting；
- refinement model；
- teacher feedback；
- offline correction traces；
- SFT / STaR。

所以它完全不是“没人做过”。

### Pressure

关键 tension：

> LLM 常常具有解决题目的知识，
> 但单纯让它“再想一次”反而无法稳定修正自己。

更进一步：

> 如果已经有 correction trace，为什么 SFT 仍学不会真正 self-correct？

### Reconstructed formation path

这篇最值得学的是：

> **先做 baseline autopsy，再造 method。**

作者不是从：

> “RL 很火，所以 self-correction + RL”

开始。

而是先分析：

- SFT correction trace 为什么无效？
- naïve RL 为什么也可能无效？

他们识别出至少两个具体 pathology：

1. **distribution shift**  
   训练数据里的错误来自旧 policy，部署时错误来自新 policy。

2. **behavior collapse**  
   训练把能力吸收到第一轮，第二轮只做表面修改。

这两个 failure 对修法有直接约束：

- 要 on-policy；
- 要 multi-turn；
- 要显式奖励“second-turn progress”；
- 要限制第一轮 collapse。

于是 SCoRe 出现。

### Related-work relation

非常漂亮：

> prior 已经证明 self-correction 难；
> prior 也已经有很多训练方法；
> 新论文不是“再一种训练法”，而是解释**为什么现有训练范式结构性学不到目标 behavior**。

### 可迁移 search move

当一个 behavior：

- 社区已经明确想要；
- baseline 反复失败；
- 每个 paper 都在调 recipe；

优先做：

> **failure-of-training autopsy。**

### 危险模仿

不要看到一个失败就加 RL。

必须证明：

> 为什么监督形式 / data distribution / objective 与目标 behavior 不匹配。

---

# 5. Paradigm D — Decompose one successful objective → components behave asymmetrically

## Exemplar

**NeurIPS 2025 — The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning**

### Before

RLVR 已经有效。

大部分 work 研究：

- PPO / GRPO；
- advantage；
- KL；
- sampling；
- rollout。

但默认把 binary reward 的正负信号一起看。

### Pressure

一个非常简单但强的问题：

> **RLVR 到底是因为“奖励正确”有效，还是因为“惩罚错误”有效？**

这不是新 benchmark。

也不是新 optimizer。

是对一个成功 objective 的**factorization**。

### Reconstructed formation path

1. 有一个强 method；
2. 它由两个概念上不同的信号组成；
3. prior 一直联合训练，因此作用纠缠；
4. 把 objective 拆开；
5. 单独训练 PSR / NSR；
6. 出现反直觉结果：
   - positive 提高 Pass@1，却伤 diversity；
   - negative 单独已经很强；
7. 再做 gradient analysis；
8. 最后才提出 upweight NSR。

### Related-work relation

这类论文不需要：

> prior 完全没研究 mechanism。

只需要：

> **prior 没把一个 load-bearing compound operation 拆开。**

### 可迁移 search move

对所有热门方法问：

> **它是不是把多个 qualitatively different learning signals 压成了一个 loss / reward / score？**

例如：

- positive / negative；
- exploration / exploitation；
- selection / execution；
- content / style；
- planning / execution；
- correctness / calibration。

### 危险模仿

不要随便把 loss 写成 A+B 就称“decomposition”。

必须让 A/B：

> 有不同 prediction、不同 downstream behavior。

---

# 6. Paradigm E — Wrong unit of analysis → new measurement → new phenomenon

## Exemplar

**ACL 2026 — Reasoning Fails Where Step Flow Breaks**

### Before

已有：

- attention analysis；
- saliency；
- token attribution；
- CoT faithfulness；
- reasoning failure analysis。

所以如果只看关键词：

> “attention / saliency / reasoning failure”

几乎全都有人做过。

### Pressure

作者发现真正的问题可能不是：

> 没有 signal。

而是：

> **signal 的单位不对。**

Long-form reasoning 是 step-structured 的，但现有 analysis 多为 token-level。

token map：

- dense；
- noisy；
- 无法自然表达 step→step dependency。

### Reconstructed formation path

1. 现有工具在 long reasoning 上变得 unreadable；
2. 不是发明更复杂 probe；
3. 而是改 measurement unit：
   > token → step
4. Step-Saliency 让原本不可见的结构显现；
5. 再发现 shallow lock-in / deep decay；
6. 最后 intervention 才出现。

### Related-work relation

novelty 不是：

> “我们又有一个 saliency 方法。”

而是：

> **把 long reasoning 的自然 computation unit 变成 analysis unit。**

### 可迁移 search move

遇到成熟 measurement 时问：

> **社区测量的粒度，是否和当前系统真正的 computational unit 对齐？**

可能是：

- token → reasoning step；
- frame → event；
- sample → trajectory；
- layer → phase；
- example → cluster；
- reward → sub-objective。

### 危险模仿

换 aggregation granularity 本身不够。

必须能：

> 揭示旧 measurement 看不到的 stable structure。

---

# 7. Paradigm F — Outcome failure → temporal dynamics → leverage point

## Exemplar

**ACL 2026 — Dissecting Failure Dynamics in Large Language Model Reasoning**

### Before

已有 test-time scaling：

- Best-of-N；
- tree search；
- entropy branching；
- verifier；
- self-correction。

### Pressure

这些 work 大多问：

> “怎样给失败 trajectory 更多 compute？”

但一个更底层的问题是：

> **失败是在什么时候发生的？**

如果错误早早出现，后面几千 token 都只是 locally coherent continuation：

> global resampling 很浪费。

### Reconstructed formation path

1. 从 final correctness 往 timeline 展开；
2. 找 failure onset；
3. 发现错误高度 temporal concentration；
4. failure onset 附近 entropy spike；
5. 同 prefix 的 alternative continuation 仍可能正确；
6. 所以错误是：
   > local decision failure，不是 knowledge absence；
7. intervention 应该只打在 critical transition。

### Related-work relation

它和已有 entropy branching 很接近。

真正的新知识不是：

> “entropy 有用。”

而是：

> **entropy 的价值来自它在 failure onset 的 temporal localization，并且 failure 仍 local-recoverable。**

### 可迁移 search move

对于任何 iterative system：

> 不要只分类“成功/失败”。

画：

> **failure dynamics / onset / propagation / recoverability。**

---

# 8. Paradigm G — Adjacent-domain theory → structural explanation → practical remedy

## Exemplar

**NeurIPS 2024 — Transformers need glasses! Information over-squashing in language tasks**

### Before

Transformer 在：

- counting；
- copying；
- simple algorithmic task；

上会出现奇怪 failure。

同时 theoretical transformer literature 很多，但常做：

- infinite precision；
- hard attention；
- idealized expressivity。

### Pressure

一个更现实的问题：

> **为什么真实 decoder-only Transformer 连这么基本的信息搬运都可能失败？**

### Reconstructed formation path

关键不是：

> “GNN 有 over-squashing，我们也在 Transformer 测一下。”

而是：

1. 从 decoder-only computation graph 出发；
2. 注意所有历史信息最终汇聚到 last-token representation；
3. 这在图结构上和 message passing bottleneck 有结构同构；
4. GNN theory 已经有 over-squashing；
5. 把那套 sensitivity / information-propagation logic 重新推到 decoder-only Transformer；
6. 得到 representational collapse / position-dependent sensitivity；
7. 再用真实 LLM 验证；
8. 最后提出直接由 theory 推出的 simple fix。

### Related-work relation

这类跨领域迁移真正成立，因为：

> **不是借术语，而是同一个 mathematical structure。**

### 可迁移 search move

跨领域时必须写：

> source domain 的 theorem / constraint  
> → target system 中的 homologous structure  
> → target-specific prediction  
> → empirical validation。

### 危险模仿

禁止：

> “CV 有 X，所以 NLP 也测 X。”

---

# 9. Paradigm H — Train-time invariant / coupling → deployment breaks it

## Exemplar

**CVPR 2026 — Elucidating the SNR-t Bias of Diffusion Probabilistic Models**

### Before

diffusion 的 exposure bias / inference error accumulation 已经有人观察。

所以：

> “diffusion train-test mismatch”

不是新问题。

### Pressure

旧工作知道：

> inference sample 偏离 training distribution。

但为什么？

论文进一步识别：

> training 时 SNR 和 timestep 严格绑定；
> inference 时误差累积导致 actual SNR 偏离当前 timestep。

于是：

> exposure bias 被升级成一个更具体的 broken coupling。

### Reconstructed formation path

1. existing phenomenon：reverse process 出现 error accumulation；
2. prior correction 多偏 phenomenological；
3. 问：
   > 到底是哪一个 training invariant 在 inference 时被破坏？
4. 找到 SNR↔t coupling；
5. sliding-window / theory 验证；
6. 再按 frequency decomposition 做 differential correction。

### Related-work relation

这类 successor work 很重要：

> broad phenomenon 已被发现，不等于 underlying causal quantity 已被找到。

### 可迁移 search move

对热门 inference procedure 问：

> **训练时有哪些变量天然 coupling，但部署的新 solver / search / iterative feedback 会把它们解耦？**

### 危险模仿

不能直接把“train-test mismatch”换个变量重说一遍。

必须找到：

> 一个具体 coupling，且它给出 correction prediction。

---

# 10. Paradigm I — Internal structure → new controllable primitive

## Exemplar

**ICLR 2026 — Deconstructing Guidance: A Semantic Hierarchy for Precise Diffusion Model Editing**

### Before

图像编辑大量使用：

- CFG；
- attention mask；
- cross-attention control；
- inversion；
- spatial editing。

背景修改困难是一个现实 pain。

prior 多把问题理解成：

> **WHERE to edit**

然后做 mask / attention manipulation。

### Pressure

作者换了问题：

> 会不会不是“位置没找准”，而是 guidance signal 本身对不同 semantic scale 强度不一样？

### Reconstructed formation path

1. 从实际 editing failure 开始；
2. 观察 (Delta epsilon) magnitude 有系统结构；
3. 不把它仅当 spatial mask；
4. 提出 semantic-scale hypothesis；
5. 用 Tweedie / variance / Fisher information 提供 first-principles explanation；
6. 由 magnitude hierarchy 直接得到 controllable decomposition；
7. Prism-Edit 出现。

### Related-work relation

真正新的是：

> **把同一个已有 signal 重新解释成另一个 scientific object。**

prior：
> (Deltaepsilon) = where

这篇：
> (Deltaepsilon) magnitude = semantic scale

### 可迁移 search move

对一个大家每天都在用的中间量问：

> **社区是不是只把它当 computational artifact，而没有问它携带什么结构？**

### 危险模仿

representation/probe 不能止步于“发现结构”。

强版本是：

> structure → intervention/control。

---

# 11. Paradigm J — Representation-learning insight → generation bottleneck → alignment regularizer

## Exemplar

**ICLR 2025 Oral — REPA: Representation Alignment for Generation**

### Before

diffusion / flow 模型越来越大。

同时另一条 literature 发现：

> diffusion hidden states 也能学 discriminative representation。

但它们比现代 self-supervised visual encoder 的表示差。

### Pressure

关键 jump：

> **如果 diffusion 在训练生成模型时，还要自己从头学高质量 visual representation，这会不会就是优化瓶颈？**

这不是从 generation literature 内部直接长出的。

它连接了：

- generative modeling；
- self-supervised representation learning。

### Reconstructed formation path

1. 已知 diffusion 具备 representation-learning capability；
2. 已知 external SSL encoders 的 representations 更成熟；
3. 把这两个事实放一起；
4. 形成 hypothesis：
   > generation training 的一部分成本其实是在重复学习 representation；
5. 直接把 pretrained representation 当 teacher；
6. 用简单 alignment regularizer；
7. 训练速度大幅提高。

### Related-work relation

不是：

> “给 diffusion 加 perceptual loss。”

而是：

> **重定义了 training bottleneck。**

### 可迁移 search move

当一个系统同时需要：

- 学 task；
- 又学一个已有成熟模型已经擅长的 latent structure；

问：

> 能否外部提供这个 structure，让训练只学剩下的 computation？

---

# 12. Paradigm K — Existing method works, but resource axis is new → empirical scaling law → allocation policy

## Exemplar

**ICLR 2025 — Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Parameters for Reasoning**

### Before

传统 scaling 主要：

> model size / pretraining compute。

test-time compute 出现后，社区突然多了一个新的 scaling axis。

### Pressure

真正的问题不是：

> “更多 inference compute 有用吗？”

而是：

> **固定额外 compute 到底该怎么花？**

而 prior 当时大量：

- negative result；
- uniform Best-of-N；
- verifier search；
- iterative refinement。

### Reconstructed formation path

1. 新资源维度出现；
2. 现有 literature 没有 allocation law；
3. 比较多种 test-time compute mechanism；
4. 发现效果高度依赖 prompt difficulty；
5. 于是从“method comparison”升级成：
   > compute-optimal allocation；
6. 再做 FLOPs-matched comparison，改变 pretrain-vs-inference scaling 的讨论。

### Related-work relation

它不是：

> 一个新的 search algorithm。

而是：

> **一个新的 resource-allocation law。**

### 可迁移 search move

每当新的资源维度出现：

- tokens；
- rollouts；
- tools；
- verifier calls；
- memory；
- modalities；
- agents；

问：

> uniform allocation 是否合理？
>
> 最优分配取决于什么 observable state？

---

# 13. Paradigm L — Crowded scientific object → new explanatory decomposition

## Exemplar

**ICLR 2026 — Mechanism of Task-oriented Information Removal in In-context Learning**

### Before

ICL mechanism 已经极其拥挤：

- induction heads；
- task vectors；
- implicit gradient descent；
- Bayesian inference；
- task recognition vs task learning；
- representation shift。

如果只按“parent occupied”规则：

> 根本不该做 ICL mechanism。

### Pressure

真正值得学 Zhao/Cho 的地方是：

> 他们不是继续定位同一 mechanism，
> 而是换了**explanatory decomposition**。

### Reconstructed formation path

这篇先构造：

> zero-shot query representation 是 non-selective，包含多种 task-relevant information。

然后观察：

> selective removal 某些信息可以把输出 steer 到目标 task。

于是新 framing 不是：

> demonstration “adds” task information，

而是：

> demonstration 可能通过 **removing irrelevant dimensions** 完成 task selection。

接下来：

- representation structure；
- low-rank removal；
- metric；
- attention heads；
- ablation；

都是围绕这个新 decomposition 展开。

### Related-work relation

这是一个重要 lesson：

> **crowded object ≠ no room。**

只要你改变的是：

> 哪个 latent operation 才是 explanatory primitive。

### 可迁移 search move

在成熟领域问：

> 大家一直把过程解释成 “add / retrieve / amplify / copy”，
> 是否存在另一种等价但 prediction 不同的 operation：
> “remove / gate / rotate / rebind / suppress / redistribute”？

### 危险模仿

不要为了“新 decomposition”玩文字游戏。

必须：

> 新 decomposition 产生可干预 prediction。

---

# 14. Paradigm M — Practical failure + prior fixes all attack the wrong level

这是一个跨多篇 paper 反复出现的 meta-pattern。

例如：

- self-correction：prior 调 prompt / offline trace；真正问题是 training distribution。
- image editing：prior 调 mask / attention；真正问题是 guidance signal magnitude。
- diffusion exposure bias：prior 做 phenomenological correction；真正问题是 broken SNR-t coupling。
- reasoning scaling：prior 加更多 compute；真正问题是 critical transition localization。

### Search move

当一个方向已经有大量 fixes，但 failure 仍持续：

不要直接发明 fix N+1。

先画：

> **prior fixes map**

每个 fix 实际在改哪一层：

- data；
- objective；
- representation；
- search；
- routing；
- readout；
- compute；
- calibration；
- interface。

然后问：

> **大家是不是一直在同一个 level 上修，而真正原因在另一个 level？**

这经常是非常高价值的 idea source。

---

# 15. Paradigm N — “Why does a dumb/simple thing work?” → reverse-engineer implicit computation

很多强 paper 不是从 failure 出发，而是从：

> **unexpected success**

出发。

例子结构：

- simple baseline 居然追上复杂 method；
- negative-only RL 居然很强；
- 1000 examples 居然足够；
- training-free correction 居然跨模型有效；
- pretrained feature alignment 居然带来数量级加速。

这种 pressure 非常适合当前 AI research：

> 大量工程 recipe 先出现，解释往往落后。

### Search move

主动收集：

> **“按现有解释，它不应该这么有效，但它就是很有效”的 result。**

然后问：

> 哪个隐式 mechanism 被原解释漏掉了？

---

# 16. Paradigm O — Known result + changed premise → old answer must reopen

旧问题可以重新问，但不是因为模型更新。

强 changed premise 必须是：

> prior conclusion 依赖 assumption P；
> 新系统真正移除了 / 反转了 P。

例如抽象结构：

- offline → on-policy；
- single pass → iterative deliberation；
- fixed compute → adaptive search；
- sequence reward → verifiable online reward；
- teacher-forced context → self-generated context；
- fixed solver path → learned/dynamic solver；
- same model handles prediction and critique，而不是两个独立模型。

### Search move

看老 paper 的 conclusion 时，强制提取：

> **load-bearing premise list。**

然后检查 2025–2026 新系统：

> 哪个 premise 真变了？

这是比“新模型重测”高级得多的找题方式。

---

# 17. Paradigm P — New intervention makes old debate identifiable

这类不一定有 method。

科学问题可能几十年前就有：

- representation vs use；
- local update vs reconstruction；
- planning vs reactive generation；
- latent state vs readout；
- retrieval vs recomputation。

过去难点不是没人想过。

而是：

> **没有 identification instrument。**

现代 foundation model 给了：

- exact hidden states；
- causal patching；
- controlled fine-tuning；
- log-probs；
- reruns from same prefix；
- intervention at token/layer/step；
- synthetic micro-world。

### Search move

找：

> 一个旧 debate，
> 现在第一次可以做 causal separation。

这保留了原 `ssn-taste` 的强项，也避免纯 mechanism tool-first。

---

# 18. Paradigm Q — Community proxy silently changed meaning

这是非常适合当代 AI 的 generator。

热门方向经常快速发展，导致一个旧 proxy：

- perplexity；
- entropy；
- reward；
- confidence；
- length；
- consistency；
- FID；
- preference margin；
- win-rate；

在新 regime 下**语义变了**。

例如：

- positive RL 提升 Pass@1 但伤 Pass@k；
- preference margin 变大却不代表绝对 quality 变好；
- curriculum “difficulty” 在 problem-side 和 model-side 是不同量；
- token entropy 有时是 uncertainty，有时更像 branching leverage。

### Search move

问：

> **这个 observable 过去代理 quantity Q；在新 regime 下它还代理同一个 Q 吗？**

如果不是：

> 可能得到新的 analysis、method、metric 或 theory。

---

# 19. 从这些 paradigms 看，真正应该搜的不是“题型”，而是 pressure source

下一轮不要从：

> “今天找一个 mechanism→method 题。”

开始。

而应该从不同 provenance pool 并行采样：

### Pool 1 — Contradictory literature
不同 paper 给出不一致结论。

### Pool 2 — Opaque strong recipe
能力出现了，但 ingredient necessity 不清楚。

### Pool 3 — Repeated failure
大家一直修，但问题没真正消失。

### Pool 4 — Compound objective
一个 loss/reward 中多个信号被默认等价。

### Pool 5 — Wrong analysis unit
measurement 与 computation unit 不对齐。

### Pool 6 — Dynamics
终点相同，但形成路径 / failure onset 不同。

### Pool 7 — Structural theory
architecture/operator 有硬 constraint。

### Pool 8 — Broken assumption / coupling
training 与 inference / old regime 与 new regime 不同。

### Pool 9 — Useful internal structure
隐藏量可以直接变 controller。

### Pool 10 — Cross-lineage connection
两个领域各自有一半事实，合起来出现新 hypothesis。

### Pool 11 — New scaling axis
资源增加了，但 allocation law 不清楚。

### Pool 12 — Unexpected simplicity / success
简单方法反常地有效。

### Pool 13 — Changed premise
旧结论依赖的 premise 被真正移除。

### Pool 14 — New identification
旧争论第一次可以被干预区分。

### Pool 15 — Proxy semantic drift
常用 score 在新范式下不再代表原 quantity。

每轮至少跨 **5 个 pool**，避免被单一题型锁死。

---

# 20. “related work 里怎么发现问题”的具体读法

以后读 Related Work，不能只是记 citation。

建立一个表：

| Paper | What it assumes | What it changes | What it measures | Main conclusion | Hidden dependence |
|---|---|---|---|---|---|

然后找五类结构：

## A. Same question, different assumptions

结论冲突可能来自 premise 不同。

## B. Same method, different explanation

不同 paper 都有效，但解释互相不兼容。

## C. Same metric, different semantic meaning

大家都报一个数字，但它在不同 regime 代表不同 thing。

## D. Same failure, fixes attack different layers

说明社区没有 agreed causal model。

## E. Same outcome, different path

endpoint 一样，但 learning/inference dynamics 不一样。

这些比：

> “Related work 没人做 exact experiment E”

重要得多。

---

# 21. 强论文 seed 如何长成 Main story

一个 seed 一般不是一开始就 Main-sized。

常见 growth operators：

### 1. Local observation → general law
从一个 case 找到 across-regime quantity。

### 2. Correlation → intervention
从“相关”升级成“改它就改变 outcome”。

### 3. One method → method family explanation
解释一组方法为什么有效/无效。

### 4. One failure → failure taxonomy
发现两个 qualitatively different failure modes。

### 5. One metric → hidden decomposition
把一个 observable 拆成多个 causal objects。

### 6. One model → structural prediction
不是 model zoo，而是验证 theory/机制跨实现成立。

### 7. One fix → principle
方法本身很小，但背后的 design rule 很广。

### 8. Existing puzzle → resource/training implication
科学 finding 改变实际 algorithm design。

### 9. Old debate → modern causal test
让旧问题第一次可判。

### 10. Complex recipe → minimal sufficient set
削掉 complexity，反而得到更清楚贡献。

---

# 22. 以后禁止的机械化模式

## 禁止 1

> 看到热门 paper X → 找一个 failure → 提 fix。

除非 failure 有独立 pressure。

## 禁止 2

> 看到 mechanism paper → 换 object 再做 mechanism。

## 禁止 3

> 看到 CV idea → 找 NLP 对应名词。

## 禁止 4

> 看到一个 paper future work → 直接做下一格。

## 禁止 5

> 看到一个 benchmark gap → 方法补 gap。

## 禁止 6

> 看到某个 metric 有问题 → metric paper。

必须问 downstream scientific/method consequence。

## 禁止 7

> “最近都在做 X，所以我们做 X。”

热点只能决定：

> search prior / execution ecosystem / reviewer interest，

不能代替 scientific pressure。

---

# 23. 当前 taste 的真正融合

旧 `ssn-taste` 教会我们：

> 不要找没人做过的格子，要找 unresolved knowledge delta。

新 `chasing trends` 不能把它改成：

> 找一个热门 failure 然后修。

真正融合后应该是：

> **从真实 literature structure 中找 pressure。**
>
> pressure 可以是科学的、方法的、理论的、工程范式的。
>
> 然后让最自然的 paper form 自己长出来。

有的 pressure 最后会长成：

> pure analysis。

有的：

> mechanism → method。

有的：

> theory → architecture fix。

有的：

> conflict → unification。

有的：

> minimal recipe。

有的：

> scaling law / resource allocation。

**先有 pressure，再决定 paper shape。**

---

# 24. 当前阶段的硬规则

在用户明确通过这个 V2 taste 之前：

- 本文件不直接生成或裁决 CTxx；正式 candidate 由根目录 canonical workflow 审计。
- 不注册候选；
- 不进入 pilot；
- 不因为某个 exemplar 很漂亮就复制其结构。

下一步真正开始搜题时：

> **先建 lineage map 和 pressure ledger，后形成 candidate。**

而不是：

> 先 brainstorm candidate，再补 related work。
