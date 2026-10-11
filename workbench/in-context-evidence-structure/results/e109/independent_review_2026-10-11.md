# C21/C22 独立科研校对（2026-10-11）

**结论：关键数字复算通过；支持有范围的形成路径解释，不支持唯一/必要中介或完整规则程序。** E109 Qwen3 的答案 K 干预对 namespace 逐 query 双差分的固定系数预测为 r=0.9690、RMSE=0.8100；E112 Mistral 独立确认保持 r=0.9663、RMSE=0.2649。E111 Qwen3 新情绪材料中，固定标签的跨类配对相对同类置换，经答案 K/V 形成边的幅度差为 0.6184 [0.4493, 0.8064] nats，主要由 V 版本复现。C21 得到两个家族与 Qwen 第二任务的限定支持；C22 的关联 V 结果仍只有 Qwen 情绪任务，不能随 C21 自动推广。

本会话推进 **C21/C22、P17** 的独立校对。没有启动 GPU、训练、筛样本或增加控制矩阵；没有改 workbench 状态和主张等级。需要由主会话把本报告写入 CLAIMS/README 的校对列与会话日志。本报告不作 novelty/工作台去留判决。

## 1. 独立性与复算对象

- 先读仓库 AGENTS、README、workbench 登记表、EXECUTION §4–5，以及 E108/E109/E111/E112 生成与干预脚本、E56 采样依赖、E109 重建脚本。运行流程检查：0 ERROR、31 WARN；没有为无关 warning 修改文件。
- 在读 CLAIMS、综合、实验卡结果段及作者 analysis/reconstruction JSON **之前**，从完整 E109 confirmation 与 E111 validation 的 behavior/contexts/run/preflight 复算并保存 JSON。没有调用作者 analyze 函数。
- E112 confirmation 在 run.json 缺失时不读部分 behavior/contexts；run 出现且两者均为 32 行后，先独立复算，再比较其作者 analysis。复算时作者的 confirmation reconstruction_audit.json 尚未存在。
- 最后才比较作者汇总及 C21/C22 措辞。E109 102 项、E111 114 项、E112 102 项均值/重建检查的最大绝对差分别为 1.86e−15、0、7.22e−15。未发现数字错误。E112 的作者重建 JSON 初次比较时缺失，随后生成后再核对全部五个预测器，独立复算始终在先。
- 独立 bootstrap：**context 为单位，20,000 次，seed=20261011，percentile 95% CI**；同一 context 的全部条件、world 和 8 个 query 一起抽取。作者是 10,000 次及不同种子，CI 端点略有差别是预期。以下 CI 全为独立复算值。
- 机器可读结果：[independent_recalculation_2026-10-11.json](independent_recalculation_2026-10-11.json)。包含 raw 文件 SHA、全部条件准确率、signed/absolute 读数、五个 namespace 预测器、完整性/采样与数值控制。

## 2. 读数与固定预测的含义

令 z 为模型下一 token 的目标来源标签 logit 差；g∈{−1,+1} 是 A 的私人约定下的正确方向。E109/E112 主读数是每个 context 内先平均 query：

`D_c(mode) = mean_q g_cq * [z_cq(aligned, mode) − z_cq(conflict, mode)]`

报告 `mean_c |D_c|` 和 paired differences。**它不是逐 query 绝对差的平均**，更不是该接口解释了多少百分比的完整机制。JSON 另存 signed 及逐 query 绝对变化，未筛掉任何正/负方向。

namespace 预测每个 world 的目标为 `T_w = z_w(far_label) − z_w(shared_gate)`，预测为 `P_w = z_w(edge_mode) − z_w(shared_gate)`；重点检验 `T_aligned − T_conflict` 对 `P_aligned − P_conflict`。E111 用 origin/cross 的对应 namespace 对照。系数固定为 1，未拟合截距/系数/头/层。RMSE 与 correlation 都按逐 query 数字计算，置信区间仍按 context 抽样。

raw namespace 相关可能含共同标签偏移；双差分减少了与关系 world 无关的偏移。共同减去 baseline 也不能单靠相关证明机制：这里同时报告固定系数 RMSE 和零预测 RMSE，误差中共同 baseline 会抵消，才能说明所干预子图近似重建了指定反事实。**这是使用 actual donor 激活的干预效果预测，不是无需 donor 的新输入行为算法。**

## 3. namespace 形成路径：E109 与完整 E112

每批 32 个完整 context、8 query、24 条件，均为 6,144 个评分。

| 幅度或相对 shared gate 的减弱，nats | E109 Qwen3-8B | E112 Mistral-7B-v0.3 |
|---|---:|---:|
| shared gate B-rule 幅度 | 0.7873 [0.5926, 0.9915] | 0.1052 [0.0760, 0.1405] |
| far-label 接口幅度 | 0.2341 [0.1728, 0.3038] | 0.0433 [0.0322, 0.0552] |
| 完整 label 接口减弱 | 0.5532 [0.3519, 0.7608] | 0.0619 [0.0338, 0.0951] |
| 答案 K 形成边减弱 | 0.5614 [0.3597, 0.7737] | 0.0611 [0.0285, 0.0992] |
| 答案 K/V 形成边减弱 | 0.5443 [0.3423, 0.7545] | 0.0582 [0.0293, 0.0903] |
| 答案 V 形成边减弱 | 0.2414 [0.0755, 0.4104] | 0.0381 [0.0159, 0.0592] |
| B prelabel K/V 形成边减弱 | 0.0097 [−0.0086, 0.0342] | 0.00015 [−0.00128, 0.00159] |

固定系数 **rule 双差分** 的全部预定预测器：

| 预测器 | Qwen RMSE | Qwen r | Mistral RMSE | Mistral r |
|---|---:|---:|---:|---:|
| 答案 K/V | 0.5623 [0.4886, 0.6321] | 0.9851 [0.9777, 0.9896] | 0.2254 [0.1752, 0.2747] | 0.9767 [0.9523, 0.9887] |
| 答案 K | 0.8100 [0.6622, 0.9576] | 0.9690 [0.9546, 0.9791] | 0.2649 [0.2109, 0.3147] | 0.9663 [0.9347, 0.9815] |
| 答案 V | 2.5269 [1.9780, 3.0447] | 0.6417 [0.5163, 0.7591] | 0.7536 [0.5509, 0.9618] | 0.5080 [0.3332, 0.6476] |
| B prelabel K/V | 3.2590 [2.6319, 3.8509] | 0.0739 [−0.1818, 0.2574] | 0.8707 [0.6399, 1.1073] | −0.3011 [−0.6276, 0.1798] |
| 全 B K/V | 0.5576 [0.4860, 0.6266] | 0.9853 [0.9782, 0.9897] | 0.2267 [0.1762, 0.2761] | 0.9769 [0.9525, 0.9887] |
| 零预测 | 3.2671 | — | 0.8650 | — |

因此不仅是两条均值碰巧接近：答案 K 的固定系数相对零预测 MSE 降低为 Qwen 93.85%、Mistral 90.62%，K/V 分别为 97.04%、93.21%。这些是**预测误差比较**，不能改写成“原生机制中有这些比例经该边中介”。Mistral 较小的绝对效应有精确数值阳性和 context CI；不需要用其规模比值推断架构本质差异。

E108 的完整 prelabel packet/mirror 阴性已在作者卡中保留。本次读了其轨迹脚本，但**未独立复算 E108 原始评分**，因此其数值不能计入本报告的独立证据。E109 本身已直接比较答案与完整 B prelabel 发送边。

## 4. 固定标签的关系内容：E111 新材料

所有 B 标签词、Source、标签位置及 B 输入多重集相同；cross 与 within 都重新分配 8 个 B 输入。完整 token 几何和评论外 token 身份匹配。cross 改情绪与标签的配对，within 保持情绪类别。

| 相对 origin gate 的 context 幅度，nats | cross | within | paired cross−within |
|---|---:|---:|---:|
| 全 A gate | 2.9744 | 0.9416 | 2.0328 [1.1873, 2.9133] |
| A label 接口 | 1.9906 | 0.5257 | 1.4649 [0.9850, 1.9980] |
| B 答案 K/V→A label 形成 | 0.7255 | 0.1071 | 0.6184 [0.4493, 0.8064] |

cross 的答案 K-only 幅度 0.1204 [0.0830, 0.1643]，V-only 0.7502 [0.5595, 0.9670]；K/V−K 为 0.6051 [0.4286, 0.7981]，K/V−V 为 −0.0247 [−0.0913, 0.0377]。支持**该反事实中答案 V 交换足以复现主要平均幅度、K 版本明显较弱**；CI 跨零不证明 V 与 K/V 逐 query 等价，也不说明 V 独立存有完整私人程序。

同一批 context 上，namespace 双差分仍保持 K/V RMSE=1.0973 [0.8856, 1.3289]、r=0.9579 [0.9259, 0.9767]；K RMSE=1.5991、r=0.9069；V RMSE=2.6450、r=0.7070；零预测 RMSE=3.7308。因而 K 与 V 的功能差异不是只由不同任务之间的比较得来。

**完整关系解释仍有明确残差。** 完整 A label cross 作用与答案 K/V 平均幅度相差 1.2651 [0.8900, 1.6707] nats。复算作者已有逐 query 关系重建，K/V r=0.7831 [0.6950, 0.8631]、RMSE=2.4069 [1.9285, 2.8973]，零预测=3.2995；V r=0.7628、RMSE=2.4508；K r=−0.0261、RMSE=3.3212。审稿式 POST-HOC 误差诊断：K/V 相对零预测 MSE 减少 46.79%，明显不同于 namespace 的高重建。不能把 0.618 差分当完整关联的可加中介份额。

**私人 polarity 阳性通过。** single A 的正向与反向各 16 context、各 128 query，全为 128/128；所有词表 argmax 也是正确标签。pooled 256/256。其 bootstrap [1,1] 是经验饱和，不能声称总体准确率确定为 100%。origin gate 90.625% [86.719,94.531]，far origin gate 98.438% [96.875,99.609]；origin 指令 85.938% [80.078,91.016]、cross 指令 99.219% [98.047,100]。因此这里测的是正常判断中的功能来源依赖，不支持“完全不会用 Source”的能力叙事。

within 是有效但不完美的语义阴性：同类短句仍改变词、主题和位置对应关系。cross 的超额作用、静态输出词固定以及第 0 层 B 答案 K/V 精确相等一起支持**上下文化载体含有与输入—标签配对有关的功能信息**；不单独证明抽象规则变量或唯一的关系表示。MHS E110 阴性/控制不足不能因这套简化材料成功而撤回；本次未独立复算 E110。

## 5. 采样、几何与干预实现审查

| 混杂项 | 校对判断与证据 |
|---|---|
| 完整性/幸存种子 | 三批均 32 行、context ID 0–31、每行 24 条件×8 query，所有 z 有限。无 context 内 demo/query 重叠和重复 demo 文本。argmax label/correct 的布尔值由 token ID 独立逐项重算一致。没有按输出过滤。E109 首次数值失败保留，修复后同 seed 运行，不是筛科学种子。 |
| 采样与材料范围 | E56 先按 MHS 人类目标分类/长度划池，再随机采 context；私人标签规则为实验配置，不能冒充真实 annotator 标签。E111 用输入 tokenizer 签名筛选匹配，不读取模型输出；正反约定严格 16/16，E109/E112 为 14/18，均完整保留。 |
| discovery/test 重叠 | E109 discovery→confirmation 0 完全相同 context，但独特 query 文本交集 17、全部文本交集 125；E112 对应为 0、17、135。E111 新词/新句式全部文本交集 0。MHS 只能叫独立抽取 context，不能叫评论 disjoint 的新数据。 |
| context bootstrap 范围 | 允许跨 context 复用文本，抽样单位正确；CI 条件于这些模型、池与设计，不是对全世界评论/语义/模型的总体 CI。E111 confirmation 内跨 context 重用文本也较多，不把 256 query 当独立样本。 |
| token 几何 | CPU 独立载入本地 Qwen tokenizer，核验 E109 128 个 world/namespace 配对与 E111 192 个配对：长度、roles、anchors、input/answer 索引完全一致，A token 变化 0；变化仅在设计允许的 B 范围；标签 ID、gold、姓名、每来源标签 4/4 均独立核对。答案范围为 8×(label+尾部换行)=16 token。分块 token 流在这两批中与整段字符串编码一致。Mistral 只有脚本断言及 preflight 核验，未从本机重新 tokenization 远端 tokenizer。 |
| Source gating | 在**所有 query token 和所有层**禁止读全部 role=1 的 prefix 位置，而非只屏蔽最后答案位置。A/HEAD 仍可见；query padding 不作为可见 key，live query 保持本例因果顺序。gating 只限制读取，不清除 prefill 历史依赖。 |
| receiver edge | 替换 donor 的同层、同位置 post-RoPE K 或 V，只采用 A label receiver 行的替代 attention output；其他 receiver 不直接交换，但因果后继自然演化。全部 layer/head 固定，未搜索。K-only 是未**直接移植** V；不意味着整个多层活跃 V tensor 保持 pristine shared。 |
| 消费/缓存 | Qwen 36 层、Mistral 32 层每层调用计数完全一致；E109/E112 各主 edge 模式每层 64 次，E111 各模式 32 次。cache deep-copy 后再 patch/query，源 cache 指纹精确保持。full-A 对 far-gate/cross-gate 的原始逐 query max 差三批都为 0。 |
| 数值/工具阳性 | edge self max 三批都 0；记录的 native/cache 数值 max E109=0.0002022、E111=0、E112=0.000001907 nats。E111 所有 context 的固定 B 答案第 0 层 K/V 差 0。修复后的 eager 使用完整 GEMM 形状；不拿更宽 tolerance 掩盖首次数值失败。 |
| 输入与读数一致 | 固定 raw logit 差、全部条件共享相同 query 几何、无分条件校准或增益；namespace 标签身份与语义本来共同改变，不能声称已拆成两个独立因素。 |
| 算力/饱和 | 模型冻结且未训练，无性能方法预算竞争。能力阳性饱和另报，机制主读数用 raw margin。MHS instruction 未恢复：Qwen aligned/conflict 准确率 66.4%/60.5%，Mistral 65.2%/55.5%；不从这些数字引出新能力缺陷主张。 |
| 版本/资产 | 三批 contexts SHA 和生成脚本 SHA 与 run 记录一致，FP32/eager/transformers 4.57.6。Mistral run 的 revision 原字段为 unverified，另有 model_identity_audit 报告三个权重和七 metadata 匹配 base revision caa1feb0…；本会话未独立重新 hash 远端权重，不把这一环假称已独立确认。 |

E109 实验卡初始评分条件数有 10×2 的笔误，运行实际为 12×2，作者已在结果段记录 3,072/6,144 的真实数量。原始评分无缺失，主对比没有因此改变。

## 6. 可支持的精确科学主张与必须修正的措辞

**可支持 C21 的表述：** 在 Qwen3-8B 和 Mistral-7B-v0.3 的 MHS 受控私人规则中，A 原文和标签不变、query 全程禁读 B 时，B 的输出 namespace 仍改变 A label 缓存的可读证据；只在 A label 形成时移植过去 B 答案 K，足以近似重建预定 namespace 干预的逐 query rule 双差分。该固定系数预测也在 Qwen3 的情绪任务成立。注明实际三种 model/task 组合；没有 Mistral 情绪实验，不能暗示完整 2×2 覆盖。

**可支持 C22 的表述：** 在 Qwen3 的明确餐厅情绪/私人 yes-no 任务中，固定 B 输出词、来源、标签位置和输入多重集，跨情绪配对相对同情绪置换的超额影响可部分通过上下文化 B 答案 V 在 A label 形成时传入，并改变完全禁读 B 的后续 A 判断。它是一条功能关联路径，不是完整规则程序。

**自然主旨的可信范围：** “来源条件化检索使用的证据，可能已经经输出命名相关的上下文化含入另一来源的关联”与这些结果相容，而且比“读取哪个 Source 就只使用那个 Source 的关系”更准确。本轮独立重验的是形成→A-only 读取的干预链；原生 Source 字段如何调节 query 检索的 C16/E59/E64 证据没有在本会话重新复算，应继续独立引用，不能由这里的强制 gating 代替其原生路由证据。

当前 CLAIMS 的“近似重建”“部分”“不是完整程序”大体准确。进入摘要/形态卡时以下措辞必须落实：

1. **“K 单独，V 保持 shared”改为“该 edge 不直接替换 V，后继状态自然演化”。** 后者是代码实际执行的反事实。不能把多层 K-only/V-only 叫两个正交模块或固定内容与固定地址的完全分解。
2. **“输出身份决定检索坐标”改为“输出命名的作用可经形成时的答案 K 交换近似复现”。** K patch 既包含 token 身份，也包含上下文化 sender state；结果未识别唯一坐标、同标签相似度算法或唯一必要路径。
3. **“V 与 K/V 相同/复现规则”改为“V 版本复现主要平均幅度，完整 label 关联仍有显著残差”。** 均值差 CI 跨零不是 equivalence test；逐 query 关系重建显著弱于 namespace 重建。
4. **“跨架构机制成立”必须限定 namespace；“关系 V 跨架构成立”目前不支持。** E112 没有在同一任务重新测 E64 的 query 来源处理时序，不能据此声称本轮已验证形成时序与读取时序的架构解耦。
5. **“排除输入编码/Cho/CTA 解释”只能限定被测试的交换路径。** 弱 prelabel 反事实不证明全部 prelabel 计算不必要，强答案边重建不证明其它冗余路径不存在；不得声称完整原生网络机制已枚举。

一个范围明确的英文摘要候选：

> In Qwen3-8B and Mistral-7B-v0.3, changing a foreign source's output vocabulary alters target-source label evidence even when every query position is prevented from attending to the foreign source. Interchanging foreign answer-key messages only at target-label formation approximates the resulting namespace intervention on independently sampled contexts, without fitted coefficients. In a controlled sentiment task in Qwen3-8B, fixed-label input–label re-pairing also propagates partly through contextualized answer-value messages.

没有将独立校对通过当成自动升 L3/L4 的命令。C21 可以由人结合三个已验证组合讨论 scoped 泛化；C22 保留单家族/单任务边界。未验证的新模型、新任务、无 donor 的行为预测与唯一中介不在这段候选内。

## 7. Cho/CTA 的具体定位

仅依据本地已核对论文卡和 KEY_PAPERS 的相关段落，**没有新一轮联网 novelty 检索，也不假称本会话重新逐页读过原文**：Cho2025 `cho2025-icl-circuit-functional-packets.md`，Cho2026 `cho2026-information-removal.md`、`cho2026-contextualization-channels.md`，CTA 的 KEY_PAPERS §“Bakalova et al.”，以及 Bertsch/InvICL 对预编码边界的卡。

- **Cho2025 已有**上下文增强 forerunner、forerunner→label copy、label 语义与文本特征合并/去噪。E108–E111 不能叫首次发现 label 处的 contextualization，也不能用 prelabel 阴性反驳其全部编码机制。差别是合法多 Source 的私人映射在共享输出空间下，namespace 如何改变 **target label 形成时的外来源依赖**，并用 Source-gated query 与定量反事实重建检验。
- **CTA 已有** position graph、跨示例 y→y 形成边，以及输入/输出/token identity/functional mapping donor 来识别信息含义；“历史答案载体传 functional relation”或“context 依赖不等于完整 task program”不是新所有权。E111 与其方法有明显继承关系，作者在卡中明示设计来源是正确的。
- 可陈述的距离是 **Source 位置上的读取限制与关系信息的功能来源不一致**，以及 **同一 context 上 namespace 的答案 K 反事实与固定标签配对的答案 V 反事实具有不同作用**；并且前一项以固定系数在新 context/另一家族上近似重建。它是既有上下文化框架内的具体边界和预测，不能声称发现新的 QK/V 模块或推翻 CTA。
- Cho2026 的信息移除框架也已明确构造性功能检验与完整原生机制之间的区别；这里不争通用“规则改变 query 计算”的发现。当前目标是跨 Source 的具体形成信息，而非新命名全部 ICL 程序。
- 综合 §30 的所有权表大体没有过度声称；“新增 source×namespace×形成阶段的具体预测”比“首次功能关系传播”准确。需要改的强动词已列在上节；不因这份定位自动关闭工作台或要求扩张控制矩阵。

**交付判断：** 本报告完成了从原始结果、采样脚本和干预实现出发的独立复算。算术、完整性、Qwen token 几何及现有数值 controls 通过；保留 E108/E110 原始复算未覆盖、Mistral tokenizer/远端权重未独立重验、C22 跨架构未验证等范围。下一步是综合和人审准确措辞，不是继续增加字段/头/memory 接口。
