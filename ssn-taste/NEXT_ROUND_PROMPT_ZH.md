# 下一轮科研选题搜索启动提示词 — 2026-09-17 Late

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste` 的下一轮科研选题搜索。

目标会议：**ACL / EMNLP / NAACL Main**；同时用 **ICLR / ICML / NeurIPS / TACL** 校准科学问题与机制研究 taste。CVPR / ICCV / ECCV、speech/audio、multimodal、general ML，以及认知科学、统计、信息论、控制、动力系统等领域都可以作为 idea provenance，但最好**从真实论文出发**，不要只搬一个概念名词。

## 0. 开始前必须先读

先读：
- `ssn-taste/README.md`
- `ssn-taste/SELECTED_TOPICS.md`
- **全部** `ssn-taste/FAILED_TOPICS*.md`
- 必要时读对应 topic 文件与最近 commits

当前 repo 的正式状态以文件为准。`SELECTED_TOPICS.md` 当前正式 selected 是 **S03 — From Document End to Task Done**。这一轮任务不是推进 S03，而是继续寻找**新的、彼此独立的 scientific question**。

极其重要：repo 中我们自己提出的 selected / active / serious / killed topics **都不是正向 research-taste exemplars**。它们只能用于：避免复活失败题、学习搜索流程失败、检查已有实验资产。不要因为新题“像 S03 / 某个 survivor”就给它加分。

---

# 1. 正向 research taste 只有两个主要来源

### A. Sasano 的真实判断
持续读 Slack 中 Sasano 对真实学生课题/论文的评价：他为什么觉得某问题有意思、为什么觉得 finding 不意外、为什么认为与先行研究差太小、怎样修改 RQ、怎样从平均 reviewer 角度组织 Introduction。

不要把 Sasano taste 压成一次性 checklist。每轮都要重新读真实案例。

### B. 真正优秀的 Main papers
持续抽样 ACL / EMNLP / NAACL Main，同时参考 ICLR / ICML / NeurIPS。不要只看 Best Paper，也要看普通强 Main；不要长期只看 RL / reasoning / agents / post-training。

重点研究：
- 为什么这个问题在方法出现以前就值得问？
- Introduction 第一页制造了什么 scientific pressure？
- nearest prior 为什么没有拥有同一个母问题？
- 核心实验区分了哪些世界？
- 如果结果方向相反，论文是否仍然有科学意义？
- 去掉 benchmark / model / method 名字以后，我们到底新知道了什么？

---

# 2. 用户真正偏好的题

用户广义上感兴趣：**理解、生成、可解释性、representation / computation、学习与训练机制、多模态 / vision / video / speech 中可迁移的机制问题**。

但：
- **不喜欢复杂、费劲的语言学小现象。** coercion、presupposition、indexical、复杂 scope、dynamic semantics、garden-path 等不能再成为默认搜题池。除非母问题一句话就能懂、非常 broad，语言学只是一种干净实验载体。
- 不做 RAG、benchmark、metric、robustness leaderboard、主要靠造数据集的题。
- 不喜欢“方法类刷分刷点”。
- 更喜欢机制 / 解释型问题，但**机制不是题目存在的理由**。先有值得问的行为/学习/computation 问题，mechanistic analysis 才有意义。
- 允许最终 0 survivor；绝不能为了产出降低标准。

---

# 3. 可解释性必须特别对齐 Hakaze Cho / Zhao 的研究方式

学习的是他的**出题与解释结构**，不是照抄 ICL / attention head / subspace 题材。

核心路线：

> **Representation → Computation / Transformation → Circuit / Component → Causal Mechanism → Controllability**

具体要学：
1. 不满足于“某层可 probe 到 X”。先找模型内部**到底组织了什么 representation structure**。
2. 不停在“head X 很重要”。问 hidden state 从 `h_l` 到 `h_{l+1}` **究竟发生了什么 transformation**。
3. 尽量把零散 component-level 现象统一到更高层 computation，例如 separability / alignment / rotation / filtering，而不是再发现一个 head。
4. 最好的题常来自**旧解释解释不了的边界条件**，从而迫使我们换 computational primitive。Information Removal 的价值就在于不继续补“copy/add information”故事，而是用旧故事无法解释的 case 引出 `remove/filter irrelevant information`。
5. 必须有 intervention / ablation / steering / patching 等因果验证；correlation/probe 只能做前置证据。
6. 如果 mechanism 真的理解了，可以进一步问能否用这个 mechanism 控制行为；但 controllability 是结果，不是为了应用而硬加 module。

禁止把 Zhao-style 误读成：
- “找到一个 attention head”；
- “画 hidden-state PCA”；
- “probe 某层信息”；
- “再做一个 steering vector”；
- “已有 anomaly + mechanistic follow-up”。

Zhao-style 的真正要求是：**一个强 mother question + competing computational explanations + representation dynamics + causal intervention。**

---

# 4. 这轮流程暴露出的主要错误，下一轮必须主动防止

### 错误 1：跨领域“搬概念”，而不是搬 prediction
latent inhibition、symmetry breaking、prototype/exemplar、iterated learning、efference copy 等概念一旦落到 LLM，常常已经有对应 parent，或者只是换名字。

**纠偏：** 外部理论只有在它能事前给出新的、可区分的 prediction 时才有价值。最好从真实 CV/ML/认知论文出发，学它如何制造科学压力。

### 错误 2：过度迷恋架构小谜题
LayerNorm 如何表示 confidence、weight tying 如何连接 input/output、append-only KV 如何撤回内容，这些可以很漂亮，但“mechanistically tractable”不等于“Main-level important”。

**纠偏：** 先问：如果完全不知道它的机制，平均 reviewer 会真的想知道答案吗？如果 mother question 不强，漂亮 circuit 不能救。

### 错误 3：追成熟论文刚暴露的 anomaly
这是过去最失败的路线：异常可能复现不了；即使真实，作者/后续工作往往已把解释空间吃掉。

**纠偏：** 优先从开放科学问题、理论冲突、功能必要性、训练/架构事实出发。若启发来自 recent anomaly，做 `remove-the-trigger-paper test`：那篇论文消失后，这个问题是否仍然自然存在？

### 错误 4：发现相似论文就只做 KILL，没有学习它怎么长大

**纠偏：** 每次 collision 后记录一个 `growth lesson`：初级 idea 如何被论文升级成 mother question？它怎样从 observation 变成 competing explanations？用了什么反向 prediction / non-monotonic law / minimal system / causal intervention？然后把**成长动作**带到新题，而不是复活旧题。

### 错误 5：把可解释性变成工具清单
probe / SAE / activation patching / ablation / steering 不是 scientific question。

**纠偏：** 先写 computation：模型必须完成 A/B/C 中哪一种内部操作？再决定什么工具能区分它们。

### 错误 6：同一个 generator 连续使用太久
这一轮曾连续掉进语言学 distinction、认知效应、架构 paradox、cross-modal analogy 等局部舒适区。

**纠偏：** 约每 **8–12 个 serious seed** 强制停下重新校准；若更早出现同质化，也立即停。

---

# 5. 下一轮的搜索面必须主动轮换

至少在这些来源之间轮换，不要长期停在一个子领域：
- understanding / representation / world or task state；
- generation dynamics / generative models；
- Zhao-style mechanistic interpretability；
- training / learning dynamics / acquisition；
- CV / image generation / video / multimodal；
- speech/audio（只要问题 broad，不陷入 tokenizer/ASR 细节）；
- general ML / optimization / representation learning；
- cognition / neuroscience；
- statistics / information theory / control / dynamical systems。

但是**不要强行把外域问题映射成“LLM 版”**。跨域最有价值的东西是：
- 新的 competing explanations；
- 一条可验证的 law / shape；
- 一个最小系统；
- 一个结构性矛盾；
- 一个理论上必须存在的 latent variable；
- 一个 intervention 可以让两个解释产生反向预测。

---

# 6. 高效搜题流程

## Phase A — Fresh calibration
每轮开始先读一小批新鲜 Main / ICLR / ICML / NeurIPS papers + Sasano Slack，不要直接生成题。

## Phase B — 产生 seed，但先做超便宜 parent collision
每个 seed 先写：
- 一句话 RQ；
- 为什么问题在实验前就存在；
- 2–3 个 competing explanations；
- 哪个结果会改变我们对模型的理解。

然后立即搜 parent-level nearest prior。不要先设计一堆实验再发现母问题被占。

## Phase C — 一次只深审一个最强 seed
有一个明显更强就停止发散。完整检查：
- reviewer compression；
- nearest-prior ownership；
- remove-trigger-paper test；
- 是否只是 `old question + new model/modality/condition`；
- 是否只是成熟 behavioral anomaly 后补 mechanism；
- 是否需要复杂语言学/大量数据才能讲清；
- identification 是否真的能区分解释。

深审完只能给两个结果：**SURVIVE / KILL**。不要给用户半成品。

## Phase D — Similar paper 出现时先学习，再 kill
如果论文已经覆盖：
1. 先明确它如何从初级 idea 发展成完整论文；
2. 提炼 `growth lesson`；
3. 再写进 `FAILED_TOPICS*.md`，包括 revival condition；
4. 不要围着它继续找很窄 follow-up。

## Phase E — 只有过完 novelty/importance 才设计 pilot
最小 pilot 不是为了证明预设 anomaly，而是**把可能世界分开**。最好 A/B/C 任意结果都回答同一个母问题。

---

# 7. 候选进入 SERIOUS / PILOT-AUTHORIZED 的硬门槛

必须同时满足：

1. **一句话值得问。** 不靠 elaborate rhetoric 才显得重要。
2. **问题先于方法存在。** 去掉具体 model / benchmark / interpretability tool 仍成立。
3. **不是复杂语言学小题。** 普通 ML/NLP reviewer 可以快速理解 scientific pressure。
4. **不是成熟 anomaly follow-up。** recent paper 消失后问题仍自然存在。
5. **parent-level novelty 真存在。** reviewer 不能一句话压成已有 parent + 新模型/新条件/更深机制。
6. **有 competing explanations。** 至少两个自然世界会导致不同 prediction；不是只赌一个漂亮现象出现。
7. **actual experiment 是科学实验，不是 evaluation。** 去掉 metric/benchmark 名称后仍能说出发现了什么规律或机制。
8. **识别逻辑干净。** intervention 真能区分 explanation，而不是 context confound / probe artifact / distribution shift。
9. **可解释性题额外要求 Zhao-chain。** 至少能讲清：representation structure → transformation/computation → component → causal intervention；只找 feature/head 不过关。
10. **初期可做。** 一个小模型/少量 controlled data/公开 checkpoint 就能做高信息量 pilot；不先大规模训练/标注。

---

# 8. 强制重校准触发器

不必等满 8–12 个 seed。出现任一现象立即停下重新读 Sasano + Main papers：
- 连续几题来自同一 literature；
- 每个 idea 都变成“某 recent paper 没做的下一步”；
- mechanism 越来越复杂，而母问题越来越难一句话说；
- 又开始做 benchmark / robustness / metric；
- 又回到复杂语言学小现象；
- 又连续找 RL / reasoning / agent 热点；
- 一直在找 head / vector / probe，而没有 computation；
- cross-domain idea 只剩“X 在 CV 有，所以问 LLM 有没有 X”；
- novelty 只能靠 exact cell，而不是 parent RQ。

这时允许**推翻当前 generator**，不要机械遵守旧提示词。

---

# 9. 当前状态与禁止复活

正式状态以 repo 为准：当前 selected topic 是 S03；本轮继续找新的 independent topic，不以 S03 风格为模板。

必须先读全部 `FAILED_TOPICS*.md`。截至当前，durable kill ledger 已经覆盖大量路线，包括：复杂语义/语言学、memory/forgetting、source memory、mutual exclusivity、latent tokenization、retraction/repair、prototype/exemplar、ambiguity posterior、representational drift、prospective obligations、copy-vs-recompute、DLM coarse-to-fine、reachability/steerability、negative constraints、fast/slow memory、sampling uncertainty、branch awareness、trajectory attractors、weight tying、closed-loop generation、LayerNorm/confidence、implicit reward、ICL-vs-SFT computation、VLM routing、object permanence、speech timescale disentanglement、causal-state induction、video intention、audio feature routing、semantic commutativity 等。

**这些 kill 是排除项，不是 taste exemplars。不要因为要“换一点条件”就复活。**

当前还有一个 `UID online regulation` 只属于 **SERIOUS SEED / NOT PILOT-AUTHORIZED**：它的核心识别问题是无法干净区分 active compensation 与普通 conditional-distribution narrowing。可以重新审，但不能默认推进；如果解决不了识别，继续 kill。

---

# 10. 最终输出纪律

用户不要看几十个半成品。

你可以内部大量搜索、杀很多 seed，但对用户：
- 没有完整过关题：直接说这一轮 0 survivor，并说明最重要的 kill / growth lessons；
- 有题：只在完整审完以后给出。

一个真正交付的 survivor 至少要包含：
- 一句话 mother question；
- 为什么它值得 Main reviewer 关心；
- 独立 scientific pressure；
- competing explanations / possible worlds；
- nearest prior 与明确 ownership boundary；
- 如果是可解释性题：Zhao-style representation → computation → causal mechanism 路径；
- 最小 identification experiment；
- 多种结果分别意味着什么；
- kill conditions；
- 为什么不是 benchmark / method / mature follow-up。

**允许长期 0 survivor。好题很稀缺不是流程失败；真正的流程失败是为了留下题而降低标准，或者搜索慢慢滑回我们已经知道不喜欢的题型。**

现在开始下一轮搜索。提示词只是最低纪律，不是固定算法；必须在搜索过程中不断用 Sasano 的真实判断和新的强 Main papers重新学习 research taste，并在必要时主动修改自己的 search process。