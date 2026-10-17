# C02确认与C03阶段pilot：证据及混杂核对

主张范围：在固定LIGHT三阶段执行结构中，原persona附加的两套一致角色立场（firm/责任与agreeable/关系）改变实际请求物品转移的概率。人格干预包包含优先立场，不拆称纯BigFive效应，不把给/不给当唯一正确角色行为。

| EXECUTION §4项目 | 核对与范围 |
|---|---|
| 噪声 | pilot/confirm独立图，三个固定采样seed、图内平均及200图bootstrap；确认32B+13.7pp [9.7,17.8]，Gemma+6.7pp [4.3,9.3] |
| 工具有效 | 原native两路径CPU执行、原材料状态及canonical事件；协议/源引擎拒绝全部保留 |
| 选窗/采样 | 固定源图SHA split，一世界一个confirm任务；不按行为结果选样、补seed或调整读数 |
| 自校准 | 两P共用同一引擎和固定物品/requester/目标定义，没有各P自行打分 |
| 提示默认 | E55普通grounding后P差仍13.8pp/7.0pp；E56发现history阶段禁止动作的范围解释，撤销由其无动作推人格失效 |
| 输入一致性 | 固定world/角色/动机/request/观察/菜单和采样配置，全链路一致P；P词与责任/关系句共同改变，范围限整个指令包 |
| 幸存seed | 5501/5502/5503全部，解析失败/未裁决/源拒绝保留，27B不因进度较慢筛掉 |
| 算力 | 同一结构内P对照调用预算/采样相同；不同direct/plan结构只是参照，不能据其效率称新方法优势 |
| 污染/重叠 | confirm 200原图与40pilot图隔离；LIGHT公开预训练污染未知，所以不声称未见数据推理能力 |
| 多重比较 | 卡先登记四结构；核心P差完整报告，kind/QC切片明确是定位；不挑最大的结构当总体persona效应 |
| 地板/饱和 | 部分直接结构请求率低、goal控制高；核心计划结构报告绝对概率及区间，不以归一化扩大效应 |
| 系统特有 | 多模型但同LIGHT原生引擎/脚手架，限该任务族，不升级跨游戏通用机制 |

证据：E50、E55、E56实验卡；results/E50_32b_coherent_pilot_complete.json、E55_32b_independent_confirm.json、E55_gemma_independent_confirm.json、E56_32b_state_action.json、E56_gemma_state_action.json。代码与数据hash在各manifest，原记录在cache/runs。

定位：Personality Illusion、Rethinking Psychometric、Story Shapes、Persona Vectors、PDD、Trait Activation与Persona Circuit已经拥有人格/语境/策略作用等一般结果；FAIRGAMER已有角色身份对资源决策。C02是本项目可信的原生行为基础，不单独称新的顶会贡献。剩余研究通过原作者私有目标、动态伙伴、前置条件、取得手段和真实不可逆后果继续推进。

## C03与E50：阶段pilot的独有证据

同40图×三seed的32B一致人物，接受差+17.5pp [8.3,27.5]、计划优先请求差+19.2 [10.0,30.0]、完整渠道实体转移差+13.3 [4.2,23.3]。局部conversation×downstream（update+exec）单seed交叉中，固定两种downstream时conversation差均+15pp，区间[5.0,27.5]/[2.5,27.5]；固定conversation时downstream差约+2.5pp [−5.0,12.5]。这是阶段干预，不能当全链一致人物的独立确认，也未单独分离update与exec。

Agreeable无入口/agenda-only/memory-only/both实体转移8.3/27.5/11.7/19.2%，渠道交互−11.7pp [−20.8,−2.5]。120个配对分支中，agenda-only→both有8条转原任务、2条未裁决；记忆既有未执行先写“I gave”的例子，也有正常原任务提醒，不能将十条全归错误状态。C03保持L1，E51/E53/E59分别检查状态/目标/措辞竞争解释。

跨阶段residual读出还显示：conv–exec最后层方向cos在原字段/统一action读出下32B .140/.712、27B .018/−.047；两模型各480+480 forward，幅度约原激活10%–12%。测量协议会改变几何读数，没有统一人格耗散结论。原始tensor/geometry在cache及E50结果，不据角度升级因果机制。

来源与研究对象的选择依据另见E50卡：旧E42是焦点LLM＋15固定策略伙伴，DD指difference-in-differences；鸟的worm/nut绑定与校园局部人物干预是不同竞争解释，不共同证明人格失效。跨环境旧精确读回保留results/CROSS_ENVIRONMENT_CONTRADICTIONS_2026-10-15.json，不恢复相应旧实验。
