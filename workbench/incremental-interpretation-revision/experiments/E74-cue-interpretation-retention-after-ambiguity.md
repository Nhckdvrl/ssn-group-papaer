# E74：原无歧义解释在后续歧义版本中能否保留？（2026-10-07）

- **状态：** DONE；先卡后运行。
- **对应：** C09 / I03，源关系修订与已经提供的正确解释证据的保留；不追E73的标签/掩码网格。
- **问题：** 原无歧义cue单独可读出的正确关系，在后面再给原GP句时能否保持？若保不住，则不能仅归为从未给出/建立明确关系证据。
- **设置：** 原样E72发表数据175对，MVRR24/NPZ89/NPS36/NPVP26，原GP/cue与两原Q/gold，全部四truth模式。配对程序核对gold与Q相同，不改句子/问题，不新增标注，0API。原SHA7d0252850d0e9b06f64f877e7c267bc8fd4a4044eb4c853789e78a28bcf34ce5。三族固定离线manifest、FP32/eager/seed74，pair SHA固定8卡分片。
- **核心对比：** 一个source区内按原顺序拼接GP→CUE或CUE→GP，以换行分开；两顺序完全相同文本multiset/总长度，只变阅读顺序。任务在两句之后，沿用E72单题G2/Yes-No，每个原关系独立问。单GP/单cue逐题baseline完全复用E72已闭合原LP，不重复GPU。新增两order×两Q×175对×三族=2100task/4200候选。不是新合成benchmark，不将重复描述称语义全等；仅共同两问句源支持gold已对齐。
- **读数：** initial/final正确率与正确选项概率；四context各自，以及CUE_GP−CUE、GP_CUE−CUE、CUE_GP−GP_CUE。三族四构式全部五truth层报告，null格保留。按lexical cluster paired bootstrap10000/seed74。未筛baseline正确条目；如以后错误条目个案分析则POST-HOC，不改主map。
- **阳性对照：** 已完成单cue同问题；CPU全token验证混合context的首S前缀和原单S前缀一致，两个Q读同一source前缀；固定首pair两order/两Q整串LP分批与单串差≤.001。
- **噪声地板：** 完整cluster CI；弱cue构式只描述。参考5pp而非自动门槛；不追加长度、任意顺序、prompt网格。
- **混杂审计：** 两句重复部分命题可改变语篇/强调；顺序效应可为一般recency，不自动叫GP机制。单cue强只证明原读数能正确，并不认证内部完整parse；首source前缀计算完全相同是较强的形成入口，但后续是否传播仍需核心因果实验。single与两句长度不同，cue−mixed差不能独自排除一般context负荷；两mixed顺序对比严格同长度。原cue有重排/补词等类型，不按结果筛类型。
- **决策表（跑之前写）：** 两mixed均近cue且明显优于GP→明确关系证据能保留，优先自然partial-repair用途而非继续输入顺序；CUE→GP显著掉回GP而GP→CUE近cue→后续歧义覆盖先前明确证据入口，若三族两构式且强cue，再做最直接跨源消费因果对比；两mixed均差→context负荷/联合源处理竞争，不能叫过时编码；异质→更新构式/模型范围，不硬包装共享叙事。
- **意义/定位：** Slattery2013拥有修订形成/旧解释清理分离，Amouyal有GP vs cue，Prompt Repetition有同输入再读；增量需要发现既有正确解释的稳定保留何时失效，并给关系特定的可预测因果解释，单一般recency不合格。先用一个高信息量对比看现成数据，不为无paper覆盖而迁移题目。
- **算力预算：** ≤2 GPU·h，8独立H20；完整分片/SHA闭合才看效果。外置E74；代码/小map摘要进git。

## 结果

全2100任务/4200候选闭合，实际.108518GPU·h，完整1680格及四truth pattern均已读。

CPU预检（模型效果前）：单换行使部分BPE最后句号token从`.\n\n`变为`.\n`，首句prefix不完全一致，原失败留日志；改用与单source模板相同的双换行，再全量验证。只改输入分隔，不改原句/gold/读数，科学运行尚未开始。

CPU三族全700task/族验证首源前缀相同，科学8分片已启动。输入SHA52412e9222a885eb0b115bdd301767758dc64e837983a62dd824303630037c6a，PID见外置runner-pids-v1.json。

### 数字与自审

- map SHA a2a1f6156cd5e82ce73b6216874c7a3b5805583986bd0c84dc413d95a4fb67dc；8分片，LP仪器最大.0000915527，首源前缀全相同，0API。
- NPZ89 initial p_correct CUE_GP−CUE Q/G/L −10.25 [−16.39,−4.79]/−19.15 [−27.82,−11.00]/−6.84 [−12.33,−1.33]pp；GP_CUE−CUE −10.04 [−20.23,.01]/−39.89 [−49.91,−29.92]/−15.88 [−22.44,−9.71]。cue最后并没有统一最好。两个mixed间CUE_GP−GP_CUE −.21CI含0/+20.74 [11.56,30.42]/+9.03 [3.66,14.43]。不能叫“最新歧义覆盖正确解释”的共同recency规律。
- NPZ final正确率Q/G两mixed100%，L93.26/94.38 vscue96.63；概率L CUE_GP−CUE−3.92 [−7.36,−.09]小损伤，原cue整体初始概率56.70/68.37/71.95，尚非三族都高cue。No/Yes65 initial CUE_GP−CUE−8.18CI负/−23.75CI负/−6.32CI含0，GP_CUE−CUE−1.19CI含0/−35.51CI负/−14.83CI负，不挑更好order。
- MVRR24 initial CUE_GP−CUE−24.06 [−40.45,−9.04]/−6.09CI含0/−17.86 [−29.47,−8.23]；final大多保持。MVRR YY8初始概率三族降低（CI负），其它模式异质全部保留，不将n8现象升主线。NPS弱cue，L initial提高但final损坏；NPVP G初始两mixed下降、L初始保持/提高，final L cue地板。全CI/[摘要](../results/E74-cue-interpretation-retention-summary.json)，缺失为null。
- 决策执行：mixed context确实不能单凭cue存在保持所有原关系，但顺序不支持简单最后句覆盖；编码时源间相互干扰与作答组合仍竞争。E75一个cross-source消费cut保留Task对两源访问，避免再做措辞/重复网格。C09L1/C06–08L0不变，不认证latent正确解释或合格idea。
