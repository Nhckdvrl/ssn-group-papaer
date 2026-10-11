# On Emergent Social World Models — ACL2026 main

[原文](https://aclanthology.org/2026.acl-long.1735/) · [代码](https://github.com/polina-tsvilodub/lm-emergent-social-world-models)

- 阅读正文§1–4与limitations（前10页），39页后部附录/统计结果未完整读；源码与原cache未核对，不称全文/复现。
- 来源DOCUMENTED：人脑ToM/pragmatics共享功能网络的自然理论→LM的integration/specialization两可解释→行为相关、条件预测、独立localizer、消融和通用能力control。先大问题再可检验预言，是论文尺度参照。
- 行为48models/7families/.5–72B、22ToM与16pragmatics；mean-token LP选择，不是full概率distribution。r=.68；Bayesiancontrols/LOO用于控制general-language。无可信difference不等于任务等价；size/family/training混合不能因果机制。
- 机制20models/4families，四GPT5合成localizer suites/1400stimuli，top最多1%activations lastprompttoken，simple/conjunctive t-stat；least-active matched数量control，10foldgeneralization。PCA未分群不是语义完全匹配证明。
- 原结果：global ToM与pragmatics消融loss大于least-active；但pragmatics-vs-baseline effect P3.2 CI含零，不能claim完整特异性；entity tracking也受影响。局部套件CommunicativeIntent不符合预期，conjunctive噪声更大，LB+CI CV因代码错误缺失（source明说）。作者只称suggestive evidence。
- ownership：共享ToM/pragmatics、stage/size与functional localizer已有。不能先找“pragmatics neurons”当我们的新idea，也不能把ablation损伤直接叫normative criterion。
- 可迁移动作：由竞争解释推导多条联合预测；把支持/不支持和global/局部边界同报；纯prompt/behavior相关不能代替机制。当前应先自然效应成立，不为了大故事提前做激活分析。
