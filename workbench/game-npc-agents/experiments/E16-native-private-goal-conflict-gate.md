# E16：原生双方独立目标的利益冲突任务资格（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（C01 / E06的真实战略任务资格；不虚挂idea）
- **对应：** C01 / E14；E14多数NPC目标可立即执行，不能充分测量Persona在真正利益冲突下的作用。
- **问题（一句话）：** 原作者同图角色quest与human demo是否存在共享唯一消耗品/互斥物品目标，使NPC自身行动与玩家行动产生可观察的利益竞争，而不靠抽象trait造唯一gold？
- **设置：** 沿E11固定source/data pins；全7486quest/692匹配human枚举，不按model结果筛。先按source goal text提相同物品候选：两不同角色eat/drink同item，或一方consume同item与另一方get/steal该item。逐候选原graph确认同一object node及native consume将对象移到void/删除，且该物品没有同名第二copy；原角色/目标/motives/世界规则不改。原goal事件与对象获得/消费/后续可达性分开。不把get与consume默认必然互斥，前者可能先取得再交给他人。
- **读数：** 候选/不同graph/角色/goal文本，原human request/action数量、目标合法前置、对象原owner、两方可控action范围；原事件执行后物品/生命/位置的后果。没有LLM时不报人格或战略能力。只确认对象规则与目标兼容结构，actor人格不做正确行为标签。
- **阳性对照：** 原graph load、原Food/Drink目标执行改变物品存在/所有权；源author只一copy；非法动作拒绝且state不变。双方目标可借重排动作共同完成时明确标兼容，不误称zero-sum。
- **噪声地板 + MIE：** 全量元数据确定性；固定首个资格任务CPU native episode0GPU。若原生利益可成立，单完整local双actor episode测预算后另记扩展；若目标只有字符串标注没有物理消费关系，报告不充分，不修改world/correct标准制造冲突。
- **混杂审计：** 仍是同图任务绑定、非官方原partner；human脚本不能模拟适应性，后续需规则或本地player依原作者私有goal，source相同但不声称真人；world随机失败 vs选错/合法行动 vs目标效果分开。没有开放外部游戏或付费调用。
- **决策表（跑之前写）：** 有真实不可逆资源竞争→观察双方私有目标下自述/意图/执行及Pareto机会；只有兼容物品转移→研究合作而不叫竞争；metadata匹配假阳性→保留负准入，不扩大模型矩阵；任何“persona必须选择X”自造评判→禁止。
- **算力预算：** CPU≤10分钟，GPU0；首个双actor model需要另记run前补充和成本gate，总探索≤1GPU小时，07:00起全项目≤8GPU，零API。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

CPU资格完成：36候选方向对/26图；两方consume同item去重8对/8图，其中6对唯一对象与原native消耗删除/另一方目标不可再parse的资格通过。0人类示范严格join到这些冲突对，因此不能声称已有真实玩家竞争轨迹。其余2对目标初始不可执行/物品条件未通过，保留全部，不改图。数据见E16_resource_qualification.json。下一步若有信息再用规则/本地player，双角色私有动机原作者授予，NPC不能自动知道对手goal。
