# Research Taste Recalibration

这份文件记录 `chasing trends` 最重要的一次纠偏：**不要把一种喜欢的 paper shape 误写成唯一的选题模板。**

## 1. 为什么要纠偏

最初我们从 pure-science / mechanistic search 转向更偏热点、方法、reasoning/post-training 的论文时，曾把一个常见强结构概括成：

> failure → diagnosis → mechanism → method → benchmark → ablation

这个结构当然可以很好，但它只是**一种** genealogy。

如果把它当 generator，会重复旧错误：

> 先定义“好题长什么样”，再到处寻找能填进去的现象。

真正应该训练的是：

> **paper 在出现以前，literature 已经走到哪里；作者重新定义了哪个 basic object / assumption / relation；为什么这个 opening 在当时真实存在。**

## 2. Paper shape ≠ idea genesis

最终论文都可能写成：

- motivation
- method
- experiments
- analysis

但 idea 的来源可以完全不同，例如：

- successful objective 被拆成不同 learning operations；
- deployment constraint 原本没有进入 policy state；
- method zoo 缺少统一 design space；
- analysis unit 太粗，掩盖 failure onset；
- crowded object 仍有新的 explanatory decomposition；
- theorem 的结论依赖一个 hidden asymptotic premise；
- prior phenomenon 只在 artificial evidence regime 成立；
- mature heuristic family 缺少解释 success 的 common property；
- 新 scale / modality / system role 让旧 abstraction 的语义改变。

这些只能作为**观察到的 research moves**，不能再变成 checklist。

详细实例见：

- `../academic/GENEALOGIES_01.md ... 04.md`
- `PARADIGM_ATLAS_ZH.md`

## 3. 真正要从强论文学什么

对每篇 core paper，重点恢复：

1. **Pre-paper state**：当时已经知道什么？
2. **Immediate parents**：reviewer 最可能用哪些 work 压它？
3. **Saturated axes**：哪些方向已经做烂？
4. **Hidden opening**：哪个 assumption / relation / unit 没被当成 object？
5. **First decisive evidence**：哪一个最小结果让新问题站住？
6. **Growth chain**：seed 怎样长成 Main story？
7. **Reviewer compression**：为什么它不是“旧题 + 一个新 setting”？
8. **Execution shape**：这个 research move 是否适合我们的资源？

深读规范见：

> `PAPER_GENEALOGY_GUIDE.md`

## 4. Related work 的角色

related work 不只用于：

> 找一篇很像的 paper → kill。

它还用来恢复：

- field 的 dominant decomposition；
- inherited assumptions；
- saturated coordinates；
- missing relations；
- changed premises；
- parallel discoveries。

真正有价值的 opening 往往不是：

> 某个格子没人填。

而是：

> **已有 work 都在同一 abstraction 下推进，而这个 abstraction 开始挡住理解或方法。**

## 5. Cross-domain 的正确用法

允许大量阅读 CV、generation、speech、robotics、optimization、theory、science FM。

但迁移的不是：

- adaptive
- latent
- hierarchy
- curriculum
- world model
- bottleneck
- invariant

这些词。

要迁移的是 source paper 中真实的：

- constraint；
- conflict；
- identification logic；
- state/control relation；
- resource law；
- representation requirement；
- failure provenance。

然后必须在 target field 找到**独立存在**的 pressure。

## 6. 强 paper ≠ 适合我们

以后分开判断：

- **Intellectual value**：问题和证据是否真改变理解？
- **Paper quality**：claim 是否证明充分？
- **Execution suitability**：我们能不能现实地做？
- **Taste transferability**：它的问题形成方式是否值得学？

允许：

> intellectual A / execution D。

例如从头训练 foundation model、1000+ run sweep 可以是强科研，但不是我们的默认 project shape。

反例库见：

> `CONTRAST_CASES_AND_ANTI_PATTERNS.md`

## 7. 当前稳定结论

现在最重要的不是背“18 条 genealogy”或“17 种 paradigm”。

稳定原则只有几条：

- literature 先于 brainstorm；
- pressure 先于方法名；
- same decisive unknown 比关键词 overlap 更重要；
- basic object 的变化必须由真实 evidence/constraint 逼出来；
- trend 越热，越需要 cluster-density 与 reviewer-compression audit；
- execution cost 是 topic quality 的一部分；
- broad scan 只负责校准，formal candidate 必须回 nearest prior 深读。

当前正式流程以：

> `../SEARCH_GUIDE_ZH.md`

为准。
