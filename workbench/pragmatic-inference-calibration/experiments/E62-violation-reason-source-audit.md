# E62：跨到relevance/informativeness的原理由操控资产（2026-10-03）

- **状态：DONE。** 本卡先于source metadata/CPU统计，0GPU预测。
- **类型：REPRO / D1。** C02/P02/I01；为E61的六precision scenes寻找独立可验证来源，未押结果方向。
- **问题：** Beltrama/Papafragou2023原reason manipulation能否固定待评价的交际选择并独立区分inability/unwillingness，与原人类Warmth/Competence规范配对？不把paper示例补成完整素材。
- **读数：** 原paper/stimuli/raw/R版本与hash；独立scene/condition/rater计数，reason改变何种信息/哪些字串；原human key效果可执行parity及缺失；不生成新gold，不使用闭源API。
- **阳性对照：** publisher/OSF source一致，ID联接与response scale、exclusions全量核对；真实控制与原scene版本保留。不能因为release不理想就先编辑其句子做finding。
- **噪声地板 + MIE：** source hash/计数精确；模型0次，当前不写效应CI。原R舍入parity按原precision；匹配失败明确未识别。
- **混杂审计：** 未读完整原文前不假定reason同utterance、knowledge等同能力或social评估等同intent。读原全文/讨论/原filter，条件内与跨scene比较分开。
- **决策表（跑之前写）：** A原人类与理由对照可匹配→原协议驻留，再根据E61证据另写跨来源pilot；Breason同时换utterance或difficulty→保留局限，重新设计固定对象干预，不偷换因果；C资产缺失→记录未核对，用可访问原public source继续，不复制paper数字冒充复现；D已有人类/LLM直接近邻→定位其层claim，重新判断实质增量，不自动kill/缩题。
- **算力预算：** CPU/公开direct-only数据≤100MB，0新权重/训练/API judge；8卡继续E61，不为本卡占GPU。

## 结果
公开OSF三套材料、fillers、Rev CSV和R取得；作者站41页正文/讨论读完，图像未独立审。公开Rev总4192行、retained86/93/83人、共享16scene，每scene cell16–30人。人/项目唯一、四ratings1–7与作者Avg.Comp/Avg.Warmth精确匹配；双算术均值差<1e−12。完整norm/count/hash见[结果](../results/E62-violation-source-audit.json)。原lmer/p值尚未复现，排除者/理解题响应不在release，不能重新审其筛人。

有真实reason变化：E2改knowledge自述、固定后续off-topic contribution；E3增speaker-oriented preamble。但public规格有E2scene15缺slash、scene16缺信息量括号、E3scene3多brace/scene16缺括号；跨实验词串也不同。**source完整不等于running-input精确可恢复**，未自行推断或修原gold。后续只对逐项可核对且明确声明的派生输入写新卡；原全16人类规范永久保留。publisher下载返回HTML，通过PDF magic失败，随后使用作者站公开链接取得合法PDF；无VPN fallback/验证绕过。

少量原paper描述均值与Rev发布版本不一致（E1 Irr considerate约2.22 vs2.12；E2 Unw knowledgeable约2.27 vs2.17），不冒充完整统计复现/反驳。C02/I01不升级，PROPOSED不变。
