# Who Says What（NeurIPS2026名单核对，2026-09-25作者v1主文）

证据：[作者主文](https://arxiv.org/html/2609.31193v1)§1–6完整；AppA1、A3–5文字、B1–3、E/F，A2/C图与D示例未逐图深读。KAIST/Oxford。官方accepted cache记录title/authors/OpenReview M0fBuZdipl；正式最终稿与评审未核对。HTML SHA806c4ff147aef14d8a23b22e5b9082eb08c9e4f383066f29728fb02ab2eab291。

1. **形态：** 扩大binding对象＋分阶段机制/特定失败入口＋轻量方法，自然任务回接机制。
2. **压力：** 同时出现多个讲话者时AVLLM常把话归错人；识别词/人并不解决音画对应。单模态binding ID机制如何跨两个不同坐标系仍不清楚。
3. **改变前提：** 不假定实体内容直接跨模态绑定；先取anchor ID，再转为另一模态target ID，最后检索内容。这里时间ID与空间ID的转换是新的失败对象。
4. **idea来源（RECONSTRUCTED）：** Feng2024文本binding IDs→Assouel2026 VLM symbolic spatial IDs→自然多说话者归属失败→三模态多坐标轴→因果factor swap的阶段预测→已成熟ASD补缺失对应。创新来自具体转换与真实后果，不在bbox/patching工具本身。
5. **近邻距离：** Feng实体属性连接，此文time↔position ID转换；Assouel视觉坐标ID，此文语音时序；Kim/VLM binding修复，此文定位三阶段；AVSpeaker/DiaDem已有难题，此文机制；VISER/NumPro视觉prompt已有，此文用ASD提供正确跨模态关联。不是寻找完全空白的工具或数据。
6. **方法/材料：** 4动物×4位置×随机country utterance时序，AAVR/VAAR。800 RSA、960 CMA，4 models（SALMONN2+7B/Qwen2.5Omni3/7B/MiniCPMo4.5）。机制主要在正确primed输出上：先给另3speaker-word正确示范；native约27/29.6/28.7/0%，primed约99–100%，prompt-only约1/12.5/12.5/.06%。交换utterance order、speaker位置保持原答案不变，patched expected target变，语义内容变体另做；attention output quarter-depth window。失败修复按100样本挑top10head，800primed平均状态，inject未primed；SALMONN27→51、Q7 29.6→49、Q3 28.7→45.4。real SocialOmni2000两人clips只RSA；训练400synthetic human videos→2040QA/caption例，LoRA rank16，140/250step单A6000。
7. **强度/边界：** 因果操作有独立factor与预期反事实，比仅几何相似更强；但primed成功conditional不代表全部native机制，repair只部分恢复，“同回路”推断有边界。ASD引入外部检测先验，不是纯内部已知信息重读；自然real-world机制只RSA，未同样因果完整复现。QA无CI，caption±为同一输出多次Gemini judge方差，非模型训练seed方差。training-free SALMONN多数不增/降；Q7 AVSpeaker44.86→45.59、Social38.95→41.90；FT后48.79/44.25等。一般benchmark不画ASD，因此ASD=vanilla、只有FT迁移；FT原同数据对照DAVE35.15优于ASD-FT33.91，并非全数据都赢。prose若干“平均7.9/9.7/3.5”未重建统一口径，不照抄。
8. **可借动作：** 分开取实体、转换绑定索引、取内容；保持原答不变的独立factor swap产生不同patched反事实；方法只补诊断的转换缺口，同时报告未受益模型。不机械复制head/窗口全网格。
9. **对我们：** 全源whole-vector效应不认证具体语法/身份因子，C09仍限定L1。E70原子关系与E71局部说明消费可决定要找哪个转换；此文说明近邻已做机制不等于领域没空间。潜在增量必须是“解释修订”中约束如何成为后续绑定的正确/错误输入，不能只是把time/position ID换成GP。
