# topics

这里只放**正式 candidate 状态**。

## 文件类型

- `CTxx_<slug>.md`：仅 **PILOT-AUTHORIZED** candidate 的完整 registration。
- `FAILED_TOPICS.md`：已锁定、完成审计后 KILL 的 concise ledger。
- 当前 selected 总表：`../SELECTED_TOPICS.md`

## 禁止

- brainstorm list
- SERIOUS / HOLD 半成品
- paper 摘要
- 大段 source notes
- 未审完 seed

## Candidate lifecycle

```
seed（不落盘）
→ lock one
→ full audit
├── KILL → FAILED_TOPICS.md
└── PILOT-AUTHORIZED → CTxx registration + SELECTED_TOPICS.md
```

真实 pilot 后若死亡：

- registration 保留，顶部标记 `CANCELLED / KILLED AFTER PILOT`；
- 从 `SELECTED_TOPICS.md` 移除；
- 在 `FAILED_TOPICS.md` 增加索引。

当前：

- `CT01_RELEVANT_BUT_INVALID.md` — KILLED AFTER RE-AUDIT（保留 registration 作为 provenance；见 `FAILED_TOPICS.md`）。
- `CT02_IS_CONTEXT_UTILITY_RANKABLE.md` — PILOT-AUTHORIZED。
