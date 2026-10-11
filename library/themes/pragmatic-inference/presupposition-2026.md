# Presupposition and Reasoning in Conditionals（CoNLL2026）

来源：https://aclanthology.org/2026.conll-main.26/；公开review未核对。

1. **形态 / 阅读：** theory-based human/model measurement；正文intro/method/checklist/results/discussion/conclusion已读，A/B部分例子/其余appendices未全读；Table3原PDF视觉核对。
2. **压力：** 相似Likert judgment是否真的体现presupposition reasoning？
3. **改变前提 / 来源：** human graded依赖A与p相关性，不把投射压成一个bool；DOCUMENTED：proviso问题/条件语义。
4. **数据 / 证据：** 30目标命题、不同A-p相关性、with/without minimal context；4模型。Qwen2.5-7B human Spearman .25/.38，Llama .21/.30；judge Haiku4按59/52 binary checklist，human校准仅约5%。closed checklist总分>60%，open约40%。
5. **关键校对：** Table3 with-context total四模型均下降（−11.79/−7.47/−7.36/−11.82pp），原PDF正文却写context一般提高且Llama/Qwen Accuracy/Presupposition有gains；表中这两维下降。原code未核对，不能复述上下文方向。59 vs52 checklist也不完全同支持集。Judge rubric compliance不是潜在reasoning深度，作者承认可能verbalization。
6. **近邻 / ownership：** human/model判断–解释分离已拥有；相关性.38不能写成与人判断几乎相同。四模型不同family/未知closed size不支持纯scale因果。
7. **动作：** matched criterion空间，context相关性与装饰性背景分开；判断、解释、候选概率各自定义。
8. **对我们：** descriptive-human target与normative theoretical target可能分离，不能由其中一项分高推另一项。
9. **边界：** 不依赖其API judge建立本轮主实验；未取得并复现code，不包装为finding。
