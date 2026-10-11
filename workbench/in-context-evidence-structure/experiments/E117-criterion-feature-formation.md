# E117：来源证据形成会传入另一种判断标准吗？（2026-10-11）

- **状态：** PLANNED（跑前）
- **类型：** CLAIM / 新功能对象的机制区分，不锁定论文主线。
- **对应：** C21/C22、I04、P17；新增criterion主张仅在实测支持后登记。
- **问题（一句话）：** 共享输出影响本来源证据时，它只是改变现有判断的强度，还是能把另一来源关注的输入方面传入本来源的标签证据？
- **设置：** 自然的双方面餐厅评论，两个有效的判断标准：A按食物、B按服务评价，yes/no与私人正反约定平衡。从每个Source的8条full-rank四组合demos推断criterion；每context8个不同的新评论，food/service各±完全交叉、query不与任一demo文字重合。首先Qwen3-8B与Mistral-7B-v0.3，FP32/eager，整个query可读全部Source；同时whole-query A-only对照。Llama沿用同冻结设计，在权重/数值接口可用后验证。
- **反事实：** A demos和标签不变；B标签词/序列/Source/位置与评论多重集不变。在B的四条discordant评论交换两方面valence，使B criterion从service变food；within对照在相同四个位置交换同food/service组合的不同措辞，criterion不变。四条concordant评论不动。CPU匹配所有B内容边界/外部token并保证两反事实改动相同位置，输出不存在静态词替换。它不等于整段Comment交换或单纯改变输出偏好。
- **干预：** 沿用E114 label形成时的历史B答案K/KV/V消息与A-label缓存交换；先前其它A/B缓存不直接修改、后继自然演化。完整namespace formation×reading交叉保留以连接既有解释。主要功能对象是回答对两个输入方面的因果敏感性，不宣称完整criterion program或输入过滤。
- **读数：** 对全平衡queries，F_c(mode)=mean_q z_mode*food_gold、S_c(mode)=mean_q z_mode*service_gold（二者互相正交、global private polarity已纳入），分别测food/foreign-service作用，不能以accuracy/总margin替代。主要配对为origin−cross、label cross−within、答案KV cross−within，native与A-only各报；V-only相对origin为部分作用，不把不同通道的within控制当等价。保留原namespace D、所有K/KV/V与两个缓存背景的冻结系数1预测；context-bootstrap10000 seed910，不拟合feature probe/新系数。
- **阳性对照：** single A(food)与single B(service)，两私人方向；direct明确criterion/no-demo的A/B同新输入阳性，区分不能推断criterion与不能执行方面判断；原句instruction三world对照。全A/native corners、self≤.001、full/split≤.001、static B答案layer0 KV差0、源指纹与所有层消费。52条件×8query，n16=6656/n32=13312。
- **配置：** discovery n16 seed117001旧词句；confirmation n32 seed117101 validation新词/模板。所有模型接口/条件/读数固定，只有modeling模块路由，不为好结果选择标签/层/头/alpha。CPU预检在GPU前；换对象来自MHS的private能力弱和论文的功能操作区分，不是修改MHS结果挽救。
- **噪声地板 + MIE：** 先过数值与实际消费。若single任一criterion/方向弱，不作“两个标准都掌握但组合失败”的推断；direct阳性只说明给定标准可执行，不能代替从demos推断。弱结果同样完成独立确认，不改读数、不筛种子。
- **混杂审计：** Source/A raw/label固定；B两个world输入多重集与输出stream一致，cross/within改同四位置；full 2×2 query feature组合拆开共同bias/food强度/service敏感性；新query文字不复用、不同context仍可共享词/模板。F/R缓存非独立模块，A-only不能排除所有A内其它历史路径。feature响应可由检索或表示选择实现，**不直接识别input filtering**；只有形成时的消息/label反事实识别其功能经过的路径。全部通道/范围公开，不给一个head命新名字。
- **决策表（跑之前写）：**

| 结果 | 解释更新 |
|---|---|
| single两criterion可靠，B criterion使A-only的service响应改变，label/答案边可传入 | 形成过程可传递criterion相关输入方面的功能信息；新材料确认部分路径，不称完整标准程序 |
| private能力可靠，只影响food强度/共同bias、service效应弱 | 不支持foreign criterion feature混入；解释应转向本criterion证据强度/校准，不能包装成标准迁移 |
| native有service作用而A-only/label形成作用弱 | 该任务主要是读取阶段的混合，不能外推旧形成路径解释所有多规则 |
| label功能明确但答案形成边弱 | 当前子图不足，保留范围与下一重要缺口，不自动增开细头/层矩阵 |
| single criterion弱而direct强 | 尚不能把from-demo标准完整掌握作为前提；报告推断/执行区别，不硬套部署缺陷 |
| 数值/几何不通过 | 不作科学解释，修工具并保留版本 |

- **算力预算：** 每家族≤.35 GPU·时，独立单卡并行；模型沿用节点NVMe，不训练。先n16数值有效→同源码n32新材料确认（含阴性），不边看结果边铺后续分支。
- **论文设计来源：** ACL2026 Lepori把结构形成与后续应用分开、显式结构对照检查原子；NAACL2025 Crosbie/Shutova从参与组件推进到具体operation knockout；EMNLP2024 Yu/Ananiadou比较映射下QK与OV并解释不同偏置；Cho信息选择提供task-feature角度。此实验把原输出反转升级为“哪个输入方面实际约束判断”，不把三种已有操作改名作novelty，亦不误称已有feature敏感性静态反例证明了输入过滤。

## 结果（运行后追加）
待CPU预检/GPU运行。源码SHA256：e53cd8e011518b027e0753d3a2898034c74778e4dc2a9128ec07d9313f989ccf。

CPU预检校正（无GPU数据）：两个B四组合可共享concordant字符串，dict.values不是带重复的多重集；按每条demo应用mapping核对multiplicity，保持原seed/全部context，未筛样。A/query采用不同的词对，8query全unique且不与demos重合；不是重复评分。

### PRE-RESULT观测补记（探索已启动，尚未读取任何E117科学结果）

原food/service平均对比保留不变。2×2 query已经完整采样，平均service效应可能因food的两种条件作用相反而抵消；这是纯代数的识别问题。另存POST-HOC-DESIGN的完整四点分解（共同bias、food、service、food×service）与food±下条件service效应，**不修改正在运行的引擎或原primary读数**，不只挑更显著的新量。确认n32之前冻结该观测；新增项在新材料才作确认，用于避免以平均0宣称完全不使用service。科学场景/52条件/样本均不扩展，不是新能力门槛。
