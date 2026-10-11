# E119：更强模型的同一证据形成与功能规则（2026-10-11）

- **状态：** PLANNED（跑前）
- **类型：** REPRO / 跨能力计算边界，不锁定论文。
- **对应：** C21/C22/C23、I04、P17。
- **问题（一句话）：** 模型更强时，输出命名/历史关联的形成路径仍参与原生预测吗？多方面的来源关系会改用更有criterion特异性的表示吗？
- **设置：** Qwen/Qwen3-14B revision 40c069824f4251a91eefaf281ebe4c544efd3e18，FP32/eager/frozen；官方模型是post-trained hybrid thinking/non-thinking，非Base。本次plain continuation无需chat/显式reasoning，不把它叫完整reasoning压力测试；8B同族也不是Base。8 shard cached29536665640字节，复制到fvcrc10 NVMe；A10080GB单卡独立完整模型，弱互联不作集群训练。
- **两块独立问题：** (1) 原E115/E114完整native namespace formation×reading与固定标签关联，不改43条件；(2) 原E118四世界criterion×B私人约定，不改33条件/字节匹配/完整四点功能与actual-donor预测。两个问题用不同seeds并行，不以第一个的阳性选第二个。不扫层/头/标签，不加方法训练。
- **配置：** native discovery n16 seed119001→confirmation n32 seed119101 validation；criterion discovery n16 seed119201→confirmation n32 seed119301 validation。前者5504/11008、后者4224/8448评分。数值有效即按原冻结设计确认，正负都保留。科学脚本仅默认path/revision metadata/seed替换：native SHA2ac1db6e0fa8d1dcf8c28004f066a87550af8af2a013de0be87c811bcd7fb8eb，criterion SHAbb65c208f6a3d74f8903c1897e2d8f5c6bb215ab668420be292405ddb0e2dc1c。
- **读数：** native原D、两个A/B缓存背景signed/abs及signed交互，K/KV/V系数1raw/rule预测r/RMSE/zero、固定label cross−within；criterion全部F/S/bias/交互、两个task代码反转、J、native/A-only/label/形成边/far_label，全部公开。J是平均交互，两个task不同强度的同一gain方向也可产生J，不能单独当标准运输。直接看两task完整响应，Food与Service分别是否对齐；不将弱能力与弱接口混称全模型无表示。
- **阳性对照：** 原single A全部私人方向、criterion四single B/private函数、explicit/instruction；实际分块token流full/split与self≤.001；static label layer0 KV0、cache pristine/all-layer消费、样本full-rank与multiset/matched geometry；模型checkpoint与官方revision匹配。候选margin及全词表argmax分开。
- **噪声地板 + MIE：** 固定FP32/eager环境；bootstrap10000 context seed910，重建沿用E109；不用高r代替target非零/完整规则正确；零或反向也原样确认。不以某一模型版本继续失败作为科学前提。
- **混杂审计：** 14B与8B为同族能力对照，非第四独立架构；任务不同块不比作单独gating效应。完整新词/句式确认、字节交集报告；旧pin checkpoint不更新到新模型。源码metadata改动单列，读取操作不变；query自然演化，cache不是独立语义模块，actual donor充分近似不称无donor程序。
- **决策表（跑之前写）：**

| 结果 | 认识更新 |
|---|---|
| private能力更强，形成/关联效应保持 | 能力提高并不消除同一形成过程；比较正常使用与形成路径，不靠失败率定义论文 |
| native能更好处理来源，label/edge功能结构仍共同化 | 原生使用可补偿/选择已经混合的证据；解释数据支持的阶段分离 |
| label响应对两个B criterion产生可确认不同方向 | 来源形成证据具有更细功能内容，明确与8B差别，不自动称完整程序 |
| namespace预测在更强模型失准 | 当前形成子图存在能力/模型边界，报告实际残差，不继续头/层搜索 |
| private能力/数值不通过 | 分开接口/能力与科学阴性，保留所有失败；只修数值工具 |

- **算力预算：** 两独立单卡并行，fvcrc10空GPU0/1优先；模型copy一次、共享NVMe读取。每块≤.8 GPU时，实际记录run。空卡授权来自用户；不因可用全部卡填满无信息量配置。
- **定位：** Cho/CTA/AddUp拥有宽信息选择/上下文化解释，已有E115–E118提供来源功能测量。此项检验同一机制是否随能力改变，不因增一个模型自动产生novelty；普通paper共识源与最新近邻明确引用。

## 结果（运行后追加）
待预检/运行；模型identity及原始脚本差异在结果中记录。
