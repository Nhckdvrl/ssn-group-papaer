# Paper Autopsies — 2026-09-19

> **Status note — superseded as the canonical interpretation.**
>
> This file was the first breadth/deep-reading pass and contains useful paper-level observations, but its synthesis over-weighted one paper shape: `failure → diagnosis → method`.
>
> Do **not** use its concluding archetype as the topic-search template.
>
> Read it together with, and subordinate it to:
>
> - `RESEARCH_TASTE_RECALIBRATION_2026-09-19.md`
> - `PAPER_GENEALOGY_GUIDE.md`
> - `SEARCH_GUIDE_ZH.md`
>
> The current goal is to reconstruct **multiple question genealogies** from strong papers and their related work, not to make every new topic look like the examples below.

目的：

> **学习“问题 / failure 是怎么长成方法论文的”，不是收集方法名。**

这份文件是 `chasing trends/` 的第一轮 positive calibration。

重要说明：

- PaperNotes 用于大规模 discovery 和跨会议分类。
- 关键 exemplar 尽量回到 ACL Anthology / OpenReview / NeurIPS / CVF / ECCV official page 核实。
- PaperNotes 中尚未逐篇核实原文的论文会明确标记为 **INDEX-ONLY CALIBRATION**；未来若真的基于它生成 candidate，必须重新读原论文。
- 这里的论文也**不是 candidate**。它们只提供 paper-growth pattern。

---

# 0. 先说结论：最值得学习的共同结构

这一批论文跨 ACL / EMNLP / ICLR / ICML / NeurIPS / AAAI / CVPR / ECCV，但最强的方法论文反复出现同一个拓扑：

> **现有热门方法总体有效**
>
> → **在某个清楚 regime 下出现系统性 failure**
>
> → **作者不是马上加 module，而是先找一个可测量的中间量**
>
> → **这个量揭示 failure 实际发生在哪里 / 为什么发生**
>
> → **方法只修改那个位置**
>
> → **standard benchmark 上涨**
>
> → **gain 对 failure-strength / mechanism-strength 呈预测关系**

最值得迁移的不是：

- GRPO；
- entropy；
- diffusion；
- attention；
- saliency。

而是：

> **把“哪里坏”变成“哪里应该改”。**

---

# 1. ACL 2026 — Reasoning Fails Where Step Flow Breaks

**类型：CORE EXEMPLAR**

## Pressure

长 reasoning chain 的失败不能被 final-answer accuracy 解释。

两个错误 trace 可能：

- 一个早就偏航；
- 一个只在最后一步算错。

如果只看最终 reward，它们被当成同一类失败。

## Diagnosis

论文把关注点从：

> “这条 reasoning 对不对？”

转到：

> **信息能否从一个 reasoning step 正确流向下一步。**

Step-Saliency 揭示两类 failure dynamics：

- **Shallow Lock-in**：很早形成错误方向，后续持续强化；
- **Deep Decay**：前面方向合理，但深层推理中信息逐步断裂/丢失。

## Method growth

不是 generic self-correction。

它根据 flow breakdown 的位置做 targeted repair，形成 StepFlow。

## 为什么这是我们想学的

完整链条非常清楚：

> final failure 太粗
>
> → step flow 是更对的 diagnostic object
>
> → failure 有不同 dynamics
>
> → intervention 应该打在 flow break 上
>
> → benchmark gain 证明 diagnosis 有 utility。

## 可迁移 primitive

> **Outcome-level supervision is too coarse when failure is localized in a trajectory.**

这可以迁移到：

- tool trajectories；
- multimodal reasoning；
- diffusion sampling；
- planning；
- iterative refinement。

不能机械迁移成：

> “别的任务也做 Step-Saliency。”

---

# 2. ACL 2026 — Dissecting Failure Dynamics in Large Language Model Reasoning

**类型：CORE EXEMPLAR**

## Pressure

reasoning failure 常被当成整个 trajectory 的整体属性。

但如果 failure 实际由少数转折点触发：

> 全局重采样 / 全局反思会浪费 compute。

## Diagnosis

核心发现是：

- 失败往往起源于少数较早的关键 transition；
- 这些位置伴随 entropy / branching signal；
- 即使当前 path 走错，附近 alternative branches 仍可能成功。

也就是说：

> 失败不是“整条 chain 已经坏死”，而是**局部 branch selection 错误**。

## Method growth

GUARD 只针对危险 transition 进行识别和 redirect。

## 为什么强

方法不是在 paper 后半段突然出现。

如果 diagnosis 是真的：

> selective branch repair 几乎是自然结论。

## 可迁移 primitive

> **Find the earliest irreversible or high-leverage decision, not the final error.**

---

# 3. ACL 2026 — Calibration-Aware Policy Optimization for Reasoning LLMs

**类型：CORE EXEMPLAR**

## Pressure

group-relative RL 可以提升 reasoning accuracy，但模型 probability/confidence 可能被错误塑形。

## Diagnosis

作者不是泛泛说“RL 不 calibrated”。

关键是指出：

> GRPO 的 uncertainty-agnostic advantage construction 会在特定状态下产生和 calibration 目标不一致的 gradient。

这是 objective-level diagnosis。

## Method growth

CAPO 直接修 advantage / update，使 optimization 对 calibration-aware。

## 为什么值得学

这是非常干净的：

> **popular objective → derive bias → correct objective → benchmark + calibration gains。**

比：

> “我们觉得 confidence 重要，所以加一个 calibration loss”

强很多。

## 可迁移 primitive

> **先检查 popular surrogate 的 gradient direction 是否与真正目标一致。**

---

# 4. ACL 2026 Findings — Understanding and Mitigating Spurious Signal Amplification in Test-Time Reinforcement Learning for Math Reasoning

**类型：CORE EXEMPLAR**

## Pressure

test-time RL / self-training 使用模型自身生成的信号时，最危险的不一定是完全错误样本，而可能是：

> 中等一致性、看起来有信息但实际 ambiguous 的样本。

## Diagnosis

论文把噪声细分后发现：

> group-relative advantage 可能放大这类 spurious signal。

## Method growth

通过 DDRL 一类重新处理/抑制 ambiguous feedback，而不是简单提高采样数。

## 可迁移 primitive

> **Self-generated supervision may amplify medium-confidence ambiguity, not only obvious errors.**

这是非常值得在：

- self-training；
- verifier-guided search；
- agent reflection；
- synthetic data；

中寻找的 failure class。

---

# 5. ACL 2026 Findings — On the Step Length Confounding in LLM Reasoning Data Selection

**类型：CORE EXEMPLAR**

## Pressure

很多 reasoning data-selection 方法用平均 log-probability / confidence 选“好步骤”。

但这个 score 是否真的表示 step quality？

## Diagnosis

作者发现：

> score 被 step length 等 surface factor 系统性污染，尤其受到低概率开头 token 的影响。

也就是说：

> selector 正在优化一个带 confound 的 proxy。

## Method growth

ASLEC-DROP / CASL 一类方法修正选择逻辑。

## 为什么很适合我们的 taste

它不是纯 metric-validity paper。

因为 confounded score 会进一步改变：

> **哪些数据进入训练 → 哪些 gradient 被模型看到。**

因此 metric diagnosis 直接变成 training method。

## 可迁移 primitive

> **Popular selection score → identify nuisance confound → show downstream training harm → debias selector.**

---

# 6. ICLR 2026 — Emergent Hierarchical Reasoning in LLMs through Reinforcement Learning

**类型：CORE EXEMPLAR**

## Pressure

“RL 能提升 reasoning”太粗。

真正有用的问题是：

> RL 的提升发生在哪一类 computation？

## Diagnosis

论文观察到层级化变化：

- 较低层 / procedure skill 先稳定；
- 后续瓶颈转向高层 strategy / planning；
- training signal 对不同 token 的价值并不相同。

## Method growth

HICRA 把 credit 更集中到高影响 planning tokens。

## 为什么强

mechanism 不是 head/circuit。

它是：

> **learning dynamics 中 computation hierarchy 的变化。**

而这个 dynamics 直接决定：

> gradient 应该往哪里放。

## 可迁移 primitive

> **As a skill becomes mastered, the learning bottleneck migrates upward.**

---

# 7. ICLR 2026 — SimpleTIR: End-to-End Reinforcement Learning for Multi-Turn Tool-Integrated Reasoning

**类型：CORE EXEMPLAR**

## Pressure

tool-integrated RL 看起来只是普通 RL 多了 tool output。

但 tool feedback 会改变后续 context distribution，并让早期错误持续污染后续 rollout。

## Diagnosis

论文定位到：

> 某些 void / unproductive turns 产生坏 feedback loop 和 harmful gradients。

## Method growth

不是发明复杂 agent architecture。

核心修法很小：

> 过滤特定坏 trajectory / turn，阻断错误 signal 继续进入更新。

## 为什么适合我们

这是 agentic RL 中少数相对“轻”的 archetype：

> **先找 trajectory pathology，再改 training signal。**

## 约束

这不意味着下一轮应该追 agentic RL。

环境成本仍然可能过高。

---

# 8. ICLR 2026 — Fixing the Broken Compass: Diagnosing and Improving Inference-Time Reward Modeling

**类型：CORE EXEMPLAR**

## Pressure

inference-time scaling 越来越依赖 reward/verifier 选最好 candidate。

直觉上：

> sample 越多，选择应该越好。

但 verifier 本身可能随着 search scale 失真。

## Diagnosis

论文识别出多种 failure：

- easy problem 反而 degradation；
- sample 数增加时 discriminative ability 下降；
- search diversity 增大时 reward reliability 变差。

## Method growth

CRISP 类方法用 cluster / prefix information 重新组织 reward signal。

## 可迁移 primitive

> **A selector that works on iid candidates may fail once the search procedure changes candidate distribution.**

这是非常重要的 changed-premise：

> selector 的输入分布被 inference-time scaling 自己改变了。

---

# 9. ICLR 2026 — Characterizing and Mitigating Reasoning Drift in Large Language Models

**类型：CORE / ANALYSIS→METHOD**

## Pressure

长 CoT 不是单纯“越想越好”。

模型可能：

> 在持续生成中逐步离开本来正确的推理方向。

## Diagnosis

把 drift 定义成过程变量，而不是只看终点错误。

## Method growth

通过针对 drift state 的 intervention / adaptive strategy 减轻偏航。

## 可迁移 primitive

> **Iterative computation can create its own distribution shift.**

这可迁移到：

- iterative refinement；
- multi-turn tool use；
- repeated self-correction；
- diffusion / search。

---

# 10. NeurIPS 2025 — Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning

**类型：CORE EXEMPLAR**

## Pressure

sequence-level RL 把同一 trajectory 中所有 token 都纳入 update。

但真正决定 reasoning branch 的 token 可能非常少。

## Diagnosis

作者发现：

> 少数 high-entropy / forking tokens 承担大部分有效决策。

这不是“entropy 越高越好”。

而是：

> entropy 提供了 **decision leverage** 的定位信号。

## Method growth

只在高价值 token 上更新，仍可匹配或改善 full update。

## 为什么强

同时提供：

- science：learning signal 不均匀；
- method：selective update；
- efficiency：少更新；
- analysis：关键 token。

## 可迁移 primitive

> **Gradient budget should follow decision leverage, not token count.**

---

# 11. NeurIPS 2025 — The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning

**类型：CORE EXEMPLAR**

## Pressure

RL 通常同时有 positive successful signal 和 negative failed signal。

社区默认二者都重要。

## Diagnosis

拆分后发现：

- negative signal 本身非常有效；
- positive signal 在某些情况下会压缩 diversity / exploration；
- 二者不是对称信息源。

## Method growth

重新分配 positive / negative update 权重。

## 可迁移 primitive

> **Different feedback signs may teach qualitatively different things.**

不要只做：

> reward coefficient sweep。

应该找：

> 哪类行为 / diversity / strategy 被每种 signal 改变。

---

# 12. NeurIPS 2025 — SPARKLE

**类型：CORE EXEMPLAR**

## Pressure

RL 在 reasoning 的不同维度上提升不均匀。

## Diagnosis

细分能力后发现：

> RL 更擅长改善 knowledge integration / planning flexibility，而 plan execution 仍有缺口。

## Method growth

基于这个 gap，引入 partial-step scaffolding，让 hard problems 可以被继续利用，而不是简单丢掉。

## 可迁移 primitive

> **A training method can improve one phase of computation while leaving another as the new bottleneck.**

---

# 13. EMNLP 2025 Main — Enhancing Efficiency and Exploration in Reinforcement Learning for LLMs

**类型：POSITIVE BUT IMPORTANT WARNING**

## Pressure

uniform rollout allocation 浪费 compute：

- easy question 几乎没有 learning gain；
- hard question 又需要更多 sampling 才可能找到正确 path。

同时 RL 可能抑制 exploration。

## Method

动态分配 rollout budget + adaptive temperature 维持 entropy。

## 为什么值得学

它展示一个非常实用的 paper structure：

> compute allocation inefficiency → difficulty-aware policy。

## 为什么不能机械学

到了 2026，这个 parent 已经非常拥挤。

下一轮若只是：

> “difficulty-aware rollout + entropy”

大概率太晚。

### Lesson

> **旧 Main paper 可以用来学 growth pattern，但不能把 2025 的 gap 当 2026 novelty。**

---

# 14. EMNLP 2025 Main — Analyzing the Effects of Supervised Fine-Tuning on Model Knowledge from Token and Parameter Levels

**类型：ANALYSIS-FIRST CALIBRATION**

## Pressure

SFT 数据更多不一定知识更好。

论文报告某些设置下：

> 更多 SFT examples 反而降低 closed-book QA。

## Diagnosis

从 token / parameter 两层分析，发现大量 parameter updates 不贡献 knowledge enhancement；恢复部分 update 可以改善表现。

## 为什么值得学

它说明：

> 不是只有 RL 才能做“训练机制 → 方法”。

普通 SFT 里也可以从：

- harmful updates；
- update localization；
- knowledge interference；

长出方法。

## Warning

这种题必须避免：

> 变成 1000-model sweep 本身就是 contribution。

我们的版本更偏向：

> small diagnosis → actionable update rule。

---

# 15. EMNLP 2025 Main — Stepwise Reasoning Checkpoint Analysis: A Test Time Scaling Method to Enhance LLMs' Reasoning

**类型：METHOD STRUCTURE CALIBRATION**

## Pressure

普通 beam / DVTS 类 TTS：

- path homogenization；
- intermediate results 浪费。

## Method

在 reasoning step 间建立 checkpoint：

- answer-clustered search 保留 diversity；
- intermediate checkpoint candidates 参与最终决策。

## Why useful

这类 work 说明：

> test-time scaling 论文可以不用训练新模型。

如果 failure 是 search procedure 本身：

> training-free method 可能非常适合我们的算力/迭代节奏。

---

# 16. AAAI 2026 — Answering the Unanswerable Is to Err Knowingly: Analyzing and Mitigating Abstention Failures in Large Reasoning Models

**类型：BEHAVIOR→INTERNAL SIGNAL→INTERVENTION**

## Pressure

模型面对不可解题仍然强行回答。

## Diagnosis

内部 readout 显示模型在相当程度上已经能识别 unsolvability，但外部 policy 没有正确使用。

## Method

cognitive monitoring + inference-time intervention 提高 abstention。

## 为什么值得学

这是一个允许 interpretability 的形式：

> internal signal 不是终点，
> 而是 controller 的输入。

## Warning

generic “represented but unused” 在旧 ledger 已经被杀过。

要成立必须有：

> 一个重要、具体、可改进的 downstream decision。

---

# 17. ICLR 2026 — Diagnosing and Improving Diffusion Models by Estimating the Optimal Loss Value

**类型：CROSS-DOMAIN CORE EXEMPLAR**

## Pressure

大家习惯把 diffusion loss 越低看成越好。

但理论上：

> optimal loss 本身不是 0，而是未知正值。

因此 raw training loss 混合：

- irreducible difficulty；
- actual underfitting。

## Diagnosis

推导 optimal loss estimator。

## Method growth

这个 estimator 不只是分析工具，还用于：

- diagnose training；
- design better schedule；
- improve FID；
- clean scaling-law fit。

## 最值得迁移的 primitive

> **Observed loss = irreducible component + improvable component.**

在 LLM 中应寻找：

> 常用 training signal 是否也混合了不可改的难度与真正可学习误差。

不是把 diffusion 公式照抄过来。

---

# 18. CVPR 2026 — Elucidating the SNR-t Bias of Diffusion Probabilistic Models

**类型：CROSS-DOMAIN CORE EXEMPLAR**

## Pressure

training 时：

> timestep 和 SNR 有严格 coupling。

但 inference solver 走的实际 trajectory 可能打破这个 coupling。

## Diagnosis

这是一个 clean train–test mismatch。

## Method growth

通过轻量 correction 修复 bias，几乎不增加 overhead，并能跨多个 diffusion 模型改善。

## 为什么非常值得学

这是 chasing-trends 最理想的论文形态之一：

> **one hidden assumption → show deployment violates it → derive correction → plug-and-play gain。**

## 可迁移 primitive

寻找 LLM 中：

> training procedure 依赖的某个 coupling，在 decoding / search / tool feedback / test-time scaling 时失效。

---

# 19. ICLR 2026 — Deconstructing Guidance: A Semantic Hierarchy for Precise Diffusion Model Editing

**类型：INTERPRETABILITY→METHOD CORE EXEMPLAR**

## Pressure

guidance scale 被当成一个粗糙 knob。

但为什么不同 guidance magnitude 会对应不同 edit behavior？

## Diagnosis

分析 guidance difference 的内部结构，发现它和 semantic scale / hierarchy 有系统关系，并给出理论解释。

## Method growth

Prism-Edit 直接利用这个 internal semantic organization 做更精确 editing。

## 为什么它比纯机制更适合我们

如果论文只停在：

> “guidance direction 有层级结构”

对我们吸引力有限。

真正关键是：

> **internal structure 变成新的 controllable primitive。**

---

# 20. ICLR 2026 — A Hidden Semantic Bottleneck in Conditional Embeddings of Diffusion Transformers

**类型：ANALYSIS / BOUNDARY EXEMPLAR**

## Pressure

高维 conditional embedding 是否真的需要那么多维度？

## Diagnosis

发现 embeddings 极度 angular-similar，语义信息集中在少数维度；大量维度可删而质量基本不变。

## 为什么放进来

它提醒我们：

> 一个很漂亮的 bottleneck finding 不一定自动长成我们要的方法论文。

如果后续只是：

> prune dimension / compress representation，

story 可能偏 efficiency。

### Lesson

> internal finding 必须问：“它能不能导出一个更广的 design principle？”

---

# 21. CVPR 2026 — Denoising, Fast and Slow: Difficulty-Aware Adaptive Sampling for Image Generation

**类型：CROSS-DOMAIN RESOURCE-ALLOCATION EXEMPLAR**

## Pressure

固定 denoising budget 默认：

> 所有区域 /阶段同样难。

实际上 generation difficulty 不均匀。

## Diagnosis

通过 difficulty measure 定位需要更多 computation 的位置。

## Method growth

adaptive sampling：

> 难的地方慢一点，容易的地方快一点。

## 可迁移 primitive

> **Compute should follow local uncertainty/difficulty.**

这和 reasoning 中：

- adaptive rollout；
- selective thinking；
- branching token；

形成非常强的跨领域结构同构。

---

# 22. ECCV 2026 — Analyzing and Improving Training-Free Fast Sampling of Text-to-Image Diffusion Models

**类型：CROSS-DOMAIN CORE EXEMPLAR**

## Pressure

few-step sampling 的性能差，可能有多个原因：

- solver；
- model capacity；
- feature cache；
- timestep schedule。

## Diagnosis

论文把瓶颈定位到外层 time schedule，并用 trajectory geometry 的 curvature / torsion 描述少步生成。

## Method growth

TORS 用 equal-total-rotation 重新安排 sampling times，完全 training-free。

## 为什么值得学

这是：

> **geometry analysis → schedule method**

而不是：

> geometry 只用来画图。

## 可迁移 primitive

> **If trajectory changes non-uniformly, uniform discretization wastes steps.**

可启发：

- reasoning checkpoints；
- adaptive depth；
- iterative refinement；
- RL rollout checkpoints。

---

# 23. ECCV 2026 — Diffusion-SDPO: Safeguarded Direct Preference Optimization for Diffusion Models

**类型：CROSS-DOMAIN OBJECTIVE-DIAGNOSIS EXEMPLAR**

## Pressure

preference margin 变大不等于 winner 真的变好。

DPO-style relative objective 可能出现：

> winner / loser 两边绝对质量都恶化，但相对 gap 仍改善。

## Diagnosis

共享参数下 winner 与 loser gradient 的几何关系会产生这种 pathology。

## Method growth

根据 gradient relation 自适应缩放 loser update，保护 winner。

## 为什么非常值得迁移

这是一个普适结构：

> **relative objective 可以在“比较正确”的同时把两边绝对值都推坏。**

LLM preference / reasoning RL 中也值得寻找类似 failure。

但未来必须重新 audit 是否已有直接工作。

---

# 24. ECCV 2026 — Towards Scalable Pre-training of Visual Tokenizers for Generation

**类型：CROSS-DOMAIN REPRESENTATION→DOWNSTREAM LEARNABILITY EXEMPLAR**

## Pressure

visual tokenizer 的 reconstruction 更好，不代表 downstream generator 更容易训练。

## Diagnosis

继续只优化 reconstruction：

> reconstruction FID 可以改善，但 downstream generation FID 反而变差。

说明：

> representation quality 不是单一 quantity。

## Method growth

联合加入 semantic / contrastive / reconstruction objectives，形成对生成更友好的 latent space。

## 可迁移 primitive

> **Upstream representation metric can improve while downstream learnability worsens.**

适合迁移到：

- distillation；
- tokenizer；
- SFT representation；
- verifier feature；
- multimodal adapters。

---

# 25. CVPR 2026 — Reward Sharpness-Aware Fine-Tuning for Diffusion Models

**类型：INDEX-ONLY CALIBRATION — candidate 使用前必须核实原文**

PaperNotes 汇总指出：

> diffusion reward fine-tuning 中 reward score 上涨但 perceptual quality 不升，可以理解为对 reward surface sharp directions 的 exploit / reward hacking。

其方法不是重训 reward model，而是对 reward gradient 做 sharpness-aware robustification，并可插入多种 reward fine-tuning framework。

## 为什么放进 taste

即使未来原文细节需要重新核实，这个 paper-growth pattern 很值得学：

> **reward hacking → 不是“reward model 不好”这种泛解释**
>
> → 定位为 local sharpness / adversarial sensitivity
>
> → robustify optimization target
>
> → plug-and-play across algorithms。

---

# 26. CVPR 2026 — Improved Mean Flows: On the Challenges of Fastforward Generative Models

**类型：INDEX-ONLY CALIBRATION — candidate 使用前必须核实原文**

PaperNotes 的总结呈现一个非常典型结构：

- 原 MeanFlow target 依赖网络自身；
- CFG scale 在训练前被固定；
- 这两个 design constraint 成为 one-step generation 的瓶颈；
- 重新写 target + 把 guidance 变成可变 condition 后显著改善。

## Lesson

> **强方法论文经常来自“把原算法里一个默认常量/依赖关系重新当成变量”。**

这是很好的 generator。

但绝不能看到这个结构就去 NLP 硬找“某个 constant”。

---

# 27. EMNLP 2025 — Massive Supervised Fine-tuning Experiments Reveal How Data, Layer, and Training Factors Shape LLM Alignment Quality

**类型：CONTRAST CASE**

## Why read it

论文通过 1000+ SFT models 系统研究：

- data properties；
- task synergy；
- layer-wise changes；
- perplexity 与 downstream effectiveness。

这种工作很有价值。

## 为什么不是我们默认 archetype

它的主要力量来自：

> **大规模 controlled sweep。**

当前搜索不希望把 execution 变成：

> model × dataset × recipe matrix。

### Lesson

> 我们可以借它发现 candidate pressure，
> 但不要复制它的实验规模。

---

# 28. ECCV 2026 — From Hallucination to Grounding: Diagnosing Visual Spatial Intelligence via CRISP

**类型：NEGATIVE CALIBRATION FOR THIS ROUTE**

## Why interesting

通过 Spatial QA + 3D Scene Graph + consistency protocol，区分：

- genuine spatial understanding；
- semantic shortcut。

diagnostic structure 很干净。

## 为什么不是 chasing-trends 首选

它主要长成：

> benchmark / diagnostic evaluation。

没有自然、直接、低复杂度的 method closure 时：

> 很容易回到用户不喜欢的 evaluator/benchmark 路线。

### Lesson

> diagnosis 本身再漂亮，如果不能约束一个有用方法，也不一定适合本路线。

---

# 29. 从这些论文抽出的 10 个 paper-growth patterns

## P1 — Final outcome → local transition

不要只问成功/失败。

找：

> 第一个高 leverage transition。

StepFlow / GUARD 类。

---

## P2 — Uniform update → selective update

默认每个：

- token；
- sample；
- trajectory；
- timestep；

权重一样，通常只是实现方便。

找到真正 decision-bearing subset 后，可以直接长 method。

---

## P3 — Relative objective → absolute pathology

优化：

> A 比 B 好

不代表：

> A 真变好。

Diffusion-SDPO 这类结构非常值得在 preference / RL 中搜索。

---

## P4 — Proxy → confound → downstream harm

只有证明：

> confound 真的改变 training/search choice

才从 metric paper 升成 method paper。

---

## P5 — Fixed compute → difficulty-aware compute

在：

- reasoning；
- search；
- diffusion；
- sampling；

都反复成功。

但 2026 已经很拥挤。

新题必须找到一个新的、未被直接利用的 difficulty signal / allocation unit。

---

## P6 — Training assumption → deployment violation

SNR-t bias 是漂亮模板。

寻找：

> training 时天然成立、deployment 时因为新 inference procedure 不再成立的 invariant。

---

## P7 — Better teacher/data ≠ better learner

“quality”必须相对于 learner 定义。

适合：

- distillation；
- synthetic reasoning data；
- verifier feedback；
- curriculum。

---

## P8 — Analysis variable becomes controller input

好 interpretability 不是：

> “发现一个 direction。”

而是：

> direction / state / bottleneck 直接驱动 routing、stopping、correction、editing。

---

## P9 — Bottleneck migration

训练过程中：

> 低层 skill 学会以后，高层 decision 变成新瓶颈。

这允许 adaptive training，不需要解释整个人生史式 training dynamics。

---

## P10 — Minimal fix beats broad redesign

最漂亮的论文常常方法非常小。

因为：

> diagnosis 已经完成了大部分 intellectual work。

---

# 30. 反过来：什么论文结构不要学

## 1. Module stacking

> encoder + verifier + memory + curriculum + contrastive loss + search。

很难说明 gain 来自哪里。

---

## 2. Analysis as decoration

先有 method，
最后做 attention map 解释。

不是 mechanism-guided method。

---

## 3. Benchmark first

先造新 benchmark，
发现 baseline 不行，
再加一个 system。

这会回到旧路线明确不喜欢的 evaluation work。

---

## 4. Generic “entropy”

entropy 可以是：

- uncertainty；
- branching；
- diversity；
- instability；
- noise。

不先说明它在当前系统中是哪一个，就不应该围绕 entropy 造方法。

---

## 5. Generic “difficulty”

difficulty 也可能是：

- current model correctness；
- probability；
- verifier score；
- sample complexity；
- search branching；
- irreducible ambiguity。

“难题多采样”到 2026 已经不够。

---

## 6. Full training biography

不要：

> checkpoint 1 到 50 看所有能力怎么变化，然后解释。

S03 已经证明这种问题很容易 recipe explosion。

---

# 31. 对下一轮找题的直接约束

真正开始 CT01 搜索后：

1. 先找 **failure / mismatch / allocation error**，不先想算法名。
2. 优先搜能在 inference / small SFT / small RL 中复现的。
3. 每个 failure 至少有两种会导出不同 method 的解释。
4. diagnosis 成立后，method 最好只有一个核心变化。
5. full paper 必须有：
   - standard benchmark；
   - strong baseline；
   - compute-matched comparison；
   - mechanism-heavy slice；
   - mechanism-strength × gain 关系。
6. 如果一个 idea 需要先做大规模训练才知道 diagnosis 对不对：
   - 默认不选。
7. 如果一个 paper 只是因为“这个热点很火”才有吸引力：
   - 不选。
8. 如果 cross-domain idea 只有名字很酷：
   - 不选。

---

# 32. 当前 calibration verdict

经过这一轮跨会议阅读，`chasing trends` 的目标可以更精确地表述为：

> **不是“方法为主”三个字。**
>
> 而是寻找：
>
> **一个当前重要方法的具体 pathology，**
>
> **用足够轻但有区分力的分析把 pathology 定位到一个 actionable mechanism，**
>
> **然后做一个最小修复，并用标准 benchmark 与 mechanism-aware ablation 闭环。**

这是接下来 search guide 中最应保护的 paper shape。

当前仍然：

> **不生成 CT01，等待用户审核 framework。**
