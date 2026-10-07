# E80：合法GP的输入信任与潜在语法纠正（2026-10-07）

- **状态：** RUNNING；生成器E431在模型运行前改本线E80，非事后补卡。
- **对应：** I02 / C06–C09 / P17。仍问GP先前错误解释为什么没有依后文修订，不进入一般agent/安全/认知读时新线。
- **问题：** E76–79外显关系/消费/强面板没有共同恢复。E2除了世界内容合理性，还有“观测输入是否被漏字/错字”的先验；模型是否把合法低频GP当成待纠正语言，从而维持另一解释？不是先认定noisy-channel成立。最便宜核心预测是语法零编辑信任与可能漏字先验，会以不同方向改变真实原SourceQA。
- **来源/定位：** 已全文读的人类Ceháková/Chromý2025有noisy-channel作为竞争解释（包括MVRR插which、NPZ插pronoun），不能把这个宽假说叫首次。MIT Clark/Hoover/Gibson/Levy EMNLP2025 main/limitations/算法附录已精读；2026 targeted-regression已在既有知识库读CoNLL正式主文，当前arXiv摘要回看不是新增精读。增量若有，应是native instruction LLM源解释如何响应输入可靠性、能预测实际解释操作和跨用途恢复，不是只有一条prompt涨分。新颖性仅定位，不自动关线。
- **数据：** 原E65/E76 892QA/356S/178clusters，MVRR27/NPZ89/NPS36/NPVP26，GP/cue、原S/Q/G2 gold、两个mapping/words与letters完整。SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b；原Published/已冻结T3资格，不新增数据构造、不重审成熟S。0新API；新输入状态是研究干预，不作为语义gold或新材料。
- **条件：** NATIVE完整E65 NONE原raw复用；TRUST在Source之前加 `Input status: The sentence is grammatical exactly as printed.`；NOISY加 `Input status: The sentence may contain a missing or misplaced word.`。这仅操纵输入可靠性先验，后面的Source/TaskG2/Q/选项/答题指令全同。NOISY可能性不等于Source实际有错，原金标不换成“想说什么”；不要求学生改写源，不显示parse/QA答案。三族Q8/G12/L8同offline manifest FP32/eager/seed80，8卡Q3/G2/L3按原SHA分片。
- **主读数：** TRUST−NOISY及分别−NATIVE原gold correct/p_correct，initial/final/all和joint all原Q，三族四构式GP/cue两readout/两mapping全部；10000 lexical cluster bootstrap/seed80。保住正确关系/cue才能叫选择性恢复，No增加不能叫修订。不筛truth模式或成功模型，模型/source分片覆盖先锁。
- **阳性对照：** cue的原支持/原NATIVE；CPU全S/Q/gold字节与native prompt SHA复现、任务内Source prefix一致/不重复BOS，状态提示没有Q/gold；固定首Source旧NATIVE LP与新实现差<.001。两种状态的prompt token长度全报，不能把metadata不同的对比称纯等计算实验。原E54一句修订指令全结果保留，不新增防御性prompt网格。
- **噪声地板：** 两mapping flip与paired CI、数值仪器；不加seed/措辞重复。5pp只信息价值参照。
- **混杂审计：** 状态prefix同时可影响词句表征、Task解释和一般回答偏好；Source位置/长度也略变，此pilot不能直接定位内部编辑或称bayesian机制。信任声明提供真实语法metadata，因此它是oracle条件下的行为，不等于native能力；R8不能凭提示恢复单独作能力证据。实际新编辑/复述若需机制归因，才对新输出Step Plan≤5项审核；现成gold可直接测pipeline行为不等teacher。
- **决策表（跑之前写）：** TRUST跨三族两构式改善真实GP两关系/joint、cue保留且明显区别NOISY→在原输入上观察学生实际解释及其对应的最小编辑操作，用新增输出语义审核分辨“输入重构”与一般grammar instruction；相同收益/同样损伤→一般context/polarity或compute，不能noise机制；NOISY提高No而损正确final→是信息/响应偏好；null/异质→不换措辞追胜，把噪声通道可能性降为未证成，回已有完整原子/自由表达脚印或新的核心对象。不自动关线或资格升级。
- **算力预算：** ≤2 GPU·h，2×892×4读出映射×3族=21408新QA条件；native零整面板重跑，仅固定仪器。8独立H20，不终止轻服务。代码/card小摘要入git，raw/config/assets外置E80。

## 结果

尚无科学效果。

CPU预检三族全部7136新tasks/族与3568原native SHA一致，892QA原语法双pass均acceptable；8卡PID：2429505, 2429506, 2429507, 2429508, 2429509, 2429510, 2429511, 2429512。
