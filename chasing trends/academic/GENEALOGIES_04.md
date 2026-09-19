# Longitudinal Genealogies 04 — Unified Multimodal Objectives, Speech Tokenizers, CoT Faithfulness, World Models

> **Status: literature / taste calibration only.**
>
> 这份继续补 `02/03` 尚未做厚的几个地方。
>
> 仍然不生成候选题。
>
> Relation tags：
>
> - **[DIRECT]**：后作明确把前作/方法定位成 parent；
> - **[FIELD]**：同一公开 problem family；
> - **[RECONSTRUCTED]**：用于理解 frontier movement 的 conceptual reconstruction，不推测作者心理史。

---

# LINEAGE 15 — Vision-Language Pretraining Objective：从“选 contrastive 还是 generative”到“一个模型怎样同时保留不同任务需要的信息”

## 15.1 Contrastive representation learning — 建立共享 embedding space [FIELD]

CLIP-style pretraining 的核心：

> 大规模 image-text pairs 上做跨模态对比学习。

它极大强化：

- zero-shot classification；
- retrieval；
- transferable visual representation。

### Primitive

```
image and text
→ aligned global representations
```

这种 objective 天然擅长：

> discriminative / representation tasks。

但对：

> 细粒度 conditional generation

并不是同一个目标。

---

## 15.2 Generative VLP — token prediction保留不同类型的 supervision [FIELD]

另一支 vision-language pretraining 采用：

- captioning；
- prefix language modeling；
- seq2seq generation。

这类 objective 更自然支持：

> image-conditioned text generation。

但它未必直接给：

> 对比式 retrieval / global semantic alignment

最强 representation。

于是早期 field形成一个很明确的 objective split：

```
contrastive understanding
vs
generative captioning
```

---

## 15.3 BLIP — “understanding vs generation”不是必须二选一 [FIELD]

**BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation (ICML 2022)**

BLIP明确指出：

> 当时很多 VLP model偏 understanding 或 generation其中一边。

它同时处理另一现实问题：

> web image-text pairs数量大但噪声高。

因此 BLIP不只是：

> 把两个 loss加起来。

它设计：

- encoder / decoder / image-grounded encoder；
- image-text contrastive；
- matching；
- language modeling；
- caption bootstrapping + filtering。

### Primitive change

```
choose a downstream orientation
→ build one pretraining system whose representation supports both understanding and generation
```

### 但注意

这类 unified objective paper很容易变成：

> 多 loss 拼接。

真正强点必须在：

> 不同 objectives为什么共享 / 冲突，
> architecture如何让它们共存。

---

## 15.4 CoCa — objective unification本身可以更 minimalist [FIELD]

**CoCa: Contrastive Captioners are Image-Text Foundation Models (2022)**

CoCa做了一个很干净的 decomposition：

- decoder前半不 cross-attend image，用于 unimodal text representation；
- 后半 cross-attend image，用于 multimodal generation；
- 同一 computation graph同时算 contrastive + captioning loss。

### Primitive change

相比：

> 为每个 task建独立头/复杂 module，

CoCa强调：

> **architectural factorization可以让同一 model不同阶段承担不同 representation role。**

这个 genealogy值得学的不是：

> “contrastive + generation一起训”。

而是：

> **当两个 objective需要不同 invariance / information granularity时，network哪里共享、哪里分开本身就是问题。**

---

## 15.5 BLIP-2 — 大模型时代让 objective问题转成 interface / freezing问题 [DIRECT/FIELD]

到了 frozen LLM + frozen image encoder时代：

> end-to-end objective unification成本变得极高。

BLIP-2不再主要问：

> 哪组 pretraining loss最强？

而问：

> **怎样在不破坏两个大 pretrained expert的情况下，让它们交换足够信息？**

Q-Former用两个阶段：

1. 从 frozen vision encoder学习视觉-语言 representation；
2. 对齐到 frozen LLM 的 generative interface。

### Frontier movement

```
jointly learn multimodal representation
→ bootstrap alignment between already-learned representations
```

这是 foundation-model时代很典型的 shift：

> model内部 objective design
> → interface/alignment design。

---

## 15.6 Unified understanding + generation 再次回归，但 changed premise 已经不同 [FIELD]

到 2025–2026，unified multimodal models又把：

- understanding；
- text generation；
- image generation；
- editing；

放进同一 model。

表面看像：

> 回到 BLIP 的 unified understanding/generation。

实际上 premise变了：

早期：
> 输出主要是 text。

现在：
> model可以 both consume and generate multiple modalities。

因此新问题不再只是：

> contrastive loss + caption loss如何共存。

而是：

> **理解分支学到的 semantic structure能不能直接成为 generation 的 learning signal？**

---

## 15.7 “Learning to Generate via Understanding” — 已有能力之间的 asymmetry成为 supervision source [FIELD]

**Learning to Generate via Understanding: Understanding-Driven Intrinsic Rewarding for Unified Multimodal Models (CVPR 2026)**

论文观察：

> unified model常常 understanding强、generation相对弱。

不是简单：

> generation data再加一点。

而是利用 model自身较强的 understanding branch：

> 对它自己生成的 image提供 token-level text-image alignment reward，
> 形成 self-supervised RL。

### Primitive change

```
two capabilities coexist in one model
→ stronger capability can supervise weaker capability
```

这是一种 capability-asymmetry利用。

### 但这个 surface 也很危险

“model自己当teacher”已经非常热门。

真正 novelty必须来自：

> 两个能力之间有什么可验证的信息关系。

不是：

> self-reward本身。

---

## 15.8 Unified Multimodal Models as Auto-Encoders — task relation可以通过新的 mathematical decomposition重写 [FIELD]

**Unified Multimodal Models as Auto-Encoders (CVPR 2026)**

这篇把：

- image→text understanding；
- text→image generation；

重新解释成：

> 一个跨模态 auto-encoder 的 encode / decode 两个方向，
> text作为中间 semantic latent。

于是提出 reconstructive reward：

> 如果 I2T真的理解 image，应编码足够 structure；
> 如果 T2I真的理解 text，应能把 structure还原。

### Primitive change

```
two tasks sharing a backbone
→ two directions of one reconstructive relation
```

这个 move比：

> “multi-task loss”

更有 research taste，因为它：

> **重新定义了两个成熟任务之间的 relation。**

---

## 15.9 这条 lineage真正教什么

```
contrastive and generative objectives optimize different information
→ unified pretraining tries to preserve both
→ architecture factorizes where objectives share / diverge
→ frozen foundation models make interface the bottleneck
→ any-to-any models reunify understanding and generation
→ capability asymmetry / reconstructive relation becomes a new training signal
```

### Saturation warning

截至 2026：

- unified understanding-generation；
- self-reward；
- any-to-any；
- reconstruction；
- contrastive + generation；

都已经是密集空间。

所以：

> “统一两种能力”

不是问题。

必须问：

> 两种能力之间此前缺了哪一个具体 relation。

---

# LINEAGE 16 — Speech Tokenization：tokenizer不是前处理，它决定 speech LM 到底能学什么

## 16.1 Neural audio codec — 首要目标是高保真压缩 [FIELD]

SoundStream / EnCodec一类 neural codec 的原始目标更接近：

> 在低 bitrate 下重建自然音频。

所以离散 code首先优化：

- waveform fidelity；
- perceptual quality；
- bitrate。

如果把这种 codec token直接送进 speech LM：

> 它未必是最适合 language modeling 的 symbol system。

因为：

> reconstruction-relevant information
> ≠ language-prediction-relevant information。

---

## 16.2 Semantic units — self-supervised speech representations提供另一类 token [FIELD]

HuBERT / w2v-BERT式 discrete units更偏：

- phonetic；
- linguistic；
- semantic。

优点：

> language structure更明显。

缺点：

> 声音细节、speaker、prosody、timbre损失。

于是 field出现一个很强的 tradeoff：

```
semantic token
vs
acoustic token
```

---

## 16.3 SpeechTokenizer — 不再二选一，而是把信息分层放进 RVQ [FIELD]

**SpeechTokenizer: Unified Speech Tokenizer for Speech Language Models (2023)**

论文首先做 SLMTokBench，指出：

> 单独 semantic token 与单独 acoustic token都不是理想 SLM representation。

然后不是简单 concat两种token。

它让 RVQ hierarchy承担不同信息：

- first quantizer通过 speech SSL teacher蒸馏，更偏 semantic；
- 后续 quantizers补 acoustic/timbre细节。

### Primitive change

```
choose one speech representation
→ hierarchical token stream carrying different information layers
```

### Genealogy value

一个 representation problem被改成：

> **information allocation across codebooks。**

---

## 16.4 Mimi — full-duplex deployment把 token rate / streaming latency变成 representation约束 [DIRECT/FIELD]

Moshi使用的 **Mimi codec** 又改变 objective。

它不仅要：

> speech quality + semantics。

还必须适合：

> realtime autoregressive dialogue。

因此关键约束包括：

- fully streaming；
- ~80ms frame latency；
- 低 frame rate（约 12.5 Hz）；
- 低 bitrate；
- semantic first codebook via WavLM-style distillation。

### Primitive change

```
token quality for offline speech LM
→ token quality under autoregressive step-rate + streaming latency constraints
```

这非常像 VLM compression从：

> FLOPs

走向：

> real operator latency。

representation不能脱离 deployment。

---

## 16.5 Scaling Properties of SLMs — tokenizer quality会直接改变“scale是否能救你” [FIELD]

EMNLP 2024的 scaling study显示：

> speech LM的 linguistic ability随 compute扩展得比 text LM慢得多；
> coarser tokenization和 synthetic semantic data能改善 scaling behavior。

### 关键 implication

如果 representation本身让模型花大量 capacity建模：

- waveform细节；
- speaker变化；
- redundant frame-level variation；

那么：

> 继续加 compute不一定高效地转成 syntax/semantics。

所以：

> **scaling law与tokenizer并不是独立问题。**

输入 symbol system决定：

> compute被花在哪里。

---

## 16.6 DM-Codec — semantic/acoustic二分仍然不够 [FIELD]

**DM-Codec: Distilling Multimodal Representations for Speech Tokenization (Findings EMNLP 2025)**

当 semantic+acoustic统一已经出现后，论文指出：

> 仍缺 contextual representation。

它用：

- LM-guided contextual teacher；
- speech SSL semantic teacher；
- acoustic reconstruction；

一起 distill 到 codec。

### Primitive change

```
speech information = semantic + acoustic
→ speech information = acoustic + semantic + contextual
```

### 这里也给出 saturation warning

如果下一篇只是：

> 再加第四种 teacher signal，

很容易 module stacking。

真正的问题必须是：

> 哪个 downstream failure证明现有 information decomposition漏了一个必要 component？

---

## 16.7 Tokenizer lineage的关键演化

```
audio compression code
→ semantic speech unit
→ hierarchical semantic+acoustic tokenizer
→ streaming/low-rate dialogue-compatible tokenizer
→ contextual information enters the tokenization objective
```

### 最值得迁移的 taste

> **一个 tokenizer不是被动压缩器。**
>
> 它定义：
>
> > downstream model看到什么是一个“symbol”，以及模型必须花capacity重建哪些 variation。

这适用于：

- speech；
- robot action；
- image token；
- video latent；

但每个 modality 的 information decomposition不同。

---

# LINEAGE 17 — CoT Faithfulness：从“CoT看起来合理吗”到“到底要用什么 intervention定义 faithful”

## 17.1 CoT成功以后，explanation与computation很容易被混为一谈 [FIELD]

CoT prompting最初主要目标：

> 提高 reasoning accuracy。

当模型输出可读 reasoning以后，用户自然会额外推断：

> 这段文字解释了模型为什么得到答案。

但：

> performance usefulness
> 与
> mechanistic faithfulness

不是同一个 claim。

于是新的 research object出现：

> CoT是否 causal地参与 final answer？

---

## 17.2 Bias/hint intervention — 第一个常见 identification strategy [FIELD]

早期 faithfulness work经常：

- 给模型暗示；
- 加错误 hint；
- bias answer；
- 看 CoT是否承认真正影响它的 cue。

如果 answer被暗示改变，但 CoT编了另一套理由：

> 说明 verbal rationale可能 post-hoc。

### 优点

causal intervention清楚。

### 弱点

> intervention本身是 artificial。

这后来制造了：

> in-the-wild faithfulness

的新问题。

---

## 17.3 Causal mediation — 不再只看“CoT内容是否提到bias” [FIELD]

**Making Reasoning Matter (Findings EMNLP 2024)** 一类 work使用 causal mediation：

> 改 reasoning steps，观察 final answer是否随之改变。

这把 faithfulness从：

> textual overlap / plausibility

转成：

> **intermediate rationale对输出的 causal influence。**

### Primitive change

```
explanation text says X
→ changing explanation-state should change decision if X is causally used
```

---

## 17.4 Different model families use CoT differently [FIELD]

**Analysing Chain of Thought Dynamics: Active Guidance or Unfaithful Post-hoc Rationalisation? (EMNLP 2025 Main)**

论文比较：

- instruction-tuned；
- reasoning；
- reasoning-distilled models；

在 soft-reasoning tasks 上的 CoT dynamics。

结果显示不同 family：

> 对 CoT作为 active guide / post-hoc rationale 的依赖不同。

### Important changed premise

“CoT faithfulness”不能被当成：

> 一种固定 model property。

因为：

> training procedure本身改变了 generated rationale在 computation中的 role。

这会让旧 measurement跨 family迁移时失效。

---

## 17.5 FUR — faithfulness相对于“模型参数中的belief”重新定义 [FIELD]

**Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps (EMNLP 2025 Outstanding)**

这篇没有沿：

> cue injection。

它问：

> 如果某个 reasoning step真的反映模型依赖的 parametric information，
> 把对应 information从参数中 unlearn后，answer是否应该改变？

FUR通过：

> unlearning reasoning-step information

来测：

> generated reasoning与 parametric belief之间的 causal relation。

### Primitive change

```
faithfulness to observed prompt intervention
→ faithfulness to model's parametric information
```

这说明：

> “faithfulness”本身不是一个单一定义。

它取决于：

> 你声称 explanation faithful to **what**。

---

## 17.6 Causal Diagnosticity — metric本身也需要 ground-truth-ish intervention test [FIELD]

当 faithfulness metric越来越多：

- perturbation；
- counterfactual；
- filler tokens；
- attribution；
- causal mediation；

下一问变成：

> metric自己怎么验证？

**A Causal Lens for Evaluating Faithfulness Metrics (EMNLP 2025)** 用 model editing构造：

> faithful / unfaithful explanation pairs，

再测试各 metric有没有 diagnosticity。

### Primitive change

```
measure faithfulness
→ measure whether a faithfulness metric can identify controlled causal differences
```

### 这是一个典型 meta-evaluation escalation

但它也说明：

> 一个 field如果 identification不稳，会自然出现 evaluator-of-evaluator。

对我们：

> 这通常不适合作为默认项目，因为很容易掉进 measurement infrastructure。

---

## 17.7 Natural faithfulness — artificial intervention不足以回答deployment question [FIELD]

2025–2026另一支 work把焦点转向：

> 不注入 bias时，自然 reasoning里是否存在 post-hoc rationalization / illogical shortcut。

这重新连接了：

- causal faithfulness；
- deployment monitoring；
- reasoning model safety。

### Genealogy lesson

同一个 concept会沿两轴生长：

1. **definition / measurement** 更严格；
2. **evidence regime** 更自然。

两者都可以产生新 paper。

但如果只说：

> “我们测一个新 setting”，

不够。

必须说明：

> 原 measurement为什么不能回答实际 claim。

---

## 17.8 CoT faithfulness cluster的 saturation

截至 2025：

- bias injection；
- causal mediation；
- activation patching；
- unlearning；
- explanation consistency；
- metric benchmarking；
- natural vs artificial cue；
- multimodal faithfulness；

已经非常 crowded。

所以：

> “CoT可能不faithful”

绝对不是题。

> “提出一个faithfulness metric”

也默认低 priority。

我们学习这条 lineage主要是：

> **scientific concept的 definition / identification会怎样逐代收紧。**

---

# LINEAGE 18 — Video / World Models：从“生成未来画面”到“什么 latent variable真正承载可迁移 dynamics”

## 18.1 Video generation首先解决 visual fidelity + temporal coherence [FIELD]

早期 text/image-to-video的重要目标：

- 生成清晰 frame；
- 保持 temporal consistency；
- 长度更长；
- obey prompt。

这时 video model主要被理解为：

> **generative model of visual sequence。**

---

## 18.2 World-model framing — 生成的不是“视频”，而是 environment transition [FIELD]

如果 video generation被用于：

- planning；
- robotics；
- games；
- embodied simulation；

那么目标改变：

> 不是只要看起来像合理视频，
> 而是 action-conditioned future必须反映 environment dynamics。

于是需要显式加入：

- action；
- state；
- camera；
- geometry；
- controllable interaction。

### Primitive change

```
p(video | text)
→ p(future observation | state, action)
```

同一个 visual generator获得新的 scientific role。

---

## 18.3 Dexterous World Models — static digital twin缺少 interaction dynamics [FIELD]

**Dexterous World Models (CVPR 2026)**

论文观察：

> 现代 3D reconstruction可轻松做高质量 static digital twin；
> 但这些 twin主要支持view synthesis / navigation，不会因手的action发生合理变化。

于是用：

- static 3D scene render；
- egocentric hand-motion sequence；

condition video diffusion生成 interaction outcome。

### Question-forming move

```
digital twin quality
→ interactive world response
```

这不是“video quality再提高”。

它把：

> **action-conditioned change**

设成了新的 adequacy criterion。

---

## 18.4 VideoWorld 2 — appearance modeling与 task dynamics可能不该由同一个 latent承担 [FIELD]

**VideoWorld 2 (CVPR 2026)**

如果直接从 real-world videos学习 long-horizon control：

> pixels里大量 variation来自 appearance，
> 但 agent真正需要的是 task dynamics。

论文引入 dynamics-enhanced latent dynamics model：

- pretrained video diffusion负责 appearance；
- latent codes聚焦 compact task-related dynamics；
- autoregressive latent model用于 policy / long-horizon reasoning。

### Primitive change

```
video latent = compressed visual future
→ separate appearance from transferable action/task dynamics
```

### Genealogy value

这与 speech semantic/acoustic disentangling有结构相似。

但不能机械迁移：

> 两者 decomposition的物理意义完全不同。

真正 shared research move：

> **当一个 generative representation承载太多 nuisance variation，任务需要的 dynamics可能被稀释。**

---

## 18.5 Motus — fragmentation itself成为 obstacle [FIELD]

**Motus: A Unified Latent Action World Model (CVPR 2026)**

field常有分别的：

- understanding model；
- video generator；
- action policy；
- inverse dynamics。

论文framing：

> 真实 embodied agent需要这些能力协同，
> 独立 model使 heterogeneous data无法被统一利用。

于是用：

- multiple experts；
- shared latent action/world representation；
- flexible scheduler；

统一多种 modeling mode。

### 这类 paper对taste的双面性

正面：

> 它识别的是 task fragmentation / information sharing问题。

负面：

> 很容易进入 giant unified system engineering。

对我们：

> 主要作为 field-evolution例子，
> 不作为默认执行 shape。

---

## 18.6 Autoregressive video — long horizon暴露 error accumulation与cache state [FIELD]

**STARFlow-V / ARCache (CVPR 2026)** 等工作展示：

当 video generation变成 autoregressive segment generation：

> 前一段 output会作为下一段 context。

于是 classic问题出现：

- temporal error accumulation；
- cache reuse error；
- causal generation speed；
- residual correction。

### Primitive change

```
generate one clip
→ recursively generate a stateful trajectory
```

这时：

> generation error不再只是frame quality，
> 而会改变未来 state distribution。

与 autoregressive LM / imitation learning的 compounding error有结构相似。

---

## 18.7 World-model lineage真正值得我们学习的地方

不是：

> world model很热门。

而是：

> **当一个 generative model从“内容生成器”变成“环境模拟器”时，evaluation object和representation requirement都会变。**

同一 video quality metric：

> 可能完全不足以评价 planning utility。

这又回到一个反复出现、但不能机械化的 pressure：

> deployment role改变了“什么叫正确模型”。

---

# 19. 四条新 lineage的交叉分析

---

## 19.1 “Unified”有至少三种完全不同含义

### Unified objective
CoCa / BLIP：
> understanding + generation objectives。

### Unified representation
SpeechTokenizer：
> semantic + acoustic information。

### Unified agent/world model
Motus：
> understanding + generation + action。

这三个都叫 unified。

但 research problem分别是：

- objective compatibility；
- information allocation；
- capability/system integration。

所以：

> **看到热门词 unified 完全不能判断题型。**

必须恢复它解决的 fragmentation到底是什么。

---

## 19.2 Information bottleneck常常不是“压得太狠”，而是“压错东西”

Speech：
> codec保留 waveform，但未必保留LM需要的 semantics/context。

World model：
> video latent保留appearance，但 task更需要dynamics。

VLM：
> current-query pruning保留当前 salient region，但未来query需要别的信息。

CoT：
> text rationale保留可读解释，但未必保留真实 causal computation。

### 更准确的共同点

不是：

> compression bad。

而是：

> **representation objective 与 downstream use之间的信息优先级不匹配。**

---

## 19.3 Relation between capabilities可以比单个 capability更有研究价值

Unified multimodal：
> understanding ↔ generation。

Speech：
> semantics ↔ acoustics ↔ context。

World models：
> appearance ↔ dynamics ↔ action。

CoT：
> verbal explanation ↔ parametric belief ↔ final answer。

强 paper经常不是：

> 再把每一项做强一点。

而是：

> **原来两项之间的 relation被默认了，但没有被真正识别。**

---

# 20. 当前进一步确认的 crowded vocabularies

以下词已经不能作为 novelty carrier：

- unified
- latent reasoning
- self-reward
- semantic token
- world model
- adaptive
- dynamic
- faithful
- causal
- multimodal
- intrinsic reward
- hierarchical token
- student-aware
- budget-aware

以后看到 candidate依赖这些词带来“新鲜感”时：

> 先删词再读。

删完还能说清：

> 哪个 prior inference / relation / constraint改变了，

才继续。

---

# 21. 目前 genealogy library 已经覆盖的主要 problem-growth families

不是模板，只是 coverage检查：

- successful algorithm → internal signal decomposition
- resource amount → resource allocation/control
- coarse outcome → transition/local event
- crowded explanation → new explanatory decomposition
- theorem → assumption audit
- artificial evidence → natural evidence
- heuristic zoo → invariant/property
- prediction unit → representation/statistical structure
- scaling scalar → structured resource variables
- supervision → learner-relative supervision
- architecture → task computation/geometry
- modality bridge → interface bottleneck
- compression → future-information preservation
- turn sequence → real-time concurrent process
- observed limitation → measurement re-attribution
- endpoint explanation → trajectory dynamics
- objective family → objective relation/unification
- tokenization → information allocation
- explanation concept → identification/metric refinement
- content generator → action-conditioned world transition

如果下一阶段继续读，目标不是：

> 再把这张表扩成50条。

而是：

> **开始比较哪些 moves在不同领域出现时其实有不同 prerequisites，哪些只是 surface 同名。**
