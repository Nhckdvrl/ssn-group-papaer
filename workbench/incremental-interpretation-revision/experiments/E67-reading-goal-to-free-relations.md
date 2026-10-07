# E67：提前目标的收益能迁移到自由关系复述吗？（2026-10-07）

- **状态：** RUNNING；先卡后运行。
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

## 结果
尚未运行，C06–C09 L0，不认定合格idea。

- 全输入356S/178clusters已核对，源manifest SHA3edaec29912ca958d3fcea831f5cce4a4bfe7f8d98535e6948b6f8ae8ee7a887。首次wrapper漏传旧greedy接口的空donor字段，三族在首次forward前KeyError，科学输出均0；失败代码/config/log保留failed-before-generation-v1。补齐无效空donor信息并验证BASE无hook，原prompt/data/cap/条件不改，用runs-v2继续。

- 分析用独立合成fixture验证：role/joint真实迁移+1，已达cap的正确标签不算完整成功，未知标签保持missing且上/下界分开；不以标注失败当语义错误。结果外置stat-fixture-v1/verified.json，未读科学role输出/部分标签比例。
