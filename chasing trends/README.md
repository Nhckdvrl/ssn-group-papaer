# chasing trends

这是 `Nhckdvrl/ssn-group-papaer` 中一条**与 `ssn-taste/` 并行、但目标函数不同**的科研选题路线。

建立日期：2026-09-19

> **当前阶段只做 taste / literature / workflow calibration。**
>
> **在用户明确通过这套规范以前，不开始生成 CT01 / S10 / 新候选题。**

---

# 1. 为什么要建立这条新路线

`ssn-taste/` 的上一轮搜索把标准推到了“问题先于方法、多个 possible worlds、即使结果相反也有科学知识增量”的极致。这套纪律留下了很多非常有价值的东西：nearest-prior audit、reviewer compression、identifiability、data/compute gate、anti-resurrection、不要用新模型重测老现象等。

但它也暴露了两个现实问题：

1. **纯机制 / 纯科学问题太难找、太难做。**
   很多候选一旦真正执行，就会滑向 circuit hunting、复杂 probe、难以识别的 latent construct，或者为了排 confound 不断膨胀实验。

2. **training-dynamics 尤其容易变成 recipe biography。**
   S03 和 S09 的最终失败都说明：如果“科学变量”本身捆绑 optimizer、budget、data mixture、stage、model family、serialization 等训练轨迹，最后很容易不是稳定规律，而只是某条 recipe 的传记。

因此，本目录的目标不是继续把论文做得“更纯科学”，而是回到一个用户更喜欢、也更清晰的顶会论文结构：

> **热门且重要的范式 / 方法**
>
> → **找到一个真实、可复现、可解释的 failure / bottleneck / bias / mismatch**
>
> → **用分析或轻量机制实验说明为什么会坏**
>
> → **从这个 diagnosis 直接推出一个方法**
>
> → **在现有 benchmark 上证明方法真的更好**
>
> → **用 ablation / intervention / transfer / scaling 再闭环解释为什么有效**

这不是“不要科学问题”。

真正的变化是：

> **科学分析不再必须独立承担整篇论文。它可以成为方法设计的因果依据和设计原则。**

---

# 2. 当前 repo 正式状态

必须以 repo 最新状态为准，而不是旧 handoff。

截至 2026-09-19 最新 `ssn-taste/`：

正式仍为 **SELECTED — PILOT-AUTHORIZED** 的是：

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S05 — When Does Reading Become Learning?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?
- S08 — Is Metacognitive Control Shared?

已经正式取消：

- **S03** — actual pilot 后因 developmental story 对 training budget / model family / recipe 不稳定而 KILL。
- **S09** — 因“memory age / learning history”本身是 optimizer-path construct，无法形成 recipe-stable law，而 KILL。

因此，旧 handoff 中“S03–S09 共 7 个 selected”的状态已经过时。

本目录不会重新审这些题，也不会把它们当正向 taste exemplar。

它们只用于学习：

- 什么会导致 execution explosion；
- 什么会导致 recipe dependence；
- 什么会让纯机制题太大；
- 哪些 audit 规则值得保留。

---

# 3. 这条路线的目标论文长什么样

最典型的目标不是：

> “我们观察了现象 X，并研究了它的 mechanism。”

也不是：

> “我们发明了模块 Y，在 benchmark 上涨了 2 分。”

而是：

> **现有方法 M 在重要 regime R 下有一个具体 failure F。**
>
> **我们用分析 A 找到 F 的可解释原因 / operating mechanism C。**
>
> **C 直接给出设计原则 P。**
>
> **由 P 得到一个尽量小、尽量局部的改进 M′。**
>
> **M′ 在强 baseline 和多个标准 benchmark 上稳定改善。**
>
> **进一步分析证明收益确实来自修复 C，而不是额外参数、更多 token、更多数据或隐藏 compute。**

最理想的 Introduction 可以被压成五句话：

1. X 很重要，现在大家都在用。
2. 但 X 在 Y 情况下系统性失败。
3. 我们发现失败不是泛泛的“模型不够强”，而来自 Z。
4. 这提示一个直接的设计原则，因此我们提出 M。
5. M 不仅提高 benchmark，而且它的收益随 Z 的强弱按预测变化。

---

# 4. 正向 calibration 来源

## 4.1 Sasano 的真实判断

仍然保留 `ssn-taste` 最重要的一条：

> **正向 taste 来自 Sasano 的真实判断与真实强论文，不来自我们自己过去 selected 的题。**

但在 chasing-trends 模式下，Sasano taste 的解释要稍作调整。

最重要的不是“必须是纯 mother question”，而是：

- reviewer 一眼能明白问题在哪里；
- introduction 能让平均 reviewer 同时“納得できる + 面白い”；
- method 不是突然出现，每一步都有前一节实验或分析支撑；
- 主要结果不应该藏在 appendix；
- 论文结构必须让人很容易回答“为什么做这个实验 / 为什么需要这个模块”。

方法型论文同样必须有一个**清楚的问题链**。

---

# 5. 文献校准方式

本路线不能只盯 NLP。

优先系统扫：

- ACL / EMNLP / NAACL
- ICLR / ICML / NeurIPS
- AAAI

同时主动看：

- CVPR / ICCV / ECCV
- image / video generation
- multimodal / VLM
- speech / audio
- robotics / embodied
- optimization
- learning theory
- control / dynamical systems
- information theory

跨领域迁移的不是模块名字，而是：

> **failure decomposition**
>
> **objective mismatch**
>
> **credit assignment logic**
>
> **adaptive compute allocation**
>
> **bias correction**
>
> **train–test mismatch**
>
> **distribution matching**
>
> **coarse-to-fine / fast-slow computation**
>
> **constraint-derived design**
>
> **diagnosis → minimal intervention 的论文生长方式**

PaperNotes（https://papernotes.org/）可作为**高吞吐索引与分类器**，但不能把它当唯一事实来源。

正确用法：

1. 用 PaperNotes 按 conference × area 快速扫大量标题、摘要、方法结构；
2. 找到真正和本路线相关的 paper；
3. 对核心 exemplar 回到 ACL Anthology / OpenReview / NeurIPS proceedings / CVF Open Access / arXiv 原文核实；
4. 做 paper autopsy，而不是只抄一句摘要。

---

# 6. 当前已经确认的强 archetype

这一轮校准已经反复出现以下结构：

### A. Failure dynamics → targeted intervention

典型：

- ACL 2026 — **Reasoning Fails Where Step Flow Breaks**
- ACL 2026 — **Dissecting Failure Dynamics in Large Language Model Reasoning**
- ICLR 2026 — **Characterizing and Mitigating Reasoning Drift in Large Language Models**

共同结构：

> 不是“推理会失败”
>
> 而是定位**失败从哪里开始 / 如何传播 / 哪些状态仍然可救**
>
> → 只干预真正危险的位置。

---

### B. Learning signal decomposition → new optimizer / credit assignment

典型：

- ICLR 2026 — **Emergent Hierarchical Reasoning in LLMs through Reinforcement Learning**
- NeurIPS 2025 — **Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective Reinforcement Learning for LLM Reasoning**
- NeurIPS 2025 — **The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning**
- NeurIPS 2025 — **Beyond Accuracy: Dissecting Mathematical Reasoning for LLMs Under Reinforcement Learning**

共同结构：

> 先拆开“RL 到底改了什么 / 哪些 token 或 sample 真正在起作用”
>
> → 再把 policy update 放到更值得更新的部分。

---

### C. Objective / estimator flaw → corrected objective

典型：

- ACL 2026 — **Calibration-Aware Policy Optimization for Reasoning LLMs**
- ACL 2026 — **Understanding and Mitigating Spurious Signal Amplification in Test-Time Reinforcement Learning for Math Reasoning**
- ACL 2026 Findings — **On the Step Length Confounding in LLM Reasoning Data Selection**
- ICLR 2026 — **Fixing the Broken Compass: Diagnosing and Improving Inference-Time Reward Modeling**

共同结构：

> 不是凭直觉换 loss。
>
> 先证明 / 实证现有 score、advantage、reward 或 selection criterion 在某个 regime 下系统性偏。
>
> → 方法就是对这个偏差做最小修正。

---

### D. Train–test mismatch / hidden bias → plug-and-play correction

CV / diffusion 中非常常见，也非常值得迁移：

- CVPR 2026 — **Elucidating the SNR-t Bias of Diffusion Probabilistic Models**
- ICLR 2026 — **Diagnosing and Improving Diffusion Models by Estimating the Optimal Loss Value**
- CVPR 2026 — **Denoising, Fast and Slow: Difficulty-Aware Adaptive Sampling for Image Generation**

共同结构：

> 训练时成立的假设在推理时被破坏，或 training metric 混合了不可约项。
>
> → 先把 mismatch 定义清楚
>
> → 再做非常小的 correction / scheduling / adaptive allocation。

---

### E. Internal structure → useful method, not interpretability for its own sake

典型：

- ICLR 2026 — **Deconstructing Guidance: A Semantic Hierarchy for Precise Diffusion Model Editing**
- ICLR 2026 — **A Hidden Semantic Bottleneck in Conditional Embeddings of Diffusion Transformers**

这里机制分析之所以有价值，不是因为“发现了一个方向”，而是因为：

> 这个内部结构给出了**可以立刻利用的 design primitive**。

这正是本路线更喜欢的 interpretability。

---

# 7. 与 ssn-taste 最重要的融合

保留：

- nearest-prior deep audit；
- reviewer compression；
- 不做 old problem + new model；
- 不做 benchmark / dataset 本身；
- 不把 method 名字当 novelty；
- data / compute feasibility；
- kill experiment explosion；
- 不从 recent paper future work 原句直接长题；
- 不用复杂术语掩盖普通问题。

放宽：

- 不再要求“所有 possible worlds 都能独立撑起论文”；
- 不再要求 opposite/null result 也一定 Main-sized；
- 不再排斥 benchmark gains 作为重要贡献；
- 不再排斥 mechanism follow-up，只要 mechanism **真正改变方法设计**；
- 不再要求 mother question 删除 method 名后仍完全成立；
- 不再把“方法论文”默认视为不够科学。

新增硬门槛：

> **diagnosis 必须对 method 有约束力。**

如果分析完以后，十种完全不同的方法都一样说得通，那么 diagnosis 太弱。

反过来，如果 method 去掉以后，前半篇分析仍然是一篇完整但完全与方法无关的纯机制论文，也要问：

> 我们是不是又滑回了旧路线？

最佳状态是：

> **analysis 和 method 相互需要。**

---

# 8. 默认不追的方向

即使追热点，也不等于什么热点都追。

默认低优先级：

- 重工程 RAG；
- 以 benchmark / dataset 为主贡献；
- 单纯 evaluator / metric；
- 大规模 agentic RL 环境；
- 需要复杂 multi-turn simulator 的 RL；
- 从零发明全新 PPO/GRPO 家族大算法；
- 需要多轮大规模 RL sweep 才能看出方向；
- full pretraining 才能验证的 idea；
- 大 architecture 重构；
- 纯 circuit / head / SAE hunting；
- “我们发现某层有一个 vector，所以 steering 一下”；
- 纯 model-zoo；
- “换 Qwen3 / Llama4 再测一次旧现象”；
- 需要大量闭源 API / judge 才能完成主实验。

---

# 9. 新路线的成功标准

一个 topic 最终值得做 pilot，至少应该有：

1. **Trend relevance**
   - 当前社区真实在做；
   - 有强 baseline、现成 benchmark、代码和生态。

2. **Concrete pain**
   - 不是泛泛“性能还不够”；
   - 有一个能被局部测量的 failure / inefficiency / bias。

3. **Diagnostic handle**
   - 有低成本实验能先确认这个 failure；
   - 最好能定位到 step / token / sample / layer / stage / state / distribution / estimator。

4. **Mechanism-to-method link**
   - 分析结果明确约束方法设计。

5. **Small intervention**
   - 最好是 loss weighting、sampling、routing、filtering、credit assignment、adaptive compute、轻量 representation intervention；
   - 而不是重写整个系统。

6. **Benchmark path**
   - 已有标准 benchmark；
   - 不需要先造一个大 dataset 才能证明方法有效。

7. **Compute path**
   - pilot 可以小模型 / 小数据 / 少步数判断方向；
   - full story 不依赖无限 recipe sweep。

8. **Ablation closure**
   - 能证明不是“模块堆多了所以涨”。

---

# 10. 下一步

用户通过本目录的 taste / workflow 以后，才进入真正找题阶段。

下一阶段不是一次 dump 20 个 brainstorm，而是：

> broad scan → pressure/failure mining → lock one trend → reproduce diagnosis cheaply → nearest-prior audit → method sketch → compute audit → **PILOT-AUTHORIZED or KILL**

候选编号建议使用独立序列：

> **CT01, CT02, ...**

避免和 `ssn-taste/Sxx` 混淆。

正式流程见：

- `SEARCH_GUIDE_ZH.md`
- `PAPER_AUTOPSIES_2026-09-19.md`
- `LESSONS_FROM_SSN_TASTE.md`
