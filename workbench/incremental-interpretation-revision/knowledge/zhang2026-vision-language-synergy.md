# Think Visually, Reason Textually: Vision-Language Synergy in Abstract Reasoning

分开规则发现与执行：Zhang等，CVPR 2026，主文§1–5。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 子任务机制诊断与修复方法。
2. **背景与压力：** [会议原文](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Think_Visually_Reason_Textually_Vision-Language_Synergy_in_Abstract_Reasoning_CVPR_2026_paper.html)。ARC/ReARC/BARC，4个VLM；先分离规则提取与应用，再以视觉找规则、文字执行、视觉检查生成网格。平均约4.3pp，主文未给重复seed/CI；微调对比中双8B模块与单8B文字模型不等参数/算力，不能全部归因于模态互补。
3. **改变的前提：** 某模态整体优劣可能由方向相反的子任务掩盖。
4. **idea来源（RECONSTRUCTED）：** “视觉更直观却不一定更会解ARC”的压力被拆成两个方向相反的子任务，随后才设计VLSR/MSSC。相对Visual Sketchpad、ViLaSR和ARC记忆方法，距离在角色分工及视觉检查。网格的图/文字表达可互相转换，检查并未引入新的外部事实；收益可能是访问已有信息更容易。主表/正文的部分分数不一致，按具体实验解释。对我们最重要的是拆开结构发现、关系使用和错误检验，而不是泛称多模态能纠错。
5. **与近邻的距离：** Visual Sketchpad；ViLaSR；ARC记忆/规则方法；text-only self-correction；增量在分工与视觉检验。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main sections 1-5 and acknowledgements; appendix not read。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
