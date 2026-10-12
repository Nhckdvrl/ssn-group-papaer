# Emergence and Localisation of Semantic Role Circuits in LLMs（ACL Findings2026）

[正式原文](https://aclanthology.org/2026.findings-acl.1964/)；主文§1–6及limitations（p1–9）完整，AppB/C完整、D1开头，其余附录未深读。32页PDF SHA1ff32c7eb3d8b6375720f95320c064f67012e489e57b1879fd07d33a7a0f5cf3。Manchester/Idiap，Nura Aljaafari、Danilo Carvalho、Andre Freitas。引用本篇不意味着投稿Findings；不涉及EACL。

1. **问题与idea来源（重建）：** 已有IOI/事实/算术circuit分析，但对抽象predicate–argument结构与训练中何时可用的解释不够。把frame semantics/PropBank的role转换为可局部操纵的continuation scaffolds，再用Hanna EAP-IG跟踪训练checkpoint；研究对象＋时间视角贡献，而非全新电路算法。与TRACE/CARMA自家前作、MIB/训练电路稳定性近邻的发展清楚。
2. **实际操作/数据：** eight roles主要preposition scaffold：to the/with the等只改变提示尾部，target/foil选不同role的discriminative词库（office/truck），只用单token/等长度配对，目标词不在prefix。每模型约6028–7988对，**按最后checkpoint两个context都预测正确筛选**，不是完整自然语料成功率。Pythia14M/410M/1B及Llama3.2-1B；主文引用Llama2023，实际附录C型号3.2。没有AGENT/THEME主要实验，不能直接当GP actor/patient修订已覆盖。
3. **方法与读数：** negative logprob target；IG5步、Top200绝对edge归一化mass，再聚合node；Top20节点约89–92% mass（非89–92%实际行为因果解释），8role source到nexttoken消费任务。faithfulness=(circuit CNPacc−null)/(full−null)，consolidation是node Jaccard≥.6持续2点，变化点分段拟合；跨模型节点按layer/head索引匹配，不是表征或算法相同。小Laplacian谱距只说明图几何，不能叫functional transfer测试。
4. **finding与质量边界：** 论文提出逐渐结构精炼、结构与功能非同步、不同model复用component但重新连线；典型node overlap24–51%、edge11–17%。作者明确仅prepositional浅语义，成功样本选择，不能据next-word适配证明任意source真实role binding。主文Table2 “all consolidate within~2k”与表50k/5k矛盾；tcons先于tind的叙述与Instrument128vs32相反；Table3 Instrument点50k在CI[128,10k]之外；主文spectral k16与AppC k20不一致。以上未核对代码，记录为证据可靠性限制，不凭它给整篇质量判死。宽变化点CI不足以逻辑“排除phase transition”。
5. **近邻距离/尺度：** 由因果电路定位延伸到role＋训练轨迹，数据千级、多checkpoint、四尺度但仅两模型族。核心增量属于抽象结构的具体功能操作与时间演变；“role有局部circuit”及“结构形成≠当下作用”已有owner。role识别Scaffold与自然先前解释修订是不同对象，近邻不关闭我们的空间。
6. **对我们：** 可借contrastive具体操作与功能使用分开，不能借模板恰当下一词当真实role正确。E75 wholeSource切断不恢复，不能说没有role circuits；E76关系草稿的端到端优势若存在，仍需具体源断言/角色变化与后续用途相连。GP actor/patient主题要检验真正遇到的自然错误，而非绕到成功样本抽象head图证明有语法。主文limitations建议non-prepositional结构只是开放方向，不自动是我们的novelty。
