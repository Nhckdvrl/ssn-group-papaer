# E93：共享判断标准，保留各自偏好（2026-10-10）

- **状态：** PLANNED（先冻结设计与静态反例，再运行）
- **类型：** PILOT；一个正交功能实验，不扫位置/头/别名
- **对应：** I04 / C16 / C20 / P17
- **问题（一句话）：** 模型怎样借用其它来源的判断标准，又让新输入按当前来源自己的偏好输出？

## 为什么现在做

E91证明其它来源的输出编码影响当前来源自己的历史证据，但未证明这种信息具有可用的规则意义。E92在8B的oracle/B自身也弱；固定同材料强模型原生thinking可完成关系判断（预定parser 63/64正确，余1正确内容但非合规格式），使研究可以落到正确计算，而不要求强模型持续失败。

E92仍有一个实质缺口：所有人都把good称positive，所以A自己的偏好数据不是执行规则的必要信息。E93让两位评论者共享或不共享关注方面，但各自喜欢的属性值独立。例：都关心辣度，Alice喜欢辣，Bob喜欢清淡。借用Bob的证据来判断Alice关心什么，不能等于照搬Bob的yes/no。

设评论有两个非价值属性x=(辣/清淡, 快/从容)，编码±1。Source s判断一个属性c_s∈{0,1}，喜欢的值p_s∈{±1}，输出f_s(x)=p_s x[c_s]（yes/no）。已知两人关注相同/不同属性r，故c_A=c_B xor r；**偏好p_A、p_B不共享**。A全部示例只有++/--，可确定p_A但不能确定c_A；B覆盖四格，能确定c_B及p_B。A与B都有不可替代的功能信息。

## 运行前的竞争解释与识别范围

| 解释 | 在本次全因子新评论上的预测 | 本次能否区分 |
|---|---|---|
| 直接采用B的判断 | 当p_A≠p_B时产生系统错误；联合flip可以不改B答案却改变A gold | 可以与正确关系/私人偏好使用区分 |
| 先借用关注属性，再按A偏好判断 | 正确；B只改偏好不应改变A gold | 与下两种尚不可区分 |
| 计算B verdict，再用p_A/p_B及方面关系换算 | 同样正确：f_A=(p_A/p_B)(x1*x2)^r f_B | **强替代解释，不能省略** |
| 从B获得属性匹配几何，用A自己的labels读出 | 同样正确；metric M=e_c e_cᵀ对B偏好flip不变 | 待后续因果比较，非已有LLM发现 |

静态枚举验证后三者行为等价。因此本pilot不以全对宣布抽象criterion，也不再把Task识别阳性当“已有全部程序”。若有功能响应，将在**新Input尚未出现**时比较四donor，并改变recipient自己的偏好/可读证据，使完整A程序、来源地址、criterion或B规则换算给不同预测；该因果分支尚未执行。

方法来源是Test, then Route的正交donor与Mixing Mechanisms的“同一个patch不够，再改变证据可用性”动作；前者已拥有给定条件的test/routing区分，后者已拥有多机制组合及指针/内容区分。CTA、Cross-Task ICL已有有用跨任务信息；Cho的信息移除与Sun2025的PC patching已有任务子空间干预。因此“借用任务信息/出现子空间”本身不是novelty。候选具体增量是**从多来源示例推断哪些规则部分可以共享、哪些须按本地证据保留，以及如何在正确计算中组合**，尚未成立。

## 设置（跑前冻结）

- 新合成餐厅属性评论，不复用E92情绪句池。A8条（4++/4--），B8条（四格各2）；每Source每标签4/4。姓名、句序、示例顺序随机；8个contexts、seed93001，新query措辞四格各一，不复用demo。句池有限，8context不是广泛语言/真实标注泛化。
- A的偏好±、B criterion两种、B偏好±、same/different关系完整交叉，共16worlds；**只改变相应标签/关系，不改原始评论**。A自己的raw证据在B的四donor间逐字相同。B criterion-only与criterion+preference joint分别只改4个labels（discordant/concordant），频率和扰动数量匹配。
- 每context：native16world×4query=64；一句恢复指令同64；B自身4world×4=16；给出真实A关注属性与偏好的oracle4rule×4=16；物理A-only 2偏好×4=8；合计168请求。yes/no共用输出空间，family明确（恰好关注一个方面、有个人偏好），criterion/preference从示例推断；不宣称无先验程序发现。
- 第一阶段Qwen3-8B，已用本地revision；verl-clean conda，float32/eager，原生chat thinking关闭，Answer: prefill，单卡batch16。引擎保存全部行、unrestricted argmax与二选一z=logit(yes)-logit(no)。不训练，不筛正确world/种子。
- 8B完成后若功能有效，设计内容干预而非扩模型列表；若direct弱，只允许对**同一个已冻结设计**做Qwen3.5-27B行为诊断（固定前4contexts，同native及阳性；direct和原生thinking另在卡登记具体请求/预算）。不因direct失败直接推出Sources不能组合。
- 一句恢复：`Use the other reviewer's examples to infer the relevant aspect, while preserving the requested reviewer's own preference from their examples.` Oracle直接给A偏好与criterion，B-probe测试其自己的完整规则；A-only在两可能criterion上有50%平均discordant gold，这是一条设计恒等式。

## 读数与对照

- **主读数：** 每context、分别按same/different保留：(1) criterion-only影响D_c=mean_discordant g_base*(z_base-z_cflip)/2；(2) joint影响D_cp相同计算，joint的B verdict在这些query上完全不变；(3) B偏好-only对A的|z_base-z_pflip|/2与答案改变率；(4) A偏好flip的有向响应D_A。读数对全部p_A、p_B、两个criterion方向平均，不能挑donor。
- 同时报告native/instruction全四格、discordant、concordant准确率和合法标签率；以context bootstrap 10000次seed930给CI。criterion与joint正、A preference正、B preference输出稳定是功能结构签名，**不是独立latent、完全程序或输入过滤的因果证据**。confidence可以随p_B变，不把logit完全不变当必要条件。
- **阳性对照：** 同材料oracle与B-probe；静态枚举唯一可识别规则及四donor扰动数；no-op重复首batch，max logit差≤.001nats。完整native/instruction/primitive行，所有argmax未知保留。
- **噪声地板 + MIE：** 上述数值地板；5百分点/约.15nats可改变下一步投资，非自动判死。8context仅pilot，暂不升L2/L3；后续材料必须独立于探索挑选。
- **混杂审计：** Source结构/词频/金标完整枚举；personal preference是显式任务家族、隐式具体参数。不同关系文字长度有差，不做关系token patch归因；yes/no先验和固定词池仍在。本次只是functional discrimination，已明确保留exact-correct的verdict换算与metric解释。strong hybrid不用Source-token mask冒充全部历史隔离。

| 实际结果 | 会怎样改变判断与动作 |
|---|---|
| 原生D_c/D_cp/D_A为正，B preference只影响confidence或少量决策 | 从任意cross-source依赖推进到可用、成分特定的信息；下一步区分before-input内容与换算/证据地址 |
| 仅跟随B答案或丢失A偏好，oracle/B各自有效 | 得到共享结构与私人映射混合的具体功能边界；不能叫完整criterion已存在而未部署 |
| 指令恢复上述功能 | 策略可切换；研究正确策略与默认策略的计算差异，不把failure普遍化 |
| oracle/B也弱 | 具体样例/语义接口诊断或一次强reasoning检查，不做新一轮头/位置扫描 |
| 强模型都正确 | 同样有计算对象；已有机制完全覆盖与否要由因果预测判断，非correct=trivial |

- **算力预算：** 第一阶段≤.25 GPU·时；强诊断须先追加配置，暂不启动。**实际：** 待运行。
- **资产：** `results/e93/qwen3_discovery`；小run/analysis/design_audit和源码入git，raw prompts/contexts/behavior本地。

## 结果（跑完后追加，不改冻结协议）

待运行。C16/C20、I04及正式ACTIVE状态保持；E90/E91/E92结果不撤回。


## 8-context第一阶段结果与下一次运行的冻结协议

全部1344行、numeric no-op0、286.634秒=.07962 GPU·时。native same/different mixed accuracy48.4%[43.8,53.1]/50.0%[46.9,53.1]；B自己76.6%[68.8,84.4]、explicit oracle67.2%[60.9,71.9]。A偏好响应1.70[1.20,2.27]/1.63[1.12,2.23]nats；B仅换私人偏好仍使A答案改变19.5%[12.5,25.8]/15.6%[9.4,21.9]。criterion响应+.106[.056,.156]/−.095[−.142,−.048]nats；一句指令没有恢复完整功能结构。不称完整标准已形成后部署失败，不启动8B位置/层扫描。

**读数审计（POST-HOC发现，原结果保留）：** 对完整对称p_B网格平均，D_c与D_cp的均值按换元必然相等；不是两份独立证据。逐world的joint仍保持B新输入verdict而改变A gold，这个反事实有效，但不能把相同的总体均值当额外机制确认。preference的有向/幅度响应及完整逐world正确性一并保留。

**在强诊断GPU前登记：** 原冻结contexts前4，Qwen3.5-27B实际qwen3_5_text，openslime+vendor transformers5.12.1，bf16/SDPA行为。Direct：native16world×四格、oracle/probe各4world×四格，共384请求。Thinking：固定其中前2context，完整同样96请求/context，共192，medium greedy1024；所有初始截断按已保存prefix续2048。固定前2不是挑正确world；n分别是4/2context，不冒称独立大样本确认。两种模式不混合单位，direct给nats，thinking为±1输出的有向响应（未解析0且单列比例）。所有未解析/截断保留；冻结parser闭合think后接收exact yes/no或final Answer行，不改格式追阳性。

模型材料/system/问题与8B相同，仅使用实际原生chat的direct/thinking差异；不加恢复指令、不训练，不对hybrid伪造Source-token mask。Direct repeat首batch≤1e−4；loading无missing keys，text loader的vision/MTP辅助unexpected按已核对白名单。脚本`scripts/e93_native_diagnostic.py`与上述协议提交后启动，`results/e93/qwen35_native_diagnostic`保存全部raw，小结果入git。预算≤1.5 GPU·时，完成登记的全部轨迹。

**本次判断：** 这是当前功能问题的一次强模型诊断，而非新qualification关卡。若正确，按before-input内容/recipient私人偏好竞争研究其计算；若弱，分析具体错误及已有8B/E91对应结构，不继续新格式/模型/头矩阵。正式主线、I04、C16/C20等级不变。
