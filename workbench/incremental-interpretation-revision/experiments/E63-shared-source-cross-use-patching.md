# E63：同一源状态是否共同改变问答与自由角色表达？（2026-10-07）

- **状态：** RUNNING（三族v5仪器均通过，全体共同资格已固定）；先卡后代码/科学运行，生成器E431运行前改为E63，菜单E61/E62保留。
- **类型：** PILOT。
- **对应：** I03/I04、C06–C09、P13/P14；不是I05继续扫窗口。
- **与修订的关系：** 晚消歧后的GP解释必须能用于不同任务，不能仅改变一个No答案。E55已给自然cue源替换的因果入口；E60的早切断改善伴随严重正确关系损失，不支持选择性修订。E63问一个具体的新问题：同一任务未知源前缀、同一源donor向量，能否同时修好原QA与无Yes/No选项的角色表达？
- **来源：** E55的预定前1/4层歧义区跨三族MVRR正效应；选择这个入口发生在E55之后，明确POST-HOC实验来源，E63跨用途结果前瞻登记。粗残差含句式/形态等多因素，不预称关系特异机制。
- **读数：** 原QA硬正确率/正确概率；自由复述CORRECT_ROLES、GP_MISREADING、OTHER，由独立双遍Step5、分歧第三遍判定。按已有连通词汇cluster先平均重复Q/mapping/源，再10k bootstrap95%CI；每族/构式/任务/GP与cue均报告，两种QA输出与顺序保留。T4不使用自动词共现判角色，不筛baseline错误/成功cue。
- **阳性对照：** 清晰cue源BASE；PAIR双向交换，反向cue→错误不是同方向干预保持性；同方向GP patch对原正确QA/角色的损伤必须报告。复述的“一句能否恢复”已有E53 R8全族完整生成、仍在双盲审计，不从部分结果引述。全量SELF不新增科学条件，但仪器固定输入验同源替换不改变评分/逐步生成。
- **噪声地板：** 本地FP32/eager、greedy/cap256；BASE候选评分与独立2D校验差<.001；SELF逐位置abs<.001或relative L2<1e-5且LP差<.001。source-only截断cache与任务全prefix源状态一致；不同QA/复述的源token-prefix必须逐字一致。固定4源的16步BASE/SELF greedy必须相同；全族统一每步完整prefix重算、无KV-cache，避免缓存路径差异。仪器失败先修，不读科学结果。
- **决策表（跑之前写）：** QA改善且GP角色正确增加/误角色下降→共同功能入口，随后独立关系变量及输入保持性定位；QA改善但角色不改善→用途特定组装/输出代理，不能称统一修订；GP角色变化伴随大量OTHER/原正确损失→干预损伤，不能称修复；两任务皆null或cue弱→任务frame/资格限制，回到E53完整角色地图，不推出内部parse不存在。任何情况都不自动认定合格idea。

## 数据与操作

仅用E55的原公开S、Q、原gold/T1/T2/T3与自然cue配对，不新造句、不扰动旧24模板、不重新审计可信源。任务前固定源前缀：原生user chat中`Read this sentence carefully.\nSentence:\n<S>\n\nTask:\n`，QA或复述指令只在此后出现；源token末允许尾随空白，不能含Task非空白。对每个S缓存截至源末的状态，严格证明所有QA/复述用途共享它。不是把E55的另一个frame向量直接移植过来，也不把新frame的BASE当作E53/E55原BASE。

QA在源后附G2源支持规则、原Question、两选项顺序×words/letters；复述在源后附Amouyal的两句忠实角色指令，无示例、无答案、无问答gold。两科学操作BASE、PAIR；PAIR仅在floor(.25*(L−1)) block后替换已有T2歧义区的同词对齐状态。三个预定模型Qwen3-8B/Gemma3-12B-it/Llama3.1-8B全部运行；词token数资格完全由输入决定，整对排除，记录每族cohort与交集，不以效果挑样本。复述按源/对应donor/已有词跨度去重，不把同句多个问答当独立源；来源别名与连通cluster保留。

源prefix donor不得包含Task非空白、QA、复述指令、答案。完整prefix与单源缓存一致、SELF、完整prefix生成一致等先通过，冻结代码后才全量。所有原始predictions/cache、code/config/model/data SHA和失败保留外置E63，git只代码/卡/摘要。新生成文本审计用Step Plan step-5-preview、batch2≤5、共享总并发≤8，原E53的完全相同source/output标签可复用，失败不算通过。

## 规模、预算与解释边界

输入上限322QA/161pairs/72独立GP源，预计机械token资格约E55的220QA/52源，不把15clusters当大规模机制证明。这里是检验跨用途的决定性pilot；若成功，再用成熟语料更大独立源做关系特异验证，数量对齐相关GP文献而非十几例定题。三卡独立单卡，每族预算≤3GPU·h，最大256生成token；与E53同时是两个pilot。HF只镜像，已缓存模型离线，不触碰已有服务。这个操作检验功能迁移，既不证明原GP内已有正确parse，也不把whole-vector操纵称细粒度语义中介。

## 结果

尚未运行；C06–C09 L0，无合格idea，未请求状态/候选决定。

### 科学运行前仪器修正

首版任务缺native format字段，三族在评分前停止；补字段后CPU全族输入预检一致（236QA/108源units，43pairs输入排除）。Qwen/Llama原KV-cache校验通过；Gemma默认HybridCache仅分配prefix长导致下一token越界，显式预留后仍与完整prefix重算有29.94最大LP差，仪器拒绝，未运行科学输出。所有失败代码/log保留。改用全三族统一每步完整prefix重算的manual greedy、固定原EOS/cap；每步重施同一源patch，源因果prefix不变，16步SELF必须一致。没有改数据、cohort、干预层、读数或按科学效果调门槛；原缓存要求由这次前瞻修正替代。

- v5三族共同输入资格：236QA/118同题pairs、108源units（每方向54），1888 QA评分+216复述/族。MVRR/NPS/NPZ分层全部保留，不从效果筛源。源prefix同一、QA独立/SELF LP、源向量abs/relative与16步SELF greedy均通过；hierarchical统计和完整三族合成fixture通过，不作为科学结果。
