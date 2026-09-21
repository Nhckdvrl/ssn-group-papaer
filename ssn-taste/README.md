# ssn-taste

Sasano-taste-driven research-question search ledger.

Primary targets: **ACL / EMNLP / NAACL Main**.

## Canonical structure

每轮只需要按这个顺序恢复：

1. **SEARCH_GUIDE_ZH.md** — 唯一长期方法论。
2. **README.md** — 当前状态与目录。
3. **SELECTED_TOPICS.md** — 当前 PILOT-AUTHORIZED topics。
4. **当前 selected 的 Sxx registration** — 只用于恢复具体 claim / pilot。
5. **Recent commits** — 最新 repo 状态优先。
6. **NEXT_ROUND_PROMPT_ZH.md** — 极短 handoff。

### Historical archives

- `FAILED_TOPICS*.md`
- `RE_AUDIT_2026-09-18_NOVELTY_CALIBRATION.md`

这些是**定向查重 / anti-resurrection / 历史失败档案**。  
不要在每轮开局顺序通读，不要把它们当正向 taste 或 idea generator。

---

## Current selected topics = 4

均为 **SELECTED — PILOT-AUTHORIZED**：

- **S04 — How Do Language Models Update Situation Models Across Event Boundaries?**
- **S06 — What Does Deliberation Do to Evidence?**
- **S07 — Where Does Surprise Go?**
- **S10 — Does the Language We Plan to Speak Change Event Construal?**

S03 / S05 / S08 / S09 已 KILL。

> Selected 只表示“当前值得第一刀实验”，**不是正向 taste exemplar**。

---

## Taste hierarchy

> **Sasano 真实研究判断 > ACL / EMNLP / NAACL / TACL 强 Main 的问题形成方式 > 其他顶会/跨领域启发 > 同门题材。**

同门研究只作弱参考，不作为找题模板。

本仓库不限定“语言学”或“interpretability”。  
复杂语言学默认谨慎：如果普通 reviewer 不能很快理解 why-care，不优先。

---

## Core discipline

搜索不是为了制造候选，而是为了找到：

> **清楚、重要、未解决、现在有直接 attack 的 scientific question。**

禁止的常见 drift：

- 赌一个新 anomaly；
- 别人发现现象，我们补 why；
- old psychology/linguistics + new LLM；
- A≠B / shared-vs-separate / encoded-vs-used 套模板；
- mechanism-first；
- 热门 lineage 里找 exact-cell novelty；
- 为了不 KILL 不断加 controls。

Agent 一旦开始“救当前 seed”，必须回到：

> **核心目的不是保住 seed，而是找到最值得做的问题。**

具体流程见 `SEARCH_GUIDE_ZH.md`。
