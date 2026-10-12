# 好论文的 idea 如何从旧研究中生长？

本页是**思想来源的逆向重建**，不是对作者私下创意过程的事实陈述。每条使用【作者明确】/【根据论文结构重建】两个标识；已读范围与版本在公共论文卡，不把读过摘要当作读过附录。

## 1. Amouyal et al. ACL 2025 → ACL 2026：从一个受控现象到跨构式的解释空间

- **前一知识压力：** 心理语言学在 GP 上已有复杂性、及物性、合理性、阅读困难的分歧；简单的 LM surprisal 不告诉我们最终回答出了什么错。
- **作者问题与最小动作【作者明确】：** 2025 在对应条件下做人/LM同题理解，并用复述和图像任务验证行为差异；2026 统一问题格式和 matched baseline，扩到七类结构、五家模型族，寻找困难结构的排序。
- **idea 尺度【重建】：** 不靠提出一个新的 GP 算法，而靠更好的比较对象使“处理困难是否类人”成为可讨论的现象，随后通过跨结构扩展检验其外延。
- **最近邻距离：** 心理语言学读时/surprisal → 统一问答与受控跨构式比较。今天“GP 难、早晚 cue 差”已经被其拥有。我们新增模型不能简单当贡献。
- **本项目的反教训：** 作者原 No=not necessarily；E52 要把“原问答正确率”与真正逻辑矛盾拆开，不能用作者结论自动当内部修订机制。

## 2. Hanna & Mueller NAACL 2025：从“可读信息”转成“真正使用的因果特征”

- **前一知识压力：** parser/probe 能从表示解码语法，不能证明网络靠它做后续 token 预测；GP 的读时研究不能解释神经计算。
- **突破动作【作者明确＋重建】：** 先用延续词概率定义功能性阅读偏好，再用 SAE/AtP-IG 选择相关特征、通过 up/downweight 验证；接着问这些已验证的特征是否用于 QA。不是在随机 feature 里找漂亮例子。
- **尺度：** 一个重要现象，三条逻辑相扣 RQ：结构特征是否因果？同时支持多解吗？读完会修复吗？先以一个任务中的真实功能选 feature，再跨任务做 falsification。
- **关键边界：** 72条原数据、Pythia-70M/Gemma-2-2B；部分实验只检验 Gemma，MVRR 续写 choice mass 受限而退出相关后续分析；选择的 feature circuits 仅有限 faithfulness，不能把“干预无效”外推全部语法计算。
- **本项目能学：** 必须验证 O4 的替代内容与 O5 的功能使用；但“representation ≠ use”已被拥有，不能把 E63/Gemma Hint 差异换名作新发现。

## 3. Slattery / Sturt / Ceháková：从正确 parse 到残留与局部修订

- **前一知识压力【论文结果重建】：** 句末看似正确，并不能推断最初解读已完全消退。人类研究使用第二句/指代/反身依赖与句法及意义任务，观察 good-enough、merged/partial interpretations。
- **idea 尺度：** 核心不是提出“存在两种理解”这一宽概念，而是把彼此可以分离的读数放在同一刺激上。
- **我们的严格距离：** 只测出“旧错误更少、新关系未必更完整”还不足；需要找到新的计算条件/后果，能够预测哪次修订会失败，或证明既有推断不成立。旧 E107 是测量纠正，不是这类论文的重新发明。

## 4. Yoshida et al. ACL 2026：将既有“反证”变成存在性检验

- **前一知识压力：** 现成预训练 LM 的 surprisal 常低估人类 GP 阅读代价，社区容易直接否定 surprisal 理论。
- **论文转折【作者明确】：** 如果问题在代理 LM 的分布估计而非理论本身呢？微调使预测匹配 GP 并测试 held-out GP / 普通文本，得到解释人类阅读时间的 existence proof。
- **思路价值：** 把“模型/指标失败”与“理论不可能”分开；设计一个原则上足以推翻过强结论的正例。我们不能凭 E54 的某个 oracle 无效而宣称增量机制不可能。

## 5. ABBEL（作者 v2，arXiv 2512.20111）：从记忆内容更新到可训练的监督接口

- **压力：** 长程 interaction 中无结构摘要可能丢细节，而单一任务结果 reward 不清楚是哪次 memory 形成失误。
- **推导【重建】：** belief bottleneck 将状态写入与行动决策分开；既然 belief 自然语言难以逐步 ground truth，就尝试用新 belief + 旧 belief + action 对最新 observation 的 reconstruction 作为内容训练信号，并约束长度。
- **距离：** 从通用摘要或仅下游任务 reward → 中间内容具名训练对象。其目标是 **最新观察** 的重建，而非旧 belief。其源码选择片段与论文 Algorithm 的 sum/归一化/cap 细节未完全一致（见既有代码阅读卡），不可把伪代码单独作为实际训练机制。
- **我们的独立问题：** 若观察需要重新解释，字面重建奖励是否错奖某些内容更新？必须先证明正确完整候选在同 observation 下被选错，不能用 E92 GP/cue 表述差立即宣告作者 RL 缺陷。

## 6. ReBel（arXiv 2605.20061）：用可检验的延迟反馈而非字面重建

- **压力：** 终局奖励稀疏；仅用 observation-hash 给同类 state 分组，在 POMDP 下不代表语义相同。
- **动作【重建】：** 显式 belief predicates、后续 observation 对它们的可检验性和 delayed buffer，结合 step-level credit / grouping。
- **关键差异：** ABBEL 的 observation reconstruction 与 ReBel 的 predicate-consistency 不是同一个 reward；现有项目 E94 的代码选段反映关键词/追踪器实现边界，不能将抽象“belief reward 错”当成跨方法证据。

## 7. Causal Quotient（作者预印本 2610.05292）：重新定义被解释对象

- **压力【重建】：** 线性 probe 或方差变小常被说成 post-training “忘掉 belief”。坐标变化、实际使用与信息保存不是一回事。
- **关键创意：** 先在精确 HMM 中定义 reward 对某些方向不敏感的 quotient，分测可恢复 R、因果使用 U、尺度 A，再用 anchor/filter/优化对照证明哪些结论由什么产生。
- **idea 尺度：** 新认识 + 让竞争解释可区分的测量方式，不靠刷 benchmark。我们不能再次把 “state 与 output 不同”当创新；要分清 O3/O4/O5 这种可操作的关系性变化。

## 8. 两篇新近跨领域近邻（2026-10-12只核会刊摘要，不计新精读）

- **Zhao et al. ICML 2026, Large Language Model Agents Are Not Always Faithful Self-Evolvers**：官方摘要报告 4 框架、13 backbone、9 环境，raw/condensed experience 的因果替换，指出决策不一定忠实使用压缩经验。这强烈占有“记忆可用≠被行动忠实使用”的一般叙事。其干预方法与解释边界须全文精读，**未读不推断**。
- **Zou et al. ICML 2026, On Information Self-Locking in RL for Active Reasoning**：摘要区分行动选择决定能看到什么观察，belief tracking 决定能不能用观察，提出相互锁定与 reweight。它占有一般 agentic AS–BT 反馈叙事；我们的增量不能只叫 observation credit 会错。全文/实验尚待阅读。

## 逆向思维的三个问题

1. **作者不做那个额外实验时，前一个结论还有哪种替代解释？** 比如 Hanna 若仅有 probe，就缺因果；只有 causal feature，就缺第二用途；只有 GP wrong，就缺问答 Gold 语义。
2. **是什么方法的能力边界促成了新研究对象？** 比如 Yoshida 的核心不是更多对照，而是分清现成 LM 是否能代表整个 surprisal 理论。
3. **换到我们的问题，这个动作是否真的会判别两个理论？** 能直接复用方法，但不能只换数据名就声称新的 idea。
