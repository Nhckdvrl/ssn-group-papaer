# HAMLET：私有角色目标、公共剧情与行动裁决

- 来源：[ICLR2026全文／arXiv v5](https://arxiv.org/abs/2507.15518v5)、[作者仓库](https://github.com/Tsumugii24/HAMLET)。PDF `/tmp/npc_hamlet.pdf`；checked main pin `bb2c09e9fdbc2dfc3032da8f11ac75cf97ca87cf`。
- 阅读范围：正文§3–5、主表、附录D的PAD、G的评价校准／latency、I的Advancer消融、J提示入口；未逐个看全部100topic或训练样例，未运行推理。

## 论文事实

离线产生角色／剧情blueprint，在线actor同时依据公共point flag和每act更新的私有目标。PAD融合persona、memory、goal、relationships及外部事件，选择快／慢／静默／动作路径。physical prop动作由narrator按状态与规则判定，再广播结果；这不同于独立确定性引擎的物品转移或合法动作判定，但不能据此否认戏剧评价的用途。

评价含100cases（50文学／50自定义），主干GPT-4o；PAD和HAMLETJudge使用人工标注训练，并有IAA与留出人类评分一致性核对。作者已有raw prompting／w/o PAD／reviewer及Advancer消融。附录I的w/o Advancer结果Table13为68.1%，同段叙述68.7%，仅记录原文不一致，未重算。论文已明确人物因风险／安全约束而不执行剧情动作，以及强公共推进指令改变这一情况；“NPC不跟剧情走”或“人物／剧情可能冲突”不是我们首次发现。

## 源代码事实／未核对

该pin的`git ls-tree -r HEAD`只有README与poster PNG，`ls-remote --heads`仅main。README称official implementation，但目前没有可读的PAD／narrator／runner实现。源码缺口只限制本次代码级审计与复现，不成为创新或自动去留理由；未来若发布代码再对照动作状态协议。

## 解释与定位

人物自主目标、动态goal更新、外部剧情推动和目标冲突已有强近邻。E35／E44须继续区分合理重排、上下文信息与独立引擎执行，不能用单个离开讲座的例子重新包装这些命题。角色理由不等于完整后果；这一通用区分也不是新贡献。
