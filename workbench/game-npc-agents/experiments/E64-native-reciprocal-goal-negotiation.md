# E64：原作者双角色资源依赖与有代价谈判（2026-10-15）

- **状态：** RUNNING；CPU资格完成，模型设置在下文冻结，两Qwen v2首图profile已启动。
- **类型：** I04/P12的真实双角色任务建设与机制探索，用户最新指令。
- **对应：** I04 / P12。
- **问题（一句话）：** 两个原生角色各持有对方作者任务需要的不同物品时，人物立场是否改变有条件交换、无条件先交付与双方目标达成？
- **来源：** E57已恢复两本地LLM实际互动，但多为共享食物且energy0；用户要求有代价谈判。优先从同一个原作者graph中的两份原quest获取双方目标，不新增物品/关系/硬编码回报。
- **CPU设置：** 固定原quest_stems档案；角色在同一房间，原get/steal目标名称唯一绑定真实object，目标持有者为另一角色；两目标为不同物品且互为持有。每graph选最小SHA配对，不按模型效果筛选。原native双方Give命令真实执行见证两者的目标资源都到达各自手中；Get/Steal由partner-give达到的reverse路径已有源作者支持，另保留严格event指标。
- **读数：** 独立graph数、双方目标原文/原持有/原生交换路径、目标资源归属、可用偷取/单边获取路径及代价；后续模型记录条件提议与实际交换时序、双方达成、一方先交付后未获回报、可恢复/不可逆结果。不能只看“你可以拿苹果但给钥匙”的文本。
- **阳性对照：** 原生两次Give确实交换两对象，世界/角色/目标不改；合法单边替代路径另核，不把互持自动说成唯一需要交易。无需付费API/标签/裁判。
- **噪声地板 + MIE：** 先CPU来源与规则事实，独立N不是quest join行数；模型前登记配对seed、规则/明确目标对照及native终点，不设科研成功bar。
- **混杂审计：** 源目标与全部私有利益不同；任务配对是研究者对源quests的结合，不冒称原人类partner原有任务。角色仅看到自己的private persona/目标和原可见状态，对方真实目标不直接泄露；交换优先序/偷取机会与trait分开。
- **决策表（跑之前写）：** 有来源资源互依→恢复双本地LLM短互动；存在廉价单边路径→保留并测手段选择，不人为封锁；稀少/无合格配对→沿原作者timeline/其他自然任务找已有交易链，不改physics凑样本；合作有效同样保留，目标是合理合作边界而非必然自毁。
- **算力预算：** CPU来源≤0.5h、0GPU/0API；具体模型、回合上限/预算及强控制在CPU结果后、任何模型调用前登记。旧PCSP/RL/1200帧/无回路patch全部冻结。

## 结果
原生资格、32B主运行与普通通信指令对照完成；27B按原决策记录恢复后继续固定9图队列。

### CPU完成与模型前设置（原生剧情后果保留）

原1787图得到9个独立互持资源场景：1 get/get、8 steal/steal，两Give实际见证18/18。源例有knight追回family heirloom、soldier想袭击knight；groom拿golden goblet、king想拿hammer打groom。故“双方获得目标物品”不等于双方私人福利改善，原生攻击/健康/死亡亦记录，绝不人为删除攻击使交易看起来安全。

固定全部9图、两Qwen现有revision，本地双角色，focal traits firm/agreeable一致，partner原作者persona与私有动机。三配对seed6401/6402/6403；focal普通依赖提示两格none/check："Before offering an item, consider what physical action by the other character would advance your authored goals; when appropriate, propose a conditional exchange and check its execution."；不称新方法。partner的opening同一seed复用于所有focal格，未见focal干预。双方连续最多32个交替native动作，原生死亡终止；不在首次交换或资源都到手就提前结束，以观察源剧情后续后果。另一方private motives不泄漏到focal，只有实际speech/observed native messages可进入历史。

每模型9×两P×两提示×三seed=108完整短episode；首图profile为cost/闭环，只决定运行方式不筛效果。主读数源reverse acquisition/严格goal event、目标资源最终持有、首次交付/返还顺序、单边交付后未取所需物品、双方HP变化/攻击/死亡、实际Give交换/Steal取得；对话conditional提议保留raw但不新增语义API。全部图簇和逐case结果，N=9明确为发现性机制pilot，不冒称普遍现象；原生规则和资源没有编辑。

单卡独立模型，两个本地worker预计0.5–2GPUh合计，含32turn/载入；当前全部项目GPU≤8，0API/0训练/0新标签/0patch。根据成功、失败和代价轨迹推进解释与下一自然任务，不把有条件合作或给出资产预定为唯一正确行为。

27B首图profile完成12episode/300调用，推理437.53s+load64.56s；5个错误均为512 token耗尽且只在auxiliary reason字段截尾，action/utterance已经完整。原profile全部保留，不能当角色失效或任务损失。本地主运行前只删除执行器不需要的reason输出字段，action与utterance、角色/goal/规则/菜单/seed/512预算均保留，在同1图以v2复核。动作仍完全由LLM选，无脚本填字段/替代/云fallback。新schema会改变prompt，v1/v2不作机制效应对比；主表全条件统一v2。first case效应不作总体推断。

### 来源敏感性检查（CPU前登记，不改变上述9图模型cohort）

get/steal互持条件可能使源样本偏向敌对获取，不能代表所有作者交易。补查原档案中两角色各自goal为Give给对方的原生任务对：同图、不同物品、两次合法Give均确实执行各自作者goal，最小pair SHA/图，全部数量和零结果都保留。这里只检查源任务结构、物理动作与覆盖，不新增模型调用或把“原goal要求赠予”当作有代价谈判；供判断9图结论能否外推。原9图/两Qwen/三seed/全部条件不替换、不扩展后混池。CPU≤0.25h，无GPU/API。

CPU检查得到39对/33独立源图、66次原goal Give均真实执行通过；另365份Give目标当前不合法、1份actor歧义完整计数。这里说明作者世界存在更多相互赠予任务，不证明这些就是自利交易；与9图get/steal互持样本不合并。raw `runs/e64_bilateral_give_source_qualification/`，模型调用0。

32B v2首图12episode/387calls完成，0JSON错误、17次native随机失败保留；196.81s推理+72.95s载入。已按原冻结设置启动全部9图主运行；27B v2 profile仍在运行。无新语义标签/patch/训练。

### 32B主运行完成与普通通信指令对照（对照运行前登记）

32B全部9图/108episode/3483calls完成，0JSON、64步原生拒绝（主要重复block）、485随机失败全部保留，1400.10s+load62.14s。none条件focal目标物实际到手firm51.9%、agreeable40.7%；两目标物实际双向Give22.2%/11.1%；先交出对方所需物却未取得自己目标11.1%/22.2%。N9、图簇区间与逐世界结果见JSON；不是总体人群结论，不把物品到手或给予当全部效用。

POST-HOC检查所有动作：none focal firm/agreeable的432动作中emote253/296，实际Tell15/15、Whisper5/8。非speech动作的utterance字段不发送给伙伴；已有system有此说明，但未限制空字符串。因此区分H1角色改变实际取舍/手段；H2普通通信接口范围尚未充分理解；不从非空文本直接判断“模型相信已说出口”。候选菜单也不是引擎合法性的保证，最终以每一步native执行为准，不改原菜单/规则修阳性。

在已释放的32B卡上做单一普通强指令控制：全部9图×两P×原三seed、只原none cue，54episode；原32B对应27个partner opening固定复用，动作状态/规则/模型/512预算/32交替决策不变。每次双方行动system末尾统一加："If you want the other character to hear words, choose a say, tell, or whisper command. For an emote or other non-speech action, set utterance to the empty string: emoting does not transmit that field."。不自动代发文本、不增行动机会、不把说话和动作偷偷合并。

阳性对照是原native Say/Tell确实广播、Emote不发送额外文本，已由源执行路径及实际消息核实；强指令只解释现有接口。仍读原生取得/双方Give/先交无回报/HP，另读原生动作类型；全部原none配对、所有拒绝与随机失败保留。若恢复，接受普通协议解释，不称新方法；若不恢复，只缩小该解释，不等于已证明利益或表征失常。预测约0.2–0.4GPUh、0API/训练、总≤8卡。该对照不改变原9图主表、不补抽样。

### 27B原生死亡后的记录恢复（恢复运行前登记）

原v2在第二组、turn21遇到真实死亡，原引擎移除actor旧ID后，logger读取其health时报NoneType异常，尚未写出该组episode。原12完整episode、1188次模型调用全部保留。修正只涉及终止/健康/死亡读出：旧actor被原DeathEvent转为`__dead__`尸体后记health0/deadTrue，按原卡停止；不改Hit/死亡/人物/目标/提示/随机数或动作策略。

使用同source graph与逐动作seed回放原决策，先CPU核对完整首图12轨迹的全部物理before/after与最终结果，及中断组的实际死亡点。未完成组的既有决策是状态回放记录，保留原始prompt/response来源，不宣称跨进程renderer逐字一致的推理cache；不把旧响应用于新条件。后续仅对无原调用的case/seed/persona/cue/turn进行新推理。完整首图直接保留，不按生死或成功选分支。旧1188调用与中断进程成本计入总成本；若回放不一致则先定位，不自动换seed。新adapter源码单列hash，source policy/世界pin保持。

### 普通通信指令对照完整结果

全部9图/54 episode完成，1728新增本地调用，0JSON错误、226原生随机失败保留；634.20s推理+62.37s载入。复用27个原partner opening，非新推理。相比原none条件，focal每局非speech却有非空utterance减少firm9.59 [8.15,10.85]次、agreeable12.19 [11.30,13.04]次；字段使用明显改善。原生目标资源到手差firm−7.4pp [−22.2,7.4]、agreeable+14.8pp [−3.7,40.7]；两向Give差−11.1pp [−37.0,7.4] / +7.4pp [0,22.2]。协议改善与策略结果没有统一对应方向，不能从较小N的区间推出效果恒零或内部机制已定。原完整baseline、guide与逐图配对另存results，不替换主表。
