# Industry Frontier Scan — 2026-09-19

> **Status: research-taste / direction calibration only.**
>
> 这条轨道与 academic genealogy 并行。
>
> 目的不是：
>
> > 大公司做了 X → 我们也做 X。
>
> 而是：
>
> > **业界拥有学界无法复制的 scale / traffic / infrastructure / multimodal data / agent environments，因此会最早暴露一些“小模型时代不存在或看不见”的 scientific / algorithmic pressure。**
>
> 我们从这些 artifact 中挖：
>
> - 新 regime；
> - 新 bottleneck；
> - 新 system variable；
> - 新 deployment constraint；
> - 新 failure；
> - 新 capability relation；
>
> 再把它们抽象成 **学界可问、我们可低成本验证** 的问题。
>
> 核心桥梁：
>
> > **Industry frontier observation**
> >
> > → **remove proprietary scale**
> >
> > → **identify the load-bearing relation / assumption**
> >
> > → **academic question**
> >
> > → **cheap falsifiable proxy**
>
> 如果这座桥搭不起来：
>
> > 只当 inspiration，不进入 candidate pool。

---

# 1. 为什么业界论文必须单独看

学界与业界并不是简单的：

> 学界更科学，业界更工程。

真正区别是 **可观察 regime 不同**。

大公司可以看到：

- 30T+ token pretraining；
- tens of thousands GPUs；
- trillion-parameter MoE；
- 1M–10M context；
- 真实大规模 agent / tool traffic；
- 数十万/百万环境 rollout；
- 大规模用户切换模型、重试、修改任务的行为信号；
- proprietary multimodal/audio/video data；
- production latency / KV / kernel / networking bottleneck；
- long-running coding/research agents；
- inference cost × quality × latency frontier；
- deployment incidents / rare failures。

其中很多问题：

> 学界并不是“不够聪明所以没研究”。

而是：

> **没有那个 regime，就根本看不到问题。**

所以 industry artifact 对找题最有价值的作用之一是：

> **给我们提前看“下一代 academic question 可能从哪里冒出来”。**

---

# 2. 但 industry artifact 不是 ordinary academic evidence

公司技术报告 / system card / launch blog 有几个常见限制：

- training recipe 未完全披露；
- data 不公开；
- ablation 远少于 academic mechanistic paper；
- benchmark 选择可能服务产品定位；
- internal evaluation 无法复现；
- system stack 与 model weights混在一起；
- 大 scale effect 未证明 small-scale mechanism；
- negative runs / failed iterations 很少公开；
- product claim 与 scientific claim 的证据标准不同。

所以必须分两种用途：

## Frontier evidence

> “这个 regime / bottleneck / capability relation 在 frontier system 中真实存在。”

公司材料非常有价值。

## Mechanistic evidence

> “为什么存在，以及一般规律是什么。”

公司材料通常不够。

因此：

> **Industry report 可以制造 pressure，不能自动完成 explanation。**

---

# 3. Industry artifact taxonomy

以后 industry scan 不只搜 “technical report”。

至少分六种。

## A. Foundation-model technical report

例如：
- DeepSeek-V4 Technical Report
- Qwen3 Technical Report
- Llama 4 release / technical details

最有价值：
- architecture choices；
- training stage变化；
- scale；
- system co-design；
- new regime；
- ablation中真正被认为 load-bearing 的选择。

风险：
- recipe bundle 太大。

---

## B. Model card / system card

例如：
- OpenAI GPT-5.x System Cards
- Gemini model cards
- Anthropic model/system cards

最有价值：
- capability boundary；
- failure categories；
- deployment setting；
- effort / tool / context / modality support；
- external vs internal evaluations；
- product configuration changes。

它们经常比 academic paper 更早告诉我们：

> **下一代系统把什么变量产品化了。**

例如：
- effort level；
- routing；
- parallel test-time compute；
- context management；
- tool autonomy。

---

## C. Production engineering paper

例如：
- production speculative decoding；
- serving / kernel；
- KV cache；
- distributed inference；
- async rollout infrastructure。

最有价值：
> academic FLOPs / algorithmic improvement 到 production 后到底哪里失真。

这类 report 很容易暴露：

> **paper proxy ≠ real system bottleneck。**

---

## D. Product / deployment report

例如：
- coding agent实际工作流；
- deep research；
- context compaction；
- user steering；
- team/subagent orchestration。

最有价值：
> 哪些 capability 被真实用户持续调用，哪里需要人工 intervention。

风险：
> confound极多。

只能作为 pressure source。

---

## E. Real-usage / internal-traffic research

例如：
- aggregate usage statistics；
- internal coding traffic evaluation；
- user model-switch / preference signals。

最有价值：
> benchmark distribution 与真实 task distribution 的差别。

这种数据学界很难触及。

但：
> access通常不可复制。

---

## F. Safety / incident / failure report

公司偶尔会公开：
- tool misuse；
- prompt injection；
- long-horizon failure；
- unexpected autonomy；
- deployment incident。

即使我们不做 safety，
这些 report 也非常适合看：

> **frontier system 的“真实 action space”扩大以后，新 failure unit 是什么。**

---

# 4. 第一批 industry frontier observations

下面不是 topic。
只是建立 industry-reading taste。

---

## I01 — OpenAI GPT-5：router 本身被产品化

GPT-5 system description 不再只是：

> 一个统一模型直接回答所有 query。

公开系统卡描述的是：
- fast model；
- deeper reasoning model；
- realtime router；
- router依据 conversation type / complexity / tool need / explicit intent；
- routing还会利用用户切换模型、preference、measured correctness等真实信号。

### 为什么 academic taste 上有意思

这说明 frontier deployment 已经把：

> **“这道题该花多少 intelligence / compute”**

从 offline benchmark question 变成：

> **online routing policy。**

学界 test-time scaling通常研究：
- sample多少；
- search多久；
- difficulty多少。

产品系统进一步拥有：
- user intent；
- tool requirement；
- interaction history；
- observed correction signals。

### 我们不能机械做

不能：
> 复制 ChatGPT router。

没有真实 traffic。

### 可以抽象出的 pressure

> **compute allocation policy 的 state，在真实系统里比 benchmark difficulty 更丰富。**

未来若要产生 academic question，
必须再找到：
- open-model proxy；
- direct observable state；
- small offline experiment。

否则只做 inspiration。

---

## I02 — OpenAI GPT-5.5 / GPT-5.6：effort / parallel test-time compute 被显式产品化

GPT-5.5 system card公开区分：
- normal model；
- Pro setting；
- Pro 使用 parallel test-time compute。

GPT-5.6又提供：
- Sol；
- Terra；
- Luna；

形成 capability / latency / cost 不同的 family。

### Frontier signal

过去 academic test-time compute 常是：
> 一个 model，调 reasoning length / samples。

产品里已经变成：
> **model selection × effort × parallel compute × latency/cost。**

这说明 inference scaling 的现实 object 已经不是单轴。

### 不能直接迁

我们没有：
- closed model internals；
- product traffic；
- exact router/training recipe。

### Inspiration value

值得持续观察：
> academic literature 是否仍用单一 compute variable 描述一个已经多维化的 deployment problem。

---

## I03 — Anthropic：effort control + context management + long-running agents

Anthropic 的 Opus/Sonnet release materials反复强调：
- effort parameter；
- fewer reasoning tokens for comparable outcomes；
- context compaction；
- advanced tool use；
- long-running coding / knowledge tasks；
- subagent coordination。

Claude Tag一类产品还暴露：
> 模型进入长期团队上下文，而不是单次 benchmark episode。

### Frontier signal

agent quality不再只是：
> one-shot tool success。

还包括：
- when to think；
- context budget management；
- compaction；
- interruption / steering；
- multi-agent delegation；
- long-horizon state preservation。

### Academic abstraction opportunity

不是：
> 做一个 Claude-like agent。

而是问：
> **哪些 state-management decisions 已经成为 agent computation 的一部分，而现有 academic evaluation还把它们当 infrastructure？**

只有能缩成可验证关系时才继续。

---

## I04 — Google Gemini model cards：effort × quality × cost × latency成为正式 model interface

2026 Gemini Flash model cards公开支持：
> customizable effort levels controlling quality / cost / latency tradeoff。

同时新型号覆盖：
- audio live；
- multimodal；
- agentic video understanding；
- robotics embodied reasoning。

### Frontier signal

“reasoning effort”已经从 research trick变成：
> **API-level control variable。**

这意味着未来 academic question可能不只是：
> reasoning多一点有用吗？

而是：
> effort这个 control signal到底在不同 modality/task 中控制了什么 computation？

### 但当前不可直接立题

因为 closed model中的 effort implementation不透明。

需要先在 open model上找到：
> 独立可操作 proxy。

---

## I05 — DeepSeek-V4：long-context 不再只是 context-length benchmark，而是 architecture × system co-design

DeepSeek 2026 官方材料把 V4 的核心目标明确放在：
> **cost-effective million-token context intelligence。**

公开报告/发布材料显示其重点不是单一 benchmark，而包括：
- sparse/compressed attention；
- MoE；
- training optimization；
- long-context extension；
- inference efficiency；
- agentic/coding usage。

### Frontier signal

当 context从：
> 32K/128K → 1M

以后，“long context”不再是：
> position extrapolation单问题。

它同时涉及：
- attention compute；
- KV/storage；
- retrieval/selectivity；
- training curriculum；
- optimizer stability；
- serving；
- agent history。

### Academic lesson

业界大 scale 会把原来分散在不同论文里的问题：
> 绑成一个 real-system bottleneck。

我们不能复制 V4。

但可以问：
> **这些 bundle 中，哪个 relation能在小模型上独立识别？**

---

## I06 — Meta Llama 4：30T-token / 32K-GPU scale 下，architecture hyperparameter transfer 本身变成问题

Meta公开 Llama 4材料包括：
- MoE；
- native multimodal early fusion；
- >30T tokens；
- 32K GPUs；
- FP8；
- mid-training long-context extension；
- MetaP用于跨 batch/width/depth/token transfer关键 hyperparameters；
- Scout 10M context。

### Frontier signal 1：hyperparameter transfer

在学界：
> 一次 training recipe tuning 可能只是实验细节。

在 32K GPU / giant-model setting：
> **每次 retune 都极贵，hyperparameter transferability 本身具有巨大价值。**

这会让：
- scaling-law；
- optimizer parametrization；
- recipe transfer

成为工业优先问题。

### Frontier signal 2：mid-training

pretrain → post-train 的简单两阶段 narrative 已经不够。
frontier models公开出现：
> mid-training / context extension / specialized stages。

这直接支持我们过去从 S03 学到的 warning：

> **现代训练 recipe 根本不是“pretrain→SFT→RL”三个干净 causal stages。**

因此 academic training-dynamics题若把“stage”当自然变量要非常谨慎。

---

## I07 — Meta production speculative decoding：paper FLOPs improvement 与 production speedup不是同一件事

Meta 2025 production report专门讨论：
- tree attention；
- multi-round speculative decoding；
- GPU implementation；
- large batch；
- production latency。

公开结果显示：
> speculative algorithm到 production 后，需要大量 kernel/system优化才能兑现 theoretical speedup。

### 为什么值得读

它是 academic-vs-industry差异的典型案例：

Academic object：
> acceptance rate / generated tokens / theoretical compute。

Industry object：
> actual latency under batch, kernel, synchronization, memory constraints。

### Inspiration

未来看到“efficient reasoning / token pruning / sparse attention”等 academic idea时，
要习惯问：
> **它优化的是 proxy，还是 deployment bottleneck？**

但我们本身不需要去做 production infra paper。

---

## I08 — Qwen3.5 open materials：million-agent RL / async RL 把 agent training的 cost shape暴露出来

Qwen官方开源材料对 3.5 系列描述了：
- unified early-fusion multimodal pretraining；
- hybrid architecture；
- large-scale RL；
- million-agent environments；
- asynchronous RL infrastructure；
- environment orchestration。

### 最重要的不是“百万环境很牛”

而是它说明：

> 当前 frontier agent post-training 的核心 constraint之一已经是 **rollout infrastructure / environment throughput / asynchronous orchestration**。

这对我们的决策恰好是负面信息：

> 如果一个 agentic RL idea只有在这种 scale 下才显现，
> 当前就不适合我们。

### 但 inspiration仍有价值

这些系统可以暴露：
- synchronous RL assumption；
- rollout staleness；
- environment imbalance；
- reward delay；
- policy lag；
- curriculum across environment complexity。

如果某个 pressure能够：
> 在小规模 simulator / offline traces上被独立验证，

才可能转成 academic problem。

---

# 5. Industry → academia 转译梯子

任何公司 artifact 里看到一个有意思的东西，强制过六级。

---

## Level 1 — Raw frontier observation

例：
> million-token agent需要 sparse attention + serving co-design。

只记录事实。

禁止马上问：
> “我们能不能做一个新的 sparse attention？”

---

## Level 2 — Remove company-specific implementation

去掉：
- model name；
- GPU count；
- proprietary environment；
- product interface。

留下：
> 哪个 underlying variable / constraint出现了？

例如：
> context越长，attention selection / storage成本开始主导。

---

## Level 3 — Identify the load-bearing relation

必须能写：

> When X changes, Y becomes the bottleneck because Z.

而不是：
> 大模型遇到很多效率问题。

---

## Level 4 — Academic abstraction

把 relation变成：
- measurable quantity；
- competing explanation；
- algorithmic constraint；
- theorem assumption；
- causal intervention。

例如：
> selection sparsity究竟应由 semantic relevance还是 future reuse value决定？

这一步只是例子，不能直接当 candidate。

---

## Level 5 — Cheap proxy

问：

> 这个 relation在 1B–8B / inference-only / existing dataset / short finetune中是否应该已经出现？

优先：
- inference intervention；
- offline replay；
- small SFT；
- short RL；
- existing logs；
- synthetic micro-world作为 identification instrument。

如果答案：
> 必须1T model、million agents、real users才知道，

停止。

---

## Level 6 — Independent academic pressure

最重要的一关：

> 即使删除那个公司报告，这个问题能不能从公开 academic evidence中独立成立？

如果不能：
> 只是“抄 frontier lab 的 feature”。

不进入 formal candidate。

---

# 6. Industry Inspiration Score ≠ Candidate Score

以后可以给 industry artifact内部做两个完全分离的判断：

## Inspiration value
- 是否展示新 regime？
- 是否暴露学界看不到的 bottleneck？
- 是否重新定义 deployment object？
- 是否有真实 traffic / scale / system evidence？

可以非常高。

## Execution transferability
- open weights？
- small-scale proxy？
- dataset available？
- environment available？
- inference-only验证？
- need from-scratch pretraining？
- need production traffic？

可以非常低。

允许：

> **Inspiration A / Execution F**

而且这种 artifact仍然值得读。

---

# 7. Industry material 不应该怎样使用

## 错误 1
> DeepSeek用了某 architecture → 我们也设计一个 architecture。

## 错误 2
> Qwen百万agent RL → agentic RL一定是好题。

## 错误 3
> GPT effort parameter → 我们做 effort parameter。

## 错误 4
> Gemini支持1M context → long context很热门，做long context。

## 错误 5
> Claude subagents强 → 多agent一定是frontier。

这些都是：
> product feature → topic

的机械迁移。

---

# 8. Industry material 最应该怎样使用

## Use 1 — Find regime changes

例：
- 1M/10M context；
- parallel test-time compute；
- live multimodal；
- long-running agents；
- async RL；
- physical robotics。

问：
> 旧 academic assumption在这个 regime 还成立吗？

---

## Use 2 — Find hidden system variables

例：
- remaining budget；
- effort；
- routing；
- context compaction；
- rollout staleness；
- inference latency；
- KV reuse；
- kernel compatibility；
- user correction signal。

这些变量很多在学术 benchmark中被固定。

---

## Use 3 — Find proxy failures

例：
- FLOPs reduction不等于 latency；
- benchmark accuracy不等于 real workflow success；
- context length不等于 usable memory；
- reward不等于 user correction；
- successful tool call不等于 long-horizon agent reliability。

---

## Use 4 — Find “solution bundles” that need decomposition

Industry report常常一次同时改变：
- architecture；
- data；
- optimizer；
- infra；
- post-training；
- inference。

产品上合理。

science上反而产生问题：
> 到底哪个 component在什么 regime是 load-bearing？

注意：
> 不能靠我们自己复刻整个 bundle来拆。

必须找便宜 identification。

---

## Use 5 — Watch what becomes a product knob

一个变量如果被不同公司反复暴露成 API / system control：
- effort；
- context；
- routing；
- tools；
- memory；
- parallelism；

说明它已经从 research detail变成 operational object。

这不代表它还有 novelty，
但说明：
> 它周围会产生真实的新 questions。

---

# 9. Industry scan 的优先阅读顺序

以后每轮 trend calibration除了 academic papers，再加：

## Frontier model reports
- OpenAI
- Anthropic
- Google DeepMind
- Meta
- DeepSeek
- Qwen
- 其他真正有frontier-scale evidence的lab/company

## Systems / infra
- inference serving
- speculative decoding
- KV/cache
- sparse attention
- distributed training
- RL rollout systems
- multimodal serving

## Model / system cards
尤其关注：
- 新 control knob；
- 新 evaluation category；
- 新 failure；
- product architecture变化。

## Real usage reports
只作为：
> pressure / distribution evidence。

不当 causal proof。

---

# 10. Academic–Industry Dual Ledger

以后每个重要方向可以同时维护：

### Academic frontier
- nearest papers
- unresolved scientific relation
- available datasets / models
- novelty cluster

### Industry frontier
- latest deployment regime
- proprietary-scale observation
- product/system bottleneck
- operational variable

然后问：

> **两边有没有“尺度不同，但 underlying pressure相同”的交点？**

最好的 inspiration zone通常不是：

> industry已经解决的问题。

而是：

> **industry已经证明这个 pressure真实存在，但 academic literature还没有把它抽象成可识别、可低成本研究的问题。**

---

# 11. 新增硬门槛：Scale-Stripping Test

任何来自industry的candidate seed必须回答：

> **把公司规模优势剥掉以后，还剩什么？**

如果剩下：
- 一个 relation；
- 一个 assumption；
- 一个 failure law；
- 一个 allocation problem；
- 一个 representation issue；
- 一个 deployment-induced mismatch；

可以继续。

如果剩下：
> “他们有更多GPU / data / agents / users，所以效果更好”，

直接停止。

---

# 12. 新增硬门槛：Frontier-Only Phenomenon Test

有些问题真的只在frontier scale出现。

这不是问题本身不好。

但对我们：

> **不可做。**

例如若需要：
- >100B model；
- hundreds of billions training tokens；
- million environment rollouts；
- production user traffic；
- 1M-context full training；
- proprietary tool ecosystem；

才能观察核心现象：

> 记入 inspiration ledger，不进入 pilot ledger。

不要试图用 toy proxy硬冒充。

---

# 13. 新增硬门槛：Cheap Causal Echo

最理想的 industry inspiration 是：

> frontier现象很大，
> 但它的 causal core 在小系统里已有“echo”。

例如：

Industry：
> giant agent system需要context compaction。

Academic proxy：
> 小模型长trajectory中，状态压缩方式改变future action quality。

这里仍需真正 novelty audit。

但至少：
> causal variable可以控制。

这比：
> 缩小1000倍模型然后假装同一问题

可靠得多。

---

# 14. 当前 industry scan 的直接结论

第一批材料已经说明：

> **业界最值得我们看的不是 SOTA table，而是它把哪些变量从“研究细节”升级成“产品/系统控制量”。**

目前反复看到：
- effort / test-time compute；
- routing；
- context management；
- long context；
- tool autonomy；
- multimodal early fusion；
- environment orchestration；
- async RL；
- latency / serving；
- architecture-system co-design。

这些词本身都不是题。

真正的价值在于：

> 它们告诉我们 modern frontier system 正在受什么约束。

下一步 academic reading应该反问：
> 公开literature对这些约束已经抽象到哪一步？
> 哪些还停留在工程经验？
> 哪些可以被小而直接的实验识别？

---

# 15. 当前纪律

Industry track 和 academic track 同时存在：

> **Academic papers负责：novelty / explanation / identification taste。**
>
> **Industry reports负责：frontier regime / real bottleneck / system pressure taste。**

两边都不能单独生成candidate。

正式 candidate必须同时回答：

1. academic nearest prior是什么？
2. industry pressure是否真实，还是marketing wording？
3. scale stripped以后问题是什么？
4. cheap causal proxy存在吗？
5. 我们的资源能不能在初期就判生死？
6. full project是否仍然不需要复制frontier-lab scale？

只有这样：
> industry insight 才是灵感，而不是诱惑。
