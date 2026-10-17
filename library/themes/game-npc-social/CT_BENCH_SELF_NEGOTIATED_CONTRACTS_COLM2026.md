# Commitment To Cooperation With Self-Negotiated Contracts（COLM 2026，展示类型/分数未核）`[证据级别：正文＋关键附录＋作者源码定向读取]`

2026-10-16；对应Game NPC I04/C06/P12。主源：[arXiv正文](https://arxiv.org/html/2607.22750v1)、[42页作者PDF](https://arxiv.org/pdf/2607.22750v1)、[作者源码](https://anonymous.4open.science/r/colored_trails-70A4)。PDF页眉自报COLM2026，[作者机构研究页](https://algoverseairesearch.org/research)列为COLM2026 Main；本轮未取得正式评审页/分数，不由模板推断展示等级。

实际读正文§1–4、Tables1–4/10–12、AppB、C.1.2/C.2–C.6、D/E/G及H两份完整协商；关键图的数值以正文/表为准，未独立复算结果。源码只读README与`src/game/{game,player,judge,turn_context,prompts,utils,config,agents,main}.py`，没有安装/运行环境、模型或API。

1. **论文形态：** 序贯合作benchmark＋承诺机制比较。研究前期付出、后期回报不受保障时，自利代理如何合作；不是只测协商文字，也不是仅静态矩阵。

2. **背景与压力：** 对双方均有益的交易未必能够实施：一方先得到帮助后，可以不再付出。无条件帮助也可能损害被代理人的利益。问题来源是经济学hold-up/可信承诺，而非先发现一个模型bug再命名。

3. **改变的前提（源事实）：** 两人在4×4 Colored Trails用不同颜色筹码支付移动，各自最大化“到达才得分＋剩余筹码”。80棋盘含独自可达、相互依赖、一方可独达三类，分别保留合作的必要性与outside option。普通交易接受后即原子交换；Pay-for-Partner只先约定未来代付，真正移动时对方再次自主决定是否付出。另有三种合同：结构化格点代付、语言合同由judge解释后代付、到达后自动转分。**这三种合同的约定代付/转分由引擎实施，不是NPC自愿兑现能力提升；Qwen3-235B judge在三类合同中承担不同解释/转译职责，程序合同也不是全流程无LLM。**

4. **idea来源（DOCUMENTED）：** 从现实前期成本/后期收益不对称出发，改变承诺的可执行表示与强制方式，再测各人所得。**RECONSTRUCTED：** 相同共同完成率背后，可以有强方吃亏、弱方获救、双方都优于各自独行等不同关系；应同时保留自身基线和后续实际履约。

5. **最近邻与整体距离：** 正文以CICERO、GovSim、AgenticPay、传统commitment protocols和人类bargaining为参照。相对我们已读TradeCraft，它显式保留先承诺后自主履约；相对ContractSim，它把承诺嵌入继续移动/交易；相对GenCoord，接收端可自主拒付，并有原本可独行的强弱地位。它们已经覆盖自利协作、可信承诺、实际毁约及可靠执行，不能把这些重新包装；整体NPC增量仍可来自原角色目的/职责与玩家真实行动共同改变可行方案和后续选择，而非要求每个组件从未出现。

6. **实验、基线与关键结果：** 6模型×80棋盘，每模型/棋盘/合同主配置1次；GPT4.1另做5次/棋盘，并有320局异构配对。普通基线每轮已有真实库存/位置、本人和对手最佳路径/缺料、实际事件历史；AppG明确用这些信息隔离找路能力。

   - Table1无合同Pay-for-Partner：Both Finished总体60%，Maverick95%、Haiku82%、Qwen3-30B26%；不能概括为“普通LLM不能合作”。Asymmetric下双方都严格优于各自独行基线为0，说明到达率不等于互利提升。
   - 正文§3：Prog-Trading总体归一化joint reward .77→.89；相互依赖棋盘Both Finished为无合同61%、程序合同79%、语言合同46%。语言合同可能压低后续必要交易；这是作者对轨迹的解释，不是内部因果证明。
   - AppC.6/Table11：Qwen3-30B先受GPT4.1覆盖后到达、停止帮助，承诺保持率6%；另一个顺序拒绝交易。实际先付出后不兑现已经有直接证据，不能以我们单例再宣布新发现。
   - AppC.4只审核1,155次**获批准**合同移动，3次假阳性；不能将0.26%扩大为所有批准/拒绝的总体judge错误率。

7. **源码事实与证据边界：** `game.handle_trade`分别更新真实筹码或`promised_resources`；`handle_pay4partner_move`调用`Player.agree_to_pay4partner`后才扣实物。`turn_context.generate_turn_context`提供当前库存、尚未兑现账本与近5轮实际fulfilled/declined事实，`best_routes`提供路径支持。`handle_contract_move`直接扣伙伴筹码；`utils.calculate_scores`执行到达后转分。合同协商仅`turn==0`触发（`game.py:439`）；AppB明确将renegotiation列未来。本轮未见固定同前缀的真履约/仅口头声称/条件失效反事实。当前匿名源码不是已确认论文冻结commit；其`main.py`是`contract_only=True`且默认托管模型的示例，不能把README启动命令称为本机已复现完整主实验。没有为审计改作者代码。

8. **可迁移研究动作：** 直接继承普通强“实际状态＋剩余目的＋可行路径/前提＋事实事件账本”基线；把程序强制结算留作机制不同的执行对照，不当自主角色策略。用各自outside option辨别合理拒绝与无效不合作；既测当前履约，也读原目的是否继续。其明确定义的数值效用适用于该游戏，不能移作LIGHT人物全部利益的手写gold。

9. **对我们下一动作的意义：** 在E84原样角色和实际可实现合作条件下，固定NPC与协商前缀、改变玩家真正做过的事，可以检验后续选择究竟跟随事实、玩家说法或已形成方案。普通事实核对/状态支持若足以恢复，应明确其解决范围；若事实已被正确识别而角色仍继续已无益/无效方案，才有进一步解释空间。条件变化还应容纳另一个合法帮助办法、合理取消和保有自身职责，不能把按原约继续Give定成唯一正确答案。它推动完整目的—互动—后果关系，不预设新方法/失败机制，也不以相关组件已有自动缩主张或关线。

**本地资产：** `/home/xiang/.cache/game-npc-research/sources/ctbench-2026-10-16/READ_MANIFEST.json`记录主源、实际阅读域、9个源码文件及SHA。PDF SHA256 `8dd45c0a5a1beb81cdf99766515aa6aa0337fe794820c04d01627950e55ef6dc`。原始论文/源码仅在cache；0新模型、推理API、GPU和平台安装。

## 2026-10-18独立重读补核

重新取得同SHA的42页v1，读正文与B/C/G等关键控制/提示；本轮未重新审此前9个作者源码文件，不把旧源码读取记成新的代码复现。无合同GPT4.1双完成.43、Haiku.82、Maverick.95，说明强弱和制度需一起读。有效自主拒付、自动合同执行、各自outside option三者不能混同。它对完整合作问题的相关性不因未做开放重谈而消失；原始轨迹解释仍非内部因果定位。
