# E66：canonical材料与人类条件规范逐项核对（2026-10-03）

> 关闭后保留的历史证据：2026-10-03用户决定终止；原始输出、数据和实验runner现已删除。文中local raw路径为历史定位，不能再逐条重算；最终汇总保留。代码可从关闭前Git快照51a578c1追溯。

- **状态：DONE。** 本卡先于join、统计与语义分层；只做已授权核心数据核查。
- **类型：D1/D2，C02/P02。**
- **问题：** ImplicatureX原候选含义/场景与human baseline/cancel判断能否逐项对应？现有模型缓存究竟测同一事实、同一意图，还是未获norm的派生条件？
- **设置：** 读取固定parent canonical prompts/datasets、expert与Prolific responses、human stimuli/UI/instructions/filter代码、原公开论文；全271 canonical item（源排除some_all_8）都登记，不按human effect或模型输出筛项。核对comment/canary header、原worker过滤规则与item计数。加入prior/negation/strengthen/irrelevant仅作派生规范清单，绝不自动继承human norm。
- **语义字段：** 每项q原文、target事实/意图/说者commitment/混合/未定；cancel所否定的层次；baseline/cancel两侧human数据覆盖、stimulus bytes一致性；supported/insufficient-support/refuted三类仅在独立依据成立时填写。关键词自动flag只供人工检查，不作为gold。Likert原量尺/participant/item保留，不线性当真实概率。
- **读数：** source-hash、原材料/源prompt/UI逐项diff、覆盖/missing/重复/过滤计数；原scale内human项目和participant结构、方向与不确定性；各缓存checkpoint/readout/顺序/numeric/source可用性。匹配统计为全量计数，无科学能力claim。
- **阳性对照：** 纯源码formatter生成的baseline/cancel场景与发布prompt逐条一致；human stimuli原text插值与model对照分别核对（已知{implicature}/speaker/frame差不能忽略）；原canonical排除与专家sample单独记录；原Likert范围、contains_cancellation实际编码、同item跨condition/worker模式查实后再join。原human总体趋势重算不替代单项规范。
- **噪声地板 + MIE：** 字节/hash/schema错0容忍；有合理UI插值差异保留原及明确规则，不静默归一。统计CI按item/participant分别说明，未采新human。pilot只决定可测性，不靠大量raters冒充独立场景；无固定human effect筛选阈值。
- **决策表（跑之前写）：** A canonical与human可对应、目标层次可分 → 冻结可用scope和少数正常端点缓存分析卡，先对原支持/削弱证据做条件响应，不claim首次撤回。B只有部分source/目标对应 → 以源属性固定范围，不按模型/显著性筛；未定保留并明确限制，不硬Hit/FPR。C关键条件无norm或语义目标混杂 → 明确缺哪种对照，只在它能区分解释时构造20–30条草案/独立人类norm方案，不直接铺GPU或生成1000条。若仍无法自然可靠识别，交人判断冻结，不另换题材。
- **混杂审计：** human Likert非模型belief概率；human问法与True/False MCQ可能不同；专家只验证sample、派生控制没有自动规范；同源item和重复participant非独立，挑战/validity筛选不能估自然总体失败率。只检验已存在semantic target，不将取消意图与世界事实否定混合。
- **算力预算：** CPU/阅读 only，0新GPU/闭源API/权重下载；新推理总上限15GPU·小时。若需后续GPU或数据构造，必须另写冻结卡且先说明缺口，不为卡数补齐配额。

## 结果
全量技术/文本join完成：原过滤multiset精确复现2285评分、76保留worker、271 canonical（raw attention记录88 worker，不强行补到论文90）；542 condition cells中3/4/5评分分别62/301/179，重复item-condition-worker=0，同worker见同item两条件=0。human两条件是不同参与者，不伪称人类成对within-worker实验。

全部271 q与actual-seen datapoint对应。仅移除HTML显示标记/重复场景标题、scalar单说者A前缀后，243项在两侧q/场景均匹配；其余28的拼写、标点或措辞差异逐条保留，不静默当同文。canonical与stimuli四文本字段也有28项差异，但这项检查与actual-seen检查不等同。初版过强的“全部stimulus字段必须相同”断言被实际版本修正拦截：原审计文件保留，改为报告差异，不改变human标签。

human raw取消平均变化（原1–7量尺）：scalar −2.648、discourse −1.741、synthetic −3.091、natural −1.586。共255项下降、14项上升、2项相同，全部保留；item bootstrap仅描述，未同时重采participant，不当完整推断CI。

固定32项source-stratified语义pilot由root盲于E67输出核对：包括事实反驳、撤回支持、例外、意图/计划变化；`might`/`may`、generic/only、信念/claim等范围不可硬混。逐项说明见[语义pilot](../results/E66-semantic-pilot.json)。**不是独立human裁决，全部三态gold/全量layer仍UNADJUDICATED。** 243文本匹配cohort只支持graded条件响应，不支持二分类许可/FPR。

决策B：存在可用的human graded桥梁；canonical baseline/cancel有norm，派生四条件没有相应norm，仍不混入核心。进入E67有限阶段/现有端点响应；未发现需要立刻新造数据才能区分的稳定残差，不启动数据生成。

[汇总](../results/E66-canonical-human-audit.json)；全271项actual human/model文本、原rating counts和层次未定标记在`/data1/xiangding/work/pragmatic-inference-calibration/data/E66-canonical-human-audit/items.jsonl`。0新GPU/API。

**POST-HOC技术补充：** UI的instructions.js:471–488使用innerHTML。243 presentation-normalized匹配中16项模型含字面`<laughter>`/`<noise>`等注释，人类浏览器可能隐藏这些cue名。原norm函数对两边去tag会遮掉这类输入差异，故243不能被称为全视觉刺激等价。[逐项风险](../results/E66-ui-render-risk.json)。原冻结cohort保留，E67另报227无该风险敏感性（只按UI/source筛，不按结果），不改读数/gold。此风险不是新科学finding。
