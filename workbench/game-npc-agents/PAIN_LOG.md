# 本地痛点与意外现象

## P01 · 2026-10-14 · 本地依赖/运行路径恢复（工程痛点，不是科学增量）
ActionCastle首次导入缺prompty/aiofiles：现有Conda fgvd加隔离依赖overlay后CPU闭环8/8通过。PCSP原测试在PettingZoo1.24.3因AgentSelector导入失败；改用1.25.0后重试，原失败日志保留。
Qwen3-32B单GPU权重成功加载61.03 GiB，但vLLM0.23.0/flashinfer采样kernel warmup找不到PATH中的ninja，尚未发生模型推理。需完整Conda激活，或明确使用已有非flashinfer采样器。工程失败不能当“persona行为失败”。版本、log与资产见E07/E08。

## P02 · 2026-10-14 · 作者目标动作与当前地点/执行后果错位（单seed发现性观察）
E07 Qwen3-32B non-thinking、原生pureReAct seed101，20次NPC决策，11/20合法执行，4次NPC动作有material变化；未启script fallback。troll在已经位于Drawbridge时说“return to my post”却执行go west离开，guard离开Courtyard后该处阻挡解除；ghost离开Dungeon后因黑暗连续返回失败（1/9动作成功），其目标性理由没有消失。全部失败保留。
不是已证明persona失效：竞争解释H1为NPC原生观测/动作语法/后果信息不足，H2为地名与自我位置整合或叙事prior导致目标型语言先于当前state；H3为non-thinking/128token/采样的运行模式影响策略；H4为多NPC/未在场全局Game narration与history使目标对象错位。最小下一动作：在同一自然snapshot分别测无历史的当前位置、原版action、一个明确核当前地点的提示和信息等价structured state；先定位，再谈新机制。CPU自动吃鱼事实仍仅为执行归因。

## P03 · 2026-10-14 · 位置probe与原生动作contract不同（E09）
Gemma3-12B在发现性snapshot原版location9/9，却action合法3/9；单句/viewer/neutral能保持location但动作变0/9，raw输出包含不在场target等失败。Qwen32部分位置literal失败是前缀格式而非知识。位置原文、probe格式/语义、动作参数/对象scope必须分开；不能由“模型知道当前位置”或“问卷正确”自动判断execution能力，亦不能强行把位置提示改善称策略改善。下一步先作者per-action descriptions/scoped tool arguments与可靠格式，不加训练。

## P04：独立意图/行动的采样差不能直接当战略差（2026-10-14）
E14修复后首12图seed901均选择并原生执行了作者goal事件（不等于所有抽象利益已达成），但独立intent与action仍常不同；许多是emote/speech等可替代选择。H1：同策略两随机draw/多种等价动作；H2：hypothetical意图问法改变选择分布（已有Rethinking上下文解释）；H3：行动粒度/菜单模板与speech payload/真实效果不一致。E15用A/A抽样噪声与I/A分布、原生fork执行校准，不预设存在gap。

## P06：同一训练目标混合政策塑形与读出学习，需独立控制（2026-10-14）
PCSP已有gradient审计与external trait负结果，均不是我们的发现。源损失同时学η与共享φ，no_consist消融同时移除encoder对齐；检索变化无法单独识别policy变化是否必要。H1：φ改变使策略轨迹更可区分；H2：原policy已经有足够信号，η没学会读取；H3：state/needs机制携带角色信号。E17冻结θ/φ后训练原η，先核原full正控制/held100，若恢复才拆H3；不把这个校准自动当新idea。

## P07：说话与物理行动是否争用一个机会（2026-10-14）
E20完整36episode/70合法原生动作，0speech；其中一次follow长目标、一次examine食物，不能当人格失败。H1：共享资源与原饥饿目标使角色选择直接行动；H2：当前单动作交替task binding让说话占掉争取物品的先手机会，弱化原Dragon先utterance后action的互动机会；H3：对话规范/信息与角色长期动机本来未正交。E21先复用原native事件，提供已由Dragon研究的speech/action分解控制，原物理规则/目标不改；scheduler差异单列，不给因果persona或新颖性结论。

## P08：公开归属语言、目标物品绑定与实际访问（2026-10-14）
E21首seed的p14908 bird公开称worm为幼鸟食物并安全存放，put到公共nests后fox用合法get取走。source短动机自己eat worm，中动机feed young with nut；实际nests是开放公共surface，desc为abandoned。这里只是一个发现性样本，不宣称persona失效或必须自私。H1：合理长目标取舍/威胁信号（Can与Will不同）；H2：角色规范性归属被误当物理权限；H3：自己的公开台词priming/目标object绑定被合并（已有上下文/goal grounding近邻）；H4：抽样/菜单/本地clock解释。I01/E22在同物理/相同菜单快照独立测权限，强普通一句事实/原目标物品提醒作为对照；E21另外两个固定seed继续，不筛选成功put。

E22后：不支持H2；源目标绑定可将放worm9/32降到1/32，事实提醒不恢复该动作。负向权限字段neutral阳性对照失败，联合机制读数降级；不能因其与行动同向就升级。详见I01/E22。

## P09：角色编码的批次上下文混杂（2026-10-14）
E23原500资产500/500高余弦复现，right-padding情况下原脚本末列pool有480行取padding query；同原文编码随批次最长伙伴改变。正确last-nonpad是作者smoke_test和官方已有算法，跨batch变化回到数值地板。E24六原trained政策原生收益受固定padding影响约2–14%，但Full/NoCons没有一致稳健性排序。H1：padding query位置/长度的额外编码信号；H2：旧政策对训练编码分布的正常敏感性；H3：多角色同时变码的动态交互。先建立正确编码训练基线E25，不能把工程缺陷自动升为创新。

## P10：角色数量、单属性覆盖与功能控制不是同一问题（2026-10-14）
E34完整300轮后，Full三个seed的局部C利益方向均强于No，不能讲persona只有proxy；同时整体native return更低、等义相对敏感性更大。E37/39同状态同幅度控制与E40身体反馈／C标注对照提供三种分开的读数。源train400实际上是20种BF组合×20职业；20种非C背景与test5种完全不重叠，原500中没有精确单C配对。线性设计满秩6并未保证非线性条件policy的单属性组合能力。
H1是训练目标／projection的形成路径，H2是单属性干预覆盖不足，H3是目标与身体相关及不同状态机会；不将任一个先判定为真。下一先用普通surface augmentation与C配置干预进行等预算训练，避免一看到差异就设计新loss。干预保持每episode C边际、原body与preferred_actions，评价沿原作者任务／固定读数。

## P11：角色社会互动时，已有责任是否仍进入决策输入（2026-10-14）
源代码事实：E35 seed3502 turn787/call77，教授的原speak消息有warm/precise人设、当前Irvine地点、六条学生相关chat/reflection/observation；没有当前时钟或本人10:00讲座责任。本人原schedule/t0计划已有该责任。对话主动邀请学生去Williams，双方outcome判immediate，revision保留10:00讲座到later；真实frame967起教授离开Irvine。原conversation输入的阶段差异是待解释事实，不自动是科学创新。

我们的解释：角色规范“热情教学”与实际已有责任的关系，可能受组件所见信息影响；不能由友善台词或plan字段 alone 判断执行。竞争解释H1时钟不可见、H2责任检索／显著性、H3合理教学重排或原执行gate。E44在同原生prefix用普通时钟／本人责任一句事实作最小对照，不改规则／角色／gold；成功与负结果均保留。3503学生的错地点计划随后实际恢复共同Irvine活动是正证据，不能沿“gap”故事删去。
