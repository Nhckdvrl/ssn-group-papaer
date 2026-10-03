# E59：interpretation-wording-stage（2026-10-03）

- **状态：DONE。** 本卡先于CPU预检和GPU运行；只有预检全过才启动。
- **类型：REPRO / D2。** E51明确读数痛点的鉴别，不是新metric/paper idea。
- **对应：C02 / P02。** 本会话推进同一原自然材料上的措辞与stage归因。
- **问题：** SFT→DPO人类四类分布距离增大，是同一解释对象在不同表述下仍变化，还是主要跟随候选措辞/支持质量？
- **设置：** 全IQAP150原development及原30判断/题，不筛模型正确材料、不读65evaluation。原W0与两预定义paraphrase W1/W2，保留definite/probable与yes/no四类位置；bare/common-chat，8 cached endpoints：OLMo2-13B四stage、Q25-14B Base/Instr、Mistral7B Base/Instr。每model900自然读数＋24 literal-reference-copy技术控制=924，8共7392；FP32/eager/noTF32，完整候选likelihood及原terminal，0training/API judge。
- **操控范围：** 自然dialogue bytes、人类counts、任务主句、原无唯一答案提示固定，只换四选项措辞。W0原B definitely/probably meant to convey；W1 B's intended answer was definitely/probably；W2 B's intended answer was certainly/likely。并非声称三个词的所有人类概率含义精确相等，允许词义强度差；只查阶段变化能否对简单等类表述稳定。uncertainty referent仍listener对B意图解释，不能改叫speaker知识或model factual confidence。
- **读数：** 各alias/interface全150方向accuracy、4类human Brier、definiteness偏差、完整candidate mass、content-only secondary；无QA prior单独报告。stage内同item paired CI，alias×stage交互用相同item与source-cluster sensitivity；不以null校正值当新ground truth，不事后选择最优alias。原W0 OLMo/Q25逐行与E51/E52概率/LP核对，最大差<.001，只同frozen配置比较。
- **阳性对照：** 24合成literal-reference-copy只检验四类映射/词义对齐与输出支持，不作为自然行为finding/gold。参考句来自原四解释，答案明确指定；所有mapping保留。源/候选prefix/EOS/实际backend全量CPU检查；同family完整input IDs一致。每alias/interface/kind首末两次重复与独立全logits teacher forcing，LP<.001、prob<.001、argmax一致才预测。不得用full mass小就静默删模型。
- **噪声地板 + MIE：** 数值门控.001、repeat1e-6；2000bootstrap seed0按原item/source（68clusters）敏感性。阶段Brier差的alias变化≥.10且CI支持可改变归因优先级；不是自动novelty门槛。每stage一个checkpoint，没有training-seedCI。
- **混杂审计：** 已控制原对话/人类counts/完整共同tokenizer/raw评分/batch1/精度/全部alias。未控制paraphrase的精确human语义norm与训练数据/算法共同变化。Base套commonchat非native；Mistral/Q25 native EOS角色不同，共同Instr terminal仅受控入口。copy控制不能代替自然语义理解，词汇prior也不能识别因果能力。原E51/E52结果已知，本实验为有明确替代解释的后续，不能称独立发现。
- **决策表（跑之前写）：** A阶段差随alias反转/显著移动且null或copy一起变→优先回答措辞账户，停止从该读数推能力；回独立自然source/行为。B所有alias方向稳定且copy/source质量可用、null不足解释→保留真实stage条件对象，再跨独立源/readout检验；仍不直接称DPO因果。C质量/控制不可用→记录未识别，换有原norm的源或数据构造，禁止再加一组alias保护结论。D各stage全好/无新关系→记录成功/null，回territory下一未知。不关线、不自行升级L3。
- **算力预算：** 8独立单卡lock，显存<10GB既有使用时才加载，不杀其它进程；≤4GPU·时。新raw目录E59-*不覆写旧脚本/raw，所有hash冻结。

## 结果
[完整summary](../results/E59-wording-summary.json)：7392/8model完整，192 independent/repeat门控全部过；OLMo/Q25 W0六端点共1800行逐row score/prob原parity零差，成功1.5527GPU·时。

SFT→DPO common-chat四类Brier W0 +.3128 CI[.2772,.3475]；W1 +.3419[.3047,.3796]；W2 +.3771[.3332,.4222]。source68cluster三CI亦全正。方向差−.0067/−.0133/+.0067，不能CI含零叫等价。W1−W0 interaction+.0291[−.0120,.0705]；W2+.0643[.0184,.1129]但source-cluster CI含零。三个措辞未逆转stage分布变化。

OLMo SFT/DPO chat全部reference-copy正确；full候选质量.922–.966，但no-dialogue W1 probable-yes .629→.953、W2 .551→.909，prior账户未排除。Base低mass仍不能stage能力比较，MistralInstr W2 copy只有2/4，全部端点/alias保留。决策B的“null不足解释”未满足，保留措辞稳健的任务变化，能力归因保持未识别；按A/C回独立自然source，不再加alias救故事。C02仍L0，0成熟贡献。

### 跑前校对
CPU gate拦截Mistral common-chat模板自动加assistant首空格，而手拼content遗漏该空格；零GPU预测。只对真实模板的完整文本拆出content（保留该separator），原OLMo/Q25 W0仍逐token对旧helper相等。全部alias/原文/候选类别及读数不变；重新做全量CPU gate。
