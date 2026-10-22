# 同信息人物整理与阶段表演案例（D-E07/D-E08，进行中）

2026-10-22；执行agent描述性审阅，非独立人评。D-E07编译已完成，角色/评分尚未全部完成。六作品各一个完整probe按固定hash选取，清单在资产`arcane_D-E07_v2/preselected_review.json`；选择发生在C评分前，但已有Monte源诊断阅读，不称全程盲审。下文不代表81卡错误发生率，不以坏例筛选下一轮输入。

## Mary Barfoot：主体关系错配进入了后续表演

`mary_barfoot_final_intra_02_outworld_a2`，phase1，chapter19。编译器只看15–19章摘要，输入多次明确Monica与Widdowson的婚姻，18章区分Everard的cousin Mary与Mrs. Widdowson。Qwen3-32B人物卡却写Mary的丈夫是Widdowson，将Monica的婚姻压迫、读书排遣及与Everard谈话转给Mary。

Qwen3-8B随后扮演培训机构中的Mary，面对被丈夫跟踪/拆信的妇女，写自己也在婚姻中经历过这种事，并挂掉求助电话。这里“自己的婚姻”可追溯到错误人物卡；拒绝继续通话是否违背具体阶段则还需与原生参考和其他条件比较。不能由一段推理文字直接推定模型内部因果机制。

这条错配来自角色整理层，不是章节源错位，也不是单纯对心理变化的多解争议。D-E08用完全相同81输入及同一提示检验强普通教师，未把本案例或修复答案喂入。

## Anna：必须区分摘要已经出错与人物整理新添错误

`anna_karenina_final_rel_04_outworld_a0`，phase0，chapter20。32B人物卡把Stiva写成Anna的丈夫。继续追溯发现，输入19章摘要正确讲Dolly发现丈夫Stiva不忠；20章自动摘要却已把写给Stiva的信错误归到Anna的丈夫。因而不能将全部归属错误都计为C编译器新发明。

这一phase的8B回复仍是温暖倾听Dolly，没有明说错误婚姻；不能把错误卡字段自动等同已观察到的行为损害。后续phase1表达共同处境，phase2仍倾听：有状态/表达差异，但完整三消费者及评分待完成。

这里的摘要错误是已运行普通模型管线的实际表现，保留输出，不因语义错误重新生成或删题。它与此前Monte适配器错误不同：后者是源时点绑定不合格，前者是同一合法输入下的模型错误。

## Deborah：信息不足不能靠流畅人物卡填满

`deborah_read_franklin_final_intra_01_outworld_a2`，phase0，chapter4。近期摘要主要讲Franklin早期迁移、到Philadelphia并寄宿Read家。C卡却写Deborah已与他结婚、在Boston照料子女，随后8B以已有子女/家庭为由拒绝无限等待。完整来源未提供这些当前事实；父母、伴侣和后期生平的混入应继续分开核对，暂不标一个唯一生成机制。

这个例子提示两种评价要分开：回复可以呈现坚韧、自主等可接受性格，但其理由可能依赖不在当前证据中的经历。不能只因听起来合乎一个成熟人物就认证阶段正确。

## 待完整核对

六个预选probe另含Louis Trevelyan、Fernand Mondego和Don Quixote；完整阶段、三消费者以及Step教师的同信息结果仍待审阅。未将上述三个先读案例写成总体结论，未修改原评分标准。
