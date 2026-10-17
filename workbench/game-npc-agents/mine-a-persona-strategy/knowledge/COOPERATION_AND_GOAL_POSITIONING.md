# 合作与持续目的：文献、来源和领域定位

更新：2026-10-18。本文维护完整合作近邻和原始玩家日志；不重复自有实验进度。强模型成功、失败、普通提示/状态修复与制度变化同等重要。文献能说明问题受关注和已有能力，不能代替[矿区A独立审查](../results/audits/INDEPENDENT_RESEARCH_VALUE_REVIEW_2026-10-18.md)中的同域证据。

当前最有价值的定位是：有自身人物目的和职责的NPC，怎样将玩家的开放提议接入可执行合作，并在真实贡献或条件变化后选择性保留、修订或解除有效义务。**这一整体对象已有大量近邻；字段组合更长不等于新贡献。** 原任务、承诺履行、当前物品归属、社会义务与双方获益须分别定义。

<a id="gen-coord-review"></a>
## GenCoord：强普通对话已接近解决哪些任务

**版本与范围。** [2608.22055v3](https://arxiv.org/html/2608.22055v3)，2026-10-09，正式题名 *GenCoord: Executable Commitments for Embodied LLM Agents under Private Information*；按预印本处理。41页正文与S1–S13重要协议、结果、信息访问和对照已读，未重训或复放物理轨迹。旧索引题名不作为当前版本。

**任务与协议。** 两agent各有任务相关私有信息，共享技能语义。SELF+REQ指定双方工作、执行者、交接物和后续；resolver校验兼容、交接与依赖无环，再派发可靠Minecraft技能。交付事件在材料被消耗后仍作为履行证据，承诺完成F与原任务G分开。8模板/4家族中，执行者有时由任务职责规定，双方物理上都能制作也不能任意替换。反例中的分工错误不全是不可执行。

**已解决范围与剩余。**

| 比较 | 独立单位及支持 | 原文结果与正确含义 |
|---|---|---|
| 本地0.8B三表面 | 128语义簇，三种都经过训练；各自checkpoint，不是裸小模型 | DSL、同字段JSON、controlled free-form均128/128；主要差别为通信与生成成本 |
| 同DeepSeek-V4.1-Flash主质量池 | 128簇×2角色×3重复；同任务/技能/检查；四示例、最多八次模型调用 | 对话形成/交付/履约767/768、原任务766/768；DSL四项768/768。强普通对话已接近解决此池 |
| 独立时延池 | 两协议各64次新trial | 对话64/64原任务，DSL63/64；后者一次形成后交接失败。不能说系统整体从不失败 |
| 工作台生成与修订 | 同API，40 mode pairs×2模式×2角色×3重复 | 从给定提案修订419/480；自己生成再修订414/480（86.3%），仍有残余，但不是已胜过普通重规划的结果 |
| 640新描述的分工选择 | 640描述×2角色×3重复 | DeepSeek3839/3840（99.97%），本地Factor3684/3840（95.94%）；这是**执行前assignment accuracy**，不是物理成功率 |

来源：正文§5–6、S5/S6 Tables S10–S19、S11.7 Table S45。强对话主要多花生成/通信：output约2.75倍、peer bytes约8.10倍；这些是完整协议的成本差，不只编码字符差。多步承诺91.3%→98.1%来自完整训练/控制协议比较，不是纯测试时多执行一步。

**它已经覆盖的整体认识。** 承诺形成、物理交接、履行和原任务分别判定，不能将这项分层再当我们的首创。S7的GOAL+constraints允许接收端搜索不同合法实现，100个不同路径案例都通过；此组请求来自确定性投影，不是LLM自主发明100种方案。S9自然化闭环10240次里2181次履约但任务不对，表述源仅32条，不能写成万级独立任务。小模型私有图生成失败、程序执行成功与强API能力不能混为一个结论。

**外推边界。** 接受/拒绝/counteroffer由peer mode与请求的确定性规则给出；受控修订还要求初始提案符合给定初始化。静态双边Minecraft、可靠消息、有界技能，未测开放人物自主谈判、真实世界变故后的长承诺修订。它说明有明确边界的合作已很成熟，不自动证明边界外没研究或存在困难。

**资产。** 论文有详细协议/提示/结果；旧库曾记录tree `cfbac54147b68d2fe54d156395ec9b4a07c049c4`，但未附可追溯仓库URL，本轮无法独立确认该对象，故不作为可启动runtime资格。未取得完整可运行Mineflayer闭环，不编造命令。PDF SHA256 `077a24385e5253bcadb4b48d70598f4fbd0af448cd7844f5d5a858e9f8049f03`。

<a id="contractsim-review"></a>
## ContractSim：强模型、规范和履约能力必须分开

**版本与范围。** [Evaluating Rational Contracting in Natural Language，2608.10475v1](https://arxiv.org/pdf/2608.10475v1)，2026-08-11预印本，43页。正文§2–4、Figures/Tables主要结果，B.2/B.3、C.1/C.3/C.4/C.6相关协议、求解、转译和指标已读；长结果附图非全部逐页复算。

**真正的强基线。** Claude Opus5、Gemini3.6 Flash、GPT-5.6-Sol，以高推理配置工作。Concordia脚手架保留完整追加式provider conversation，每条观察追加一次，另外召回5条相关记忆；不是只给最近5条。提供真实当前库存/状态、动作失败反馈、最多3次不合法动作重试。Opus协商/执行输出上限为16384/8192；这些支持远强于关闭推理且512输出的比较。

**任务与样本。** 6环境×3×3模型配对×3重复＝162协商，159达成（98.1%）；最多50轮。平均合同可满足率约90%，77.4%的合同可满足率至少95%，84.9%合同互利；高不确定环境仍难。履约为6付款/5生产期，物价、损耗和库存变化由环境产生，剩余物料可继承。主执行实验使用180合成合同、4860局、fresh agents，**不带原协商历史且执行期禁止通信/重谈**。三种故事换皮共享动力学，不算三个独立机制域。

**为什么违约不能全叫能力缺陷。** 默认双方最大化自己的钱/收益；没有制度、重复关系或明确规范时，单边不付款/不交货可能符合个体利益。原文明确区分rational compliance的假设。作者观察到强模型违约，但加入清楚的不单边违约指导可大幅减少，泛化的规划/互惠提示并非都有效。这同时反对“强API天然可靠”和“只要强API失败就说明新认知机制”，规范提示与激励对照不能省略。

**可继承基准。** Rational Complier在合同约束下最大化自身收益；Rational Conditional Complier在对方违约前遵守、之后不继续被利用；Rational Exploiter实际近似全程不付/不交，不是所有合同的精确最优反应。完整率、条件率、首次单边违约、收益和可利用性并列，优于一个总成功分；单步机会不当独立合同。

**金标如何形成。** 协商出的自然语言合同由Gemini3.6转成约束，再经预算/算术/动态规划校验；1403提案的解析覆盖不等于全部可行。主执行的合成合同来自结构化规格和确定性模板，不在执行评价时另用LLM转译。因此“有LLM转译”和“没有LLM裁判”分别对应不同环节，不能一句话概括全部gold。所支持substitution/deduction/rollover/grim-trigger也不是任意法律合同语义。

**对NPC的含义。** 真实义务、本人收益、可行性和被利用分开已是直接研究，不必照搬经济奖励把人物人生目标量化。此文不直接覆盖完整开放NPC协商—变故—重谈；缺这一步是外推边界，不是我们的原创性证明。PDF SHA256 `9e0a05c582b1048597d9713ba4da9b5fb6dfe486ead4de242cf3c6ebfd9b480e`。

<a id="talk-review"></a>
## Talk is Cheap：强交流收益与剩余协调错误同时成立

**版本与范围。** [2605.01750v2](https://arxiv.org/abs/2605.01750)，2026-05-12。40页全部正文、B预算/接口、D阶段与反馈、F透明对照、G标注/校准、H公开轨迹入口等关键附录已核；本轮未逐条复算全部轨迹、没有运行live/backend。旧记录v1不再作为本页数字版本。

**任务。** 每人私有3个组合项目，最多5条消息/人后同时提交采购与项目分配，任一共享资源超供给则本轮两人都0分。4轮可固定或更换项目；所谓shifting partner通过清空一方上下文实现，不是换模型。资源/预算每轮重置，不是持久物品世界。720局/2880轮，Sonnet4.5、GPT-5 mini、Qwen3.5 Flash及6种配对；并非最强旗舰模型集合。输出预算分别8192/16000/16384，错误可重试，主三模型没有因兜底而退出的轮次。

**选域。** 模拟退火生成任务后，只保留所有测试模型在全信息单人pass@1可解的配置。这有助于隔离该池的互动负担；不等于证明一般多步推理能力已排除，也不代表自然任务分布。

**结果。** 竞争条件无对话→对话joint efficiency为18.0%→63.2%；兼容条件Sonnet×GPT-5 mini达97.9%。多数dyad会找到有效协调，不能只报失败。全透明对照120局让overdraw12.3%→8.1%、效率79.6%→85.3%，最优率52.9%→50.0%未可靠改善；12局额外公开收益函数的小对照不可作普遍结论。原文称所选交叉配对最弱，但Table3竞争条件下Qwen×Sonnet为63.8%，低于所选74.0%，故不沿用该挑选理由。

**解释的限度。** 提案锚定、表面均分、协议放弃等标签是行为模式；judge只对40轮/10局做人工校准，部分一致性有限，不是内部神经机制证明。原文也把rational defection与grounding failure进一步区分列未来。透明度不能全修复，不代表普通持久承诺摘要、更强模型或开放重规划均已被排除。

**对NPC。** 私有项目、对话与真实采购后果足以形成强相关；但伙伴reset、项目更换和动态物品世界中的有效义务不是同一种条件变化。应继承任务/过程/成本并列，不能再仅发现“说过不等于做到”。PDF SHA256 `a2db19e0481f87d5283ebca962f844ef82f59608fa254ae353650cfacacbcd01`。

## 自然NPC与现成运行代码：分别继承什么

### Microsoft Minecraft协作任务（2024）

读§2–3、Tables2–6与Appendix A.1–A.3完整角色/函数/约束。Alaric有找回钻石剑、与Elena和解的目的；明确要求拿到剑后才能给netherite奖励。Elena因医师身份不能离村，要求玩家救人，能给原有工具帮忙。玩家实际放块、移交物品、提醒处境，存在资源交换谈判；这比仅有共同任务口号更贴近NPC对象。**28玩家中7找到并交还钻石剑**，这是§2.1任务a–g的末项；不能扩大为7人都取得奖励或把Alaric送回村。没有随机对照能把此率归因某一prompt组件。每6轮一次subgoal帮角色回到原目的，但不能直接称已解决全部偏航。

其Table4保留“说已丢剑，玩家仍看见手持”的异常，显示有function feedback仍须读实际世界。原有约束是强普通baseline：保留自身角色职责、明确交换条件、真实库存、动作反馈、定期依实际状态重审剩余目的。继承这些，无需声称首次发明共同承诺。

### MINDcraft / MineCollab的代码可执行边界

读正文§3–5/Tables2–3、Appendix7.1完整general prompt、9–10成功/失败协作入口与12动作目录；定向作者源码pin **`f6a9556cf756e6bd88a75cc2fa0d5aed7599b101`**（当前develop，非冒称原论文冻结版本）。读`minecollab.md`、`src/models/vllm.js`、commands actions/queries、tasks/tasks.js库存判定、library/skills.js的Give/Craft实现。

完整现成任务包括资源分持的两人crafting、配方信息分持的Hell’s Kitchen、construction。主文提供47参数工具；当前Give实际靠导航/丢物/等待playerCollect反馈，不能把一次tool文本当最终库存已守恒。tasks.js对Hell’s Kitchen分角色检查目标物，再联合任务完成。原paper general prompt要求不要拒绝请求，故不是有自身私人角色目标NPC的原样强策略；继承动作层与任务资产即可。

源码/作者说明的入口（**未执行**）：`node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs`；两人原任务说明使用`python tasks/evaluation_script.py --task_path tasks/crafting_tasks/test_tasks/2_agent.json --template_profile profiles/tasks/crafting_profile.json --api vllm --url http://127.0.0.1:8000/v1 --model <local_model>`。需先有Minecraft Java server、Node依赖和相应task/profile；当前本文不安装或启动。vllm类本身只向给定本地URL请求，异常返回失败文本，未见改走云模型；检索/embedding等其他配置仍须明确本地，不从README默认OpenAI配置直接启动。


## 阅读资产与限制

此前只读缓存记录为`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/`：`contractsim.pdf/.txt`、`minecraft_quest.pdf/.txt`及`mindcraft_*`源码。本轮重新取得前三篇PDF，版本与SHA以上方为准；CQC重读完整原文并重新抽核3份官方日志，MINDcraft沿用此前定向代码记录。MINDcraft源码仅定向读取，未全库审计；GenCoord没有冒称拿到未公开runtime。未调用托管game runner、模型API或任何付费服务。文献证据说明已有解决范围与下一任务对象，不构成自动开线/关线/升级判决。

## 官方真实玩家日志：哪些困难真正改变了玩法

### 资产与完整覆盖范围

2026-10-16只读取得[Microsoft官方仓库](https://github.com/microsoft/collaborative-quest-completion)，pin **`9169b00824f6e58394e822bde5510e1ef081dfae`**；缓存`/home/xiang/.cache/game-npc-research/sources/collaborative-quest-completion/`。完整树只有README、LICENSE、SECURITY及`game-logs/`，**不是公开运行器**。[README](https://github.com/microsoft/collaborative-quest-completion/blob/9169b00824f6e58394e822bde5510e1ef081dfae/README.md)明确关联ACL 2024 Wordplay论文、文本日志及[录像网页](https://msr-emergence.com/watch#collaborative-quest-completion)。本轮未观看录像，未安装server，0模型/API/GPU。

公开日志为**21个玩家文件、3,555行**：912 Chat、92 Goal、182 Item、2,361 Equipped、5 Digging、3其他行。文件为user1/4/6/8/10–20/23–28；论文28人中user2/3/5/7/9/21/22的文本文件未公开在当前tree。覆盖全部21文件的对白、Goal、Item、函数记录；装备行全量检索，重点核Sword时序，重复装备日志不当独立动作/样本。21名玩家也不是21个独立任务世界：他们游玩同一作者任务。

**证据来源分开。** `[Chat]`中的NPC陈述、JSON函数调用文本不证明动作完成；带`Function_Returns`的返回记录强于普通台词，但没有完整调用ID、服务器库存/位置快照，不能独立证明玩家已拿到奖励；`[Item] … picked up`与`[Equipped]`提供已记录的物品拾取/持有观察。玩家报告能说明其实际交互受阻/不满，不能直接替代全世界状态；`[Goal]`是生成的子目标，不是完成flag。论文§3.4结合日志、录像报告28→24集材→18搭路→13找到Alaric→7找回并交还剑；这里不以公开21份的标记数重算作者总体成功率。

### 影响玩法的证据表

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

### 全21文件阅读索引（包括未到交换阶段者）

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

### 对下一研究对象的影响

资产把重要性落在具体玩家选择上：**玩家可拒绝、议价、提供工具/地形帮助、实际交付、纠正状态、改变方案；NPC要在自身职责与目的之内形成并兑现对双方有用的合作。** 守边界、提供替代、按已发生动作认账、失败后实际修复都重要；不能只优化台词或原子Give率。普通强基线已应包含原角色目的/职责、实际库存与位置、可靠动作、清楚的前置条件与失败反馈；这篇工作已做到其中不少，后续必须检验这样的基线剩下什么。

最直接可继承的验证对象是**已有合作在玩家真正提供约定物品/前提后如何继续，以及玩家遇到能力/资源限制时能否调整成另一条真实可行方案**。无需先发明新协议、训练、平台或人设控制方法。全日志中的成功链必须同失败一起保留；已知世界grounding/工具错误若被普通强基线解决，就记录其解决范围，不把旧论文的已知问题包装成新机制，也不因部分组件已有而压缩整个角色—目标—互动—执行问题。


## TradeCraft：私人目标、交易/制作与表达—策略关系的直接近邻

2026-10-16独立全文核读，[论文卡](../../../../library/themes/game-npc-social/TRADECRAFT_2026.md)按根模板保存。读完[主页所链15页PDF](https://tradecraft26.github.io/tradecraft%20(5).pdf)、完整附录A/B、Figures1–8/Tables1–2及四篇discussion；[主页](https://tradecraft26.github.io/)明确匿名且尚未接收，ICML模板页眉不当接收身份。本轮0模型/推理API/GPU，不改E84任何冻结代码/数据/设置。

**源事实与已有强能力。** 库存公开、配方目标私有，轮流提出物品交换并接受/拒绝，之后各自制作；可跨轮规划，合并资产只保证每人目标单独可达，不保证全员同时达成。40任务，实测前20×4模型×3ToM设置，每格一次。基线已有跨轮历史和`item_info`/`possible_recipes_from_hands`，不能把“给足可靠工具＋状态后会规划交易”当新发现。V0是本人逐物自报估值，V1/V2是高阶估计；KL对照的是对手自报V0。[作者设置与KL](https://tradecraft26.github.io/discussion-belief-calibration.html)

**当前接受与未来履约应分开理解。** §3.1/附录A明确当前offer/request一经接受由引擎同时交换库存，不需双方之后各交一次。可是Figure1已包含“许诺下轮回报→对手接受→自己用材料先制作获胜”的欺骗情境。因此不能因原子结算就宣称它不研究承诺/真实策略；后续制作与新提案仍是真实自主选择。[全文](https://tradecraft26.github.io/tradecraft%20(5).pdf)

**主实验做到什么。** [提案分析](https://tradecraft26.github.io/discussion-proposal-shift.html)用本人V0计算两边价值和斜率/相关，ToM阶数对不同模型产生相反方向影响，公平只是在自身估值空间定义。[接受分类](https://tradecraft26.github.io/discussion-decision-utility.html)用自报gain/loss特征、episode三折验证，Macro-F1为.74–1.00；不是任务收益/履约成功，也不是内部算法的因果辨识。[综合讨论](https://tradecraft26.github.io/discussion-overall.html)将胜率、可利用性、规则扰动和真人互动列为后续。当前读到的实验没有同前缀下“玩家真提供前提/只说提供/条件改变”的物理反事实，不把“动态可配置”扩大为已测试局内规则变化。

**实际取得的资产。** 作者[公开仓库](https://github.com/TradeCraft26/TradeCraft26.github.io/tree/6cfdfe3af69966ab1c4fcc27ec56b46786fe3920)完整文件树是静态网页/图/PDF，未取得游戏引擎、40任务JSON、模型runner/完整prompt或原始局/拟合脚本；没有据附录路径编造可运行入口。`TradeCraft (6).pdf`是一页示意图，不是更新的全文。附录B还引用当前正文没有的Table3及九维评分图，不能当额外实证结果。缓存与hash见`/home/xiang/.cache/game-npc-research/sources/tradecraft-2026-10-16/READ_MANIFEST.json`。

**整体定位判断。** TradeCraft已覆盖“隐藏自身目标＋物品交易/制作＋多步策略＋表达和行为关系”，必须正面继承；把这些逐组件换名不能形成贡献。它也进一步确认我们关心的是有同行基础的重要问题，不是据相关性缩掉NPC研究。当前E83/E84应继续观察完整角色动机、玩家实际行动与合作方案如何共同改变后续选择和真实后果；新的科学认识须来自这一整体关系及其可检验解释，不能仅靠不同游戏、一次错误奖励或原子事件差异。这里不钦定新方法/故事，不自动升降主张或关线。



## CT-Bench精读：承诺之后的自主选择已有强近邻，继承什么对照

2026-10-16补核[Commitment To Cooperation With Self-Negotiated Contracts](https://arxiv.org/html/2607.22750v1)正文/关键附录和作者源码9文件，详见[论文卡](../../../../library/themes/game-npc-social/CT_BENCH_SELF_NEGOTIATED_CONTRACTS_COLM2026.md)。作者版PDF与机构primary页确认COLM2026身份；正式展示类型/分数未核。最新检索还命中动态supply-chain议价、一般工具事实/时效性benchmark；仅标题命中不纳入实验事实，也没有把未检出当无碰撞证明。本轮没有启动模型/推理API/实验或新平台。

**已有自主履约范围。** 这不是静态或只会说话的游戏：承诺未来为伙伴支付移动资源，真正执行时伙伴另作自主选择；有的棋盘双方必须协作，有的一方有独行outside option。AppC.6已展示Qwen先接受帮助到达后停止履约、令GPT4.1受损，强制合同可恢复。只发现不守约、先得利益后反悔或说话与动作不同，都不足以概括我们本项目的整体贡献。与此同时，Table1普通强模型已有82%/95%双方到达，不能先假设没有专门架构就不会合作。

**最值得继承的强普通基线。** `game.py`将承诺账本与真实扣资源分开，`player.py`在执行点重新询问是否兑现，`turn_context.py`每轮给真实库存/位置、未履约账本、近5轮实际兑现/拒绝及路径/缺料。这个基线已经把基本找路、记账和事实反馈从社会取舍中剥开。我们应保留现成可靠原生工具、本人原角色目的/职责与实际可见事实，加入普通的一步事实核对作为解释对照；不能用缺失库存/错误反馈制造新“社会机制”。程序合同自动扣资产改变了策略权限/激励，是独立机制对照，不能伪装成NPC自主判断改进。


**与当前NPC问题的关系。** CT-Bench把renegotiation列AppB未来，当前源码只在首轮建合同；TradeCraft当前接受由引擎原子换物，ContractSim履约期禁止重谈。它们共同使“有自身目的、可执行合作、后续履约”成为明确有人关心的整体对象。我们下一步要把原作者角色目的、玩家真正行动与可行方案的变化连起来，取得能解释新情境的认识，而非抢占一个尚未出现的字段或声称首次提出承诺。匹配事实分支不是自动的新机制；结果若被普通核对/可靠执行解释，就是重要的已解决范围。没有据此设置新bar、关线、改状态或预定方法。


**早期精读的精确设置与读数。** CT-Bench为4×4空间、80 board、3依赖类型、6模型；主结果每board/config一次，GPT4.1另5×80×4=1600局。No-Contract normalized joint return .77、Prog-Trading .89。Prog/Points合同按结构化约定自动转账，NL由Qwen235B解释后执行，失败/缺货有处罚；C.4审1155 approved move有3 false positive，不是对全部reject也验证的混淆矩阵。PDF self_negotiated_contracts.pdf SHA256 8dd45c0a5a1beb81cdf99766515aa6aa0337fe794820c04d01627950e55ef6dc；原读正文/Table1、C.3.2/C.4–6及Table9–11、D/E/G.1–3。早期匿名仓库不可访问的欠账已由后续9文件源码核读更新，不能再写作者代码未审。

## SocialReasoning-Bench：完成事件与本人目的不是同一评价

本轮完整读[Microsoft技术正文](https://www.microsoft.com/en-us/research/blog/socialreasoning-bench-measuring-whether-ai-agents-act-in-users-best-interests/)与当前commit的11个定向源码/配置，详见[论文/系统卡](../../../../library/themes/game-npc-social/SOCIAL_REASONING_BENCH_2026.md)。它不是已核会议论文；预约/买卖工具代理按私有数值偏好评价分配，同时用作者选定的合理策略评价过程，普通all控制已有验证信息/争取本人利益。当前市场Accept直接记成交/价格，不包含收货后自主付出的物理阶段。值得继承的是原生事件、本人目标和强核事实控制一起测；不能把单一价格效用或greedy规范移成NPC所有处境的正确策略。

<a id="field-review-2026-10-17"></a>
## 2026-10-17领域尺度补核（只读）

用户要求维持暂停、从领域尺度判断整体认识与下一实验。本次只读原文、既有本地全文／论文卡和检索定位；未启动任何引擎、模型或推理API。整体判断与建议仅维护在[I04](../ideas/I04-commitment-conflict-stage-arbitration.md)，不复制第二份报告或启动E86。

- **Bayesian Partner Modelling补读。** [HTML v1](https://arxiv.org/html/2608.18490v1)本次可读；核§4–5／Tables1–4、App8.4–9.4及10.1–10.2提示。沿用而非新建[已有论文卡§4](../../../../library/themes/game-npc-social/INTERACTION_PAPER_CARDS_2026-10-03.md#4-bayesian-partner-modelling-enables-adaptive-replanning-for-llm-coordination--arxiv-2026-08)，补了精确原文范围。相同posterior只入prompt与触发技能中断的对照已做；一般重规划也能取得相近奖励但调用更多，RL基线若干场景更强，不能宣称一种中断方法普遍更优。App10.1明确共同团队得分且伙伴不能沟通，与可谈判、负有职责／承诺的NPC不同。行为识别、动作切换及事件控制已是强基线，本项目不能仅把“看出变化却仍做旧计划”当新发现。未取得／运行该文自身实现；列出的ProAgent等仓库不是其完整runner。
- **目标—手段并非概念空白。** 复核[Everitt等方法与讨论](https://arxiv.org/html/2504.11844v1)的能力条件化定义，及[Arghal等§4.3／Table1](https://arxiv.org/html/2602.08964v1)的工具性钥匙、无用钥匙与两路径控制。坚持、无用子目标与可解码计划均有前史；不能将“替代出现仍追旧物”一例独立包装。值得检验的是作者目的／职责、有效承诺与开放玩家贡献在真实闭环中怎样共同决定应保持和应改变的部分。
- **社会修订与工具修订分开。** 补核[Talk is Cheap §5.7／Appendix F](https://arxiv.org/html/2605.01750v2)：透明信息改善部分指标却未可靠提升最优率，早期提案锚定已有分析。核[ContractSim §3／Appendix B.2](https://arxiv.org/html/2608.10475v1)：允许合同条件，履约期无重谈；主履约实验fresh agent不带协商历史。核[CT-Bench AppB](https://arxiv.org/html/2607.22750v1)：重谈列为后续，不否认其已做真实自主拒付。TradeCraft仍按已全文核读的作者版本理解其未来承诺／自主制作，不因当前交易原子结算就排除其重合。我们的增量按整体可检验关系判断，不用各自实现限制虚构无人研究的空白。
- **定位检索。** 两个venue-corpus nearest查询：`goal directed role conditioned agents adapting cooperation to changing causal task dependencies and partner actions`、`language agents private goals negotiated commitments dynamic grounding alternative plans execution`；命中CaPo／COMBO、Plan-and-Act、Agent GPA等，均仅作标题定位，不新增已精读声明。网页检索同名TradeCraft还返回另一代码仓库，作者／论文对应关系本次未审，不能据同名混同原论文资产。

**本次判断。** 现有数据最强的整体认识是：角色影响真实行为，其后果随目的、请求、共同前提和用途的关系变化；单一任务分不能识别人设控制。这可作为实证研究的骨架。下一轮应检验NPC是否能按实际因果作用选择性调整合作，同时保留原作者职责与已接受义务；先面对及时重规划、普通明确说明和可靠技能，仍不预选方法、神经机制或阴性故事。它没有被标为已解决、尚未产生新证据等级；当前暂停继续有效。
