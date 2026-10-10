# E92：另一来源的信息什么时候成为可用的判断标准？（2026-10-10）

- **状态：** RUNNING-DIAGNOSTIC（16-context主pilot完成；新增强模型行为诊断先登记）
- **类型：** PILOT；先定义可辨别的功能信息，不扫头/层/别名
- **对应：** I04 / C16 / C20 / P17；从E90/E91的历史依赖推进到有用的规则信息共享
- **问题（一句话）：** 当前Source的样例对food/service标准有歧义时，模型能否按来源关系利用B来确定标准；共享标签与分开标签怎样改变这种信息的作用？

## 为什么现在做；运行前的设计推导

E91证明B的词编码改变A历史K/V，并不直接证明A获得可用criterion。下一步不能把任意状态影响都叫规则形成；需让B的信息对A具有明确、可检验的功能。A的例子全部food/service同号，两个标准都完全拟合；B覆盖全部四格，可以识别其criterion。给出“同一方面”或“不同方面”的真实关系后，A的criterion唯一确定。两种关系下A的原始文字与标签完全不变，B的文本也不变。

四格新评论使简单策略给不同预测：

| B按food；问A | food好/service差 | food差/service好 | 两方面都好/都差 |
|---|---|---|---|
| 来源关系是同一方面：正确A | positive | negative | positive/negative |
| 来源关系是不同方面：正确A | negative | positive | positive/negative |
| 直接跟B标签（不读关系） | positive | negative | positive/negative |
| 不同方面时把B答案整体反转 | negative | positive | **negative/positive，错误** |

因此本次同时要求discordant与concordant读数，不能把整体答案偏置/反转当criterion使用。**较强的关系条件化检索仍可得到全对**，与输入过滤/独立抽象程序尚不能分开；本实验检验的是功能标准信息与直接标签共享的区别，不一次性宣布全算法。

CTA已有用歧义例检验上下文化的直接所有权，而且实际更支持unambiguous例获得上下文化权重，并非ambiguous例携带足够task信息。MT-Bayesian ICL明确支持有用的其它任务先验，不能以“B帮助A”作首次发现。Cross-Task ICL（ACL2024）与CrossICL（2505.24143）已研究标签空间复制、任务差异和转移收益；前者§5主要是activation相关，后者§3–4/4.6/附录A是显式合成/对齐方法和错误分析。Mixing Mechanisms的学习动作是让反事实输出互异，再改可访问证据区分指针/内容；这里用关系×四格先确保功能可辨，再用全query禁读B检验A历史能否承载这份信息。已有框架不被宽泛相似性自动否定或重复命名。

## 设置（运行前冻结）

- Qwen3-8B，本地revision b968826d9c46dd6066d109eabc6255188de91218；verl-clean conda；float32/eager，原生chat、thinking关闭，无新训练。n16、seed92001。新合成餐厅句池，与E88/E89不同；n32/seed192001、新措辞池仅在本轮功能结果有信息后确认。
- 每context A8条同号例（4++/4--）；B8条、四格各2。姓名/food-service句序/demo顺序随机，所有评论含两个方面，query来自另一句池，无demo复用。每Source每word正负完全4/4。
- B criterion两world：food或service，只改B discordant例的4个labels；A全部raw token固定。关系same/different固定在demo之前的header，均明确Task家族但不告诉实际criterion。A标准=`B criterion xor relation`，B label map依concordant例确定。
- A永远negative/positive；B共用同词或flag/pass。词均单token、频率平衡、位置不变。Header不因namespace改变；B词语义/熟悉度是本次变量的范围，不宣称纯相似度定律。
- 每关系×namespace×world运行native，以及**所有query位置只可读A/header/query**。不改变demo prefill、不细拆K/V/头/层。原生chat的closing与assistant-prefill也归query，不能提前从B写入一个未受mask限制的answer位置。
- 阳性：在相同材料上，明确给出A criterion的oracle设置；询问B的新评论，测试B自己的规则识别。阴性：物理删除B全部demo，A两criteria可解释性相同，两个world上平均discordant accuracy应50%。这是信息不足对照，不当作mask机制份额。
- 一句指令恢复：`Use {B_name}'s examples and the stated relationship to resolve {A_name}'s otherwise ambiguous criterion.` 对shared/far native、两关系与两world都运行，不搜索措辞。

## 读数与有效性

- **读数：** z=logit(positive)-logit(negative)。按关系的A gold计算discordant/concordant accuracy、margin；另报告unrestricted argmax标签率与accuracy，避免强制词表隐藏请求错误。每context criterion响应 `S=mean_discordant(g_base*(z_base-z_flip))/2`；正确使用B推断标准，两种关系S都应正；直接跟B输出则same正、different负。全部context S保存，不筛符号。另报告concordant的world间绝对变化和label bias。
- **主对比：** native→A-only的S变化；far−shared的S变化，分别保留same/different。不能把二者混平均成“来源混合有益/有害”。阳性与A-only的效果一并报告，不除小gap、不用高accuracy直接推出input filtering。
- **阳性对照：** explicit A criterion与B-query在这个接口有效；split/native完整chat一次前向误差≤.001nats；四格枚举验证A-alone两criterion均拟合、加B及relation唯一拟合；Source/标签频率、raw不变、token边界严格校对。
- **噪声地板 + MIE：** 数值max≤.001nats；16context bootstrap10000次seed920。S约.15nats或5百分点会改变投资判断，但不作自动判死；若raw argmax大量非标签，不作能力负归因。
- **混杂审计：** family/relation是明示的，criterion是从demo推断，不能叫完全无指令发现。A-only mask包括完整chat query、header只能在demo前；上下文化信息仍允许进入A。新句池受控非自然语料泛化；far词含先验，same/different关系文字长度不同，未用关系交换patch，不以其logit大小当纯单token因果效应。direct label retrieval加关系计算仍兼容正确行为，不称所有retrieval被排除。
- **决策表（跑之前写）：**

| 实际结果 | 改变判断的方式 |
|---|---|
| native两关系正确、A-only也有可靠正S | A历史携带关系可用信息；进一步设计状态内容/检索政策反事实，不再用任意coupling代替criterion |
| native有效、A-only S≈0或wrong、B-query有效 | 合法信息主要需query直接咨询B；E91的历史影响不能当完整标准共享，不撤回其真实依赖 |
| shared促进same但在different跟随B；far减弱此效应 | 输出身份影响共享方向，但逻辑关系未稳定调节；比较因果结构与纯答案投影，不将分标签永远叫修复 |
| 两namespace都关系使用良好 | 强边界：标签分开不必阻断标准转移；研究正确机制，不以无failure否定问题 |
| native很弱、oracle/B自己明显有效 | 原生模型尚未稳定组合关系；允许一次独立强推理模型行为检验，禁止格式/位置控制无限扩张 |
| oracle或B自己也弱、请求不成立 | 不从弱接口归因Source独有缺陷；回到原文/具体样例重设计，不升级新qualification门槛 |

- **算力预算：** 单卡pilot≤.5 GPU·时；确认/强推理备用只在pilot回来后登记具体配置与预测，不提前铺分支。
- **实际：** 待运行。raw prompts/context/behavior仅本地，小summary/script/结果校对入git。

## 结果

运行前静态枚举已通过（`results/e92/qwen3_discovery/design_audit.json`）：A-alone始终两标准拟合；B及关系唯一拟合，允许B输出polarity正反两种后亦唯一。逻辑规则100%、直接跟B及关系整体反转均75%全四格，discordant/agree错误分布不同；这是设计验证，不是LLM证据。

未运行。与上一goal turn的区别：上一轮是实际进展（E91已验证并上传），本轮明确检验可用的规则信息，未改研究目标为一个更容易通过的小目标。

## 16-context主pilot与强模型诊断的运行前附记

原引擎SHA2edb17847ef6361b63521580d0c3a35771141a48c531dba56828d79ffdfd5f44，16全contexts/34条件完成，numeric7.63e−6nats、.04815 GPU·时。shared native S：same+.28695[.04771,.52912]、different−.27466[−.49340,−.05622]；但B-probe discordant45.3–60.9%、explicit oracle50.0–64.1%。查看完整四格样例，concordant几乎全对、两个mixed-sign例经常都给negative，不能把该签名单独归因“知道标准却不能按关系使用”。E90/E91不撤回，本pilot也不因Task-family已明示就宣称criterion已可靠形成。

**新增诊断在此附记与脚本提交后运行：** 用本地已验证可运行的Qwen3.8-27B目录（实际config为Qwen3.5 hybrid，非普通Qwen3 attention）检查同材料的能力与接口。固定前4个context、每个template0四格；shared词表，native两关系×两world全部四格，oracle只看两discordant格，B-probe两world全部四格，共128请求。固定前4不是挑正确样例；不扩far/格式矩阵，不伪造hybrid Source-token mask。

- native chat对比direct（thinking关闭、Answer: prefill）和原生thinking（medium）；Task内容/例子/问题一致。bf16/SDPA仅用于behavior，不移植activation或从微小logit差定位机制。模型loading不得有missing keys，允许原已核对的vision/MTP辅助tensors未进入text路径。
- thinking greedy，每请求1024 token；**所有**截断轨迹按已生成prefix追加2048，不把截断当错误、不给成功样例额外预算。final parser在闭合think之后接收exact positive/negative及Answer行，unknown/censored完整报告，不过滤。原始文本/token仅本地。
- 显式criterion与B-probe若在强model可靠，则这个自然Task接口可继续研究；若更强model也不稳定，重新分析材料/任务而非扫位置。强model正确不支持“小model缺陷永久存在”，而是给正确计算一个机制起点；direct/thinking差不直接定位原生电路。
- 此次是主pilot回来后的诊断，**不是E92关系或namespace效应的独立确认**。128样例来自4context，只检验Task/接口可行性，不用样例数冒充独立context数。单卡预算≤1 GPU·时，必要完整续完已登记轨迹；不新建research line、不升级C16/C20。
