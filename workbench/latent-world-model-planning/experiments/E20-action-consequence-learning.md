# E20：有限数据下真实动作后果学习（2026-10-04）

- **状态：** RUNNING；Stage0/bank44与joint CPU/CUDA预控DONE，Stage1a方法训练开始；native闭环尚未运行。
- **类型：** PILOT
- **对应：** I14、P04/P10，R1/R2/R4。
- **问题（一句话）：** 同样有限真实分支数据下，后果相关训练/表示机制是否超越充分训练的普通预测与inverse，并改善新动作/新目标控制？
- **设置：** 原生SWM0.0.6 TwoRoom/PushT，既有venv；Stage0每task从既有100训练episodes随机固定6个，seed104200，合法physical action Box[-1,1]^2。每anchor从数据public state的t−10 freshreset/setter开始、统一10步实际合法warm prefix，实际history帧−10/−5/0与过去actions保存；不是精确原dataset hiddenstate。source selection无reward/goal/success/features。12个25-step branches全执行：zero/重复zero/factual clipped/±x/±y/smooth/negative smooth/random constant/IID/reverse IID；重复zero是恢复阳控，训练时须排除重复控制。再单独重复首branch验证。preflight只每task1anchor，完整batch每task6，预控失败不看方法效用修改。
- **读数：** 所有primitive pixels/public state与Push agent/block velocity/angularvelocity/force/torque诊断、history/action/5:5:25 future、action bounds；重复轨迹的exact error、不同合法commands的完整state/未来分歧。不以末帧或position相同宣布full equivalence，不把branchpairs当独立samples。Stage0不比较方法success，不claimnovelty；完整小bank后模型只能读history/actions预测全部branch，再由真实后果评价选择误差，另做native闭环。
- **阳性对照：** identical action/freshreset/warm prefix重复必须全部pixel/state/flags一致，跨branch history一致；different-action真实state差作为measurement阳控，若没有差异报告，不筛anchor。标准环境步进即使done仍固定记录25步（训练transitionbank非episode success评测），flags原样保存，无reward选择。
- **噪声地板 + MIE：** deterministic重复maxabs=0且pixelexact；非0则暂停当前数据bank查restore/integrator，母问题不关闭。Stage1至少3固定data trainseeds和新的锁定评估集合，数值阈值依据真实noise另锁，不能用数千pairs提高虚假n。
- **混杂审计：** 采样/实际动作都是physical合法域，模型入口才normalize；训练state标签权限全部一致，物理量仅诊断；source warm重新生成不声称原始轨迹复制。12branch全执行与fixedselection ledger先写，不读hidden outcome挑数据。原16/32/48均开发集，后续确认另锁；此144branches仅Stage0数据/接口试跑，不是完整方法证据。
- **决策表（跑之前写）：** 重复失败→查数据/接口后新unique retry、原failure保留；存在legal差异→同数据plain/effect/deterministic-probabilistic inverse连续训练；只有pixel相似但dynamic不同→保留history/多步标签，禁止合并后果；普通预测或概率inverse已解决→接受强baseline，不包装loss；effect改善error但不改善nativecontrol→调整任务/预测/接口，不只lambda sweep。
- **算力预算：** Stage0 CPU，无GPU训练，full 12anchors×(12+1)branches×(10warm+25)=5460env steps；preflight2×13×35=910steps；uint8 nodecache，大raw不入git。

## 后续训练设计（尚未运行，执行前继续锁定实际config）

同一legal branch bank/充分训练base、samewarm history、equal branch exposure与optimizer isolation；联合训练encoder/predictor而非永久冻结。首个机制为sameanchor-centered预测与stop-gradient真实后果匹配；这只是残差方差重权，不是novel贡献。普通prediction、等weight全局MSE、匹配target-detach、deterministic/probabilistic inverse及最近AD-WM结构是强对照。继续开发history/action-dependent effect code必须由首轮结果驱动；state-only线性降秩可能误伤离开障碍的作用，不预设正确。

## 结果

见下方按阶段追加。raw完整bank、code/hash/seed/训练权限与失败写回；不升级science claim。

Stage0首次CPU预控仅在数据入口失败：PushT路径被错误写成pusht.h5；没有simulator/outcome读数。原failure、log和失败源码保留于20261004-E20-legal-effect-preflight；重试改为读取已有native config的实际dataset路径pusht_expert_train.h5，记录config SHA，不重新采样/改seed/挑anchor。source/config/fileexists在生成ledger前核对；retry1为unique raw，不算方法负结果。

Stage0 retry1真实CPU预控PASS：两task共24branches/910env steps，每branchhistory相同、duplicatezero和最后fresh重复全primitive pixels/诊断state/flags/reward完全一致；源码7d721c4869cc8412f477b77d4851310cce472f40015ef06a4ed10ec8c3ad1564。实际结果只证明collector/合法动作重复契约，不证明fullstate等效或方法作用；保留firstfailure。完整6×2anchor/144branch全bank沿相同seed/协议开始，new raw/durable `20261004-E20-legal-effect-bank`，不再挑anchor。

Stage1数据协议（生成前）：Stage0完整12anchors/144branches/5460steps、全重复exact已落盘；不是方法证据。扩大每task固定44个原100训练episode，由同seed无replacement选择，first32为新增branch训练、last12为held-out branch query development；所有WM baseline可能已见这些sourceepisodes，不能称unseen states。每个anchor保留12候选全真实outcomes和fresh重复，共2×44×13×35=40040env steps，全成本计入。训练排除branch1重复控制，所有方法相同rawbank、相同train/eval split，val outcomes只label不参与sample selection；CPU不加新GPU。新collector仅可配置anchors6/44，其余契约不变，原Stage0源码/hash保留。raw/durable `20261004-E20-legal-effect-bank44`。

Stage1a训练matrix（执行前锁定，尚未训练）：Nav先用固定BASE100充分训练u5650的三个独立source seed，不永久冻结encoder/predictor；新branchbank每task44里first32训练/last12新branch query开发；每anchor11有效branches，zero重复branch1不用于训练。每job fresh AdamW/LR5e-5/WD1e-3/clip1/bf16，2000updates、8anchors×4branches，5个sliding three-frame teacher-forced futuretargets+.09 SIGReg、same sample RNG104800+seed/labels/actions。五arms PLAIN / GLOBAL-SG(额外整体现实target-detach MSE) / CENTER(同anchor中心化额外target-detach MSE，λ1) / DET-INVERSE / PROB-INVERSE(raw10维动作embedding组件，λ.1；后者heteroscedastic Gaussian NLL)。GLOBAL-SG对齐额外loss和SG，不把loss放大当机制。两inverse只是显式组件强对照，不是完整SMWM/AD-WM复现，不能用它们被击败宣布战胜近邻。

固定u0/600/2000：每个held12anchor预测全部12实际候选；goal候选ID=2+anchor%10只提供目标图，不向model读物理future；actual候选轨迹对应同共同warm状态，position成功阈值16与GTdistance作为offline读取，不把latentL2当truth。12anchor为独立分析单位，不把12×12pairs扩n；不是native闭环或confirmation，尚无方法science claim。随后必须physical-bounded CEM采样/评分/eliteupdate/执行全部一致的新native闭环（含原nativecontrol参考）和新锁定goalset；未经这步不称方法成立。CPU实际joint gradients/loss hand-recompute/中心误差分解/原生H3→5future索引控全部通过后再GPU。source SHA e8b2dee8f8aaa660022c9492c5e03f99c3ff9cca65f6f0c370e2466da550b26e，源码/数据ledger执行后冻结。首seed0五arms并行，seed1/2对应各独立充分训练source继续，不筛seed。

Stage1a root全文审/actual CPU和CUDA/bf16预控全部通过：五方法jointgradient/freshoptimizer firststep、source不可变、center与global SG误差手算/decomposition、H3历史+future5和原生rollout一致、全部held12完整bank queryeval且eval权重/buffers不变。source e8b2dee8f8aaa660022c9492c5e03f99c3ff9cca65f6f0c370e2466da550b26e。全controls/脚本/log已durable，portable E20_20261004_joint_training_preflight.json。将五arms各接source0/1/2（base devsuccess38/19/36全部保留）；source1弱不筛，方法对其增益必须面对PLAIN同data/update。五独立A100任务槽，各顺序3独立source seed，stage同nodecache/archiveSHA cb27e11df5653052d3fe6967f6c325258cf3824e1182ff80851c079ad07eb5f0，模型HF不同目录；A100 timing不混RTX。首GPU真实step确认后再扩大其余任务，不占已在用卡，source/selector/config固定。

A100实际运行扩展：PLAIN首source0已到850updates并保存固定600快照，无failure；首job完成真实I/O/训练/完整candidate query控制后，第二GLOBAL-SG slot启动，待其首步确认再扩至其余三arms。source0的单partial读数不用于筛方法；三个source和所有五方法既定均保留。
