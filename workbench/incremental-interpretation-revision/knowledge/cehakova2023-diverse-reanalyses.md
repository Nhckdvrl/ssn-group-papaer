# Garden-path sentences and the diversity of their (mis)representations（2023）

[PLOS原文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288817)，[原材料OSF](https://osf.io/98g26/)。阅读身份已更新：**2026-10-12正式PLOS HTML主文包含Exp1–5的材料、方法、结果与讨论均重新核对**；更早一版仅深读E4/5并略读E1–3是历史阅读状态，不再代表本卡现状。OSF逐行实验数据与R脚本未复算，不能宣称独立复现。

1. **形态：** 人类最终理解的多种失败形式；不用单个No替代完整representation。
2. **对象：** Czech dative/accusative暂时歧义，同verb的真实object和possessive关系，而非英NPZ逗号。
3. **动作：** 接受度预检；完整句/逐词×Yes-No/自由回答，animacy干预。
4. **来源（DOCUMENTED）：** Slattery完整新parse+旧trace结论与Huang/Ferreira2021全局结构不足解释之间的争论。
5. **近邻增量：** 质性编码找只有旧对象、合并、犹豫、无完整解释，避免只看聚合binary正确率。
6. **核对：** E4 179人/E5 141人、相同48实验项目；自由题分别问动作和possessor。Substitution/Other/I-do-not-know/Different分开。E5逐词disambiguation与两spillover区域均有ambiguity/animacy主效应，无其交互。
7. **边界：** 部分free题并非简单二选同题重措辞，作者明确不能直接比较任务accuracy；错误分类依赖人工准则。问句重新激活与原解释持续仍未完全区分，不能称直接内部共存证明。
8. **可迁移动作：** 把失败类型与控句错误对比；真实object题和possessive题提供不同依赖；观察哪个问题改变结果而非寻获胜prompt。
9. **对我们：** 双读数、free-response更深理解、多个局部结构不一致均有人类owner；Lee/Shin2026已有LM paraphrase。没有根据这篇立即扩多语言。结合E01观察追哪个语言证据改变完整解释及下游使用，是同一个revision对象。

## 2026-10-12 原文完整主文重读：五个实验是一条推断链

**来源**：[PLOS ONE正式HTML（2023-07-18）](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288817)、[原始材料/数据/分析脚本](https://osf.io/98g26/)。本次实读理论背景、实验1–5的设计/结果/讨论及General Discussion；OSF代码与participant数据尚未下载复算。下文修正历史笔记“E1–3只读片段”的读数身份，原旧阅读历史仍可从Git追溯。

**真正的三条可分命题（Exp2/3）**：
`qcor`：晚到真实宾语是否接到目标动词（gold Yes）；
`qmis`：旧错将临时歧义名词当宾语，是否仍被接受（gold No）；
`qpos`：原歧义名词是否正确回接为受益者/外在领属关系（gold Yes）。
单个 No 可以在 qcor、qpos 都失败的情况下“正确”，所以绝不能由旧错No得分认证完备修订。

| 阶段 | 样本/设计 | 之前还区分不了什么 | 本次论文的判别动作 |
|---|---|---|---|
| Exp1 acceptability pilot | 70捷克语母语生、48实验items+fillers、2歧义×2宾语生命性 | 新形态对照本身是否不可理解 | 非歧义控制接受度；不把基线坏句误诊为修订压力 |
| Exp2 whole-sentence comprehension | 174人、48 items、2×2×3，qcor/qmis/qpos | 旧错残留是不是同时伴随完整新句义 | 真宾语、旧误角色、受益/领属三种关系分开问；Yes/No/Don't know |
| Exp3 wordwise comprehension | 159人、同源与问句，critical+两个spillover | Exp2差异来自加工困难还是整句呈现/回视 | 关键区域及spillover RT与结果分开；ambig与animacy各有主效应但无交互，不能据此说后续理解没有交互 |
| Exp4 whole-sentence open | 179人、同48 items，两类open问题 | 二元错误是错绑定、模糊、拒答还是答别的问题 | 用 substitution (另识别其中的GP旧误)、other、I don't know、different 分类 |
| Exp5 wordwise open | 141人、同材料与编码，preregistered | Exp4模式是否依赖阅读回视/呈现方式 | 重做开放输出并加入区域RT；复现部分错误类别与区域效应，仍不能把“无显著交互”认作“无影响” |

**关键结果及边界**：Exp3 critical区 ambiguity β=.035，animacy β=.028（均显著），交互不显著；两个spillover也见主效应。Exp4的 `qwhat` substitution 可能明确旧误，而 `other` 包括 “He searched someone” 这类**不够具体**的内容；`qwhose` 缺失可对应 “I don't know”。Exp5三region相似。作者明确警告开放题与三选择题问法在难度与评价单位上不等价，不能直接把同一百分比当同一能力。

**思想继承（RECONSTRUCTED）**：Slattery2013提供“存在有效新结构却未清旧意”→Huang/Ferreira2021提供“局部合法树与全局完整解释可能不一致”→这篇问二者是否需要强制二选一→用*同一个确切依赖*的多个正负读数及类别化输出回答。对E103→E107，这是优先重新定义完整角色内容的前人证据，而不是自己发现“正确/错误与省略混在一起”。

**最近邻差距**：本研究是捷克语人类受益者/外在领属的特定形态暂时歧义；不能未经映射就把其qpos与英语NP/Z的主句主语、或Agent belief更新，当作相同神经过程。