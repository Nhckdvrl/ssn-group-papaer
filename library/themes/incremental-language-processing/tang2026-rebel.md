# Rewarding Beliefs, Not Actions: Consistency-Guided Credit Assignment for Long-Horizon Agents（作者v1，2026-05，接收未核对）

`[证据级别：主文精读＋关键附录]` [arXiv2605.20061v1](https://arxiv.org/abs/2605.20061v1)，NUDT/IGDL/Xiamen；25p PDF SHA2e06429dac587aefd64cd38c2455d4584b346da587334717ef8707b77d2d6ab0。

1. **论文形态：** state-content监督＋训练分组／credit方法。
2. **背景与压力：** episode RL奖励晚，observation-hash分组在部分可观测时把不同state混在一起。将生成分成belief/think/action，belief predicates由后续观察检验，pending buffer处理晚证据，belief-anchor分组提供step优势。
3. **改变的前提：** 内容credit不一定需要外部teacher逐步打分，可用可观测谓词及动作后反馈；但要求能定义哪些predicates可检验及验证过程的可靠性。
4. **idea来源（RECONSTRUCTED）：** 从GiGPO step grouping失配→在决策的语义近邻而非观察哈希上分组→用迟到可验证反馈修正中间state→episode＋step优势。主要新研究动作是分组对象与dense信号的耦合，不是首次有belief或RL。
5. **最近邻距离：** GiGPO、GRPO/PRM、POMDP-state、belief-world-model／memory。作者区分二值symbolic belief而非Bayes完整posterior，这是可借的构念诚实边界。I07不能把它与ABBEL的字面重建视为一个reward。
6. **实验：** 一个Qwen2.5-1.5B、ALFWorld128 heldout／WebShop，三seed；SFT390/500 trajectories、3epochs、再RL100iterations；baseline150iter。主表SR93.2±4.1／75.1±2.7，GiGPO两variant各域真正最强不同，不能统一称w/o std：ALFWorld w/std86.7高于w/o86.1。WebShop Score79.8低于GiGPO83.5，但SR较高，完整指标留。
7. **方法与理论边界：** main consistency先声明未observable reward undefined，AppF使用max(1,maskcount)即0；pending集合公式只存bt,k=1，负信念如何延迟校对/输出unconfirmed到binary的映射未代码核对。验证还应处理动作导致state改变，不能照搬bt与ot+1相等判错。理论P1需观测验证soundness/有限delay，未证明实际学习会收敛；P2 return对不同action差距≤LR×belief drift是很强假设，完美belief会使action收益差为0，不能视为一般POMDPvariance定理。
8. **资料scope及校对：** 已读Main1–5 pp1–9全，AppA–F pp14–22全，25页余case23–25与代码未全读；figure2/3已文字核，图表视觉未全检。AppALFWorld prompt竟为WebShop式product_id／shopping-phase schema，具体运行prompt未核。main汇总93.2与ablation96.9／FigGRPO60.9而主表72.8属于不同scope，不能拼成同一种增量；正文35iteration与fig约45不统一，2.1x应带scope。SFT-only弱不能单独证明只学format。以上不是桌面否定方法，只限定借鉴。
9. **对我们／可迁移动作：** 区分state formation、checkability、credit传播、后续action；将晚证据归到原生成predicate是有后果的操作。I07目前有观察表达改变重建reward排序，未证明其它一致性reward也错，尤其它用显式谓词verification。因此下一Belief-R先测能力与reconstruction是否失配，不为了凑更大scope把本工作与旧方法全判失败。若要迁移到真实agent，应核实际parser/verifier和动态state，而不只改prompt或报观察词袋相似度。

**2026-10-08 selected code补读（不新增MAIN计数）：** GitHub10f0d2eee4edf2486f32ac9e0c14a85386767e2e，9selected文件与SHA外置。ALFWorld tracker1–705、WebShop385–551、env_manager279–351／506–554、rollout383–432、core_rebel87–236／576–712、实际ALF RL prompt27–121已读；其它download仅关键词定位、不假装全仓精读。当前code由累积regex观察state／task-phase／next预测keyword／format四信号组成，非原文单一binary/pending谓词公式的逐字实现；selected段未见pending buffer不等于全仓不存在。其ALF prompt正确物体schema，论文ALF prompt复制WebShop疑点在当前代码不成立。env.step先更新tracker再给先生成belief的state分，是E94测的具体对象；r_pred是keyword/bigram，negation词被排除，不能称完整语义verifier。默认launch grouping gt_phase、cumulative state和分支advantage与主文版本范围不可混；episode reward调用注释/当前rollout对env-only约定不同，尚未核ray_trainer完整调用，故不宣告训练bug。E94全公开transition只证明当前选定接口参照偏好，不证伪论文RL数字；主要参照遗漏／时间与parser，不能叫一般belief reward有错。
