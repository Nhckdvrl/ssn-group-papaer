# E49：joint-speaker-listener-parent（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2，自然人类parent文本迁移与派生speaker读数
- **对应：** C02/P02
- **问题（一句话）：** 同一源场景中，模型对说话者选择表达的预测，是否与其听者对象解释相容，并受partner身份调节，还是只有互不约束的任务输出？
- **设置：** Mayn/Loy/Demberg2025已E47逐行核对的全部24原场景（8critical/12unambiguous/4ambiguous）、四原available messages，不新增对象或message。identity unspecified/adult/four-year-old；listener三循环对象位置；speaker三个目标对象×四循环message位置。每model216 listener+864 speaker=1080，八endpoint=8640 frozen greedy calls。Q25-3B Instr、Q3-4/8/14B、Q25-14B Instr、Mistral7B Instr、OLMoE SFT/DPO；全部pinned已完整模型。原形状颜色用明确word描述，不添加reasoning/严格恢复prompt。native chat，Q3关闭thinking；OL共用完整SFT tokenizer，同actual输入。
- **读数：** 完整EOS whole JSON integer list，listener三数/speaker四数，0–100且和100；源角色映回target/competitor/distractor及message。listener单独记录原human Exp1/2 adult/child所有cell means与分布；unspecified没有human gold。speaker预测无原human标签，只用于配对描述：均匀对象prior下P(source msg|object)归一得到Bayes预测，与listener全三类分布L1距离；四word order全部报告，不能把跨task Bayes差叫真实内部机制或能力错。收到消息预测总质量0时不可定义后验，明确missing，不加epsilon。
- **阳性对照：** 12unambiguous listener有唯一source真对象，argmax正确且完整≥.95是能力解释floor；全部control/ambiguous/critical均保留，无挑正确材料。source E47 SHA一致；每场景objects/msg完全原源；human原排除/24项join；三/四循环恢复原角色精确一致。每model首末source×两task重复IDs精确一致/LP<.001，独立full teacher-forcing逐generated token LP<.001。parser正/负/EOS用例CPU先通过。源L0/.5与S0→L1 2/3同一规范预检。
- **噪声地板 + MIE：** greedy仅仪器重复；按原24item cluster bootstrap2000 seed0（critical8/controls12/ambiguous4分开），word/object rotation不是独立item。八endpoint不是训练seed总体。先task floor，再conditional结构；无预注册方向/效应量paper标准。
- **混杂审计：** 原human三practice/photos/实验历史未迁移；adult/child改text identity，不能称原human identity效应精确复现。原source game也不是开放域自然对话；新增speaker任务与human listener不同，跨QUD输出一致性不等于内部过程。speaker可赋非真词概率，这不是gold FPR；可能代表能力信念。无照片/自主选择反馈，不能归因学习partner policy。SFT/DPO只在共用tokenizer/input后比较，但无isolated RLHF因果。完整分布是显式metalinguistic，不叫next-token语义概率。失败先parser/floor/rotation审，不能为保结论换prompt或筛item。
- **决策表（跑之前写）：** A控制成功且speaker预测能条件约束listener→记录parent边界，下一步独立自然材料/可区分选择账户，不宣称finding；B两读数成功但无关系或身份只影响一侧→支持任务/目标分离，需独立readout后才解释；C控制/格式失败→仪器不适用，无能力negative，不增修复prompt；Dhuman同方向→parent复现，不能当model缺陷；E完全无差/强端点很好→保留成功，不制造anomaly。任何结论不自动改workbench状态。
- **算力预算：** 八独立GPU锁，FP32/noTF32/single/max64，预计≤4 GPU·时；不下载权重、不训练、不API/judge/子agent。源raw与完整输出不入git，derived summary审计后入git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行；论文32页/附录A–E及原models.R已读，E47源审计完成；这是parent驻留迁移，不是paper idea。C01/C02仍L0。


2026-10-03执行：CPU全部原source/human/token/parser gate通过；三Q3相同actualtoken，OL SFT/DPO相同actualtoken；八作业开跑，全部原场景保留。两个Q25首次校对失败且0实验预测：原生repetition_penalty=1.05使generate.output_scores是处理后分数，与full teacher-force原logits不同。原四control/日志/目录带failed-score-gate-r1永久保留。r2独立runner使用output_logits原分数，生成默认策略不变，重复与full前向阈值仍.001；其余六已运行脚本不改。两个队列和脚本SHA分别保存，不把失败当能力negative。原始generation_config亦在Q25 r2 config中保存。

2026-10-03完成：八endpoint全部1080、8640 calls；原source/input/wholeEOS/生成策略/独立完整LP gate通过。Q25两失败processed-score门只保存0实验预测，raw-logit重跑保持native策略、全部完成；失败不伪装为模型能力。三身份listener无歧义correct/36：Q25-3各12，Q3-8为35/35/34，Q3-14为35/35/34，Q25-14为34/34/35；OL SFT/DPO、Q3-4、Mistral原严格whole-list控制0可用。没有模型三身份全过既定.95，但这不是自动kill，明确format、position与few-error边界，不筛模型成功项。Q25-14 critical adult−child .02083 CI[.00833,.03750]只是文本协议下读数，缺photo/练习、未共同过控制且跨readout不稳，不升human-like reasoning finding。

原raw抽查POST-HOC：Q25-3轮换场景仍常输出[50,30,20]；Q3-4使用JSON代码围栏，Mistral使用字符串列表。按预先整数whole-list规则全部invalid保留，不事后剥围栏/转字符串救分。原obj/msg/rotation角色反向映射核对无改。结果：results/E49-joint-speaker-listener-summary.json，所有missing bounds/zero-source-word evidence保留。C01/C02仍L0。
