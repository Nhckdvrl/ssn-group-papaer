# Revisiting Real-Time Digging-In Effects（arXiv2603.23624v1，2026；接收未核对）`[证据级别：正文HTML Methods、两实验、Discussion/Limitations]`

[正文](https://arxiv.org/html/2603.23624v1)；本地PDF/hash见ledger。

1. **形态：** 经典机制的边界复核；受控实验发现先前解释的测量混杂。
2. **压力：** 延长歧义是否让承诺更难修订？动态自强化与概率预期给出不同预测。
3. **改变前提：** 句末时长可能含wrap-up，不能全部解释为实时承诺。
4. **idea来源（DOCUMENTED）：** Tabor/Hutchins经典材料的句末设计；复用构式并把finality显式因子化。
5. **近邻：** Futrell已有模型reverse digging-in；Huang有GP surprisal低估；本工作在两个人类任务中检验相同语言操纵与finality。
6. **实验：** Maze30项、SPR36项；GP/comma/object×短长，SPR再交叉句末/非句末；16LM的预测；两任务cue作用并不完全一致。
7. **证据/短板：** 非句末没有明显正digging-in，句末呈正趋势；三因子交互仍不确定，不能将“没有显著证据”写成严格零效应。SPR在 RT 分析中仅保留理解题答对的 trial，RT分析不直接回答错误理解的过程。
8. **可迁移动作：** 把一个熟悉解释所依赖的测量位置拆开；再看解释是否保留。独立任务复核也暴露comma的任务特异性。
9. **对我们：** E01歧义延长不能自动命名digging-in/commitment；不同词汇modifier也可改变预期、NP引用和问答。需先看跨cue与非GP读数的结构，后续对照必须能区分这些解释。本文owner不关闭探索。

## 2026-10-12 原文纠错与数值对齐（原卡新增，非新实验）

[arXiv v1 HTML 完整主文](https://arxiv.org/html/2603.23624v1) 的 §Experiment 2 *Additional Details* 明确写 **36 critical items**、233招募/225保留、每位参与者18/36 items（原卡曾误记为24，已在主条目修正）。Exp1 为 **30 items、191招募/167保留**，各条件并非全在 item 内正交，22/30为非句末，故不能把Exp1的最终性子组效应当随机正交的纯因果比较。Exp2把歧义、长度、cue类型（comma/object）和critical词句末性全作为 *within-item* 操作。

- E1 human GP critical median 225.79ms、digging-in interaction 11.71ms (pd70.83%)；final group +93.64ms (pd97.38%，**仍低于作者97.5%阈值**)，nonfinal −18.24ms (pd76.30%)。
- E2 非句末 GP +34.45ms (pd99.77%)，digging-in −8.68ms (pd82.91%)；句末GP +75.87ms，digging-in +19.69ms (pd92.62%)；三因子 ambiguity×length×finality +14.42ms，pd96.63%，**不显著**。两项均不是“证明没有自强化”，只能说未给出 robust real-time positive digging-in。
- **容易遗漏的仪器混杂**：Maze comma cue的另一个呈现选项也带逗号，导致comma不能像SPR一样清楚地提供字面disambiguation。作者§Experiment2 discussion明确Exp1 comma效应未复现；这不是语言处理普适差别。
- **设计逆向**：旧研究观察length→critical代价，既可解释为强承诺，也可能来自句末wrap-up或词概率。E1用Maze先定位而暴露finality/cue差异；E2把两者正交；最后把LLM预测（由filler拟合RT映射）与human分开。对我们，E01的扩展材料不应直接当“锁定旧角色时间”操作，E104的then切点同理要先审语义与仪器。

**版本、范围与未核**：实读arXiv 2603.23624v1 HTML §1–Conclusion及两项Exp的数值表、模型RT映射、局限；未运行作者R代码，也未重审原参与者逐trial数据。