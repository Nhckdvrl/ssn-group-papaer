# 下一轮 Sasano-Taste 科研选题搜索启动提示词

当前日期：2026-09-16。

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste` 的下一轮 NLP/LLM 科研选题搜索。

目标会议：**ACL / EMNLP / NAACL Main**。

辅助校准：**TACL / ICLR / ICML / NeurIPS**。

**EACL / AACL / Findings / workshop / arXiv 只用于查重、nearest-prior、novelty collision；不能作为正向选题 taste。** Best/Outstanding 论文可以帮助校准 taste，但绝不能变成 Main 选题的生死阈值。

当前正式状态：**0 个 selected topic**。这是允许的。不要为了有 survivor 而降低 novelty 或 scope 标准。

---

## 一、最高优先级：先对齐 Sasano，再对齐 ACL/EMNLP/NAACL Main

不要把 Sasano taste 简化成“喜欢机制”或“喜欢语言学”。从 Slack 已确认的正负例看，更稳定的共同点是：

> **问题本身容易理解、自然值得问；与 nearest prior 的差异真实；实验直接回答问题；claim 不超过 evidence。**

关键锚点：

- **Sato**：最强正例。真正值得学的是“人人能懂的 puzzle → 明确科学对象 → 控制实验排除来源/解释”的找题方法，而不是见到任何现象都问“来源是什么”。
- **Guo**：最强负例。Sasano 明确指出“先行研究との差が小さい”。`旧问题 + 新模型` 通常不够；除非模型/数据/前提发生了足以改变结论的实质变化。
- **Hamdi**：top conference 的 Introduction 要让平均 reviewer 觉得“纳得 + 有意思”；RQ 与 finding 清晰对应；结果和预期不同也可以有价值；不要为了机制而机制。
- **Utami**：现实技术/社会环境变化可以产生新问题，但要是一个明确变化 + 一个可解释后果，不是泛泛“LLM 改变语言”。
- **Kisako / Tsukagoshi**：不要求深机制。围绕同一个实际资源目标，两个成熟操作之间的系统 trade-off / interaction 也可以是好研究。
- **Oshika**：成熟 workflow 中，如果前后两侧都已有研究，但一个独立必要的中间决策一直被 human/gold/oracle 给定，这个 missing step 可以成为独立问题。
- **Youchi / Yano**：不要机械认为“有相似 prior 就死”。如果已有方法/问题 formulation 有一个明确、重要、真正该改的结构性缺陷，改进也可以成为研究主题。

---

## 二、上一轮最大的流程错误：禁止再次滑回去

上一轮反复滑回：

> **Main 论文先发现母现象 → 找它没有解释完的 why / mechanism / boundary condition → 当成新题。**

这条路已经反复失败。母现象一旦够重要，它的 mechanism、boundary、source、representation、training explanation 往往已经被原论文、同期工作或紧随其后的工作占满；即使 exact experiment 没人做，reviewer 也会压成普通 successor/follow-up。

以后对这种 seed 先做：

> **Remove-the-trigger-paper test：如果启发这个 idea 的那篇新论文不存在，这个科学问题还会不会因为独立理论、现实变化、方法缺陷、workflow、measurement assumption、resource trade-off 而自然出现？**

如果不会，默认降级，不要花大量时间救。

但不要过度矫正成“所有 successor 都杀”。合法 successor 必须是：

> **已有 formulation/method 有 load-bearing assumption 或结构性缺陷；修正后会改变科学推断、研究对象或实际能力。**

而不是：

> “他们发现 X，我们解释 X / 多做一个边界 / 换新模型 / 做更干净的 ablation。”

---

## 三、题材约束：不要追热点

**不要默认去 RL-for-reasoning、generic agent/tool-use、多智能体等热点池找题。** 上一轮多次跑偏就是因为这些文献显眼、容易产 seed，而不是因为它们最符合 Sasano。

优先搜索即使热点消失仍然成立的对象：

- language understanding / model knowledge；
- 简单、易解释的 semantics/pragmatics（不要重语言学）；
- representation / readout / generation behavior；
- evaluation / measurement validity；
- embedding / representation compression / systematic trade-off；
- multilingual / language variation，但必须有新 scientific distinction，不能只是 benchmark；
- real-world language change；
- text generation / human communication；
- 传统 NLP workflow 中被默认给定的独立 decision；
- 旧科学问题因现代模型提供新 identifying operation 而真正变得可区分。

用户个人偏好：**不喜欢 benchmark-centric，不喜欢难造数据，不喜欢复杂语言学；喜欢问题简单、实验干净、数据自然、初期成本低。**

---

## 四、什么才算我们要的好题

一个值得认真留下的题，至少要同时满足以下核心性质：

1. **一句话能讲清楚为什么值得知道。** 不需要复杂 framing 才显得重要。
2. **有独立问题来源。** 不是依赖某篇新论文的 future work 才存在。
3. **novelty 看 reviewer compression，不看 exact keyword gap。** 必须问：ACL/EMNLP/NAACL reviewer 会把它归进哪个 parent literature？
4. **RQ / claim / Related Work 宽度正确。** 不是“越宽越好”或“越窄越安全”，而是和附近 Main 论文 Introduction-level question 同一个抽象层级。
5. **实验直接识别目标量。** 简单 controlled experiment 优于复杂方法堆叠。
6. **硕士可做。** 优先已有/自然数据、小规模 inference 或轻量训练；不要在 RQ 尚未确认前先造大 benchmark 或大规模 pretraining。
7. **claim 与 evidence 对齐。** 描述型/systematic paper 也允许；机制不是入场券。
8. **不要纯赌 anomaly。** 探究型问题可以不知道答案，但不能只有出现一个怪现象时才有 paper value。

注意：**简单问题不等于弱问题。** EMNLP 2025 `Flaw or Artifact?` 和 NAACL 2025 MORCELA 都是在挑战一个 load-bearing evaluation assumption；问题本身并不花哨，但一旦 assumption 错了，会改变已有科学结论。这是值得学习的 Main-level taste。

---

## 五、优先使用的 idea provenance

不要机械照列表生成，要用真实论文持续修正；但以下是当前高优先级来源：

### A. Load-bearing assumption / measurement validity
已有大量论文依赖一个 measurement、linking function、normalization、aggregation 或 evaluation assumption。如果 assumption 错了，会改变 effect、ranking 或结论。

### B. Changed premise / changed population
旧问题的关键前提真的变了，所以旧答案不能直接外推。`new model` 本身不是 changed premise。

### C. Hidden oracle / missing independent workflow decision
pipeline 中一个必要中间 decision 一直被 human/gold 给定，而且 Main 工作尚未真正把它作为独立变量研究。

### D. Same objective / resource, different mature operations
两个成熟方法都在优化同一个自然资源量，但社区没有在同一资源单位下理解它们的差别、interaction 或 budget allocation。Kisako-style。

### E. Existing method 的结构性缺陷
已有工作可以很近，但缺陷必须改变 inference/validity/usefulness，而不是“我们实验更全面”。

### F. Old debate + new identifying operation
现代模型提供以前没有的干预/观测手段，使旧理论第一次能被真正区分。不能只是把经典 psycholinguistic task 搬到 LLM。

### G. Cross-lineage collision
两个成熟 literature 对同一个 quantity 有冲突 assumption，交叉后产生一个新的可测 quantity / prediction。`Paper A + Paper B` 本身不算 idea。

---

## 六、下一轮实际搜索流程——保持轻量，不要再堆 gate

### 1. 每一大批搜索前先重新校准

重新看几条 Sasano Slack 原话/学生案例；同时抽样几篇近期 **ACL/EMNLP/NAACL Main** 的普通强论文，不只看 Best/Outstanding。

重点读 **Introduction + Related Work**：

- 这篇论文的问题到底从哪里来的？
- 它的 parent RQ 有多宽？
- 它如何说明 nearest prior 不够？
- 实验宽度和 claim 宽度如何匹配？

### 2. 先找 scientific pressure / raw RQ，不要先写完整 paper story

不要一出现 seed 就设计机制、训练方法、五个实验。先确认问题值得问、来源独立。

### 3. 早做 parent-level novelty collision

对 promising seed 广泛搜索 ACL Anthology / arXiv / web，并实际读 nearest papers 的 Intro / Related Work。

问：

- prior 已经拥有的 parent 是什么？
- reviewer 会如何一句话压缩我们的工作？
- 我们是新 scientific question / structural defect，还是只是一个 cell、model、language、dataset、mechanism follow-up？

**EACL/AACL/Findings/arXiv 可以把题撞死，但不能成为正向 taste。**

### 4. 做 scope + Sasano audit

至少拿几篇附近 ACL/EMNLP/NAACL Main 和 Sasano anchor 对比：

- RQ 是否处于相似抽象层级？
- Related Work 是否自然？
- 是不是靠把一个小 cell 包装成大 parent 才显得新？
- 是不是为了热点而做？

### 5. 过了以上再设计 minimum experiment

只设计最便宜、最能区分核心问题的实验。不要一开始做 benchmark/data project。

### 6. 持续记账

- serious but dead -> `ssn-taste/FAILED_TOPICS.md`
- 真正通过 novelty + scope + Sasano fit -> `ssn-taste/SELECTED_TOPICS.md`

当前 selected = **0**，允许保持 0。

---

## 七、必须定期做“搜索偏航检查”

上一轮最大的问题是注意力逐渐漂移，所以这一条很重要。

大约每认真检查 8–12 个 seed，或连续几个 idea 都来自同一热点时，暂停生成，检查：

1. 最近这些 idea 都从哪里来的？
2. 是否又出现大量 `Main mother phenomenon -> why/mechanism/boundary`？如果是，立刻换 generator。
3. 是否又因为 RL/agent/tool-use 热而不断往那里搜？如果是，离开该领域。
4. 是否把 EACL/AACL/Findings/arXiv 当成了正向 taste？纠正。
5. 是否只查 exact gap，没有看 reviewer-level parent？
6. 是否又开始造 benchmark / 难数据？
7. RQ 宽度是否仍对齐真实 Main Introduction？
8. 重新读至少一条 Sasano 原话 + 一篇强 Main 的 Introduction/Related Work，再继续。

**如果连续很多 seed 因同一种原因死亡，不要降低标准，也不要继续把 parent 越缩越细；说明 idea generator 出问题了，应该换 scientific object / provenance。**

同时，不要机械服从这份 prompt。如果大量优秀 Main 论文显示我们的搜题流程本身有偏差，要主动修改流程并说明原因。

---

## 八、明确禁止的常见坏路

- Main 母现象 -> 没解释完的 why/mechanism/boundary；
- 旧问题 + 最新模型；
- known capability 再造一个 benchmark；
- `别人做 behavior，我们做 probing/mechanism` 当 novelty；
- occupied parent 里换语言/模型/数据集；
- 先发明 `X ≠ Y` 口号，再强行找 scientific object；
- 对所有探索题都套 anomaly robustness / why-space / belief-update / MDE 等重 gate；
- 默认追 RL/agent/post-training 热点；
- 强迫所有题有深机制；
- 用 Best Paper 标准杀普通 Main-level 好题；
- 用 EACL/AACL 的接受风格决定我们喜欢什么；
- exact cell 其实很窄，却靠 rhetoric 把 parent 说大。

---

## 九、上一轮状态与防复活

必须先阅读：

- `ssn-taste/README.md`
- `ssn-taste/FAILED_TOPICS.md`
- `ssn-taste/SELECTED_TOPICS.md`
- 老的 `failed/` ledger

已明确不应继续换皮的方向包括：

- post-training uncertainty: latent vs readout；
- message/turn serialization neutrality；
- API/tool optional/default semantics；
- timeout/idempotency recovery；
- SFT response-length implicit weighting；
- broad cross-lingual transfer/shared-representation origin；
- typo/noise robustness source/mechanism；
- reasoning-control degradation mechanism；
- Writing-RL long-output -> long-input why；
- proxy predictive fidelity vs causal/interventional fidelity；
- absence/unknown vs false/closed-world parent；
- PRM step segmentation sensitivity；
- grammar-constrained decoding semantic neutrality；
- self-generated memory vs external evidence / reality monitoring；
- factuality claim decomposition granularity；
- fixed rollout budget / same-temperature-as-same-exploration；
- generic agent success-vs-trajectory-length measurement。

不要通过换名字复活。

当前只有两个 **raw pressure，不是 candidate**：

- cross-model token entropy comparability：只有证明它会改变已有 scientific conclusion/ranking 才值得继续，否则只是 metric 常识；
- LLM 写作辅助普及后，同一真实作者 idiolect 是否纵向减弱：Utami-like，但目前 causal identification 很弱，可直接放弃。

不要继承它们为 survivor。

---

## 十、下一轮的输出方式

**直接搜题，不要再让我先选抽象 territory。**

只有出现实质进展时简短汇报：

- 一个真正新的 scientific pressure；
- 一个 decisive collision；
- 一个搜索流程纠偏；
- 一个真正 survivor。

对 serious candidate，至少讲清：

1. 一句话 RQ；
2. idea provenance；
3. 为什么符合 Sasano；
4. ACL/EMNLP/NAACL Main 的 scope / Related Work 对齐；
5. nearest prior 和真正 novelty；
6. 最小实验、数据、算力；
7. 最大风险。

不要拿一堆弱 seed 来凑数量。连续杀题完全可以，0 survivor 也完全可以。

**最终目标不是“完成提示词流程”，而是找到：经过真实文献阅读后，确实像 Sasano 会愿意指导、也像 ACL / EMNLP / NAACL Main 会认真审的 research question。**
