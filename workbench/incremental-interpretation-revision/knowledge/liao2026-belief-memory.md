# Belief Memory: Agent Memory Under Partial Observability（作者v2，接收未核）

`[证据级别：主文精读＋全部方法附录]` [原文](https://arxiv.org/abs/2605.05583v2)。MBZUAI/RIKEN/UT Austin/Wuhan；18页，SHA83bfc18b8ac3dc5f5f8d68f549ea70660a2bbaaf47d38af3cd5d9736ecbd70f8。NeurIPS2026旧检索缓存出现题名，但当前官方Downloads find未匹配，不认证接收；最终稿/代码未核。

1. **形态/压力：** memory方法与现成benchmark；单一结论导致不再探索其它解释，把暂时API失败固化为永久不可用。改变存储/检索对象而不是刷一个新的RL算法。
2. **idea来源（RECONSTRUCTED）：** 从POMDP local posterior与已有memory add/merge/read建立联系，保持属性的多个候选及置信度，再让retrieval把候选一起返给policy。将不确定性丢失定位到写入与检索，而非笼统“记忆太短”。
3. **近邻距离：** Mem0/A-MEM/Memory-R1已有记忆管理，ABBEL/Belief Engine已有belief对象；新组合是属性候选置信存储+保留候选检索。一般“保留多个可能解释以避免自我强化”已有owner，不属于我们独有。
4. **实际方法≠精确Bayes：** LLM提subject/predicate/entities/qualifiers形成属性；概率为未校准confidence，新项clip[.7,.9]，同候选noisy-OR cap.99，不归一化；同属性不同候选按规则视作冲突，旧项降.25并保历史版本。本文明确ack非posterior，但引言图称Bayesian Update，不能把图当精确推断证据。
5. **规模/评测：** LoCoMo GPT4o/mini，官方F1/BLEU1、seed20260413；ALFWorld Qwen3-Next80B-A3B，140 seen/134 unseen，50步，3000训练expert经验bank/半bank1500，eval不入bank；actionseed42/greedy32token。TopK按LoCoMo类别20/30、ALF20，最多4候选/属性。无多seed/CI主表，不将差异等同稳健因果幅度。
6. **结果/边界：** LoCoMo mini均F1 42.38 vs官方Mem0 40.99（重跑35.20），4o42.87 vs39.66；不是每类最优。ALF半bank59.88 vsReadAgent54.03，fullbank58.66；#steps在成功episode上，不能当所有episode效率。halfbank最佳是数据size探索后选出的表述，不说明更多经验普遍有害。
7. **核心检查尺度：** 去概率retrieval ALF51.77、去候选存储28.71；211人工可映单属性LoCoMo gold所选样本的Top1 convergence87.68%不是开放后验定理。102 adversarial项由高排错误/正确不在TopK筛选，10步含5valid+5noise构造更新；correction是retrieval rank不是自然agent完成率。语义属性抽取与同属性冲突判定本身仍可错。
8. **阅读范围/数字校正：** main1–5 pp1–10全部，AppA–E pp12–17全部、extraction prompt p18全部，主表2/3 p8视觉；refs未逐篇核。正文称K30 unseen“8.5% absolute”但61.19−55.97=5.22pp，约8.53%相对，不能复制混用。λ表.9/1.0平均约60.5高于默认59.88，不说默认全面最优。
9. **对I06/I07：** 提高候选可获得性与faithful关系修订分开。E103 MVRR同Source池没有新增好P，NPS有proposal但selection范围有限；不把保留候选或概率排序改名为我们的novelty。具体增量若存在，是重建同一需要改读的观察产生相反关系credit，而非一般belief uncertainty方法。
