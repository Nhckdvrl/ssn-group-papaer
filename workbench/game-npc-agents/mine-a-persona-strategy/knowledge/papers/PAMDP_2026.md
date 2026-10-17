# PAMDP — ICLR2026

- 主源：[正式论文](https://proceedings.iclr.cc/paper_files/paper/2026/file/3416b3266ec9bbdab2097c78ef203b67-Paper-Conference.pdf)。已读§2–4、表2／Appendix D奖励与模拟用户prompt、Appendix E表6及动态profile实例；未完整复核全部证明／训练代码，正文未找到可确认作者代码链接。
- **正文事实：** 将对话对象的profile设为actor不可见的动态上下文；冻结LLM表征→低维连续action→再投回LLM生成。先BC，随后A2C，使用history critic与profile-aware critic，并以初始policy KL约束。原式优势为r+γV(h′)−V(h,ω)，非仅增加第二个预测头。
- **评价事实：** ALOE／PrefEval及LLM模拟交互，72B模型给偏好reward并裁判；表6同为相对Vanilla的rw，BC .4050、普通RL .4300、双critic .4655；双critic对普通RL直接比较rw .0311。不是游戏中的物理收益。
- **idea来源：** 交互中未显露的信息可由训练时critic利用，不能将“人格进入critic／低维行动／互动中推断profile”据为首次。启发我们区分角色文字、可观察游戏反馈与训练特权信息。
- **距离与竞争解释：** 本轮NPC自己的作者目标通常直接给policy，区别于隐藏用户profile。需要用真实可见信息和原生后果研究控制形成；不因它覆盖一部分技术就舍弃该问题。未复现其训练，不把论文效果当本地结果。
