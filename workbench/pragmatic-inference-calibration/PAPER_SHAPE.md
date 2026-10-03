# 论文形态卡 — 2026-10-03

- **一句话未知：** 语用理解进步中，哪些是更会区分语境，哪些是更倾向补充言外之意？
- **形态：** 重新归因 / 跨现象finding / 测量工作均为可能，尚未选择。
- **manuscript-critical contributions：** ❌ 当前为零。parent复现、解析修复、SDT、generic response bias不能单独成为贡献。
- **摘要主张：** 无。C01/C02是驻留问题，不是paper claim。
- **图表：** E01资产、E02/E06/E10格式/预算、E03/E17分布、E04/E13/E18公开结果匹配、E19/E20知识条件与readout、E21–E28原更新/stage/数值边界，均为instrument证据。
- **基线：** Hu原Flan-T5-XL已逐项复现；Wavelength FP32/关闭thinking与3模型sampling完成；Multi原Qwen1.5-14B完成；TACL2023 BERT/GPT2 string复现；EPITOME原SI评分与partial IR资产核对；ImplicatureX七模型/19源cache完成，Qwen matched stages已测。
- **证据标准：** 许可和选项类型可靠；ROC/连续score与单操作点分开；跨≥2家族与≥2现象边界；item/pair cluster CI；stage比较用真实连续Base/SFT/DPO checkpoints。难度、标签、prompt/chat模板/解码/格式先审计。
- **近邻：** ALTPRAG拥有stage/free-form gains；PaCE拥有context flip/over-inference；DRInQ拥有人类语境许可与过强解释；CIS拥有表征偏移与item差异；generic SDT拥有sensitivity/bias分解。[定位](POSITIONING.md)
- **compression risk：** 高。另一metric说明bias、模型更强但脑补均不足；能否改变已有结论尚无证据。
- **停止损失：** 三轮逐步加限制或accuracy与辨别读数同排序且无边界，提议人审转向；不自动关线。
- **目标：** ACL/EMNLP/NAACL主会；无截稿绑定、无周计划。
- **决定：** 用户授权D1/D2；继续核对仪器，升线/科学产出判断待人。

**本轮扩展：** 最有信息量的未知目前是“不同交际证据怎样共同调节具体推断”，而非保住global criterion。EPITOME拥有mental-state使用缺口，ImplicatureX拥有撤回与prior控制，ICLR2026拥有目标权重。S1/S2/S3只是动作种子；必须有自然条件结构或对已有结论的实质重新归因才可能成为论文。宽泛知道不用/不会更新/格式偏差都不足。八卡只跑问题明确的独立实验；权重下载等待不称实验。

**增量约束更新：** CoNLL2021已拆同题辨别与默认偏好；ACL2026 accommodation已有纠错/误报与QUD/source；Social Meaning2026已拆方向/强度。当前仍0成熟贡献，数据规范/入口/真实stage检查后才决定科学对象，不将数值或tokenizer bug卖成语用发现。


**E28/E31–37更新：** 强现代端点已补齐，两组原human自然材料、八端点与同question配对完成；强方向成功例和readout混杂共同出现。balanced strict提升强側而损伤弱侧，不保“恢复=能力”故事。第三family Mistral原Hu/取消/自然强度八slot在跑。本局部位置/措辞分支不再加救分实验，保持0成熟贡献；下一对象必须对具体交际证据如何改变推断有实质解释、可跨材料验证，不能只描述prompt变分数。


**深读更新：** 前人最强动作是改变可区分的前提：Mayn拆自己的推理与对partner能力信念，Weak Evidence用选择机制解释旧反转，NMI/Confidence-Commitment拆报告含义与后续行为，Roleplay用真假×角色endorsed控制浅行为与内部改变。generic“一个能力分不够”“知道不用”“criterion移动”都已有ownership。当前候选未知是表达选择预测能否约束具体听者解释及不同社会判断；E49仍为parent驻留，不注册结果方向。E45 task floor失败、E41支持质量、E46基础理解限制均保留。不能把一个reference task不一致缩成paper，需独立自然来源的可迁移条件解释；贡献仍0。
