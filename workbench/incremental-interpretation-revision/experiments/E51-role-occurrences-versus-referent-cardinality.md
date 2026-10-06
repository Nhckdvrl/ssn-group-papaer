# E51：role-occurrences-versus-referent-cardinality（2026-10-06）

- **状态：** RUNNING（未结项；推断完成，审计PARTIAL；2026-10-06用户明确暂停，无后台任务）
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E50 pair_names 的同patient世界特别差，普通actor锚定复述接近正确；尚不能据此声称一般关系使用失败。
- **问题（一句话）：** 联合报告角色的错误是“two names”问法的不同实体预设，还是在无此预设时仍把不同角色默认分配给不同名字？
- **设置：** 全部768个E49/E50原文冻结：24source/12family × old/new各2角色 × 第二事实Name/Desc × inventory有/无 × 同/不同V。外部数据作者写三种问句，再由不同审计者全文审查：(a)neutral_pair按earlier/later的角色各报告名字，避免two names/entities与不同患者预设；(b)keyed_roles分别填Earlier object / Later object，仍无不同名字预设；(c)distinct_name_count报告原文明说为两次活动object的不同名字数量，不能问实际世界总患者人数。三query × base/一句repeat-allowed恢复=4608outputs。固定Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218，FP32/SDPA、no-thinking、greedy、seed0、batch8、cap96。E50原two-names问法作为已冻结历史对照，不重跑挑样本。
- **读数：** neutral/keyed的old/new/joint准确率，明确不同名字替换、same-patient错误与omission/null；count准确率及1→2/2→1混淆。所有条件、all/eligible/common-grammar/nonpossessive11报告；同patient−不同patient、neutral−E50 pair_names、keyed−neutral、repeat指令−base先在每family两source和平衡角色内平均，10000 paired bootstrap seed20261005。未知答案保留上下界，不把未判断当错误，也不只看明确答案幸存组。
- **阳性对照：** E49单问第二角色1530/1536正确，E50 actor锚定普通复述接近98%；当前keyed和count帮助区分从原文找不到角色与输出多样性惯例。Count仅限明说名字的数量，不评价真实世界排他性；两个问法恢复不能单独证明内部编码正确。
- **噪声地板 + MIE：** 同frozen greedy种子和不变事实，无新seed筛选；input/output哈希与完整cap报告。此pilot看成对方向、family分布和不确定界限，采用科学判断而非自动阈值。不同用途的任务解读效应是被测变量，不叫hidden-state机制。
- **混杂审计：** facts/aliases/actor/VP/库存全继承冻结输入，不构造新事件、不引入错误前提；neutral/keyed避免different/two实体要求，keyed标签仅格式；count明确只计reported names而非包括未报告参与者。repeat恢复固定一句：A name may be used more than once; use the name reported for each activity. 同一指令用于count也不改变数量定义。名字性别quirk、群体actor/reciprocal活动等父材料局限全部保留分项，自然transport未完成。所有gold与全答案语义标签来自外部Luna，不由root自行重标；审计错误版本完整留cache。
- **决策表（跑之前写）：** neutral/keyed恢复且count正确→上一错误主要问法预设/列表惯例，不能称一般角色绑定问题；neutral仍对同患者特别差、keyed恢复、count正确→联合输出格式/多样性压力，下一用自然多角色同一实体作决定性transport并定位已有多答案QA；neutral/keyed均差且count在同患者偏2→默认不同角色对应不同实体竞争解释更强，但须自然材料和无角色/普通重复控制；count正确但两角色仍错→数量推理与角色应用可分，下一比较同一输出内计数与赋值来区分输出约束和事实检索；repeat一句恢复→显式指令可用，不能叫能力缺失，追默认来源；没有稳健结构→回到同一领域的真实痛点，不继续模板局部优化。不预设任何结果自动构成novelty。
- **算力预算：** 0–3/6/7六独立单卡shards，每query两shards各768outputs；≤.7GPU·h估计。不碰peer4/5，复用existing venv/local model，不下载权重。
- **命令：** 材料和外部审计完成后在任何推断前记录SHA、preflight及actual CLI。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：全部4608输出完成，.319116GPU·h，count5条cap；六shards代码41a60c1b。literal neutral base joint81.510–82.422%，两端paired95CI[76.823,86.198]/[77.344,87.370]；repeat91.276–91.536%，两端CI[86.719,95.443]/[86.849,95.703]。同patient−不同patient base bounds−26.563..−24.740pp，CI两端[−32.813,−20.313]/[−31.510,−17.708]。
- 结果文件：[small stats](../results/E51-literal-schema-compact.json)、[Plan audit snapshot](../results/D0-StepPlan-pause-snapshot.json)；完整原分析cache/E51-material-preparation-v1/literal-schema-full-summary-v1.json，不压缩、不进git。
- 按决策表执行了什么：尚不能执行最终科学分支；Step完整语义审计仅39/192批（936回答），108 max_tokens、29缺passage hash、12断言、4缺item ID，不按成功批做总体结论。用户暂停，不新实验或重试。
- 主张变化：C05 L1→L1，I01 PILOT，不认证novelty。
- POST-HOC 分析（事后才想到的，单独标注）：保守literal-schema解析只接受简单完整格式，其他null、给上下界；description按父材料外审alias作实体引用但Name-format单列。keyed大量长格式未解析，不能用下界说role正确率约54%；count措辞和description字符串仍竞争，不能用count错误证明实体个数不理解。完整答案外审未完，原input/prereg/输出均不改。

- **推断前冻结输入：** 2304 whole-input外审，4608variants全eligible/acceptable、old/new角色与count Gold均与parent机械匹配。fields fe3a098c6d5a5643ded64443a14525de0eda9d3ca757f324b59771a3c9e37aec，audited06ba3860fb93f9efb75bbec514ad253f21f3188c9bf93060b9625b53fa09a168；[D0](../results/D0-E51-input-audit.json)。三queries独立启动，每query两shards，CUDA_VISIBLE_DEVICES0/1/2/3/6/7：time_indexed_role.py run --experiment E51 --query neutral_pair/keyed_roles/distinct_name_count --num-shards 2 --shard-index 0/1 --data cache/E51-material-preparation-v1/question-audited-v1.jsonl --out cache/runs/E51-{query}-{shard}。FP32、batch8、cap96、greedy、两mode同context分到同shard；不使用代理、不改facts。

- **2026-10-06 用户审计修订，任何本次Step输出前：** 当前Luna输入审计在新指令前已完成，版本不替换。后续constructed/adapted语义标注使用Step Plan / step-5-preview，endpoint固定 https://api.stepfun.com/step_plan/v1/messages，禁现金接口、总并发≤8。现有E01请求完成释放槽位后进行全4608回答Step审计，按不见Gold的24条同source/predicate/form/inventory小批组织，每条仍带完整passage/question/answer及hash。角色答对和Name-format另列；description正确指称不能叫角色错误。count需同时外审question是否清楚、reported proper-name count是否由原文关联成立；若把description当另一个name string也属合理解读，则标不确定，不事后强迫1。此为POST-HOC审计歧义敏感性，不改变原问句、Gold或推断，原primary definition与全部输出保留；count材料问题不能用个别得分解决。
