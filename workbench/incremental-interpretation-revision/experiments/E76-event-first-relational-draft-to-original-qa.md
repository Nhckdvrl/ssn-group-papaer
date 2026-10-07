# E76：按主事件先行生成关系草稿，再回答原问题（2026-10-07）

- **状态：** RUNNING；先卡后运行，方法动作探索，不先假设novelty。
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

尚无科学结果。

CPU三族全部356源/3568 FREE QA/族验证prefix；8分片已启动，共1068新草稿、21408后续QA条件。新增EVENT_FIRST生成后再全量token校验，无效果筛选。PID见外置runner-pids-v1.json。
