# E102：只评价修订证据的内容credit oracle

- **状态：** DONE；完整注册三族已封版，旧INTERIM版本保留。
- **对应：** I07/P20；E101 Min完整族启发的新决策读数，不替换E96/E101原指标，首结果POST-HOC启发/全三族新分析预注册明示。
- **问题：** 评分对消歧信息有正修订信号，却被原前缀拟合抵消；如果只让内容reward评价修订证据，能否更正确选择更忠实的解释？区分prefix credit cancellation与全程无可靠修订信号。
- **数据：** 原E96冻结50发表GP/cue pair、三当前native writer/selfgrader；同一对原P、同一GP观察目标、原全部tokenLP不改。原T2共识唯一index覆盖50/50，原共同Q双遍T1及裁决Gold，全部Source保留，cap/Gold未知上下界，缺polarity结构NA明示。现成Source不重审、不造新P/Goal。
- **条件：** WHOLE原观察重建sum；REVISION_EVIDENCE从原共识消歧词起的后缀sum（唯一主oracle）；WORD_ONLY仅消歧词分数为预定诊断而非最佳参数挑选。只移除评分加和中的前缀项，不改变解释、模型、target、评分context或任何forward，故是objective干预/证据位置oracle，不是neural parsing修复、现成部署方法或RL训练实验。
- **读数：** 相对原共同Q pattern/fidelity rank的alignment与correct下上界，explicitopposes、tie、REVISION_EVIDENCE−WHOLE配对；原50所有和各MVRR/NPZ/NPS，结构eligible及changed/tie预定诊断，Source→原paircluster10000bootstrap seed102；WHOLE baseline必须逐项等于原E96rawrank。主读数是可解释选择质量，不只报告nats，WORD_ONLY不得事后顶替主suffix。
- **阳性对照：** E101已验证token/offset/word/context/prompt SHA，pre+from=whole；同P对不同region的rank来自完全相同LP，不因为forward条件变化；cue参考的原全分数正对照仍E96保留。
- **噪声地板：** oracle使用真实T2位置；其效应不能冒称自动cue识别或下游训练会变好。scope常有Goldtie，changed诊断提前说明、全NA/cap不删；数据是真实临时语法歧义而非完全空白题。
- **决策表（跑之前写）：** suffix选择质量跨族/ct改善→评价总量会漏掉真实修订信号，是值得追的objective对象；只有WORD改善suffix不行→局部词信号不等于可用内容credit，不能据最佳word偷升；异质或null→改机制范围，不继续cut/window网格。改善存在后再用高信息量功能后果发展，不要求今晚补完整训练论文。
- **算力：** CPU缓存LP/stat，0GPU/0API/0model下载。先完整Min族INTERIM，默认3族主图等E96 blind语义全部封版；不得读部分Source teacher效果。原mean/subset/所有地图不覆盖。

05:59Min完整族INTERIM840panels/map d555d3a25d58cacb73b8da7cc50dbe2c234039ed152fea1779d799a999b0a4c8：fidelity36eligible suffix correct77.78[63.89,91.67]% vswhole50[33.33,66.67]%，paired+27.78[11.11,44.44]pp；alignment增+.5556[.2222,.8889]。所有50 Source pattern correct+21.88[9.38,35.42]pp，MVRR+35.29[11.76,58.82]、NPZ/NPS方向正但diffCI含0。WORD仅诊断不替换suffix。这个objective oracle支持“前缀credit抵消修订证据”，不是完整自动reward方法、latent神经修复或RL训练已改善；其余两个族按同suffix边界/指标待完整盲T1，不加cut grid。

2026-10-08T06:22:28.509912+08:00 完整范围自审：完整三族2520panel，0GPU/API/新P，主map revision-evidence-oracle-map-v1.json SHAcbe92ffae660bae729233093164ce8cf9c135148cbfe1b87b10e3b0e3c417b43。所有50 Source pattern suffix−whole正确选择 Q+10.42[3.13,18.75]/G+8.33[−2.08,20.83]/Min+21.88[9.38,35.42]pp。G总体CI0但NPZ+37.5[12.5,75]pp；Q/Min总体及MVRR支持，NPZ/NPS其余差异不伪造共同显著。唯一固定T2后缀oracle支持更具体prefix cancellation种子，原候选对含cue-source proposal，因此E103必须另测same-original-source8候选可获得性/选择实际后果。
