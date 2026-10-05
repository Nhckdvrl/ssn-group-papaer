
# CLAIMS — In-Context Evidence Structure

**2026-10-05：PROPOSED baseline residency。当前无论文级科学 finding。**

| ID | 主张 / 待验证对象 | 等级 | 当前依据 | 升级条件 |
|---|---|---|---|---|
| C00 | 本地 procedural task 能让 frozen LM 在 episode-randomized nonce mapping 上表现出可靠 few-shot task learning，而不是仅靠 label semantics / copy | L0 | 设计成立，尚未本地运行 | E00 通过；0-shot vs few-shot、held-out query、nonce remap 全部报告 |
| C01 | 我们能稳定测出 demonstration 的 position-wise influence，并在 exchangeable 与 obvious-change 两个阳性条件下得到可区分 readout | L0 | 文献给出预期方向，尚未本地运行 | E01 通过，readout 波动小于两极差异 |
| C02 | frozen LM 的 evidence weighting 会/不会随 stable-vs-change 的统计证据系统改变 | L0 | 这是 workbench 科学对象，不预注册方向 | E02 matched pilot + CI；必须与 fixed-prior / set / sequence / adaptive accounts 比较 |
| C03 | structure selectivity（若存在）能跨任务族或 evidence type 泛化 | L0 | 未测试 | E02 成立后用第二 substrate 达 L3 范围前不得泛化 |

**禁止提前升级**
- order sensitivity 本身不是 C-level novelty；
- recency under change 不是 novelty；
- one noisy demo hurts 不是 novelty；
- probe 可分离某个 task state 不能单独证明 adaptive structure inference。
