# chasing trends 科研搜索指南（Canonical）

目标不是追热点本身，而是利用快速变化的 literature / deployment / open artifacts 进入值得长期理解的 scientific territory。

## 1. Source 的角色

- **Academic lineage**：告诉我们 parent question、已建立结论、真正未识别之处。
- **Industry/deployment**：证明 operational pressure 真实，不自动证明 mechanism 新。
- **Open checkpoints / HF / startup artifacts**：提供可实验杠杆，不自动构成 scientific question。

不要把一个新产品 knob、公开 checkpoint 或 future-work sentence 直接变成 candidate。

## 2. Territory first

先恢复一个 lineage，然后决定是否值得住进去。

好的 territory 应该让我们能够：
- 跑一个 strong/open baseline；
- 在真实任务或自然数据上看行为；
- 通过多次探索逐渐积累 object knowledge；
- 即使没有 paper，也留下可复用理解。

不要先决定要做 failure→method、adaptive compute、memory、routing 等 paper template 再找例子。

## 3. Strong baseline / artifact archaeology

使用公开 artifact 前先确认：
- 版本/recipe/checkpoint 真正可比；
- 所谓 matched pair 是否真的只差目标变量；
- published mother effect 在我们可实验 regime 里复现；
- evaluator / harness / tokenizer / post-processing 没有偷换 quantity。

CT05–09 / ShapeLab 已证明：架构 intuition 和公开 checkpoint 很容易在这里失真。

## 4. Observation before candidate

先记录观察，不起 CT 编号。

Observation 至少要：
- 在真实或自然 setting 中存在；
- 简单 baseline / generic drift / scale / recipe 不能解释；
- 有 fresh subset/seed/setting 支持；
- 一句话可讲清。

如果 observation 只是“某个 blog 直觉没成立”，那是 territory knowledge，不是 candidate。

## 5. Ownership

只有 observation 值得解释时才做深 owner audit。

危险形状：
- strong paper 的 obvious future work；
- parent diagnostic + 已知 mechanism；
- 更便宜、更干净、更 deployable 的 successor；
- mathematically prettier formulation of an already-owned relation；
- known AI failure 换一个 current model/setting。

Reviewer compression 仍然是最有用的问题：

> **“你不就是 ______ 吗？”**

## 6. Candidate

只有 observation + importance + owner gap + feasible confirmation 同时成立，才创建正式 candidate ID。

Candidate 不因为：
- 热；
- artifact 新；
- E01 便宜；
- method 很容易接；
而获得额外分。

## 7. Method/actionability

CT03 的永久教训：

> **good signal ≠ good supervision ≠ deployed action ≠ downstream gain**

任何 method story 都拆成：

> Failure → Bottleneck → Action → Outcome

如果 Bottleneck→Action 没有自然、principled 的控制面，不进入 loss/module search。

## 8. Discovery / confirmation

Discovery 阶段允许探索、换解释、看 curve。

Confirmation 阶段才冻结：
- metric；
- held-out data；
- controls；
- statistical test；
- stop rule。

Continuation threshold 是投资规则，不是“现象是否存在”的定义。

## 9. Compute

便宜 pilot 是好事，但不是 topic-quality gate。

CT08 的教训是：如果 published mother effect 只在我们无法干净操纵的规模存在，不能因为另一个便宜 regime 可跑就把它当作同一个科学问题。

## 10. 当前工作单位

> **territory → baseline → observation → candidate**

不是：

> lineage → paper gap → CTxx → rescue。

允许一整个 territory 最后没有 candidate。
