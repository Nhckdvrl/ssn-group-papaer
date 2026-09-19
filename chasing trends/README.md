# chasing trends

建立日期：2026-09-19  
当前状态：**V2 taste calibration — no candidate search until user approval**

这个目录不是“追热点方法论文模板库”。

它的目标是建立一套更现实的 AI 科研选题方法：

> **从优秀论文与真实 related-work 结构中，反向学习问题是怎样形成的。**
>
> 先找 scientific / methodological pressure，
> 再让最自然的 paper shape 自己长出来。

---

# 1. 核心纠偏

最初版本过度强调：

> failure → diagnosis → method → benchmark

这只是强论文的一种范式，不是统一搜题公式。

以后必须区分：

1. **Question provenance**  
   问题从哪里来？

2. **Related-work relation**  
   新 paper 相对 prior 到底增加了什么？

3. **Final paper form**  
   最终长成 science / mechanism / method / theory / simplification / unification / scaling 中哪一种？

不能从第 3 点反推第 1 点。

也就是说：

> 不允许先决定“我要找 mechanism→method”，然后再去 literature 里找素材。

---

# 2. 当前优先目标

优先会议：

- ACL / EMNLP / NAACL Main
- ICLR / ICML / NeurIPS

持续阅读：

- AAAI
- CVPR / ICCV / ECCV
- TACL

PaperNotes 用于：

> 高吞吐跨会议 discovery / taxonomy。

核心论文必须回到：

- Introduction；
- Related Work；
- motivating experiment；
- key theorem / method；
- main result；
- ablation；
- discussion / limitations。

不能只看摘要。

---

# 3. 当前正向 taste 来源

只有两类：

## A. Sasano 的真实判断

尤其：

- 普通 reviewer 是否能快速理解；
- introduction 是否“納得できる + 面白い”；
- 为什么做下一节必须自然；
- novelty 不能只是 new model / new setting；
- paper 的主要知识不能靠 appendix 才成立。

## B. 真实强论文

不把任何自有 S/L/F/CT candidate 当正向 exemplar。

强论文需要做：

> **reverse engineering**

而不是“总结贡献”。

每篇都要重建：

> prior state → unresolved pressure → key conceptual move → decisive evidence → paper growth → relation to related work。

---

# 4. 当前 repo 状态

旧 handoff 已过时。

截至当前 `ssn-taste/`：

**SELECTED — PILOT-AUTHORIZED**

- S04
- S05
- S06
- S07
- S08

正式 KILL：

- S03
- S09

它们只作为：

- execution lessons；
- anti-duplication；
- recipe-risk；
- process evidence。

不作为新 taste 的正例。

---

# 5. V2 paradigm atlas

当前已经从强论文中重建出多种不同的问题形成范式，包括：

- literature conflict → hidden axis → unification；
- opaque frontier success → minimal ingredients；
- repeated baseline failure → training autopsy；
- successful objective → causal decomposition；
- wrong analysis unit → new phenomenon；
- outcome failure → temporal dynamics；
- adjacent-domain theory → structural explanation；
- train-time invariant → deployment violation；
- internal structure → controllable primitive；
- cross-lineage connection → new bottleneck；
- new scaling axis → allocation law；
- crowded object → new explanatory decomposition；
- prior fixes all attack wrong level；
- unexpected simplicity / unexpected success；
- changed premise；
- new intervention makes old debate identifiable；
- proxy semantic drift。

详见：

> **PARADIGM_ATLAS_ZH.md**

这些是：

> **search lenses**

不是：

> candidate templates。

---

# 6. 下一轮真正的搜索方式

用户通过 V2 taste 后，先不 brainstorm 标题。

第一步建立：

> **lineage map + pressure ledger**

每个 lineage 至少记录：

- 核心问题；
- 最近强 paper；
- 彼此 assumption；
- 彼此结论；
- used metric / objective；
- 哪些事实冲突；
- 哪些 premise 最近改变；
- 哪些 failure 被反复修却仍存在；
- 哪些 recipe 复杂但 necessity 不清楚；
- 哪些 observable 可能混了多个 quantity。

然后再从 pressure 中长 candidate。

---

# 7. 保留 ssn-taste 的硬纪律

新路线不会因为“更灵活”而变成凑题。

继续保留：

- nearest-prior deep audit；
- reviewer compression；
- old problem + new model 禁止；
- exact-cell novelty 禁止；
- terminology transfer 禁止；
- data / compute audit；
- experiment explosion kill；
- recipe biography kill；
- hidden compute 检查；
- benchmark / dataset 不作为默认 contribution；
- 允许 0 survivor。

---

# 8. 与上一版 chasing-trends 的关系

上一版不是完全废掉。

其中：

> mechanism→method、
> objective mismatch、
> failure dynamics、
> resource allocation

都保留。

但它们从：

> **统一主线**

降级为：

> **paradigm atlas 中的若干分支。**

下一轮 agent 不允许说：

> “我们现在的 taste 就是 failure→method，所以找这种题。”

正确说法是：

> “我们现在从真实 related-work pressure 出发，再判断这个 pressure 最自然长成什么 paper。”

---

# 9. Canonical reading order

下一轮开始前按顺序读：

1. `README.md`
2. `PARADIGM_ATLAS_ZH.md`
3. `PAPER_AUTOPSIES_2026-09-19.md`
4. `SEARCH_GUIDE_ZH.md`
5. `LESSONS_FROM_SSN_TASTE.md`
6. 未来建立的 pressure / failed / candidate ledger
7. recent commits

在用户通过之前：

> **不生成 CT01。**
