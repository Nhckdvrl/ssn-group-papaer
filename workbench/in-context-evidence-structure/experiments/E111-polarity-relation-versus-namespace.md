# E111：在明确情绪反事实中区分标签namespace与学到的关联（2026-10-11）

- **状态：** DONE-VALIDATION
- **类型：** PILOT / 简化形成机制的功能内容
- **对应：** I04、P17、C16/C20。
- **问题（一句话）：** E109识别的namespace形成路径能否也传递输入—标签关联，还是对输出身份与关系内容有不同作用？
- **设置：** Qwen3-8B固定revision，FP32/eager，16新context seed111001；同Comment/Annotator/Label格式。餐厅短评论：明确正/负情绪，同类候选仅改变同义形容词及短句形式；私人规则A为情绪→yes/no、B相反，A polarity反转平衡。B固定8标签词/Source/位置，仅交换正负评论使B与A规则对齐；阴性为同情绪评论互换，同样改变8位置，完整输入多重集不变。匹配完整token几何与content外token身份，未见query输入。另在同一任务给B更换pass/flag namespace，以同时比较两种形成反事实。不使用码词、函数定义、thinking运输或头/层搜索。
- **读数：** 原origin/cross/within的A-only signed/absolute margin差与same-class差；A label KV作用及B答案形成边K/KV/V作用；同两个关系world的namespace形成边K/KV/V作用。10,000 context bootstrap。完整raw读数全保存。单来源A能力、两种private polarity、一句指令对照同时测量。
- **阳性对照：** all-A cross cache精确重建cross gate；label interface；native A-only private convention准确率和instruction。固定label关系反事实B答案第0层KV差0、全fields身份相同；edge self-copy≤.001、原cache不变。若single-source convention失败，不声称规则已会却无法组合。
- **噪声地板 + MIE：** FP32、matched full-matrix eager边计算。阴性同类置换实测，不以模型输出筛词。只有关系超越同类置换且形成接口有效才用未参与探索的新措辞/形容词确认；没有则接受namespace路径与关系路径未统一，不再增文本/位置矩阵。
- **混杂审计：** 合成评论是构造性机制切口，不冒充真实标注者分数；预训练情绪识别提供输入特征，个人label convention需由demo确定。both private polarities平衡，不能只报符合预训练yes/no的样本。namespace与关系反事实在同一模型、同一任务、同context中比较，避免跨任务的K/V差异被当因果分工。B输入固定多重集和所有token几何，position配对仍是研究变量。关系阳性不能证明抽象criterion本体，仅证明功能关联。
- **决策表（跑之前写）：**

| 结果 | 对主问题的更新 |
|---|---|
| 关系大于同类置换，B答案消息转移 | 标签载体有可用关联信息；namespace改变对这些关联的形成时访问，支持两阶段的来源边界解释 |
| namespace K强而关系主要V、两者新材料保持 | 输出身份决定形成时的检索坐标，关联内容有另一功能通道；不叫首次QK/V分离，贡献在来源证据怎样形成 |
| 关系大于同类，但B答案路径仍弱 | 已有namespace子图只解释命名，不是完整外来源规则传播；回到prelabel/label功能结构，不全量搜组件 |
| 同类与跨类仍不可分、或single低 | 实验未分离目标，不包装成功；回到问题与最强文献，不为该接口追高分 |

- **算力预算：** pilot＋可能的独立材料确认≤1 GPU·时，单卡。**实际：** 待记录。

## 设计来源

CTA2025 §3.2–3.3把token身份与功能关系分开，并用易解释的put/spread歧义让机制竞争；Cho2025 §4.1区分复制与label语义重叠；Wessel2026 §3.3用不同token的同规则检验token invariance。这里借鉴这种简化/关系反事实，而不是增添极细控制。E110的真实长评论阴性仍保留；不会因为简化材料成功就说MHS关系解释已成立。

## 结果（运行后追加）

待运行。

### 运行前配置冻结

同shared origin/cross/within与far origin/cross，原生A-only5条件；关系label/full-A3、关系答案边4、两world namespace label2、namespace答案K/KV/V6、single A1、instruction3，合计24条件/context、3072评分。所有语料/形容词模板在preflight文件；私人polarity按context奇偶严格8/8平衡。Source/标签/position关系审计通过。固定的namespace系数1重建（包括rule双差分）同时在这套新任务验证，不另拟合。

### Discovery更新与新材料确认冻结

16context全部3072评分、single A 128/128（p两方向各64/64）。跨情绪置换比同情绪置换的作用大1.726[.755,2.775]nats；A label接口差.922[.242,1.619]；B答案形成边KV差.309[.182,.439]。在该关系反事实中，答案V-only幅度.434、KV .439，两者差.0046[−.079,.096]；K-only仅.105。namespace子图系数1重建rule双差分：K r=.920、KV r=.948。这是在同模型/同task/context里，让输出命名与配对信息的功能差异可见，不跨任务宣称K/V独立模块。

下一步为真正的新材料确认：`--materials validation --n 32 --seed 111101`；新10正/10负形容词、10新句式，输入文字与discovery disjoint。词表/模板写入preflight，不根据模型输出筛选；两private polarity各16contexts。源码只增加材料分支，所有既有条件/读数/边接口保持，旧源在e59ec14b保存。相同3072/6144结构，不另扫组件。actual discovery .0282 GPU·时、numeric/self/source cache0。

### 新措辞独立确认完成

32context，6144评分；与discovery原始评论交集0，两private polarity各16contexts，single A256/256。A-only自身证据对外规则仍敏感：跨情绪 vs同情绪置换作用差2.033[1.189,2.878]nats，A label接口差1.465[.982,2.000]；B答案形成边KV差.618[.446,.813]。关系反事实中V-only幅度.750、KV .726，两者差−.0247[−.0907,.0381]；K-only .120。namespace固定系数1 rule双差分重建：K r=.907/RMSE1.599，KV r=.958/RMSE1.097，零预测3.731。发现的方向与新的词/句式材料保持，所有self/numeric/source fingerprint误差0；.0545 GPU·时。

**更新：** 固定答案词/位置时，过去答案消息确实能传递改变本Source判断的语义关联，不能只归结为静态标签身份。与namespace的Key作用形成有边界的功能分离；不是“首次QK/V不同”，也不是两个独立模块。答案边未解释完整label关联效应（完整label与答案KV仍差1.265[.900,1.665]），接受它是部分计算结构，不把残差自动升级为下一轮逐字段搜索。真实MHS的E110控制不足结论保留。

任务准确率较高（shared original A-only90.63%，far98.44%），因此研究对象是正常规则使用中的证据形成，也不依赖模型必须普遍失败。C21的namespace解释得第二任务支持；关联内容可另记有界L2，不自动升到L3/完整理论。接下来综合E90既有全局结果与E112架构差异，不重复early/late mask矩阵。

### 关联内容主张的L2审计（§4）

1. 噪声地板/工具：self与全A重建0、layer0 B答案KV相等0，功能量.618nats；原cache保持。
2. 采样：词/句式仅按输入token几何匹配，未看输出；16探索→32新seed、新完整词/句式，raw评论交集0。所有极性/条件保留。
3. 读数：相同yes/no logit差；signed与absolute预先报告，无condition normalization；同类置换作为实测对照，不设为0。
4. 默认提示/能力：single A与instruction同时保留；两私人映射均100% single。结论是功能关联影响，不叫默认完全不会用来源。
5. 输入/幸存：Source/标签/位置、B词频与输入多重集严格保持，仅配对改变；未剔除失败词/seed。CPU boundary失败发生在模型评分前，构造修复记录。
6. 公平：无训练/性能竞争；全24条件预算内，未挑winner。
7. 污染：情绪语义来自预训练是预期；私人标签约定由context决定，两方向平衡，不声称新情绪能力。
8. 多重比较：K/KV/V均报告；没有层/头/强度搜索。namespace预测系数1，不重新拟合。
9. 饱和：single ceiling用于阳性，机制用非饱和raw margin，不以100%作为效果大小。
10. 范围：Qwen3-8B、合成餐厅情绪和私人yes/no约定；MHS E110的不确定关系解释保留。答案形成边只解释关联的部分，不声称完整程序。

### 独立校对完成

`results/e109/independent_review_2026-10-11.md`从原始新材料记录先行复算，作者114项相关数字最大差0。C22维持单模型L2；C21的namespace另有Mistral确认。关系KV逐query重建r=.783、RMSE2.407（零3.299）明确为部分路径；KV−V平均差区间跨0不证明等价。K/V干预仅不直接交换另一通道，允许后继状态演化，不叫两个独立模块。
