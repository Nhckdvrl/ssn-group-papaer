# E104：语用信念更新中的前后重建credit，是否同样抵消？

- **状态：** DONE；完整三族CPU图已封版，自动E431在任何新统计前更名E104。
- **对应：** I07/P20；E101/E102完整GP图后的跨领域核心追问，0新forward/标注。
- **问题：** GP中的prefix cancellation是否只是临时语法歧义特有？在作者原人类语用suppression任务，评价新条件前半句与then后结果的credit是否同向，移除前缀是否使正确修订更可被选择？不把语用Gold冒称经典逻辑truth。
- **数据：** 原E93全1744 Belief-R原题、原a/b/c、原先验/新观察/goal及作者Gold，全3当前族完整15696候选LP；原完整SHA5477a87d5a03b2382cddc54058b0a9787e35bdeb17d97ecfff83241c2c7ccf41。0Source修改/重审，1744全留；UPDATE1073/MAINTAIN650/先验链接缺21与Gold/modus分层固定，不选择成败题。
- **唯一oracle：** 新观察原条件句唯一词边界then起的后缀（含then，唯一固定cut），WHOLE原全句为baseline，PREFIX仅机制诊断。若无唯一then，位置STRUCTURAL_NA，留全部1744主上下界与覆盖，不用替代cut救数据。只改变评分加和，不改变任何LP/context/候选内容。
- **读数：** WHOLE、SUFFIX选原三候选对作者Gold的准确率上下界（ties取abc最小序，效果前固定）与配对差；UPDATE/MAINTAIN/UNKNOWN_PRIOR、Goldabc、原modus完整分层；更新题额外原Gold候选减原initialGold候选的prefix/suffix/whole margin与整体反向但suffix正的数量。source→原204atomic cluster10000bootstrap seed104，不能混同actual自由输出能力。
- **阳性对照：** SHA复建原reconstruction task/offset；各候选相同target token/offset；PREFIX+SUFFIX=WHOLE；baseline逐项等于E93最大sum选择。原数据为已发表Suppression语用任务，社区Gold沿用，不给现代grader当新Teacher。
- **噪声地板：** 0新随机forward/标签，位置结构oracle不是部署方法；候选Goldc可在经典逻辑上有争论，读数只称作者语用任务的一致性，不混同源真假。NA全保留上下界，任何null/反向原样报告。
- **决策表（跑之前写）：** UPDATE三族prefix反向/suffix正且选择修复→revision credit失配有跨对象预测；GP有效Belief-R不效→当前机制对象限定临时语法歧义，不继续扫描其它cut；若MAINTAIN也同形→通用候选/措辞偏好比修订机制更合适，不能借跨域当证明。目的为探索idea，今晚不硬补训练稿。
- **算力：** CPU缓存LP分解/统计，0GPU/API/模型下载，原tokenizer元数据停卡后仍保留。不会占用别人09:00后卡。

2026-10-08T06:30:06.834009+08:00 全3族5232records/222panels、0GPU/API，map /data1/xiangding/work/incremental-interpretation-revision/E104/belief-r-revision-evidence-map-v1.json SHAaee39d833bdbd7f43c719b85328fb659157d4400d6a51b8c502fb18870d91b4d。全部1744主图SUFFIX−WHOLE lowercorrect Q−7.11[−10.54,−3.66]/G−.22[−4.34,3.92]/Min−12.08[−16.02,−8.14]pp；UPDATE Q−12.72[−16.99,−8.52]/G−.04[−5.08,5.12]/Min−25.12[−29.09,−21.05]pp。Min更新Gold减initial suffix margin−.338[−.376,−.300]且prefix+.415[.325,.506]，和GP方向相反；不能靠少数11.8/20.4/4.6%的局部cancellation例子挽救总体。MAINTAIN Q+5.19[.39,9.94]/G−.70CI0/Min+16.12[9.37,23.09]pp，明确不是通用修订方法。作者语用Gold非经典逻辑truth，保留两位置NA；跨域推广不成立，I07当前机制对象须限定语法歧义的解读credit，不追加别的cut/窗口。

2026-10-08T06:38:57.045221+08:00 E104解释校正（原数字/SHA/条件完整保留）：原条件句唯一then是结构边界，未被认证为引发人类语用suppression的最早证据位置；alternative-cause等关键内容常在antecedent。因此其负结果只排除这次机械consequent-only迁移，不能作为“真正语义修订证据oracle在跨域失败”的反证，也不能声称否定通用prefix cancellation机制。当前跨域机制仍未核对/未建立；不继续扫描cut或事后挑语义位置。这是实验解释限制，不是Source数据错误或重标需求。
