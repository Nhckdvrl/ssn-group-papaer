# E124：私人规则独立形成时，共同身份上下文作用于形成还是读取？（2026-10-12）

- **状态：** DONE-CONFIRMATION；三checkpoint全部16→32，完整raw独立校对。
- **类型：** PILOT / CLAIM；由E123整体功能反例检验新的协调解释，不作为旧C21–23的必过门槛。
- **对应：** C23、I04、P17。
- **问题（一句话）：** 不共享任何私人监督、仅共享无标签的来源姓名列表，是否足以帮助两套独立形成的规则共同使用，且作用是在形成期还是query读取期？
- **为什么现在做：** E123完全分来源形成后own-space分类仍强而full输出约54%，选择性形成优于完全隔离；当前解释仍未分清“共享什么信息有用”。本项使身份共同上下文与私人监督共享分开。Feng的实体绑定提供候选解释，但姓名列表不等同已识别binding ID；PCW已研究独立上下文与joint query，本项保留原位置、不复用position、不冒充PCW重现。PCW再审的ensemble提醒单源函数可靠与联合使用要分别测。
- **设置：** 冻结Qwen3-8B/Mistral-7B-v0.3/Llama-3.1-8B，同前轮revision/conda/FP32/eager。沿E121 official SST5极性0/4、5–64tokens、train SHA奇偶不同demo池与validation/test queries；n16 seed124001→n32 seed124101（`--materials validation`），不按pilot科学方向筛模型/contexts。每ctx8A8B/8新query；A raw与no/yes固定，B origin为反约定、cross为同约定，B使用pass/flag。私人极性平衡。discovery Alex/Sam，confirmation Robin/Jordan，Source名字排列沿固定rng匿名分配；query与demos一起换，未给出criterion/私人映射。
- **独立形成图：** 全层阻断所有严格历史cross-source demo→demo access，各Source保留自己历史与通用HEAD。在HEAD之后、所有demos之前加`Names: <两个姓名>.`，这段不含label/规则/输出词。两类列表：实际Source姓名、无关姓名；均是非排他的列表，不宣称只有这些参与者。无关姓名从冻结池按token长度匹配选择，只看tokenizer不看评分。所有通用HEAD在列表之前，避免形成关闭时经后续公共token转发。列表内部causal正常，但不可能读未来私人监督。
- **形成/读取交叉：** F∈{0,1}决定所有demo token能否读取列表；R∈{0,1}决定整个query能否读取列表。Source之间私人信息始终隔离，只读列表可作为共同身份上下文。两Source共享每个prefix缓存；query仍可读两Source实际demos。true/unrelated×F×R×origin/cross×A/B=32主条件。无列表native4、无列表全来源独立4、single A/B两约定3、一句指令的无列表独立4，总47×8=376评分/context。
- **读数：** primary完整词表下一token准确率，按每context均匀两world×两Source×8query。关键冻结对比：真实列表的形成-only增益(F1R0−F0R0)，减去无关列表同样增益；读取-only对应F0R1−F0R0及其真实−无关差；true F-only vs R-only、F×R交互均报告。辅助own-space候选准确率、是否输出本Source词、另一Source词率、正确label margin，A/B、private正/反与same/opposite完整保存。A固定词空间的B-code half response signed/abs保持；不把candidate改善冒充联合词表使用恢复。
- **阳性对照：** 本批实际single函数/native/no-roster independent差与一句指令；默认cache与4D-native/fullsplit≤.001，true/unrelated F0R0所有Source-cache与query输出应相同≤.001（列表既不可到demo亦不可到query）；F1R0 graph中列表不能经公共晚token直接绕到query。每层实际mask消费、strict-past/self、缓存deepcopy指针/seq、配对tokengeometry、官方gold/私有方向。all-cross＋query-own-only下Bworld→A graph-zero；单源all-cross mask严格no-op。
- **噪声地板 + MIE：** FP32数值floor≤.001；context-bootstrap10000/seed910。n16数值有效即固定n32三家族确认，不因正向挑模型。形成-only真实−无关差CI/幅度以及Source分解用于更新；不指定任意涨分资格或搜索alpha/head/层。
- **混杂审计：** primary先定full词表；列表不提供输出词/映射或新样本，文本形状/token数控制，counterfactual只改变公共身份内容与可达phase。mask改变attention mass并使后继状态活演化，测的是图操作非纯固定向量；列表关闭对比使用同长度/位置。无列表baseline位置较短，仅作复现/功能参照，不用其差作为F因果主张。SST可能pretraining见过，fresh私人配对与匿名Source不同；本实验新contexts/Source名字非新benchmark，query pool与旧实验可能重用，E124 discovery/confirmation原文独立。无关人名可能有词先验，primary使用各自F/R差再difference，保留所有方向。名字列表有无协调作用不能自动证明/否定所有binding算法，尤其Feng是完整实体-属性绑定而非空名字表。
- **决策表（跑之前写）：**

| 实际结果 | 更新认识/下一动作 |
|---|---|
| true形成-only特异改善full/source-word使用，candidate仍强、无需跨Source监督 | 身份共同上下文可在私人规则形成前提供协调，新增具体形成/使用认识；对齐binding与TR/TL，不称新ID构件；回到整篇再决定最小有意义验证 |
| 读取-only强、形成-only弱/零 | 此信息主要作为读取cue；不把当前全隔离失败归因为形成期身份协调不足，主文原形成/关系结果保留 |
| true与无关列表同增或都弱 | 列表不足以识别身份协调/主要泛化prompt作用；不换十种姓名列表或继续head定位；重新读文献和已有功能反例 |
| 两Actor/方向相反、candidate受损 | 全部报告，不叫私人函数无损协调，不以平均吞掉身份/输出先验 |
| 数值/可达性/几何失败 | 只修实现并记录0-score或VOID，不从失败科学分数挑seed；源再封版 |

- **算力预算：** 三checkpoint独立空卡，Qwen/Llama本地21、Mistral20；当前21 GPU0有他人作业不碰。各16→32；预计约0.6–1.5 GPU·时。confirmation使用新source名字，不按pilot选模板。没有新训练、head/layer/strength矩阵。

## 结果（完成后追加）
全部6项CPU材料预检通过（3checkpoint各16/32ctx）：token长度/角色/公共列表无监督/确认别名一致。首评分前科学源SHA256 `ea65caf59d2b69ef5c14803fd1edbd7b227ad3813d2b4fa261c001faaaaea727`；材料builder沿冻结 `f02104a87b9e67dec413c9c642c107a0f90a7d1046421306e8c4202c59da94ec`。实际query全层mask消费hook在评分前加入，与原图/读数相同。预检退出均0；旧ResourceTracker退出stderr原样保留，不作为科学数值。

GPU结果尚未生成。


### 冻结确认与实际更新

| 模型n32 | 形成-only身份特异full增益pp | 读取-only身份特异full增益pp | true F0R0→F1R0 full% |
|---|---:|---:|---:|
| Qwen3-8B | 4.59 [2.73, 6.64] | 0.29 [-0.78, 1.46] | 52.73→58.98 |
| Mistral-7B-v0.3 | -1.07 [-2.05, -0.20] | 0.49 [0.10, 0.98] | 53.32→52.83 |
| Llama-3.1-8B | -0.68 [-1.95, 0.49] | -0.20 [-0.88, 0.39] | 53.22→54.59 |

Qwen形成期的身份特异收益A+3.71[.20,7.42]/B+5.47[2.73,8.59]pp，same/opposite和私人方向均确认；candidate特异差+.10CI跨零，Source词率与full同增。Mistral方向相反且true形成A−5.66/B+4.69pp；Llama candidate特异差+.78[.20,1.46]但full未改善。不是统一形成修复、也不是完全无身份作用。名字列表仅有界地帮助Qwen formation，不足以让三家族独立函数共同正确输出；该结果不否定完整binding机制、不影响旧C21–23等级。

6批144contexts/54144scores，.564224 GPU·时。独立11742数值复算max0、1872实际token流/2448mask/54144gold，81600 prefix和225600 query层调用，4608 F0R0 argmax对比全同；floor≤1.53e−5，inert/graph0。未独立GPU重跑。全Actor/private方向/同反约定/47条件/halfresponse/图见[报告](../results/e124/report.md)、[summary](../results/e124/summary.json)、[独立审计](../results/e124/independent_review_2026-10-12.md)。首评分前commit f9b9b31c，scienceSHA未改。

**下一步与问题连接：** 名字存在不等于Source–输出关系。有限E125进一步检验公开词空间绑定在形成/读取阶段的作用，不提供私人配对、不变层/头/strength；不为了把4.59推到80%追一串名单模板。
