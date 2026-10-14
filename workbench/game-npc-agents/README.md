# Game NPC Agents — 游戏中的自主非玩家角色

**状态：PROPOSED；用户选定本轮优先矿区 A：人物设定、真实利益与战略行为的关系。** 全局ACTIVE状态不变；安全、人格漂移、社会互动和游戏经济仍开放。允许结果显示Persona对真实行动很有效。

## 当前研究动作

追问同样的角色属性变化，何时改变利益取舍、何时只改变可替代的行为；以及这些控制路径怎样随训练形成。依据真实轨迹发展解释和方法，不先规定GRPO／steering／新损失，也不用自设MIE、通过比例或噪声倍数判科学价值。

- **原生NPC闭环：** ActionCastle／LIGHT已恢复。E35原三人校园世界三个自然episode各1200帧，129/129/166本地27B调用、5/5/8对话；首episode完整cassette独立回放一致。正向目标对应与地点/计划异常均保留，新增承诺超出episode边界的不记失败。E42两强模型与具体偏好提醒参考正在八卡执行原生200cycle闭环。
- **PCSP完整预算：** E34正确编码、原作者300轮预算，三seed×Full／No全部完成（4608万原生transitions）。30／100／300轮全部保留；300轮Full局部人物利益响应三seed更强，完整游戏收益三seed较低，正在拆状态与长程后果。E41等预算比较原训练、等义表面扩充和C属性干预覆盖；先检验普通数据解释，不预设新损失。
- **功能测量：** E37同人物／状态／latent幅度，分开测等义变化、C属性编辑和作者原生收益方向；60000动作累计reward完全重建。E39跨人物交换方向并加入局部功能参考，拆表征方向与控制响应。当前继续查状态分布／人物利益结构等解释，尚不据此推一般能力结论。
- **独立战略环境：** E38恢复原MeltingPot2.4.0／DMLab2D1.0.0；26次默认/强/正确编码训练与360完整原生episode均完成。正确码Full−No团队return−12.54、五seed簇95%[−38.52,13.43]，内部读取38.1%/6.9%，不同层次分别解释。PHASE5源码稀疏检出遗漏已纠正，作者独立读出路径完成数值审计。

[实验卡](experiments/) · [结果与校对](results/README.md) · [完整日志](logs/2026-10-14.md) · [I02形成机制](ideas/I02-causal-separation-of-role-control-and-readout.md) · [主张账本](CLAIMS.md)。C01仍为L1基线可行性；研究主张根据证据继续形成。

## 阅读与执行入口

[LOCAL_AGENT_START](LOCAL_AGENT_START.md) · [EXPLORATION_ENTRY](EXPLORATION_ENTRY.md) · [领域地图](knowledge/DOMAIN_ATLAS.md) · [人格—行为知识](knowledge/persona-behavior/) · [源代码审计](knowledge/persona-behavior/SOURCE_AUDIT_2026-10-14.md) · [强近邻定位](knowledge/persona-behavior/RELATED_WORK.md)。源代码事实、我们的解释与未排除的竞争解释分别记录。

不自动恢复已撤出的E00／E02–E05，不建立第二套工作台。优先原作者人物／目标／合法动作与实际后果；自述表达、特定场景意图和执行策略分开；抽象标签不对应唯一正确动作。

## 资产位置与重建

完整轨迹、checkpoint、模型输入输出保存在`/home/xiang/.cache/game-npc-research/runs/`，不进Git；E35完整三人轨迹在`e35_original_cast/`。模型复用HuggingFace缓存；上游源码在同缓存`sources/`，版本与hash见各结果manifest。原PCSP主pin5420f7b与MeltingPot隔离分支4fbbffa分别保留，不改运行中源码。

环境优先现有Conda／venv：NPC／Mini-Inzoi用fgvd＋deps overlay，MeltingPot用lightwam＋项目隔离overlay。用户已授权七节点全部GPU；07:00 Asia/Tokyo起本项目最多8卡，不干扰其他任务。核心链路零付费API，不允许SDK云端fallback。依据实际计算特点使用GPU；先原生完整episode再扩大。
