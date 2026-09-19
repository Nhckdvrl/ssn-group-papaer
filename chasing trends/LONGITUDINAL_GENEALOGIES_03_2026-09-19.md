# Longitudinal Genealogies 03 — Multimodal, Speech, Negative Results, Optimization

> **Status: literature / taste calibration only.**
>
> 继续扩展 genealogy library；不形成候选题，不注册 CTxx。
>
> 本批 deliberately 选择四条与 reasoning-RL 很不一样的 lineage：
>
> 1. VLM interface / visual-token efficiency；
> 2. speech/audio / full-duplex interaction；
> 3. negative / limits / measurement-reinterpretation papers；
> 4. optimization dynamics / SAM。
>
> 目的不是“跨领域凑素材”，而是检验：
>
> > 我们在 NLP/LLM 里觉得新鲜的问题形成方式，换到视觉、语音、优化以后是否仍然成立；  
> > 如果不成立，到底是哪类 domain structure 在决定 paper genealogy。

---

# 0. Relation tags

沿用上一份：

- **[DIRECT]**：后一篇明确把前一篇/同一方法视为 parent；
- **[FIELD]**：属于同一公开 literature family；
- **[RECONSTRUCTED]**：事后 conceptual reconstruction，不声称作者心理来源。

---

# LINEAGE 10 — VLM：从“把 vision 接进 LLM”到“视觉信息在 LLM 内到底应以什么生命周期存在”

## 10.1 Flamingo — multimodal interface 首先是“怎样让 pretrained modules 接起来” [FIELD]

**Flamingo: a Visual Language Model for Few-Shot Learning (2022)**

大规模 language model 和 vision encoder 各自已经很强。

真正困难不是：

> vision 有没有 feature。

而是：

> **怎样把任意交错的 image/text context 接入 pretrained LM，同时保留少样本语言建模能力。**

Flamingo 使用视觉编码/重采样和 gated cross-attention，把 frozen/large pretrained components 连接起来。

### Primitive

```
separate pretrained vision + language systems
→ multimodal interface that lets language generation condition on visual context
```

在这一阶段，visual token efficiency 不是第一问题。

首要问题是：

> interface 能否工作。

---

## 10.2 BLIP-2 — multimodal capability 成功后，end-to-end training cost 成为第一约束 [DIRECT/FIELD]

**BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models (ICML 2023)**

如果视觉-语言大模型需要：

> 从头 joint-train 巨大的 vision encoder + LLM，

成本极高。

BLIP-2 重新定义连接问题：

> 能否 freeze 两端，只学习一个轻量 bridge？

Q-Former 同时承担：

- 从 frozen vision encoder 提取适合 language 的信息；
- 跨越视觉/语言 representation gap。

### Primitive change

```
multimodal model = jointly train large components
→ multimodal model = align frozen experts through a learned bottleneck
```

### Research pressure

这里的 novelty 不只是：

> “参数更少”。

而是：

> **当 pretrained foundation modules 已经存在时，最自然的 architecture object 从 backbone 变成 interface。**

这是 foundation-model 时代非常普遍的 changed premise。

---

## 10.3 LLaVA — connector 变简单，instruction data / conversational interface 变重要 [FIELD]

**Visual Instruction Tuning / LLaVA (NeurIPS 2023)**

LLaVA 进一步展示：

> 很简单的 vision-to-language projection + instruction-tuned LLM，也能产生强 multimodal chat。

它把 GPT-4-assisted visual instruction data 引入 multimodal instruction tuning。

### Frontier movement

从 architecture 角度看：

> connector 不一定越复杂越重要。

当简单 connector 已经够强，field pressure 转向：

- instruction data；
- resolution；
- OCR/detail；
- multi-image/video；
- visual token count；
- latency。

### 这是一种很重要的 historical effect

> 一个 component 一旦被证明可以很简单，
> 研究资源会自然迁移到新的 bottleneck。

这与 TORS 那种“统一后发现 dominant component”不同：

- TORS 是主动 attribution；
- LLaVA lineage 是 empirical success 让某个 component 失去“必须复杂化”的地位。

---

## 10.4 High resolution / AnyRes — capability提升制造 token explosion [FIELD]

更高分辨率对：

- OCR；
- document；
- fine-grained perception；

很重要。

但把高分辨率 image 切更多 patch：

> visual tokens 急剧增多。

由于这些 tokens 进入 LLM self-attention：

> perception improvement 直接变成 inference cost。

于是 visual token 不再只是：

> multimodal input representation。

它同时成为：

> **compute resource。**

---

## 10.5 Early token-pruning family — “很多视觉 token 是冗余的”成为新默认 [FIELD]

2024–2025 大量 work 开始：

- attention-based pruning；
- clustering/merging；
- fixed-ratio dropping；
- early-layer pruning。

核心经验：

> 模型往往不需要在所有 LLM layers 都完整保留所有 visual tokens。

### 这里需要非常谨慎

一个新 cluster 一旦形成，极容易产生低质量选题：

> 换一个 importance score；
> 换一个 pruning layer；
> 换一个 merging rule。

这类轴在 2025–2026 已经极度拥挤。

因此：

> “visual token redundant”本身已经不是 research opening。

---

## 10.6 FastV / related analyses — visual information 的作用随 depth 变化 [FIELD]

**FastV** 一类工作观察：

> deep LLM layers 对大量 visual tokens 的依赖会下降；
> 可以在较早层完成视觉-语言融合后，减少后续视觉 token 计算。

这里真正值得学的 object shift：

```
visual token importance
→ visual token importance as a function of network depth
```

也就是说：

> 一个 token 的价值不是静态 intrinsic score。

它依赖：

> representation processing stage。

### 这一步为后面更多 dynamic work 打开空间

但也迅速形成 saturated axis：

- layer-wise；
- instance-wise；
- attention-free；
- variation-based；
- approximation-error based；

2025–2026 已经非常密集。

---

## 10.7 ATP-LLaVA / PACT / TopV — 2025 进入“importance metric + deployment compatibility”竞争 [FIELD]

CVPR 2025 可以看到 token reduction 已经发展出多个并行轴：

**ATP-LLaVA**
> pruning ratio 应随 layer + instance 自适应。

**PACT**
> 不只 attention score，结合 pruning + clustering，减少 retained-token redundancy。

**TopV**
> 直接把 FlashAttention / KV-cache compatibility 拉进算法约束。

### 这里出现一个有意思的 frontier move

早期 compression paper 关注：

> 减 token 后 accuracy 掉多少。

当 field 进入真实加速阶段：

> **理论 FLOPs reduction ≠ 实际 latency reduction。**

于是：

- kernel compatibility；
- KV-cache；
- irregular token shapes；

成为 method design 的一部分。

### Primitive change

```
compression quality = fewer tokens at same accuracy
→ compression quality = end-to-end operator-compatible speedup
```

这类 deployment pressure 与 BG-MCTS 的 budget-aware search有共性：

> 一个 paper-level proxy 已经不等于系统真正关心的 resource。

---

## 10.8 Video: DyCoke — single-image pruning 的“静态 relevance”假设在 temporal input 上失效 [DIRECT/FIELD]

**DyCoke: Dynamic Compression of Tokens for Fast Video Large Language Models (CVPR 2025)**

视频把 visual-token 数进一步放大。

但更关键的是：

> video 中不同 decoding iterations 会关注不同 frame/token。

因此一次性 one-shot pruning 有新风险：

> 当前不重要的 token，后续生成时可能变关键。

DyCoke做：

- temporal redundancy merging；
- dynamic KV-cache token reduction；
- decoding-stage-dependent retention。

### Primitive change

```
token relevance is static for a prompt
→ token relevance evolves during autoregressive decoding
```

### 这一步不是“video 比 image 多了 time”

更具体地：

> **输出生成过程改变了输入 evidence 的未来价值。**

这是一个 sequential decision / information preservation问题。

---

## 10.9 2026 token compression cluster — 一个很好的 saturation laboratory [FIELD]

CVPR 2026 同一方向出现密集方法：

### V2Drop
从 token **variation** 出发，强调：
- positional bias；
- efficient operator compatibility；
- task-agnostic variation property；
- progressive dropping。

### ApET
避开 attention importance，改成：
- basis reconstruction；
- approximation error；
- information preservation；
- FlashAttention compatibility。

### DUET-VLM
把：
- vision-side redundancy compression；
- LLM-side text-guided dropping；

做成双阶段。

### Unified spatiotemporal compression
同时压 temporal + spatial 冗余。

### MetaCompress / Rethinking Token Reduction
把一个新的 deployment setting拉进来：
> **multi-turn VQA。**

---

## 10.10 Multi-turn token reduction — current-query salience 与 future information preservation 冲突 [FIELD]

**Rethinking Token Reduction for Large Vision-Language Models (CVPR 2026)**

这是 token reduction cluster 里真正值得 taste 学的一跳。

大多数 prior：

> 已知当前 question，
> 再决定哪些 visual tokens 没用。

但 multi-turn scenario 里：

> 下一轮 question 未知。

因此 prompt-dependent compression 会遇到：

> 当前 query 不相关 ≠ 未来 query 不相关。

论文于是把 reduction 重新写成：

> prompt-agnostic learned compression mapping，
> 在多轮未知 future query 下保留可复用视觉信息。

### Primitive change

```
relevance to current question
→ information sufficient for unknown future questions
```

这个 opening 比“新 importance score”更结构性。

因为它改变了：

> **compression objective itself。**

---

## 10.11 VLM token-compression lineage 的真正 movement

```
Can vision connect to language?
→ can frozen pretrained experts be bridged cheaply?
→ simple connector works, high-resolution becomes useful
→ high resolution creates visual-token explosion
→ not all visual tokens matter equally
→ importance varies by layer / instance
→ theoretical token saving must become real kernel-compatible speedup
→ video makes relevance dynamic across decoding time
→ multi-turn interaction makes future query unknown
→ "what to discard" becomes an information-preservation problem under future uncertainty
```

### 重要 conclusion

“visual token compression”这个 surface 已经非常拥挤。

但 field 的 genealogy显示：

> 真正有生命力的新问题通常不是再换 score，
> 而是**系统使用方式改变后，旧 compression objective 本身不再对。**

---

# LINEAGE 11 — Multimodal Reasoning：text 作为默认 reasoning medium 开始被重新审视

这条与 token compression 平行，不要混。

---

## 11.1 Early multimodal reasoning — language decoder 是统一 reasoning interface [FIELD]

LLaVA/多模态 LLM 成功后，一个自然 architecture：

> image → visual tokens → LLM → text answer。

即使任务高度视觉：

> 中间 reasoning 也通常通过 language hidden states / text CoT 表达。

这种设计很好用，因为：

- LLM pretrained reasoning；
- text supervision abundant；
- evaluation方便。

久而久之：

> **language 成为默认 reasoning medium。**

---

## 11.2 Explicit visual intermediate states — “用图想”但代价高 [FIELD]

一些 work 开始：

- crop；
- depth；
- helper images；
- generated image；
- visual tool output；

让模型在 reasoning 中间显式地产生视觉状态。

这证明：

> 有些任务 text-only reasoning 不够自然。

但代价是：

- image-generation training；
- annotation；
- helper representation 先验；
- latency；
- task specificity。

于是下一步 pressure 出现：

> 需要视觉 computation，但不一定需要显式生成 pixels。

---

## 11.3 Mirage / Machine Mental Imagery — latent visual state 作为中间 reasoning carrier [FIELD]

**Machine Mental Imagery: Empower Multimodal Reasoning with Latent Visual Tokens (CVPR 2026)**

论文的 opening：

> text-only decoding 迫使视觉 reasoning 被 verbalize；
> explicit image-generation intermediate又太重，甚至可能干扰 reasoning。

因此：

> 把 hidden states 重新作为 latent visual tokens，
> 允许 text token 与 latent visual token interleave。

训练上先用 image embedding distillation给 latent token起点，随后减少显式视觉监督并继续 task/RL 优化。

### Primitive change

```
reasoning state must be verbalized
→ reasoning state can remain in a learned latent visual channel
```

---

## 11.4 Latent Implicit Visual Reasoning — 连“visual intermediate 应该长什么样”也不该手工规定 [FIELD]

**Latent Implicit Visual Reasoning (CVPR 2026)**

类似 pressure，但 framing 略不同：

> helper images / depth maps / crops 都对“有用视觉 abstraction”施加了人工先验。

于是让模型使用 task-adaptive latent visual reasoning tokens，而不需要指定中间 representation。

### lineage signal

到 2026：

> “latent visual reasoning token”

本身已经不是一个空白 idea。

多个 paper 同时把：

> explicit/verbal reasoning interface

改成：

> implicit multimodal latent computation。

---

## 11.5 这条线对我们最有价值的不是 latent token method

而是一个 general research observation：

> **foundation model 的统一 interface 是 enabling abstraction，也可能是 modality bottleneck。**

text interface：

- 统一 supervision；
- 统一 architecture；
- 统一 decoding。

但新 task regime 会暴露：

> 某些信息通过 text 序列化时有不必要的 bottleneck。

### 机械迁移 warning

绝不能得到：

> “那给 LLM reasoning 加另一种 latent token。”

这个 surface 已经很拥挤。

真正值得学：

> **统一 interface 的收益与损失要在目标 modality 的信息结构上重新审计。**

---

# LINEAGE 12 — Speech/Audio：从“内容 token 序列”转向“时间同步本身就是建模变量”

## 12.1 Text-style pipeline — spoken dialogue 被拆成离散模块和回合 [FIELD]

传统 spoken assistant 常见：

```
VAD
→ ASR
→ text dialogue model
→ TTS
```

优势很明显：

- 每个 component 成熟；
- text LLM可以直接复用；
- debug简单。

但这个 pipeline 隐含两个强 assumption：

1. speech 的主要意义可以通过 text中介；
2. conversation 可以被切成清晰 turn。

真实人类对话却有：

- overlap；
- backchannel；
- interruption；
- hesitation；
- prosody；
- non-speech sound；
- sub-second timing。

这些不是“更多数据”能自动解决的。

它们质疑：

> **turn-based text interface 是否就是正确 basic object。**

---

## 12.2 Speech LM — token interface 被保留，但 modality statistics 很不同 [FIELD]

speech language model 把 raw audio编码成 discrete tokens，再做 next-token modeling。

表面上：

> 终于和 text LM统一了。

但 **Scaling Properties of Speech Language Models (EMNLP 2024 Main)** 发现：

> speech LM 的 syntactic/semantic performance 随 compute增长，速度可比 text LM 慢最多约三个数量级；
> coarser tokenization / synthetic semantic data 会明显改变结果。

### Primitive challenge

```
speech tokens are "just another language token stream"
→ tokenization rate / acoustic variability changes the scaling problem
```

这和 FAST 的 action-tokenization非常类似：

> token interface成功，并不意味着 token statistics 相同。

---

## 12.3 Synchronous LLMs — 没有 real-world clock，就无法真正 full duplex [DIRECT/FIELD]

**Beyond Turn-Based Interfaces: Synchronous LLMs as Full-Duplex Dialogue Agents (EMNLP 2024 Main)**

这篇非常适合 research-taste学习。

它不是：

> “把语音模型 latency再减几十毫秒”。

作者先明确：

> pretrained LLM 本身没有现实时间概念。

如果两个人同时讲话，模型需要：

- 一边听；
- 一边可能说；
- 处理 overlap；
- 对 pause/interjection timing 做反应；
- 考虑网络 latency。

因此：

> **time 不是外部系统 metadata，而应该进入 sequence model 的 state。**

论文加入 periodic synchronization tokens / shared clock，并对未来用户 speech做短时预测以容忍网络延迟。

### Primitive change

```
conversation = alternating utterance sequence
→ conversation = two concurrent streams embedded in a shared real-time clock
```

这个 move 极其重要，因为：

> 它不是优化已有 turn-taking detector，
> 而是改变 dialogue 的数学对象。

---

## 12.4 Moshi — pipeline decomposition 本身成为 latency/semantics bottleneck [FIELD]

**Moshi: a speech-text foundation model for real-time dialogue (2024)**

Moshi更激进：

> VAD→ASR→text model→TTS 的 modular pipeline有三个结构性问题：
>
> - 累积 latency；
> - text中介丢 prosody/non-linguistic information；
> - turn segmentation无法自然表示 overlap/interruption。

于是直接建：

> speech-to-speech generative dialogue。

模型并行维护 user / model speech token streams。

但有意思的是：

> 它没有完全抛弃 text。

反而加入 time-aligned text “Inner Monologue”，先预测 semantic text token，再生成 acoustic token。

### 这个设计非常值得 taste 学

不是：

> “speech end-to-end 比 pipeline先进”。

而是：

> **当移除旧 interface 后，作者发现旧 interface 中某一层 abstraction（text semantics）仍然有用，于是把它从 external bottleneck 变成 internal scaffold。**

换句话说：

```
external mandatory text interface
→ remove it for full-duplex speech
→ reintroduce aligned text internally where it helps semantic organization
```

这比“端到端替代 pipeline”更细。

---

## 12.5 Speech representation — acoustic / semantic 的二分也可能太粗 [FIELD]

codec / tokenizer literature长期在权衡：

- acoustic fidelity；
- semantic content；
- token rate。

到 2025 的一些 work继续指出：

> acoustic token + semantic token 的二分仍可能缺 contextual representation。

例如 multimodal-distillation codec方向尝试让 tokenizer同时吸收：

- acoustic；
- semantic；
- contextual；

teacher signals。

### Primitive movement

```
audio code = compression
→ audio code = representation interface for generation + semantics
→ representation must preserve multiple information types under a bitrate budget
```

---

## 12.6 Speech lineage 的真正独特压力：physical time

LLM text research经常把时间理解成：

> token position。

speech/full-duplex里：

> 真实毫秒时间就是 causal variable。

例如 200ms latency：

- 不是多两个 token那么简单；
- 它会改变 interruption、overlap、turn-taking是否自然。

所以 speech给跨领域科研一个特别好的提醒：

> **有些 modality / system variable 不是 observation feature，而是 interaction dynamics 的组成部分。**

这类 structure 不能机械映射到 text。

---

## 12.7 当前 speech/audio surface 的 saturation warning

热门方向：

- speech tokenizer；
- semantic/acoustic dual codebook；
- full-duplex；
- streaming；
- speech-text unified model；

已经快速变密集。

因此：

> “做一个 full-duplex model”
> 或
> “加 semantic token”

都不是 research question。

真正要理解：

> real-time concurrency、representation bandwidth、semantic/acoustic/contextual tradeoff 中，哪个 assumption 正在成为 bottleneck。

---

# LINEAGE 13 — Negative / Limits Papers：强 paper 不一定发明新能力，也可以重新定位“问题到底在哪”

这条非常重要，因为只读 method paper 会产生严重 survivorship bias。

---

## 13.1 Prompt calibration — few-shot LM 的 output prior 会造成巨大表面波动 [FIELD]

**Calibrate Before Use: Improving Few-Shot Performance of Language Models (ICML 2021)**

早期 few-shot prompting发现：

> prompt wording / examples可以显著改变预测。

该 work把一部分问题归因于：

> model 对 label/output forms存在 context-induced bias。

content-free input可用于估计/校正。

### primitive move

```
prompt changed → capability changed
```

被重新分解为：

```
prompt changed → output prior / calibration changed → measured accuracy changed
```

这是一个 measurement/decision-layer attribution。

---

## 13.2 Prompt ordering — 现象被进一步放大为 accepted limitation [DIRECT/FIELD]

**Fantastically Ordered Prompts and Where to Find Them (ACL 2022 Outstanding)**

论文系统显示：

> few-shot demonstrations的排列顺序能让表现从接近 SOTA 到近 random；
> 好 permutation不容易跨模型转移；
> 增加 example也不简单消除 variance。

在当时，这使：

> prompt order sensitivity

成为非常真实、非常重要的 model-use problem。

### 为什么这篇 paper当时是强 paper

它不需要证明：

> LM内部为什么如此。

仅凭：

- effect大；
- across scale；
- operationally critical；
- 给出无标注选择方案；

就足够改变实践。

这提醒：

> **不是每篇强 paper都必须有深 mechanism。**

---

## 13.3 Instruction-tuned LLM时代 — 老 limitation 与新模型目标发生矛盾 [FIELD]

几年以后，模型发生重要变化：

> instruction tuning让模型显式训练在多样 prompt/instruction formats上。

于是一个 tension出现：

> 如果现代模型真的能跟随多样自然语言指令，
> 为什么 benchmark研究还报告极高 prompt sensitivity，甚至 model ranking随 template翻转？

这不是：

> “再测一遍新模型”。

因为 changed premise并不是：

> GPT-4 比 GPT-3 大。

而是：

> **model training objective 已明确把 prompt-format robustness纳入能力。**

因此旧 phenomenon 与新系统设计之间出现了理论/经验冲突。

---

## 13.4 Flaw or Artifact? — 从 model limitation 改成 evaluation-channel attribution [FIELD]

**Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs (EMNLP 2025 Main)**

论文重新检查 modern instruction-tuned models：

- multiple prompt templates；
- multiple-choice + open-ended；
- heuristic extraction；
- log-likelihood scoring；
- semantic/judge evaluation。

发现：

> 很多所谓 prompt sensitivity来自 rigid answer extraction / scoring，
> 模型生成语义正确但格式不同的答案时被误判。

换 evaluation以后：

> performance variance下降，ranking更稳定。

### Primitive change

```
prompt sensitivity = model property
→ measured prompt sensitivity = model behavior + evaluation channel
```

### 这是一种非常强的 negative contribution

它没有：

> 发明一个更robust模型。

而是告诉 field：

> **你以为你在测 model sensitivity，实际上 measurement apparatus本身贡献了相当部分。**

---

## 13.5 为什么这种 paper 很容易做坏

机械版：

> “benchmark metric有问题。”

然后换 LLM-as-judge。

这非常容易落入用户不喜欢的 evaluator work。

强版本必须满足：

1. field已经依据旧 measurement形成重要结论；
2. 新 measurement揭示不是小数值变化，而是 attribution改变；
3. 解释为什么旧 measurement在新 regime下失效；
4. 结论影响我们如何理解模型，而不只是 leaderboard。

也就是说：

> **measurement audit必须改 scientific interpretation。**

---

## 13.6 Foundation model “world model” — high task performance不能直接推出 structural understanding [FIELD]

**What Has a Foundation Model Found? Using Inductive Bias to Probe for World Models (ICML 2025)**

foundation model有一个宏大 narrative：

> sequence prediction可能发现底层 world structure。

但标准 benchmark accuracy只告诉：

> 预测是否好。

并不能识别：

> 模型是不是学到了我们声称的 underlying world model。

这篇提出 inductive-bias probe：

> 用一个 hypothesized world model生成 synthetic adaptation data，
> 检查 foundation model适配时是否表现出与该 world model一致的 inductive bias。

作者报告：

> 很多 model可以把训练任务做得很好，却未表现出预期 world-model bias。

### Primitive change

```
high predictive performance
→ evidence for latent world understanding
```

被打断为：

```
high predictive performance
≠ structural inductive bias
```

### 为什么这比“又一个 benchmark”更科学

因为 probe被设计来区分：

> 两种不同解释。

不是简单测：

> 能做几题。

---

## 13.7 Negative/limits lineage 的真正 pattern

```
large observed failure/success
→ community attaches an interpretation
→ system/training regime changes
or a new identification tool appears
→ old measurement no longer uniquely identifies the interpretation
→ re-localize the phenomenon
```

### 强 negative paper 的贡献单位

不是：

> “发现模型又不行。”

而是：

> **改变我们把 failure/success 归因给谁。**

可能从：

- model → evaluator；
- capability → prompt prior；
- sequence prediction → structural understanding；
- reasoning trace → post-hoc artifact；
- benchmark gain → shortcut。

---

## 13.8 Contrast：普通 stress test 为什么经常不够

例如：

> 改 option length / label / format后，accuracy掉很多。

这种 result可以重要。

但如果 paper只停在：

> 模型不robust，

很容易变成：

- another benchmark；
- another adversarial perturbation；
- another failure taxonomy。

Main-sized scientific story往往需要再回答：

> **这个 failure推翻了 community 的哪一个 inference？**

否则：

> effect大 ≠ question大。

---

# LINEAGE 14 — Optimization / SAM：成功方法的“原始解释”本身也会成为后续研究对象

## 14.1 SAM — 从 final loss value 转向 neighborhood geometry [DIRECT/FIELD]

**Sharpness-Aware Minimization for Efficiently Improving Generalization (ICLR 2021)**

overparameterized network中：

> training loss都可以很低。

因此只优化 pointwise loss无法解释 generalization。

SAM的核心 framing：

> 不只要当前位置 loss低，
> 邻域中的 worst-case loss也要低。

于是：

> 参数更新在局部 weight perturbation下寻找 flat region。

### Primitive change

```
minimize loss at θ
→ minimize neighborhood-aware sharpness objective around θ
```

这篇把一个 generalization intuition变成可优化目标。

---

## 14.2 后续 field很容易把“flat minima”当固定解释 [FIELD]

SAM成功以后，大量 paper围绕：

- efficient approximation；
- adaptive radius；
- layer-wise perturbation；
- variants；
- generalization bound。

容易形成一个 folk story：

> SAM好，因为最后找到更flat minima。

但一个优化算法的作用发生在：

> 整条 trajectory。

只看 converged point可能漏掉主要 dynamics。

---

## 14.3 SAM Operates Far from Home — 从 endpoint geometry改成 training dynamics [DIRECT]

**SAM operates far from home: eigenvalue regularization as a dynamical phenomenon (ICML 2023)**

论文明确挑战：

> 只在 minima附近解释SAM。

它发现：

> SAM在整个training trajectory中就持续调节 Hessian top eigenvalue，
> 与 edge-of-stability dynamics有关。

理论给出：

> learning rate / SAM radius 与最大 eigenvalue稳定值的关系。

### Primitive change

```
SAM explanation = geometry near final minima
→ SAM explanation = dynamical stabilization throughout training
```

这里非常值得 taste 学：

> **成功 method 的 original motivation 不等于它实际起作用的唯一机制。**

后续 paper可以研究：

> method does what it was designed to do?

而不是：

> method有没有效果。

---

## 14.4 SDE / saddle analysis — 同一个 dynamic effect也可能制造 pathology [FIELD]

**An SDE for Modeling SAM (ICML 2023 line)** 等理论 work进一步分析：

> SAM的 memory/noise/dynamics。

其中一个重要 result：

> 在某些条件下，SAM可能受到 saddle points吸引。

这就把：

> “sharpness control improves generalization”

变成更复杂的 picture：

> 同一种 dynamics可以带来 regularization，也可以引入 convergence pathology。

### Research evolution

```
method success
→ mechanism reinterpretation
→ mechanism has unintended consequence
→ new optimization problem appears
```

这是一种很漂亮的 longitudinal growth。

---

## 14.5 Lookahead — method直接从 newly exposed dynamics 长出来 [DIRECT/FIELD]

**Improving Sharpness-Aware Minimization by Lookahead (ICML 2024)**

paper引用前面对：

> convergence instability / saddle oscillation

的认识，并针对它设计 lookahead式修正。

这里 method story强的原因：

> 修正对象非常具体。

不是：

> 加 momentum因为通常有效。

而是：

> **如果 trajectory pathology是核心，就应该改变算法怎样看前方/逃离该 dynamics。**

---

## 14.6 BiSAM — 更进一步：也许原始 min-max formulation 本身就不是正确 proxy [DIRECT/FIELD]

**Improving SAM Requires Rethinking its Optimization Formulation (ICML 2024)**

另一支不是继续修 dynamics。

它回到 objective：

> SAM让 minimize/maximize player优化同一个 differentiable surrogate loss。

作者认为：

> 对 classification generalization真正关心的是 0–1 loss意义下的 robust behavior；
> 同一 surrogate的zero-sum formulation并不天然对应它。

于是 reformulate成：

> min/max使用 upper/lower surrogate，形成 bilevel optimization。

### Primitive change

```
SAM approximation needs improvement
→ original mathematical formulation may optimize the wrong game
```

### 这很重要

同一个 successful method可以同时产生：

- dynamics lineage；
- objective lineage；

它们不是竞争“哪个解释唯一正确”。

而是：

> 一个成熟 algorithm开始被拆成多个 scientific objects。

---

## 14.7 Tilted SAM / later variants — neighborhood aggregation本身继续被审计 [FIELD]

**Tilted SAM (ICML/NeurIPS 2025 period)** 一类 work指出：

> worst-case local perturbation只关注一个最坏邻居，
> 可能丢掉 neighborhood distribution其余结构。

于是用 exponential tilting等方式平滑 generalised sharpness。

### lineage signal

最初：

> point loss 不够。

SAM：

> worst neighborhood更好。

后来：

> worst neighbor本身又是过粗 aggregation。

frontier变成：

> **怎样概括 local loss landscape。**

---

## 14.8 Optimization memory — “optimizer state”可以重新解释成 implicit loss modification [FIELD]

**How Memory in Optimization Algorithms Implicitly Modifies the Loss (NeurIPS 2025)**

这篇不属于SAM本身，但非常适合作为 parallel lineage。

Adam/momentum/Lion等 update依赖历史。

通常我们把：

> momentum / EMA state

当算法实现。

作者提出一般技术：

> 用把 past iterates替换为current iterate的 memoryless算法 + correction term近似有memory算法。

correction可以解释成：

> **loss perturbation / implicit regularization。**

并用它比较 AdamW 与 Lion 的隐式 anti-regularization差异。

### Primitive change

```
optimizer memory = update bookkeeping
→ optimizer memory = implicit modification of the objective landscape
```

这是很典型的：

> **换数学表示后，原本 engineering state变成 scientific quantity。**

---

## 14.9 为什么 optimization theory 对找题 taste 非常有用

它通常不依赖：

> 最近哪个模型 benchmark最热。

而是训练一种更稳定的问题形成方式：

- algorithm original motivation vs actual dynamics；
- endpoint vs trajectory；
- explicit objective vs implicit objective；
- min-max proxy vs task loss；
- memory state vs regularizer；
- stability boundary vs average convergence rate。

这些 conceptual distinctions很多可以跨领域提供 pressure。

但：

> 不能只迁术语。

---

# 15. 四条 lineage 放在一起后的 meta-observations

---

## 15.1 Interface 是最常被低估的 research object

VLM：

> visual-language connector / visual tokens。

Speech：

> text中介 / turn segmentation / clock。

Optimization：

> objective interface between local geometry and actual task error。

Negative/evaluation：

> answer extraction / scoring channel。

这些东西一开始常像：

> implementation detail。

当系统变强后，它们却可能决定：

- 可扩展性；
- latency；
- information loss；
- scientific interpretation。

### Taste lesson

不要默认：

> “真正科学的问题一定在模型内部。”

有时真正 load-bearing 的是：

> **系统和系统、模型和 measurement、modality和sequence之间的 interface。**

---

## 15.2 “动态”不是 novelty；关键是谁的状态在变

VLM token pruning：
> relevance随 decoder step变。

Speech：
> user/model两条stream共享现实clock。

SAM：
> Hessian spectrum随optimization trajectory变。

这些都叫 dynamic。

但 scientific objects完全不同。

所以：

> “做 dynamic/adaptive method”

毫无价值。

必须先定义：

> **哪一个 state变化会改变 decision value？为什么？**

---

## 15.3 Strong negative paper经常是 re-attribution paper

Prompt sensitivity：

> model flaw → partly evaluation artifact。

World-model probe：

> task success → 不足以证明 structural understanding。

CoT faithfulness：

> explicit rationale → 不自动等于 causal explanation。

这类 work真正贡献：

> **把一个已经被 community接受的 causal attribution拆掉。**

它与纯 benchmark stress test的差别就在这里。

---

## 15.4 一个 field 的 method zoo 往往先于 measurement refinement

VLM compression：

> 先有大量 pruning/merging方法；
> 后来才越来越认真看真实 latency / operator compatibility / multi-turn preservation。

SAM：

> 先有强method；
> 后面才不断重写“sharpness”到底应该怎么测/聚合/解释。

这告诉我们：

> **大规模方法繁荣本身就是未来 science question的原料。**

但需要找到：

> method zoo共享的未验证 abstraction。

不是：

> 对每个method做一次分析。

---

# 16. Saturation / execution ledger

## VLM token compression
当前高度拥挤：
- attention score pruning；
- layer-wise adaptive pruning；
- instance-wise pruning；
- merging；
- FlashAttention-compatible pruning；
- dynamic video pruning；
- approximation-error / variation metrics；
- multi-turn compression。

结论：
> generic token reduction不应当成为我们候选题来源。

## Latent visual reasoning
2026已有多篇：
- latent visual tokens；
- multimodal interleaved reasoning；
- implicit visual reasoning。

结论：
> “text reasoning不够，加入latent visual thought”已经是 crowded surface。

## Speech/full-duplex
方向前沿且工程成本高：
- codec；
- streaming；
- synchronized generation；
- huge synthetic speech hours；
- end-to-end realtime system。

对我们：
> 非默认执行方向；主要作为 question-forming source。

## Negative/evaluation
危险：
- another stress test；
- another judge；
- another benchmark；
- prompt template sensitivity redux。

只有当：
> attribution真正改变
才值得高评价。

## Optimization
危险：
- theorem只在toy quadratic；
- another optimizer acronym；
- 不可验证的 implicit-bias story。

优势：
> 常能用小模型 / controlled objective做高信息量pilot。

---

# 17. 下一步仍需补厚的地方

虽然已经比第一批厚很多，仍缺：

1. **Video generation / world model lineage**
   - 不只 token compression。
   - 看 temporal consistency / autoregressive vs diffusion / latent dynamics。

2. **Multimodal pretraining objective lineage**
   - contrastive → captioning → generative unified objective；
   - understanding/generation冲突。

3. **Speech tokenizer完整 lineage**
   - neural codec → semantic token → dual-stream / delayed pattern → full-duplex。

4. **Negative-result lineage再加至少两条非 prompt examples**
   - scaling assumption；
   - reasoning monitorability；
   - benchmark shortcut；
   - representation probe failures。

5. **Optimization再补一个非 SAM family**
   - Adam/Lion / SGD implicit bias；
   - bilevel or constraint optimization；
   - optimizer memory。

6. **Cross-field “same surface, different genealogy” comparison**
   - adaptive compute；
   - token pruning；
   - curriculum；
   - latent reasoning；
   - selective update。

这是后续真正能防止机械迁移的一层。
