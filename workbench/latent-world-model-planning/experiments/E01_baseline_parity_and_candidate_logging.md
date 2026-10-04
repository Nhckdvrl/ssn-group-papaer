# E01｜强基线与共用评测

- **状态：** RUNNING；完整发布AD-WM参照DONE，同数据三arm×三seed重训进行中；不称论文数字复现。
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
最新状态见下方Stage0及实际config/预控/进程记录；此前未运行段落是原设计历史，不覆盖当前训练。

## 2026-10-04｜AD-WM完整发布模型接续（运行前）

I14/E20的raw inverse只是组件对照，新增官方AD-WM完整模型参照以避免弱替代品。官方代码7c27ebfdc4a2ba8e5a16268f2e4aa852fda72144，HF31ab745259718946aa83f2d6df19dfebb0c8ebd4；仅下载TwoRoom/PushT seed3072与config/manifest到标准HF缓存，不拉Cube/Scene全套。先在专用新Python进程AD代码namespace加载，核对object class/predict residual/inverse+MI heads/config/hash；同真实pixels/actions的cached rollout与AD原生get_cost parity。不能在已经import LeWM或Fast的jepa/module namespace里pickle加载AD，避免同名类静默套错predict。若dependency冲突，先在现venv做最小隔离import，不能改正在运行训练的环境。完整checkpoint加载仅工程证据；数值replica/官方eval与fixeddata同数据训练未完成时，不claim战胜AD-WM。新48source开发集released训练episode未知，不称unseen于官方模型。

完整AD CPU控首次失败于native input contract：info缺dummy action，官方get_cost对goal.pop(action)触发KeyError；此前object class/residual/inverse/MI/strict/finiteness加载已过。原源码/log/failure durable20261004-E01-adwm-cpu-preflight-failed，未生成方法读数。retry1补真实原生输入dummy action，不变dataset/source/动作/模型，不覆盖旧failure；不把接口缺key误判方法预测不一致。

AD-WM retry1完整CPU控PASS：TwoRoom/PushT两个完整object均exact官方JEPA/module namespace、residual formula原式exact、完整inverse+MI heads、strict321keys/19,220,654 params、全部tensor finite、H3+future5原生cached cost导航差0、操作maxabs9.5367e−7（rtol/atol1e−5内）。两checkpoint SHA与官方MANIFEST一致；未删aux后冒充完整加载。portable E01_20261004_adwm_cpu_controls.json，raw durable20261004-E01-adwm-cpu-preflight-retry1，原missingaction failure保留。后续GPU完整闭环/同数据训练仍待执行。

GPU完整参照（运行前）：专用AD namespace fresh进程，官方seed3072 TwoRoom/PushT完整object，先用实际像素/动作/native_control校对，再保存E20全部held12×12真实候选读数（Nav position成功<16；Push原生pos+角成功）。TwoRoom在同新48source development/100newsteps/H25EX25上跑physical与native接口两个完整controller，300/30/30/共同planner resetseed105400+j×100+d；完整真实actions/state trace与statehash不可变守卫，失败保留。不混两发布trainseeds或删辅助head后冒充完整SOTA；当前两任务均同publishedseed3072，训练数据/充分训练量与E20不匹配，因此仅external strong reference，不做同数据优劣claim。原paperbenchmark协议未运行，不能称完整paper numeric reproduction；新scope/data/planner参数全存raw。

GPU reference运行源码7c45a38f775b889386110a4090ec8deb9e0b9c64b53c2ea510a31689e76b2d38；两CPU原生控通过后启动专用RTX槽，新raw/durable20261004-E01-adwm-reference-RTX-s3072。没有先读其query读数改方法或目标。

完整AD-WM reference已DONE：原native近24/24、远18/24，physical20/24、8/24；共96导航episode全部保留，两task各12offlinequeries（Nav12/12、Push3/12）。RTX GPU native cost maxabs均0；CPU Push约9.54e−7的旧读数保留不混写。完整trace SHA/初始位置/原native距离阈值成功复算/源checkpoint重新hash通过，见E01_20261004_adwm_full_reference.json。一个发布trainingseed/未知未匹配训练data，不能称同data loss增益或原paper数字复现；它是必须面对的full strong reference，而非raw inverse头替代。

## 完整AD-WM同数据训练分解（2026-10-04，运行前）

对应P04/I14与R1/R4：发布full reference强，但训练未匹配；需要区分residual结构与learned-action inverse/normalized recovery本身。锁定同BASE100的100episodes/9295rows/7295 clips、原norm、四frames0/5/10/15与20真实actions、joint encoder/predictor、fresh AdamW5e-5/1e-3/clip1/bf16/128batch/5650updates。三独立trainseed0/1/2全部保留；同各seed backbone303初始化和shuffle33000+seed。三arm ABS / RESIDUAL / FULL-AD，各seed顺序完成全部arm，绝不把已训练absolute权重加residual当同initialfunction。ABS/RES共有初始化weights，函数差异是显式结构干预。FULL-AD增加官方两个完整192dim embedding-recovery heads，目标SG/batch ddof0 normalize/fixed-unit NLL按192维sum/KL.01，权重inverse.1/MI.01/SIGReg.09；不用raw10dim替代。

直接从固定官方train.py提取pure paper_forward/inverse_features/normalized_recovery_loss三函数，保留源码SHA；不安装完整Lightning到live环境。模型组件仍官方AD namespace，严格303公共tensor/新增headkeys校对。恒定LR是本地匹配训练协议，非原Lightning scheduler数值复现。CPU/CUDA预控须通过loss逐项手算、ABS与原LeWM源objective一致、SG目标无梯度、fullencoder/predictor/action+heads梯度finite/freshoptimizer源state独立、H3+future5官方cost parity、正确cache真实索引；然后启动九独立single-GPU训练。模型与optimizer/RNG存HF，训练raw/cache本地；节点render有1LSB差故训练不进行simulator efficacy评分。完成后在原RTX用同新48 wholeepisodes/同plannerbudget比较所有九model，两个接口均面对强参照；fixedu5650未完成前不挑checkpoint。

主读数：matched native success、新envsteps、same-bank真实candidate regret（开发readout）及独立trainseed原数；每pair episode/source CI，不扩candidate为n。阳控ABS回到原同data训练实现、officialloss手算；噪声baseline38/19/36说明不筛弱seed，数据/encoder维度间MSE不横向排能力。决策：FULL-AD稳定胜RES→进一步动作后果/数据组织设计；只RES有效→识别结构效应；均不胜充分plain→改变监督/表示/数据机制，不扫lambda。第一批为complete-method baseline calibration，不是novelty确认。训练预算九×5650，四A100独立slot至多，先实际单step/峰值再确认并发；不占其他工作。

GPU启动前再校对：CPU实际完整loss/gradient控制通过；A100初次GPU预控在构建初始化对比处失败（没有训练步或效用）。源303 saved-init完全保留，不能要求不同CPU的seeded构造浮点结果bit-exact；新版每arm显式strict-copy同一保存的initial303 tensors，随后逐tensor exact断言，记录constructor mismatch数量与saved-init SHA。不是用不同initial放宽公平性守卫。old CUDA失败log/源码durable保留，retry3实际CPU+CUDA再跑后训练。

最终CPU/CUDA retry3全部PASS：ABS/RESIDUAL/FULL-AD/VGIQL-JOINT/VGIQL-SEPARATE actualbf16 loss/手算/finite梯度/fresh step、learned-action target SG、Bellman absorbing/duplicatepixel语义、Sep完整两阶段、源three savedinitial加载exact与原生H3+5future成本maxabs0。代码SHA0400260fc47d21629414582d266eb39bca47693905f118b6e1782cdff666d077，GPUconstructor74/75tensor不bit-exact但saved303权重显式strict-copy之后全exact。实际启动同A100节点四独立slot：source0/1队列已真实1900/500updates、各14.8GB/95–97%利用率，1→2没有failed或共享数据stream；再启动source2和value队列到4，各node-local同41MB压缩cache解压1.4GB、manifest/原7文件SHA验证。三source每条依次ABS/RES/FULL-AD，共九5650；value sequential JOINT/SEP共二5650，全部完成前不筛方法/seed/readout，所有model/HF/raw unique。不是novel方法confirmation或跨节点simulator评测。
