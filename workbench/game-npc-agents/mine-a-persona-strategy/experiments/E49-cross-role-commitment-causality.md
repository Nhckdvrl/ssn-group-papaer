# E49：其他原生角色的新承诺与已有计划，哪些实际改变行动？

- **状态：** DONE；全部24条完整后缀、24条独立1200帧回放及本轮分析完成。
- **类型：** 自由探索／跨角色机制检验，不预定方法或新颖性结论。
- **对应：** P11；E45–48的自然NPC任务选择。
- **问题（一句话）：** 对话角色描述影响任务采纳时，实际后果是否由显式agenda传递；符合承诺的行动是否也可能由已有计划独立产生？
- **竞争解释：** H1非冗余新任务主要由显式修订传递；H2对话记忆、其他trigger或伙伴反馈仍可改变动作；H3描述只改变表达，或教授个例／后缀随机性产生先前差异。原生代码数据流和普通角色条件化本身不是创新。
- **设置：** 复用E35全部三个原episode，新增焦点为Diego Torres和Sofia Ramirez。每个取10:00后第一条该角色structured speak，只按时间／类型选择：Diego 833/877/825，Sofia 909/788/755，种子3501/3502/3503。所有先前历史／世界／其他角色完全原样，后缀至原1200帧。四格为原角色描述／局部描述对照 × 正常／阻止焦点conversation显式计划修订，共6处境×4=24完整后缀。
- **人物干预：** Diego仅`creative, focused`→`conventional, focused`，Sofia仅`wide-eyed, friendly`→`wide-eyed, reserved`；其职业、年龄、好奇／sketch兴趣、历史与执行器／planner人格不改。不是同一心理构念、不是完整人格改变，没有“conventional应做X／reserved应拒绝”的正确行为gold。原描述对照观察是否确实影响自然表达与承诺，不预设成功。
- **信息／协议：** 两角色所有四格均提供本人当前时钟、runtime原plan与schedule执行指针／activity，焦点两路dialogue预算512。其他角色／非对话预算原样。该强普通基线排除此前具体缺信息／截断解释，不能宣称最优提示或实体任务完成。
- **机制干预：** 仅焦点fork以后CONVERSATION原因的maybe_revise_plan返回空PlanRevisionResult；speech、关系与高importance意图memory、伙伴及其他原因修订保留。阻止调用改变后续call-index采样，明确不是整条common-random-number配对。
- **读数：** 每次具体口头提议／接受、source outcome、修改前后agenda／cursor、被阻止事件、全部角色逐帧x/y与活动、合法parser与material delta、完整成本及错误。先按原计划核查承诺是否新增地点／任务或与原计划兼容，不自动从文本相似度判冗余，也不把activity文字或计划状态当物理完成。Persona Expression用原始自然台词审阅，Contextual Intention用具体承诺，Executed Behavior用真实动作／世界后果；未做心理量表效度。
- **阳性对照：** 六处境prefix逐帧、source第一请求逐字相同；真实LLMAgent.converse强制tool失败，确认两路角色／进度／512均暴露，其他actor不变；block上游真实apply_conversation_outcome确认关系和PLANmemory保留、agenda不改；非target／其他原因委托原函数；独立完整cassette重放带同窄干预。资格只防实现错误。
- **噪声地板 + MIE：** E45三原输入重复已经显示一个episode有后缀变异。三固定历史／两个源角色共享同世界与同27B，不估人格人口CI、不设MIE或比例bar；全部条件和失败保留。需要新的随机重复或模型时按实际疑点追加，不挑最佳seed。
- **混杂审计：** 不同角色的描述对照不能混成统一trait效应；旧历史与执行人格保持original，测conversation组件条件作用。对话互相影响、运行后种子索引分化、长输出内容／done、agenda自带目的地均要分开解释。原任务／地图／物理规则／评价不改，迟于episode结束的承诺不记失败。
- **决策表（跑之前写）：** 两新角色也有可核对的显式计划渠道→整理跨角色可预测条件并与已有工作定位；行为仍变→追踪记忆／伙伴／其他trigger；仅表达变→保留行为稳定结果；与原agenda相同的出行不能单凭承诺符合性记作因果。无统一方向也不淘汰研究线；普通解释足够时承认，下一实验按未解释轨迹决定。
- **算力预算：** 先CPU全部prefix与两路真实资格，再八个独立worker（2actor×2描述×2渠道）各串行三处境、同一已载入模型复用。GPU21/20各四卡须逐卡再查空闲，≤8，无跨节点同步；fgvd/deps/cache，全本地0API。按E48实测每完整后缀约270秒加一次载入，预计合计约2GPU小时，实际token与wall另记。raw runs/e49_*不进Git。

## 结果
尚未运行。此实验为跨角色认识提供证据，不将普通角色／计划数据流命名为新贡献。

上句为运行前记录。最终：八worker均完成三个处境并复用一个模型，24×1200帧／1173新调用／8852新后缀帧；独立同窄干预零模型回放全24条一致，完整结果 `E49_complete_cross_role_commitments.json`，证明 `E49_all_24_independent_replay.json`。根级parser后缀146/147合法（所有角色），全部129次结构化解析失败保留；焦点speak83+58次零失败，不能外推所有组件已无协议问题。三自然历史共享，同一27B，不报人口CI或“成功比例”科学bar。

Diego3501/3503的正常角色描述改变路线，阻止显式修订后留Irvine；3502两描述路线相同，阻止修订将Williams出发967→1193，原agenda下一处为Meyerson，意图仍可能驱动目的地。Sofia3501本人位置相同而活动／计划文字及伙伴行程可变；3502正常original去Williams、contrast留Irvine，阻止后两者都留；3503两描述分别去Kamin／Moelis，即使焦点修订被阻止也如此。实际844帧travel输入含对应PLAN承诺记忆，原agenda仍指向Houston，故显式agenda不是唯一入口，但不能由此量化所有中介。人物局部指令与后续采样／伙伴仍需区分，未提出新方法或升级C01。

记录的模型载入3040.95秒＋分支wall13811.95秒，合计约4.68GPU·小时，未完整包含初始化／退出间隙；高于原2小时粗估。按用户最新要求，本轮分析归档后暂停，不追加推理／训练；全局workbench与idea状态不关闭。

解析失败归因核对：129次为19次非焦点speak、110次score_memories；焦点speak141次均0，焦点score_memories仍29次失败。outcome trace温度0.0与source默认一致。新计划内容、伙伴fallback、importance缺失和后续随机索引均保留解释限制；不把一个组件资格推成全agent无混杂。

CPU资格v1：Sofia全部四格×三处境通过；Diego在3501同一833帧的首个原决策调用早于目标speak，单用frame切换后缀导致请求计数断言失败，未产生GPU测量。raw与v1脚本保留，不作为科学零效应。独立v2以原response计数继续重放该帧中目标以前的请求，再在指定speak切入；全部24个CPU条件重新核对，实验处境／干预／读数未变。

全部v2 CPU资格已通过，见 `results/E49_all_cpu_qualification.json`：24个精确prefix／首次source请求、目标两路512／角色句／真实进度、非目标两路原128不改、block原生outcome记忆保留与agenda不改。固定script hash后运行GPU；八卡刚确认空闲，既有fgvd环境和缓存，0API。
