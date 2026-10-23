# 矿区D：Baseline登记与比较边界

更新：2026-10-22。本页登记**实际运行的系统及其研究角色**，不按模型名字数量统计进展。模型/数据完整revision、下载和原始输出路径以[ASSETS](ASSETS.md)为准；逐次配置以run metadata为准。所有D实验属于原Game NPC Agents工作台，没有另开工作台。

## 已完成的比较

| 实验 | 任务与实际样本 | 已运行系统 | 评价及研究用途 |
|---|---|---|---|
| D-E01 | ArcANE 64完整probe / 205phase / 6作品 | Qwen3-8B、ArcANE-8B-DPO；V与A上下文 | 原生APF/RPF/RAE/PTF提示，本地Qwen3-32B评分；现成阶段表演与后训练参照 |
| D-E02 | LongEvo 64下一轮问题 / 24角色 / 4长程语料 | Qwen2.5-7B-Instruct；Base、RP、NR、PHASE文本状态 | 原生Char/Sem提示＋原句NLL；状态供给用途。状态内容及tokens不同 |
| D-E03 | ArcANE嵌套25probe / 81phase | 两8B及Qwen3-32B；V/A/S | 容量与普通近期摘要。**旧Monte S无效，当前有效S使用D-E07纠源表** |
| D-E04 | EvolvingWorld公开训练资产64状态更新 / 8作品 | Qwen3-8B、Qwen3-32B；原生与固定一句主体提示 | 发布更新flag、完整PUF及人工案例分开；通用更新能力与简单提示恢复 |
| D-E05 | 同D-E04的64输入 | Step5 Token Plan原生状态更新 | 强普通更新参照，非专用EW模型；65实际请求含1恢复 |
| D-E06 | 29角色×8发布顺序更新；87后续问题 | Qwen3-32B更新：逐步发布前态T、递归R、普通递归摘要S；三角色消费者 | 五种状态的原句预测与生成案例；共有当前动机，尚非自主目标形成 |
| D-E07 | 同25probe / 81phase，Monte来源纠正 | 同S信息→Qwen3-32B普通人物整理C；三消费者 | 内容组织是否帮助实际阶段行为，额外教师成本单列 |
| D-E08 | 同81逐字一致整理输入 | Step5普通整理C-Step；两个8B消费者 | 同信息强教师参照；82实际请求含1恢复，未测32B消费C-Step |

完成报告：[D-E01–05](results/D-OVERNIGHT-REPORT-2026-10-22.md) · [D-E06–08](results/D-CONTINUATION-REPORT-2026-10-22.md)。同名指标也须匹配相同cohort和judge；不将ArcANE与LongEvo原始分数混合成排行榜。

## 预算停止、未完成的参照

**D-E09：** 六个既有预选角色、15完整probe/47phase，Qwen3-32B从完整原生前缀逐窗形成普通人物记忆，再给两8B表演。301窗口分两条独立队列，固定来源/查询边界、统一预算恢复；每worker有4.5小时停止启动新batch的预算保护，总卡预算见[实验卡](experiments/D-E09-full-prefix-character-memory.md)。与近期摘要的信息范围、教师成本不同。是否完成须查metadata与报告，不能由目录存在推断。

该项已按预算停止：225次尝试、208/301提交态，3/6注册前缀完整；0演员/评分，没有完整角色表现读数。[运行报告](results/D-E09-REPORT.md)。保留为底座，不继续围绕窗口或某条输出追加局部实验。

## 模型在系统中的角色

| 模型 | 已承担角色 | 不能混写为 |
|---|---|---|
| Qwen3-8B | ArcANE/连续状态消费者、通用单步更新 | 独立第二模型家族 |
| ArcANE-8B-DPO | 已有角色后训练消费者 | 我们训练的新方法；原始经历更新器 |
| Qwen3-32B | 容量参照、摘要/状态教师、本地评分、来源句前向 | 独立外部裁判；ArcANE-32B专用模型 |
| Qwen2.5-7B-Instruct | LongEvo文本条件消费者 | PHASE参数适配模型 |
| Step5（供应方返回step-5-preview） | D-E05更新、D-E08整理；首夜还有部分独立评分 | 固定权重可复现本地模型；完整强商业角色消费者 |

Step仅使用已授权Token Plan入口；现金接口和其他付费服务未获本任务授权。密钥不进入仓库、配置、日志或归档。部分Step评分不能与本地完整评分拼成一列。

## 直接近邻的复现范围

- **ArcANE：** 已运行发布8B-DPO与原生上下文/评价提示；未跑其32B-DPO/RLVR或训练流程。本地judge不同于论文主judge。
- **PHASE-Tree：** 已运行发布文本状态及普通文本参照；参数资产已下载，参数适配未运行。没有把读取发布状态称为复现完整在线更新。
- **EvolvingWorld：** 已运行单角色更新/消费组件；专用EW权重及完整人物—世界联合模拟未运行。
- **DREAM、EvoSpark、PD-LLM、CRPO：** 当前为方法阅读与定位来源，未将论文数字写成我们实测。DREAM固定公开repo只有占位文件。

强普通系统和直接近邻是方法构建的基础，不是逐项缩窄问题的理由。完整研究叙事与学习目标见[POSITIONING](POSITIONING.md)；任何未来训练须另有实验卡和清楚的整体能力目标。

共享数据入口：[experience_store](scripts/experience_store.py)已索引整个发布训练文件，连接动机、互动、更新与后续同人物出场。它供各方案使用同一来源，既非新benchmark，也不提前规定人物状态表示或训练loss。[数据清单](results/D-EXPERIENCE-INDEX.json)

## 补充互动资产：已有发布结果，非本轮模型运行

MiniMax Role-play Benchmark固定revision的六表已取得：95角色场景种子、3,135模拟互动轨迹及一一对应的评分。11模型/推理档位×3次运行/种子，数组每条102项，包含初始消息。公开模型输出不计入我们的调用总数，也不把3,135轨迹当3,135独立人物。评价允许有铺垫的人物演化并关注互动边界，但没有ArcANE式phase参考；它可补充连续互动证据，不能替代阶段测量。详见[ASSETS](ASSETS.md)和[库存](results/D-MINIMAX-ASSET-INVENTORY.json)。

DualMem / RoleMemo保留为直接学习方法参照：已核查官方实现入口，但完整数据、权重及循环RL agent仍标待发布，未运行其baseline；不与MiniMax已发布轨迹混淆。

EW数字场景ID是文件内命名空间；当前共享索引的后继尚未认证为原著时间线。D-E04–06使用同一冻结文件的原生组件任务，未来跨文件/连续成长学习须遵守[来源资格](results/D-EW-SOURCE-QUALIFICATION-2026-10-22.md)。这不是模型新失败或方向关闭理由。

## 学习基线（D-E10完成，D-E12补齐完整对话监督）

[D-I01](ideas/D-I01-learning-character-adaptation.md)指定原生更新SFT、原生更新/动机/互动多任务SFT，以及固定演员反馈下的更新学习作为直接比较。已从同一固定源全量建立24,977条[资料视图](data/README.md)，其中32作品14,079条原生更新已导出为训练输入与独立completion。其余整作品分别保留验证、后续测试和已观察开发身份；未按模型结果或变化标志挑选。

2026-10-22用户要求立即实际训练后，[D-E10](experiments/D-E10-trained-character-adaptation-baselines.md)已经冻结三任务数据并启动更新SFT和多任务SFT。两者各约85.9M forward tokens，LoRA64/128、seed42、相同底座/32训练作品；多任务含23,088个原生互动segment第一目标turn的候选池，实际按三任务平衡和token预算取16,931次样本。原生更新完整2 epochs/28,158次曝光，不伪装两者相同监督次数。

新测试6作品47经历/87后续context：base、U-SFT、MT-SFT、strong32、发布后态/动机、完整经历、冻结旧态七系统均已完成。MT-SFT使用训练后的更新/动机/演员，U-SFT仅替换更新器；另由共同未适配8B作来源句前向。最终质量base4.055、U4.083、MT3.872、strong32 4.330；U差的95%区间跨0，MT下降，强普通系统更好。[科研报告](results/D-E10-RESEARCH-REPORT.md)解释范围与训练覆盖，不将原生更新拟合改善等同成长。

七系统609回复、693评分及共同消费者前向已完整保存并持久归档。全部12预选人物的训练后状态—动机—互动已补齐[CASEBOOK](results/D-E10-CASEBOOK.md)。首轮MT按事前方案只学片段首回复，不能称官方完整多轮SFT复现；下降也不能直接证明多任务角色学习无效。

[D-E12](experiments/D-E12-full-conversation-character-training.md)已开始完整对话监督的同预算基线：固定训练顺序是旧MT的相同row ID前缀，16,684序列/85,900,222 forward tokens，互动5,561片段监督15,195回复。单任务编码与原验证128条完全相同；验证扩至三任务384条。没有Tulu3混合、没有新loss，不称完整官方最终模型复现或新算法贡献。后续是在已观察D-E10 cohort上的探索比较，原负结果不覆盖。[缓存与核验](results/D-E12-training-data.json)

## 原生连续生成参照（D-E11）

本项复用官方EW模拟器，6官方OOD作品各一个固定起点，最多3场景×12互动。世界固定未适配8B，人物路径base/U/MT，训练路径只用最终完整checkpoint；规划、别人的回应、世界维护、人物反思和下一场景都实际生成，不塞参考未来对白。它是同一角色成长问题的交互系统读数，不是新多智能体社会研究线；普通8B世界的限制和路径分化必须保留。

三路径已结束：1,913正式生成/506互动，各4/6完整但作品不同；初次争用21完整返回及未知在途保留。官方PF/SSF/MDB的tracker时点视图不符合标注，统一不作科学比较；其余190原任务经13次恢复后183可解析。无完整6作品质量均分/CI，不将短模拟称真人玩家长期成长，也不将本地8B世界当最强官方系统。总生成＋评分11.172 GPU进程小时，已归档。[最终报告](results/D-E11-RESEARCH-REPORT.md) · [逐书CASEBOOK](results/D-E11-CASEBOOK.md)
