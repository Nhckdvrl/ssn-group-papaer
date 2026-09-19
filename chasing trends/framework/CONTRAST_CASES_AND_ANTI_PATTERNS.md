# Contrast Cases & Anti-Patterns — 2026-09-19

> 这份文件专门防止一个危险：
>
> > **只读 accepted / strong papers，然后把每一篇都事后解释成“作者洞察了一个漂亮问题”。**
>
> 真实科研里：
>
> - 有些 paper 很强，但主要靠规模 / 工程；
> - 有些 paper 有漂亮现象，但不适合我们的执行条件；
> - 有些 paper 的方法有效，却很难说 method 是从 analysis 自然推出；
> - 有些方向本身正确，但已经 crowded 到几乎只能靠 incremental axis；
> - 有些 paper 的 contribution shape 值得尊重，却不是我们应该复制的 taste。
>
> 所以 positive genealogy 必须和 contrast case 一起学。

---

# 1. Strong paper ≠ suitable project

这是整个 `chasing trends` 必须长期保留的区分。

一篇 paper 可以：

- venue 很强；
- experiment 很扎实；
- impact 很大；
- conclusion 很可靠；

但仍然完全不适合我们做。

至少要分：

### Scientific value
这个问题是否真的增加理解 / 改变方法？

### Paper quality
作者是否充分证明 claim？

### Execution shape
我们是否能用现实算力 / 数据 / 工程做出来？

### Taste transferability
它的问题形成方式是否值得学习？

这四个不能混成：

> “这篇很强，所以我们应该做类似的”。

---

# 2. Contrast A — Giant sweep science：很可信，但不能成为默认执行范式

## Case: massive SFT empirical studies

2025 出现使用 **1000+ fine-tuned models** 的系统 SFT study。

这种 work 很有价值：

- 能系统比较 data / model / dataset；
- 能统计稳定 regularity；
- 能减少 cherry-picking；
- 容易给 field 提供 empirical baseline。

但对于我们：

> 如果一个 claim 必须靠数百到上千个 training run 才能成立，
> 它就是 execution mismatch。

### 真正可迁移

- 它发现了哪些 candidate variables；
- 哪些 proxy 稳定；
- 哪些 layer / perplexity signal值得在小规模验证。

### 不能迁移

> “我们也做一个 comprehensive sweep”。

### Anti-pattern

```
interesting question
→ evidence only convincing with huge grid
→ no small discriminative experiment
```

默认 KILL for us。

---

# 3. Contrast B — Beautiful architecture idea, catastrophic training bill

## Case: Recurrent Depth latent reasoning

**Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach (NeurIPS 2025)**

从 intellectual perspective：

> 很漂亮。

它把：

> test-time compute = more generated tokens

改成：

> test-time compute = more recurrent latent depth。

而且与 Universal/Looped Transformer lineage有自然关系。

但 proof-of-concept：

- 3.5B；
- from scratch；
- ~800B training tokens。

### 学什么

> changed premise 可以让旧 architecture primitive 获得新 role。

### 不学什么

> 看到漂亮 architecture → 自己训一个新的 3B backbone。

### Anti-pattern

> **Idea quality不能抵消 validation cost。**

formal candidate gate里必须始终有：

> cheapest decisive evidence。

---

# 4. Contrast C — Method zoo incrementalism

## Case: visual-token compression 2025–2026

这个方向现在同时有：

- attention score；
- pruning；
- merging；
- clustering；
- layer-wise；
- instance-wise；
- variation；
- approximation error；
- FlashAttention compatibility；
- dynamic video；
- spatiotemporal；
- multi-turn；
- dual-stage。

其中很多 paper 本身做得很好。

但作为“下一题”的来源，危险极高。

### 为什么

当一个 surface 到这种密度以后：

> 换 metric / layer / module 很容易有 gain，
> 但 reviewer compression也极强。

例如：

> “又一个 token pruning score。”

### 真正能重新打开空间的通常不是

> score更聪明。

而是：

> **objective / deployment contract 变了。**

multi-turn example就是这样：

> current-query relevance不再等于 future utility。

### Anti-pattern

```
crowded method family
→ find one untried module
→ benchmark gain
```

没有更深 problem change时：

> 低 priority。

---

# 5. Contrast D — Hot new primitive can become crowded in one conference cycle

## Case: latent visual reasoning, CVPR 2026

表面上很“新”：

> 不再只用 text CoT，而让 VLM 用 latent visual tokens思考。

但同一时期已经有多个相近方向：

- Machine Mental Imagery / Mirage；
- Latent Implicit Visual Reasoning；
- multimodal latent interleaving；
- visual reasoning token。

### Lesson

一个 idea 在我们第一次看到时“感觉新”，不等于：

> field里是空白。

尤其 AI 时代：

> preprint / parallel discovery会在几个月内把一个 conceptual move占满。

### Anti-pattern

> **单篇 paper novelty illusion。**

必须问：

> 这是一篇孤立 breakthrough，
> 还是已经形成 cluster？

这就是 breadth scan 必须先于 candidate registration 的原因。

---

# 6. Contrast E — Benchmark failure ≠ scientific question

## Weak shape

```
perturb input
→ score drops
→ conclude model is brittle
```

这类 work有时能发，也能提醒 practitioner。

但如果我们目标是 Main-sized research question：

> 往往不够。

### Stronger negative paper shape

**Flaw or Artifact?**

不是只说：

> prompt换了，score变。

而是：

> prior literature把这个 variation解释成 model weakness；
> instruction-tuned model的目标与这个解释有冲突；
> 重新审 scoring channel后，发现相当部分 variation来自 evaluator；
> 因而 attribution改变。

### Distinction

```
effect
vs
interpretation-changing effect
```

### Anti-pattern

> 收集 failure，而没有回答：
>
> **这个 failure让我们对什么已有结论改观？**

---

# 7. Contrast F — New metric / evaluator can quietly become the whole project

用户明确不偏好 evaluator / benchmark方向。

这不是说：

> measurement不重要。

恰恰相反，genealogy里 measurement经常非常重要。

但需要区分：

## Measurement as identification tool

例：
> 新测量能区分两个 competing explanation。

这是 science。

## Measurement as deliverable

例：
> 做一个新的 judge / benchmark / aggregate score。

这可能是好 paper，但不是我们当前偏好的 contribution shape。

### Anti-pattern

```
interesting scientific question
→ cannot measure it
→ spend whole project building benchmark/evaluator
→ benchmark itself becomes paper
```

如果 user的兴趣已经被 infrastructure吞掉：

> KILL。

---

# 8. Contrast G — Training dynamics biography

这是从 S03 真实失败中继承的最重要 anti-pattern之一。

## Bad shape

> model在 checkpoint A先学X；
> checkpoint B再学Y；
> SFT阶段出现Z；
> RL阶段出现W。

看起来像 development science。

但如果：

- training recipe换了顺序就变；
- data mixture改变就变；
- optimizer/budget改变就变；
- checkpoint spacing改变现象；

那么研究的不是：

> general mechanism。

而是：

> **这一次训练 run 的 biography。**

### literature calibration后的升级版判断

2025 training-dynamics paper并没有说明 biography题都不能做。

它们比较可信时通常有：

- 明确 local quantity；
- 多 architecture/data复现；
- theory/controlled model；
- causal intervention；
- state variable而不是时间标签本身。

### Anti-pattern

> “when during training”被误当成“why”。

---

# 9. Contrast H — Student/teacher mismatch 已经是 cluster，不能继续用 generic wording

2025 distillation出现密集主题：

- capacity gap；
- simpler CoT；
- key step；
- curriculum；
- student trajectory；
- selective teacher intervention；
- fidelity/generalization gap。

因此：

> “teacher太强学生学不会”

已经不是新 insight。

### 如果 future paper只做

> difficulty-aware distillation

reviewer很容易压成：

> another student-adaptive KD.

### 真正需要的

必须有一个更具体、可辨识的 learning quantity，例如：

- 哪种 student state决定 supervision transfer；
- 何种 signal在 student capacity边界附近改变；
- 哪个 current proxy把两种 instructional effects混了。

否则：

> surface crowded。

---

# 10. Contrast I — “Adaptive”不是 scientific contribution

我们现在在很多 lineage都看到 adaptive：

- adaptive test-time compute；
- adaptive diffusion schedule；
- adaptive visual-token pruning；
- adaptive curriculum；
- adaptive teacher intervention；
- adaptive computation depth。

如果机械总结：

> adaptive方法很强。

这几乎必死。

### 真正问题

adaptive policy至少需要：

1. state：根据什么状态？
2. action：调什么？
3. objective：优化什么真实量？
4. counterfactual：不同 state 下为什么应该不同？
5. identification：state 与 marginal action value之间有证据吗？

没有这些：

> “adaptive”只是多一个 controller。

---

# 11. Contrast J — “Selective / sparse”也不是 scientific contribution

同样：

- high-entropy tokens；
- key reasoning steps；
- visual token pruning；
- parameter restoration；
- selective negative feedback；
- selective teacher intervention。

都可以表面归成：

> only a subset matters.

这非常容易诱发垃圾 idea：

> 找一个新 importance score。

### 必须区分为什么 subset matters

- decision branching；
- student mistakes；
- visual redundancy；
- knowledge-destructive update；
- failure onset；
- computation bottleneck。

如果 causal reason不同：

> 它们不是一个 reusable method template。

---

# 12. Contrast K — “Latent reasoning”已经不是 novelty

截至 2025–2026：

- recurrent latent depth；
- continuous/latent CoT；
- latent visual reasoning；
- hidden-state recurrence；
- internal reasoning token；

已经是大 cluster。

所以：

> “不用显式CoT，在latent space里reason”

本身无法构成 topic。

### 有价值的问题可能仍存在

但必须落到：

- computation control；
- observability；
- training signal；
- faithfulness；
- modality-specific bottleneck；
- architecture constraint；

中的具体 unresolved pressure。

### Anti-pattern

> fashionable noun substitution：
>
> explicit → latent
>
> 就当创新。

---

# 13. Contrast L — Cross-domain analogy without source genealogy

最危险的跨领域迁移：

> diffusion有 adaptive schedule  
> → LLM也做 adaptive schedule。

或：

> robotics用 action chunk  
> → reasoning也 chunk。

或：

> SAM看 local neighborhood  
> → RL也做 sharpness。

这叫：

> **surface analogy。**

### 合格的迁移必须恢复 source pressure

例如 TORS 的真正链：

```
multiple fast-sampling branches
→ matched design space
→ schedule dominates
→ trajectory geometry
→ nonuniform schedule
```

要迁移的如果只是：

> nonuniform schedule，

就是错的。

需要先问目标域有没有：

> matched design-space attribution缺失；
> geometry/state真的定义 marginal compute value。

没有：

> 不迁。

---

# 14. Contrast M — Reviewer compression is stronger in trendy fields

越热门：

- RL reasoning；
- test-time scaling；
- VLM compression；
- latent reasoning；
- diffusion acceleration；

越容易发生：

> 你觉得差异很大，reviewer觉得“X + 一个 heuristic”。

### 所以 trendy topic的 novelty bar不是更低

反而通常更高。

必须能回答：

> 如果把 method acronym删掉，
> 新 paper到底让 field学到了哪一个此前没有的 relation / constraint / object？

如果答案还是：

> performance更好，

很危险。

---

# 15. Contrast N — “Paper成功”有时靠作者资源，不代表 idea formation可复制

例如：

- 从头训 foundation model；
- 海量真实/合成 speech；
- 1000+ model sweep；
- 多 robot embodiments；
- gigantic human study；
- 大型 proprietary evaluator。

这类 paper可以提供非常好的 scientific evidence。

但我们不应该从它推导：

> 这种问题值得我们做。

### 必须额外问

> 有没有 small-scale discriminative pilot？

如果没有：

> 只作为 taste source，不作为 execution source。

---

# 16. Contrast O — Simple method不自动说明问题深

最近很多强论文：

> finding很深，method只改一个 weight。

这容易造成另一个机械误区：

> “小改动 + 大提升 = 好题”。

不是。

简单 method只有在：

> **design choice被前面的 diagnosis强约束**

时才有意义。

否则：

> 一个 coefficient / weight / threshold调出提升，

仍然可能是 heuristic。

### Strong

```
specific mismatch
→ predicts direction of correction
→ one-line correction
→ behavior changes exactly where predicted
```

### Weak

```
try small tweak
→ it works
→ invent explanation afterwards
```

---

# 17. Anti-retrospective-storytelling rule

这是这次 genealogy project必须特别防的。

看 finished paper时：

> Introduction已经把故事写得极顺。

我们很容易以为：

> 作者从第一天就知道问题在哪里。

真实研究通常不是这样。

所以 genealogy只允许恢复：

- literature state；
- observable tension；
- available methods；
- final paper的 logical dependency。

不能擅自恢复：

> 作者脑内 chronology。

### 强制语言

用：

> “在这篇出现前，literature已经具备X；它把Y改成了research object。”

不要写：

> “作者看到论文A，于是自然想到B。”

除非作者自己明确说明。

---

# 18. Anti-template rule

当某个 meta-pattern连续出现3次以后：

> 立即把它加入“禁止机械 generator”表。

当前已经禁止直接作为 generator 的包括：

- hidden assumption；
- representation bottleneck；
- train-test mismatch；
- objective mismatch；
- adaptive compute；
- selective update；
- sparse key steps；
- latent reasoning；
- invariant；
- decomposition；
- measurement artifact；
- success-solution becomes next assumption。

这些都可以继续作为 reading vocabulary。

不能作为：

> “今天就搜10个这种题”。

---

# 19. 什么样的 contrast study最值得继续收集

下一批不要只收 weak paper。

更有价值的是成对比较：

### Pair A
两个 paper都解决同一个 problem：
- 一个靠 module stacking；
- 一个重新定义 object。

### Pair B
两个 paper都有大 gain：
- 一个 hidden compute；
- 一个 compute-normalized仍成立。

### Pair C
两个 negative papers：
- 一个只是 stress test；
- 一个改变 attribution。

### Pair D
两个 mechanism papers：
- 一个只画 probe；
- 一个 mechanism能预测 intervention。

### Pair E
两个 theory papers：
- 一个 toy impossibility；
- 一个 assumption change会影响 practical regime。

这样才能学：

> 为什么一些 story有“内在必要性”，另一些只是完整。

---

# 20. 对未来 candidate gate 的新增约束

等用户以后允许正式找题时，每个 seed除了 novelty / compute，还要多过：

## Contrast Gate

> 最近最像的 accepted paper中，有没有一个更简单的解释：
>
> “他们能发，是因为有我们没有的资源 / sweep / benchmark / deployment / proprietary model”？

如果有：

> 不能只学 surface。

## Story Necessity Gate

> 把所有 method module名字遮掉以后，
> 每一步是否仍然由前面的 evidence逼出来？

## Cluster Density Gate

> 这个 conceptual move是单篇，还是过去6–12个月已经有5篇平行工作？

## Identification Gate

> 结果若出现，能排掉哪个 competing interpretation？

## Execution Asymmetry Gate

> negative/ambiguous result是否需要巨大额外实验才能解释？

这些 gate以后再并入正式候选工作流。

当前：

> 仍然只用于读论文。
