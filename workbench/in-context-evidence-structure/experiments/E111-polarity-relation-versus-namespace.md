# E111：在明确情绪反事实中区分标签namespace与学到的关联（2026-10-11）

- **状态：** RUNNING-DISCOVERY
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
