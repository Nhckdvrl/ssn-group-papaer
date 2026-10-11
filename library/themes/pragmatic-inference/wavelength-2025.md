# On the Same Wavelength? Evaluating Pragmatic Reasoning in Language Models across Broad Concepts（EMNLP 2025 main）

**证据：正文、related work、方法、appendix A–G、代码/数据已读；末尾逐模型分布图尚未全部校对。** [原文](https://aclanthology.org/2025.emnlp-main.1008/) · [代码](https://github.com/linlu-qiu/wavelength-eval)

1. **形态：** human-distribution benchmark + RSA实验。
2. **压力：** 固定gold/离散现象忽略开放概念和人类不确定性。
3. **改变前提：** 给clue恢复连续scale位置，比较完整概率分布；理解与production角色分开。
4. **来源 DOCUMENTED：** Wavelength语言游戏、RSA和graded pragmatic inference。
5. **近邻：** Hu细粒度、Multi多语、Wu自由生成；本工作已拥有强模型mean近人类和分布过窄/spiky，不能把后二者再次claim。
6. **协议：** 50concept pairs×2targets=100；每项40human responses，总4,000；先由人筛选高质量clue。原开放家族Llama3、Gemma3、Qwen3。listener评所有21位置的完整assistant `<answer>n</answer>`，含chat结束tokens，非单digit；parent明确enable_thinking=False。
7. **短板：** 挑选好clue限制生态分布；paper使用expected位置MAE，repo还报告argmax误差，必须分开；listener fullsequence仍是prompted task，不能当自然字符串knowledge。无二值warrant标签。
8. **动作：** 原模板/likelihood数值parity → human/model distributions，concept-pair cluster CI；RSA production成功不能套成listener必然变好。
9. **对我们：** graded instrument，不是直接证明binary-MCQ artifact；初版Qwen3 thinking错误读数已作废，重跑原protocol。
