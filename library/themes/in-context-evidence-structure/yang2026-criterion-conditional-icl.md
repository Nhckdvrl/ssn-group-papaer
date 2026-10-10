# Criterion-Conditional ICL（ICML2026，venue corpus）[v2主文§1–6]

[v2正文](https://arxiv.org/html/2607.02575v2)，Kaiyun Yang等。2026-10-10读主文§1–6与表1–4；接受状态来自本地venue corpus，未再核官网。附录与代码未完整读。

1. **形态：** 问题/测量/benchmark与构造性训练。
2. **压力：** 同一个异常检测任务、同一图像，可以因容忍标准不同拥有不同合法答案；单context accuracy不测标准适应。
3. **改变前提：** 同query和support输入、改变support标签，分别测标准敏感案例与不受标准影响的案例。
4. **idea来源：** RECONSTRUCTED；固定任务语义下阈值变化→成对context→敏感性/不变性读数→多标准训练。非真实发现时间线。
5. **距离：** 多模态ICL/task induction与预训练prior；与ICES共享标准适应问题，不能声称首次提出从demo推断criterion。其主旨为能力测量和训练，未建立native来源状态/地址的因果机制。
6. **实验：** 工业/医疗/视频3580测例；3-shot同support图像、仅敏感示例改标签；7种base VLM。LoRA r4训练两轮，跨类别/领域与两→三标准迁移，shot和图像/文本prompt对照。CS要求同query在两标准下都答对，CI要求不变案例两边都对。
7. **边界：** CS/CI受基础任务难度影响；CoT比较不证明其宣称的内部机制改变；有限prompt对照不证明所有prompt engineering无效，也不证明必须额外训练。三标准迁移比ID涨分更有信息量。
8. **可迁移动作：** 先让几种解释对同一个query产生不同答案，再用不变案例控制整体输出偏好，避免只报总分。
9. **对ICES：** E88的相反/同向评论已有强测量参照；待测增量是多个标准同时共存、同名字的标准相关信号与recipient证据竞争。此差异须用因果结果建立，不能仅因任务文字不同宣称novelty；不作为桌面关线理由。
