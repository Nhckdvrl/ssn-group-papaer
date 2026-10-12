# Min 等：以输出为条件，解释每个输入词（ACL2022 main）

1. **来源/范围：** [正式论文](https://aclanthology.org/2022.acl-long.365/)，UW/FAIR/AI2。主文§1–7 pp1–9完整；AppB p12实现/超参数/表6–9完整；其余附录、代码未审。15p PDF外置SHA bdffb76c2b99964c92b40da96b513c5fd3f9290d3e34d564d171efe6653f1e6b。
2. **压力/idea来源（RECONSTRUCTED）：** ICL和prompt tuning表面平均分好但verbalizer/seed不稳定→机器翻译与generative classification的channel传统→反转输入/输出角色，使完整输入提供训练/评分信号→不只新方法，加入常被漏掉的head tuning和数据条件比较。最重要动作是问什么情况下改参数位置、评分方向才有效。
3. **近邻距离：** Ng/Jordan、Yogatama、Lewis/Fan已有generative分类/QA；Holtzman有PMI零样本校准但假设input/output可互换；Tam label-conditioning仍判别训练。该文新增few-shot LM prompting的channel接口与系统条件测量，不能说首次逆向推断。其Bayes推导令class prior均匀，字符串LM不同顺序不自动保证共享一致joint；E81仅借评分动作。
4. **方法/规模：** 11成熟文本分类集、2–14类，GPT2主要Large、其他大小只附录；K4/16/64/full，不按类别强平衡抽样。4verbalizers×5data seeds，tuning另4train seeds；20prompt tokens、100global steps、lr按平均训练loss选择，无dev。Direct++除NULL label score，channel评分输入；concat/独立示例LP乘积ensemble。使用length normalization；同一x的两label比较长度相同，所以argmax不变，分数温度不同仍要明示。
5. **结果/限制：** few-shot最好channel相对最好direct平均+3.1/worst+7.2pp；这个“最好”会按任务选concat或ensemble，不是固定一种全胜。zero-shot SST2 Direct++80.3高于channel77.1，不能外推零样本普适。prompt-tuning channel相对direct prompt平均+13.3/worst+23.5，但head tuning在TREC/Subj更好；Kfull direct更强。未见label泛化、跨任务仍异质。单一GPT2族/分类集合，没有自然GP解析、内部因果或现代chat强模型证据。
6. **对本线：** E81用候选判断解释原Source全词，原数据即可直接测，0新API。若共同恢复，应再问语法证据是否在关键token改变候选相对支持，区别一般label prior；若只是No增长/正确关系损伤，动作收束。逆向method本身有owner，不能只换GPbenchmark叫novel；也不因旧方法已有而拒绝借用。真正增量仍需解释先前关系如何被修订、怎样可继续使用，能力/latent parse不凭逆向分数升级。
