# Document-Level Event Argument Extraction by Conditional Generation（NAACL2021主会）`[证据级别：正文部分]`

[正文](https://aclanthology.org/2021.naacl-main.69.pdf)；[作者数据入口](https://github.com/raspberryice/gen-arg)。2026-10-06读§1–4.6、Tables2/4–7；附录未读完。

1. **形态：** 自然任务压力＋生成方法＋标注资产。
2. **压力：** trigger附近head/pronoun论元不够信息完整，跨句证据与共指需要联合使用。
3. **改变前提：** 从nearest span转向informative referent；不假设一句就包含一个event的全部论元。
4. **idea来源（DOCUMENTED）：** 实际information seeking需要跨句；文中展示后句付款信息和前文名字解指代。
5. **增量：** 相对BERT-QA/CRF与RAMS，模板条件生成统一角色、多论元/缺失；不是首次role binding或QA。
6. **设计：** BART/T5、copy限制和type clarification；WikiEvents246documents，人工标注events/arguments/coref，nearest与informative两任务、zero-shot另设。源缓存实际3241/345/365事件，与Table2一致。
7. **限制：** 表中BERT-QA-Doc性能下降已有明确discussion，作者指出additional context会分散event focus；跨事件论元混淆或nearest/informative gap均不是我们首创。六release文件未暴露event-coref，不能把不同mention IDs当不同occurrences。
8. **动作：** 同一事实的直接span和信息完整referent两读数；不同任务失败原因细分，避免把所有误差叫长距离。
9. **对本线：** 这是一份已人工标注的自然角色/共指资产，可避免GUM的UDobj→patient捷径；用于核对晚证据如何用于事件角色，不另开EAE benchmark或训练线。需要先逐项验证prefix证据与event identity，不能以原annotation自动认证世界truth。
