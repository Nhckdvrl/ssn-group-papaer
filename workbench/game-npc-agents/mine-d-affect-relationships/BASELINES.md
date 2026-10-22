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

## 已启动、尚未完成

**D-E09：** 六个既有预选角色、15完整probe/47phase，Qwen3-32B从完整原生前缀逐窗形成普通人物记忆，再给两8B表演。301窗口分两条独立队列，固定来源/查询边界、统一预算恢复；每worker有4.5小时停止启动新batch的预算保护，总卡预算见[实验卡](experiments/D-E09-full-prefix-character-memory.md)。与近期摘要的信息范围、教师成本不同。是否完成须查metadata与报告，不能由目录存在推断。

这项运行在用户要求整体方向校准前已启动；保留为底座，不继续围绕窗口或某条输出追加局部实验。

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
