# E79：foreign label提供了词典，还是提供了别人的规则？（2026-10-10）

- **状态：** DONE（词典lookup阳性，direct组合执行阳性失败；不做provenance机制归因）
- **类型：** PILOT；先检验语义分解任务的有效性，不在行为基础失败时铺patch。
- **对应：** I04/C09/C15/P17/P18。承接E74未鉴别、E76均值捷径、E77/E78函数描述先验控制；不预设新“识别却不用”机制。
- **问题（一句话）：** 相同的最终label翻转，若分别来自本Source的函数参数变化与共享输出词典变化，模型能否区分它们，而physical foreign-label贡献是否必须意味着foreign-rule使用？
- **为什么现在：** 继续堆operator准确率不能自动提升意义，Liu2024已拥有识别/预测/执行分离。返回更具体的推断桥：E48标签位置的来源是否足以决定规则证据的来源？共享词典反例在逻辑上不新；科学增量只有在可识别任务上因果拆出模型实际使用的变量，并对原任务的测量给出更准确解释才成立。当前仅建立有界behavior gate。
- **设置：** Qwen3-8B同revision、float32/eager、conda、空GPU0。16新contexts seed79001，Alice/Bob/Casey/Eli。theta_A/theta_B/theta_D独立copy/subtract，8组合各2；Casey公开固定copy。所有Source先做x或9−x，再用同一共享bijection g将0..9换为十个color words（每context随机置换）。A/B各Input2/7各2；C/D各Input0..9一次；28条混排。所有C/D标签各词一次，A/B各只g(2)/g(7)，每Source边缘不泄露theta。C已知copy使g可唯一确定，再由A/B的2/7关系唯一确定theta，避免全局g/函数同时翻转的不确定性。
  - Query A/B全0..9：seen2/7、插值3/4/5/6、外推0/1/8/9；另C全0..9词典lookup阳性。novel正确词在A/B所有demo均未出现，只在C/D的label中出现，Header/query都没有word inventory。这是“label词来源”条件，不说所有表示只来自foreign。
  - 两定义顺序（完整copy/subtract定义块交换）；E78已说明需要此控制，等权合并并分别报告，不选最佳。
  - 四证据：mixed inferred、mixed+一句Source scope、own+dictionary（所问A/B自己的4records＋Casey10records，仍保留合法共享词典，不能叫字面single Source）、mixed direct rule table（theta_A/B/D全部明确，仍需由Casey读取g）。Direct多给参数/变长，仅执行阳性，不作matched Header机制效应。
  - 八真反事实：base；owned_A/B/AB（只把相应Source的Input2/7交换、label Word位置不动，theta翻转）；lexical（g(v)与g(9−v)互换，仅v不为2/7，A/B文本不变）；ownedAB+lexical；foreign_D（D Input字段x↔9−x，label Word位置不动，theta_D翻转、g与A/B不变）；dictionary_reorder（C的novel成对完整records交换，g/所有theta不变、正确词位置变）。所有inferred条件长度/每Source输入与输出Word频率相等，label/input sites固定；direct更新其真table，不称pure Word edit。
  - 对novel query，ownedAB与lexical单独操纵产生**相同正确label翻转**，合起来又回到base正确词。这使输出词相同但latent原因不同；foreign_D与reorder不改正确答案。两类操纵不是同信息量控制：一个改私人函数，一个改共享词典，依exact oracle解释。
- **读数：** 精确十完整单token color continuation logp，strict margin>0 accuracy；seen/interpolation/extrapolation、copy/subtract、C lookup分开；对应base/changed oracle均保存，不挑seed/Source/定义顺序。owned/lexical同方向target margin响应、both取消是否跟随oracle；foreign_D/reorder影响。4000context bootstrap seed790，函数子组以ratio重采样所有context，不删无该函数context。
- **阳性对照：** CPU枚举两函数/共享g唯一识别；global/perSource Word频率、位置/长度、完整token分段检查；完整权重与no-op/full-forward-cache≤.10nats。Casey lookup≥.95，seen≥.90；direct两函数两novel组各≥.90才解释未知函数行为。
- **噪声地板 + MIE：** no-op≤.10；inferred两函数两novel组各≥.80才有行为基础。owned/lexical oracle-margin响应≥1nat且CI不跨0为读数有效阳性。foreign_D不敏感须95%CI完全落±.5nats，不能CI跨0当无效应；reorder同理但允许改变物理检索路径。要比较own+dictionary与mixed，accuracy差≥.10且CI不跨0才改变干扰判断。
- **混杂审计：** task family与共享codebook公开，不是arbitrary algorithm learning；known SourceC人为打破参数不可识别性，不能声称所有多标注数据都有共享g。novel输出词只在foreign label出现，Codebook利用必然依赖C；逻辑必要性不是attention机制发现。限制candidate评分非自由生成能力；Word语义/tok/先验虽随机g打散，须独立新word/new names确认；C reorder动整个record，是物理位置控制非仅单Word状态。Codebook真假因果变化与原ICES的同label任务不是同一数据分布，不据此抹掉原泄漏现象。
- **决策表（跑之前写）：**
  - C lookup/direct失败 → 接口/复合计算阳性无效，不把低分解释Source不能组合；先原生gate。
  - direct有效、inferred失败 → 仅证明已知参数执行与推断有界，不做foreign-label机制归因；已有Liu2024邻近，增量仍有限。
  - inferred可靠且own/lexical/both跟随oracle、foreign_D等效无影响 → 才进一步分解因果label messages的共享词典与private参数作用；物理foreign贡献≠rule来源成为可测对象，仍需独立确认。
  - 同时错误跟随foreign_D → 真foreign函数干扰与合法词典共享并存，继续分解，不以单一pooling或单一binding解释。
  - 仅Header order/reorder支配 → 先把边界定为格式/位置敏感，不称通用函数或provenance规律。
- **算力预算：** 空GPU0预计.15GPU·时；先本卡behavior gate，其它GPU不铺下游mechanism。**实际：** 429.0415s=.1192GPU·时。
- **产物：** scripts/e79_codebook.py、scripts/analyze_e79.py；small JSON入git，raw本地。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e79_codebook.py --model /tmp/ices_models/Qwen3-8B --out results/e79/qwen3_codebook`。完整CPU预检在权重加载/科学评分前通过，函数/词典唯一识别、gold XOR、word频率与分段等价均断言。
- **定位：** Wang/Cho labels、Few-Shot Examples Add Up的task-specific QK/non-specific V与alignment，Feng/Gur-Arieh的value检索、Cho信息过滤、Ortu read-but-suppress均属强近邻；一般attention≠解释已被拥有。需要具体parameter/codebook因果读数与适用范围，不以任务新命名宣布novel。

## 结果（跑完后填写；不改上方读数/门槛）

16新context、4证据×2order×8真反事实×30query×10候选完整，429.0415s=.1192GPU·时；no-op0、24项full-forward/cache max5.82e−5nats，原引擎hash未变。`results/e79/qwen3_codebook/{run,preflight,analysis}.json`；raw本地。

### 阳性未过，先收窄结论

| 证据（两order等权） | Casey词典lookup | seen A/B | 插值copy/subtract | 外推copy/subtract |
|---|---|---|---|---|
| mixed inferred | .9531 | 1.00 | .7500/.1953 | .7031/.1406 |
| mixed+Source scope | .9844 | .9844 | .6875/.2266 | .7266/.1094 |
| own+dictionary | .9875 | .9922 | .9844/.0234 | .8828/.0469 |
| direct true rule table | .9625 | 1.00 | .8594/.2188 | .8203/.1563 |

Direct subtract插值CI[.0625,.3889]、外推[.0667,.2639]，即使提供真实私人规则，也未可靠完成复合任务。Lookup/seen好不能推出算术/新词典的组合有效；**同context的numeric原子F尚未测，不能宣称两个原子都可靠却不能compose。** 整个direct gate失败，更没有inferred两函数≥.80的基础；不进入label messages/provenance patch。

Mixed own_A/B signed响应插值1.528[.435,2.774]/2.102[.471,3.980]，外推1.663[.450,3.010]/1.860[.539,3.335]。这些方向不等于完整函数执行，再次不能拿Source响应替代准确率。Lexical插值1.978[−4.375,9.121]、外推.853[−4.965,7.282]，未稳定鉴别；foreign_D CI非常宽，插值−.705[−5.258,3.763]、外推.057[−4.002,4.246]，**不满足±.5等效界，不说foreign函数无影响**。own+dictionary的foreign_D零效应由该source文本未入prompt逻辑保证，不当模型自主隔离。

own+dictionary−mixed插值+.0313[−.0859,.1602]、外推+.0430[−.0586,.1485]，未过差值MIE；Source scope同样无稳定恢复。高copy/低subtract差异允许copy字典的便利检索、数字→word接口、先后计算/Source规则读取不足等解释；不能由此直接推出新计算定律。

### POST-HOC错误签名与分析修正
`error_signature_posthoc.json`：每函数256个novel Source/query/order全保留。direct subtract48正确，151输出g(x)，57其它；own+dictionary subtract9正确，198输出g(x)，49其它。符合跳过数值变换直接lookup的输出签名，但没有内部时序证据，**“read-before-transform”只是猜测**。
初版analyzer对bool准确率数组做相减，报TypeError且尚未写analysis/打印科学统计；改为float subtraction，读数/门槛/样本不变。评分引擎与结果不改、不重跑科学数据。无主张升级。

### 实际决策
若继续此分支，按原表应先做native原生有效性和同context原子F/G对照。可能的解释包括即时候选评分接口、Source/算术读取、数字与Word的接口及计算顺序；广义组合缺陷、可解码≠部署、晚层hop/backpatching已有强近邻，不自动把本结果重命名成新compose limitation。

**本次综合排序（人纠偏之后）：** 不启动上述后续，不把它们当ICES整条主线的门槛。本结果保留为诊断；优先综合E59–E71已有计算证据与聚焦一个解释问题，见[`RESEARCH_SYNTHESIS_2026-10-10.md`](../RESEARCH_SYNTHESIS_2026-10-10.md)。这是投入排序变化，不改跑前标准或实验事实。
