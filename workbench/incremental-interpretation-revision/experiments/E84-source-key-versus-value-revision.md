# E84：关系修订的源地址匹配与内容取出（2026-10-07）

- **状态：** DONE；生成器E431在任何效果前改本线E84，非POST-HOC。
- **对应：** I02 / C09 / P17，GP先前关系的修订在Source内容还是消费者对Source的匹配中发挥功能。
- **问题：** 既有whole-state源修补正向恢复不共同，但反向cue角色损伤跨族；E83发现条件后到证据与整体代价不同，仍不是完整parse恢复。回到更具体的源消费对象：cue带来的变化经K地址匹配还是V内容读取起作用？只拆这两个关键投影，不扫head/层/更多mask，不把一般routing/content概念叫novel。
- **定位：** Hanna有GP特征共存/QA未复用，Feng与Gur-Arieh有binding与匹配，Lee2026有contrastive QK工具；source key/value一般分解已有owner。增量若有必须是自然关系修订的具体、可预测后果和可跨用途恢复，不是单张attention图。当前未认定finding，已有工作不自动关线。
- **数据：** E64完整已冻结输入/QA/Source banks，三族同一源原发表MVRR/NPZ/NPS、双向GP/cue（NPVP缺失完整报告）。0新数据/标注/生成，不审原数据，复用原gold/映射/原Source-span，teacher Role不为本轮QA先行门槛。K/V的PAIR源来自原E63 quarter-layer自然cue修补后轨迹，不是完整cue oracle。
- **条件：** BASE_BANK与TARGET_BANK完整E64原QA复用。新KEY_ONLY/ VALUE_ONLY：每层Source block output均回放BASE_BANK；从下一层的同一个BASE/PAIR目标位置hidden分别经该层input-layernorm、k_proj或v_proj，仅覆盖对应Source目标token的投影。K投影之后照接收者位置作原k_norm/RoPE，无移入donor位置旋转。其它Source投影、queries、Task token都原计算。每层内Source queries可变化，但其output被BASE回放覆盖，不宣称所有Source内部计算native不变。问题未知的原Source轨迹及bank SHA锁定。
- **必要仪器：** 在固定首源验证K+V同时替换重现原TARGET_BANK QA（<.001），BASE回放重现原母BASE（<.001）；K-only的V、V-only的K、非Source目标位置投影均字节不变。投影后续normalization/rotation按模型原实现走；Source回放输出每层精确BASE，非Source输出不覆盖。K+V只作数值仪器，不新增整面板控制。
- **主读数：** 原gold correct/p_correct，initial/final/all/joint全Q、全部3族3构式GP/cue与words/letters/两mapping，KEY−BASE、VALUE−BASE、KEY−VALUE及对TARGET参照；原强位cue/其它关系保持。10000 lexical cluster bootstrap seed84，FP32/eager/seed84，8独立H20按Source SHA分片。
- **阳性对照：** 母BASE/TARGET和原cue；上述投影/回放/母LP一致性，没有额外gold、QA或answer进入donor。数据/model/bank/config/raw SHA闭合。
- **噪声地板：** 全mapping flip和paired CI，母LP/重现数值误差；不按首个效果挑层/头。NPZ9等小规模限制明示，不为了显著扩同一cell。
- **混杂审计：** 固定每层Source轨迹是规定的consumer协议，不独立认证native源内传播/正确parse保存。Cue whole-vector包含多种语义/位置因素，K变化不能直接命名某个语法变量，V也不是纯实体语义。非线性KEY+VALUE不按效果相加，queries在后续层会随先前输出变化。单用途QA恢复需要实际Role功能才能升级能力/好idea（R8）。
- **决策表（跑之前写）：** KEY跨三族两构式共同两关系恢复且cue保持，VALUE不同→源匹配是具体功能入口，再自由角色用途检验；VALUE共同恢复→内容可用性入口；二者类似或都损正确关系→一般信息/融合，不能拟合routing故事；异质/null→整个K/V块自审收束，不追head/层扫描，转当下E82强baseline与完整E70/E67真实断言。新颖性定位不是桌面判断。
- **算力预算：** ≤2GPU·h，仅2个新投影模式，原base/target不全重跑，原输入/缓存全复用，0API。8卡Q3/G2/L3、offline、保留轻服务；raw/config/banks外置E84。

## 结果

实验与完整分析已完成，最终结果见下。

CPU三族944个原QA读出/映射、108Source/51lexicalclusters、M19/NPZ9/NPS26 GP源，与母cohort/prompt SHA/gold完全一致。共5664新增K/V条件，0API；输入SHA ac680197e3f4ed9672bf25707441b12566f024cdba17f4134417272d01fe22b5。8卡PID 2835054, 2835055, 2835056, 2835057, 2835058, 2835059, 2835060, 2835061，各分片先K+V/BASE母LP与投影/回放仪器，再跑两新模式；不读partial效果。


### 完整结果、自审

8分片5664新条件完成，.237380GPU·h/0API；5400格全部报告并读取（NPVP/无other空格保留），全部240mapping噪声行、覆盖与8分片仪器核对。BASE母LP差全0，BOTH重现母TARGET最大.000122。最终v2 map SHA3b69b7fd235c8c9dcde309024baf00f69304a8ee7ef6ae6154cb9f9f6b91a73f，raw/bank/model/config/provenance入summary。

统计勘误：v1误用原cluster/target而非冻结analysis字段，重复来源被多算；v1 VOID记录外置保留，v2新增逐项母metadata断言后重算，原raw/条件/队列不变，不引用v1科学结论。最终108Source/51clusters（M19/NPZ9/NPS26 GP）。MVRR只有11/19 units同时注册initial/final，4只有initial、4只有final；NPS21/26双关系、2initial、3other。joint全注册QA不冒称每源完整parse；原E70原子图覆盖的是同S全部publishedQ，分母另有区别。

MVRR GP VALUE−BASE initial p_correct Q/G/L +24.97 [+0.30,+49.77] / +6.98 [-9.83,+22.35] / +13.62 [+6.82,+21.25]pp；KEY−BASE +2.83 [-11.93,+20.04] / +3.26 [-6.82,+13.70] / +6.87 [+2.83,+11.63]。NPZ VALUE−BASE initial +22.24 [+0.02,+55.55] / +16.58 [-0.01,+38.73] / +22.72 [+11.80,+33.56]（仅9clusters）；K部分也有影响。NPS Q/G改善接近0，L有小收益，不能拼成共同机制。完整initial/final/other/all/joint、words/letters、两方向与6contrast均报。

MVRR GP joint VALUE−BASE correct +13.16 [-7.89,+36.84] / +0.00 [-13.16,+10.53] / +5.26 [+0.00,+13.16]pp；NPZ +22.22 [+0.00,+55.56] / +11.11 [+0.00,+33.33] / +0.00 [+0.00,+0.00]。没有跨3族2构式共同完整恢复。MVRR cue initial VALUE−BASE p_correct -26.34 [-51.11,-1.35] / -10.04 [-26.59,-0.03] / -14.40 [-27.08,-4.40]，V会破坏正确关系；KEY损伤较弱，但也未成为共同repair。L letters最大mapping flip52.27%，均保留、不能忽视。

当前最好三句：消费者通道有不对称，V往往贡献更多关系变化，K也能调制而非纯地址空壳。其共同完整修订与正确关系保持未成立，不能将一般K/V路由机制或反向损伤叫novel。这个核心块到此自审结束，不继续head/layer/更多mask；下一E82当下强模型的真实错误分布和正在完整闭合的E67自由断言，原数据不追加审核。C09限定L1/C06–08L0不变，无需人决定。
