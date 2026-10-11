# E129 首评分前独立设计审阅

2026-10-12；对应 C23/C24、I04、P17。本记录为卡片与识别范围审计，不是源码/token/实际mask或原始结果封存。E128八批raw与report已独立封完；E129当前0科学评分。未运行GPU、未修改科学卡/源码/claims、未改变状态或增加矩阵。

审阅卡片快照SHA `cc4e07015d49c3f138460ef12f69510a10806dd2805df1deaf6b8c3d38cacac4`。

当前设计可以进入既定CPU实现核对；未发现需要更换核心对比的实质设计错误。可支持的阳性对象是：在同名B选择块、新输入尚未到达、recipient私人历史保留的条件下，移植的完整多层Cue能否携带Source条件的criterion×code功能信息。它检验固定Source群地址或一条共同输出方向的受限解释；无法把一般上下文化检索policy与独立规则执行彻底分开。

- Cue准备可读两Source，避免oracle mask替模型预先选B。private形成隔离，body的own主图只读同一个recipient B历史、Cue及HEAD；CueA辅助控制在同recipient B位置/body图部署。这是控制共同task信号的合适比较，前提是实现实际保留所有recipient demo K/V、不让另一个donor token成为body的旁路。
- 四donor criterion×code与两个same-code recipient均冻结；B评论双射应保持输入多重集与labelstream，名字、词集、Cue长度和global位置必须真实token匹配。完整8query的四格、私人方向、native early/late、纯instruction、single冲突4query与已有阳性/数值地板已写明。当前64接口/17prefix/8Cue准备是计划数，尚未从源码或CPU文件验证。
- 先每recipient/context计算det，再两个recipient等权/context bootstrap，避免将平均矩阵det替代非线性目标。det(M_CueB)和det(M_CueB−M_CueA)同时保留，能够避免仅两rank-one矩阵相减就冒称CueB自身具有两criterion方向。例如MB=[[1,0],[1,0]]、MA=[[0,1],[0,−1]]各det0，差矩阵det2；第一个co-primary会保留这个失败。正确Food/Service行方向及实际功能也必须同时看：两行一起反向仍可能有正det。
- 功能矩阵的非共线不等于latent表示rank≥2或新binding ID。一个标量状态加非线性读出也可产生非共线功能响应；whole-layer/whole-block K/V可同时改变任务内容、检索权重和后续校准。卡已保留这些边界，不需要为完整逆向增加head/layer资格测试。

有两处解释需要保持严格。第一，CueA/B名字不同，B-world代码差能消掉**加性、world不变的词法主效应**，不能保证名字×world非线性交互消失；这个交互可能正是Source条件效应，不能当成被完全匹配的词法路径。第二，同名token与位置不代表上下文化“地址”固定；若阳性，应排除的是固定、与donor任务无关的地址或共同功能方向，而非所有身份绑定/任务条件检索模型。Source-only图零、self交换恒等均是几何/实现控制，不作独立隐藏模块证据。

近邻拥有范围实际核对：

- [Hendel等，2023](https://aclanthology.org/2023.findings-emnlp.624.pdf) §2–5、附录A.1/Fig6已实现输入独立task表征和在冲突recipient demonstrations保留时的任务覆盖。一般criterion/task状态移植与“recipient demos仍在”不能作为首次结果。
- [Just-in-time task representations，v3](https://arxiv.org/html/2509.04466v3) §3、§4.1–4.3已包含局部/分布task状态与query呈现前Q-colon的部分跨token功能转移。因此“新输入之前”本身也不是充分新颖性。此次候选增量是多Source、身份不变、同recipient图的条件选择及criterion×私人约定方向，而非普遍早期task状态。
- [Dong等，ICLR2026](https://proceedings.iclr.cc/paper_files/paper/2026/file/20dcab0f14046a5c6b02b61da9f13229-Paper-Conference.pdf) 摘要/§1、§3理论设置、§4、附录B.4提出representative-demonstration解释并比较单向映射与组合双向bijection。该理论中的rank-one限制不能直接外推到这里完整多层Cue；其通用解释与限制应继续承认。

阅读范围坦率说明：本次完整读E129卡；没有读尚在实现的E129科学源/CPU token或任何新GPU结果。近邻只核上述章节与表，未独立复现它们的代码/训练。既有Feng/Dai/Mixing范围沿用前次独立审计。设计审阅不代表已通过真实mask消费或运输能力核验，不判研究价值、grade或投稿状态。
