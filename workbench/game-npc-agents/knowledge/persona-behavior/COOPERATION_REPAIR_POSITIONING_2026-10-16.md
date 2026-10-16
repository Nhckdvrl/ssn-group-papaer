# 合作提案、实际履约与条件变化：任务资产及强基线核读

2026-10-16；推进I04/C06/P12的后续研究对象判断。仅主源检索、正文/关键附录及作者代码只读，0推理API/GPU/新实验；不改状态，不预定方法。先读已有GAIA、Dragon、CoopEval、PUBG/FACUL、MineNPC、SidConArena、MMOAgent等卡，以下补直接协议和可取得资产，不重复泛泛定位。

## 1. 能直接改变下一步动作的判断

**下一能力对象应是：角色围绕自身目的形成可执行的条件合作方案，并根据玩家真正履约、未履约或条件改变继续行动。** 它不同于把同一源物索要局增加话轮；E80已显示仅恢复会说话/Steal的玩家并不自动产生足量的不同资产协商。下列强近邻已分别覆盖有界承诺执行、条件履约、重复修复和真正游戏协作。应直接继承其可靠执行与评价，不把“LLM会谈判/承诺接技能/双方有目标”当新发现，也不以这些组件已有就判整个NPC问题无价值。

| 主源 | 已确认的有效协议 | 实际可取得资产；不是已运行声明 |
|---|---|---|
| [Talk is Cheap, Communication is Hard](https://arxiv.org/html/2605.01750)（2026预印本，正文自述under review） | 私有项目＋每轮协商后分别提交资源/项目，程序判越额及收益；重复遭遇和项目变化 | [官方trace explorer](https://devyaoyh.github.io/a2a-negotiation/)实际可HTTP读取（HTML含数据），正文AppH列主实验run IDs和live runner；未确认公开backend仓库，不启动托管runner/云模型 |
| [GenCoord v3](https://arxiv.org/html/2608.22055)（2026-10-09预印本） | 自己路径＋请求对方续作；验证交接后激活义务，规则反馈可触发改分工 | [作者仓库](https://github.com/JulianZJN/GenCoord)是论文及紧凑证据数据，README/文件树已核；没有完整Minecraft运行器，不能称可直接复现系统 |
| [Evaluating Rational Contracting / ContractSim](https://arxiv.org/pdf/2608.10475)（2026-08预印本） | 协商合同后11期实际付款/采购/生产；可比较遵约、被剥削、合理停止 | 完整附录prompt、受限合同语言和动态规划基线说明可读；未找到可确认作者源码入口，不能称现成可运行环境；**协议后禁止通信/重谈** |
| [Collaborative Quest Completion](https://arxiv.org/html/2407.03460)（2024原始研究） | 原角色要营救/找回剑，玩家可帮忙、反问奖励；NPC接矿采、跟随、丢物等游戏API | 已读原论文角色/约束/API prompts与案例；当前版本未确认完整引擎/日志下载，不能把检索摘要的release表述当已取得资产 |
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

读§2–3、Tables2–6与Appendix A.1–A.3完整角色/函数/约束。Alaric有找回钻石剑、与Elena和解的目的；明确要求拿到剑后才能给netherite奖励。Elena因医师身份不能离村，要求玩家救人，能给原有工具帮忙。玩家实际放块、移交物品、提醒处境，存在资源交换谈判；这比仅有共同任务口号更贴近NPC对象。28玩家中7完成全部任务；没有随机对照能把此率归因某一prompt组件。每6轮一次subgoal帮角色回到原目的，但不能直接称已解决全部偏航。

其Table4保留“说已丢剑，玩家仍看见手持”的异常，显示有function feedback仍须读实际世界。原有约束是强普通baseline：保留自身角色职责、明确交换条件、真实库存、动作反馈、定期依实际状态重审剩余目的。继承这些，无需声称首次发明共同承诺。

### 5.2 MINDcraft / MineCollab的代码可执行边界

读正文§3–5/Tables2–3、Appendix7.1完整general prompt、9–10成功/失败协作入口与12动作目录；定向作者源码pin **`f6a9556cf756e6bd88a75cc2fa0d5aed7599b101`**（当前develop，非冒称原论文冻结版本）。读`minecollab.md`、`src/models/vllm.js`、commands actions/queries、tasks/tasks.js库存判定、library/skills.js的Give/Craft实现。

完整现成任务包括资源分持的两人crafting、配方信息分持的Hell’s Kitchen、construction。主文提供47参数工具；当前Give实际靠导航/丢物/等待playerCollect反馈，不能把一次tool文本当最终库存已守恒。tasks.js对Hell’s Kitchen分角色检查目标物，再联合任务完成。原paper general prompt要求不要拒绝请求，故不是有自身私人角色目标NPC的原样强策略；继承动作层与任务资产即可。

源码/作者说明的入口（**未执行**）：`node main.js --task_path tasks/basic/single_agent.json --task_id gather_oak_logs`；两人原任务说明使用`python tasks/evaluation_script.py --task_path tasks/crafting_tasks/test_tasks/2_agent.json --template_profile profiles/tasks/crafting_profile.json --api vllm --url http://127.0.0.1:8000/v1 --model <local_model>`。需先有Minecraft Java server、Node依赖和相应task/profile；当前本文不安装或启动。vllm类本身只向给定本地URL请求，异常返回失败文本，未见改走云模型；检索/embedding等其他配置仍须明确本地，不从README默认OpenAI配置直接启动。

**本轮动作结论。** 现成强系统足以提供可靠动作和双方条件的执行起点；最应优先寻找的是原任务里双方确实有可实行的合作/替代关系，玩家动作真的改变角色下一步应如何做。先运行这样的完整自然任务并看成功/失败，不新增同种索要网格、不先制造一套“修复方法”，也不要求先上人评才承认行为证据。

## 阅读资产与限制

只读缓存沿用`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/`：`contractsim.pdf/.txt`、`minecraft_quest.pdf/.txt`及`mindcraft_*`源码。MINDcraft源码仅定向读取，未全库审计；GenCoord没有冒称拿到未公开runtime。未调用托管game runner、模型API或任何付费服务。文献证据说明已有解决范围与下一任务对象，不构成自动开线/关线/升级判决。
