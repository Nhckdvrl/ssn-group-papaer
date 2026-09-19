# Lessons from ssn-taste

这份文件只保留旧 `ssn-taste/` 对新路线仍然有用的经验。具体历史候选不作为 positive taste exemplar。

## 1. 必须保留的纪律

### Restore repo first

正式状态以最新 repo 为准，不相信过期 handoff。

### Reviewer compression

任何 idea 都要问：

> reviewer 最狠会把它压成什么？

如果去掉术语后只剩 setting change，说明 novelty 很薄。

### Nearest-prior deep audit

危险 prior 要读 claim、decisive experiment 与 ownership boundary，不靠标题查重。

### Data / compute gate

选题质量包含执行成本。若生死只能靠巨大模型、recipe sweep、昂贵 simulator 或大量人工判断，默认不适合当前项目。

### Anti-resurrection

failed topic 不能换标题复活。旧 ledger 的核心价值是防止重复走同一个 parent。

### Identification before rhetoric

漂亮 explanation 必须能让 competing explanations 对某个实验给出不同 prediction。

---

## 2. 旧路线哪里走得过头

### 纯 scientific mother question 被当成唯一正确 paper type

这让大量候选被迫承担：

- multiple possible worlds；
- null/opposite outcome 也 Main-sized；
- mechanism 必须独立成科学故事。

对 method / systems / theory paper 不必如此。

### “behavior 已知 → mechanism”被过度警惕

真正危险的是：

> generic mechanism follow-up。

如果 mechanism 会改变：

- method design；
- scientific interpretation；
- boundary prediction；

它仍然可以是强 work。

### benchmark 被过度排斥

benchmark 不能成为唯一 contribution，但方法论文需要标准 benchmark 证明实际价值。

### 方法被默认视为“不够科学”

新路线不反对 method。反对的是：

> arbitrary module stacking + post-hoc explanation。

---

## 3. S03 的关键教训：training biography

S03 试图解释 stopping capability 在 pretraining/post-training 中如何形成。

执行后暴露：

> “training stage”并不是干净变量。

它同时捆绑：

- data mixture
- serialization
- optimizer
- budget
- SFT/preference stage
- model-family interface

当合理 recipe 改动就重写 developmental story 时，研究对象变成：

> 某次 training run 的 biography。

新路线因此优先：

- within-run measurable quantity；
- local intervention；
- direct state/gradient/objective variable；

而不是宏观“能力何时形成”的时间线。

---

## 4. S09 的关键教训：path-dependent construct

S09 的 “memory age/history” 同时绑定：

- acquisition time
- recency
- gradient exposure
- spacing
- dose
- optimizer state

即使 within-recipe control 可以改善，也很难形成 recipe-stable quantity。

因此 training/continual-learning 题优先使用：

- current uncertainty
- current accessibility
- gradient/update quantity
- interference
- representation/use
- directly observable state

而不是把历史摘要标签直接当 causal variable。

---

## 5. FAILED ledger 的主要死法

旧候选反复集中在五类：

1. **Parent 已做掉 same decisive unknown**  
   不是关键词 overlap，而是核心 distinction 已回答。

2. **Mechanism 漂亮但没有新的解释/方法压力**  
   只剩 probe、head、vector、geometry 图。

3. **跨领域只迁移名词**  
   没有 target-field 独立 pressure。

4. **Exact-cell novelty**  
   为逃 prior 越切越窄。

5. **Experiment explosion**  
   为救 candidate 不断增加 arms、models、recipes、controls。

这些 death mode 在 chasing-trends 中仍然成立。

---

## 6. 新旧规则的真正融合

旧路线保留：

- question / pressure 不能伪造；
- nearest prior；
- identification；
- reviewer compression；
- execution feasibility；
- anti-resurrection；
- experiment explosion kill。

新路线放宽：

- 不要求所有 paper 都是 pure science；
- 不要求 null result 都 Main-sized；
- 允许 method 作为主要 contribution；
- 允许 benchmark 作为 validation；
- 允许从 known failure 出发，只要新的 diagnosis/constraint 真改变理解或设计。

最终原则：

> **不是降低标准，而是把标准从“论文必须长成某一种科学形状”改成“问题、证据和方法之间必须有真实必要性”。**

正式流程见：

> `../SEARCH_GUIDE_ZH.md`
