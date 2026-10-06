# Identifying and Answering Questions with False Assumptions: An Interpretable Approach（EMNLP 2025）

**证据范围：** primary引言、§2、§3.2–3.3、§4主要结果/错误分析、§5与结论；§3.1及附录未完整核对。[原文](https://aclanthology.org/2025.emnlp-main.1228.pdf)。暂停前阅读的补记。

1. 论文形态：诊断＋检索/atomic-assumption方法。
2. 压力：fact verification不足覆盖问题暗含假设；常规回答可能事实正确而没处理错误前提。
3. 改变前提：把问题拆atomic assumptions、逐个验证，再给可解释答案。
4. 来源（DOCUMENTED）：QAQA/CREPE/FalseQA的question-vs-statement及外证据对照。
5. 距离：跨三个现有corpora，retrieval与原子假设组合；不是仅新一套false-premise问题。
6. 实验：五LLM及baseline，解释可读性、计算成本、错误类别；知道question有错误前提也未必给出正确解释。
7. 短板：retrieval/生成假设仍有误，完整assumption recall难定义；标注错误和不自然修订问题被作者显式讨论。
8. 动作：验证question assumptions与answer correctness分开；保持genuine问题，少量机械扰动不能替代数据质量。
9. 对我们：generic“事实知道但问题诱导出错误”已有owner。E50/E51须明确增量与自然功能后果，不把指令恢复或count词语歧义本身叫好idea。
