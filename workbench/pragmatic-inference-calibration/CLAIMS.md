# 主张账本

没有已识别的语用能力、训练算法因果或SDT结论。C03登记可重复的任务观察；技术资产、任务观察与科学解释分开。

| ID | 主张（一句话，可证伪） | 等级 | 证据（实验卡、结果文件） | 已知威胁 / 未控制混杂 | 最近更新 | 校对 |
|---|---|---|---|---|---|---|
| C01 | 原始 MultiPragEval 数据与公开评测协议可在本地 open weights 上复现并保持客观评分。 | L0 | [E01](experiments/E01-substrate-audit.md)、[E02](experiments/E02-multiprageval-native-reproduction.md)；原14B四语言三seed完成；原数字误差与解码限制见状态页 | 官方 config、checkpoint/chat template/解码差异 | 2026-10-03 | 未校对 |
| C02 | 至少一个自然 parent substrate 能分别识别 warranted 与 unwarranted inference，不能把所有错误叫 false alarm。 | L0 | [E01](experiments/E01-substrate-audit.md)、[E05](experiments/E05-annotation-feasibility.md)；标签可识别性未成立 | literal accuracy ≠ FPR；任务难度/措辞与 inference-choice 标签 | 2026-10-03 | 未校对 |
| C03 | 在原IQAP开发集150项、OLMo2-13B共用聊天入口的固定四候选读数中，DPO相对SFT的human Brier距离增大，三种预定义表述均保留该方向。 | L1，任务观察 | [E51](experiments/E51-dense-stage-natural-parents.md)、[E59](experiments/E59-interpretation-wording-stage.md)；[完整结果](results/E59-wording-summary.json)：差+.3128/.3419/.3771，item与source cluster CI均正；192数值控制通过、原1800行零差、OL SFT/DPO chat copy全对 | 无对话prior同步变化；paraphrase新human norm未采；条件归一化不是内在belief；单checkpoint/开发集，算法与数据共变；不是能力下降/criterion或论文新颖性结论 | 2026-10-03 | root全量source/概率/数值校对；未独立会话校对 |

## 技术资产（不是paper贡献）

Flan-T5-XL 1,365个选择与作者公开结果全部匹配，概率MAD=0.000077；[E04](experiments/E04-hu-native-logprob.md)、[结果](results/E04-flan-parent-parity.json)。这是D1复现资产，不据此升级pragmatic claim。

## 候选解释（不作为 finding）
- H-A：训练阶段/规模提高语境辨别能力。
- H-B：主要改变推断倾向。
- H-C：两者都变；也可能没有跨现象共享的 criterion。
- 来源 **RECONSTRUCTED**：ALTPRAG gains × PaCE literal-side cost。只能同设定检验，异构数据的差不是因果证据。

## 作废 / 降级记录
当前有L1任务观察C03，没有已升级的语用能力/机制claim。不能因为解释未识别，把实际观测也记成零；不能因为观测成立就包装成成熟论文贡献。

- 2026-10-02 E03技术校对：初版Qwen3未显式关闭thinking，与parent不一致；16.4204 MAE作废为能力/复现证据，保留原文件并按原protocol重跑。不是预注册hypothesis的反例，也不是新finding。

- 2026-10-03 E08：BF16 batch-dependent与Flan target-left-padding读数不通过gate，原文件保留，隔离科学解释；FP32/right-pad替代运行通过，不事后改旧结果。
- 2026-10-03 E19：Flan数字候选非一token，atomic协议不可用；GPT2-r2绝对position gate失败、无预测，r3显式position修正后通过。IR缺40条件不插补。
- 2026-10-03 E17：旧item-summary的MAE bounds对应E|X−t|，不能用于|E[X]−t|；新summarize_sampling明确分开，两份历史文件均保留。
- 2026-10-03 C01/C02仍L0：精确复现与技术修复不自动形成语用主张；仍无合法SDT gold；stage任务读数已出现但未形成可靠科学主张。

- 2026-10-03 E21/E16/E19/E20：OLMoE Base与SFT虽共用Jinja template，但bos=None/50279及special-token mapping不同，actual chat prompt/token SHA不一致。旧聊天结果隔离于stage归因；E12裸入口仍有效，E26逐词token parity通过，E27固定完整tokenizer并控制两个BOS。原文件不覆写，不升级能力。
- 2026-10-03 E24/E25：ImplicatureX源BF16 pair和不总是1，True>.5与True>False不等价。小模型自然recognition数字对算术/选项顺序敏感；仅源数据描述和技术复现，不据此 claim universal hallucination 或整个parent结论无效。

- 2026-10-03 E29：首轮access regex窄导致8run全部在模型加载前停止，0预测；r2源变体全量预检后完成。OL SFT/DPO裸入口全量历史parity各一题超.001，整入口隔离细粒度归因，不局部替换行。role full恢复同时partial恶化/极性不一致，不称知识能力恢复。E30仅数值debug。

- 2026-10-03 E28/E31–37：强现代端点与两组自然强度素材全部完成，有界strict/Flan控制完成。C01/C02不升级：IQAP含词汇/terminal prior、Circa负强度有巨大order effect；一句指令改善强侧可能恶化弱侧，不能用单侧恢复claim能力。原数据/条件/两order均保留，完整结果可审；E35第三family仍运行。没有post-training统一criterion证据。
- E35跑前两次CPU gate：Hu尾部重复空格会retokenize；官方Mistral chat_template完整重渲染assistant时丢system。二者0 GPU预测，冻结原generation prefix与nativeassistant内容后全量前缀通过；不算模型语用错误。

- 2026-10-03 E38/E39/E42：原5token生成的nonEOS numeric不是完整scalar answer。5196个中3677延长后成为prose；Q3裸、Q25Instr裸、MistralBase裸的相关短numeric解释隔离，原raw/摘要永久保留。E43完整源/human迁移已有结果，但入口/初始理解/事实读取/评分可用性未共同满足能力归因；无科学升级。

- 2026-10-03 E41/E45–49：E41强matched pair25508完成，但natural Base候选mass<.01且projection入口可用性不对称，不升级stage能力；E45五endpoint全部未过build floor，confidence/partner解释隔离；E46读数完整但Instr chat理解6/8、facts58/64，不筛正确材料讲机制。E47 literal S0仍提供2/3关键后验，不构造negative gold。E48为parent数学账户审计，0LLM证据，不作paper finding。E49八端点原source联合speaker/listener迁移运行；照片/原练习与human speaker数据缺失明确，不自动upgrade/kill。C01/C02仍L0。


2026-10-03 E49/E50完成：8640/6912原source读数完整，数值/source/token/EOS gates通过。E49无endpoint三身份全过无歧义控制；E50多数Qwen listener恢复，但speaker候选质量弱、身份effect随入口/terminal反转（Q3-8 bare full−.0180 vs content+.0048）。全部原item/missing bounds保留，不把generic role不一致或格式差叫新发现；C01/C02仍L0。当前未知需由独立自然source、成功理解与概率质量共同约束。E51跑前卡已写，核对dense OLMo2四stage和原IQAP/Circa输入；不追加E49/E50的局部prompt救分，资产预检尚在进行。


E52强Q25配对4064完成：IQAP chat方向+.2333 CI[.1467,.3133]而四类Brier+.2084[.1343,.2872]，但Base完整candidate mass8.04e−13/Instr无QA prior偏probable-yes .99697，不能升级能力/校准claim。Circa条件原序弱correct升.7969→.9766，negative弱class仍有原序.1154/逆序.8462的顺序混杂。E53明确POST-HOC无损格式审计全8640与固定6阳/15阴cases通过：四endpoint从0可用恢复962–1079，但无歧义semantic controls仍未共同通过，原primary不改，不将format失败叫能力negative。C01/C02仍L0。E51八槽等待固定权重，有限collector只汇总8作业全完成且校对通过的结果，不更新主张/状态或自主开实验；实际状态保存在本地data/E51-collector-status.json。


2026-10-03 E57：23,552完整技术校对与missing bounds通过；Base入口invalid近全量，plausible语义控制没有全材料通过。E3源内不同端点noise效应方向不一致，不称训练criterion变化或新finding。见[实验卡](experiments/E57-source-exposure-response.md)与[完整原summary](results/E57-exposure-summary.json)。C02仍L0，I01仍SEED；E58先对20条原句盲态辅助审计，原gold不改。


E51八阶段/任务作业8128完成：SFT→DPO human四类Brier变差但polarity变化CI含零，完整candidate质量与terminal控制可核对；原null prior与Circa顺序仍混杂。见[E51卡](experiments/E51-dense-stage-natural-parents.md) / [summary](results/E51-dense-natural-summary.json)。不能直接叫语用能力下降或criterion shift，C02仍L0。
