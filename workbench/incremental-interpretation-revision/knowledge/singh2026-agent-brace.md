# Agent-BRACE: Decoupling Beliefs from Actions in Long-Horizon Tasks via Verbalized State Uncertainty（2026-05作者v1，接收未核对）

`[证据级别：主文精读＋指定附录]` [arXiv2605.11436v1](https://arxiv.org/abs/2605.11436v1)，UNC/UT Austin/Microsoft。25p PDF SHA67ed87fd97413a234a02094b66ca7d156c96b7730191c6a6a06908b2c7f81797。官方缓存未找到精确title，不据此判质量。

1. **论文形态：** state/policy职责分解＋训练方法＋跨任务泛化。
2. **背景与压力：** 未观测世界属性需要不确定性，历史context不断涨；旧memory把推理/当前事实混合，训练和评价接口不清。将belief model与policy共同训练，belief逐原子claim附WEP certainty。
3. **改变的前提：** 将仅压缩history推进到面向后续action的可表达近似状态，不只是改变存储形式。WEP边缘claim并不是完整联合posterior或充分统计的证明。
4. **idea来源（RECONSTRUCTED）：** POMDP充分状态理论→自然语言point summary缺uncertainty→分开belief/policy并设计可密集评分的state更新→用OOD任务/15→100steps检验用途。研究尺度来自新接口、reward职责与后续消费，不是发明自然语言belief概念。
5. **最近邻距离：** MEM1、ABBEL、PABU、StateAct已有摘要/显式state；本文增量是WEP层级与joint train、多个reward、heldoutQuest/Treasure/Cooking及ALFWorld。一般“答案不等于state”和“奖励state”都有owner，I07需要具体观察解释到credit失配的机制。
6. **方法与实验：** 两Qwen基族3B/4B，Quest训练、3TextWorld域，1k/100/200games每套seed分离；训练15turn评估100。训练4A100/TP2，teacher SFT再RL；额外ALFWorld三次评估。claim correctness与tracking judge为Qwen30B，truth/judge不等于概率oracle。
7. **reward细读：** tracking是新增信息coverage×retained prior freshness，包含Nmissing，所以**不是只precision/漏掉缺失惩罚**；correctness看被表达claim与simulator state；diversity奖励certainty标签hist entropy；format乘法门；discounted task success。后者不替代前两者。未知标成p≈0的Brier不等于不知道事实为真的概率应为0；不能照用此定义判断GP能力或完整belief。
8. **证据边界：** Main1–6 pp1–9全，AppA–K pp13–22与24–25全（Prompt5 p23未读）；Tables2/4/11与Fig4/5已文本核，p8图4视觉核对。References10–12、代码未全读。主表3B PABU59.5高于DirectRL58.3，故“strongest基线+14.5”要按所选Direct报，不能称超过真实最强14.5。4B Cooking69低于DirectRL75.5，跨域不是每项都更好；摘要平均成绩不抹阴性。
9. **进一步校对与可借：** Brier正文.40→.28却称“below.25 throughout”数值不符；fig显示逐episode step，不是单独训练全过程校准。训练开始reward低不能证明SFT只学format，未提供knowledge-transfer干预。J仅移除judge two rewards，4B Cooking升69→82，表明职责不总同向。借从具体错误到职责设计和用途检验，不把这些文本矛盾挖成论文bug题。对I06/I07：要能说清所修操作、reward给它什么信号、后续哪个用途变好；先高信息pilot而非补成稿控制链。
