# E12：原始句子概率与最终答案访问分开测（2026-10-05）

- **状态：** PLANNED
- **类型：** MEASUREMENT / abnormal-result follow-up，非paper idea
- **对应：** C03 / C02 / P07
- **问题（一句话）：** 提前问题/选项的影响是否已经进入模型对原句的逐词预测，还是主要发生在末尾答案读出？
- **设置：** 原E10 SAP全部2304 prompt（原72题/144句/24共享lexical sets，全部Q×option位置×mapping×一句repair）及原E08 Amouyal4968 prompt（69sets/276QA、相关/对应极性无关focus×before/after×repair），逐个full prompt SHA与原run匹配；没有新增句子、题、语义gold或提示词。frozen本地Qwen3-8B FP32/eval/no-grad/native/thinking off/TF32 off，现有env；GPU0与1独立运行。仅计算原句字符范围的teacher-forced source token概率。代码input_probability.py，seed0。
- **至少两个竞争解释：** (a) answer/readout主导：位置改变最后答案，但句子条件概率的GP−cue差值在同类内容提前/后置之间很少改变，尤其E10固定末尾options；(b) content-conditioned processing：提前问题已经改变消歧词/句子概率，其GP交互在options固定末尾下仍有；E08相关−无关focus能区分内容特异性与普遍前置输入干扰；(c) lexical priming/option contamination：效果集中在带目标动词的final focus或options前置，GP与cue同时受益，而非GP特异结构更新。可混合，非唯一机制判别；有概率效应不直接等于句法parse改变。
- **主读数：** E10固定options末尾的Q前−后×GP−cue在作者指定disambiguator word的surprisal（bits）；base与repair各报，两个mapping全部报。按每lexical set内三family平均后paired cluster bootstrap（10000draws/seed20261005），三family另报。作者xlsx target与control原标记分别报，六flag差异未重新标注。原位置指示词在72 GP/cue对中必须是相同源词，任何错误先追why。
- **次读数：** E10 disambiguator+后两词平均、后续全部词平均、全句平均bits；问题/选项位置的所有配置完整报告。E08全句mean bits的initial−final、相关−对应极性无关focus×GP−nonGP、all69/clean67、prob/reflexive。没有Amouyal作者disambiguator标注，所以不由agent追加语义region，不能把全句读数叫晚cue局部效应。与原E08/E10最终answer scores并列解释，不事后筛答对项或挑region。
- **阳性对照：** 无提前Q/options的SAP GP−cue消歧词差值，所有family报告，不作为科学停步gate；whole source token→word覆盖与原target对齐。位置在句子后面的Q/options/focus无法影响先前source概率：按causal token-prefix一致性复用，明确这是架构/输入所蕴含的null，不包装为独立经验发现。
- **噪声地板 + MIE：** 先前FP32同prompt随batch最大漂移约5.95e−5/0binary flips（概率，不直接换算bits）；当前无gold正确率或任意通过阈值。报告原始bits/paired CI；效应不足/混合也指导下一动作。不要为降低测量噪声重复无新信息sweep。
- **混杂审计：** 两组原输入全文SHA匹配；源数据hash、许可/revision沿用已审版本；重复token-prefix只算一次，之后回填所有分析行，不把复用当新增GPU评估。prefix截到原句末字，确保未来Q不泄漏；末尾tokenization可能与带后缀的full prompt不同，主消歧词位于内部，末尾whole-sentence值仍须注明该条件分布。每source token必须只属于一源whitespace word、不跨非空白header，不人为分摊多词token的概率。语义/句法因果解释仍受lexical priming、system与非中性chat训练影响；R8一句repair来自原配置。
- **决策表（跑之前写）：** 答案交互明显而source交互弱 → 降低早期parse叙事，优先追原句读数/自然后文用途；source GP交互在末尾options保持，相关focus也特异 → 保留content-conditioned处理解释，下一实验用语言证据而非更多位置模板区分词汇预激活与结构更新；仅前置options/词汇final焦点影响 → 先追内容泄漏，不叫task-directed revision；混合/小样本target → 完整报告，并借E01有效语言读数选择下一操作，不能自动判死领域。
- **算力预算：** 两独立单卡、合计<.4 GPU·h；相同模型和cache，无新增下载/训练/SAE/probe。实际待填。

## 结果（不改上述读数与决策）
- 数字及CI：
- 结果与配置文件：
- 解释 / 下一动作：
- 主张变化：
- POST-HOC：

### 跑前机械核对
- [alignment](../results/E12-preinference-alignment.json)：E08全部4968 parent prompts SHA匹配，1380 unique causal prefixes；E10全部2304 SHA匹配，1728 unique prefixes；72/72 GP/cue消歧词同词；所有词有token，所有source token只归属一个源word，无跨非空白header。没有按模型答案筛选数据。
- 固定options在末尾时，两个mapping在句子截止点之前token-prefix相同，source processing读数是同一计算复用，不是两次独立复现；原末尾answer不同mapping的结果仍分别报告。配置记录unique-prefix物理计数与全部parent分析行。
