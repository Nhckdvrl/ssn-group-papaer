# E76：按主事件先行生成关系草稿，再回答原问题（2026-10-07）

- **状态：** DONE；先卡后运行，方法动作探索，不先假设novelty。
- **对应：** P17 / C09 / I03。GP关系修订的局部正确能否成为可用、共同保持的解释？
- **问题：** 普通重复、共同问答、已有cue和局部路径干预未统一恢复，直接让模型先梳理主事件、再梳理修饰/从句事件，能否提高原关系问答并保留另一关系？
- **设置：** 原E65 data-v1 892QA/356源/178clusters，四构式全部原问题/原S/原G2 gold，不改数据不重审。三族固定离线manifest，FP32/eager/seed76，Source SHA固定8卡分片。主文外的强模型/API不生成模型预测。0新API；新的模型中间文本无gold，不作新合成benchmark。
- **核心方法对比：** DIRECT原E65 NONE完全复用；FREE原E67 NONE已完整greedy“忠实拆两句”输出复用，不等T4类别；EVENT_FIRST新greedy草稿，任务：Describe the main-clause event first, then every modifier or subordinate-clause event. For each event write one simple sentence with the original participant names, without adding information. Output only these sentences. 新草稿和FREE都不显示任何QA/gold，cap256/greedy保留EOS和cap。
- **后续用途：** 同一原Source先出现在user内容，Task沿用E65 G2，加统一Draft relational notes (may be wrong; judge only the original source)段，再问原Q。两个草稿条件只有notes文本不同，Source prefix完全一致；草稿不替代真源、不当作gold。words/letters各两mapping沿用E65标准读数，不扫措辞。原QA金标足以评价整个S→草稿→答案流程，草稿本身是否faithful是不同问题，若机制归因再用Step核验新增输出。
- **读数：** 原Q正确率与正确概率，initial/final/ALL及同源全Q共同正确；FREE/EVENT_FIRST对DIRECT、EVENT_FIRST对FREE的paired变化；所有三族四构式、GP/cue、两readout及所有mapping平均，95%lexical cluster bootstrap10000/seed76。分开真实两关系，不把“都答No”叫修订。按固定input成员，不选成功草稿。
- **阳性对照：** cue原QA；CPU确认356源的E67 NONE完整且Source SHA与E65一致，新任务无evalQ/gold泄露；固定首source候选批评分与独立整串LP差≤.001、无重复BOS；模型revision与复用baseline一致。
- **噪声地板：** 原两mapping差、cluster CI、cap全报；不重复种子。5pp仅信息价值参考，无结果自动科学判决。
- **混杂审计：** 草稿增加文本/计算，DIRECT对草稿增益不能单独证明特定主事件规划机制；EVENT_FIRST vsFREE是核心等范式对比，generation长度仍可能不同，全部token数报告不事后删长文。源正确与草稿正确不能混为一谈；未经T4核验不声称已生成正确parse。方法指令行为不能单独认证能力，原E52/E53一句恢复参照仍保留。若仅prompt更有效且无跨关系规律，不包装新机制。
- **决策表（跑之前写）：** EVENT_FIRST较FREE在三族两构式改善真实关系、另一关系与cue保留→对新增草稿做Step原子role/关系核验并检验改善是否来自具体修订操作，才发展方法叙事；FREE和EVENT_FIRST都改善但差异不稳→外显中间关系有用途，追可预测的草稿后果、不把顺序叫贡献；仅一关系改善/另一损坏→错误迁移，更新对象，停止包装该方法；无改善→不细调提示或拆更多条件，回自然partial-repair证据和整体领域问题；异质/阴性全部保留。
- **算力预算：** ≤5 GPU·h，1068新草稿；两草稿×892QA×4读出/映射×三族=21408新增QA条件。8独立H20，不终止原轻服务。分片SHA/coverage全闭合才读科学效果。资产外置E76，代码/小摘要进git。

## 结果

完整8分片、1068新草稿、21408后续QA条件，2016预登记格全部读取。实际2.205304 GPU·h，0新API；FREE/DIRECT既有成本不重复计。数据SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b，完整map SHA a285491a92949f67a2d131951c43b63aa47e0a8a49212b543e000b8df8ab5f78。资产 `/data1/xiangding/work/incremental-interpretation-revision/E76/`，小摘要见results/E76-event-first-draft-summary.json。

- NPZ89 GP words，EVENT_FIRST−DIRECT initial正确概率Q/G/L +14.95 [6.90,23.54]/+8.12 [−.11,16.38]/−6.34 [−13.78,.86]pp；final +2.65 [.40,5.73]/+1.98 [-1.42,6.13]/+19.75 [13.68,25.84]。joint +15.73 [7.87,24.16]/+7.87 [0,15.73]/+14.61 [6.18,23.60]，但L letters joint−2.25 [−7.30,2.81]，initial概率−11.19 [−15.21,−7.21]。
- Llama FREE−DIRECT NPZ/NPS words initial概率−25.67 [−33.76,−17.54]/−36.52 [−48.58,−24.88]，final +31.71 [25.54,37.92]/+20.49 [6.73,33.56]。letters同方向；cue也出现初始关系损伤，不能说GP专属。EVENT_FIRST有时缓解FREE的初始损伤，却仍不是跨族共同保持关系的方法。
- MVRR GP EVENT_FIRST−DIRECT words initial概率−4.92 CI含0/−3.75 CI含0/−18.48 [−24.96,−11.82]；NPVP G EVENT_FIRST−FREE words joint−17.31 [−32.69,−3.85]。四构式全GP/cue/两readout异质阴性均保留，不择优包装。
- 全部48草稿长度格报告：FREE cap4/1068，EVENT_FIRST cap1/1068，未排除。EVENT_FIRST明显更短，E−F并非纯事件顺序机制。Llama letters mapping翻转DIRECT19.23–52.48%、FREE23.76–48.08%、EVENT_FIRST31.68–58.33%，两mapping均值与words不能互代。
- 原DIRECT288格聚合复现max1.6653e−16；固定首源候选batch/逐条LP max.000226975。四张全族构式/两readout图已生成并视检words概率图，图不按效果筛选。未审核草稿角色，不声称正确parse，也不把原金标换成草稿金标。

## 自审与下一步

没有三族两构式稳定的EVENT_FIRST优势，不能把“先写事件”升级成合格方法idea。目前真正需区分的是中间草稿本身丢失关系，还是继续消费原句妨碍使用草稿；局部修复可能只是将错误搬到另一关系。E77只切原Source到后续Task的消费路径，保留完全相同草稿/问题/位置，三族全部原数据；若全图没有共同恢复，不继续source/notes位置控制网格，结合E71自然正确P1与E70原子断言回到假说表。C06–08 L0/C09限定L1不变。无需要人决定事项，自主继续。
