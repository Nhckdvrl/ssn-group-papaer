# E156 静态预检（2026-10-27）

- 未发现必须修复的实现错误；尚未从本次审阅确认 GPU 控制通过。
- P/A/B 对应模型索引 0/1/2；`n.assemble(...,(0,0,r,s))` 固定 P 的 dense/gate，分别选取 R/S 来源（`e156_run.py`、`e150_native.py`）。
- 常数 oracle 覆盖九格 R/S 来源和 shared 系数；三个 gate 相同，不能仅凭该 oracle 验证 P gate，来源由 `assemble` 代码和调用元组确定。
- 全词表首答案 token KL：相对 P 原生 full；预算 KL：各格自身 full 相对自身 masked。四候选 choice-score KL 分开报告（`e156_run.py`、`e156_analyze.py`）。
- P/P 先检查真实 cal 组合身份，逐题复用 native P；9×2 + 3×2 − 2 = 22 个不同条件。
- selector 仅由 P 和逐 subject validation cal greedy 生成，固定用于全部来源；相关 context manager 和收集 hook 均在 finally 恢复（`e153_data.py`、`e153_harness.py`、`e150_restricted.py`）。
- 真实前置检查包括各源参数/state_dict 和 buffer hash、旧 cal 逐位一致、full mask 身份及全部 native 逐题 LL 重放；结束恢复模块并复核 hash。是否实际通过以运行记录为准。
- 分析器核对 3×3×2×128×4、native 3×2×128×4、来源次序、两科各64及预先固定的共同成功集 36/8；A/B对角线与非对角线对比符号与实验卡一致。
