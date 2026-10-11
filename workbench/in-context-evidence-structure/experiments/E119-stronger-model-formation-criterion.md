# E119：更强模型的同一证据形成与功能规则（2026-10-11）

- **状态：** DONE-CONFIRMATION（2026-10-12；两独立问题各16→32，独立校对4/4完成）
- **类型：** REPRO / 跨能力计算边界，不锁定论文。
- **对应：** C21/C22/C23、I04、P17。
- **问题（一句话）：** 模型更强时，输出命名/历史关联的形成路径仍参与原生预测吗？多方面的来源关系会改用更有criterion特异性的表示吗？
- **设置：** Qwen/Qwen3-14B revision 40c069824f4251a91eefaf281ebe4c544efd3e18，FP32/eager/frozen；官方模型是post-trained hybrid thinking/non-thinking，非Base。本次plain continuation无需chat/显式reasoning，不把它叫完整reasoning压力测试；8B同族也不是Base。8 shard cached29536665640字节，从官方缓存复制到fvcrc10，实际RAM缓存位置见下文；A10080GB单卡独立完整模型，弱互联不作集群训练。
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

- **算力预算：** 两独立单卡并行，fvcrc10空GPU0/1优先；模型复制一次、共享RAM模型缓存读取。每块≤.8 GPU时，实际记录run。空卡授权来自用户；不因可用全部卡填满无信息量配置。
- **定位：** Cho/CTA/AddUp拥有宽信息选择/上下文化解释，已有E115–E118提供来源功能测量。此项检验同一机制是否随能力改变，不因增一个模型自动产生novelty；普通paper共识源与最新近邻明确引用。

## 结果（运行后追加）
预检与四批GPU评分全部完成；探索/确认均保留。模型身份见`results/e119/model_identity.json`，官方配置/8 shard大小核过，未把cache blob名核验冒称全文重hash。

### 存储执行校正（无科学评分）

fvcrc10复制后根盘余量过低；只把本任务复制的Qwen3-14B移动到空余131GiB的/dev/shm/ices_models/Qwen3-14B，释放本任务约27.5GiB占用，不碰其它资产/进程。采用RAM模型缓存、独立80GB GPU，源码/权重/指标不变，实际--model覆盖该路径。模型仍官方post-trained revision40c069824f4251a91eefaf281ebe4c544efd3e18。

### 功能方向观测（首个E119评分前冻结）

E118独立校对指出平均J可被两个task不同幅度的同一方向产生。E119额外保存每个context的2×2 causal-code-response matrix（行Food/Service标准，列Food/Service输入响应）；共同方向＋任意行增益的受限解释预测determinant=0。报告signed determinant与signed normalized rotation的context CI、完整matrix；任一行norm≤.001nats时rotation定义0并记录count，全部contexts保留。det≠0可反驳这种受限功能gain解释，但不排除非线性latent等价、不证明独立criterion program。此是现有完整响应的功能区分，未扩条件或GPU实验，observer SHA e453f4b97c9f50cb2d567bbb4f80c3e8e9f9cac2f0eba0ec96ea048b50197407。不能把旧E118 post-hoc方向解释冒充本prospective验证。

### 14B确认：既有形成路径保持，交互方向并非所有模型相同

两个私人方向single A均100%。正常全Source读取时，改变A形成历史在B shared/far背景的幅度作用分别3.0595[2.5573,3.5707]/2.4969[1.8282,3.1579]nats；signed交互−.6856[−1.1330,−.2368]，与8B家族确认的正交互不同。它确认条件依赖，而不是统一正向放大电路。

冻结系数1历史答案KV对native A-label namespace rule反事实：两个背景r .9337/.9271，RMSE1.0473/1.8182（zero2.6105/3.9488）。固定标签关联的KV cross−within abs .3180[.2256,.4214]、signed .2488[.1151,.3898]。形成效应没有因使用14B消失，V-only namespace重建较弱也完整保留。

### 14B确认：criterion的功能结构与标签子图不能等同

单A Food私人方向84.4%/79.7%；单B四task/private函数82.8–87.9%，explicit Food98.4%；native请求A准确率75.4%。不以candidate margin或下列矩阵冒称全任务已解。

| n32确认 / 接口 | J（nats） | signed det（nats²） | signed normalized rotation |
|---|---:|---:|---:|
| native | 0.3432 [0.2649, 0.4326] | 0.5680 [0.4078, 0.7509] | 0.4098 [0.3304, 0.4926] |
| gate | 0.0585 [0.0294, 0.0890] | 0.0289 [0.0032, 0.0553] | 0.1899 [0.0734, 0.3097] |
| label | -0.0238 [-0.0478, -0.0025] | -0.0201 [-0.0374, -0.0052] | 0.0059 [-0.1207, 0.1400] |
| label_gate | 0.0383 [0.0119, 0.0683] | 0.0074 [-0.0106, 0.0271] | 0.1237 [0.0167, 0.2422] |
| edge | 0.0060 [0.0029, 0.0093] | 0.0007 [0.0001, 0.0013] | 0.0848 [-0.0419, 0.2145] |
| edge_gate | 0.0126 [0.0076, 0.0188] | 0.0019 [0.0003, 0.0047] | 0.0720 [-0.0402, 0.1896] |
| far_label | -0.0192 [-0.0348, -0.0060] | 0.0019 [-0.0012, 0.0056] | 0.0109 [-0.1450, 0.1636] |

native两task各自偏向对应方面：Food选择性.2823[.1989,.3711]、Service .4042[.2942,.5284]。A-only完整缓存仍有正det/rotation，说明B的criterion相关历史作用能够通过剩余图进入新输入判断。但A-label只交换并未重现native的两个方面选择性；其负det也表明不能把形成端全部宣布为rank1共同增益。label_gate normalized rotation小正而det区间跨0，历史答案边则det小正而normalized rotation区间跨0；尺度/符号/完整profile均保留，不挑一个读数宣布成功或不存在。

答案KV的系数1预测对actual A-label反事实只是部分：native/gated r .668/.665、RMSE .646/.878（zero .746/1.018）。因此输出命名的形成子图解释更强、criterion方面响应呈接口依赖；后一措辞只描述测得的功能接口，不定位新的独立模块或全latent程序。

**范围：** 14B是同族大小对照，未控制训练数据/配方，不能把差别只归因于参数规模。Food始终在Service前；功能方向区分不等于位置无关criterion。当前测的是请求A且A raw固定时B规则的影响，不是B自己任务能力或成功Source隔离。

**完整性与独立校对：** 4批96contexts、29184评分、.746101记录GPU·时；full/split最大1.72e−5，self/layer0 0，40层消费完整。独立primary4028项max4.66e−15、observer1528项max1.67e−16，720 CPU token流/15360 availability项通过；没有独立GPU重跑。E115–E119总计24批/576contexts/181632评分，三份审计封版，计数不是科学价值证据。

**结果文件：** `results/e119/{native,criterion}_{discovery,confirmation}/{analysis,run,preflight,completeness_audit}.json`；criterion另有`response_rotation.json`。见[独立校对](../results/e119/independent_review_2026-10-11.md)、`wave_summary.json`和[完整方向图](../results/figs/fig_stronger_model_functional_responses.png)。
