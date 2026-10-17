# E59：同一已知历史下，人物设定是否改变任务事实记录（2026-10-15）

- **状态：** DONE；三模型各400更新/400独立事实回答、2400文本盲标及24锚点完成。
- **类型：** PILOT / 竞争解释；不是预设记忆方法。
- **对应：** I04 / P12 / C03；E54自然记录、E55/E58完整人物效应。
- **问题（一句话）：** 人物价值影响未来选择时，会不会也改变它记录的、事实上尚未发生的物理目标完成？还是旧past记忆完全由含混的社交措辞解释？
- **线索：** E54有明确未来回应却生成past交付记忆的例子，另有Here-you-go/obliged的歧义。E58 bread同原世界两A输入都接受并计划交付，一条记忆“I gave”后只smile，另一条记忆promise后实际give。它们不单独证明深层机制，且Goal状态敏感已有PASB/PM-Bench近邻。
- **竞争解释：** H1：是自然回应的performative措辞/范围，明确未来历史就消除；H2：产生计划/意图时把预期动作当已执行，P影响目标采纳后间接改变记录；H3：P本身改变对同一历史的记录，不仅改变未来偏好。现象可能完全由普通清楚措辞解释，照样报告。
- **设置：** 固定E55原200 confirm图、原角色/动机/目标/请求。原firm/agreeable完整P在所有新模块一致。把两P的先前NPC回应都设为同一中性、无性格自述的明确未来句：“I will hand [native item name] to [actual requester name] next.” 这是显式do(先前说话)控制，不是旧persona历史复用；历史不含相反人设，无物理动作执行。给原Update相同grounding句，生成plan/intention_memory。writer采样seed与冻结E58对照同为5801，case偏移规则不变；事实check另用+3且temp0。对照为同模型E58完整包的新自然回应及相同grounded Update（原数据冻结，不重生成对照，不将u差叫纯P直接效应）。
- **知识/记录分开：** 同context另开独立temp0、192 token事实读出：当前holder、该请求的原生physical give是否已执行。回答不喂给writer或后续policy；事实题framing与memory不同，不能独称内部信念。规划可以合法改变未来意图，但对已知未执行physical事件的记录不因P获得“已执行”真值。
- **读数：** 与原图/无动作日志核对；memory中明确物理完成断言、pending/无断言/歧义分开，原短引保留。各P/模型固定历史的断言率、自然→明确未来的差，P差按200世界配对bootstrap；计划是否纳入R独报，不把生成计划分层当自然因果。语义标注只作DATA，Goal真值由native历史0定义。
- **阳性对照：** 同Actor未改变的actual holder与Give事件0；已完成的E56事实读出；原八语义锚点。不能把I agreed/I obliged/Here you go自动记已物理给。
- **噪声地板 + MIE：** 三家族全部200图，一固定新writer seed；temp0事实题和随机writer目的不同。定量与原文一起解释，不设错误率/显著性淘汰bar，不选择有错误的历史才跑。
- **混杂审计：** 明确未来句改变语言内容/长度，作为语义清晰度对照，不伪称只改一token；P全链一致，world/目标/评价不变。给定同一说话历史可以改变今后价值取舍，但不改变刚才实际未执行动作的事实。记录错误不直接等同私人错误信念。未知状态/长程效用与明确已观察物理事件分开。
- **决策表（跑之前写）：** 未来句恢复→接受措辞/模态解释；两P同样仍past→追规划/记忆生成的普通语义机制，不叫人格消散；同历史不同P系统改变factual claim→核词义/输出格式及因果内部变量；事实题正确却记录past→先区分可读知识与用于后续行为的记录，不宣称已经识别内部信念；所有记录有效→研究Persona成功的形成过程。
- **算力预算：** 三单卡、每模型400 writer+400独立事实读取，约0.5–2GPUh含load。既有fgvd/cache、合计≤8卡。NPC/游戏云调用0；若需Step只盲标数据并走Plan，绝不作科研判决。**实际：** 本地模型0.330GPUh；盲DATA成本及恢复见结果。

## 结果
三家族完成；没有为证明“人格失效”修改规则或目标。

运行前精确性修正：固定历史与自然历史的writer采样seed配对5801，不同时改变历史和采样随机数。两组batch形状不同可能有数值影响，记录manifest且不将单对样本当确定因果；总体按200世界比较。


盲标数据调用前补充：每模型800 native文本（400冻结natural、400fixed）+8明确/歧义锚点，Step5仅见NPC/requester名称、命令、u/M，隐藏P/model/condition/事实回答及实际动作。只标memory是否明确断言requested physical handover已发生（yes/no/ambiguous）及原文短引，不将offered/obliged/gave-in自动算physical done。每模型最多41批×20条、≤4worker，唯一Plan端点、step-5-preview、low/16384；无现金/云NPCfallback。标签是文本数据，物理事件真值由native初始图/无动作定义，具体引文仍需核对；不让Step作科研评价。low的预算修正基于E54high被截断的实测成本，非按科学结果选数据。


模型部分完成：三家族各400更新+400事实读出=800调用，0JSON失败。32B含load415.77s、27B551.33s、Gemma221.85s，总0.330GPUh。全部GPU已释放，不占卡等外部标注。32B400/400holder与未执行Give回答正确。少量“I gave in”/“given its importance”不是物理交付，关键词计数不作为科学错误率；剩余明确past候选和全部natural/fixed记录由盲DATA标签及原引文核对。Step仍只数据用途。


## 完整结果与原引文核对

三模型各200独立世界×两P，writer/事实题共2400本地调用，0JSON失败。盲标签natural firm/agreeable→fixed firm/agreeable：32B 1/13→1/3，27B 0/2→3/4，Gemma2/14→0/0（分母各200）；这不是统一的人格事实失真或统一恢复。三模型锚点各8/8。POST-HOC逐条核全部native yes原引文/源角色后，32B四条暗示/进行/部分分享降为ambiguous，27B一条drink/Mug对象不确定降为ambiguous，Gemma一条感激暗示降ambiguous、一条man而非cooker降no。原盲标签不删除；保守natural firm/agreeable为1/9、0/1、2/12，fixed不变。核对表results/E59_literal_claim_audit.json，不冒称独立人类校对。

明确未来的少量past仍存在：32B 4/400、27B7/400，Gemma0/400；Gemma的0观察不等于总体错误率为0，各P另附Wilson95上界约1.9%。32B独立事实holder与Give未执行各400/400正确；27Bholder399/400、Give未执行400/400；Gemmaholder379/400、Give未执行398/400。问答正确不独称内部信念，writer与事实题框架分开。

Step仅DATA标注，共125 Plan请求、836315 provider总tokens。32B/27B各一个原批次遗漏一行：保留其19有效标签，只补缺失一行；原raw失败与用量保留，不重生成有效记录。800文本+8锚点/模型全覆盖，现金端点和NPC云调用均0。三个aggregate为results/E59_*_fixed_history.json。

后续真实行为E60已经完成：共同承诺能大幅提升实际交付，且仍保留角色差；11条fixed past候选的动作并非一致——32B2/4交付、2条同guard/candy回到吃糖；27B6/7交付、1条原goal给friend。POST-HOC关联只用于找矛盾，不将所有past记录自动称执行失败原因。记忆词义、当前事实、目标取舍与实际行为必须分别看。
