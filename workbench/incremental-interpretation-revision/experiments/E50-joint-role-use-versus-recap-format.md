# E50：两事件联合角色使用与复述格式（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E49部分真实复述出现actor/patient混淆，首轮审计另含格式误判，正在全量重审，尚不采用错误率。
- **问题（一句话）：** 两事件联合使用的失败来自关系重构的干扰，还是actor–action–patient格式/姓名指令的任务解读？
- **设置：** E49全部768contexts原文冻结，24source/12family、旧×新角色、同/不同V、第二Name/Desc证据、inventory有/无不删不选。换三种由外部模型逐条写、全文再审的用途：(a)同时报告旧/新actor对应的两个patient名字，只列两个名字；(b)普通两短句复述，明确名字用于object、unnamed actor仍用原描述，不要求三元组；(c)普通两短句复述但问句分别点明旧与新actor/action。三query×base/原E49一句scope恢复=4608outputs。比较原E49formal recap是冻结历史对照，case/world/role全配对。
- **读数：** 两名字联合old/new/joint正确；两复述的old/new actor/action/patient分项、明确错配、遗漏/不确定、joint、unsupported patient。完整答案盲审，不从firstNP或固定冠词/gerund regex判错；certainty unknown保持null，报告上下界。主format差、congruent−incongruent×same/differentV和Name/Desc/库存调节；R8 paired差。先family两source和两个平衡role assignments平均，10000 bootstrap seed20261005。all/eligible/commongrammar/nonpossessive11全报。
- **阳性对照：** E49第二patient直接问+E48旧patient/alias调用；本卡两个patient联合读数去掉输出actor的格式成本，anchored vs unanchored普通复述去掉event retrieval cue不足。即使联合问能修好，也不能直接称“内有正确状态”。
- **噪声地板 + MIE：** 同FP32 frozen Qwen3-8B/no-thinking/greedy seed0，native batch8/token cap96；原E49 formal recap不重跑不选种子。不同query也改变任务/注意力，不能把问句恢复当独立证明编码过程改变。
- **混杂审计：** 三用途中事实、alias、姓名性别quirk/群体actors完全一致；只列名字不是Name替换actor。普通复述允许词义等价时态/被动、正确的省略，严格区分显式反角色与格式缺项。新旧世界均非exclusive，只评价原文明确报告角色。E49 first-review的解析误判记无效解读、原文件保留，独立交叉校对后才取分数。
- **决策表（跑之前写）：** 两名字与两普通复述均正确而formal失败→主要格式/指令问题，不支持一般角色使用机制；两名字正确、普通复述仍有患者/actor系统错配且随congruence/V变化→关系重构的干扰，下一自然event论元材料；anchored普通复述恢复但unanchored失败→检索cue/注意力是主要竞争解释，需要自然材料验证，不把generic recoverability卖novelty；两个patient联合也失败、单问有效→联合关系使用压力，继续区分输出序列自我干扰与输入关系检索；仅Name/Desc条件不同→映射/共指使用竞争。没有一次null就关workbench，没有自动novelty门槛。
- **算力预算：** existing venv/localmodel、GPU0–3/6/7共6独立shards，各768outputs；不用peer4/5；预计≤.7GPU·h。下载全部直连。
- **命令：** 待材料/完整审计后写实际SHA与命令；任何推断前完成。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- **推断前完整输入：** fields9dc7ccfe871e78b54927ffdbdd96b85e0db698915b301b9ab4835246fcdc85f7；768unchangedE49contexts×3Qs=2304audits，4608variants全部eligible/proposedagreement/grammaracceptable，全部prompt actualtoken<1024。[D0](../results/D0-E50-input-audit.json)。原E49因differentV反而较差，不能以此预设sameV共享角色collapse；原决定表保留，三格式全跑。run time_indexed_role.py --experiment E50 --query pair_names/unanchored_recap/anchored_recap --num-shards2 --shard-index0/1；analysis analyze_observed_roles.py --experiment E50。
