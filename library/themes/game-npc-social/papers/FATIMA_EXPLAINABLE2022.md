# Towards Explainable Social Agent Authoring Tools: A case study on FAtiMA-Toolkit

规范记录：`NPC-PA11`；arXiv preprint; peer-reviewed publication not verified。实际版本：arXiv 2206.03360v1, 2022-06-07; author draft retains review disclaimer。

**实际阅读范围：** 全文正文 §0.1–0.10、§1–3，全部统计表/方法；文内提到的问卷附录不在PDF，未取得。

[原文](https://arxiv.org/pdf/2206.03360v1) · [发表／主源信息](https://arxiv.org/pdf/2206.03360v1)

**规范来源：** [Towards Explainable Social Agent Authoring Tools: A case study on FAtiMA-Toolkit](https://arxiv.org/pdf/2206.03360v1)。发表/阅读版本：arXiv 2206.03360v1, 2022-06-07; author draft retains review disclaimer。

**阅读身份与范围：**新读 arXiv 2206.03360v1 全部正文、全部方法与统计表，参考文献浏览。https://arxiv.org/pdf/2206.03360 。首页声明等待审稿，排版仍有未渲染引用及章节编号问题；没有读取到正文所指的问卷附录。因此以 2022 作者预印本记录，不冒充已核查的正式发表版本。

**实证设计：**研究一为 20 名计算机学生，10 名已有至少 10 小时 FAtiMA 经验、10 名无经验，均看十分钟教程后完成十道构造/解释/问题求解题。两组按已有经验划分，不能视作随机训练干预。平均得分 9 对 7.7，p=.017；情绪评价题差距突出，完成时间和总努力未检出显著差异。研究二分析 2021/22 课程的 35 名学生、16 组作业：先实现同一餐厅故事，再创作至少两角色、15 对话状态、三个推理组件的情境。第一任务平均约 95.6 个规则/条件/信念/台词等人工构件，第二任务 178.8、约 3 角色、15.38 交互周期、3.44 结局。

**认识及边界：**作者大部分工作投入对话和决策，情绪构件用得少；这可能来自理解困难，也可能来自作业目标和缺少可见表现，论文未区分原因。其约 21 小时的单人制作估计是小样本小组自报和人数换算，不是实测行业工时；构件数量只是复杂度代理，不能当质量或劳动时间的统一指标。最有价值的发现是“规则透明”不自动意味着创作者能预测行为，情绪概念尤其如此。需要交互式解释、可修改中间表示、快速模拟和因果调试。结尾的自然语言助手为方案设想，未实际验证。此文应与正式工具论文关联，避免把相同课程生态误计成独立大规模采用证据。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents](FATIMA_TOOLKIT2022.md) | 同工具族，后者架构/用例为主，此研究直接测作者理解与制作过程。 |
| [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](STORYASSEMBLER2019.md) | 实际作者项目同样显示生成空间和调试理解之间张力。 |
| [Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation](ORCHID_CREATOR2026.md) | 后者现代LLM作者工具加六个月艺术家案例，透明卡片仍未消除调试负担。 |
