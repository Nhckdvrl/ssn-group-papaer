# E66：原生动作字段的概率竞争读出（2026-10-15）

- **状态：** DONE
- **类型：** 用户指定动作logits探针；不做activation patching或层扫描。
- **对应：** I04 / P12 / C05，和E65限制范围反事实配合。
- **问题（一句话）：** 资产包下目标动作的相对质量、无物理变化动作的质量与合法起始分支熵怎样变化；简单的“物理动作普遍均匀化”是否符合数据？
- **来源/队列：** E63全部79 wear/wield图，两P，预先固定seed6301，Gemma与Qwen3-32B。读取第一执行决策（step0），不筛成功/失败或选最明显帧；后续先失败再挑帧容易选择偏差。原none/generic/asset完整自然路径各158上下文。
- **同状态干预：** 另外以原asset的158上下文为固定计划/记忆/世界/人格，把exec中的Decision rule替换为none/generic/asset_with_use；asset原文也是sham参考。仅这组是明确标注的执行阶段规则干预，不叫全链人格修改。全链自然条件与同上下文读出不混成同一因果效应。
- **读数：** 在动作JSON值的共同token前缀后输出raw top10 token、raw全词表熵、各当前合法动作起始token的raw logit与归一化概率；输出目标命令、emote frown、目标examine等预定命令在合法命令trie下的完整路径概率（若不存在则明确missing）。raw分布、温度0.7和合法mask后的分布分开；首分支熵是动作族读数，不冒充完整命令熵。目标与无状态变化动作的log-odds及概率差按79图聚类。
- **前缀与token化：** 恢复原messages/schema/chat template并核prompt SHA。原输出中的JSON布局与统一action前缀分别记录；统一前缀用于跨规则对齐。token片段不等同完整动作，合法菜单多参数/多token；只打印top10不能证明机制。精确路径读数采用固定完整原生菜单，不把动作为两个选项重新定义游戏。
- **阳性对照：** exact prefix/token/tree合法性、概率归一化；asset sham重复少量固定前缀核数值地板；原生goal合法，选择已列命令。原E63自由生成/原生结果与概率读出关联，但该读出不替代实际行为。
- **噪声地板 + MIE：** 无新采样seed搜索；固定模型推理，记录重复数值差、世界簇CI。低概率与CI跨0不解释为表示消失。
- **决策表（跑之前写）：** 目标质量减少而emote更集中→动作竞争偏移，不支持均匀化；合法起始熵升且多个物理分支分散→支持分散候选，非训练安全先验因果；同上下文rule替换有效→执行阶段直接贡献；仅自然跨rule不同→早期计划/对话中介或上下文差；各模型方向不同→论文写模型依赖，不扫层刷共同故事。
- **算力预算：** 两模型各单卡，预计总0.5–2GPUh，现有fgvd/HF缓存；0API/训练/内部干预。原始大概率轨迹在cache，Git只摘要/图/可核top10样例。

## 结果
两模型各948/948上下文完成，全部79图、两P、固定首步/seed均齐全；0新动作采样/API/内部干预。Gemma/32B含载入分别0.07144/0.18488GPUh，另三次小数值校验合计0.01927GPUh。

主读数（两P先图内平均）：自然asset−generic目标命令概率Gemma−39.19pp [−47.93,−30.72]、32B−22.78 [−30.68,−14.75]；但asset−none分别−21.05 [−29.34,−13.32]和+18.23 [10.84,26.22]。两模型相对none方向相反。

同asset上下文替换为generic，目标概率分别+17.61pp [11.32,23.79]和+12.64 [8.40,17.23]；移除规则则+17.11 [11.37,23.30]和−3.85 [−7.44,−0.92]。追加use许可分别−0.88 [−2.21,0.31]和−0.33 [−1.85,1.01]。这定位了执行规则的直接作用，未识别神经回路或安全训练来源。

首分支熵asset−none的两模型区间均跨0，不支持普遍均匀化解释。Gemma丢失的目标质量亦分配到examine/Give/tell，并非全流入emote。全结果与固定top10样例：[Gemma](../results/E66_gemma_competition.json)、[32B](../results/E66_32b_competition.json)、[解释记录](../results/audits/EXECUTION_RULE_CLAIM_AUDIT_2026-10-15.md)。

sham logits差为0；固定首4上下文同batch/padding的独立完整teacher forcing核最大路径概率绝对差Gemma1.38e−10、32B3.40e−8，高概率已观察动作亦校验。最初Gemma校验未包含已观察动作，补一次固定同样本校验，三次成本全部保留。canonical读出与原采样器的区别仍有效。

### GPU前读出协议落实
两模型原948个上下文的source prompt SHA、原目标菜单成员与frown命令全部CPU通过。统一前缀固定为`{"action": "`，避免Qwen把开引号与部分动词合成token后把格式分支当动作竞争。完整原菜单采用单一canonical tokenization的trie，在温度0.7下精确累乘路径；不是原JSON grammar所有空白/同义tokenization的精确概率。raw词表与合法首分支熵分开，跨模型不比较绝对logit尺度。首batch做sham重复和独立完整teacher-forcing对照，保存数值差。两模型各948上下文，0新动作采样。

概率读出后的POST-HOC解释表：在原已记录全部合法起始分支上列出所有动词族质量，特别区分tell/say等交流与emote，避免目标概率下降就认定无害动作吞掉全部质量。不新增推理；只给纯动词分支分配质量，混合token分支明示。原预登记的目标/frown/entropy读数保留。

## E65–E66合并成本与原始入口（文档整理迁入）

[两轮完整账本](../results/E65_E66_ROUND_COSTS_2026-10-15.json)计15630次本地生成、1.196GPUh，包含E66三次固定数值校验；0API，不把teacher-forcing／概率读出算新增环境episode。raw为`runs/e65_gemma_scope_s{0,1}`、`e65_gemma_scope_analysis`、`e66_{gemma,32b}_competition`，各manifest保留模型／数据／代码hash、输入、所有失败与完整概率路径。一般规则、许可、熵和动作质量的解释仍按本卡及E65原结果，不因历史报告曾写L1而覆盖CLAIMS当前L2范围。
