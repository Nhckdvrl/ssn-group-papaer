# E37：同人物、同状态的角色编辑功能几何（2026-10-14）

- **状态：** DONE；全部30／100／300轮、三个状态银行及身份对照完成。
- **类型：** EXPLORE；由E36实际现象延伸，自由探索，不设科学淘汰bar。
- **对应：** I02／P06；E33、E36。
- **问题：** 等义改写与真正改变作者利益的文本编辑，在相同人物anchor、相同latent角度和游戏state下，怎样影响动作与原生收益方向？这些关系为何随人物和训练阶段改变？
- **来源：** E36把C_low作为anchor，但421／441的原canonical不是low，且最初C五人物与alias百人物汇总不完全配对。新观察保持原结果，直接做配对，而非因不一致舍弃线索。
- **设置：** 原held100、五原型×20职业。原C_low→high、high→low、mid→low/high，共120单属性编辑；作者模板100/100逐字重建，其余四BF／年龄／职业／body／preferred_actions保持原样。Qwen3-Embedding-.6B只编码120编辑与100canonical数值重复；原canonical／reverse来自E26正确pool。原文、目标C、token长度和全部编码保存，不调用生成API。
- **功能比较：** 三训练seed各30/100/300检查点。每pair在canonical anchor取C编辑及reverse方向；共同角度为两policy两方向原角度之最小值，各取一半／全部，确保不外推原角度。沿球面路径直接输入原actor，观察原E32相同states。16随机切方向辅助理解整体gain，方向间比较本身共享anchor／幅度。120pair中mid人物重复使用state，按persona／原型／职业分列，不能作120独立人物。
- **原生收益：** 用原source _apply_action产生每state的20合法动作即时收益向量，分别用原C与目标C，身体／prefs不改；包括style和social全部项。由真实obs恢复该收益函数使用的位置／自身需求／同伴BF配置。先与原训练真实reward核对实现。报告两策略×两目标四格expected即时收益及相对方向，绝不把它替代长期战略效用；后者继续使用E34完整native episodes，并据观察追加有信息量的真实轨迹。
- **读数：** 原始／共同角度动作JS、C／alias响应比、random gain、全部四格即时收益、逐state／persona／occupation／train seed分布。JS使用float64计算并记录数值重复。探索功能几何是否能解释并预测原生目标控制，不只追求分离得更远。
- **阳性对照：** canonical编码数值重复；原phi注入原actor与源logits同一；路径端点／范数；收益重建与原训练动作实际reward对应。不触及科学价值判决。
- **噪声地板 + MIE：** 记录浮点差、随机方向变异及三seed差异；不设MIE、通过率或2×noise筛选。
- **混杂审计：** source的BF→style是作者定义，不称独立心理效度；即时R不是长期回报；latent路径不保证文本可达；三seed短／长阶段全部保留，不挑最好。PCSP已有semantic projection，PERSONA已有组合向量，Persona Vectors in Games已有策略steering，DAIL／Projection Heads已有绑定／几何；本次围绕实际功能路径与game-defined利益解释，不把定位当否定结论。
- **决策表（跑之前写）：** 读取所有现象后更新解释和预测；不按预定bar舍弃。若只由整体gain／距离解释，继续理解它为何形成；若出现人物／state相关差异，查真实动作与原收益，并用新场景或新职业验证具体解释。
- **算力预算：** GPU1单空闲卡编码约数分钟，与GPU0 NPC episode独立，本项目白天总≤8卡；CPU功能测量和source奖励核对数分钟，无额外RL训练／付费API，复用fgvd/deps和模型缓存，raw既有cache/runs/e37_*。

## 结果
尚未运行。

功能测量前的执行细节补充：即时source收益分析统一改用E34 seed42/No30的fresh-AEC原生states（34011/12/13，cycles0/20/100/199），同一批状态用于所有policy／角度，保留E36旧状态结果。这样source收益对应真实逐actor观察，避免E25旧cycle快照与后续actor实际世界的时序差。除25600训练transitions核对外，将用该native数据全部60000实际动作的累计reward再核对重建。此时尚未计算E37功能读数。

## 首批功能读数（30／100轮，保留三seed）

100人物／120编辑，每pair共3世界×4真实逐actor状态；60000原生动作累计reward逐episode重建，300/300与原引擎完全相同。功能测量计算30轮6.03秒、100轮7.47秒。共同幅度同时匹配No／Full与C／alias。

30轮Full的alias动作JS为.00266／.00209／.00379，C编辑为.00192／.00139／.00155；100轮对应alias .00636／.00233／.00369，C .00473／.00243／.00141。动作敏感度不能替代利益方向：100轮Full C编辑即时reward DD为−.00132／−.000097／+.00137，且不同原型和seed差异明显。DD是四格相对方向，不是总效用改善。

这批结果把“等义稳健性、真正角色控制、原生利益方向”三个读数分开了：Full较小的动作变化并不总对应较弱或较强的利益适应。继续对照完整训练与实际轨迹解释这些差异，不按任何比例淘汰。全部四格／逐人物结果见results/E37_matched_functional_i30.json、E37_matched_functional_i100.json；原始probabilities／状态／reward vectors在cache/runs/e37_matched_i{30,100}/。

POST-HOC构念分析（不改原读数）：查看源reward vectors后发现，C编辑并不总改变当前state的收益最优行动。1440个pair-state中446个无共同即时最优动作；五原型分别115/240、18/480、73/240、0/240、240/240。中C原型两种编辑故480而非240。这个差异提示应先看利益结构允许/需要哪些不同选择，再解释策略是否变动；不是用“应变/不应变”门槛淘汰角色，也不是长期目标的唯一真值。训练20个BF组合的截距+5轴线性设计满秩6，不能用“线性不可识别”解释全部编辑差异；非线性组合/语义词频/行动反馈仍未排除。后续对现有arrays按原reward机会和原型分解，并保留全部状态。

### 额外竞争解释：固定旧状态与当前政策的分布差异（运行前补充）
原E37/E39固定No30状态以保证跨政策可比，但100轮本人的native需求/行动分布已不同。不能把旧状态上的利益方向直接推成当前episode能力。现在用已经完成的E34 seed42/100轮No和Full各自原生fresh-AEC states，重做100轮六政策的完全相同E37读数；每个state bank保持角色／cohort／world来源明确，照常重建全部60000实际动作reward，不新增rollout/训练。两个bank全部保留：若方向随状态分布改变，这是实质解释；若都存在，继续查形成路径，均不作价值bar。30轮/旧No30及E39原结果不覆盖。

300轮完整预算后的同一状态分布控制：在原No30固定bank中Full三seed的C功能方向均更强，现将相同读数也应用于已有seed42的No300／Full300本人原生state bank。仍保留所有已注册政策与读数，不用有利state bank替换原结果；目的是确认完整训练的正面功能形成与状态机会的关系。

运行前补充（利益相同的身份编辑，衔接I03/P10）：源码train400的big_five/decay_modifiers/preferred_actions组合精确20类、每类20身份；held100也按五配置各20个年龄/职业文本。使用同一held角色与原native状态，第三种direction为同功能配置的另一真实身份输入，和alias/C-edit一起匹配latent幅度；目标/身体/世界不变。选donor为同配置按ID排序循环下一个，规则在看其结果前固定，不选低损失donor。报告natural与matched响应、原目标expected reward变化与C利益方向，保留多个合理style行为，不把身份变化要求为“动作必须一致”。仅固定300完整policy三个seed两route，分别报告原state、No300/Full300state；既有E37重建60000native reward资格沿用。该控制区分全局ID敏感、表述敏感和实际利益编辑，不称功能等价测量本身首创，也不自设bar。
