# I'd rather just go to bed — CIRCA / EMNLP2020 main

[论文](https://aclanthology.org/2020.emnlp-main.601/) · [原数据](https://github.com/google-research-datasets/circa)，commit02ad965518ab2fbd8bb24463d312ebb03bac5368。

- 阅读：正文§1–7、相关工作、Appendix A/B全部文本与实践题；嵌入UI截图文字尚未逐条重建，原训练未复现。README/34268 TSV全量已审计；README写CC BY4但license链接指BY-SA4，发布衍生资产前需确认，不改原署名。
- 来源DOCUMENTED：真实间接答有条件、非承诺和不确定，极小scalar语料不足以学习跨情景语言。十自然情景、不同workers问句→回答→解读，回答阶段不预指定意义，避免人工均衡语义。
- 资产：3431unique question、34268 QA，原strict8judgement categories、relaxed合并；实验排除unsure/other/NA后strict6、relaxed4。多数≥3，strict κ=.61/relaxed .76。实际发布34248项5judge、20项4judge，原majority labels全量重算全部匹配；E34仅原5/5一致子集，缺失不补。
- parent结果：BERT-MNLI-YN matched relaxed .882、strict .848；matched答句only .817/.778。out-of-scenario最低.819/.744。问句only高于majority不自动artifact：rhetorical question自然有prior；answer-only有真实语义cue，与NLI hypothesis-only的构念不同。
- 已拥有的关键困难：Probably no 69%被选No，偏好horror并不排除买过romance；middle含speaker不承诺/unknowncontext/vague阈值，不能都变0.5。PY混合probably和sometimes，语义频率不等于模型置信度。
- 学方法：意义丰富→不强迫指定回答标签→原few-shot标注practice→source/情景heldout→question/answer-only→具体错类解释。不是仅把二分类扩成六分类。
- 增量边界：generic overcommitment已拥有。E34同问句原unanimous回答检验强/弱与条件范围，source-hash抽样先冻，仍不同答案语义/难度，不是单因素warrant intervention。真实stage若改变具体条件结构才可能有科学对象；目前无finding。
