# Prompting is not a substitute for probability measurements in large language models（EMNLP 2023 main）

**证据：正文方法/相关工作/讨论已读，附录入口已定位；附录全部实验图未逐项核对。** [原文](https://aclanthology.org/2023.emnlp-main.306/) · [代码](https://github.com/jennhu/metalinguistic-prompting)

1. **形态：** evaluation validity finding。
2. **压力：** 负prompt结果被解释成缺乏语言知识，却额外要求metalinguistic access。
3. **改变前提：** direct string概率与“报告自己的判断”不同。包含word prediction、semantic plausibility、syntax isolated与minimal pair，不是专门语用实验。
4. **来源 DOCUMENTED：** 对语言科学中prompt负结果与能力理论的推论做测量校对。
5. **最近邻：** Kadavath/Mielke关注honesty/expressed uncertainty；Turpin关注CoT解释忠实性；本工作直接比较字符串概率和metalinguistic回答。Hu fine-grained使用numeric MCQ，仍是meta读数。
6. **实验：** Flan-T5 small/large/XL与curie/davinci variants；P18 384、2023News222、semantic395、SyntaxGym345、BLiMP390；direct与三类zero-shot prompt。
7. **边界：** prompt/task更远，相关下降；minimal pair更有效。不是所有prompt都劣、不保证直接概率永远反映pragmatic knowledge；现代chat模型泛化未复现。公开评审未知。
8. **动作：** 同题readout对照、自然continuation与option概率区分、恢复指令。
9. **对我们：** Hu的raw numeric MCQ logprob和Wavelength bracket-answer logprob仍有metalinguistic task，不应标成“直接读取语用表征”。E06恢复不证明能力缺失或latent knowledge。
