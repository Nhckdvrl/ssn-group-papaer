# E41：干预覆盖与普通等义增强的等预算控制（2026-10-14）

- **状态：** DONE；四条件 × 三种子共12次有效300轮训练及所有阶段评价完成。
- **类型：** EXPLORE；I03的研究动作，不预设新loss。
- **对应：** I03／P10，衔接E34/37/39/40。
- **问题：** 单C功能控制与文字稳健性需要哪种经验：普通等义表述，还是独立变化C与其他特质／身体的干预覆盖？
- **比较：** 原E34 NoInfoNCE为baseline；新增surface-only NoInfoNCE与C-intervention NoInfoNCE，三固定seed42/43/44、原300iterations／每轮25600transitions／所有PPO及diversity设置不变，从同初始化训练。先NoInfoNCE避免1200变体造成contrastive候选数量／false negative差异；不把读出提高当控制效果。
- **surface设置：** 每原episode选择相同16背景／body／goal；用独立augmentation RNG对每NPC选原canonical或E26整句顺序翻转，episode内固定。既有正确编码，不调用LLM生成。原400canonical保持逐byte，diversity reference pool仍原400。
- **intervention设置：** 同原sampler的16 base角色，将其原C值在这16人之间随机置换，因而每episode C边际完全相同；不改其他四traits／年龄／职业／身体需求衰减／preferred_actions。只更新原persona.big_five.C及作者模板文字，源style／social奖励照原函数计算。该训练配置干预不是修改世界规则或评价。最多400×3=1200 C输入，原C编码仍直接用E34原数组；新800及canonical数值重复用同本地.6B／正确pool编码。
- **split：** 原20训练非C背景与5测试非C背景完全独立，所有编辑后的held背景仍不入训练；职业／年龄的源切分按原协议，不宣称新职业独立。只读取held metadata核对隔离，不能据test结果选训练。
- **执行资格：** augmentation=none必须复现原E34初始参数及first rollout全部obs/actions/reward；surface保留所有body/goal；C干预逐episode C计数同一且body/prefs逐项同一。独立augmentation RNG不消耗原sampler RNG。新编码保存文本／hash／token长度和canonical-repeat误差。
- **读数：** 固定E34 native mixed utility／needs、E32等义与跨角色响应、E33完整利益四格、E37同状态同幅度利益方向；300轮为完整预算，30/100只描述形成，不挑最佳checkpoint。保留成功与负结果；若简单增强解释充分，承认而不造方法。首批不以η未训练分数判能力。
- **阳性对照：** 上述逐byte重放、参数／source reward路径资格；canonical original输入精确不换码，C相同的变体精确复用；原作者动作空间与合法执行闭环。
- **噪声地板 + MIE：** 三训练seed／原三world全部保留，数值重复与采样方差分别记录；不设MIE、通过率或科学淘汰bar。
- **混杂审计：** C重排同时改变多NPC偏好配置，允许真实social反馈；边际与body保持但不能把全部长期效应归单一actor。source C的心理构念不独立验证，使用的是作者明确的utility参数。普通surface增强是已有方法对照，C干预也可能只是一般数据增强；新颖性须靠形成机制和跨任务预测继续建立。
- **决策表（跑之前写）：** 读完整轨迹／指标后区分表述覆盖、属性组合覆盖和形成路径；充分考虑普通解释。任何结果都更新认识而非按bar舍弃。必要时再研究训练机制，不先规定损失。
- **算力预算：** .6B数据编码一张已有空闲GPU，白天总≤8；训练先精确CPU单update计时，沿E34同小MLP CPU更快的事实，最多6独立单core CPU任务、每task完整300轮约1.5小时（以实际为准），不新建env，0付费API。raw既有cache/runs/e41_*。

## 结果
none路径与E34相同初始policy及25600首轮obs/actions/reward逐byte相同（21.50秒）；1200 C输入的400原canonical完全复用，800编辑与400重复编码共9.17秒，重复cos最小.99999105。20训练／5held非C背景交集0。六个source300轮训练任务在既有CPU环境运行，保存30/100/300全部checkpoint；原生CNN评测使用八GPU，训练小MLP沿实测更快的CPU路径。结果未完成，不提前判方法。

评价接口补充（首次增强checkpoint评价前）：复用原E34逐actor fresh观测、原三个world与全部held100、原E32固定state、原E33五base/三world完整四格。仅指定reference=同seed原No与alternative=对应增强，不改变原读数；旧harness别名no/full在manifest明确是reference/alternative，不伪称增强使用了InfoNCE。E37按original/surface/intervention三policy共同最小角度匹配，固定同原状态银行；natural端点也报告，三seed及30/100/300全部保留。supervisor三CPU并行评价，未完成manifest不会读取checkpoint；没有best选择或科学淘汰。

### 实现作废记录：surface v1（2026-10-14）
30轮三个surface policy与原No逐byte相同。源码追踪确认E26 reverse_clauses.npy只改变held100，train400是canonical副本；因此v1 sampler虽选择reverse标志，实际训练输入没变化。这是本地执行错误，三个surface结果不能作为增强无效的科学证据。已停止三个本项目surface v1训练与等待器，保存原轨迹/权重/日志，E41_surface_v1_invalid.json明确作废；C-intervention使用独立1200代码与实际变化，不受影响，继续300轮。

修正后surface v2必须先核每个train400改写与canonical向量确有差异、所有词/事实保持，仅调换同样五条人格描述顺序；记录正确pool数值重复。用新路径保存，从同seed原初始化重新完成全300轮，与原/CF同预算。不覆盖v1、不把工程错误当负结果或创新。评价器只在明确修正manifest存在后使用v2。
表面编辑精度备注：源_BF_DESC每个trait包含多个逗号分隔形容片段，E26实际是所有这些片段逆序，而非五个完整trait block逆序。修正数据精确复用E26规则、全部片段multiset/年龄职业/五trait metadata不变，held100输入逐byte保留；不将词袋一致直接升级为严格心理语义等价。编码v2资格发现固定“五片段”假设不符作者文本，在加载模型前停止，失败日志保留；v3采用原实际规则。surface训练v2的名字指有效训练版本，与编码资格v3不同。

### 属性经验与目标绑定的竞争解释对照（启动前补充）
有效surface30结果跨seed不同；C干预30的canonical收益差+.787/+1.952/+2.459，但利益方向跨seed不同，不能从早期提升归因某种机制。增加unbound-code对照：使用与intervention完全相同的16 base IDs、C向量置换/独立augmentation RNG/每episode文本C边际，但环境persona的真实BF.C与原No全部保持；body/preferred/其他traits也不变。因此仅扩大输入属性组合覆盖，没有把该C输入绑定到对应利益配置。不是新环境reward或方法，而是普通“输入多样性/正则化”与“匹配属性—利益经验”的区分。

三个预定seed42/43/44，NoInfoNCE、原全部PPO/div/300轮/30-100-300保存；原始No、有效surface、matched intervention都继续，不筛分支。先一轮控制：初始policy、obs/actions/reward与原No逐byte相同（FiLM初始persona调制中性），但实际变码导致首次PPO更新权重不同；C向量选择必须与matched intervention相同，环境C实际保持原值。记录文本C/环境C，不误写它们匹配。该配置故意打断训练绑定，不能拿其失败当自然NPC失败；任何混合/正向/负向结果均保留。三CPU单线程原300轮，白天八GPU继续原生强LLM实验，不为小MLP强占更慢的GPU。
unbound评价补充（首次控制checkpoint评价前）：原/有效surface/matched intervention的primary三policy共同幅度比较保持v2协议；unbound与原No另做原生/等义/完整四格及E37两policy匹配，不回头改变primary幅度。跨四条件比较采用相同natural文本端点与原生收益；不同比较pool的matched数值不可直接拼成方法排序。全部30/100/300与三个seed保留，metadata明确旧no/full别名的真实条件。

### 补齐目标分布竞争解释（启动前登记）
matched比unbound好的结果也可能来自训练目标配置扩大，而不只是文字—利益绑定。因此补goal-only：和matched完全相同的实际C置换/边际/目标/身体/偏好/原sampler，却保持原canonical C输入。与原No、unbound、matched构成2×2（input是否置换×真实目标是否置换），surface另作普通表述控制。三个seed/300轮/30-100-300，全部原优化参数不变；分析canonical原生收益及natural文本C完整四格/功能响应的interaction，而不把不同比较pool的matched幅度混用。目标与输入刻意不匹配的诊断cell不作自然角色失败论据。

先一轮正控制：goal-only与matched初始policy及25600obs/actions/reward必须逐byte相同（初始FiLM中性），实际输入仍original、environment C选择完全与matched同一、首次更新权重应不同。采用既有harness的冻结专用版本，不再修改其他进行中训练脚本。三单core CPU，已有八GPU用于强本地模型闭环，不新增环境/API/世界规则。该cell用于区分reward-config覆盖/输入覆盖/匹配经验，不能因结果不理想舍弃；所有四cell完整预算保留。

全部完整预算对照完成：surface/matched/input-only/goal-only四条件×3seed，均300轮，每次7680000transitions，共12新训练／92160000transitions。30/100/300所有读数归档E41_complete_factorial_all_stages.json，无挑选。300轮binding interaction的原生reward差为[8.1212,2.6036,-3.1668]，逐背景四格保留，不由此自动判科学成败。原作者给定reward诊断不包装“利益控制”新题；更具体人物／社会目标／执行解释沿E35/E44/E45继续，C01不升级。
