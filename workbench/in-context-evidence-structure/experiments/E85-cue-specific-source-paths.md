# E85：名字K的来源影响与码词影响是否共用同一条读取通路？（2026-10-10）

- **状态：** DONE（32-context探索→64新context确认）。
- **类型：** PILOT；回native因果路径，不再加回归feature。
- **对应：** I04 / C15 / C16 / C20 / P20。
- **为什么现在：** E84确认native同时使用Source字段与code，但预测的布局读取变化更跟随code代理。其逐query行为重建不足，不能以新回归器取代解释。E59已定位Source-name K，E61有NameK×LabelKV交互；现在把同一干预放到两独立query身份下，问依赖关系，不重新找头。
- **问题（一句话）：** 交换来源名字K时，是否只改变Source字段的影响，还是连code所指向的规则也随之改变；改变Label映射后两种影响怎样组合？
- **设置：** Qwen3-8B固定revision b968826d9c46dd6066d109eabc6255188de91218，float32/eager、conda verl-clean，本地GPU0。32新contexts seed85001；E84相同demo与8query Source字段×code交叉；两布局均测。所有contexts/donor错误保留，无层/head选择。
  - 每布局生成四个native prefix cache：base；N（仅demo来源名字Alice/Bob互换，code/输入/Label不变）；M（所有demo最终class标签翻转，名字/code/输入不变）；NM（两者同时）。query文字始终用base字段，不跟随donor改名。counterfactual的词频、token多重集、长度、sites保持一致。
  - 在base上2×2：来源名字token的K取base/N；Label锚点K与V取base/M。其余cache保持base，全36层/head。得到base、name_K、label_KV、joint，整段query运行。联合干预不声称等同native NM：donor历史上下文化不同，专门有full-N/full-M/full-NM对照。
  - 自拷贝NameK与LabelKV的no-op；两原生布局一句Source指令。full donors与整段前向一致性在前2contexts逐query检查。干预作用不只读最后attention token；query所有位置正常运行。
- **读数：** 按E84四格输出field/code/common/interaction分解，base自然query accuracy仅辅助；其它counterfactual相对base规则的margin/agreement仅是原规则参照，不能称counterfactual正确率。conflict不当能力测试。对每hybrid/native donor报告field、code及相对base的差；NameK×LabelKV交互分别对field/code计算；context bootstrap4000 seed850。只在native donor相应分量有清楚反事实效应时报告恢复比例，其它用绝对效应，不以比例当互斥模块份额。
- **阳性对照：** token/sites/频率与完整forward/cache；self-copy=0预期，误差≤.01nats。native N应反转field而保留正code，native M应反转两者，native NM应field回正/code反转（均是检验预测，不预删失败context）。cache patch只修改声明的K/V切片，非目标切片逐位相同；mask/finite控制。
- **噪声地板 + MIE：** no-op/full-forward≤.01nats；NameK对field或code的改变量>.15nats且CI不跨0作为可确认线索，code保持与否报告绝对差及CI；没有预设“完美选择性”准入门槛。小/不确定效应限制这项依赖解释，不增加新任务关卡。
- **混杂审计：** hybrid K/V来自不同counterfactual，可能不落自然表示流形；Source-name K可能含历史信息，不仅裸名字。Source字段/code冲突语义有歧义，TF prefix改变输出条件，只做计算诊断。field/code的四格分解本身不识别模块；即使NameK只影响field，也不能排除两路径随后汇入同一抽象Source状态。此项只检验native名字key路径是否为code影响所依赖，**不证明两个独立Source ID**。
- **决策表（跑之前写）：**
  - NameK使field反转而code主要保留，M/joint符合两Cue不同反事实：code可通过不充分依赖NameK的路线影响共享Label证据；组织有限cue-specific读取解释，不命名新head。
  - NameK同时改变两分量，接近native N的哪部分或与M存在共同交互：code影响也依赖名字key计算，单纯独立code-match解释不充分；保留同一来源解析/协作路径作为候选。
  - M改变两分量但N作用不选择性、hybrid未遵循full donor：报告当前接口混合的有界依赖，不把patch成功/失败直接当算法数目。
  - native反事实未遵循符号预测：该模板的规则/别名重解释不如假设，不能用hybrid判断抽象Source结构；认真看保留样例，不换seed追符号。
  - 数值/切片控制失败则VOID，同seed修复；科学符号不符合不是VOID。
- **定位：** Cho已拥有label读取/旁路；Feng及Mixing Mechanisms已拥有多个binding检索机制；E59/E61已有NameK与LabelKV定位。这次增量候选是来源字段与码代理在**学习到的分类规则**中的依赖与可预测counterfactual组合，而非“多个头/多个位置参与”本身。
- **算力预算：** 单卡pilot≤.2GPU·时；若读数有区分，再固定预测64新contexts≤.3GPU·时，不提前铺下游分支。**实际：** 待填。
- **产物：** 新native patch脚本、analysis/run/preflight；raw contexts/behavior本地，summary与脚本入git。精确命令/hash预检后填。

## 结果（不改上方读数）

CPU/token/variant预检通过，科学源码SHA256 `efbd56e31b04d4f448fb9bb8bb8386032ed843c52f85570d5cc7694440ec89e3`；N/M/NM与base的词频、sites、长度一致。命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e85_cue_paths.py --model /tmp/ices_models/Qwen3-8B --out results/e85/qwen3_discovery --n 32 --seed 85001`。

32-context pilot已完成，18条件×8 queries全部保留。科学墙时123.562s（.03432 GPU·时）；no-op=0、完整前向误差3.62e−5nats、行和误差5.96e−7、mask=0，所有非目标cache切片逐位相同。结果见`results/e85/qwen3_discovery/{run,analysis}.json`。

| 布局/干预 | field分量（nats） | code分量（nats） |
|---|---:|---:|
| Tag base | .336 [.282,.396] | .198 [.154,.247] |
| Tag NameK | −.235 [−.292,−.182] | .098 [.055,.144] |
| Tag LabelKV | −.299 [−.368,−.235] | −.212 [−.277,−.152] |
| Tag joint | .240 [.184,.297] | −.088 [−.129,−.049] |
| Prefix base | .609 [.499,.727] | .464 [.374,.562] |
| Prefix NameK | −.398 [−.488,−.308] | .325 [.254,.406] |
| Prefix LabelKV | −.539 [−.643,−.443] | −.494 [−.601,−.398] |
| Prefix joint | .376 [.300,.461] | −.314 [−.382,−.254] |

四种完整native反事实的符号都符合跑前预测。NameK使field反转而code仍正，但code也减弱，因此不是完美分离；LabelKV使两者反转，joint的field回正/code仍负。支持cue-specific依赖与共享映射的参与，不识别两个独立Source ID或唯一电路。

### POST-HOC解释与独立确认前冻结（尚未看确认数据）

看到pilot joint之后提出一个有限组合解释：每布局/每cue分别用三个**pilot均值**b（base）、n（NameK）、m（LabelKV），预测joint为`n*m/b`；与直接相加的预测`n+m-b`比较。它测试名字读取与映射的平均增益是否能组合，不是新的注意力数学，不是逐query完整算法。拟合只用pilot b/n/m；事后提出的身份如实保留。参数不在确认集重新拟合。

冻结文件`results/e85/gate_forecast_posthoc.json`记录原始行为hash、脚本hash、4000次context bootstrap的参数不确定性。固定绝对均值预测：

| 确认目标 | product预测 | additive预测 |
|---|---:|---:|
| Tag field | +.209 | −.870 |
| Tag code | −.105 | −.311 |
| Prefix field | +.352 | −1.545 |
| Prefix code | −.345 | −.633 |

确认固定64新contexts、seed185001、相同科学源码/18条件/8queries，不筛donor或样本。先报告跑前native/hybrid符号预测是否重现；再比较冻结模型的四项joint绝对预测与实际均值/CI。主比较为每context四分量等权的固定预测MSE（product−additive，context bootstrap4000 seed851）；同时报告均值绝对残差。pilot参数不确定性与确认采样CI分开，不把CI重叠当等效。即使product胜出，也只支持此接口下的平均组合，不自动宣称新组件或跨任务机制；若均值误差明显，则收窄这一模型，不用确认数据改系数。

确认命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e85_cue_paths.py --model /tmp/ices_models/Qwen3-8B --out results/e85/qwen3_confirmation --n 64 --seed 185001`。本段与预测文件先commit再运行。

### 独立确认（冻结commit decabf63之后运行）

| 布局/干预 | field分量（nats） | code分量（nats） |
|---|---:|---:|
| Tag base | .329 [.290,.368] | .235 [.203,.268] |
| Tag NameK | −.204 [−.244,−.165] | .099 [.071,.127] |
| Tag LabelKV | −.312 [−.352,−.275] | −.209 [−.238,−.181] |
| Tag joint | .203 [.172,.235] | −.082 [−.102,−.063] |
| Prefix base | .566 [.503,.632] | .496 [.437,.559] |
| Prefix NameK | −.337 [−.390,−.285] | .321 [.270,.373] |
| Prefix LabelKV | −.497 [−.562,−.436] | −.460 [−.516,−.406] |
| Prefix joint | .319 [.274,.365] | −.309 [−.352,−.265] |

四种full-native反事实符号与pilot一致；两布局的NameK/LabelKV/joint符号也全部重现。NameK不是对code无影响：其code分量减弱，但没有跟field一起反转。保持原读数，不将counterfactual的base-rule agreement叫正确率。

冻结product预测+.209/−.105/+.352/−.345，对应实测+.203/−.082/+.319/−.309，均值绝对残差.007–.036nats。Tag code的实测−预测+.022 [.002,.041]，说明固定预测存在系统残差；其它残差CI跨0不作等效零。四项等权、按context比较的固定预测MSE：product **.0232 [.0190,.0280]nats²**，additive **1.2189 [1.1670,1.2723]**，差 **−1.1957 [−1.2490,−1.1436]**。它只预测四项均值；相加模型在field双翻转时本来就作出相反符号，不把胜出称完整算法重建或新乘法原理。未用确认集重估任何参数。

产物`results/e85/qwen3_confirmation/{run,analysis,gate_validation}.json`；图`results/figs/e85_cue_paths.{png,pdf}`。确认科学墙时220.403s，两次合计343.965s=.09555GPU·时；同引擎/依赖hash，self=0、full-forward≤3.63e−5nats、行和≤5.96e−7、mask=0。18×8矩阵全部finite/完整，非目标切片逐位相同，无科学VOID。raw JSONL留本地。

**认识更新：** 在此分类schema中，两种共线的身份线索不能直接用一个“来源信息有没有”读数概括；它们对native名字key有不同依赖，但共同受标签映射影响。这是一项有可确认反事实预测的具体读取解释，不识别唯一地址/模块数，不证明不存在共同Source状态，不外推所有ICL。C20追加L1，不改正式状态。
