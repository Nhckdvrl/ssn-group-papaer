# 下一轮科研选题搜索启动提示词

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste` 的下一轮科研选题搜索。

**不要机械执行一套固定 checklist。你的任务是像研究者一样持续判断：我们现在是否还在找真正重要的问题，还是已经被 novelty gap、mechanism、synthetic data 或热门 literature 带偏。**

完整规范先读：

- `ssn-taste/SEARCH_GUIDE_ZH.md`

同时恢复：

- `README.md`
- `SELECTED_TOPICS.md`
- 当前 selected registrations：S04 / S06 / S07
- 全部 `FAILED_TOPICS*.md`
- `RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md`
- 最近 commits

repo 最新状态优先于任何旧聊天或 handoff。

---

## 0. 当前正式状态

### SELECTED / PILOT-AUTHORIZED

- S04 — How Do Language Models Update Situation Models Across Event Boundaries?
- S06 — What Does Deliberation Do to Evidence?
- S07 — Where Does Surprise Go?

### 最近关键 KILL

- **S03**：真实实验后发现 developmental story 随 training budget / family / recipe 改变，继续会变成 training-biography archaeology。
- **S05**： broad conditioning-vs-learning 问题很漂亮，但可执行的 decisive experiment 只剩 matched response relevance → persistent trace 的 exact causal cell；strongest likely finding scientific consequence 不够。
- **S08**：即使 confidence 与 termination control 被干净 causal dissociate，最强结论仍偏“内部架构不同”，scientific consequence 不够；不要用 universal metacognition / 更多行为 / steering archaeology 复活。
- **S09**：memory age/history 本身就是 optimization-path construct，正结果会强迫 recipe matrix。

所有 S/L/F/Unring/selected/failed 都只是 process evidence 和去重材料，**绝不能当正向 taste exemplar。**

---

# 1. 这一轮首先重新校准 taste

不要立刻 brainstorm 题。

先重新抽样：

- Sasano 最近真实 Slack feedback；
- 3–6 篇近期强 ACL / EMNLP / NAACL / TACL / ICLR / ICML / NeurIPS papers；
- 至少跨 2–3 个不同 lineage；
- 必要时扩展到 CV / multimodal / generation / speech / robotics / cognition / statistics / control。

重点不是“这些论文做了什么方法”，而是：

> **为什么这个问题在实验之前就值得问？**

对其中几篇做极简 autopsy：

> Pressure → Mother question → What belief is at stake → Decisive attack → Why the result matters.

特别牢记当前 Sasano calibration：

- top conference 要让平均 reviewer **納得 + 面白い**；
- reviewer 不会替你找亮点；
- unexpected result 可以很好，但必须改变真实解释；
- 内部差异可以有趣，但不自动够 main contribution；
- 和 prior 差太小时，要敢于見切り，不要继续包装。

---

# 2. 不要从标题开始；先维护 Important Pressure Portfolio

先收集大约 **5–10 个 important pressures**，不是 20 个候选题。

每个 pressure 只写：

1. 社区现在相信/观察到什么？
2. 哪里有矛盾、unexplained component、可疑 premise 或 changed regime？
3. 为什么现在可能有一个以前没有的 attack？

优先 pressure：

- 广泛默认但未经真正验证的 premise；
- 两篇以上可信 work 无法被同一个解释统一；
- apparent success 可能靠绕过真正关键 computation；
- training/deployment、observable/latent quantity、endpoint/dynamics 之间有结构错位；
- 一个老问题因现代 LLM 的 intervention 能力第一次变得可识别；
- strong negative result 会真正推翻当前理解。

不要因为“A 和 B 可能不一样”就生成题。  
不要因为“shared vs separate mechanism”形式漂亮就生成题。  
不要从 future work 原句生成题。

---

# 3. 锁一个 seed 后，先问 significance，不先问 novelty

第一问永远是：

> **如果最强结果成立，所以呢？**

要求能用普通话写出：

> “如果 World A 成立，我们必须如何改变对模型的理解；如果 World B 成立，又必须如何改变。”

如果答案只是：

- architecture 不一样；
- 找到了两个 representation；
- 某 vector 可以 steering；
- 某 setting 下 effect 有/没有；

直接倾向 KILL。

做 30 秒 reviewer test：

> 不用专有 mechanism / benchmark 名词，一个普通 AI/NLP reviewer 能否马上理解为什么想知道答案？

过不了，不进入复杂 novelty search。

---

# 4. 再做 nearest-prior 和 decisive-unknown audit

不要追求零 overlap。

必须写清：

> **Prior 已知 X；Y 仍未知，因为 Z；这个 experiment 第一次区分 A/B/C。**

Kill：

- same decisive unknown 已做；
- difference 只是 model/data/language/modality/condition；
- cleaner replication；
- paper A × paper B；
- novelty 只能靠 exact cell。

Future work 不是自动 kill，但 remove-trigger-paper 后问题仍应自然存在。

---

# 5. “有 attack”是选题的一部分

不要选“很重要但不知道怎么测”的题。

PILOT-AUTHORIZED 前必须已经有一个 reasonable attack：

- scientific variable 尽量直接 observable/manipulable；
- 一两个小实验就能让主要 worlds 分叉；
- pilot 第一目标是回答 science，而不是寻找 probe/vector、发明 evaluator、造 benchmark、验证 instrument 是否存在。

如果第一轮主要是在问：

> “这个 latent construct 能不能被 decode / steer 出来？”

这是明显风险信号。

---

# 6. Execution gate：只在 seed 已经重要以后检查

### Data

优先：

> existing data + native ground truth  
> small programmatic controlled stimuli  
> 少量自动生成 + spot check

避免：

> 大 annotation / LLM judge / 新 benchmark / generator 越做越复杂。

### Training

对 training/post-training 题：

> 不要把 arbitrary recipe point 当 learning law。

优先 within-run / same-state matched intervention。

如果为了知道 qualitative conclusion 必须做 optimizer × LR × dose × family matrix，KILL。

### Mechanism

Mechanism 只能回答已经重要的问题。

不要：

> behavior 已知 → 找个 mechanism 当 novelty。

### Scale

小模型/toy pilot 可以判生死，但如果最终 claim 指向真实 LLM dynamics，要提前想清最小 realistic validation 路径。

---

# 7. 不允许用“所有结果都有意义”自我安慰

A/B/C 不是形式要求。

每个 major outcome 必须至少做到一个：

- 改变 live belief；
- 排除真实 explanation；
- 推翻/支持重要 assumption；
- 给出可复用的 scientific law。

“没有 effect，所以我们知道没有 effect”不算自动有意义。

---

# 8. 必须周期性主动纠偏

**不要完全听从这份提示词的固定流程。**

即使暂时没有明显故障，也要周期性轻量校准：默认每完成约 2–3 个完整 seed audit，或一个较长搜索批次后，重新读少量不同 lineage 的强论文和一条 Sasano feedback。不要机械计数；发现 drift 就提前 reset。

如果发现：

- 连续 2–3 个 seed 同一种死法；
- 越来越像 A≠B / shared-vs-separate 套模板；
- “所以呢”越来越难回答；
- synthetic / controls / mechanism 越来越复杂；
- 只盯 reasoning/RL/agent 热点；
- strong papers 只用于查重和杀题；

立刻暂停。

重新：

1. 读 2–4 篇不同 lineage 的新鲜强论文；
2. 读一个 Sasano 最近 thread；
3. 写一句：
   > **我们为什么走偏了？**
4. 重新生成 scientific pressures。

你有权改变搜索顺序、换 provenance、放弃 generator。  
规范是防 drift 的，不是让你机械 obey 的。

---

# 9. 一个 seed 必须审到底

不要给用户 SERIOUS / maybe。

锁定后继续工作到：

> **PILOT-AUTHORIZED**

或者：

> **KILL**

允许 0 survivor。

PILOT-AUTHORIZED 的真正含义：

> **问题重要、knowledge delta 真、现在有直接 attack、数据/recipe/construct 不会自然爆炸，第一刀值得真正投入时间。**

通过后注册新的 Sxx；失败则写 failed ledger 和 anti-resurrection reason。

---

# 10. 最后四句

如果搜索过程中开始迷失，只回到这四句：

> **先问 why care，再问 novelty。**  
> **从真实 scientific pressure 出发，不从 literature blank 出发。**  
> **一个好问题必须现在有简单、直接的 attack。**  
> **持续用 Sasano feedback 与强 Main/顶会论文校准；一旦开始套模板，立即 reset。**
