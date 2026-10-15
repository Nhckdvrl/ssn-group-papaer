# 人物、后果理解与真实选择：研究尺度校准（2026-10-16）

中心仍是有自身作者目标的NPC怎样响应社交请求，而非通用规划器、人格问卷或一个引擎菜单缺陷。推进I04/C06/P12，不更改PROPOSED/PROMISING和主线分配；论文正文暂缓。

| 强近邻与实际已读内容 | 已有ownership | 本轮判断与研究动作 |
|---|---|---|
| [Principled Personas](../papers/PRINCIPLED_PERSONAS_EMNLP2025.md)，EMNLP2025主会 | 角色的期望/非期望任务效应；能力、相关性与忠实度；先能力回答再persona改写 | “人设也会改变能力”本身不够。物理真值与角色愿意做什么分开，然后验证其对真实取舍的解释。 |
| [SimpleToM](../papers/SIMPLETOM_ICLR2026.md)，ICLR2026 | 显式信念与应用行为推断差；提醒/CoT干预 | 仅说预测对却不执行是旧问题。要看错误后果判断替换能否解释同任务人物效应随前提改变。 |
| [TriEx](../papers/TRIEX_ACL2026.md)，ACL2026主会 | 游戏真实执行、显式社会信念、rerun控制、数值profile干预 | E74表格替换是诊断，不是新技术。动作后果真值/自身目标/人设三者联合读出仍需实测。 |
| [Trust一致性预印本](../papers/TRUST_BELIEF_BEHAVIOR_2025.md) | 多轮角色预报—行为与self-conditioning，时距变化 | 不能声称此前没有序贯角色信念研究，不能把自我预报当物理世界模型。 |
| [角色信念v3](MECHANISTIC_NEIGHBORS_2026-10-15.md) | truth probe与行为辩护/推理推广联合识别；probe局限 | E74黑盒预测不命名为内部信念；若要神经结论须有额外因果证据。 |
| [PSALM](../papers/PSALM_NAACL2025.md) / [AGWM](../papers/AGWM_2026.md) | 原生前提反馈与动作模型学习、动态世界模型 | E73反馈帮助执行属于强普通解释，不自称新规划方法。 |

**为什么领域会关心：** 可控NPC需要在保有不同角色取舍时具备可靠动作能力。若把任务完成分数直接看成人物目标偏好，就可能把动作知识改善误判成人设/价值改变，也可能在提高执行后才暴露新的资源去向。现有数据里这两类变化真实并存；下一步要给出能在同角色、任务和处境上检验的解释，不为“控制能力与人格独立”的预设定理搜证。

**当前候选解释：** H1人物改变行动后果预测/采用，H2理解相近但推进与受益对象选择不同，H3加入明确动作链本身改变注意力/行动机会。E74独立分叉先测客观预测，再以同格式自产表格/原生真值表格闭环执行，缓存E73为额外脚手架参照。所有结果可以改变判断；不设显著性/保留率bar。

**Compression risk：** 只得到“给正确信息更好”“多一步更难”“persona影响正确率”会落入现有结论；这也是为什么oracle替换只作为解释工具，最终应回答人物行为评价何时混淆执行推进和目标取舍，而不是把表格包装成新框架。若同样正确预测仍有角色差，也先检验具体动作/优先采用，不直接钦定预训练社交劫持。

本轮venue查询：`nearest "Persona-conditioned action effects beliefs versus preferences in autonomous game NPC decisions"`，返回Principled Personas、PANDA、TriEx、PAMDP及Trust预印本；分数/接收状态只作地图，不替代全文与科学判断。官方最新主源检索已核，awesome入口沿library/sources/AWESOME_LISTS.md，只读未新开复现。
