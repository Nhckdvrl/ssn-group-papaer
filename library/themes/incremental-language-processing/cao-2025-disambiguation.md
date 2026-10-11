# Are Larger Language Models Better at Disambiguation?（CMCL 2025）`[证据级别：正文 §1–7 + 刺激形式]`

[全文](https://aclanthology.org/2025.cmcl-1.20/)。评审分数未核对。

1. 论文形态：反直觉观察 + 解释区分实验。
2. 背景与压力：强模型是否在晚到证据后恢复正确structure，不能由总体语言能力推断。
3. 改变的前提：用disambiguated prefix的completion所需结构判定，而不只依赖comprehension问答。
4. idea来源（DOCUMENTED）：Altmann 1992人类context刺激，结合模型scaling与noisy-channel/text-error解释。
5. 与近邻距离：Aina/Linzen用生成测歧义；Hanna追内部机制；Li/Amouyal用QA；本文用结构指示的completion与error对照区分“恢复”与“忽略坏输入”。
6. 方法/数据：30 RC/complement prefixes，每模型每项50次temperature1生成，五模型家族；删除主句构造不可能合法完成的局部矛盾对照；36基础项生成72 reflexive pairs检验下游binding。
7. 证据与短板：较大模型completion更少合法；error对照支持更依赖广context、将局部矛盾当文本错误的解释。binding方向一致但显著性弱，限英语/此类歧义；自动parser判断有误差。
8. 可迁移动作：观察到“晚证据没起作用”后，不只加模型；构造让竞争解释给出不同预测的对照。此处一个error条件改变了原观测的含义。
9. 对我们：下游依赖与noisy-channel并非无人研究。可借其研究动作：E01若cue/extension呈稳定分离，就优先改变证据的合法性/诊断性，明确区分修订、忽略、语义补全，而非只做更多prompt。
