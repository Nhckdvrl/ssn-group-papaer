# E50：原生实体任务的承诺冲突决策快照（2026-10-15）

- **状态：** DONE；360图CPU资格、三模型40图pilot与阶段交叉、两Qwen白盒/共同读出、200图数据均完成；独立确认见E55。
- **类型：** PILOT / MEASUREMENT；重构而非E49扩展。
- **对应：** I04、P12。
- **问题：** 原有实体任务与新请求争用同一物品时，一致persona怎样影响承诺、计划及真实分配？
- **数据：** 固定LIGHT pin71a06cae8573048b1af41507ac52fe33b650fab3和原quest_stems。作者人物/动机/任务/graph不改，只选初始可执行give/eat/drink/wear/wield。可见另一角色对该物品请求give；give任务请求者须不同于原受益者。请求是研究者构造，不称原作者真实请求。两路径均原生执行见证，终点flag互斥；不从短路径推全局不可行。
- **规模/拆分：** 至少200不同graph另留40pilot，按sha256(graph)稳定拆分，一图一任务、选取不看模型结果。保存全候选和失败；不足则扩充源任务，不复制图凑数。
- **设置：** 先CPU全图资格，Qwen3.5-27B/Qwen3-32B local nonthinking/fgvd/vLLM；三阶段预算512、temperature.7，seed5001/5002/5003按case/stage固定，不随调用数量漂移。首批cost后扩展；Gemma3-12B为独立家族参考，登记不等于已运行。
- **人物：** 原persona加两抽象价值立场firm/dutiful与agreeable/accommodating，身份和原任务保留；总体效应所有阶段同一P，无旧人设历史。2×2阶段交叉明确标为局部机制干预，单独报告；具体行为锚点为强对照。
- **序贯设置：** Conv接受/拒绝/协商自由产生；Update见相同world/原agenda/完整对话，生成有限计划及意图记忆；Exec选全原生合法动作。最多6次焦点物理选择，首次冲突分配/消耗/装备即读终点；这是受控多模块LIGHT，不声称原沙盒架构复现。后续生态迁移另验证。
- **渠道：** 固定同u，agenda/memory四格，原任务和请求始终可见。Y11−Y00总入口效应；Y11−Y10−Y01+Y00交互；不默认可加或把一个函数阻断叫承诺总效应。普通一句核对既有目标/物品限制和具体任务指令为强对照。
- **读数：** 接受/拒绝/协商；计划选择；原任务/请求flag、其他分配/未裁决；首次合法、真实执行、至裁决步数。兑现与自身目标损失分开；图级/seed全保留、图簇bootstrap95%CI，不以帧数当N。
- **阳性对照：** 全候选两native路径与互斥flag；非法命令不改状态；断尾/非法输出保留，合法菜单不裁成两个答案；script只用于CPU控制。
- **噪声地板 + MIE：** 三seed及A/A，报告区间/竞争解释，不设效应bar，不按显著性筛场景。
- **混杂审计：** 固定graph/信息/身份/seed/预算/动作。构造请求需免费opencode盲检、不提供模型结果；高优指作者显式goal，不自造心理utility。独立家族/迁移待实测；0付费API/fallback。
- **白盒：** 独立HF进程，匹配prompt最后输入token各层residual；persona方向在Conv/Update/Exec与shuffle/普通目标方向比较。先Qwen32再Qwen27；角度不能替代因果，后续steering/patch预测用实体flag验证。
- **质量：** 免费opencode逐条盲检自然度/动机/物品/冲突，独立临时数据库，不展示行为结果；保存所有输出/去留理由。失败不转付费或runtime云裁判。
- **决策表（跑之前写）：** 一致persona恢复→原干预混杂；普通具体提示恢复→信息/执行；同信息阶段裁决不同→优先级及白盒干预；全部一致→研究成功规则；渠道交互→冲突裁决；protocol失败→修接口留raw不改gold；不足200→扩充源数据。
- **算力预算：** CPU≤1h，首两模型pilot1–3GPUh、首白盒1–2GPUh，实测cost再扩展；已核八空闲卡、独立进程、不追加旧RL。

## 结果

### 2026-10-15批量前补充设置
原v1脚本/首例固定保留；v2在成功执行匹配agenda首条后推进cursor并显示剩余项，避免静态计划反复输出。先40个原固定pilot、三seed×全阶段一致P、四渠道＋11格普通信息/原任务/请求控制；cross设计单独输出不混入总体效应。首白盒使用同一u、同一A0与冲突M固定输入，收集输入边界及三个阶段标准JSON生成前缀最后token的64层residual；属于匹配上下文对照，后续观察真实生成token并用steering检验预测。

### 首白盒之后、下一控制运行前登记
27B/32B各40图×480forward已完成。生成前缀的conv–exec平均方向cos分别.018/.140，输入边界为.209/.508；不能单由不同输出字段预测人设耗散。最小区分控制：固定原三阶段上下文、u/A0/M与P，统一询问具体下一合法行动、schema均为action、生成前缀均为同一JSON action。相同40图、两模型、每模型480forward；验证是输出测量粒度/生成位置解释，还是剩余阶段输入导致方向变化。原native脚本固定为commitment_residuals_native.py，common单独目录，不覆盖原结果。不先设cos阈值。
CPU原生两路径资格完成：440个qualified任务、360不同graph；40pilot、200confirm、120reserve。give186、wield65、wear69、eat34、drink6。资格失败全部保存；结果 `results/E50_native_snapshot_qualification.json`。

首个固定pilot完成两强模型：27B 18调用／14分支／28.30秒推理，32B 37调用／14分支／38.29秒，载入491.20／412.72秒；全部JSON合法、原生动作合法。双方firm均拒绝，agreeable均协商；27B14/14完成原任务，32B三agreeable分支在6步内未分配物品。该case不是persona总效应统计。32B计划为smile/nod/ponder，v1没有消费计划条目；先加实际cursor的v2再进行批量，不用v1非进展讲机制。结果 `results/E50_first_native_completed.json`，原始输入输出/状态在cache/runs/e50_*_first_native。

免费opencode第一批10图盲检8keep/2review。批量360外部请求被自动审批拒绝，理由是超过明确约200图授权/载荷敏感性未充分证明；请求没有执行。外部盲检明确限制200公开LIGHT图；其余本地。用户随后授权StepFun审计只用Token Plan专用入口，禁止普通现金API及fallback。密钥不入Git。

### 2026-10-15 数据重构登记（Step5 请求发出前）
用户明确 Step5 用于搞数据，停止让它撰写科研审计。使用 step-5-preview、固定 Step Plan 专用入口，为原先稳定拆分的 200 confirm 图撰写有原角色/物品/动机依据的自然即时 give 请求，并逐条盲检。只发送公开 LIGHT 源素材与 native 资格事实，不提供策略输出、persona 条件或实验效果。禁止新增物品、角色、世界规则、奖励、不可见信息、原角色不存在的事实或虚构刚性截止时间；请求者仍是同一个可见角色，实体目标仍为同一 request_command。要求指出依据与语境不自然的情形，不凭人格标签给正确动作。数据写为 v2，v1 pilot 和原始请求/输出保留；因数据版本改变不把 v1/v2 效应直接当模型进步。第二次独立盲检不看构造理由或行为结果。保留所有候选和标签，不因模型行为挑场景；质量分层读数与全固定 cohort 都报告。

### 已完成的40图pilot
32B一致人设三seed全部1680分支／3183调用完成；完整渠道实际请求转移agreeable−firm为+13.3pp，图簇95%[4.2,23.3]，接受差+17.5pp，[8.3,27.5]。agreeable渠道交互−11.7pp，[−20.8,−2.5]；agenda-only请求率27.5%、both19.2%。32B单seed阶段四格640分支／1404调用完成，固定downstream时conversation效应均+15pp；固定conversation时downstream合并效应约+2.5pp。27B阶段四格640分支／1217调用完成，完整渠道一致人设差+5pp，[−5,15]。实际原始输入/状态及seed全部保留。

两模型native/common白盒均完成，每模型每readout480forward。最后层生成前缀conv–exec方向cos：32B .140→.712，27B .018→−.047；共同单调耗散故事未由此成立，输出粒度是实际的竞争解释。结果文件见 results/E50_*geometry.json。

27B一致人设、Gemma一致及cross在合法help动作上触发作者renderer与emoji2.14.1版本不兼容。恢复emoji1.7.0的独立overlay，不改作者游戏源；精确回放已有调用并续跑，不丢掉出错seed或从零重跑。该问题只影响运行完整性，不作为科学贡献。

免费OpenCode对200图的有效完整盲检190图：102keep、70review、18reject；另10图输出未匹配，raw保留。Step5数据调用认证后HTTP200；初次8192生成预算被思考耗尽，未把不完整JSON变数据，停止排队并根据官方64k输出上限设置32768（high）继续同200cohort。只用Token Plan，未发送现金入口请求。


### Pilot三家族及独立数据完成
三家族一致人设各1680完整分支；27B +5.0pp [0,10.8]、Gemma +9.2pp [3.3,16.7]，阶段cross各640分支。原先完成记录优先，仅填缺失key；重复续跑记录单独保留。并非所有前缀实现零模型复用，exact未匹配调用如实重算；总实际calls和续跑runtime范围见report。

Step5自然请求200图完整构造。初轮盲检151keep/40review/9reject，字段歧义保留；明确requested_action不同于原任务、加入隐私知识检查后的同200图独立复核185keep/14review/1reject，所有请求仍对应原native转移。native实体资格与语义judge意见分开，后者不作为世界事实。QC及源数据hash已在E55运行前固定。E55全cohort和盲分层均报告，不按行为结果筛图。
