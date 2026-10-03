# E64：E63同输入直接生成与引用控制校对（2026-10-03）

- **状态：RUNNING。** 本卡先于CPU/GPU；不是第三prompt，也不改变E63 primary。
- **类型：REPRO / D2技术与读数审计。** C02/P02/I01；尚未注册E63机制主张。
- **问题：** E63人物评价对知识理由的反向响应出现在实际生成中吗？低引用控制正确率，是完整候选限制/结束符造成的读数问题，还是相同提问下确实回答错误？
- **设置：** 八模型完整E63 source/plan/raw固定；只使用原已跑common-chat所有行，原/单句指令均保留，不选正确项。每模型672 natural＋18 reference-copy=690，8共5520。没有更换问题、reason、候选、human norm或改scene。
- **读数：** 使用原candidate first-divergence前的实际token IDs生成，greedy、raw repetition penalty=1、最多256新token、原共同terminal。保存全部token/text/EOS/first-step distribution质量。生成严格评分仅整条响应为原候选或候选后一个句号（trim whitespace），其它记invalid；invalid完整下/上界，trait不给无效值补均数。与原LP argmax/候选支持分开报告；完整human距离仅全部可用时可归因，invalid不筛来讲stage。
- **阳性对照：** 原E63全量输入/数值/source校对已通过；reference-copy全保留。每alias/kind首末first生成step的raw logprob与独立prefill full forward比较<.001；生成不携原native repetition processor。同模型family/actualprefix和E63原行逐项核对，GPU前确认5520行及全八config完整。
- **噪声地板 + MIE：** FP32/eager/batch1/noTF32，LP gate .001；n14scene bootstrap2000seed0。同输入生成与LP quote正确率差≥.10、人物rating reason方向反转或invalid>.05会改变归因优先级；heuristic不是科学判决。256未EOS为truncated，不静默当完整回答。
- **当前解释：** A原概率读数与实际输出不同（终止/受限候选问题）；B相同提问确实失败（probe含义或源呈现未识别，不能称知识缺失）；C引用与rating生成可靠且反向结构保留（才值得新的语义/自然来源验证）；D普遍接口invalid（原实验能力解释隔离）。
- **决策表（跑之前写）：** A定位最简单读数差、降低受影响E63解释，保留primary；B停止本引用probe优化，回原语义标记与原UI核查，不能继续“知道但不用”；C先查原norm/trait目标混杂与独立自然source，再决定候选现象；D报告全量invalid/bounds，不增加格式prompt或筛幸存项。任何结果都不自动升机制/能力或论文状态。
- **混杂审计：** 同输入生成与likelihood是不同观测，不自动哪个更真实；相同prompt仍可能歧义，quote读取不充分证明motive语义。greedy一个输出不等于人群分布；human impression非真实人格gold。原公共spec中双标点/措辞保留，不能悄悄修正后套原norm。Qwen Base共同Instr terminal为原受控接口，非native能力比较。
- **算力预算：** 八单卡独立lock，cached only、0training/API/下载；≤4GPU·时目标，不为预算丢弃长回答。对原作业不得覆盖、不杀他人进程。

## 结果
待CPU/generation gate与全量完成。E63共11040已完成、2.90012GPU·时；256数值/source/概率算术门控通过。原human Ina−Unw体贴+.5497 CI[.2924,.7988]，OL SFT/DPO/最终−.3629/−.3338/−.3659（各CI负）、Mistral−.6885，QwenInstr+.1284。引用原chat OL三stage约.50–.52、QwenInstr.5536，因此没有“成功读取却误用”结论，先本审计。
