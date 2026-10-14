# E38：PCSP外部原生战略环境恢复（2026-10-14）

- **状态：** RUNNING（依赖／源码恢复，尚无训练或科学结果）。
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
