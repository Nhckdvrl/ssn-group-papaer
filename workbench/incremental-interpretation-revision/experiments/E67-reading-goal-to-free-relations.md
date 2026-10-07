# E67：提前目标的收益能迁移到自由关系复述吗？（2026-10-07）

- **状态：** DONE；先卡后运行。
- **对应：** I03/I04、C06/C09、P13/P15。E65完整矩阵后提出，E66还在运行；本实验不依赖E66效果，提前登记不选择有效的模型/目标/构式。
- **与先前解释修订的关系：** 二元QA目标可能只准备某个答案；若撤销旧关系/建立正确关系成为可复用理解，应在不询问任何事实Q的自由输出上留下正确关系。这是同一源同一目标、换真正用途的核心检验。
- **条件与数据：** E65全部356原S/178clusters/4构式，原initial与final目标不改；NONE/INITIAL/FINAL读完S后均只有相同Amouyal原论文的faithful two-sentence指令，source先于Task。不显示eval Q、答案、G2规则、选项、不先生成目标Q回答。3原定模型族各356×3=1068自由输出，总3204。源材料仅由E65输入资格决定，未过滤模型正确率。两个目标可含结构/词汇线索，不能自动视为纯目标心理变量。
- **主读数：** T4_CORRECT_ROLES（完整终止并保持主要事件/角色）、GP_MISREADING（明确旧角色；含新旧共存）、OTHER、UNKNOWN、cap，以及两句格式独立报告。逐三族/四构式/GP/cue、目标相对NONE差、GP−cue差变化；同S→词汇cluster平均/bootstrap10k/95%CI/seed67，全部并列。与E65同S的QA全Q共同正确作联合描述，不能把QA与role同时正确当唯一潜在parse。
- **阳性对照：** 相同目标cue全覆盖；NONE新frame的自由基线必跑，E53/E63旧frame角色不拿来当相同分数。E53的一句恢复原对照独立完成，未完成前不以单独行为探针升级能力。
- **噪声地板：** 已通过E63/E64的FP32/eager/native BOS/no-cache greedy路由复用，cap256/seed67、输入排序首4source检查prefix与goal Q一致；科学运行前核对三族可分离prompt/source，不再增加缓存工程路线/提示网格。全部失败保留。
- **标注：** 已纠正P15语态≠施事的T4-v2，全新输出盲于模型/目标/QA/gold，按Source＋FinalText SHA复用完全相同packet。Step Plan step-5-preview，batch2（≤5），两次独立shuffle、分歧第三遍，失败不算通过，所有请求留外置缓存。共享HTTP池最多8个活请求；只读完整面板，不读部分标签效应。可信原S/Q不重复逐条审核。
- **决策表（跑之前写）：** INITIAL相对NONE跨三族至少两构式role恢复、cue保住，同时other-Q可复用→追源修订可携带机制，联系E66路径；只QA涨而role不涨→更像回答准备，换修订触发/组装问题；FINAL与INITIAL方向不同且词汇clusterCI可分→建立关系/撤销旧关系不同入口的线索，不能只借人类既有good-enough命名novelty；各族/构式不一致就保留地图并更新假说，不挑成功族。
- **算力：** 独立单卡GPU3/6/7，已缓存三族FP32/eager，预估≤3GPU·h/族；0/1/2同时E66，4/5服务不动。HF离线/镜像，无现金账户。无新构造S，无额外语法控件。
- **定位与自审：** Lee&Shin2026已拥有GP复述错误和task-depth现象；Patson/Christianson已有partial重析。这里可能的增量是具体目标入口对未经询问关系的恢复及E66的源路径，仍未证明。E65→E66/E67是目标异常的两次局部追问，完成后必更新假说表、评价审稿人为何关心；不能继续做第三个目标措辞实验。

### 标注前的吞吐调整（2026-10-07）

E67尚未发出任何T4请求、三族仍生成时，前瞻改为每批5项（用户上限内），仍两遍独立打乱/不同请求、分歧第三遍、原schema/哈希/覆盖校验与失败单条重试、Step Plan step-5-preview，共享总8活HTTP不变。audit_paraphrases新增可选batch-size，默认2不改变在途E53/E64；只E67后续显式5。先前卡中的batch2是agent实现选择，不是用户要求，不让自设小批次阻碍大批高质量标注。数据/模型/条件/读数不改，没有读取任何部分角色效果。

## 结果
尚未运行，C06–C09 L0，不认定合格idea。

- 全输入356S/178clusters已核对，源manifest SHA3edaec29912ca958d3fcea831f5cce4a4bfe7f8d98535e6948b6f8ae8ee7a887。首次wrapper漏传旧greedy接口的空donor字段，三族在首次forward前KeyError，科学输出均0；失败代码/config/log保留failed-before-generation-v1。补齐无效空donor信息并验证BASE无hook，原prompt/data/cap/条件不改，用runs-v2继续。

- 分析用独立合成fixture验证：role/joint真实迁移+1，已达cap的正确标签不算完整成功，未知标签保持missing且上/下界分开；不以标注失败当语义错误。结果外置stat-fixture-v1/verified.json，未读科学role输出/部分标签比例。

### POST-HOC目标语义命名校对（P16）

原question_target≠预期更新操作：NPZ有17初始目标源支持Yes，MVRR有19最终目标源支持No；完整原条件/数据/读数保留，不将其整体命名撤销/建立。另以input-only initialNo_finalYes、initialYes、finalNo全部层及evalGold拆分已有输出，先保留全图再限定解释。拆分晚于E65全效应、早于E66全效应与E67角色效应，非事前主分析；没有补跑提示/重新逐条审原数据。

三族全部生成闭合：3204自由输出，Q/G/L GPU·h1.511452/1.977292/3.041235，合计6.529980。三个完整predictions SHA d1245386a269427d8b14addfd7eb1da3715ee3490e2776baf6a365b5cffceeca / aa27c25a6f9aea55441a266826eced19dec07b8f4cc8dc61775a942b911d16b0 / 69f7e36a27fcda5c794486b78cee003ce2e815b190904a3b180ccede1eb3a103。T4-full-v2批5完整双盲接续，复用已完成v2 exact packet，仅构建scope与接口进度可读，未读部分语义效果。卡仍RUNNING，主张级别不变。

2026-10-08 03:22完整审核仍在独立第三遍裁决，metadata-only两遍各缺4／3个有效请求，先补齐原失败IDs（非内容／效果筛选）；原T4-role-v2 prompt／同两遍pass号／单worker批1／共享StepPlan8slots，不覆盖原审核。原第三遍封版后仅对仍无有效结果的裁决请求补，已有有效标签逐字断言不变；独立T4-failure-completion-v1保留原summary／annotation SHA及失败补全来源。原图与新完整图各留版本，未知上下界照旧。正常原社区数据不重审。

完整T4-role-v2双遍3033／373裁决、7失败pass补全后3033/3033／0unknown，原版summary/地图保留，新完整地图 SHA3a8b7bcde6fe75a1c6f65b215263ac5f336607a9a5d49e46acfc232cb8c15f81；完整2400scope已按主要role/cap/QA-joint逐组自审。三族pooled GP INITIAL使CORRECT_ROLES降低、GP_MISREADING增加，OTHER不增加；不是只有QA-only null。问答改善与明确误角色方向相反，未证明唯一latentparse。下一按新的accuracy/faithfulness分离对象设计当下模型actualQA＋freeinterpretation核心对比；不是第三个goal恢复措辞网格，不更改原Source/cap/角色定义或主张等级。
