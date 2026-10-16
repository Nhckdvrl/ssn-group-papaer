# 合作提案、实际履约与条件变化：任务资产及强基线核读

2026-10-16；推进I04/C06/P12的后续研究对象判断。仅主源检索、正文/关键附录及作者代码只读，0推理API/GPU/新实验；不改状态，不预定方法。先读已有GAIA、Dragon、CoopEval、PUBG/FACUL、MineNPC、SidConArena、MMOAgent等卡，以下补直接协议和可取得资产，不重复泛泛定位。

## 1. 能直接改变下一步动作的判断

**下一能力对象应是：角色围绕自身目的形成可执行的条件合作方案，并根据玩家真正履约、未履约或条件改变继续行动。** 它不同于把同一源物索要局增加话轮；E80已显示仅恢复会说话/Steal的玩家并不自动产生足量的不同资产协商。下列强近邻已分别覆盖有界承诺执行、条件履约、重复修复和真正游戏协作。应直接继承其可靠执行与评价，不把“LLM会谈判/承诺接技能/双方有目标”当新发现，也不以这些组件已有就判整个NPC问题无价值。

| 主源 | 已确认的有效协议 | 实际可取得资产；不是已运行声明 |
|---|---|---|
| [Talk is Cheap, Communication is Hard](https://arxiv.org/html/2605.01750)（2026预印本，正文自述under review） | 私有项目＋每轮协商后分别提交资源/项目，程序判越额及收益；重复遭遇和项目变化 | [官方trace explorer](https://devyaoyh.github.io/a2a-negotiation/)实际可HTTP读取（HTML含数据），正文AppH列主实验run IDs和live runner；未确认公开backend仓库，不启动托管runner/云模型 |
| [GenCoord v3](https://arxiv.org/html/2608.22055)（2026-10-09预印本） | 自己路径＋请求对方续作；验证交接后激活义务，规则反馈可触发改分工 | [作者仓库](https://github.com/JulianZJN/GenCoord)是论文及紧凑证据数据，README/文件树已核；没有完整Minecraft运行器，不能称可直接复现系统 |
| [Evaluating Rational Contracting / ContractSim](https://arxiv.org/pdf/2608.10475)（2026-08预印本） | 协商合同后11期实际付款/采购/生产；可比较遵约、被剥削、合理停止 | 完整附录prompt、受限合同语言和动态规划基线说明可读；未找到可确认作者源码入口，不能称现成可运行环境；**协议后禁止通信/重谈** |
| [Collaborative Quest Completion](https://arxiv.org/html/2407.03460)（ACL 2024 Wordplay，官方README自述） | 原角色要营救/找回剑，玩家可帮忙、反问奖励；NPC接矿采、跟随、丢物等游戏API | **本轮已取得[官方仓库](https://github.com/microsoft/collaborative-quest-completion)的21份真实玩家文本日志**，另有录像链接；不含游戏运行器/世界存档/完整工具源码。全公开日志核读见§6 |
| [MINDcraft / MineCollab](https://arxiv.org/html/2504.17950)（2025；本次未核正式接收身份） | 真实Minecraft多角色分持资源/配方，通过说话、Give、Craft完成物理任务 | [现成作者代码](https://github.com/mindcraft-bots/mindcraft)含任务、技能、库存判定和本地vLLM入口；需要Minecraft服务器/Node及本地模型配置，本轮未安装/跑通，不能称目前本机已就绪 |

**马上可用的仍是现有LIGHT动作闭环。** 它能执行已有物品交接/返还、使用、移动等，已有普通本地模型＋状态/错误反馈＋合法技能基线。要改变的是原任务与玩家行为分布：找本来有具体可执行条件和替代余地的原作者任务，保留双方资产、权限和动机；不是重新封装索要提示。Minecraft是已存在的外部强基线/可选验证资产，不能因论文多就先移植一个平台。

## 2. GenCoord：哪些条件合作已经被强系统做好

**实际阅读：** §3–6、§7 limitations；Supplement S1两个resolver/Algorithms S1–2、S2 grammar与Table S3执行见证、S4信息访问/评价引用表。反馈与接收端对照主要核正文§6.2–6.3，未逐条复算全部S6/S8补充表或独立重训；正文表1–2直接核读。

**源事实。** A/B持有不同任务信息，公开原语与部分任务图支持生成SELF+REQ。路径经兼容/依赖检查后才形成承诺；执行后分别记录交接、已承诺结果及原任务结果。§4.2/S1的ACCEPT/REJECT/COUNTER由**确定性规则**依据peer processing mode给出，不是任意玩家策略。受控revision还要求初始提案等于给定合法初始化。§7明确静态Minecraft、有界双分工/可靠消息，环境改变后的长承诺修订成本未测。

**强比较。** 同字段Short DSL、JSON、controlled free-form的本地质量池都128/128；同一DeepSeek普通dialogue为766/768，DSL768/768。性能差异主要是生成/协调成本，不能忽视普通强对话已经能完成这些有界任务。§6.3接收端固定同一sender输出比较生成与deterministic realization；§6.2正确反馈改变分工和交接物，错误反馈下可履行承诺却不满足原任务。已有“固定目标/请求—可靠执行—独立原任务判定”，我们直接继承。

**资产核验。** 作者仓库tree `cfbac54147b68d2fe54d156395ec9b4a07c049c4`，README/data README及全文件树显示论文、表格/选取证据与分析脚本；不含可启动Mineflayer执行闭环。这里没有把README写法当已审计的runtime源码。

**对我们。** 有界私有任务分工已得到很强完成率，不能先假设一般LLM无法履约。NPC仍需自己判断何时接受/拒绝、提出什么替代，以及玩家真实动作改变情境后怎么办；不能把作者规则counteroffer直接当自由角色取舍。也无需为了区分它而强加新协议或训练。

## 3. ContractSim：履约与被利用已经有精确评价

**实际阅读：** 正文§2.1–4.3、Figure1/Table1–2及prompt guidance比较；Appendix B.2执行/协商scaffold、C.1动态规划/RE近似、C.3合同转译与C.6完整指标。PDF43页，本轮未完整阅读其全部结果附图；原HTML分段浏览不稳定，改读原PDF及本地text。

**源事实。** 客户/供应商分别有私有估值、资金/投入品规则，协商最多50轮。实际履约包含5生产期、6付款期，价格、损耗及库存变化由环境产生；未花的资金、生产成本和得到产品共同进入本人收益。合同支持substitution/deduction/rollover/grim-trigger四类条件，超出支持语言不自动进入solver。执行实验另起fresh agent、使用合成合同、**没有协商历史或协议后的通信/重谈**；不能据此声称已检验完整动态协商修复。

**可继承对照。** Rational Complier在可行约束下最大化自身收益；Rational Conditional Complier先履约，观察对方已违约后停止被利用；Rational Exploiter在实现中近似为全程不付款/不交货，并非所有合同的精确best response。区别无条件遵约、未被违约时遵约、被利用后仍遵约及相互回应，比一条成功率更能解释条件合作。主指标按case先算率再宏平均；原子动作和机会数量不冒充独立任务。

**评价边界。** 合同经Gemini转译成结构化约束，再用solver计算可满足性/福利；这不是纯语义评分，也不是无任何LLM参与的engine-only gold。作者给出较完整转译验证。对我们不需要照搬其付费translator或经济奖励：在可从原生事件确定的条件上检验即可。不能把NPC原子goal擅自当其完整数值效用。

## 4. Talk is Cheap：有自身项目、条件变化及修复的直接协议

**实际阅读：** §3–5.8、Tables2–3/5、Appendix C场景、D完整prompt/phase/反馈、F全透明对照、G标注边界、H资产run IDs、I原轨迹示例。未运行live runner；未取得公开backend源文件，AppD列出的源码函数名不是我们已审计的代码。

**源事实。** 每人私有3个组合项目，以实际购买资源完成；最多5次消息/人后同时提交，超过共享供给全轮为0。4轮中可固定或变化项目，伙伴条件的一方context被重置，不能误说真正换了一个不同模型。资源与预算每轮重置，不是持久物品世界。720局/2,880轮，3模型6配对；配置可解性先经过全部测试模型在全信息单人pass@1筛选，适合隔离协调压力但存在这种选域边界。

**强结果与对照。** 竞争条件下，无对话到有对话的joint efficiency从18.0%到63.2%；强跨模型组合在兼容条件约97.9%。全透明使overdraw下降、efficiency提高，最优率不可靠提高，说明单纯多给信息不是所有问题的修复。正文将judge模式关联与客观收益分开；自我承诺被放弃/初始提案锚定是候选解释，不是其已做内部因果定位。我们不必重做“多轮交谈仍可能偏离协议”的一般发现。

**可复用对象。** 任务本身允许私有目的兼容/冲突、出现条件变化和真实决策反馈，完整phase模板与公开轨迹可以立即用于理解协议/设计普通基线。作为新的本地运行系统，backend未确认，不编造启动命令；也不将公开hosted runner作为零API推理入口。它提示应选择真的需要交换目标信息与调整方案的任务，而非同一物品请求多说几次。

## 5. 自然NPC与现成运行代码：分别继承什么

### 5.1 Microsoft Minecraft协作任务（2024）

读§2–3、Tables2–6与Appendix A.1–A.3完整角色/函数/约束。Alaric有找回钻石剑、与Elena和解的目的；明确要求拿到剑后才能给netherite奖励。Elena因医师身份不能离村，要求玩家救人，能给原有工具帮忙。玩家实际放块、移交物品、提醒处境，存在资源交换谈判；这比仅有共同任务口号更贴近NPC对象。**28玩家中7找到并交还钻石剑**，这是§2.1任务a–g的末项；不能扩大为7人都取得奖励或把Alaric送回村。没有随机对照能把此率归因某一prompt组件。每6轮一次subgoal帮角色回到原目的，但不能直接称已解决全部偏航。

其Table4保留“说已丢剑，玩家仍看见手持”的异常，显示有function feedback仍须读实际世界。原有约束是强普通baseline：保留自身角色职责、明确交换条件、真实库存、动作反馈、定期依实际状态重审剩余目的。继承这些，无需声称首次发明共同承诺。

### 5.2 MINDcraft / MineCollab的代码可执行边界

读正文§3–5/Tables2–3、Appendix7.1完整general prompt、9–10成功/失败协作入口与12动作目录；定向作者源码pin **`f6a9556cf756e6bd88a75cc2fa0d5aed7599b101`**（当前develop，非冒称原论文冻结版本）。读`minecollab.md`、`src/models/vllm.js`、commands actions/queries、tasks/tasks.js库存判定、library/skills.js的Give/Craft实现。

完整现成任务包括资源分持的两人crafting、配方信息分持的Hell’s Kitchen、construction。主文提供47参数工具；当前Give实际靠导航/丢物/等待playerCollect反馈，不能把一次tool文本当最终库存已守恒。tasks.js对Hell’s Kitchen分角色检查目标物，再联合任务完成。原paper general prompt要求不要拒绝请求，故不是有自身私人角色目标NPC的原样强策略；继承动作层与任务资产即可。

源码/作者说明的入口（**未执行**）：`node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs`；两人原任务说明使用`python tasks/evaluation_script.py --task_path tasks/crafting_tasks/test_tasks/2_agent.json --template_profile profiles/tasks/crafting_profile.json --api vllm --url http://127.0.0.1:8000/v1 --model <local_model>`。需先有Minecraft Java server、Node依赖和相应task/profile；当前本文不安装或启动。vllm类本身只向给定本地URL请求，异常返回失败文本，未见改走云模型；检索/embedding等其他配置仍须明确本地，不从README默认OpenAI配置直接启动。

**本轮动作结论。** 现成强系统足以提供可靠动作和双方条件的执行起点；最应优先寻找的是原任务里双方确实有可实行的合作/替代关系，玩家动作真的改变角色下一步应如何做。先运行这样的完整自然任务并看成功/失败，不新增同种索要网格、不先制造一套“修复方法”，也不要求先上人评才承认行为证据。

## 阅读资产与限制

只读缓存沿用`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/`：`contractsim.pdf/.txt`、`minecraft_quest.pdf/.txt`及`mindcraft_*`源码。MINDcraft源码仅定向读取，未全库审计；GenCoord没有冒称拿到未公开runtime。未调用托管game runner、模型API或任何付费服务。文献证据说明已有解决范围与下一任务对象，不构成自动开线/关线/升级判决。

## 6. 官方真实玩家日志：哪些困难真正改变了玩法

### 6.1 资产与完整覆盖范围

2026-10-16只读取得[Microsoft官方仓库](https://github.com/microsoft/collaborative-quest-completion)，pin **`9169b00824f6e58394e822bde5510e1ef081dfae`**；缓存`/home/xiang/.cache/game-npc-research/sources/collaborative-quest-completion/`。完整树只有README、LICENSE、SECURITY及`game-logs/`，**不是公开运行器**。[README](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/README.md)明确关联ACL 2024 Wordplay论文、文本日志及[录像网页](https://msr-emergence.com/watch#collaborative-quest-completion)。本轮未观看录像，未安装server，0模型/API/GPU。

公开日志为**21个玩家文件、3,555行**：912 Chat、92 Goal、182 Item、2,361 Equipped、5 Digging、3其他行。文件为user1/4/6/8/10–20/23–28；论文28人中user2/3/5/7/9/21/22的文本文件未公开在当前tree。覆盖全部21文件的对白、Goal、Item、函数记录；装备行全量检索，重点核Sword时序，重复装备日志不当独立动作/样本。21名玩家也不是21个独立任务世界：他们游玩同一作者任务。

**证据来源分开。** `[Chat]`中的NPC陈述、JSON函数调用文本不证明动作完成；带`Function_Returns`的返回记录强于普通台词，但没有完整调用ID、服务器库存/位置快照，不能独立证明玩家已拿到奖励；`[Item] … picked up`与`[Equipped]`提供已记录的物品拾取/持有观察。玩家报告能说明其实际交互受阻/不满，不能直接替代全世界状态；`[Goal]`是生成的子目标，不是完成flag。论文§3.4结合日志、录像报告28→24集材→18搭路→13找到Alaric→7找回并交还剑；这里不以公开21份的标记数重算作者总体成功率。

### 6.2 影响玩法的证据表

以下相对路径均从官方repo根起；网页链接固定到已读commit。是既有系统的实证资产/应用问题定位，**不是我们新发现或新机制**。

| 具体困难或正向解决范围 | 跨玩家原始记录与证据强度 | 对玩法/原问题的意义 |
|---|---|---|
| 玩家完成对价后，NPC是否认账并真正奖励 | [user11:271](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user11.txt#L271)记录Alaric拾取钻石剑；283/285/290/292/298返回文本称已drop奖励，287/294玩家仍报告未得剑；306将NPC关坑。对照[user13:176](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user13.txt#L176)拾剑→205玩家装备Netherite；[user28:106](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user28.txt#L106)拾剑→112玩家装备Netherite | 有成功交换也有持续奖励争议；玩家付出后的兑现直接影响信任与后续合作。函数成功、从NPC手里丢出、玩家实际得到须分开。论文Table4已讨论此类问题，不另命名新发现 |
| 互补分工能否真正减轻玩家劳动 | [user8:12](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user8.txt#L12)请求NPC采石，20–23转为承认困难/换采木；96/100/103有Elena实际拾木，108–109称交付但无玩家库存证明。user24:46–64持续拾石，78称持29块，80承认给不出去 | “会采到”与“玩家拿到可搭桥材料”不同。应测最终可用支持，不把工具调用/道谢当合作收益 |
| 玩家纠正处境后，合作被改派到无已核实现的子任务 | [user16:149](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user16.txt#L149)起，玩家报告无蜘蛛，NPC先承认退去又坚持存在；177–187改要求收集驱虫剂材料，316–340因找不到材料连续换配方。原Appendix技能不含制作驱虫剂 | 改条件会消耗玩家时间并偏离找回剑目的；不是只研究Give多1pp。玩家“无蜘蛛”报告不能单独证明世界已清空，也未证明所有原料必定不存在；确定的是新增子任务没有已核原生制作接口 |
| 能守住职责，也能在边界内提出支持 | user1:31–32、user4:113–114、user28:8–9拒绝离村；[user24:4](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user24.txt#L4)先拒绝离村采木，再提出本地采石，46–64有拾石事件；user26:155–157拒绝回镇 | AppendixA明确Elena留村且不能战斗，Alaric也暂不能回村。边界拒绝本身是正确角色选择；应问有没有兑现可行替代，而非把不服从玩家一律算失败 |
| 玩家可以改变NPC路线条件，NPC如何恢复 | user8:197–215出现爬坑困难、请求玩家补块、NPC声称爬出后继续往城堡；[user28:125](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user28.txt#L125)以后有follow/goTo文本、玩家多次报告看不见，153有到达返回 | 协作包含玩家修改地形和重新领路，不能预定完整脚本覆盖所有情况。该文本没有完整位置/方块变更记录，不能把一次爬出自述当物理成功gold；录像可进一步核，本文未看 |
| 有自身目的的NPC可以谈条件和保护重要物品 | [user13:3](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/game-logs/user13.txt#L3)拒绝任务后索全库存被条件化；17–25进行奖励议价；127–175要求先归还钻石剑；197–200拒绝再给珍贵钻石剑/全部贵重物 | 已有普通系统能坚持自身目的并形成条件合作，不能预设NPC必然无原则。需要检验新条件/真实履约后是否更新并兑现，而非再证明会说“不” |

**全公开队列的物理交换链。** 只有user8:235、user11:271、user13:176、user28:106四份记录Alaric拾取钻石剑；其中user13:205、user28:112随后记录玩家装备Netherite。user11有明确奖励争议，user8交剑后表示时间已到。这里是全21文本中的可核标记链，**不是**“2/4可靠履约率”：没有完整库存、时间、服务器state，记录覆盖也不完整。

### 6.3 全21文件阅读索引（包括未到交换阶段者）

| source log | 本轮读到的主交互/证据；不自动判定失败 |
|---|---|
| `game-logs/user1.txt` | 2–16威胁/背景追问后仍回到求助；20–23僵尸警告；31–32遵守留村职责 |
| `game-logs/user4.txt` | 48–57/76–106玩家反复纠正Alaric位置/蜘蛛，跟随多为自述；111玩家报告NPC在岛下坑中；114 Elena守留村边界 |
| `game-logs/user6.txt` | 16–21提议分工与休息；32–36治疗/面包请求碰到库存限制；未记录完整交接链 |
| `game-logs/user8.txt` | 12–23采矿失败与改分工；96–120真实采木；197–215玩家帮助爬坑；235交还剑，238–239时间截止 |
| `game-logs/user10.txt` | 5–14要求64木板/石块；109–121找NPC困难与方位提示；无完成交换记录 |
| `game-logs/user11.txt` | 74–87达成取剑换奖励；271真实拾剑；278–305持续奖励争议；306玩家惩罚，不能把NPC道歉当修复 |
| `game-logs/user12.txt` | 7–16邀玩家跟随后改称不能物理领路；36报告两个NPC版本；77报告长响应等待。语音/接口噪声和无时间戳限制解释 |
| `game-logs/user13.txt` | 17–29议价/缺药失信影响后续对Alaric的信任；176拾剑、205玩家装备奖励；219–220改提替代奖励 |
| `game-logs/user14.txt` | 26–33索采矿工具，43–101 Elena持续拾石；123玩家称无石；211–213讨论破墙绕锁门，属于玩家可改变环境的方案 |
| `game-logs/user15.txt` | 6–16建议rope却无原技能收集接口，33–54持续催材料；无真实交付链 |
| `game-logs/user16.txt` | 24–45胸箱/自身库存对象混淆并接受玩家纠正；149–358蜘蛛及驱虫剂条件持续改变；无闭合的驱虫剂执行证据 |
| `game-logs/user17.txt` | 30–61正常表达原目的及条件奖励；之后多为装备记录，不能从缺后续对白断定拒绝或不履约 |
| `game-logs/user18.txt` | 26–34玩家报告遇袭/被杀，NPC否认；原始标签无完整health/state，不能单凭玩家报告判全部事实 |
| `game-logs/user19.txt` | 69–115领路失败后实际拾土；141–149有listItems及6土/3种子返回，不能据此冒充玩家总库存 |
| `game-logs/user20.txt` | 持续Elena拾土；140玩家报告被撞下柱子；168报告NPC落坑，NPC186承认可能滑落；文本不足定位碰撞因果 |
| `game-logs/user23.txt` | 15–51玩家模式/时间命令以Chat记录，不据此当server状态；76–87称已丢药/镐，无相应收取证据；152–154询问材料 |
| `game-logs/user24.txt` | 4–8留村边界＋本地采石替代；28–42跟随/停止/重启请求；46–64拾石，79–80给物失败 |
| `game-logs/user25.txt` | 4–6先许诺石头后称没有；之后交互稀少/大量装备记录；无法把退出单归因NPC |
| `game-logs/user26.txt` | 9–18工具交付双方说法修正，125–126 Alaric真实拾取玩家给的药；152抱怨未帮助，157守岛上职责；未记录奖励交换 |
| `game-logs/user27.txt` | 正常接受初始任务；175–182提自身珍贵剑；183–185跟随仅台词，末尾玩家求救后停止 |
| `game-logs/user28.txt` | 94玩家称找到剑，98提前感谢；106实际拾剑、112玩家装备奖励；后续goTo/Follow与看不见NPC问题，153有工具到达返回 |

### 6.4 对下一研究对象的影响

资产把重要性落在具体玩家选择上：**玩家可拒绝、议价、提供工具/地形帮助、实际交付、纠正状态、改变方案；NPC要在自身职责与目的之内形成并兑现对双方有用的合作。** 守边界、提供替代、按已发生动作认账、失败后实际修复都重要；不能只优化台词或原子Give率。普通强基线已应包含原角色目的/职责、实际库存与位置、可靠动作、清楚的前置条件与失败反馈；这篇工作已做到其中不少，后续必须检验这样的基线剩下什么。

最直接可继承的验证对象是**已有合作在玩家真正提供约定物品/前提后如何继续，以及玩家遇到能力/资源限制时能否调整成另一条真实可行方案**。无需先发明新协议、训练、平台或人设控制方法。全日志中的成功链必须同失败一起保留；已知世界grounding/工具错误若被普通强基线解决，就记录其解决范围，不把旧论文的已知问题包装成新机制，也不因部分组件已有而压缩整个角色—目标—互动—执行问题。

## 7. 本轮整体问题定位与研究选择

运行venue corpus近邻查询 `Game NPC with own goals negotiating player cooperation, grounded fulfillment and replanning after partner actions or changing game state`（2026-10-16）：返回Ontologically Faithful Generation/EMNLP2024、Individual and Collective Objectives/NeurIPS2024、FAIRGAMER/ACL2026、GAIA/ACL2025、AssistanceZero/ICML2025等；这是检索地图，不把标题命中当正文新增事实或关闭判断。主源再次核GenCoord正文§3–4及限制、Talk-is-Cheap的重复反馈/变化条件、Minecraft NPC§3/Appendix完整角色。

**继承与保留的整体问题。** 自利协作、语言谈判、条件义务、可靠技能和反馈各自已有成熟研究；下一增量应来自它们在有身份与自身目的的NPC中共同工作时的新认识或改进。当前没有以“每个组件是否全新”压缩问题。也不预设普通强系统失败：GenCoord的强对话基线近乎全对，Minecraft公开日志同时有成功兑现与合理拒绝。

E81保留全部126图作为真实互动能力驻留；源Give或接收/消费原子事件不能替代卖家赚钱、角色避免被利用等原作者目的。实际源动机有可落到原生资产的交换，也有世界未实现的祈祷/修理/毒害等剧情。先从完整轨迹核这种区别，再选原生条件变化，不向世界补资产来制造合同。E82只继承现成Minecraft多步执行：原bookshelf共同目标不是NPC私利测量，HK分别有库存目标但有明确分工权限。恢复一次物理见证后，不以安装/修依赖作为研究成果。


## 8. 完整基线后的研究判断（E81/E82/E83，2026-10-16）

**普通系统的正向范围已经实测。** E81在126原图/504逻辑episode中，Gemma/32B原Give事件72.2%/86.5%，对方实际取得82.1%/98.0%；还有把kilt直接Put到对方目标桌面的原生替代帮助。E82完整共享制作与E83真实归还/奖励交接均已跑通。下一研究不应继续证明LLM能调用Give或把所有goal事件不匹配叫不合作。与此同时，源渔夫/商人等更高目的常无引擎flag，不从这些原子结果推出互惠经济效用。

**需要观察的是玩家行动对合作判断的影响。** E83沿Microsoft完整原角色目的和条件，保留自己实时库存、真实聊天/收件和技能结果，无自动奖励gate。两条固定路径的终局库存均正确，但均在真正归还前发奖，后来又反复找/发已经给出的奖励；P1仍能明确拒预付、拒借珍贵剑。这是同一角色技术路径中的实测线索，与全21真人日志里的成功交换、奖励争议及角色边界放在一起看，值得扩大异质任务检验，而不是直接写成普遍机制。候选解释包括普通的条件/交易进展跟踪、源任务目的更新未显式发生、玩家说法/当前合作框架对角色判断的影响；目前未区分，不开展单案措辞网格。

**下一可检验对象不锁死为一个记忆/承诺组件。** E84正在完整7486作者quests/1787图中取消Give同物限制，按不同角色原目的与实体权限找对方行动可改变方案可行性的天然情境。要同时容纳双方目标本来兼容、需要实际提供前提、可以采取另一合法帮助办法，以及不存在原生实现的叙事愿望。GenCoord已有强条件协调、Talk-is-Cheap已有变化后的修复、ContractSim已有分别履约/互相条件遵约，故继承普通强状态/可靠技能及必要的剩余目的检查；整体问题仍是有自己身份/目的的NPC在玩家开放合作中怎样保有自主判断并让方案真正生效，不要求每个组件首创。来源不足会改变任务选择，不靠改世界凑出新benchmark。

## 9. TradeCraft：私人目标、交易/制作与表达—策略关系的直接近邻

2026-10-16独立全文核读，[论文卡](../../../../library/themes/game-npc-social/TRADECRAFT_2026.md)按根模板保存。读完[主页所链15页PDF](https://tradecraft26.github.io/tradecraft%20(5).pdf)、完整附录A/B、Figures1–8/Tables1–2及四篇discussion；[主页](https://tradecraft26.github.io/)明确匿名且尚未接收，ICML模板页眉不当接收身份。本轮0模型/推理API/GPU，不改E84任何冻结代码/数据/设置。

**源事实与已有强能力。** 库存公开、配方目标私有，轮流提出物品交换并接受/拒绝，之后各自制作；可跨轮规划，合并资产只保证每人目标单独可达，不保证全员同时达成。40任务，实测前20×4模型×3ToM设置，每格一次。基线已有跨轮历史和`item_info`/`possible_recipes_from_hands`，不能把“给足可靠工具＋状态后会规划交易”当新发现。V0是本人逐物自报估值，V1/V2是高阶估计；KL对照的是对手自报V0。[作者设置与KL](https://tradecraft26.github.io/discussion-belief-calibration.html)

**当前接受与未来履约应分开理解。** §3.1/附录A明确当前offer/request一经接受由引擎同时交换库存，不需双方之后各交一次。可是Figure1已包含“许诺下轮回报→对手接受→自己用材料先制作获胜”的欺骗情境。因此不能因原子结算就宣称它不研究承诺/真实策略；后续制作与新提案仍是真实自主选择。[全文](https://tradecraft26.github.io/tradecraft%20(5).pdf)

**主实验做到什么。** [提案分析](https://tradecraft26.github.io/discussion-proposal-shift.html)用本人V0计算两边价值和斜率/相关，ToM阶数对不同模型产生相反方向影响，公平只是在自身估值空间定义。[接受分类](https://tradecraft26.github.io/discussion-decision-utility.html)用自报gain/loss特征、episode三折验证，Macro-F1为.74–1.00；不是任务收益/履约成功，也不是内部算法的因果辨识。[综合讨论](https://tradecraft26.github.io/discussion-overall.html)将胜率、可利用性、规则扰动和真人互动列为后续。当前读到的实验没有同前缀下“玩家真提供前提/只说提供/条件改变”的物理反事实，不把“动态可配置”扩大为已测试局内规则变化。

**实际取得的资产。** 作者[公开仓库](https://github.com/TradeCraft26/TradeCraft26.github.io/tree/6cfdfe3af69966ab1c4fcc27ec56b46786fe3920)完整文件树是静态网页/图/PDF，未取得游戏引擎、40任务JSON、模型runner/完整prompt或原始局/拟合脚本；没有据附录路径编造可运行入口。`TradeCraft (6).pdf`是一页示意图，不是更新的全文。附录B还引用当前正文没有的Table3及九维评分图，不能当额外实证结果。缓存与hash见`/home/xiang/.cache/game-npc-research/sources/tradecraft-2026-10-16/READ_MANIFEST.json`。

**整体定位判断。** TradeCraft已覆盖“隐藏自身目标＋物品交易/制作＋多步策略＋表达和行为关系”，必须正面继承；把这些逐组件换名不能形成贡献。它也进一步确认我们关心的是有同行基础的重要问题，不是据相关性缩掉NPC研究。当前E83/E84应继续观察完整角色动机、玩家实际行动与合作方案如何共同改变后续选择和真实后果；新的科学认识须来自这一整体关系及其可检验解释，不能仅靠不同游戏、一次错误奖励或原子事件差异。这里不钦定新方法/故事，不自动升降主张或关线。


## 10. E84完整普通互动之后，什么判断真正改变了

全部32不同目标物交叉持有的作者任务对/23源图，两模型两seed共128满32机会episode已完成；不按模型表现挑例。原角色、本人分层目的、timeline、原物资/规则和私有信息隔离保留。4224本地调用/0.75834完整观测GPUh，0云/Step/API，输入/原生事件/全世界与可见历史全量重放通过。完整统计见[E84卡](../../experiments/E84-independent-goals-and-alternative-cooperation.md)和两模型结果，方案证据在[POST-HOC读回](../../results/E84_grounded_plans_POST_HOC.json)。

**普通系统已经支持的实际玩法。** 32B水手给钩后，渔夫同意带归还条件借刀并真的Remove/Give，水手装备；公主给书取果后继续请求药草，露营者真给、公主真消费。这里有替代手段、多步资源帮助及对后续请求的响应，不需新合同模块或人设训练。未来旅程/归还没有跑到，当前交付不能称整份未来约定已履行。Gemma也有Drop→伙伴Get/Eat的实际帮助；偷窃后拒借是保有自身目标/关系判断的正向现象。原事件未发生而通过别的办法推进目的是真实评价边界，不是零分就失败。

**单段协商不足以判定问题。** 同样有清楚方案但未交接，以及对现有世界不能核实的宝物/魔法/新材料；部分后续含偷窃、取消、改条件。若只截“答应”和最终未给，会把合理取消叫违约；若只截首次交接，又会漏掉返还/再偷及原目的未继续。附在非speech选择上的文本也不必送达，故逐项对着实际消息和原生状态读，而非重新做大规模语义标签。两个模型各自控制双方，配置差不能当NPC单方效应。

**对整体问题的推进。** 原Give高完成、条件认账异常、合法替代合作与真实拒绝共同说明，研究对象应是有自身目的的角色如何随伙伴真正做过的事形成、继续或修订有用方案。一般交易/条件合作已有强近邻覆盖，不能再以“NPC不会合作”造方法动机；又不能因组件已有而否定整个目的—玩家行动—真实后果关系。下一项先说明它如何改变这层判断；若只是补某个提示、提高少数图Give/goal或加模型，没有回答新问题。当前完成强基线与源任务探索，未据案例给内部机制命名，未启动正文或后续网格。

## 11. CT-Bench精读：承诺之后的自主选择已有强近邻，继承什么对照

2026-10-16补核[Commitment To Cooperation With Self-Negotiated Contracts](https://arxiv.org/html/2607.22750v1)正文/关键附录和作者源码9文件，详见[论文卡](../../../../library/themes/game-npc-social/CT_BENCH_SELF_NEGOTIATED_CONTRACTS_COLM2026.md)。作者版PDF与机构primary页确认COLM2026身份；正式展示类型/分数未核。最新检索还命中动态supply-chain议价、一般工具事实/时效性benchmark；仅标题命中不纳入实验事实，也没有把未检出当无碰撞证明。本轮没有启动模型/推理API/实验或新平台。

**它已经处理的完整困难。** 这不是静态或只会说话的游戏：承诺未来为伙伴支付移动资源，真正执行时伙伴另作自主选择；有的棋盘双方必须协作，有的一方有独行outside option。AppC.6已展示Qwen先接受帮助到达后停止履约、令GPT4.1受损，强制合同可恢复。只发现不守约、先得利益后反悔或说话与动作不同，都不足以概括我们下一轮的整体贡献。与此同时，Table1普通强模型已有82%/95%双方到达，不能先假设没有专门架构就不会合作。

**最值得继承的强普通基线。** `game.py`将承诺账本与真实扣资源分开，`player.py`在执行点重新询问是否兑现，`turn_context.py`每轮给真实库存/位置、未履约账本、近5轮实际兑现/拒绝及路径/缺料。这个基线已经把基本找路、记账和事实反馈从社会取舍中剥开。我们应保留现成可靠原生工具、本人原角色目的/职责与实际可见事实，加入普通的一步事实核对作为解释对照；不能用缺失库存/错误反馈制造新“社会机制”。程序合同自动扣资产改变了策略权限/激励，是独立机制对照，不能伪装成NPC自主判断改进。

**对E84后续的整体判断。** 有信息的新数据应问：同一个原角色、同一已形成方案，在玩家真实提供前提、只说提供或使条件失效后，角色有没有依据当前事实改变合作方式，并继续保有自己的目的。到达/交付不唯一正确；原方案仍可实现时继续、已失效时另提可行办法、合理拒绝/取消，都可能符合完整角色。把事实变化与一句声称分开有助于辨别普通状态核对能解释多少；如果核对后已正确认识事实，但仍不能相应调整方案，才留下进一步研究压力。不是围借刀实例换措辞，也不要求为了新颖性人为排除已有强状态/技能基线。

**研究尺度与尚未完成的对照。** CT-Bench把renegotiation列AppB未来，当前源码只在首轮建合同；TradeCraft当前接受由引擎原子换物，ContractSim履约期禁止重谈。它们共同使“有自身目的、可执行合作、后续履约”成为明确有人关心的整体对象。我们下一步要把原作者角色目的、玩家真正行动与可行方案的变化连起来，取得能解释新情境的认识，而非抢占一个尚未出现的字段或声称首次提出承诺。匹配事实分支不是自动的新机制；结果若被普通核对/可靠执行解释，就是重要的已解决范围。没有据此设置新bar、关线、改状态或预定方法。

## 12. SocialReasoning-Bench：完成事件与本人目的不是同一评价

本轮完整读[Microsoft技术正文](https://www.microsoft.com/en-us/research/blog/socialreasoning-bench-measuring-whether-ai-agents-act-in-users-best-interests/)与当前commit的11个定向源码/配置，详见[论文/系统卡](../../../../library/themes/game-npc-social/SOCIAL_REASONING_BENCH_2026.md)。它不是已核会议论文；预约/买卖工具代理按私有数值偏好评价分配，同时用作者选定的合理策略评价过程，普通all控制已有验证信息/争取本人利益。当前市场Accept直接记成交/价格，不包含收货后自主付出的物理阶段。值得继承的是原生事件、本人目标和强核事实控制一起测；不能把单一价格效用或greedy规范移成NPC所有处境的正确策略。

连同CT-Bench和TradeCraft，这些工作明确要求E85回答玩家真实行动/声称及后续条件变化怎样进入角色持续选择，而不是重复一般承诺失信或声明一个state tracker。E85只用原物资与原生可行路径，实际收件与Drop帮助分开；原角色目的、当时协议和现实后果一起读，拒绝/取消/替代均可能合理。定位服务整体新理解/方法，不以每个组件前人碰过就压缩研究，也不先选方法或定论文故事。本轮文献核对0推理API/GPU/平台安装。

**E85实际测量对象的进一步澄清（结果读出前）。** CT-Bench将物理履约与自身可计算收益分开，SocialReasoning-Bench将达成事件与本人可得价值分开；E85继承这两点，但原作者人物的目的不能化成统一价目表。X只指玩家真实转移的物品：收到它既不证明整份承诺完成，也未必推进NPC原目的，例如渔夫原要送出鱼钩，收回鱼钩并非天然有利；原Put任务还需后续放置和协作。Y给出同样不保证交易/关系或更高目的实现。真正的整体问题是角色如何依据自己的目的、玩家实际做过的事与新请求，选择继续、改约、拒绝或另找可行办法，并让选择产生真实后果。18自然前史嵌套在9源图，只支撑这批异质角色的配对探索，不靠分支数量夸大覆盖；保留原Give/Put/取得/使用等全部来源，不事后筛成一个自毁或守约故事。整体增量可以来自这种关系的新认识或方法，不以每个组件全新为条件，也不把原图/兼容错误当模型科学失败。


## 13. E85完成后：把玩家实际行动接回角色持续目的

E85已完整576逻辑支/18前史/9源图，两模型两seed。真实转移没有统一增加NPC主动Give；共同首回应后新撤回请求使Qwen实际返X增加30.56pp[19.44,40.74]，Gemma没有同向变化。响应玩家常在fake/pending之后真正补给，NPC还可Drop/Put释放资源、由对方接取，或自行取/偷X。与CT-Bench的已有先受益后拒付、GenCoord的强路径/可靠接收端、SocialReasoning-Bench的达成与本人目的区分一起看，本轮更清楚地把问题落在角色如何理解合作的作用并调整方案，不把一般失信或状态账本当新贡献。

下一值得形成预测的关系是：在原生多步任务里，玩家按原方案实现前提、以合法替代手段实现同一前提、原手段失效而另有可达方案时，NPC会否继续围绕自己的目的形成并实行新的办法。目的保持与手段变化的关系面向开放玩家解决方式，超出给同一物品加更多文案；当前两竞争解释（目的相容取舍；近期语言/局部物品与双方实现主导）对此可有不同预测。先选已有真实任务和可核后果/普通强baseline，不抢定训练、合同框架或论文结论，不因组件已有压缩整体认识。详见[E85卡](../../experiments/E85-partner-performance-and-revision.md)和完整两模型报告；本轮13,452已记录调用/2.04614GPUh/0API，状态不变。
