# 2026-10-14 源码、数据与执行审计

范围：E07/E08；pin、PDF SHA和clone路径在 [`E08_sources.json`](../../results/E08_sources.json)。Fact / Interpretation / Alternative分开。作者结果仍属作者；本地CPU路径复算不等于论文模型复现。

## PCSP：persona 到策略的真实路径

**源代码事实**（`pcsp@5420f7b`，路径均相对research/）：

- `src/models/film.py`：离线冻结Qwen3 embedding输入→1024→rank16→64的低秩线性投影并normalize；不是在语言模型本体上训练LoRA。投影供共享actor/critic使用；FiLM初始gamma=1/beta=0。
- `src/training/pcsp_trainer.py`：`collect_rollout`用no_grad采样离散动作，保存numpy obs/action；InfoNCE用GRU编码保存轨迹，与共享persona projection做in-batch diagonal cross entropy。没有通过离散环境rollout直接反传到actor，可能通过共享projection间接影响后续策略。
- PPO直接更新projection/actor/critic，diversity在同一批状态比较不同persona的action logits KL，直接更新projection/actor。两者都不直接更新trajectory encoder。
- **作者自己的**`test_gradient_paths.py`已核这一拓扑；我们执行通过且数值见E08。作者还提供trained-checkpoint audit脚本；本轮没有重跑它，所以不能将小fixture范数写成训练期结论。
- `src/env/mini_inzoi_v3.py`：needs补充/低need惩罚、preferred_action +.5、BigFive/action-style cosine ×.3、social bonus共同进reward。`build_personas_v3.py`把v1动作按C/E/O等级展开为v3偏好，300/300源码映射匹配，人物文本未改。
- `src/env/mini_inzoi.py`的当前v1实现也有preferred_action +.5和按BigFive相容性的social bonus。**“没有v3 style term”不能写成“完全persona-agnostic reward”。** 最新论文§IV说v1/v2 base只有needs-driven/persona-agnostic social shaping；历史训练源码/reward版本与当前commit是否一致尚未排除，不据此宣判论文错误。

**评价与独立性事实**：

| 数据口径 | train/test | ID/完全相同文本交集 | 职业交集 | BigFive联合原型交集 | 解释范围 |
|---|---:|---:|---:|---:|---|
| 300 v3 unseen-occupation | 240/60 | 0/0 | 0 | 15 | 组合式新职业；人物原型都见过 |
| 500 v3-large | 400/100 | 0/0 | 20 | 0（test5种） | 新联合特质原型；不是新职业 |
| unseen-archetype | 240/60 | 0/0 | 20 | 0（test3种） | 另一个作者划分 |
| unseen-combo | 240/60 | 0/0 | 18 | 15 | 两轴本身均已见，组合未见 |

`run_independent_behavior_eval_v3_large.py`：政策训练400角色，独立probe用其中320拟合/80校准，最终100角色测试；同一probe在两policy混合训练，按persona簇bootstrap/randomization，3policy seed配对。445维动作统计/749维含state，独立feature模块不读学得的projection/trajectory encoder。作者报告full .482 vs no_consist .511，含state .556 vs .558，不能冒领其发现；0.33也不能无视未见联合原型的标签支持度当万能chance。

**我们的解释**：InfoNCE内部可恢复性不是独立特质行为效度；但projection间接作用和MeltingPot/UE5证据不可删掉。最新论文已有三层stack、无consistency消融、自然语言共享政策扩展。只审v3奖励不足以关闭PCSP认识。

**尚未排除的竞争解释/阅读债**：作者独立评估的BigFive构念、组合OOD与任务机会分布都影响probe；内部分类decoder共训练与真实策略改变可能并存。需原weights/trajectory重算或外部任务评价后才能论方法效果。UE5与MeltingPot未安装/未复现；我们不声称它们失败。

## agent-sandbox：Action Castle 的原生执行范围

**源代码事实**（`d7b872e`）：

- `notebooks/hw1_llm/play.py`复用原Action Castle，给troll/guard/ghost附加作者目标；pure `make_react_behavior`没有script fallback。网页demo的`make_hybrid_behavior`则失败后可script兜底，两者不能混计。
- `npc.py`：persona第一次写入agent后缓存；goals每turn重读；系统消息含persona/goals，用户观测来自`game.describe_for`+地点归因的recent history+heard+private memory。free-text默认128token/.7 temperature；工具路径与free-text路径均重新进parser。
- `decide_and_route`首选失败后把真实失败原因附回base观测，默认1次retry；失败反思与可选周期Reflect是两件事。script fallback、memory retrieval、可选periodic reflection的贡献必须分别记。
- `parsing.py`先解析action，再检查preconditions和apply_effects；world_state可读出物品/人物/退出阻挡/事件。导出为omniscient，仅用于审计，不作为NPC观测。
- 原troll persona含临时事实“I am hungry”与未来承诺，作者目标为阻止intruders。guard怀疑陌生人并藏castle secrets；ghost被guard谋杀。不是我们把抽象人设贴成唯一gold。
- `Give.apply_effects`收到食物的hungry recipient会自动Eat；Troll_Block由hungry/位置/生死/意识判定。CPU控制8/8通过：growl成功无material delta，club attack改变玩家state，无武器攻击失败，递鱼自动吃鱼解桥。

**我们的解释**：人物设定、目标、局部信息、LLM原始选择和engine结果可拆；“NPC让玩家过桥”的世界读数可能完全由玩家give+engine决定。规则与脚本是正常工程设计，科学问题是归因/解释范围，不是代码有硬编码就创新。

**尚未排除的竞争解释/阅读债**：角色goal与当前短期利益的合理优先级、多种等价战术、模板128token/合法动词和具体语法知识、state是否被观测表达、cache persona与memory对当前state一致性；需本地强模型轨迹，不能由CPU接口检查下人格科学结论。

## E12–E14执行后的补充范围
**事实：** agent-sandbox首选call_tools→逐动作tools_for→同线程tool_result重试。原ActionCastle动作多数没有ARGUMENTS_SCHEMA，实际退回generic arguments字符串，因此有call_tools不等于获得合法target/direction闭集。parser逗号sequence递归导致raw记录多于模型root选择；E10/E12重建root 0missing，POST-HOC独立文件保留。普通强提示使E12首次合法48/133→92/135。
**解释：** 原弱默认/接口错误不能作为人格机制证据；合法性改善不等于策略改善，低material也可为合理等待。
**竞争解释：** 材料影响仍可能来自native feed/blocks；角色离岗有合理巡逻/输入视角/动作预算解释。

**LIGHT事实：** 官方7486 quest中1787不同graph，1446相同graph具有多角色独立quest，共7034条；与2111human demos严格名字/同图join得到692条bot自身作者目标。E14固定源顺序前12不同graph不按model表现筛；初始goal合法10/12（另2有物品前置），原possible_actions707canonical中25无法经原parser重parse，多数是examine/point self。物理事件/概率/原WorldViewer未改；最小host未加载原学习Soul/OnEventSoul交易攻击脚本/DM，故只声称新的本地NPC任务绑定，不是官方partner完整复现。
**解释与竞争解释：** private authored motivation可以分开NPC与player利益，不保证全部抽象动机存在可执行终点。候选菜单暴露scope和对手物品沿原协议，不能当完全无信息的观测；合法动作执行可能随机失败/无材料delta。首2条tell payload遗漏是我们的adapter错误，通信降级后修复并按原样本全量重跑。

## PCSP E17–E19观测单位与读出控制
**源代码事实：** consistency._rollout_persona 将同persona复制给全部16个v3-large actor，AEC遍历时将所有actor obs/actions顺序append到一个列表；_encode_trajectories截前200帧，所以当前约12.5世界cycle。原trainer collect_rollout则分别按actor存200-time-step trajectories并给各自的e_llm。Mixed-persona采样确在train sampler随机选择，不应误写为训练只见同类population。根results/embeddings/有500原Qwen f16编码（先前只查看research子树导致误以为未公开，现已修正）。
**本地控制：** all-A自写循环与作者helper逐byte相同；混合角色时joint解码更近群体、own更近自身，角色自己的rest偏好仍随自身code。θ/φ全冻结的η训练使同100候选角色ID解码1%→3.7%，full6.7%；conditional-policy likelihood21%/27%（full/no_consist）。所有world/政策原样，η不同不改变native后果。
**解释：** persona输入确实可影响实际策略；差读出不能单独作“政策缺人格/没有身份信息”证据。但likelihood使用生成policy，不是独立人格语义效度；作者BigFive独立probe负结果是作者ownership，不冒领。
**尚未排除：** 时间跨度/混合actor单位差、φ几何与η拟合预算、utility/body/state或伙伴信息、个人ID与trait原型粒度。需要更多公开policy seed及state-conditioned控制；当前不是新科学主张。

**三seed补充：** E17冻结政策仅校准η的top1=3.67/4.67/4.67%；E19条件似然full=21.00/36.33/20.33%、no_consist=27.00/25.00/26.33%。同100ID配对Full−NoConsist−0.22pp [−5.67,5.44]，没有一致排序反转。原η低解码不能单独推出政策persona-agnostic；与作者独立语义trait结论仍分开。具体结果E19_three_policy_aggregate.json，CI条件在三固定trained policies而非训练总体。

## LIGHT dialogue与物品访问：新增源事实
**源代码事实：** Dragon base/environments/envs.py step按initiator utterance、partner utterance、partner act顺序；partner的act输入含它自己刚说的话。E20的单事件轮换是明确本地task binding，不是这个原RL流程。E21只恢复speech/action机会分解，仍未加载原RL/Soul。
**本地事实：** E20 36episodes/70合法动作/0speech；E21独立原人物对话后出现put物品。source14908短动机worm自用、中动机nut给幼鸟，nests对象位于公共room、开放surface、没有locked_edge；狐狸随后原get取得worm。WorldViewer物品列表/背包使用set迭代，跨Python hash seed顺序不同；E22先核state及view内容一致，再复用原缓存native view/原schema保证同prompt，不把显示顺序差当模型状态错误。
**解释/未排除：** 公开台词本身是社会行为；合理照顾幼鸟或害怕对方不是人格错误。权限Can、对手Will、角色价值与自我台词priming需独立。一个source goal event未执行不等于抽象利益失败。source物品绑定合并与普通grounding近邻仍可解释观察，尚无新科学主张。

## PCSP 编码资产资格与原生后果（E23/E24）
**源代码事实：** research/scripts/compute_embeddings_500.py（SHA5d858bca9dd8f6d4084b0e60adda450cc1311118fb33703e76b740699cd0ac14）fp16/max128/batch32/sortedID，无instruction，直接last_hidden_state[:,-1]。同仓smoke_test已有attention-mask-aware last-nonpad helper。官方Qwen3-Embedding说明也支持left padding或取最后真实token。默认运行tokenizer实际right padding，不能只凭源码中没显式padding_side就断言历史runtime。
**本地资产事实：** E23全部500公开.npy高余弦复现（最小.9999883），480行末列为padding位置；同原文编码随最长伙伴变化，正确pool跨batch降至数值地板。E24保持原人物/body/奖励/初始世界，fixed128使六公开策略原生收益约降2–14%。普通正确pool已解决编码批次依赖，没有Full/NoCons一致稳健性排序。
**解释：** 当前公开数组与此原recipe高度一致，部署时同人物编码上下文影响原生行为后果；这是资产审计与工程资格，不是科学创新。
**未排除：** historical模型revision/runtime仍未由作者pin，当前公开数组不自动代表论文全部分支；旧policy输入分布改变是正常OOD效应。E24全部角色同时变码含population交互，需单focal/共同状态才分直接效应。重新训正确pool基线E25另存，不覆盖作者资产。

## PCSP 更强的已有结果：MeltingPot PHASE5
**作者公开事实（非我们复现）：** pin5420f7b的research/meltingpot/PHASE5_REPORT.md，已读§1–5、§9–12。先将random32换Qwen语义编码，full12候选heldout top1仍0；§9查明原full candidate heldout仅作负类，将pool缩到train10仍未恢复。§10 PD substrate增加行为KL但读出仍差；§11平衡persona trajectory采样+train pool首次非零但seed双峰；§12各substrate8seed，commons_harvest top1 .364[.192,.554]、top3 .480[.257,.696]，PD阳性basin2/8，spinner始终难读，且ID top3降到chance。作者明确提出projection geometry/embedding-margin与ID/OOD tradeoff，并推荐joint loss/controlled margin/persona arithmetic。
**解释：** “policy有信号而encoder读不出”、contrast pool与projection几何、简单balanced sampling修复均已有owner。不能拿该报告前半的0结果代表作者最终全证据，也不能把后半设想直接拿来重包装成我们的idea。
**未排除：** 报告属于public研究记录，不等于每一结论都进入最新论文主张；CNN trained assets/对应seed真实runtime未本地核验。MeltingPot/dmlab2d未安装，报告数字必须标作者。v3-large与CNN分支loss/编码recipe不同，不用E23替其他分支判错。

## 正确编码后独立训练与行为归因（E25–E28）
**源代码事实：** consistency的直接路径为共享φ和η，PPO/div分别保留原路径；原consistency不直接反传actor/critic。已有作者内部/独立行为评价和PHASE5 projection讨论。
**本地事实：** E25正确last-nonpad、固定全部RNG、同初值、同完整rollout，三个路由各30iter/768000原生transitions。η-only训练与NoCons的策略和native行为逐byte同一，检索却1%→5%；Full检索8.667%，utility差−1.7812[−4.0146,.5271]。E26等词/事实重排影响两类策略；E27原body固定时constant code显著降低action-only读出，真实code控制与state生理信息并存。E28实际四次辅助步、train-only对齐、小于预定MIE的utility变化及负CI保留。
**解释：** 读出改善与策略改变必须单列；输入、body、读出器、训练路由是不同因果位置。普通正确pool、已知语言绑定和PPG/Procrustes不能冒领原创。
**未排除：** E25只有一个训练seed且30iter不是完整收敛复现；E26/27全population变码含伙伴作用；固定policy下persona簇CI不是跨训练seed不确定性。不会用这些限制倒推支持所需结论，也不直接扩大训练。

## 原生成式NPC物理闭环及计划来源（E29）
**源代码事实：** 同pin agent-sandbox/godot-generative-agents：planner.generate为persona+memory→day→hour→minute stops；原MockPlanner重放authored schedule。decide由本地接入模型选原工具，perform只设activity；make原Recipe要求持有pot且stove on，再创建boiled water；drink改portions/生理及safe/raw counters。对话后原conversation_outcome按persona分类plans_changed/commitment/timing，写入locked PLAN memory，再调用planner.revise；只替未执行tail，immediate允许清下一stop未来clock gate。这些已由作者实现/测试，不是本轮创新。
**本地事实：** E29原CPU16/16；单Qwen27B episode原工具6calls/5合法，安全水首次饮用。初perform声称boiling但材料不变，缺锅make被拒，后get/activate/make/drink才产生真实后果。MockPlanner/无reflector/embedding/importance scorer；真实工具只有decide。原failure字段stale与adapter不记上游UsageLedger均注明。
**解释：** 人物表达、活动描述、可执行计划和最终物理后果需要按各自来源判定；此episode说明原生闭环可行，并非“言行不一致”新证据。
**未排除：** 没有还原LLMPlanner/对话outcome/reflector完整链，不能据此判断原完整系统角色目标控制。memory/boil、能力wish及异步deadline原作者已有实验；不重复制造相同结果。
