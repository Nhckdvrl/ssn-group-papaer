# Are explicit belief representations necessary? A comparison between LLMs and Bayesian probabilistic models（NAACL2025 main）

**阅读范围：完整main§1–5/related/limitations；附录B belief、C所有谓词图文本；A主统计方法已看但每表未全核对。原stimuli.py/model.py、certainty.R/人类及RSA字段已读，GPU/AIC尚未复现。** [论文](https://aclanthology.org/2025.naacl-long.572/)，[repo](https://github.com/pennydy/llm_belief) @ad2c36d75f9d14d192d193f7db919035c41619bd。公开评审未核对。

1. 形态：理论模型×human prediction比较；3API模型GPT3.5/GPT4/GPT4o与mixRSA，改二值NLI为speaker commitment graded inference。main20items×20predicates×2worldfacts的human规范，prior另测；source另含not_p与polar对照共1680projection/80prior。
2. 压力：已有LLM能做常规非字面推断，但是否捕捉belief attribution中prior与predicate交互？面向可解释理论、不是+accuracy榜单。
3. 前提改变：know也非无条件同强度投射，prior/QUD（at-issueness）与utterance alternatives通过mixRSA共同影响。mixRSA是prior与pragmatics混合，不是唯一可能RSA；不可读成所有belief representation必须显式神经模块。
4. 来源DOCUMENTED：Degen/Tonhauser2021原human材料+Pan/Degen2023/2023mixRSA比较。既有感知/隐喻RSA比较激发跨projection检验。
5. 最近邻：NOPE/PROPOSE的NLI标签→原human连续certainty；Hu2023非字面整体→belief attribution；Carenini2023metaphor GPT2-RSA相似→projection细粒度差。对我们世界knowledge≠speakercommitment、prior过度影响已经owned，不能换名字。
6. 实验：原APItemperature0/max_tokens5，numeric0–1(.01精度)；human/jointmixed regressions/AIC。main RSA AIC221.56，GPT380.44/309.29/341.99；添加RSA变量改LLMfit，反向未显著。know与think边界不同；certainty vsbelief附录说明readout不同，而且发布CSV重新抽名字，不能把原两版当字节同一prompt操纵。
7. 限制：只3API模型；numeric selfreport不是透明belief probability（作者明确Hu&Levy限制）；predictive superiority不证明表示必要性；actualRSA180行、部分items/verbs/polarity，与840p大表不是完整同矩阵。拟合参数/heldout范围需核代码，不能即刻作independent理论因果finding。
8. 源审计：prior_rate.csv Josie高标签是“没有护照”、低标签“喜欢法国”，projection与原human对应相反。两个fact实际字符串交叉可核对，不能按label硬配。原priorCSV已含prior_info，model.py再次前置一次；原source保留重复，不silent cleanup。源stimuli.py随机speaker/holder且无seed，使用发布CSV。原human7436行含MCcontrol、20critical；人类item大小写需canonicaljoin。
9. 迁移动作：同时测事实prior与由语言归给speaker的commitment，检验各条件predictive structure，明确“raw事实概率/解释/规范决策”区分。先E38复现原numericmain与sourcejoin、strongendpoint/stage边界，若生成格式失效不改prompt救分。不直接增加RSA新architecture或宣称必要性；先保留已owned理论并找新的稳健证据交互。
