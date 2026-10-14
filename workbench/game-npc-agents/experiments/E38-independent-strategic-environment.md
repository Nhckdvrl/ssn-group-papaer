# E38：PCSP外部原生战略环境恢复（2026-10-14）

- **状态：** RUNNING；原生引擎、作者默认和强配置及正确编码强配置全部训练完成，进入完整原生行为评价。
- **类型：** REPRO／D1；不是为了配额新建idea。
- **对应：** C01原生强基线，I02的任务边界与P06；不改变工作台状态。
- **问题（一句话）：** 在不按BF直接赋予style奖励的原Melting Pot社会博弈中，PCSP的角色条件、作者实际行动倾向和环境利益怎样进入政策与评价？
- **设置：** PCSP pin5420f7b，已有完整upstream MeltingPot2.4.0；原personas_v0的10训练／2held角色，原Qwen编码资产存在，原trained CNN weights未找到。优先恢复commons_harvest__open，PD仅在具体问题需要时扩展。原reward／地图／动作不改，不给角色臆造“唯一正确”行动。
- **环境：** 现有Conda lightwam（Python3.10、NumPy1.26.4、Torch2.7.1cu128）可使用原DMLab2D1.0.0的cp310 wheel；项目独立依赖overlay，不改基础env、不影响E34。fgvd Py3.12不兼容原1.0.0 wheel；虽然1.0.2支持Py3.12，先保留原engine版本。依赖版本差异、源路径和运行成本均记录。
- **先做：** CPU完整原生episode，合法动作／RGB变化／奖励／引擎event同步保存；复现同seed action tape，检查seed真实传入路径。随机政策仅为引擎资格，不称强NPC能力。读取作者CNN训练和semantic prior／InfoNCE／diversity路径，确认哪些角色行为已有训练监督。
- **读数：** 原生episode长度／每角色和群体return、合法动作、RGB／事件与真实采集成本；作者角色控制评价与ID检索分开。只有成本和来源清楚后才具体登记强基线训练配置，不能短训一次后判问题无价值。
- **阳性对照：** 静止与合法移动action tape、可重复world seed、原引擎苹果采集／zap事件与reward；不得将随机政策表现当人格负结果。
- **噪声地板 + MIE：** 记录确定性重复／episode随机性及计时，不设MIE、通过率或科学淘汰bar。
- **混杂审计：** 原wrapper接受seed但目前源码未见实际使用，待追踪builder；不先称作者seed实验无效。语义persona corpus是作者给定的，action_prior是否启用须逐路径核对。原reward与角色数、候选pool、均衡采样及评价人物的差异不能混作单一方法效果。新依赖／GPU与论文平台不同如实记录。
- **决策表（跑之前写）：** 来源和原生episode读清后，依据观察选择与人物—利益问题相关的强基线复现；不为矩阵整齐铺开所有substrates。不以工程安装失败或随机表现决定科学价值。
- **算力预算：** 先CPU单完整episode＋一次确定性重复；依赖复用现有Conda和项目overlay。只有确认CNN计算更适合GPU后用获授权空闲单卡，白天总≤8，不占用其他任务；0付费API。原始数据在既有cache/runs/e38_*。

## 结果
尚无科学结果，安装与源码事实分开记。

运行前成本测量补充：使用公开可执行run_pcsp_meltingpot_clean.py默认CNN＋原12persona/Qwen资产，单个完整source update=4env×256step×7agents=7168transitions，CPU与获授权空闲GPU1各测一次。保留PPO四epoch／四minibatch、lr2.5e−4、projection1e−4、trajectory3e−4、λcons=.5／div=.1、γ=.99／GAE=.95／clip=.2／entropy=.01，collective_reward_alpha=0（源默认，不增设角色reward）。这个单update只用于耗时／执行核对，不作为方法或人格效果。PHASE5报告的balanced／candidate-pool脚本在当前公开checkout尚未定位，不能把clean分支称为该报告全部配置的精确复现。

CPU原生恢复：DMLab1.0.0已运行完整episode，原引擎独立自然终止，全部动作合法，NOOP窗口RGB静止、FORWARD窗口变化，苹果／zap事件和return均记录。两次同Python seed的实际builder env_seed与settings hash相同但episode不同；继续记录Lab2d.start seed界定剩余随机性，不把它作为科学淘汰条件。v1在pip尚未完全落盘时缺chex；v2原生episode完成但bytes事件JSON失败，均属本地接入记录，已修无损序列化。

### 完整CNN基线配置（运行前登记）
原完整update实测GPU19.7秒、CPU81.1秒，GPU适合此CNN分支。因此现在运行三预定seed1/2/3×Full／NoInfoNCE，源默认500000 agent transitions（7168整update自然达到501760），不在短训后作科学结论。沿用源四epoch、4env×256、λdiv=.1；No仅用原--ablation-no-infonce，其他参数不改，默认collective_reward_alpha=0。三个空闲GPU0/1/2，每卡两个独立小CNN进程，物理卡总3≤白天8，线程1；已有六CPU Mini-Inzoi训练继续，无跨节点同步。预计总约2.4GPU进程小时，实际以原log为准。

这次定义为可核验的public clean CNN baseline，不冒充PHASE5所有配置：已隔离fetch作者明确分支research/meltingpot=4fbbffa，仍未找到run_phase5_balanced.py／cleanrl_ppo对应实现；报告、分支与已执行代码分开。12×1024源编码asset存在且单位范数／diag对应，但完整generation instruction未找到，暂保持作者原资产并显式记录hash／来源不确定性。训练期间不据此解释细粒度文字编辑因果。

环境随机性：同build seed1026200207、同settings SHA、同Lab2d.start seed704199477仍有不同RGB与return，v5动作tape完全相同而reward不同。尚未排除native／Lua初始化排序等解释；不把失败归给人格或论文。原训练分支按原设置运行，统计按独立训练／环境重复处理，不声称pair-wise byte replay。下一步看独立原生轨迹、真实收获／zapping／状态机会与角色语义，不用内部检索替代。

### 作者实际强设置补充（运行前登记，保留默认500k结果）
进一步核对cog_clean_summary.json，作者的commons_harvest强设置明确为1M agent transitions、team-mean shaping alpha=.1、五Full seed1–5；该文件的NoInfoNCE只汇总一个条件。此前500k／alpha0是可执行默认恢复，不能替代这个强设置，也不将其训练日志低reward判人格失败（源mean_ep_reward只累加当前rollout片段，不是完整episode return）。

现在另从头执行作者1M／alpha.1设置，固定seed1–5的Full与NoInfoNCE均运行，10任务。原source优化器／CNN／PPO／λcons／λdiv不改，作者alpha控制只影响训练reward，世界规则与后续评价仍用原生raw reward；默认500k结果全部保留并作为训练目标背景，不拿它冒充强配置。GPU0/1/2分摊10个独立小CNN，总物理3卡；资源允许GPU3留给本地NPC。单进程预计约5–15分钟（已观察后续update比首update快），复用现有conda／overlay，不新建env。初始训练与环境随机性范围、配置hash、实际steps全部写manifest。

评价以完整原生episode／真实动作／采集与zapping事件、raw个人与群体return为主，并单列内部ID读取。不会按训练日志、检索比例或自设bar停止/舍弃。任何自然角色偏好要结合作者明确文字、可见机会与其他玩家响应解释。

### 源码检出纠正与编码资格（运行前补充）
发现初始clone采用sparse checkout，只materialize research子树。Git树明确含根src/scripts；已在隔离4fbbffa checkout补齐，PHASE5 balanced/candidate pool和build_persona_embeddings_qwen.py实际均已公开。此前“尚未定位”的原因是本地检出范围，不是作者缺源；该不确定性撤销，旧记录保留并指向本修正。

根PHASE5为另一实现：8异步env、concat conditioning、动作+reward的独立GRU／投回原1024维embedding、train-only candidate pool、persona-balanced采样；其InfoNCE路径不经过离散action sampling回到policy。不能与research下CNN-FiLM共享projection／CNN梯度混作一套。源文件明确讨论这种解耦，属于作者已有机制owner。

编码生成原模板和FP32配置已定位。脚本设置left padding，却用attention_mask.sum−1作为绝对列索引；需用真实cache数值验证原生成路径，并与标准last-real pooling及单条编码比较。只作实现资格和强基线修复，不拿已有pooling算法当新贡献。下一步GPU0局部.6B模型编码原12文本，原／正确pool用同一hiddenstates，保留所有向量／长度／source hash／公开asset比对，不调用付费API。

### 正确编码的完整强基线（运行前登记）
E38数值资格完成4.70秒：公开12向量与作者原脚本逐人cos≥.999999999995；left padding下11/12行取到非末个真实token，改为标准last-real后公开向量cos范围.227–1，正确batch与单条最大差5.59e−7。工程pool修复有明确已有算法owner，不作为创新。

保留已经完成的作者原asset：五seed×Full/No各140更新、1003520transitions。现在仅替换为同模型／同原instruction、FP32正确pool的12×1024资产，再做同五seed×Full/No、同1M／alpha.1／相同全部优化设置；不改world或raw评价reward。GPU0/1/2独立小CNN共三物理卡，GPU3继续自然NPC。这样后续方法比较立足真正强的可核验语言编码基线；旧结果作为完整source reproduction保留，不用错码造科学gap。

### 完整原生政策评价（运行前登记）

主评价为正确编码五seed×Full/No；公开编码同样五seed×Full/No完整保留，作为来源敏感性对照。每政策采用六个预定focal persona：cooperative_sustainer、selfish_harvester、cautious_observer、aggressive_zapper，以及原heldout fast_mover、spinner。其余六玩家固定使用reciprocator、explorer、territorial_defender、risk_seeking_raider、cleaner_helper、free_rider；每局七个不同人物。三个独立world seed38011/38012/38013，focal位置随seed循环以免固定出生槽位。总360个完整episode，不筛种子；世界按原引擎自然终止。原训练使用的随机Categorical政策不改，不使用action_prior或手工角色奖励。

读数分别为：完整raw个人与团队return、逐人真实苹果采集事件与zap命中、fire尝试及ready条件、移动/旋转/静止频率、资源余量轨迹、真实episode长度。内部GRU的ID读取单列，不视为独立语义或利益评价。每100步保存同一focal RGB下全部12原文条件的action probabilities，使状态条件化响应与自由轨迹分开；保存WORLD.RGB用于人工复核。原人物表达在这里是固定作者输入，MLP政策没有语言自述／意图输出，不能冒充三层语言测量。

先跑一个完整训练政策episode计时、确认事件解码与raw reward一致，然后并行。跨条件即使相同Python/native seeds也不声称世界byte相同（E38已记录剩余引擎随机性）；分析按独立train seed与world重复，分别汇报局长归一化率和完整return，不将自然局长变化隐掉。没有MIE、通过比例或淘汰条件。source轨迹、完整动作与reward、图像和概率仅保存在既有cache。

资源核对：fvcrc10/12/15有其他任务，保持不动；fvcrc20与fvcrc21各四卡均空闲。复用共享Conda lightwam与已有overlay；原生单局核对后用这八卡执行独立评测，物理总卡数≤8，不跨节点同步。E41小MLP六任务继续CPU（已测更快）。每worker保留host/GPU/源码与policy/embedding hash。
