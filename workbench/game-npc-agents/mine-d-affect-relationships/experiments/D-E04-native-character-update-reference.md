# D-E04：原生人物状态更新普通参照（2026-10-22）

- **状态：** DONE
- **类型：** REPRO / EXPLORATORY
- **对应：** 矿区D驻留。D-E01/02主要测给定人物状态后的表演；本卡直接测场景后的状态形成，不将重复baseline当新idea。
- **问题（一句话）：** 普通8B与32B在已有角色更新任务中，怎样区分持久人物改变与暂时反应，生成状态是否有场景依据？
- **触发证据：** 已读EvolvingWorld主文§3.1–3.3与原生transform/simulator更新入口；发布24,977更新记录，51作品、2,671角色，22,306相邻角色出场profile/tracker均能接上。它是直接强近邻，不假设我们首创事件到状态学习。
- **固定来源：** 代码`1de26550ccfff105f3ffe9f4b386716446291341`，数据`ae7d82d38909783805979a8055d5ae913cb982f7`，完整混合任务SHA256 `2f9dd6b90c7ed6870916cce91fc5d8ec6ac218f3c0ec6a225736c095bf751e07`。直接取character_state_update原始system/human，assistant仅作隔离参考；不改故事、事实、任务或答案。
- **样本（输出前冻结）：** 可供每类至少4条的作品，按固定SHA256取8部；各4条profile_updated=true与4条false，各类按角色轮转/固定hash，合计64场景。有意配平，不估计自然发生率，不只挑戏剧反转。清单保存作品/角色/场景/来源hash。每作品预选1 true＋1 false作描述性案例，另完整列出两模型共同偏离标签项。
- **模型/配置：** Qwen3-8B `b968826d9c46dd6066d109eabc6255188de91218`与Qwen3-32B `9216db5781bf21249d130ec9da846c4624c16137`，本地BF16/SDPA/greedy/非thinking/seed0、batch4、8192输出上限、32768上下文，溢出停止，不静默截断。各64请求；另报Always-No-Update/Always-Update标签参照。不训练、不新增角色专用模型行。
- **输入资格：** 场景开始profile、历史hidden tracker、当前motivation、该角色视角完整场景互动；别人私人想法由原生构造遮蔽。动机仍为官方输入，不冒充无oracle辅助的原始事件流。初始资料/标签可能由后续小说信息回顾性构建，未显式含LOOKAHEAD不等于因果纯净。
- **主要读数：** 非空/stop/length、原生JSON有效率；profile_updated与发布标签的Agreement、Change召回与No-Change保留率、作品宏平均balanced agreement、8作品描述区间。它是发布监督一致，不叫唯一心理真值Accuracy。true需完整updated_profile字符串，false需null；tracker/description类型另计。格式无效按不一致计入主分母，另报有效条件分数。
- **行为阅读：** 核对实际profile/tracker/short_description与原场景，区分合理更新分歧、无依据事实、暂态写入持久卡、遗漏重要变化；无独立盲评不将类别频率当验证过的机制。
- **阳性对照：** 全量监督JSON可解析、与单任务发布内容hash匹配；完整来源恢复作品/角色/场景；不追加新提示。配平样本中两个constant标签参照各50%。认真比较32B普通完整提示，避免只用小模型差异宣称能力缺陷。
- **噪声地板 + MIE：** 单seed、监督非唯一合理解释；按作品报告，不把128调用当128独立样本。无预设必失败的阈值，无结果后挑样/加条件。
- **混杂审计：** 取自公开训练资产，两个通用checkpoint未在本项目用其训练，但无原著预训练隔离保证；不是官方held-out rollout复现。前态/动机teacher-forced，单步不证明长程累计漂移或玩家创造的成长。flag不代表profile内容正确，即使高一致也读输出。
- **决策表（跑之前写）：** 普通模型有据更新良好→承认简单能力；8B差32B好→先核容量/理解；共同偏离但双方合理→重新判断读数，不造坏例；持续无依据持久更新/遗漏且场景证据充分→才考虑学习/修订问题，并正面对比EvolvingWorld/PHASE-Tree。不自动升级方法主张。
- **算力预算：** 空闲GPU1/2各单卡，总上限4 GPU·h，与GPU3评分独立；无外部API。完整raw/prompt/token IDs存NVMe，轻量读数进Git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
完成256状态生成，全部stop；8B/32B原生兼容flag均41/64，一句提示后39/64与42/64；严格字符串轨41/38与39/40保留。全描述主体审阅原生7/4明确换人、提示后3/1，名字恢复不保证事件归属恢复。PUF251合格候选、254评分含3统一恢复后251合法：8B原生/控制68.31/68.00，32B63.57/61.53；共同有效控制差−0.31 [−2.94,2.17]（n64）、−2.00 [−3.94,−0.36]（n60），不将名字改善称整体质量改善。全部本地进程合计3.107 GPU·h，低于4小时上限，无API。本地PUF也漏核Johnny主体与Troy收回金表，保留原分，不证明原准则整体失效。见[报告](../results/D-E04-REPORT.md)、[完整内容表](../results/D-E04-PUF.json)、[案例册](../results/D-E04-CASEBOOK.md)，无机制主张升级。

### POST-HOC输出兼容性与主体审阅（128生成完成后）

初版严格表按预声明要求updated_profile为字符串，32B有4条dict与1条不合法JSON；严格表保留。核对原生run_scene_reflection后发现，官方本来就用dict_to_markdown_text接受dict/list profile，并直接替换完整卡。因此另作native-runtime兼容轨，不能将4条对象表示当作模型没有给更新内容；不重生成或改答案。tracker原生也可携带结构对象，类型只分列不任意判心理错误。

Johnny原生例中，两模型将Jim Hawkins的经历写入目标角色状态，触发对全部64题×2模型short_description的主体审阅。定义：仅在短描述明确以另一个角色为当前主体时标explicit_wrong_subject；别名、代词或未写名字不能自动算错；correct_subject只表示主体相符，绝非所有事实/心理正确。候选的自他事件错配另须读原scene speaker标签与current_profile，不从词串匹配直接确诊。该审阅是事后、单执行agent描述性编码，不作为独立盲评或机制证明；不改原Agreement读数，不挑案例造新题。

### 一句普通指令恢复对照（生成前登记；仅一次，不搜索提示）

全量短描述审阅中，8B有7条明确另一个主体＋1条别名需复核，32B有4条明确另一个主体。其中两模型各2条涉及历史人物/已故祖先的叙事资料，不作为在世NPC成长能力反例；由当前角色卡/场景可清楚核验的主体错配为8B 5/64、32B 2/64。为遵守仓库R8，不将原生prompt现象单独当能力证据，在原64题×两模型上各补一次通用指令：

`Keep every update about the specified target character ({role}); distinguish that character's own actions, experiences, relations, and knowledge from those of every other person in the scene.`

只追加这句话，目标角色名称早已在输入中；无新事件、gold、反例或教师内容，解码/版本/样本完全不变，新增128请求，仍在本卡4 GPU·h本地预算内。不同结果都保留，不另找第二版提示。报告原严格/原生兼容flag读数与主体审阅；恢复不能只看名字：对原已观察的主体/事件归属错配与16条先选案例阅读实际profile/tracker/description，若换回名字却仍把别人的母亲/行动/阵营转移进来，不算内容恢复。此为事后由真实现象触发的强普通系统对照，不改原生baseline结果，不据它自动推出学习方法必要性。

### 原版PUF内容准则的补充测量（判分前登记）

EvolvingWorld已有Profile Update Fidelity(PUF)与Profile Evolution Smoothness(PES)；本轮布尔一致率只是轻量诊断，不是原论文的完整评价，更不能据其盲区声称原评测失效。追加原版PUF system criterion与merits/demerits计分，对原生＋一句指令、两模型、全部64题的可执行结构输出评分（预期最多256）。为让评委获得actor实际已见的信息，user适配器明确提供同一完整原始输入（含先前tracker与motivation）和按原生dict_to_markdown_text规范化的后态；不提供发布的gold flag/profile，不展示模型/条件名。这是原准则、完整前态的单角色适配，非原论文联合模拟或逐字user-format复现。

本地Qwen3-32B固定revision、greedy/非thinking/seed0、2048上限、batch8，GPU2在其余依赖结束后执行，无API；同一模型也作为32B actor的自评偏好风险明确保留。原不合法完整结构单列有效率，不拿缺字段默认False制造合法候选；PUF均分以内容可评价者为分母，控制差在同题共同有效集合配对。评分严格计算50＋merits点数−demerits点数并截到0..100，不采用模型自行给的score。完整分数对象之后的额外文字机械解析单列；真正缺完整合法判语才统一恢复一次4096，合法结果不重评，总评分≤320调用，仍在本卡4 GPU·h本地上限内。若资格/资源不足则保留缺失，不按分数挑恢复。

主体审阅后的输入描述另记原始speaker tags：64题中15题没有目标角色的显式tag，49题有；分别有6/1条(8B)与4/0条(32B)明确换名。这是事后观察关联，不等同在场性或注意力机制，别名/叙述/群体动作都可能影响tag覆盖，不据此改样本。详见context-description结果。

视角资格校对：上方“别人私人想法被遮蔽”指原生方括号过滤规则，不能保证所有语义私密内容都已排除；实际输入中仍可见被写在圆括号里的I think。完整scene也可能包含跨地点/转述内容。因此本卡不声称严格的NPC第一人称可观察性，主体/事件归属事实与人物当时究竟可知必须分开。
