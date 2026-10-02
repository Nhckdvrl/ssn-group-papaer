# E10：Separate semantic reachability from geometric regularization（2026-10-02）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I06
- **前置：** E09 证明 semantic correctness 与 negative regularization utility 可分离；否则不运行。
- **问题（一句话）：** 能否不用 environment oracle，把“pair-specific planning semantics”与“global separation/regularization”拆成两个训练通道，同时改善 semantic calibration与真实 planning？
- **设置：** 方法形式由 E09 结果决定，跑前写 amendment冻结。候选最小设计顺序：
  1. **unknown-not-negative:** cross-trajectory pair默认 unknown，不给 binary / absolute-distance negative语义；
  2. semantic channel只用 observed positives、same-trajectory insufficient-budget hard negatives、以及能从 training-available local structure认证的 bounds；
  3. separate geometry channel承担 dispersion/uniformity/scale，不再把某个具体 cross pair叫 unreachable；
  4. 有 multi-route evidence 时做 interval / multi-route aggregation；
  5. 最后才考虑 learned connectivity estimator。
- **读数：** 与 E09一致，额外报告 false-negative exposure、unknown比例；calibration、fixed-candidate regret、closed-loop success、compute。
- **阳性对照：** E09 最能解释 FULL收益的 oracle/repulsion upper bound先复现；否则不声称 E10近似了它。
- **噪声地板 + MIE：** 1-seed pilot通过后才3+ train seeds；论文级扩展要求至少2 methods或2 task families。
- **混杂审计：**
  - 不使用 privileged state作为 deployable training signal；
  - semantic certification只能来自 training-available local transition/data structure；
  - geometry regularizer不能编码 test goal；
  - compute/loss exposure匹配；
  - validation-only调参；
  - 只改善head calibration、不改善decision，不能叫planning方法。
- **决策表：**
  - role-separated objective匹配/超越FULL planning且semantic calibration更好 → C##候选，扩 contact-rich + 第二method；
  - calibration更好但planning差 → heuristic repulsion仍提供未捕捉结构，回机制；
  - planning更好但semantic calibration不变 → 重新检查 role-separation解释；
  - 无稳定改善 → I06停在diagnosis/reattribution，不强做方法。
- **算力预算：** E09后填写。  
- **实际：** 待运行

## 结果
未运行。