# 下一轮科研选题搜索启动提示词

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste`。

完整方法只读：

> **`SEARCH_GUIDE_ZH.md`**

不要在本文件维护第二套规则。

## 当前正式状态

以 repo 最新 commits / `README.md` / `SELECTED_TOPICS.md` 为准。

当前 selected / PILOT-AUTHORIZED：

- S04 — Event Boundary / Situation Model Updating
- S06 — Deliberation / Evidence Reweighting
- S07 — Where Does Surprise Go?
- S10 — Thinking-for-Speaking / Event Construal

S03 / S05 / S08 / S09 已 KILL。

Selected 不是 taste exemplar；failed 不是 idea source。

## 开局动作

1. 读 `SEARCH_GUIDE_ZH.md`、`README.md`、`SELECTED_TOPICS.md` 和最近 commits。
2. 抽 2–4 条 **Sasano 最近明确研究评价**，重点看：
   - 为什么他觉得某结果有趣 / 不惊讶；
   - novelty 为什么不足；
   - 为什么值得继续 / 应该见切り。
3. 读 4–8 篇近期强 **ACL / EMNLP / NAACL / TACL Main**，跨 2–3 个 lineage。
4. 对强论文只做：
   > Pressure → load-bearing assumption → knowledge at stake → decisive attack → growth lesson
5. 建 5–8 个 **Important Pressures**，不要先 brainstorm 题名。
6. 只有 pressure 同时满足 **重要 + 未解 + 现在有新 attack** 时，才锁一个 seed。

不要开局通读所有 `FAILED_TOPICS*.md`。  
锁 seed 后再定向查 failed ledger 做 anti-resurrection。

## 本轮最重要的纠偏

### 不赌现象

不要：

> “也许有个神奇现象 → 先跑看看 → 有了再问 why。”

优先：

- 已有理论分歧；
- 未验证的 load-bearing premise；
- 已成立结果之间的冲突；
- changed regime；
- 旧问题的新 identification opportunity。

### 不做“别人发现现象，我们补 why”

除非 why 本身就是独立、重要、未解决的 mother question。

### 不从经典术语表搬题

“某心理学/语言学现象在 LLM 中是否存在”默认弱。

复杂语言学尤其谨慎：问题必须能让普通 AI/NLP reviewer 一句话听懂。

### 热门题默认降权

不要在 RL / agent / latent reasoning / uncertainty / evidence integration 等拥挤线里靠 exact-cell novelty 找活路。

## 强制 Global Reset

Agent 容易陷入局部思考，把“救当前 seed”误当任务。

出现以下任一情况立即 reset：

- 连续 2–3 个 seed 同类死亡；
- 开始不停补 controls / variants；
- 开始想“怎么绕 prior”；
- novelty 只剩 exact condition；
- 一直困在同一 lineage；
- strong papers 只剩查重用途。

强制回答：

> **我们的核心目的是什么？**  
> **删掉当前 seed 后，什么 scientific pressure 仍然值得追？**  
> **我们是在找最好的问题，还是在保护 sunk cost？**

然后重新抽 Sasano feedback + 不同 lineage 强 Main papers。

## 最终输出

一个 seed 锁定后必须审到底：

> **PILOT-AUTHORIZED** 或 **KILL**

不留 SERIOUS / maybe。

允许 0 survivor。

最后只记住：

> **不是找一个没做过的实验，而是找一个 Sasano 会觉得清楚、重要、值得知道、现在终于能直接攻击的问题。**
