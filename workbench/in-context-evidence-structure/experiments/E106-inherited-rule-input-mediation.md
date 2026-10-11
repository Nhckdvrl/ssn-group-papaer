# E106：别人规则改变自己的证据，是经输入解释还是标签端上下文化？（2026-10-11）

- **状态：** DONE-CONFIRMATION
- **类型：** PILOT / 历史形成的因果中介
- **对应：** I04、C16/C20、P17。
- **问题：** E91已确认标签namespace会改变A自己的证据；这一效应是否主要经过A评论的上下文编码，再进入A标签位置？

## 为什么做 / 与主问题的联系

E105研究共享criterion如何部署；本项独立研究证据形成。来源可用于query选择，仍不保证被选择的证据只表达该来源的规则。E91因果结果很强，但未区分input-side与label-side历史作用。这两种解释对同一中介反事实不同，不能由再测A/B attention区分。

Cho2025已明确输入上下文化和label语义合并；CTA2025§3.2以K/V路径交换区分功能关系与token身份。因此这里不是首次发现输入上下文化或label anchor。本项具体切口是：在A原始评论/标签不变、query完全禁读B的情况下，B的输出身份如何改变A可被使用的规则信息。它只先定位功能中介，不凭中介比例宣布完整新算法。

## 设置、读数（运行前冻结）

沿E91的Qwen3-8B、FP32/eager、MHS真实评论池与受控race/gender私人规则；16新context、seed106001，reverse/polarity全保留，不选择正向context。B shared safe/toxic与far pass/flag等长等频，B aligned/conflict全交叉，A原文和标签保持。四个future queries，全部query位置禁读B；原子任务与一句恢复指令沿E91保留。未训练。

每world：原生shared、far；把far的A评论内容层输入轨迹移入shared前缀、正常重算A标签；镜像把shared的A评论轨迹移入far。全部层同时干预同一预定变量族，不扫层、不改词或alpha。评论内容token通过offset mapping定位，排除Comment字段、Annotator/名字、Label与答案词。

**关键路径隔离：** 对中介prefill仅取重新计算的A标签anchor K/V，复制到原生shared cache；所有非anchor cache仍来自原生shared。query不直接读被换掉的评论编码，只有其通过重算A标签传递的结果进入查询。另将原生far A标签K/V复制到shared，作为该下游接口的全namespace效应参照。该限定不含A其余字段，不能要求它解释E91全部A-cache作用。

每world主要条件：shared gate、far gate、shared native、far native、full-A far-KV→shared（E91阳性）、far-labelKV→shared、far-input-mediated-labelKV→shared、shared-input-held-far-labelKV→shared、instruction。16context×2world×9条件×4query＝1152评分；实际统计单元context，不把query/condition当独立样本。

主读数：B aligned/conflict改变A margin的context内有符号效应及绝对幅度；输入中介恢复量、mirror阻断量和完整label接口效应均成对报告，不能只报norm或accuracy。另报unconstrained argmax、private任务准确率、label输出率。若正负效应抵消，按E91预先报告absolute，不事后只选一类context。

## 阳性对照、噪声地板 + MIE

- full-A far-KV→shared必须数值等于far gate；self input轨迹prefill后仅labelKV交换与原生shared精确对应，max全词表差≤.001。
- input干预真实覆盖全部36层、只覆盖A评论内容；A原始token保持。cache原始fingerprint不变，queryB attention允许质量为0，matched prefix/query数值校对。
- 一句来源恢复instruction仍运行，不把行为失败叫能力缺失。
- MIE不是任意百分比：中介恢复与镜像阻断要对label接口给出方向一致、可独立确认的功能效应。若input路径弱、label接口强，更新为label-side为主；不补更多token/head变量。

## 混杂审计

这是多层trajectory的构造性路径干预，jointstate不保证自然分布；输入轨迹含所有context信息，阳性不能仅凭它叫语义过滤或特定criterion。mirror与同接口label阳性可以区分输入中介和label端直接作用，但不排除所有非评论格式路径。B不直接可读只排除query阶段，不隐瞒A在prefill时可读B；这正是研究对象。

## 决策表（跑之前写）

| 结果 | 更新 |
|---|---|
| far输入中介使A label向far效应移动，mirror保持shared输入阻止该变化 | A输入上下文化是标签namespace改变自己证据的一条功能形成路径；用32新context同配置确认，不扫描组件 |
| labelKV有强作用而input中介与mirror都弱 | 当前作用主要在label端或非评论路径；接受并结束这个输入中介假说，不强找latent |
| label接口很弱而full-A阳性强 | E91作用不集中在label anchor；本接口不识别其算法，不将input中介阴性推广；回到完整证据状态解释 |
| 两方向不一致或不稳定 | 保存为局部功能作用，不拟合更多比例救故事；回到研究问题和最强近邻 |
| 数值错误 | 保留失败、修执行，不改科学变量 |

- **算力预算：** ≤1 GPU·时，独立单卡；实际待记录。
- **结果文件：** results/e106/，原始JSONL本地；小分析/audit/run入git。
- **状态：** I04/ACTIVE与C16/C20 L1不自动改。

## 结果（运行后追加）

待运行。

### 探索结果与执行偏差（2026-10-11，确认前冻结）

16context全保留。卡误写四个query；实际继承E91的nq=4是每类4个、共8个，因此共2304评分，不是1152。全部8条保留，不事后选4条；统计单位仍为context。此计数偏差明确报告，后续确认固定8个query。

shared gate的B-rule幅度.809[.541,1.107]nats，far gate .097[.067,.129]；仅换A label KV为.302[.209,.409]，减少.507[.229,.794]。反之，far评论编码经重算label传递后幅度.825，减少−.016[−.071,.037]；镜像恢复.004[−.010,.018]。完整A-cache阳性精确等于far gate，self input轨迹全cache精确不变，数值max9.54e−6；36层各66次input轨迹干预实际执行。

更新：当前评论内容编码中介不能解释label namespace效应，label端或其它非评论形成路径是强解释。它不等于“所有输入侧计算无影响”，尤其forerunner/Source/格式位置未被该评论内容干预覆盖。不追加位置/头矩阵。

**有限独立确认：** 同源脚本SHA668a455d…，全部原条件/读数不变；32未选择新context、seed106101、每类4 query。确认的是label evidence的历史依赖与评论内容中介弱的相对区别，不要求完美归零或追更高准确率。下一轮若确认，就把这一结果与E105的共享标准内容一起综合，不能默认再扩scope。结果目录results/e106/qwen3_confirmation/。预算总≤1GPU·时。

### 独立确认结果：标签证据的历史依赖确认，评论中介仍弱

32新context、4608评分（每类4query），全部父条件保留，无scope/参数改变；脚本SHA相同。shared gate .606[.448,.793]nats，far gate .132[.095,.177]。只换A label KV为.177[.120,.245]，独立减少.429[.250,.632]。评论内容中介后.600，减少.0059[−.0251,.0447]；镜像差−.0020[−.0127,.0089]。完整A缓存阳性精确重建far gate，36层各130次真实轨迹干预，self cache精确同，numeric max0。.07123 GPU·时，探索＋确认共.10792。

研究更新：在query已完全不读B时，A标签位置仍承担很大一部分B规则作用，换A评论内容编码不能重建该作用。更强解释落在标签形成或非评论中介；当前Comment→Annotator→Label的结构中Source/forerunner晚于评论，故不能将结论夸大为所有pre-label计算无效。保留该明确边界，不追加细字段/head/位置控制。自己的token来源不能替代规则信息来源，这个问题继续成立；尚没有完整label-conditioned prototype算法。C16/C20仍L1，未取得独立L3校对。

results/e106/qwen3_confirmation/{analysis,run,completeness_audit}.json。raw/contexts本地。
