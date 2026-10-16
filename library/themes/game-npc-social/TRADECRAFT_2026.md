# TradeCraft: Exploring Theory of Mind in LLM Agents’ Strategic Decision-Making and Communication（2026，匿名未接收稿，分数未公开）`[证据级别：全文＋附录＋项目页＋公开仓库完整文件树]`

2026-10-16；对应 Game NPC I04/C06/P12。读完[主页所链15页PDF](https://tradecraft26.github.io/tradecraft%20(5).pdf)及四篇discussion；目视核Figures1–8、Tables1–2。主页明确为匿名、尚未接收稿；PDF页眉的ICML2026模板不代表接收。[项目主页](https://tradecraft26.github.io/)

1. **论文形态：** 环境＋构念测量＋受控行为分析。重点是显式报告的心智理论（ToM）估值怎样关联实际提案/接受策略，不是人格训练方法。

2. **背景与压力：** 单独会回答ToM问题，不等于会在交互决策中使用对方模型。作者选择持续交易/制作闭环，同时保留可分析的行动与估值；这一整体问题与我们很近。[作者综合讨论](https://tradecraft26.github.io/discussion-overall.html)

3. **改变的前提与实际协议（源事实）：** Minecraft配方风格的回合制库存游戏，非原生Minecraft服务器。双方库存公开，目标配方私有；轮流提出具体offer/request和消息，对方二选一接受/拒绝。接受后引擎立即交换两边库存，随后各自选择制作；先制出自己目标物者获胜。制作阶段允许分数用量，结束向下取整。40个任务保证各目标单独可由合并资源制作，不保证所有目标可同时实现。正文§3.1及附录A完整说明此协议。当前交换是原子结算；跨轮未来回报可以仅是语言承诺，Figure1就用未来材料承诺与抢先获胜展示欺骗。因此不能把该研究归为静态博弈，或声称其中不存在未来承诺/策略变化。[全文§3/附录A](https://tradecraft26.github.io/tradecraft%20(5).pdf)

4. **idea来源（DOCUMENTED）：** 从“ToM自述是否进入决策”出发，把自身估值V0、对对方估值的估计V1、对方如何估计自身的估计V2变成逐轮可记录字段；不指定这些字段应怎样计算提案。**RECONSTRUCTED：** 这是一种让潜在心理解释变为可比较行为特征的研究动作；不能由拟合好直接推出模型内部按相同算式运算。[作者综合讨论](https://tradecraft26.github.io/discussion-overall.html)

5. **最近邻与整体距离：** 作者§2以ToMnet/递归信念模型、Hypothetical Minds、Cicero、Generative Agents、MSCoRe为参照，增量放在可变合成依赖下的显式高阶估值与策略联合测量。相对本仓库已读的GenCoord、ContractSim、Talk-is-Cheap，TradeCraft尤其接近“私人目标＋互换资源＋多步策略＋自述/行为”。这些组成不能再当我们的首创；新增理解应来自NPC的原角色目的与玩家实际行动共同改变合作方案时，强普通系统究竟如何选择并兑现。相关不构成关线或把研究压缩成工具实现差异的理由。

6. **方法、数据与基线：** 实测GPT-4o/o3/o4-mini/GPT-5 medium；只用40任务的前20，每配置每任务一次，共4×3×20＝240局（据协议计算）。同模型对手固定只报V0；处理组分别报V0、V0+V1、V0+V1+V2。普通基线已有跨轮对话记忆、配方查询与当前库存可制作目录，不能假设模型缺少基本规划信息。[实验设置与信念评价](https://tradecraft26.github.io/discussion-belief-calibration.html)

   - V1与对手**自报V0**的归一化KL衡量报告一致性，不是对引擎最优效用/真实心理值的误差；原私人目标由任务给定，逐物0–10价值仍由模型报告。[信念评价](https://tradecraft26.github.io/discussion-belief-calibration.html)
   - 提案两边均用提案者自报V0求和，再拟合offer/request斜率及相关；90%区间按episode bootstrap2000次。高阶提示使4o/o3与o4-mini/GPT-5方向不同。这里的“公平”是自身估值空间的代理，不是双方福利或目标最优性。[提案分析](https://tradecraft26.github.io/discussion-proposal-shift.html)
   - 接受分类器把决策者自报估值按获得/付出聚合，用LBFGS＋参数网格和按episode三折验证。Macro-F1均值±折间标准差如下；是行为预测，不是履约率、胜率或因果解释。[拟合协议与原表](https://tradecraft26.github.io/discussion-decision-utility.html)

   | 模型 | V0 | V0+V1 | V0+V1+V2 |
   |---|---:|---:|---:|
   | GPT-4o | .77±.28 | .94±.09 | 1.00±.00 |
   | o3 | .80±.19 | 1.00±.00 | 1.00±.00 |
   | o4-mini | .74±.18 | .80±.09 | .83±.04 |
   | GPT-5 medium | .74±.24 | .92±.06 | .85±.11 |

7. **证据强度与尚未取得的部分：** 主结果把估值、提案和接受连起来，足以要求我们采用有目标/状态/工具的强基线。它没有报告玩家真履约/仅声称/改条件的匹配反事实，也未量化后续兑现/重谈及任务获胜；作者把胜率、可利用性及规则扰动列为后续方向。不能把拟合系数叫内部机制；本轮未独立复算。附录B引用当前正文没有的Table3及九维评分图，故不把该段评分管线当已展示的主结果。[后续方向](https://tradecraft26.github.io/discussion-overall.html)

   **实际代码资产：** [公开项目仓库](https://github.com/TradeCraft26/TradeCraft26.github.io/tree/6cfdfe3af69966ab1c4fcc27ec56b46786fe3920)，commit `6cfdfe3af69966ab1c4fcc27ec56b46786fe3920`。完整递归树、README和37字节`index.js`只给静态项目页/图/PDF；未取得Flask/MongoDB游戏实现、40任务JSON、agent prompt/runner、原始局或拟合脚本。附录列出的`/tradeCraft/src/...`是路径说明，不是已下载代码。另`TradeCraft (6).pdf`仅一页Figure1，不能当新版全文。当前可复用的是协议与分析认识，不能声称现成可启动benchmark。

8. **可迁移研究动作：** 在完整episode内同时读本人目标、对方信息、提案、实际状态后果；按独立任务聚类而不是把话轮当样本；分别问报告准确、策略改变、本人目标是否实现。使用自身估值拟合解释策略值得借鉴，但不让自报utility替代原世界事实，也不预先把给予/公平当正确。

9. **对我们：** 直接覆盖I04的大块邻域。真正有价值的共同压力是：有自身目的的角色遇到玩家可选择的方案时，如何判断合作、识别实际前提、兑现或改约，并继续保有原角色目的。TradeCraft的原子交换、未来承诺和制作选择提供比较视角；我们的增量必须来自整体的新认识/方法及真实后果，而不是换NPC标签或单加履约字段。本轮只做定位，不改变idea/主张状态，不启动新系统。

**本地阅读证据：** `/home/xiang/.cache/game-npc-research/sources/tradecraft-2026-10-16/READ_MANIFEST.json`记录PDF/网页/完整tree/hash；主PDF SHA256 `9b194ba324f58625553dde0280bc3416dc2bf54353ccc006599c212e8aa96389`。0模型/推理API/GPU；未安装或启动TradeCraft。
