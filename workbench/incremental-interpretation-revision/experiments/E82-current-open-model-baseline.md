# E82：当前开放模型上确认真实GP痛点（2026-10-07）

- **状态：** DONE；生成器E431在任何模型评分前改本线E82，非POST-HOC。
- **对应：** C06–C09 / I02 / P17；D1强baseline更新，先确认原解释修订问题在当下模型是否仍存在，不硬挂新idea/不新开线。
- **问题：** E76–81没有共同完整关系恢复，旧基线主要2025世代。继续解释旧模型的局部错误之前，先确认2026开放模型的真实GP错误及一句恢复指令后的两关系保持；成功模型也能提供修订机制的对照，不预设失败。
- **模型/事前选择：** 官方与国内镜像已核实Qwen3.8-27B（2026-08-14官方发布）、Gemma4-31B-it（2026官方）、Ministral3-14B-Instruct-2512（当前单卡Mistral家族）。Q/G原BF16权重；Mistral作者release为FP8权重，将明确用已发布FP8后反量化到BF16计算并单独记录，不声称原BF16资产；全部单卡、FP32 logprobs、原生模板；大参数/日期不保证本任务更强，M14也不作为M24受控scale。HF镜像固定metadata SHA与ModelScope每文件revision/SHA逐项核对，禁止跟随HF镜像的海外xethub重定向；只国内ModelScope/CDN，无代理。
- **数据：** 原E65完整892QA/356S/178clusters、四构式M27/NPZ89/NPS36/NPVP26、GP/cue原S/Q/G2 gold，两映射/words与letters。SHA45137a88328224095c3d8bf1dc969f63eed7822a4f1ef4412949528c935b406b。0新增标注、不审成熟原数据、不补T2、不构造新文本、不按旧结果筛样本。
- **条件：** DIRECT原生chat零样本G2；ONE_RECOVER沿既有E54一句 `Read the whole sentence and revise any initial interpretation before answering.`，只一个恢复入口，不加R1/更多措辞控制。八独立H20，按原Source SHA分片Q3/G3/M2，不结束轻服务。
- **模式/读数：** CPU检查并冻结每模型实际支持的非thinking模板，若确实有无思考回答入口则在该入口评分原候选LP；绝不把尚在thinking入口的标签LP当最终回答。若模型只能thinking，则完整greedy生成到最终回答、保存推理与caps/格式失败，再按事前解析规则测最终correct；这种模式单独报告，不混作非thinking评分。具体模式依据模板/runtime而非效果在GPU前锁到config。强制选择correct/p_correct与joint全Q完整initial/final/all、全部GP/cue/两readout，bootstrap10000 lexical cluster seed82；若使用生成则概率读数明确不可得，不捏造。
- **阳性对照：** 原cue和原源支持规则；CPU字节/候选mapping/模板实际入口/no重复BOS；固定首Source同布局重复LP应相同，独立完整序列与优化单token读取<.001（BF16不称无限精度，若因numerical差则保持完整序列读数）；所有caps/错误完整保留、不删。生成branch的明确格式/最后答案解析只用回答格式，不借teacher/gold。
- **噪声地板：** 既有BF16局部数值误差不能外推新架构；当前固定batch/重复同布局+全部mapping flip和paired CI；不补seed网格、不选择最优checkpoint。
- **混杂审计：** 新模型训练/架构/大小/模板都不同，不称同参数scale或单个架构因果；Qwen hybrid GDN、Gemma4共享KV等不能直接使用旧patch仪器。任何prompt恢复不独立认证native能力（R8），真实原gold/另一关系/对照保持分开。基础成绩高不等于好idea，也不因旧痛点已解决自动关线。
- **决策表（跑之前写）：** 当前三族仍有共同真实错误且cue有效→针对实际错误内容选一个关键因果动作；新模型自行修好→比较成功修订所需的关系操作，不能坚持旧模型无能力叙事；一句恢复仅改变极性/伤正确关系→不叫修订；模型异质/格式或基础cue弱→单独描述，不将地板模型作为机制或领域负证据。完整图后自审继续，不因asset/runtime待处理停目标。
- **算力预算：** 非thinking评分≤6GPU·h、21408原QA条件；若必须完整thinking生成，先冻结范围/cap并修订预算后运行，不把代码模式切换藏在结果中。资产约150GB，外置models/E82/；只镜像下载，data/API额外消耗为0。runtime独立venv，旧实验/API环境不修改。

## 结果

尚无科学效果。镜像/架构/runtime核对进行中。

新隔离runtime transformers5.19.0 / 原torch2.7.1cu126已装；仅追加原research依赖路径读取，旧环境package未改。Qwen非thinking模板显式闭合think，Gemma4非thinking模板闭合空thought channel；完整tokenizer文件已国内验证，进一步CPU冻结实际词表/候选入口。Mistral确认release FP8，卡在科学运行前澄清dtype；不以文件名叫BF16。原下载PID2595587后以2637050缓存续跑，优先tokenizer并排除不使用的consolidated重复格式，没有Step HTTP被取消。

Ministral全部使用文件逐个size/SHA与固定镜像LFS核验后先启动2卡（PID2872975/2872976，GPU4/5），无需等待另外两模型下载。manifest SHA5660e761de9d3cbd98eca8555fb95192b87396f8d092d6adfb5b8767e1845cc2；两分片均通过prefix/full仪器并开始评分。原作者FP8权重dequantize到BF16，保留原生默认system/template，不称纯BF16资产。其余6卡模型准备完成即运行，0新API。

Qwen3.8使用文件全部核验，manifest01e8dd2ce75a392fafe8e698e69718c4d68bc9b921302585f1de6b89a75715a0；GPU0/3/6（PID2906669/2906670/2906671）仪器通过并全量评分。缺少可选GDN加速库时采用已支持的本地PyTorch reference运算，没有海外kernel下载/科学模式变更。Gemma权重国内CDN续跑，核验后GPU1/2/7；其余在途标签不是启动门槛。

### 完整结果与自审

三族8分片/21408新条件完成，1.271113GPU·h、0API，1008格全部读取、48长度/96mapping全部核对，原892QA/356S/178clusters/gold不改。map SHA44ec602cdb12d94dc3af334125a6104f86b0121d65906d8801e84788ec8439b5，完整配置/资产身份/量化来源/失败与raw外置，summary保存全图。Gemma资产manifest d58f157bf03e61c38d658e8bc9fb7cea7b0db0da8730edb95784f2e269b11369。

NPZ GP DIRECT initial correct Q/G/M 37.64 [28.37,47.19] / 71.91 [62.92,80.90] / 84.55 [78.93,89.89]%，final 78.37 [70.51,85.39] / 78.65 [71.35,85.96] / 28.09 [21.35,35.39]%；cue final 100.00 [100.00,100.00] / 100.00 [100.00,100.00] / 94.10 [89.89,97.75]%。Ministral初始已大多正确但最终关系仍错，说明不能只靠initial错误率给完整修订判分；未据此认证latent正确解析或原因。

NPZ GP ONE_RECOVER−DIRECT initial correct 18.82 [12.64,25.28] / 5.34 [1.12,10.11] / 2.81 [0.84,5.06]pp，final -3.37 [-6.46,-0.56] / 2.25 [-2.81,7.30] / -5.06 [-8.99,-1.69]；joint 7.87 [2.81,13.48] / 3.93 [-1.69,9.55] / -4.49 [-8.43,-1.12]。MVRR GP joint 5.56 [0.00,14.81] / 3.70 [0.00,9.26] / -1.85 [-5.56,0.00]pp。没有共同两构式完整恢复；letters/负效应/其它构式同报，不把单句提示收益单独作为能力机制。

数值边界：prefix-only与完整候选序列BF16布局最大LP差Q .250008/G1.833693/M.187166，均触发效果前预注册的全分片full_scores分支；没有混用prefix/full选效果。最终固定full2候选/单任务布局、重复LP差全0；此图是BF16标准完整序列评分，不能称prefix一致<.001，也不跨旧FP32模型认定纯scale因果。Q letters最大mapping flip26.73%，Ministral words27.78%；Ministral NPVP cue final仅19–25%，这组只能描述不能归因GP能力。

当前最好故事：最新模型的真正错误仍存在，部分模型的瓶颈已不能只用“初始误读未撤回”概括；但具体关系/否定倾向/输入判定三种解释尚未因果区分。下一最高信息量动作是复用现成人类词义材料E85，扩大修订画像而不再局部K/V；之后具体内容或任务判定核心对比，不能直接称词能改角色不能改。C06–08L0/C09限定L1不变，尚无合格idea，无需人决定。
