# ssn-taste

Sasano-taste-driven research-question search.

Primary targets: **ACL / EMNLP / NAACL Main**.

## Current state

> **Selected topics = 0.**

S01–S12 全部 KILL / cancelled。

## 每轮正常只读这三个文件

1. **SEARCH_GUIDE_ZH.md** — 唯一 canonical 方法论；包含 Sasano Slack taste、搜索流程、recon、novelty、preflight。
2. **README.md** — 当前状态。
3. **SELECTED_TOPICS.md** — 只有最终通过全部 gate 的题才能进入。

新对话交接时可读：
- **NEXT_ROUND_PROMPT_ZH.md** — 简洁 handoff。

只在需要时定向查看：
- `POOL_POSTMORTEM_2026-09-26.md` — 为什么 S01–S12 整池失败；
- `FAILED_TOPICS*.md` — anti-resurrection；
- 某个旧 `Sxx_*.md` / `experiments/` — 旧题具体失败证据。

**不要每轮通读历史失败档案。**

---

## Taste hierarchy

> **Sasano 本人真实 Slack 评价 > ACL/EMNLP/NAACL/TACL 强工作 > 其他顶会/跨领域启发 > 同门题材。**

每轮开始必须重新查 Sasano 本人的近期 Slack 研究判断，不能只依赖之前总结出的 taste。

用户个人偏好的 method paper / benchmark gain / training / mechanism 题型，不属于这个文件夹的正向 taste。

---

## Workflow in one line

> **Sasano calibration → multi-paper tension → natural reconnaissance → our stable pattern → RQ → deep novelty → preflight → selected**

详细规则只看 `SEARCH_GUIDE_ZH.md`。

---

## File discipline

不要继续新增流程文件。

新的 Claim Map / tension / recon scratch 在当前工作过程里维护即可。

只有：
- 最终通过全部 gate 的题 → 新建 `Sxx_*.md` 并加入 `SELECTED_TOPICS.md`；
- 需要 anti-resurrection 的严重失败 → 写入现有 FAILED ledger。

仓库保持少而清楚。
