# E105：共同标准推断前后，内部信息能否约束另一人的私人判断？（2026-10-11）

- **状态：** RUNNING
- **类型：** PILOT / 原生内部状态的功能反事实
- **对应：** I04、C16/C20（仍L1）、P17。
- **问题：** 从带相反私人标签的来源分组中主动推断共同criterion，是否使内部记忆获得可与另一个Actor私人证据组合的功能？

## 为什么现在做

E102的Source字段是有效地址，但不是donor程序；E103的完整私人函数主要跟KV；E104显式criterion经Rec可产生部分功能作用。其opposite-p mixed +15.6[6.25,25]pp已经提供有限阳性，不把约85%资源heuristic升级为禁止继续的科学门槛。这次只做一个有限before/after比较，不开展report/commit、层、alpha和Goal措辞矩阵。

近邻所有权：Afendulev等2609.04434的state-swap与fact/control分工；JIT 2509.04466的功能任务状态；Cho 2509.21012的信息选择/移除；DAS/TaskVectors的任务迁移。它们不是我们的novelty。具体未决对象是：来源分组必要、匿名input-label序列不变时，私人label方向不变性如何与共同criterion的功能使用结合。阳性也可能是criterion-conditioned retrieval，不称无检索的abstract program。

## 设置（运行前冻结）

- E95生成器4个新context，seed105001；24 teacher demos，A只有concordant、B/C完整覆盖且p_C=-p_B。teacher p_A=p_B=p_T∈{±1}，c_T∈{food,service}全交叉。改变c只重分8条foreign来源，匿名input-label序列相同；原E95完整代数audit。
- Owner名字Dana，与teacher的Alice/Bob/Carol不重合。Owner只有相同context的8条concordant自己的例子，p_R∈{±1}全交叉；不把p_R、c或future Review提供给teacher。
- Teacher before：相同全部demos，criterion问题尚未进行，固定中性assistant Ready.；after：对相同demos实际提出原E95共同标准问题，原生thinking直到food/service答案，保留完整生成tokens，不只截取最终词；explicit：相同demos加E104全局criterion指令，中性assistant Ready.。所有world保留，不按teacher正确与否挑选。
- 三种teacher历史与Owner历史均结束后渲染同一个未来user开头：For the next judgment, use the reviewer's personal preference from their own examples and the common evaluation aspect. Return only yes or no.；cache切在该user内、未来Reviewer字段之前。之后同一未来Owner Reviewer+新Review+private Goal正常处理。该句不提供criterion/p，是各条件共同的消费者定义。
- 两回合格式是为把真实标准推断完成状态与Owner消费阶段对齐；不同于E104单user实验，必须重新测完整Owner cue与Rec explicit阳性，不把跨实验差当因果效应。各整段conversation只render一次，suffix严格token对齐。after历史从实际prompt+完整generated IDs重算，防止generate cache少最后token；BF16生成轨迹在FP32 replay，明确这是条件历史，不冒称原生FP32轨迹。
- 仅交换全部48linear层的Rec+conv；16attention KV、位置长度和Own原始证据全留Owner。teacher KV不复制，teacher原事实可能仍在Rec；jointstate不保证自然分布。newCaller Dana与future Review均在swap之后。
- generation：27B、openslime/vendor、BF16/SDPA，greedy，1024+所有截断追加2048，16请求。机制：同模型FP32/eager两卡，无训练。
- 机制完整分母：Own32；full explicit Owner64；teacher before/after私人B判定128；Rec before/after/explicit各128，共608行，另16标准生成。完整four-input profile、真实state-query hash均报告。

## 读数、阳性对照、噪声地板 + MIE

主目标p_R*x[c_T]；强替代teacher整函数p_T*x[c_T]、实际Own无作用profile、恒yes/no。主读数是opposite-p mixed的criterion命中和配对after−before；全部输入、同p、concordant私人p保持、完整quartet、c成对双向改变、yes/no margin和invalid均报告。不给总体75%基线已高的结果遮住真正分叉。

- Teacher标准正确率不作为选样条件；按真实c与实际报告c两个预先读数均报告，wrong/unknown parent不删除。
- 完整Owner cue应可靠完成私人任务；explicit Rec给出新回合接口的功能参照。部分阳性仍保留：after弱时只能限制本接口，不推出模型无criterion。
- self-copy max logits≤.001；源cache指纹不变、Owner KV精确不变，48linear确实消费恢复initial_state。第一context全16Owner cue split/full比较：argmax一致、margin差≤.01，完整词表差报告。
- MIE是结构性criterion×Owner-p效应及after−before方向，而非一个任意成功率。n4为探索context bootstrap，需新材料确认后才升级。

## 混杂审计

before/after是完整主动推断历史的功能比较，新增问题、CoT、最终词和长度共同变化；它不单独定位推断中哪一步必要。after含模型自己生成的criterion文字，成功不能叫隐式无文字计算。未来输入未出现排除现成答案复制；p_R独立于p_T和concordant对照排除整teacher私人函数/常数偏置；相同匿名数据两world排除不看来源分组的原始label统计。保留所有parent、tokens、fingerprint、invalid，不加层或接口搜索。

## 决策表（跑之前写）

| 结果 | 认识更新 / 有限下一步 |
|---|---|
| after相对before定向提升，并保持Owner p、对p_T稳定 | 主动标准推断历史形成可用criterion信息；用未参与挑选的context确认，再检验其依赖自己生成的criterion文字还是更早推断状态，不把宽泛representation/deployment叫新发现 |
| before已经与after相当且有结构性作用 | 不支持必须先显式报告的转变；共享信息更早已有功能，下一步解释原始示例形成，不追report/commit控制 |
| after主要跟teacher p/恒label或只同p有效 | 信息运输含私人函数/偏置，不支持独立标准组合；保留反例，回到学习内容的因果分解 |
| full cue强、Rec explicit有作用，但after无结构性增益 | 此记忆接口中的显式控制与推断历史不等价；不推absence、不铺新slot矩阵，回到E91内容形成 |
| 新回合explicit也不成立 | 该消费接口未建立，保存后停止它；不把learned弱当科学阴性 |
| 数值/carry错误 | 保留失败并修同配置执行，不改变科学对象 |

- **算力预算：** ≤2 GPU·时，不铺模型；实际待记录。
- **资产：** results/e105/，原始tokens/cache/JSONL本地；小分析、audit、run入git。
- **状态边界：** I04/ACTIVE不变，C16/C20不自动升级；不宣布novelty已补齐。

## 结果（跑后追加）

待运行。
