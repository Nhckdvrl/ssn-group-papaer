# Wang 等：语法可接受性不等于字符串概率（ACL2026 main）

1. **来源/范围：** [正式论文](https://aclanthology.org/2026.acl-long.686/)，MIT。主文§1–7/Limitations pp1–9完整；AppA/B/C pp12–14与D的logistic/LASSO部分pp13–14、M/N p21完整；其它附录/代码未全审。21p PDF外置SHA a8237bc2abc61dfff205c5ac91418332af202cff7a0a4cc722ceffa641505af2。
2. **压力/idea来源（RECONSTRUCTED）：** 最小对词概率有效但总体grammaticality/likelihood不应等价→争论LM是否只有字符串统计→将判断对象从LM输出prob转到hidden→普通语料粗扰动训练简单probe，把人类语法数据留给跨分布评价→语义合理性与跨语言反向检验区别。创新是构念及泛化证据，非首次linear probe或“有特征但不能用”。
3. **方法/规模：** PTB/Gutenberg50k原句，一次insert/delete/local-shuffle构造negative，80/20调层及L2强度；末token hidden，6个base模型/3族，不测instruct以避免其distribution改变。原/扰动各5k由ClaudeOpus4.6判定，acceptable93.72/6.28%，不是独立人工真值。BLiMP134000/CoLA10657/SyntaxGym2412及6语言成熟bench；3合理性集1564/790/76。有pairwise ACC，也有全局AUC，不能混同。
4. **结果与读数边界：** probe通常语法更强、语义合理性更弱；Spearman logprob/probe .089–.47，增加logprob不一致改善，末token也可恢复部分平均logprob（R² .51–.68）。LASSO约10neurons可预测，随机同大小也非平凡；是监督可读性和selectivity，未做因果干预或证明模型原生使用该变量。英训probe迁移一般更好，但Dutch pairwise ACC多个模型低于string-LP，非所有读数普适胜。
5. **近邻距离/限制：** Katzir/Leivada讨论概率与语法不可等同，Hu理论给出不同构念；此文增加跨数据/语言的内部可读证据。粗扰动可能是语义怪异而非语法错、语料原本可能有错、只有最终checkpoint；pair级train/dev和代码未核对。正文概率示例的(1)/(2)方向与前面长度/频率论述不一致，未回原引用核实，不能照抄数字作证。元语言fewshot只4示例，低分不是一般模型能力上限。
6. **对GP：** 不把低prob、grammar判断、谁对谁做什么合成一个变量。E80给true语法metadata未恢复关系，E81反转评分也无共同联合保持；不能用probe发现宣布错误解释源已修好。若后续要定位源噪声与真实解析，需分别测其具体功能后果；当前不追加grammar probe/head网格。成熟语法/语义数据可直接复用，额外标注仅为缺少且必需的对象，不因50k粗扰动被论文使用就模仿人工新小数据。
