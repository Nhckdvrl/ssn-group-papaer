# E78：强模型的关系草稿，真实消费流程（2026-10-07）

- **状态：** DONE；仓库生成器E431在运行前改用本线E78，非事后补卡。
- **对应：** P17 / I03 / C06–C09。GP旧解释修订形成之后，是否能在后续QA共同使用？
- **问题：** 先前核心方法/干预在8–12B三族没有共同两关系恢复。用三族更强模型问清：模型已经写出自己认为的解释后，原句加草稿或只消费草稿，哪个环节决定实际源QA？这是强基线真实用途的探索，不复制小模型mask格。
- **数据：** 原E65/E76 892QA/356S/178clusters，四构式MVRR27/NPZ89/NPS36/NPVP26，GP/cue、原S/Q/gold全保，SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b。0新API、成熟数据不重审；没有成功草稿/题或模型筛选。需要解释新文本具体role时才Step Plan≤5原子项标注，不把中间标签设为总pipeline先行门槛。
- **模型：** 当前离线既有manifest中Qwen3-32B、gemma-3-27b-it、Mistral-Small-24B-Instruct-2501，按可用资产/族最大模型事前选择，不看本实验结果。三族BF16/eager，FP32 logits log_softmax，固定每batch 1 QA/2候选，seed78，与旧FP32面板分开报告，不混作重复。八卡独立分片并共享锁；不结束轻服务。新模型DIRECT不可借旧E52的不同规则评分。
- **草稿：** 复用E67 NONE同一公开faithful“两简单句”指令，Source先行，生成看不到Q/gold，greedy/cap256/EOS，HF标准use_cache=True以减少生成重复计算，版本/参数/输出token完整保存。这是强模型新1068自由草稿，不加入已失败EVENT_FIRST指令扫描。不把模型草稿当正确文本。
- **唯一方法轴：** DIRECT原Source→原G2 QA；SOURCE_AND_DRAFT沿E76原S＋统一notes may be wrong/judge originalSource段→原G2 QA；DRAFT_ONLY用新草稿作为QA可见Source→同原G2 QA，仅提供模型生成草稿；若草稿原样引用原句则完整保留并计数。每项原Q/选项两mapping/words与letters相同。DRAFT_ONLY仍用原S gold评价完整S→draft→QA流程；错误草稿的传递是错误，不改成草稿金标。两种消费不是同token因果干预，E77提供小模型同文本路径参照，不能跨不同模型宣称同一机制。
- **读数：** 原gold correct/p_correct，initial/final/all及joint allQ；各操作及两草稿条件−DIRECT、DRAFT_ONLY−SOURCE_AND_DRAFT，全部三族四构式GP/cue两readout两mapping。QA→Source→lexical cluster等权，bootstrap10000/seed78/CI95；完整成员齐后读效果。caps/长度/mapping flip全报不删。
- **阳性对照：** 原cue baseline与原Source/gold；CPU全任务完整重分词/源prefix与候选gold映射验证、不重复BOS；固定第一源重复评分数值一致，无未来标签输入。标准generation decode/token一致。BF16确定性数值校验与整体cluster CI分开，既有E52精度噪声约.24–.51%只作参考，不把小翻转证明逐条概率精确。
- **噪声地板：** 全mapping/paired CI，首Source同布局repeat LP应完全相同，无seed筛选/措辞sweep。大小模型与dtype/训练也改变，不能把模型间差直接称纯scale因果。
- **混杂：** 草稿可丢失/新增信息；DIRECT与两阶段compute不等，草稿自身faithfulness待核验。DRAFT_ONLY改变可见源/长度/文本位置，与混合消费效应不能单独定位Source神经竞争。Mistral新族/更强panel都完整报，不替换更差baseline。若只是一般错误复述/缩短context效应，无GP增量则不包装novel。
- **决策表（跑之前写）：** 强panel三族两构式出现共同恢复且保持另一关系/cue→核验新草稿实际关系，再找能预测/解释用途的具体修订规律；DRAFT_ONLY差但混合/直接好→明确草稿丢失，回真实形成痛点；正确草稿却混合损伤/单独可用→消费竞争线索，须同一强panel核心因果干预再称机制；异质/阴性→整个E76–78块自审后停止草稿/Source局部网格，更新整体hypothesis/interestingness，不自动关线。
- **算力预算：** ≤8 GPU·h，1068新greedy草稿，892×3操作×4读出映射×3族=32112 QA条件。新数据/原始输出外置E78，代码/卡/小摘要入git。不会因API等待让GPU空着。

## 结果

三族全892QA×12操作读出/映射的CPU placeholder任务语法/候选映射/prefix校验完成，真实草稿生成后全体再重分词；未将placeholder当模型输入。八独立H20分片已启动，按原Source SHA分配Q3/G3/M2，不按结果筛；GPU7等待既有E77释放锁，其余已空闲。新1068自由草稿与32112 QA条件，0新API，尚无科学效果。

## 完整结果与自审

1068新草稿/32112 QA条件/8分片/2016格全部闭合并读取，0API，2.223111GPU·h；map SHA69dc6e9e8aa0293a8b806d4f3b82bbe1bb0fe8728c04708d21ad7b22839e6fbc。所有24长度/144mapping格报告，全部cap0，固定首源同布局repeat LP0。BF16大型panel单独，不把不同模型/dtype当纯scale因果。全两readout图已生成并视检words概率/joint图；外置E78完整，小摘要results/E78-stronger-draft-summary.json。

- MVRR GP DRAFT_ONLY−DIRECT initial概率Q/G/M +1.38 [-8.91,+13.06] / +13.11 [+1.62,+26.49] / +2.86 [-9.21,+15.41]pp，final +5.13 [-7.02,+17.41] / +7.33 [-9.03,+23.33] / -4.13 [-15.46,+7.57]；joint +0.00 [-18.52,+18.52] / +25.93 [+11.11,+44.44] / -1.85 [-14.81,+11.11]。G有收益、Q/M不共同恢复。
- NPZ GP DRAFT_ONLY−SOURCE_AND_DRAFT initial概率 +4.43 [+0.97,+8.46] / +7.85 [+2.75,+13.66] / +0.34 [-1.92,+2.76]，final +0.59 [-0.37,+2.22] / -0.13 [-3.63,+3.37] / -12.00 [-15.84,-8.20]。Mistral仍有关系取舍；两mapping/letters全保，不能只报更好words。
- Mistral NPS mixed可提高initial与joint，Q/G没有共享显著增益；NPVP Q32初始收益伴随final下降，G/M不同；各构式cue和全部阴性同报。DRAFT_ONLY NPZ cue final−DIRECT +0.10 [-0.20,+0.50] / -7.47 [-13.30,-2.63] / -16.59 [-20.22,-13.22]，MVRR cue joint +9.26 [+0.00,+20.37] / +1.85 [-12.96,+16.67] / -42.59 [-55.56,-27.78]；其中大损伤不能隐去。
- 原S原样引用存在于Q2/G22/M95 of356草稿，未删任何项；所以DRAFT_ONLY是只给完整生成文本的pipeline，不是保证纯Source移除。长度范围均值Q18.1–26.6/G35.9–52.1/M31.1–102tokens；max84/177/232，caps0。Q32 letters原mapping翻转最高39.60%，Mistral words/letters也高，各映射原值与均值完整保留。

E76–78块自审：外显规划没有共同两关系保持，移除原Source消费也没有共同恢复；更强面板有一些真实端到端收益，但不是三族两构式一致方法。此块先问形成和用途、后检核心竞争并扩强基线，至此停止草稿/Source同质网格，不再换提示或择优模型。最佳三句：局部外显修订与完整可用解释不同，但这个宽叙事已有近邻。现有数字尚未给出可预测、值得兴奋的共同规律。正确修订内容已经独立确认时，原Source的再次直接消费是否覆盖它，仍是一个不同且可便宜决定的对象。E71正确P1的后续切断未共同恢复，但MVRR native仍错、NPZ近满分，下一核心对比只切Source→Sentence2，保持正确P1及其自身Source计算不变；若仍不恢复就结束此消费块，回E70/E67实际输出完整证据，不扫位置/层。C06–08 L0/C09限定L1不变，尚无合格idea，无需人状态/候选决定。
