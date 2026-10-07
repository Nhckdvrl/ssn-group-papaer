# E65：提前目标会帮助未被询问的关系吗？（2026-10-07）

- **状态：** DONE；先卡后代码/科学运行。E64完整QA节点已自审，E65不依赖未结束的角色标注。
- **对应：** I03/I04、C06/C09、P13/P14；E59全R5、E63完整QA/角色分歧及PERK/Lens/Ask Twice精读产生的POST-HOC选题。本卡的条件与读数在本实验输出前固定。
- **问题与价值：** 若读句子时的目标只改善提前询问的关系，问答正确可能反映任务准备；若同时改善未询问关系，就有更完整解释形成的入口。研究价值在自然增量修订的可复用性及其可预测边界，不是“问题先放会涨分”。
- **核心条件：** NONE不提供提前问题；INITIAL先提供同句原initial问句；FINAL先提供同句原final问句。随后三条件都阅读完整原S，并在相同源后位置回答原evaluation Q，始终保留末尾Q，避免把远端问句读取缺失混进目的。提前Q不含答案、不先生成回答。读句子与末尾Q指令完全一致。
- **数据：** E59最终资格data-v1.jsonl SHA1ab5cce22192a58ee0bdfb3ebcaacabbb2242e9f721ecd8836286f0e71af5377，原公开S/Q、gold与最终G2资格不改。以source文本SHA分组，只取存在initial/final两类问题且原GP/cue能成对的源；多个Q取(item_id,question)输入排序首个作为提前Q，全部evaluation Q保留。预检892QA、178独立词汇cluster、356源：NPZ89/NPS36/NPVP26/MVRR27 GP源。最终成对资格程序复核后给manifest，不按任何模型正确率挑源。
- **读数：** 原G2正确率/p_correct，words/letters×两mapping；逐模型/四构式/GP与cue/initial与final/两gold资格完整输出。核心矩阵为“提前目标×后来问题”，另标evaluation Q是否与提前Q完全相同；主要关注other-target而非同题回测。源内所有Q与mapping平均再cluster bootstrap10k/95%CI/seed65。原正确→错误、错误→正确及同源initial/final共同正确同步报告，不把二者正确自动称唯一潜在parse。
- **阳性对照：** 既有自然cue的相同矩阵；模型能力从完整cue正确率判断，只作描述的弱cue不能成为mechanism null。NONE保留该新frame的原始baseline。
- **噪声地板：** 原生chat不重复BOS，FP32/eager/offline；固定小输入single-token评分与独立整sequence评分LP差<.001、两candidate共享同一prefix；同源不同evaluation Q在任务前prefix逐字相同。没有测试结果时确认输入资格，失败原样保留。只做小仪器，三科学条件不附加成串排除条件。
- **决策表（跑之前写）：** 提前FINAL帮助未询问initial且正确final保持→追共享关系修订/目标触发机制；只帮助提前同题或伤另一关系→用途特定准备，检验可预测的关系选择；INITIAL/FINAL影响相反且GP特有→自然歧义下目标改变解释入口，随后核心因果源bank测试；cue同样随Q变化→更一般任务偏好贡献，不能称GP独有；所有效果弱/方向乱→该目标操纵不足，回其他大尺度问题，不扫prompt措辞。任何结果都不自动认定合格idea。
- **规模/算力：** 三预定族Qwen3-8B/Gemma3-12B-it/Llama3.1-8B，各892×3×4=10704评分，独立单卡，预算每族≤2GPU·h。按已自审的完整QA节点推进，角色审计独立并行。HF已缓存模型只离线/镜像，不直连。可信原始数据不重做逐条审计。本阶段无新生成文本，因此无额外Step标注；若完整结果值得追，再登记无Yes/No自由用途/关系因果实验，用Step Plan step-5-preview批≤5审新输出。已有E53一句恢复对照仍完整双盲中，不用部分结果作能力升级。

## 结果
完整32112评分已完成，三族总0.90014 GPU·h。C06–C09仍L0，未认定合格idea。

- 输入manifest已确定：892QA/356源/178词汇cluster，数据SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b；四构式数量与预检一致，源/Q/gold未改。尚未读取本实验科学输出。

- 三族CPU全输入检查完成：各10704个单token选择任务、同源同目标在evaluation Q前prefix全部一致。此为输入准备，不产生科学预测，也不新增pilot。结果文件为外置E65/input-preflight-v1.json。

- 四构式矩阵统计合成校验通过：未问关系迁移+1、另一关系损伤−1、只修目标关系不被计为共同正确；完全相同问句与另一问句标签分开。只验证核心读数，不添加科学条件。

- 科学运行前执行顺序澄清：检查AGENTS/README/EXECUTION_BRIEF，未发现“同时最多两个实验pilot”的硬规则；IDEA_EXPLORATION建议选1–2个idea进入PILOT，不等于阻塞独立实验的算力上限。此前等待是agent自设条件，撤除。E65只依赖E59最终S/Q/gold与E64完整QA自审，不依赖P15待纠正的role标签；保持所有预定数据、三个条件与读数。小仪器首次调用sequence_scores参数错误已修，失败代码/log保留；v2三族独立LP最大差.000117/.000261/.000071，全部通过后开跑。

### 完整自审（先读全矩阵，再决定下一步）

- 小摘要：`results/E65-goal-by-question-summary.json`；外置完整地图SHA657643df00f02f2b19268e4f728f725caef6048cf0434bc1f342092c78cbede7，含全部gold层/概率/读数/转移，不筛模型或构式。
- NPZ提前INITIAL使所有Q共同正确率Qwen/Gemma/Llama提高15.17 [6.74,24.16] /11.24 [2.25,20.22] /28.09 [19.10,37.08]pp，89clusters。initial正确率+24.72/+12.92/+18.54pp，三族CI均正；final迁移−5.11 [−9.38,−1.42]/+4.26 [.57,8.81]/+28.69 [21.02,36.93]pp（同gold，88clusters）。所以并非三族都共享关系修复；Qwen有小损伤，不能藏在joint增益中。
- NPZ提前FINAL对initial迁移+18.82 [10.67,27.53]/−5.34 [−13.48,2.53]/−37.36 [−46.63,−28.09]pp；joint+13.48/−6.74/−18.54pp。族间方向冲突，不能讲“最终关系目标统一改善解析”。
- NPS提前INITIAL initial增益50.00/12.86/38.57pp均CI正，但cue也+58.57/+10.00/+24.29，主要不支持GP特有。未问final仅Llama稳定+46.15 [30.77,61.54]pp。
- MVRR没有共同恢复：INITIAL initial+2.47/−16.67/+16.05；同一initial目标下完全同题与其他原initial问句方向可不同（Llama+35.19 vs−14.06pp）。NPVP joint增益也不一致，提前FINAL甚至损伤cue正确final。完整letters/p_correct复核方向：NPZ INITIAL初始收益三族仍正，Llama INITIAL→NPZ/NPS未问final迁移仍正；绝不只展示这两个有利模型面板。
- 当前三句话故事：提前关注“旧关系是否成立”能改善多个模型的修订判定，但其跨关系迁移不统一。最终关系的提前目标未必促进撤销旧关系，部分族甚至强化不一致。目标的作用发生在源编码还是后续组装尚未知；问句先放/重复本身已有近邻，不足认定novelty。
- 推翻与最高信息量下一步：E66只让提前目标经源token抵达后续消费者，保持源的原生编码逐层不变，比较目标效应是否保留；若普遍消失，则转向问句直接作答路径而非“目标改变了源解释”。不追加目标措辞/层位置网格；两次局部追问后再自诊断。
