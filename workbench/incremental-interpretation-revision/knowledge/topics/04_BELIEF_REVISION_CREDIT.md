# 专题四｜从 Belief-R 到 ABBEL：改变前提、更新内容、奖励重建分别在做什么？

**核心警惕**：相似的词“belief”“revision”“reconstruction”不是可直接相互替代的实验变量。我们的E91–107有潜在新问题，但旧解释尚未识别成“回报机制复制错误的旧解析”。

## 1. Belief-R的任务其实是“什么条件会抑制推论”

[Wilie et al. EMNLP2024](https://aclanthology.org/2024.emnlp-main.586/)，[作者v2 §3/4](https://arxiv.org/html/2406.19764v2)。作者继承 Byrne 1989 的 *suppression task*，先有 `if essay then study_late` 和 `essay`，由modus ponens得 `study_late`。再加入 `if library_open then study_late` 后，人可能把 **library_open视为事实上的必要条件**，从而撤回先前“必然study_late”的判断；若第三条件是“if has textbooks then study_late”，就可能保持。

**这是一个明确的逻辑/语用分歧**：在严格经典命题逻辑里 `(p→q),p,(r→q)` 仍然蕴含q；增加另一个充分条件并不能撤回旧结论。论文研究的是人在自然条件语句中的语用/世界约束补全，标注协议必须被保留。文中两侧分别设计**应该更新与应该保持**，而不是“凡是来了第三前提就改答案”。[原卡](../wilie2024-belief-revision.md)已核对1912基本题/1744带条件题和标签一致性细节。

因此本项目 E104 的 `then` 字符串切分失败，实际上没有测试“同一个belief是否在第三前提改变语义前提后得到了正确更新”。把后半句残余字符串当新证据，可能删去关键条件；要讨论跨领域revision，必须映射**新增的必要/充分关系**，而非字符串位置。

## 2. ABBEL学习的是什么内容？

[Li Dayan et al. ABBEL 作者v2 §4–6](https://arxiv.org/html/2512.20111v2)。它不是静态地给一句话打真假：
- 环境产生观测 `o_t`，Agent已有旧belief `b_t`、采取 `a_t`；
- belief generation 更新到 `b_(t+1)`，随后action selection从belief决策；
- 与保留全部history或FC-beliefs比较，定位**遗漏、错误更新、冗长**是否解释使用问题；
- 再为belief更新采样一组候选，用outcome RL和auxiliary grader训练，而不是仅在已有两个候选间进行无监督排序。

§6.2在ColBench的重建评分是 `log pi_theta(o_t | instruction,b_t,a_t,b_(t+1))`；Eq6的Bayes后验式还要**减去更新belief在旧条件下的prior**，因此评分目标不是“此belief真实概率最大”。算法/代码里有关token求和、归一化与截断的不同还留在[原卡](../lidayan2026-abbel.md)，**本轮没有复跑其训练代码**。

**实验生长为什么合理（RECONSTRUCTED）**：Full Context表现更好，不一定因为belief遗忘，也可能仅因多一次模型调用、输入格式或环境信息差异；作者对照FC beliefs/完整history，再让belief成为可单独训练中介。只改reward不会说明reward应当奖励哪一条语义关系，所以先用环境测试和遗漏分析“需要保存哪些信息”。这个动作对我们比复刻GRPO参数更重要。

## 3. 重建分数负向支持正确解释，什么时候才真构成问题？

考察同一观测 `o=(prefix,suffix)` 和两个候选 `Hnew,Hold`，恒等式

`Δwhole = log P(o|Hnew)−log P(o|Hold) = Δprefix+Δsuffix`。

假设正确信念更难预测先前歧义前缀，但更容易预测晚cue。例如对两个H：
`P(prefix|new)=.1, P(prefix|old)=.9`；
`P(suffix|prefix,new)=.8, P(suffix|prefix,old)=.2`。

则前缀Δ≈−2.197、后缀Δ≈+1.386、整体Δ≈−0.811（自然对数）。这是一个**完全合法且一致的条件概率模型**，无需“内部继承旧句法错误”也会出现E101式图像。它并不能否定“奖励目标需要改变”这一未来研究方向，只是禁止把代数符号当机制因果证明。

另一方面，即使固定两个候选的score真的更喜欢旧错误，也需观察：它们在**原生同源候选池**里有无明确正确新关系、哪一个被选择、后续行动是否因此失误。如果好候选根本没有被生成，讨论“评分器选择错误”就是在研究不可实现的oracle。若模型自然倾向生成 `someone/something`，不能把模糊输出标成完整新绑定。

## 4. 旧证据如何迫使主张降权

| 卡片 | 旧读数/实际发现 | 允许的推论 | 不允许的推论 |
|---|---|---|---|
| E91–E97 | 冻结模型中复原分数与role答案可不同；部分forward协议失效 | 方法类比存在需要辨别的候选/评估错配 | 已复现ABBEL RL失败；E93 cap/unknown也算模型belief差 |
| E98 | 当前三族未稳健得到统一的正确QA损失/收益模式 | 跨模型异质与任务交互很重要 | 凭单Q条件声称通用悖论 |
| E101/E102 | whole、prefix、suffix相对分数方向不同 | 条件概率分解和内容选择现象值得追 | 前缀神经状态保留旧解析 |
| E103 | 旧角色标签分数Q+8.33pp（边际） | score对旧标签操作有效 | 真正完整新依赖恢复8.33pp |
| E105 | Q更多候选 +13.54pp | 至少该Q条件，池增大改善选择 | “搜索越多错越多”通则 |
| E106 | 某单纯自动score无普适修复 | 某规则不够 | 所有奖励设计不可行 |
| E107 | Conservative paired bound Q+6.25pp CI跨0、Gemma0、Min+4.17pp CI跨0 | 完整内容改为严格语义gold后没有共同稳健改善 | 反过来证明score没有任何信息 |

此表照旧审计转录历史分数，外置原始候选与token级大结果未重新独立复算；源数为真实cluster，不把每个候选当独立人。

## 5. 这里更深的开放问题

从生成-选择-行动三段来看，每段都可成为解释缺口：
- **形成**：怎样的修订条件下完整Hnew候选的出现概率降低？难点来自曾经许可Hold还是关系本身复杂？可以在不训练情况下对照自然/early-clear源。
- **选择**：同池相同语义但不同表述时，rank对prefix先验、输出长度、词面控制是否发生有方向的变化？不该只把不同cue放到一起看grand mean。
- **使用**：若被选belief事实上完整，行动还失败，则是consume或任务接口；此时奖励rank或候选本体已经不是唯一问题。

贡献可以是三者之间一个令人意外、可预测的分界，不需要强行把三个研究路线永久保留。若现有证据显示这是旧文献覆盖的已知现象，也允许彻底转移问题。我们的职责是**不断让知识总图更准确**，不是维护早先I07的想象。
