# When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs

自我纠错：Kamoi等，TACL 2024，主文§1–12。`[证据级别：主文精读，附录范围见下]`；接收presentation/公开评分未核对。
1. **论文形态：** 条件综述与测量重构。
2. **背景与压力：** [原文](https://aclanthology.org/2024.tacl-1.78/)。压力来自自我纠错的正负结论冲突。作者将“自身能力能否纠错”“外部反馈能否帮助”“最终系统是否更好”分成三个问题，并检查初始回答是否尽了同等努力、是否用了oracle停止条件、是否比较等算力采样基线。
3. **改变的前提：** 自纠错收益必须相对同等初始努力与反馈信息比较。
4. **idea来源（RECONSTRUCTED）：** 不是再发明一次反思提示，而是找出不同结论实际在回答不同问题。相对Pan的广综述和Huang的局部负结果，增量在更完整的条件分析。可借动作是直接测反馈质量与错误转移；2024年的结论不能直接外推2026年的RL推理模型。
5. **与近邻的距离：** Pan等自纠错综述；Huang等内生纠错负结果；Madaan等Self-Refine；Gou等外部工具纠错。重建的是论文论证中的研究动作，不冒充作者实际发现历史；定位不产生自动关线判决。
6. **方法 / 实验 / 数据 / 基线：** 第2/4项记录已核对设置与主表范围；可复用资产由原文链接取得，不把benchmark条数当独立统计单位。
7. **证据边界：** 实读范围：Main sections 1-12。PDF与失败/版本记录位于`/data1/xiangding/work/incremental-interpretation-revision/papers/reassessment-2026-10-07`；未核对的最终版本、review/score或附录不补猜测。第4项的局限必须随结论引用。
8. **可迁移研究动作：** 把第3项前提转成能被推翻的测量，并保留旧解释与阳性对照；先对齐对象和信息/算力，再决定是否迁移方法。
9. **对我们：** 第4项给出具体可借动作与不可外推边界；与I03/I04的共同定位见[整体画像](REVISION_RESEARCH_SYNTHESIS.md)。当前没有因此升级主张或得到合格idea。
