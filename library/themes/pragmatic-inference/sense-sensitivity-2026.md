# Sense and Sensitivity（CoNLL2026）

[原文](https://aclanthology.org/2026.conll-main.4/) · Dawson Petersen / Abhishek Purushothama / Nathan Schneider。阅读：正文§1–6及limits、附录A–D全读；参考文献未逐篇，repo/Box人类数据未获取，未复现。公开review未核对。

- **压力与idea来源（DOCUMENTED）：** 从“模型对无关prompt变化不稳”走向同样材料、同样变化下的人类/模型比较；判断模型是否可代替普通使用者，不假设human自己绝不受影响。
- **自然对象与协议：** 46真实保险语义场景改编×3覆盖条件×2正负frame×2选项order=552；300招募、排12后288人，各6题=1728判断，条件中位数3人。不是552个独立human norm。Llama3.3-70B与4个GPT配置，后两真正开启推理。人的选项是按钮，模型文本Agree/Disagree，尾部Final answer is；有限输出不解析者人工code。两种接口并非完全相同。
- **拥有的claim：** 无关frame/order鲁棒性、人类一致性是两条不同轴；开启真实推理提高稳定性，仍不等于更像human。最佳模型human相关r=.57，跨两人类实验r=.87；reasoning提升稳定后仍有无人选择的模型解释。这是特定任务，不能泛称所有语用都差。
- **分析方法能学什么：** 同一自然item上有实际内容变化与表面frame/order变化；先测无关敏感度再测人类一致性。原作者GLM(version+frame+order)不是participant/item混合效应模型；稳定效应大小不等于所有null已证明等价。复现时不能照抄“p>0.05证明消除bias”。
- **校对与边界：** 模型raw不是全部首token可解析，例如GPT4.1有37/552需人工；不能把“恢复格式”当能力。附录C对GPT4.1/4.1-mini表述版本不完全清楚，source run仍待查；没有独立checkpoint干预证明训练cause。法律情境只作为语义材料研究，不拿gold当法律正确判决。
- **与本workbench距离：** E29负问试验测的是原知识readout极性可识别性；若极性错，不能替pragmatic criterion解释。单独做“CoT让prompt更稳”或“更稳但更不human”已有ownership。若继续跨stage，应识别具体交际证据与目标含义的条件关系，超出generic frame/order效应。
- **资产：** PDF/text在外置papers/2026.conll-main.4.*；作者代码Dawson-Petersen/Sense-and-Sensitivity、human analysis在Georgetown Box，尚未检查。不能登记baseline completed。
