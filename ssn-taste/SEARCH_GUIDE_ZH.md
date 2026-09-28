# ssn-taste 科研搜索指南（Canonical）

目标只有一个：

> **找到 Sasano 会认为自然、清楚、结果本身值得知道，并有 ACL / EMNLP / NAACL Main 潜力的问题。**

当前 **selected = 0**。不要为了让 ledger 非空而注册新 Sxx。

## 1. 每轮先重新校准 Sasano

优先读取 Sasano 本人最近的真实判断，尤其关注：
- 他为什么觉得一个结果有意思 / 没意思；
- 他如何压缩 novelty；
- 他什么时候认为 RQ 太多、finding 与 RQ 不对齐；
- 他对“结果不意外”“只是更干净的验证”“只是换 setting”的反应。

不要只背抽象 slogan。

## 2. 禁止三种直接起题方式

### A. 理论二分先行
> A 和 B 概念上不同，所以问 LLM 会不会区分。

S11/S12 已证明：漂亮 distinction 可以没有稳定、自然、可操纵的模型变量。

### B. 单篇 anomaly 先行
> 某篇论文有怪现象，我们来解释 why。

原作者或后续工作通常已经拥有 parent；剩下容易只是 successor cell。

### C. tension 直接 candidateize
> Paper A 与 Paper B 有 latent tension，所以写 RQ。

Tension 可以帮助选择 territory，但不能代替我们自己的 empirical knowledge。

## 3. Territory first

先选一个值得住进去的 scientific object。允许：
- 精读 lineage；
- 复现 strongest baseline；
- 看 code/checkpoint；
- 做 natural benchmark 上的 exploratory cuts；
- 找 failure gradient；
- 被结果推翻原假设。

此阶段：
- 不创建 Sxx；
- 不写 paper title；
- 不写宏大 mother question；
- 不强迫 A/B/C worlds；
- 不做“为了过 gate”的 synthetic world。

## 4. Strong baseline before clever intervention

不是“复现一个数字”就算 baseline。

至少要知道：
- baseline 的合理强配置；
- 哪些 slice 真差；
- failure 是否随 scale / recipe / prompt / data 消失；
- metric / parser / truncation 是否会改结论；
- 最简单替代解释是什么。

很多真正的问题应该从“baseline 做强以后仍然不对劲”长出来。

## 5. Observation

只有我们自己看到稳定 pattern 后，才第一次允许写：

> **我们观察到 O。**

O 至少应满足：
1. 不是单点；
2. fresh seed / natural subset / matched setting 中基本稳定；
3. 不是 parser / wording / metric / generic capability artifact；
4. 最简单 baseline 解释失败；
5. 一句话可讲清；
6. 结果本身足以让普通 reviewer 觉得“这个值得知道”。

Discovery 阶段可以探索；不要用人为 continuation threshold 把一个真实效应写成 null。

## 6. Candidate birth

只有满足下面四件事才创建新 Sxx：
- **Observation**：已有真实、稳定的现象；
- **Importance**：它改变一个 live belief，而不是只证明两个内部变量不同；
- **Ownership**：nearest prior 没有拥有同一 observation / consequence / decisive contrast；
- **Confirmation**：有可承受、能分辨主要解释的 held-out experiment。

这时才写 one finding ↔ one RQ。

## 7. Instrument discipline

进入 candidate 前确认：
- prerequisite 能力成立；
- manipulation 真对应 scientific variable；
- readout 真回答 RQ；
- positive/negative controls 正常；
- logically equivalent forms 不灾难性翻转；
- scorer/parser/gold 正确；
- synthetic diagnostic 被拿掉后，真实 observation 仍然存在。

如果需要不断加 wording、control、taxonomy 才让 construct 成立，停。

## 8. Training/post-training 特别规则

先证明 phenomenon stability，再解释 mechanism。

合理的 seed / modest budget / family perturbation 若会改变故事，优先判断为 recipe biography，而不是急着加更多机制实验。

S03/S09 是 canonical warning。

## 9. Method 只能后置

如果最终走 failure→method：

> **Failure → Bottleneck → Action → Outcome**

四层逐层建立。不要因为 diagnosis 漂亮就假设一定有一个自然 fix。

## 10. 立即停止的信号

- 为了“让现象出现”开始扫 prompt/model/threshold；
- candidate 每失败一步就新增一个解释分支；
- novelty 越来越依赖 exact cell；
- synthetic assay 同时创造并定义整个 scientific object；
- 30 秒内无法说明结果为什么重要；
- 强结果只能写成“两个 controller 不一样”之类 mechanistic detail；
- 开始用更多规则保护已经命名的 Sxx。

允许长期 **0 selected**。

## 11. 文件纪律

只维护本文件、`README.md`、`SELECTED_TOPICS.md`、`FAILED_TOPICS.md` 与真正的 experiment artifacts。

不要再创建 observation portfolio、claim map、preflight template、round log 等流程文件。
