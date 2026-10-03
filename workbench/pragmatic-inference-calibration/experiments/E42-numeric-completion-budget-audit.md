# E42：numeric-completion-budget-audit（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / 仪器校对，有界一次，不作为paper主题
- **对应：** C02/P02
- **问题（一句话）：** E38/E39原5token输出虽可解析为数字，是否其实被截断，后续输出是否会使数字改变或变成带解释的无效回答？
- **设置：** 十个已完成端点/原同prompt同tokenizer/FP32/单sequence/noTF32，唯一改max_new_tokens5→32。选择规则在运行前冻结：原human-matched行中所有numeric-valid但非EOS完成者；每interface×task×verb首个已EOS完成numeric行作sentinel。原invalid不作为“恢复分数”目标；不是全体能力排名，不换prompt。每model保存selected key/SHA/source run config SHA，GPU前CPU对source/完整input parity。
- **读数：** 首5generated IDs与原逐项精确一致；32token输出EOS/strict numeric/原rating是否改变，以及原rating变invalid数量。未EOS或变prose仍不作能力错误。不把选择样本的MAE拿来模型排名。
- **阳性对照：** 原已EOS完成sentinel延预算应保持完整generated IDs/数字；非EOS例首5应保持。任一prefix不同立即gate失败，整个对应model结果只作失败证据，不扩大预算挽救。
- **噪声地板 + MIE：** 无sampling seed，原首末生成重复gate复用；新增首末延预算重复ID一致/LP<.001；材料确定性。任何非EOSnumeric变值/变invalid均使原5token bare推断受到具体降级；无科学MIE。
- **混杂审计：** 选择由原输出完成状态决定，因此是截断诊断、非新原全体性能估计。保持base/instruct完整tokenizer与bare BOS，不能挑有效行做stage ranking。原5token结果永久保留；32仅排除budget解释，不能证明心理能力。固定32到此为止，无继续加budget或prompt。
- **决策表（跑之前写）：** A数字稳定且EOS完成→排除这些行的截断解释，但projection的构念/elicitation仍未消除；B延长变prose或数字变化→标原ratings未识别，不把原差异升级；C32仍未完整→仪器不可用，保留failure；Dprefix/repeat不一致→数值实现失败，隔离，不改阈值。
- **算力预算：** 十端点按八锁独立排队，已下载资产优先，不干扰E41同锁；预计<4GPU·时，主要一个token后EOS，不重复全体样本填卡。真实selected counts见跑前manifest。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
源结果已完成；本卡是在看到原非EOS覆盖后设计的诊断，选择规则与32预算在新运行前冻结。C01/C02仍L0，不作能力贡献。

跑前十端点完整prompt/token gate通过；选入5453行，其中非EOS numeric 5196行。见results/E42-selected-preflight.json。

2026-10-03 全十端点完成：5453 selected rows，5196原nonEOS；全部greedy prefix逐ID一致、LP误差<.001，257 EOS sentinel完整ID/rating不变。原nonEOS中3677延长后变invalid/prose，1519 numeric保持原值，0数字变值；Q3三bare合计2520、Q25Instrbare119、MistralBase914均不能按原短numeric解释；MistralInstr124 invalid。selection不是performance sample，不算新能力分数、不再延预算。见 results/E42-budget-audit-summary.json，原5tokenraw保留；C01/C02仍L0。
