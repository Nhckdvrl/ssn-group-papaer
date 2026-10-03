# E41：stronger-matched-stage（2026-10-03）

- **状态：** PLANNED
- **类型：** REPRO / D1–D2，stronger matched-stage boundary
- **对应：** C01/C02/P02/P09
- **问题（一句话）：** 同一Qwen2.5家族从3B到14B后，post-training对原自然语用判断/更新/背景信念归因的作用是否保留，还是此前主要反映较弱端点与读数可用性？
- **设置：** Qwen/Qwen2.5-14B @97e1e76335b7017d8f67c08a19d103c0504298c9 / Instruct @cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8；官方parent，不把bundle因果归因于单独RLHF。完整共用14B-Instruct tokenizer。四作业/端点：Hu bare1365/chat1365、原ImplicatureX parent+既定format6504、原projection bare/chat3520，共25508预测。已声明的原source/原human norm/评分，不增新数据或judge。
- **读数：** Hu按phenomenon/人类对照；ImplicatureX初始support、cancel−irrelevant及两编码、candidate support；projection按valid/实际fact/谓词、人类MAE全行上下界。分任务解释，不能pool一个competence或criterion。projection原5token、invalid单列且numeric非EOS单列。
- **阳性对照：** 所有原源审计复用；下载完整marker后CPU全prefix/source hash与两个端点actualtoken逐task相等才运行。FP32/noTF32/单sequence：Hu/Impli首末重复<1e−6，独立full teacher-force LP<.001、choice-prob<.001、argmax一致；projection首末greedyIDs一致/LP<.001。失败原run保留、不放宽。
- **噪声地板 + MIE：** fixed inference无sampling seed；预先沿用各parentitem/scale cluster bootstrap2000/seed0，不把两个checkpoint当训练seed总体。任何scale/stage方向只有入口支持率与读数成立后才可讨论，不设置预期paper effect。
- **混杂审计：** Base没有nativechat能力保证，共用模板是输入控制，不称native部署质量；同家族不同scale训练数据仍可能不同。Hu非均衡phenomenon不能只报总分；Impli原irrelevant续句许可未有全量human norm，取消差异不是FPR。投射背景信念与speaker知道不同。3B原E22与E38各自协议不同，跨scale先核actualinput/precision，不忽略parity直接作stage差分。
- **决策表（跑之前写）：** A14B同stage结构跨入口/原任务保留→记录候选边界，再独立材料/ownership审；B强端点任务表现很好→保留成功并削弱宽泛缺陷，不换prompt找错；C差异仅读数或支持率→仪器解释、0scientific upgrade；D各phenomenon/stage方向不统一→削弱单一criterion，分别保留对象，不硬写统一paper。
- **算力预算：** 八GPU独立锁，每端点4作业；FP3214.77B≈59GB/卡，不拼通信训练。原权重共≈59GB置ROOT/models，不进git。资产/CPU gate通过后排队，等待下载不冒充GPU利用；预计<8 GPU·时，实际写config。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
下载进行中；CPU所有原source/完整candidate prefix及同族input SHA已通过（results/E41-prefix-preflight.json、E41-projection-preflight.json）。八独立作业已排队，尚未GPU预测；C01/C02仍L0。
