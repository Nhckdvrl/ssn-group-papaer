# Modular Cognitive Architecture Emerges in Large Language Models（2026预印本，正文与关键SI）

主源：[论文](https://arxiv.org/abs/2608.13567)、[作者页](https://pengrui-han.github.io/LLM_Modularity_Page/)、[代码](https://github.com/Pengrui-Han/LLM_Modularity)。核读正文、SI1.1–1.5、SI4–6及SI10；代码只核入口，未复现。未核实主会接收身份。

**DOCUMENTED：** 46任务覆盖语言、形式、社会、物理四领域；六个24B–123B模型。先在最小对照上筛选模型能解的任务（双方均答对率至少60%），以最终提示位置的MLP down-projection输入做activation差×gradient定位，再跨任务干预。主要分析用top0.1%正归因神经元；46×45=2070个source≠target任务对，反事实替换使域内正确率平均下降25.9pp、跨域2.5pp。重叠统计覆盖六模型，阈值及三种ablation稳健性主要在Qwen2.5-32B检查；语义相似性控制含TF-IDF、GloVe、SBERT、输入embedding。不是仅凭表征夹角宣布模块。

**idea来源：** DOCUMENTED为认知神经科学中选择性损伤/功能定位的逻辑：能否由局部功能扰动得到域内大、跨域小的行为效应。RECONSTRUCTED为先建立可重复的行为对照，再把定位结果变成跨任务可证伪预测。相关最小对照、归因patch与反事实ablation均是已有工具，整篇增量来自系统性的功能组织证据。

**证据范围：** task准入及both-correct过滤决定研究的是可解任务上的功能组织；双输入长度一致、固定答案位置与所取MLP粒度也约束结论。域内任务的选择性不等于真实NPC中人物与操作能力天然独立；本研究没有角色自身任务与社交请求的动态裁决。

**对本项目的研究动作：** E74的结构化后果回答是行为读出，不能直接替代内部世界模型。若后续需要神经解释，应从已复现的人物/目标/行动路径对照提出功能假说，以跨任务因果行为验证；不恢复无假说的全层扫描。也不因定位、干预分别已有而压缩我们的整体问题：它们应服务于解释NPC角色取舍与执行推进如何共同形成真实行为。

本地资产`cache/papers/modular_cognitive_architecture_2026.pdf`，SHA256 `3e665aa99ffb68c81c70fb1d2172c24026f6f85c8e6fd68f4fddaeea72a5b92d`。
