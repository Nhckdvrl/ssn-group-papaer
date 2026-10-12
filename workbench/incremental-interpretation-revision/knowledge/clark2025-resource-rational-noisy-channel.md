# Clark 等：输入错误推断与有限计算（EMNLP2025 main）

1. **来源/范围：** [正式论文](https://aclanthology.org/2025.emnlp-main.1207/)，MIT BCS。主文§1–6和Limitations pp1–10完整；AppA/B/C pp12–14完整，Fig2/3/5及算法页另作图像核对。参考文献未逐篇核对、代码未审。外置PDF14p，SHA670ba256a84ccf42d1992325538b3de123992d39a9ec16da26d2d5c5fd64eac8。
2. **压力/idea来源（RECONSTRUCTED）：** 既有Bayesian noisy-channel讲理想后验，尚缺开放候选的增量算法→next-word LM只提供语言先验→显式错误生成模型+SMC→有限粒子会丢掉后文有利的候选→MCMC rejuvenation允许更改先前随机选择。贡献是可操纵计算限制的已实现模型，而非“语言模型天然会纠错”。
3. **近邻距离：** Levy2008已有固定字符串的有限粒子句法分析；Li/Futrell、Li/Ettinger已有异常与ERP建模；该文把候选扩大为intended string及错误动作，并给出资源、回溯的算法预测。已读Clark2026 CoNLL把同一模型用于人类回看位置；两篇不是同一贡献，也不能把2026预印本另计一次。
4. **方法/规模：** GPT2 word-level restricted decoding+6种错误动作，SMC importance correction/每步resampling；有限lookahead最多一次漏字，rejuvenation可全句第二遍或按相对unigram surprisal触发回溯。504异常句、K4–128；120主语单数/动词复数agreement项比较主语/动词修改。主文称词表intersection，AppA称union，未代码核实；算法页weight/log-weight及trigger记法与正文不完全一致，不能照伪代码认定实现。
5. **结果/边界：** 可修复异常K128比同restricted-LM约少1–2bits；无关联异常不获得同等收益。agreement item级人类编辑偏好相关，second-pass r从.19到iters2的.48，再至iters4的.42；conditional lookback6 r.34，低于人类split-half .81。不是计算越多越人类，也未测真实GP的最终关系QA。错误率非实际生产统计校准、仅一个小LM、无非词/换词位置等限制。
6. **可借动作/对本线：** 把“重新解析原字符串”与“推断源字符串被损坏”分开；先有实际编辑后果，再谈机制。E80零编辑信任/可能遗漏先验只测输入可靠性敏感性，不能认证noise posterior或native能力。若不能跨族保住两关系和cue，不加prompt网格追胜；若能，下一步需观察新输出是否执行预测的补词/换词操作，才用Step Plan审核这些新增文本。宽noise假说已由人类与LLM近邻讨论，增量要落到LLM真实错误解释的因果功能。
