# Prompting is not a substitute for probability measurements in large language models（EMNLP2023）

[出版PDF](https://aclanthology.org/2023.emnlp-main.306.pdf)，21页，已读正文§1–6与Limitations；未读完附录。hash/缓存见ledger。

1. **形态：** 评估有效性，四task/两种测量对象；泛泛competence/performance差异不是新发现。
2. **来源（DOCUMENTED）：** 依据元语言问句做能力/认知结论忽略了额外query理解与输出要求。
3. **动作：** word prediction、semantic word comparison、isolated grammaticality、minimal pair比较；直接概率与三零样本meta模板比较。
4. **数据/模型：** 小型FlanT5与GPT3/3.5；counterbalance choice order；BLiMP/SyntaxGym与词预测/语义材料；不仅一个prompt坏例子。
5. **结果：** 直接/元语言不同；直接一般更好，但有例外；minimal pairs改善meta；距离直接next-word任务越远，alignment更弱。
6. **边界：** 论文把next-token分布当word预测目标的ground truth，不是所有理解的oracle；一串文字概率高不保证拥有正确事件图。零样本三meta形式、旧模型、小语言补充限制泛化；作者并未测试更多thinking/few-shot，并明确不能拿负meta结果判无语言知识。
7. **可迁移动作：** 对同对象的已知概率与自报读数核对；原子word任务与整句句法任务分开；保持所有contrast结果，不只报一个gap。
8. **对我们：** E11元语言span与E12prediction/QA不同属已知测量压力；不能改成我们的novel story。E12更具体的24-cluster conditional变化值得追因，但纯word概率也不是parse gold。下一步用自然后文功能依赖决定语言修订对象，不继续找更漂亮问句。
