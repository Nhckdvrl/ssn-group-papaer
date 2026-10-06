# When Only Time Will Tell: Interpreting How Transformers Process Local Ambiguities Through the Lens of Restart-Incrementality（ACL 2024 main）`[证据级别：全文前半 + 结果片段（arXiv 2402.13113v2）]`

1. **论文形态：** 可解释性分析方法 + 受控刺激。
2. **背景与压力：** Schlangen 组增量 NLU 这条线：因果模型的 token 表征是静态的，不能修订已经输出的结果；restart-incremental（RI，每来一个词就重编码整个前缀）可以修订，但以往只做黑盒评估。
3. **改变的前提：** 把 RI 的状态序列形式化为转移系统，对内部状态做白盒分析，看什么时候、为什么会发生修订。
4. **idea 来源（DOCUMENTED）：** Schlangen & Skantze 2011 的增量单元框架；TAPIR（Findings'23）的修订策略；用 GP 刺激作为"已知需要重分析"的测试材料。
5. **与最近邻的距离：** 相对 Jurayj 2022（GPT-2 几何）研究的是双向 RI 模型；相对 Eisape 2022（因果模型的增量 parse 探针）强调"能否修订"；引用 Springer 2024 的 echo 重复作为让早期 token 看到后文的相关做法。
6. **方法与数据：** 双向编码器（语义表征、依存句法）的 RI 状态矩阵；GP 刺激；对角线和若干特定位置的差异分析。
7. **证据与短板：** 结论是因果模型不能修订、双向 RI 能。研究对象是标注任务里的双向编码器，没有涉及因果 LLM 的理解问答，也没有涉及因果模型通过后续 token 完成的"推迟修订"（Zeng 2026）。
8. **可迁移的研究动作：** 把"同一个模型、不同的可见范围"当作分析维度。
9. **对我们：** 它把"因果 = 不能修订"当作前提；我们要问的是，在因果 LLM 里，修订**以什么形式**发生、什么时候失败。"读两遍"相当于在同一个因果模型里制造一次局部的 RI。
