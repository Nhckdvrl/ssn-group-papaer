# E01｜强基线与共用评测

- **状态：** PLANNED；未运行。
- **对应：** 建设与R1–R5；不强挂论文claim
- **来源：** S1–S4及ASSETS原生协议。
- **阳性对照：** 先在熟悉ID任务检验native表现；真实轨迹回放和目标匹配检查。
- **噪声地板：** 独立train/eval/planner种子分开；探索可少seed，主结果再增加独立训练seed与区间。
- **决策表（跑之前写）：** 基线偏弱→查加载/协议/训练量并补强；原生可用→开展对应方法；诊断不足→补必要字段，不冻结所有研究。

## 问题
建立足够强的对照和可复用读数，使新方法收益可解释。

## 首轮方案（可在运行前修订）
至少一个trainable baseline和一个按需要选择的强参照。保留native协议，另存共同eval manifest。分开input、data、train budget、goal source、H/K、action repeat与cost。轻量记录候选与实际结果，不先建全功能logger。允许原生复现与方法试验交叉推进。

## 读数与资源
任务成功/代价、训练与推理成本，必要时固定候选regret/真实终点编码；大trace节点保存，git只存manifest/hash。

## 结果与修订
尚未运行。实际执行前补code/data/config、种子、授权资源与运行预算。探索性改动允许，必须留版本；发现数据/接口错误时修正该运行，不自动关闭母问题。

## 2026-10-04｜AD-WM完整发布模型接续（运行前）

I14/E20的raw inverse只是组件对照，新增官方AD-WM完整模型参照以避免弱替代品。官方代码7c27ebfdc4a2ba8e5a16268f2e4aa852fda72144，HF31ab745259718946aa83f2d6df19dfebb0c8ebd4；仅下载TwoRoom/PushT seed3072与config/manifest到标准HF缓存，不拉Cube/Scene全套。先在专用新Python进程AD代码namespace加载，核对object class/predict residual/inverse+MI heads/config/hash；同真实pixels/actions的cached rollout与AD原生get_cost parity。不能在已经import LeWM或Fast的jepa/module namespace里pickle加载AD，避免同名类静默套错predict。若dependency冲突，先在现venv做最小隔离import，不能改正在运行训练的环境。完整checkpoint加载仅工程证据；数值replica/官方eval与fixeddata同数据训练未完成时，不claim战胜AD-WM。新48source开发集released训练episode未知，不称unseen于官方模型。

完整AD CPU控首次失败于native input contract：info缺dummy action，官方get_cost对goal.pop(action)触发KeyError；此前object class/residual/inverse/MI/strict/finiteness加载已过。原源码/log/failure durable20261004-E01-adwm-cpu-preflight-failed，未生成方法读数。retry1补真实原生输入dummy action，不变dataset/source/动作/模型，不覆盖旧failure；不把接口缺key误判方法预测不一致。

AD-WM retry1完整CPU控PASS：TwoRoom/PushT两个完整object均exact官方JEPA/module namespace、residual formula原式exact、完整inverse+MI heads、strict321keys/19,220,654 params、全部tensor finite、H3+future5原生cached cost导航差0、操作maxabs9.5367e−7（rtol/atol1e−5内）。两checkpoint SHA与官方MANIFEST一致；未删aux后冒充完整加载。portable E01_20261004_adwm_cpu_controls.json，raw durable20261004-E01-adwm-cpu-preflight-retry1，原missingaction failure保留。后续GPU完整闭环/同数据训练仍待执行。

GPU完整参照（运行前）：专用AD namespace fresh进程，官方seed3072 TwoRoom/PushT完整object，先用实际像素/动作/native_control校对，再保存E20全部held12×12真实候选读数（Nav position成功<16；Push原生pos+角成功）。TwoRoom在同新48source development/100newsteps/H25EX25上跑physical与native接口两个完整controller，300/30/30/共同planner resetseed105400+j×100+d；完整真实actions/state trace与statehash不可变守卫，失败保留。不混两发布trainseeds或删辅助head后冒充完整SOTA；当前两任务均同publishedseed3072，训练数据/充分训练量与E20不匹配，因此仅external strong reference，不做同数据优劣claim。原paperbenchmark协议未运行，不能称完整paper numeric reproduction；新scope/data/planner参数全存raw。

GPU reference运行源码7c45a38f775b889386110a4090ec8deb9e0b9c64b53c2ea510a31689e76b2d38；两CPU原生控通过后启动专用RTX槽，新raw/durable20261004-E01-adwm-reference-RTX-s3072。没有先读其query读数改方法或目标。

完整AD-WM reference已DONE：原native近24/24、远18/24，physical20/24、8/24；共96导航episode全部保留，两task各12offlinequeries（Nav12/12、Push3/12）。RTX GPU native cost maxabs均0；CPU Push约9.54e−7的旧读数保留不混写。完整trace SHA/初始位置/原native距离阈值成功复算/源checkpoint重新hash通过，见E01_20261004_adwm_full_reference.json。一个发布trainingseed/未知未匹配训练data，不能称同data loss增益或原paper数字复现；它是必须面对的full strong reference，而非raw inverse头替代。
