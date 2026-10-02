# E13：自然scalar inference的备选表达预期复现（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1；扩读后进入解释型parent，不注册新metric。
- **对应：** C02、P02；主张不升级。来源Hu et al., TACL2023 §4：https://aclanthology.org/2023.tacl-1.50/
- **问题（一句话）：** 原始电话对话中的推断强弱，能否复现作者用备选表达expectedness得到的关联，成为辨别语境表示与作答倾向的parent仪器？
- **设置：** jennhu/expectations-over-alternatives固定commit；原human TSV13,630行，model inputs1,362行（论文1,363，覆盖差异显式审计）。原bert-base-uncased、slow tokenizer、原字符串some→some, but not [MASK],；多处some保留作者使用第一个mask的处理。八候选each/every/few/half/much/many/most/all同一次forward读概率，FP32/TF32关闭。
- **读数：** 1,362×八候选surprisal与发布CSV逐项差/预测token；按原notebook item-mean human Rating与all surprisal/prob的Pearson/Spearman，item bootstrap2000draw seed0。只先复现string predictor；GloVe concept与多变量回归未跑，不能称全部理论复现。
- **阳性对照：** 八CSV全量逐项匹配，首末题batch1/16最大surprisal delta<1e-3，失败暂停；human一对一join、缺项和多mask题显式报数，不删除低相关题。
- **噪声地板 + MIE：** deterministic FP32，发布readout容差1e-3；关联是parent复现不设保证方向MIE；13,630响应不当独立语境数。
- **混杂审计：** bidirectional BERT看到后文，causal模型不能直接同信息比较；模板显式提示备选关系，此概率不等于SI decision；graded相似度不等于二值许可。论文cosine与代码cosine+1权重不同，concept分支先登记不混用。
- **决策表（跑之前写）：** A逐项与关联重现→纳入自然expectedness探针；B数值不一致→审版本/tokenizer/多mask；C覆盖或关联与正文不一致→保留边界不判理论错误；D只此parent有结构→驻留，不包装单点论文。
- **算力预算：** GPU0在E14原14B英语后，权重约0.44GB，≤0.05GPU·时；原数据外置，无API judge，不扩20个benchmark。

## 结果
跑前冻结；数值门通过后才运行全量。
