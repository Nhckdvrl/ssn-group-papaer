# Attention Sinks and Compression Valleys in LLMs are Two Sides of the Same Coin

`[证据级别：主文精读；具体版本/附录见ledger]` [原文](https://proceedings.iclr.cc/paper_files/paper/2026/hash/1734b19d9afe7d2c7f1154954eaf0d5a-Abstract-Conference.html)。

1. **形态：** 统一现象的机制、几何界与消融。
2. **背景与压力：** sink和compression可由同一大激活驱动；已有观察缺少对对象/操作的明确拆分。
3. **改变的前提：** 大激活、attention sink和谱压缩未必是三个独立现象；但谱能量熵下降不能自动解释成语义互信息丢失。
4. **idea来源（RECONSTRUCTED）：** 将sink的异常大向量与中层谱能量集中放到同一个几何对象上，提出共同原因，再用BOS-MLP消融和训练轨迹检查它是否同时改变两种现象；最后把已有深度分工观察组织成mix–compress–refine框架。它的尺度来自统一机制与跨模型验证，不只是给层段命名；不冒充作者真实发现顺序。
5. **最近邻距离：** Sun/Gu的sink现象、Barbero的大激活与sink分析、Skean的深度压缩及Csordás的层功能研究提供邻近部分。本论文把sink与压缩联系并解释一般深度组织；我们的E55早层效应本身未超过这个范围，I05须产生针对修订的独立关系预测。
6. **方法/数据/基线：** 6基础模型/5族、7.5k GSM8K、BOS-MLP消融及训练轨迹；LogitLens/probe+32MTEB，扩展至120B。谱能量熵不是任务MI，大向量不是必然意味更多语义；附录证明未重推。
7. **证据与短板：** Rayleigh/norm界对应谱量，不证明任务语义损失。早/中/晚边界是经验框架，论文有模型例外，不能移作每个GP关系的定律。已读正式会议PDF主文§1–6，附录未完整读，证明未独立重推；LogitLens与probe也不替代关系的因果使用证据。
8. **迁移动作：** 先检验共同原因能否解释两个独立现象，再设计保持源计算不变的干预，把一般深度组织与特定修订路径区分开。只有可预测的用途差异与选择性恢复，才可能成为本线的具体增量。
9. **对我们：** I05必须超过一般早/中/晚分工与证据使用gap，找到修订具体的新预测；不能因局部近邻关闭idea。
