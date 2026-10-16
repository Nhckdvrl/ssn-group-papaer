# E83：有自身目的的NPC，真实收件与奖励兑现的原生基线（2026-10-16）

- **状态：** DONE（CPU原生见证、两条完整本地模型episode、两份独立物理读回均完成）。
- **类型：** REPRO / D1普通强基线；论文角色任务的明确重建，不申领方法/机制或微软原系统复现。
- **对应：** I04 / P12；状态、C06等级均不变。
- **问题（一句话）：** 在具有自己找回珍贵物品目的、明确角色边界和条件奖励的NPC中，普通本地LLM＋真实状态/技能能否区分玩家声称履约与实际交付，并兑现自己决定的合作？
- **动机与来源：** Microsoft《Collaborative Quest Completion》完整角色/附录与21份公开真人日志：有成功兑现、提前索要奖励、交还后争议和保留自己的珍贵剑等实际互动。E81的自然条件多缺物理实现，E82已提供Minecraft真实交接/制作底座。本卡先做一完整NPC决策阶段的能力驻留，不再把两份互补原子动作自动叫合作，也不为了N造200个剧情或发明方法。
- **重建边界：** 官方无原世界/运行器；使用现有Minecraft1.21.1/Mineflayer/作者skills，明确重建Alaric收到玩家归还剑前后的island决策切片，非整段搭路/战斗营救任务。原paper persona、找回diamond_sword与和解目的、留岛限制、diamond_sword交还后才给netherite奖励的角色条件保留；和解不伪造原生flag。岛台/箱子坐标、未注明物品数量是公开fixture参数；不宣称原作者地图或28人实验复现。只改任务初始化，不改游戏配方/交付规则/物理引擎。
- **设置：** CPU先在同一原Forest副本建小岛/箱子，Alaric持原paper iron_sword、sticks、netherite_sword；玩家通过真实开箱取得diamond_sword后切入，不能脚本直接向NPC发物。单NPC＋规则玩家（非语义裁判），8个NPC机会/episode、每次普通真实说话＋至多一原生动作；保留完整角色身份/目的、自己库存、真实可见交互/技能结果，玩家私有库存不直接泄露给NPC。场景/driver/工具SHA在首模型前冻结。CPU和首次模型episode先各完成再看成本，不按成功率删场景。
- **固定玩家行为（首模型前）：** 两条行为路径，非两个独立世界。P0普通合作：请求确认条件，第二个NPC机会后实际交还diamond_sword并索取承诺奖励。P1条件改变：先要求提前给奖励；第二机会后只声称已给剑、实际不转移；第四机会后真实交还再索要奖励；第六机会后请求借回diamond_sword。所有物理动作和机会记录；若材料已经改变，记录实际结果，不后台补物/强制形成相同终态。规则玩家只做这些实际动作和正常拾取，不替NPC接受条件或发奖励。
- **模型阶段（首模型前原登记）：** 待CPU通过后追加确定启动配置；预定现有Qwen3-32B BF16非thinking、现有Conda fgvd、localhost vLLM、温度.7/seed8321/输出512/context8192，最多上述2完整episode。0云/付费API、无默认SDK回退、无模型思考/标注调用。无人物提示变体或层/seed网格。
- **读数：** 原生逐物品库存/掉落实体/拾取事件；玩家从箱取得、NPC实际收到diamond、netherite离开NPC与玩家实际收到分别计；实际收到前奖励释放；收到后的NPC选择与自身珍贵剑最终归属；真实speech、声明、动作返回与世界状态；角色位置/错误/耗时。原动作选择不等于最终接收，helper返回true也不等于接收。归还/借回可有合理角色取舍，不预定其唯一正确选择。两条路径不估计总体比例或因果机制。
- **阳性对照：** 原native开箱→丢出→拾取→NPC奖励丢出→玩家拾取可完成且库存守恒；CPU只见证可能路径，不称NPC决策。没有奖励自动门或验证器替NPC选择；NPC可说话、拒绝、询问、使用/移动/交出自己已有资产。
- **噪声地板 + MIE：** 单任务两路径是完整episode成本/能力检查，不设科研通过bar、显著性或普适结论。先看强普通系统能做到什么；新的值得研究失败须从这些和更多真实合作任务中寻找，不能围本角色改几句提示刷成功。
- **混杂审计：** 明确原任务重建范围、原角色条件与新增普通接口；不继承MINDcraft“不要拒绝请求”的通用helper身份，不启会替NPC狩猎/决策的自主mode，不把脚本玩家算真人体验。服务只允许localhost；初始化控制与模型工具分开，模型不能调用/give等管理员命令。既有E82高层Give helper限制保留，以原native Drop/Pickup及实际库存为普通可靠技能依据，不修作者源码或发明新协议。若出现执行失败，先报告真实接口/能力，之后仅必要的一句普通对照再谈机制。
- **决策表（跑之前写）：** 普通系统可靠辨认/兑现→记录其已解决范围，转向真正影响合作可达性的不同玩家方案/条件；言语声称与实际不符→先核真正的工具执行与最新可见状态，再选信息对照；角色主动拒绝/协商→按自身目的/角色边界解释，不当“不合作失败”；源任务/fixture没有承载关键后果→如实调整任务来源，不围它堆网格。不预定方法或论文主张。
- **算力预算：** CPU单服务器2GB堆＋两角色；首次本地模型≤1卡，预估含载入0.3GPUh，现场总≤8。**实际：** 16次本地调用；模型server载入至SIGTERM占用0.34283 GPUh，至确认释放的保守槽时上界0.35650 GPUh，包含载入/CPU等待/空闲；模型请求60.258秒，episode driver含server启动157.433秒。峰值1卡、0云/付费API；Java、本地模型服务均已退出。

## 完成结果（2026-10-16）

**两条路径最后都完成实物交换，但均在NPC实际收到钻石剑前发出奖励；随后仍多次尝试发放已交出的奖励。P1同时保留了依据自身目的拒绝借剑的能力。** 最终库存、按条件履约、及时更新自己的合作判断是不同读数；只有最终物品归属会掩盖本轮最有信息的行为。

| 固定玩家路径 | 原生事实与NPC选择 |
|---|---|
| P0：正常合作，第2机会后真正交还 | 第1机会NPC已Drop netherite，玩家确实拾取；第2机会后玩家才Drop diamond，第3机会前后NPC真正收到。第4机会再次Drop已不存在的reward被原技能拒绝，之后称要寻找自己已经交出去的奖励。最后NPC持diamond、玩家持netherite。 |
| P1：预付请求→仅声称交还→真正交还→借回 | 第1机会NPC明确拒绝提前奖励；第2机会后玩家只说已归还、实际仍持diamond，第3机会NPC即真实Drop奖励且玩家拾得。第4机会后玩家才真正Drop diamond，第5机会期间vanilla碰撞拾取进入NPC库存。第7机会NPC以自身珍贵剑/Elena目的拒借，第8机会又试图发已交reward。最后归属同P0。 |

16次输入、16个真实模型决策全保留，0 JSON协议失败。3次重复Drop返回false均为reward已不在NPC库存。P1说“take iron sword”时实际选的是自己Equip/GoToPlayer，未交铁剑；不能把这些台词计交付。钻石拾取可由vanilla碰撞在推理期间完成；P0 Pickup返回“0 items”但真实收件存在，不把该helper文本当唯一物理真值。最终保留diamond及拒借符合原角色可选择范围，和Elena和解没有独立完成flag，本轮不伪造其完成。

**观察核验。** 两份独立CPU读回覆盖57份snapshot/55个post-cut独特状态，两把剑各守恒1；4个剑实体的spawn、item/count metadata和真实collector闭合。16份实际输入中的自己库存、位置、health/food、真实speech/pickup历史及上次技能结果与trace一致；无玩家私有库存泄漏、无cut后管理员动作。两次初始化`PartialReadError`原样保留；没有观察到它们破坏本轮所使用的剑归属、收件或对话字段，不将整个runtime写成无错误。

**研究判断。** 普通角色+状态+原技能已经可以真实交换，也可以拒绝不合自身目的的要求；本轮还暴露出把对方陈述当已履约、重复执行已经结清的交换的线索。它值得在异质原任务、不同玩家真实行动和普通剩余目标/状态基线中检验，不能由单角色两路径宣布普遍人格失效或内部机制。接下来E84回到完整7486作者quests/1787图寻找原世界支持的双向前提与替代合作，避免围Alaric调提示；I04 PROMISING / C06限定L2不变，正文暂缓。

结果：`results/E83_qwen_complete.json`含16轮动作/发言与真实库存变化，`E83_episode_review.json`和`E83_physical_readback.json`独立核对，`E83_native_check.json`/`E83_cpu_independent_review.json`为首模型前CPU见证；完整raw在`/home/xiang/.cache/game-npc-research/runs/e83_qwen_complete/`，含逐请求输入、输出、原生事件与server日志。模型启动/退出账本为cache/runs/e83_qwen_server_{launch,stop}.json。18390输入/1174输出tokens，16次本地请求、0云/Step/付费调用。

### 首请求前执行配置（2026-10-16追加）

现有Qwen3-32B BF16，vLLM0.23原生localhost服务127.0.0.1:58083，model alias `e83-qwen3-32b`；8192 context、max_num_seqs8、GPU memory .86、eager。客户端明确enable_thinking=false、温度.7、seed8321、max_tokens512、JSON schema约束。允许CPU场景资格与本地模型**载入**并行，CPU见证和两路径输入/hash冻结通过前不发任何模型请求。仅使用fvcrc21已释放空闲GPU0，其他E81分片不触碰；新增loader时间全计成本。

### 首模型前冻结与CPU完成（2026-10-16）

原生CPU v4与独立复核均PASS：真正的开箱、可见speech、假声称无物理转移、钻石剑由NPC实际收到、Netherite由玩家实际收到，两剑各守恒1；全部由原生动作/事件与库存见证。脚本`229f82bf6fe09e0f862607d2017371e139d65e3cb089761798c1fcecde02755f`，scene文件`07c7d5dd5d5638cd96ff00191bafeb0570412598d00fad988f1ee9a2962f3b23`，role/schema文件`433866ecef65bad07b3f3b66ce18e9cb5c9487c745eb893976de9fbdda0cd8cf`。初始dryinput/假声称物理负控不是预知未来模型回复；冻结的是角色、输入builder、schema和固定玩家路径，动态完整输入逐请求保存。

此前CPU三次失败均0推理，完整保留。额外收窄作者Mineflayer范围导致旧client与新transitive protocol/data不兼容，曾漏chat与掉落实体；恢复作者原semver后MF4.39/protocol1.68/data3.117通过，无协议/引擎/奖励规则patch。旧E82 exact环境与结果保留，新prefix/lock SHA `a950057b2f683c7caca7ed2a25f3291593fd93da1bbddd1da8736e48fb946b18`。CPU成功39.001秒，单次模型尚未发生。见`results/E83_native_check.json`、`E83_cpu_independent_review.json`。

现在按固定P0/P1、每路径8NPC机会发首请求，Qwen3-32B实际参数如上；不追加条件或seed，全部协议/原生失败保留。模型server载入与CPU并行时间计入实际成本，不将CPU修接口当模型失败或科学发现。
