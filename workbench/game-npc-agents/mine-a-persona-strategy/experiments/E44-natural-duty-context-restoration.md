# E44：自然对话中已有责任与时钟的普通恢复对照

- **状态：** DONE。
- **类型：** REPRO／发现性竞争解释诊断；不是新方法或人物失败主张。
- **对应：** P11、C01来源校对；回到人物、具体社会互动与实际后果的中心。
- **问题（一句话）：** E35 seed3502教授在10点讲座期间邀请学生去别处讨论，是否能由对话阶段缺失当前时钟／已有教学责任解释？
- **源事实：** 原persona是“precise and warm with students”；本人原schedule含10:00 Irvine讲座。turn787／call77的speak输入只有persona、当前地点和六条与学生相关的记忆，没有当前时钟或讲座时间责任。双方随后承诺立即去Williams，原planner保留已过去的10:00 stop在later_stops；后续实际教授离开Irvine。不是只看静态字段；也不自动认定教授不许改变教学安排。
- **竞争解释：** H1时钟缺失；H2教学责任在对话检索中缺失／不显著；H3模型合理重新安排教学，或原计划／执行调度本身影响地点。普通事实恢复已可解释的结果不冒称新机制。
- **设置：** 同agent-sandbox d7b872e、原3502三NPC／地图／时钟／1200ticks、原27B与原budget/schema/temperature。严格cassette恢复0..786的完整状态；从787起采用本地模型，三分支：native、clock、clock_and_duty。只在教授speak消息末追加一句真实事实：当前HH:MM[:SS]；后者同一句还说明作者安排她10:00在Irvine主持讲座。不要求拒绝学生或规定唯一行动，不改任何世界规则／角色／奖励／event。其余所有角色和组件使用原消息。先完全CPU回放1200frames并检查prefix；再一个GPU顺序跑三分支至原episode结束。
- **读数：** 教授对话原文／具体承诺及是否谈及时钟／讲座，outcome／计划变更与实际parser执行、地点活动连续段，学生是否响应、后续社交机会。表达／意图／合法执行／material变化分开；perform lecture或sketch仍只是引擎活动，不冒称物品或教学完成。保留所有分支；不以“留下来”当唯一成功gold。
- **阳性对照：** 同原cassette的1200frames复现；三个prefix到786逐frame同一；787起确由本地模型且原parser合法，前置guard阻断任何云客户端。native续跑是同接口／同原seed的恢复对照，首次请求应与原call77一致；重复采样和调度变化如实记录。
- **噪声地板 + MIE：** 单自然发现性case，不估总体CI，不设科学bar。初次对照检验普通信息解释，未跨角色／场景验证就不注册一般claim。source请求的原采样seed按前77calls继续，分支以后调用数量可分化，不能称整条后缀逐随机数配对。
- **混杂审计：** clock是额外state信息，duty是额外本人已存在的责任信息；消息更长，不能归纯措辞。公开lecture没有物理完成flag／结束时刻，不把离开自动记利益失败。沿源schedule和真实位置描述现象；不以一句话恢复为新控制方法。选择3502是已发现异常的case，不能报告为随机总体样本。
- **决策表（跑之前写）：** clock足以改变后续→普通时钟context解释；clock+duty进一步改变→已有责任在信息链中的可见性解释；都没改变→检查合理活动重排、plan／execution，不强行归人格。无material证据只汇报对应层次。任何结果都保留，不自动关idea。
- **算力预算：** CPU完整回放预计秒级；单已空闲GPU载入一次27B，三原生后缀预计20–45分钟，0付费API，既有fgvd/deps。原记录及新raw在cache/runs/e44_*，不入Git。不为填八卡铺开无关矩阵。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
CPU完成：3502完整1200frames逐frame同一，4.94秒；787frames精确prefix同一，2.32秒、77录制responses，首次新请求与原call77逐消息一致。单空闲GPU0已启动三分支，原3502成功／失败与其他3501/3503正向合作证据共同保留。本卡不是新的论文题目。

接口校对（行为结论前）：原call77 structured speak因length截断／JSON不完整返回None，实际邀请来自原call78自由文本fallback。v1只向structured路径添加事实，不能解释为所有实际发言均接受相同事实；停止尚未完成的两个提醒分支，全部raw保留，native完整后缀仍有效。独立v2统一处理speak与原自由文本fallback，世界／parser／预算不改。用上游真实LLMAgent.converse强制tool=None：三个条件均实际经过call_tool→chat，两路径的事实句一致，native均不加句；0模型/API。资格见E44_original_fallback_fact_qualification.json。v2只重跑clock／clock_and_duty，使用已完成native对照，先精确prefix再GPU。

完整结果：三个valid分支均1200frames，new model calls为native52／clock66／clock+duty64。fresh native与原episode的三人位置、活动文本全部1200frame一致，首次文字差在frame878／相同消息seed的call92；不能称整条随机或文字byte一致。两个v2事实分支各独立零模型重放全部1200frame同一。

实际选择：native教授frame967起走Williams；clock在847开始Irvine的lecture活动，937走Houston ReadingRoom，1079开始同名lecture活动；clock+duty在862..1150执行Irvine lecture活动，1151后走Houston BilliardRoom。相关新承诺、计划与逐人实际活动全部记录E44_natural_context_complete.json。lecture是合法perform活动及地点，不是公开lecture完成flag／物理教学证据，离开亦不自动失败。上下文信息是有实证支持的竞争解释，本实验persona固定，不证明人物因果效应或新机制。E45才对角色指令作局部干预，仍不以普通提醒当创新。
