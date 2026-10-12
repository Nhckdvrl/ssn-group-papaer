# Syntactic Belief Update as the Driver of Garden Path Processing Difficulty（Zhou, Stanojević & Hale 2026）

**阅读身份：MAIN_VERIFIED_THIS_PASS（作者arXiv v2 HTML，2026-10-12；定义、数据、结果定性读取；图中数值未抄录）。** [arXiv 2606.27206](https://arxiv.org/abs/2606.27206)，v1 2026-06-25、v2 2026-08-29，JHU/UCL。预印本。

## 1. 未知与来源
**AUTHOR-STATED**：lexical surprisal对GP困难预测差；他们提出困难来自**句法信念的更新量**，用去词汇化依存树分布的Rényi散度衡量一个词带来的信念变化。
**RECONSTRUCTED**：把Narayanan & Jurafsky的贝叶斯加工和Frazier/Fodor的重分析概念合并成一个可计算量；技术上靠增量非投射CRF依存解析器（RoBERTa-large biaffine，未来词用MASK）给每个前缀一个全句树分布，这是“工程使理论可测”的典型路径。

## 2. 设计
- 度量 D_α(p‖q)，q为词前信念、p为词后信念，闭式由配分函数得到。
- 数据：SAP benchmark GP部分（NP/S、NP/Z、MV/RR各24句+控制），阅读时间差。
- 对照：lexical surprisal、CCG supertag surprisal（Arehalli 2022）。

## 3. 结果
- 所有指标都低估绝对困难；**只有SBU复现NP/S < NP/Z < MV/RR的难度排序**；α越大越接近人类幅度；在自然填充句上训练仍保持排序。
- 构式内逐项相关上SBU不占优（噪声上限低）。

## 4. 对本workbench
- 这是“重分析=信念更新量”的理论形式化。它只解释**困难**（RT），不解释**最终是否重建**。我们的对象正好是它不覆盖的那一半：更新量大之后，替代依赖有没有被写入。
- 可借：用解析器分布定义“晚到证据要求的结构变化量”作为每句的协变量，预测哪些句子的替代依赖更难被LLM断言（见07_EXPERIMENT_FOUNDATION X3）。
- 边界：英语三构式、线性RT链接、单一树表示；作者自述其它树库/指标常不匹配人类模式。
