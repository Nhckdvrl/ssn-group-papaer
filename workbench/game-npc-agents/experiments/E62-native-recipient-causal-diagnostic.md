# E62：固定动作族后的接收者选择与因果白盒诊断（2026-10-15）

- **状态：** DONE；三模型各102图/4896真实Give选择、2448实际解码概率读出完成；原profile/失败保留。
- **对应：** I04 / P12 / C02；E58/E60/E61的动作种类与参数粒度线索。
- **类型：** 有原生后果的局部机制诊断；不是新的persona steering方法。
- **问题：** 当共同give动作已经指定，角色信息还能改变交给谁吗？明确承诺和原目标/请求者绑定怎样影响这项选择，内部角色信号是否真的参与参数裁决？
- **来源：** E58原goal也是give的102图，32B/27B/Gemma R差10.8/6.9/1.0pp，两个候选只差recipient；E60同承诺后角色差依旧且模型变化相反。不能把不同任务组的差直接归动作粒度，需要同场景把动作族固定的控制，并实际改内部变量。
- **竞争解释：** H1角色主要改变give/装备/消费等粗动作倾向，动作族固定后recipient差很弱；H2角色信息参与关系/原目标/请求者的具体参数裁决；H3普通名称/来源绑定与未来句清晰度已解释；H4内部交换只是一般扰动/模板、不能当特异角色机制。所有结果都会改变后续理解，不设通过bar。
- **数据：** 固定现有200 confirm图中作者goal_kind=give的全部102独立图，不按模型行为选择。原世界、人物、motivation、goal和请求全部原样；原Goal与R是不同recipient。通过native parser仅取对当前目标item、可见其他角色合法的GiveObjectEvent，保留全部recipient而非只给own/R两个答案。原始世界不修改。CPU把每个Give动作分别真实执行并核持有者/原goal/R flags；错误保留停下核adapter，不为分数改physics。
- **输入控制：** 完整P在所有输入一致，三种记录：无此前说话、同一明确未来句、同未来句加一句普通绑定事实（原任务接收者X、请求者Y不同，尚无物理交付）。没有P生成A/M或相反人设历史；事实cue不指定谁才正确。此诊断明确do(选择Give目标物品的动作族)，不是完整自由NPC政策或孤立能力证据；E55/E61完整合法菜单作为参照。
- **白盒：** 本地HF BF16/SDPA，非thinking，与既有模型revision相同。原header/状态/原目标/请求及schema保留，标准JSON action字段；对全部合法Give命令建立token trie，强制其最长共同token前缀后选择recipient。所有recipient可选，没有人为gold或修改原执行器。捕获预写中间层floor((层数−1)/2)，64层Qwen为31，48层Gemma为23在共同prefix末位的residual，source/target只有完整P文本包不同。比较baseline、同P sham、另一P donor替换、同范数随机delta；两固定seed6251/6252，配对抽样、不选层/seed刷阳性。交换是局部模型干预，不称完整角色改写。
- **读数：** 每context/P/干预真实recipient、原Goal/R/其他Give、native失败；按102世界内两draw平均配对bootstrap95，sham逐draw对应。baseline另存完整own/R action后缀log-likelihood及差（共同prefix抵消），不只看单verb token。原始prompts、token前缀、残差、概率、全部动作和真实状态保存；张量/大日志不入git。
- **阳性对照：** 同P sham与baseline；所有native Give均可解析执行的CPU资格；普通绑定句；完整自由行为E55/E58/E61已测。不因限制到Give就声称完整agent达成目标或Persona正确。H2需donor方向与真实recipient效应及普通控制一致，角度不作因果。
- **噪声地板 + MIE：** 102独立世界、两配对draw；随机delta与sham、0/弱/逆效应完整保留。单层诊断阴性不能判persona信息不存在；整套P多特质/价值语义与长度同时改变，不称纯BigFive。不同model规模/训练/架构共变，不把家族差归某个架构。
- **混杂审计：** action-field/trie与原自由JSON不同，是显式条件化诊断；共同前缀迫使进入Give参数阶段，不能推自由action分布。没有删除候选recipient，无世界修订，无API教师/裁判；当前P与历史一致。donor residual包括整个文本包及位置差，随机控制只排除一般扰动的一部分；没有独立跨任务训练方向，不冒称可泛化新方法。先动作闭环再内部实验，source捕获按实际prefill/cache配置与sham核对。
- **决策表（跑之前写）：** 固定动作族后仍有P目标差→具体参数/角色目标参与；仅future/cue恢复→接受现有具体锚点/绑定解释；donor按来源改变recipient且随机/sham不解释→定位特异当前角色信号，进一步跨任务确认；随机同样有效/方向不稳定→一般扰动或读出解释；所有模型都有效→研究成功条件；错误/噪声→保留，不关线不发明loss。
- **近邻定位：** Persona Vectors/PSE circuits已研究角色方向与因果策略变化，不宣称首次steering；Story Shapes/CDT已有具体动作锚点。增量候选为原生NPC动作参数/接收者绑定及同承诺的角色裁决，是否成立由证据决定。
- **算力：** 先CPU资格与单图完整profile。优先32B/Gemma两家族，单卡各自运行，实际成本后同固定102图继续，27B条件一致扩展而非择结果；现有fgvd/cache，总占用≤8。每模型102×三context×两P×四干预×两draw=4896原生单步诊断，另612prefill及1224候选打分，估计1–4GPUh/模型含load。无训练、0API。按实测信息量推进，不占满卡凑矩阵。

## 结果
三模型全cohort已完成；不是为某个钦定管道公式填数据。原运行前补充与资格记录按下文保留。

CPU完整资格：102不同原世界、204当前合法目标物品Give命令，204/204真实执行且原goal/R结果匹配，0模型调用。数据路径runs/e62_native_recipient_cpu；首版本地adapter把官方类GiveObjectEvent误写GiveEvent，在GPU前失败并纠正，未改作者引擎或世界，不作科学结果。

运行前竞争解释补充（E61完整结果后、E62全cohort前）：弱的实际recipient差可能只是原goal的基线选择接近floor/ceiling，不能推角色表征不存在；已登记的完整candidate log-likelihood用于区分有角色分数变化但未跨决策边界，与分数本身没有角色效应。不给概率饱和预设新理论或通过bar。

首图32B：48真实诊断+6prefill+12完整候选打分，26.90秒（load22.77秒），0协议/原生失败，12配对sham全匹配；N=1只用于成本/闭环，不判科学效果。Gemma首版loader沿用旧Transformers属性而失败，已按当前官方安装源码改model.model.language_model，原失败目录保留，以v2再资格；不修改任何世界或模型权重。

新增竞争解释：原goal=give的目标关系/实际受益对象与其他动作族不同，不能把分层差全归细参数能力；原作者短中长动机与物理recipient不同。私人利益未知处保留未知，不从Give句型推“无私”。完整候选language log-likelihood与trie限制后的选择概率不是同一量，将分别解释。

概率读出补充（全cohort结果分析前）：本批每图恰好两个合法Give叶节点，最长共同token prefix后首次分叉决定完整命令，余下token由trie强制。因此另用同一模型/输入/保存residual及相同logits processors取一次first-branch分布，记录temperature.7后的exact command概率与log-odds，sham/donor/random同样读出。每完整模型2448个单token readout、不重新执行native、不重抽已有样本；Source完整冻结后运行，估计0.1–0.5GPUh/模型。完整suffix原语言log-likelihood仍保留，不把它冒称trie选择概率。此补充提高信息密度、检查floor与角色分数差，主native读数不变、不以“有微小分数差”当新能力。

### 三模型完整结果

三个模型共14688真实Give选择，另1836 residual capture、3672完整候选打分、7344 exact概率读出。全部协议/native错误0；3672个动作baseline/sham配对完全一致，概率sham精确差0。参数动作均由原native引擎执行，没有权重训练或world修改。

同未来承诺的实际接收者P差32B1.47pp [0,3.43]、27B5.88pp [2.94,9.31]、Gemma0；对应exact概率质量P差1.54pp [0.32,3.14]、5.36pp [3.56,7.41]、0.038pp [0.001,0.103]。binding的实际差0/3.43/1.96pp，exact差0.68/4.55/2.02pp。低基线与抽样读数使动作翻转少，不能推人格表征消失；原goal/current agenda仍重复明确，关系/目的与粒度需进一步同图分离。

单中间层donor有向动作变化很小：32B全部0，27Bfuture/binding各−0.245pp，Gemma无承诺+0.245pp；随机同样可有零星变化。donor有向概率变化32Bbinding约−0.0465pp、27Bfuture−0.0882pp、Gemmabinding+0.0548pp，不支持稳定跨模型的角色定向控制。此单层/单位置阴性不判整条线失效，也不追加扫层找阳性。

完整结果 `results/E62_{32b,27b,gemma}_native_recipient.json` 与 `E62_*_recipient_probabilities.json`；CPU资格 `E62_cpu_qualification.json`。原始prompts/命令/native后果/residual张量在 `runs/e62_*_recipient_all`；概率在 `runs/e62_*_recipient_probabilities`。三个模型及概率final runtime合计约2.103GPUh（含各载入，不含首图profile/失败资格）；exact附录与主自由菜单证据分开。

## E50–E62阶段归档口径（文档整理迁入，非新增实验）

原阶段报告的跨轮成本入口保留为[ROUND_PROGRESS_COSTS](../results/ROUND_PROGRESS_COSTS_2026-10-15.json)与[ROUND_COMPLETE](../results/ROUND_COMPLETE_2026-10-15.json)。E51–E61有完整计时的最终运行合计15.3973GPUh／103672次生成、决策及独立事实调用；E62主选择与概率最终运行约2.103GPUh。该口径不含缺完整runtime的E50原中断进程、部分资格／失败profile，不能当整个阶段或项目完整成本。Step数据usage与本地决策调用分列，provider tokens不冒充Credit或现金账单。各次失败、原seed及raw保留，当前状态只见CLAIMS和整体报告，不沿历史状态重新执行。
