# MetaRAG: Belief-Action Aligned Policy Optimization for Agentic RAG（作者v1，2026-08；接收未核对）

`[证据级别：主文精读＋附录]` [arXiv2608.24214v1](https://arxiv.org/abs/2608.24214v1)，ZJU／Ant／CityU。22p PDF SHAe17ca4308da534e1383fe38267dfc75ea90dcc4a96b62b32650d624bb336512f；同名Zhou2024 MetaRAG是其它工作，不能混淆。主会接收没有从官方确认。

1. **论文形态：** 已有agentic-RAG RL强baseline上的训练reward与决策接口方法。
2. **背景与压力：** 只给结局reward，或按轨迹／观察分组的step credit，没有直接校准何时继续搜、何时回答；外部过程judge贵。不是空白题：HiPRAG／DAS／Search Wisely已有搜索边界诊断。
3. **idea来源（RECONSTRUCTED）：** 将over／under-search合成一个两侧决策边界对象→单独问同模型是否可答→与实际Search／Answer比较→只给最终正确轨迹一致性bonus→随机提出候选动作让policy先verify。新研究动作是把知识边界测量接到训练credit，再测搜索成本与实际答案；不是第一次自检或belief-action gap。
4. **与最近邻的距离：** 外部judge改成同policy独立yes/no接口，search-query token confidence改成question-history的answerability。这个probe是提示接口概率，不能视作唯一内在belief；作者也比较Internal Confidence，但未证明跨接口潜变量等价。I07一般“self-grader可能错”“应加correctness gate”已有ownership，需具体修订对象和后果。
5. **方法：** 原context另一个forward，softmax仅Yes／No得到b=PYes−PNo。b>m且Answer或b<−m且Search得1，其它0；episode平均，再R=Routcome×(1+λRconsist)，默认λ=.1／m=0，随机候选动作。不是逐token或逐步advantage直接使用该credit；最终仍是scalar trajectory reward。probe训练时用，verify-first推理时仍有输出开销。
6. **数据／规模／基线：** NQ＋HotpotQA训练，七社区QA评测，2018 Wiki／E5 top3／最多4turn；Qwen2.5 3B/7B 400iter、4/8 A100，GRPO group5。GiGPO同检索复现，其它SearchR1/HiPRAG引用Xia2026结果，不能把全表叫同一协议复现。3B41.7%／1.60 searches，对GiGPO39.8／1.32；7B45.4／1.74，对43.9／1.25。更高准确率伴更多检索，不是全指标Pareto支配。无一致性reward41.9／2.14，Under-search-only42.4／2.56；作者所选方法是在accuracy-cost上取舍。没有seed／CI完整表述，不能认证小增量显著。
7. **关键诊断：** 加GiGPO step优化可43.1／47.0%；移除verify-first test仍41.5／1.45，相同prompt加GiGPO却39.3／1.36，区分训练与即时提示收益。GLM5.1完整test轨迹后验判under-search35.6→30.1，judge看到gold与final answer且明确正确答案不判under-search，受结局正确性影响；不是独立证明每个中间belief正确。Perplexity AUROC平均59.5→60.2，PRR20.5→21.8，但GSM8K PRR15.5低于base16.1，不能称每域校准增强。
8. **资料scope及局限：** 主文1–5及Limitations pp1–9全；AppA–N pp12–22全部（algorithm、settings、per-dataset、prompts／case／timing），refs10–11／运行代码未全读。p5Table1、p6Fig3/Table2视觉核对。训练额外forward／verify推理成本已承认：7B281s/step vs249GiGPO、525HiPRAG；方法限制在Search／Answer、无query词汇质量或rationale faithfulness监督。BrowseComp3.49%较2.65高而绝对水平低，不能包装成解决deep research。接收说法来自二手未据此记主会。
9. **对我们：** 合格方法idea可从明确压力长出来，不需完全空白，但必须有新的测量对象→训练接口→后果。I07拟研究新的关系修订为什么得不到观测credit；若仅raw likelihood坏或提示换路，距离不足。可以借用correctness-gating的原则但不能把它当新方法；关键是让无teacher监督在语义更新处有辨别力，而不是再造一个一致性分数。
