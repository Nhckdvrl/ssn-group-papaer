# E48：同一指称实体的事实表达×后续表达交叉（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E47表明额外名单影响预测，不能把词表改变直接归为身份含义。
- **问题（一句话）：** 在名字与描述明确共指时，角色证据的后续作用跟着同一实体走，还是依赖事实和读数的表达匹配？
- **设置：** E43固定全部24来源names/actor/predicate与E46普通nearby、old/newother同/不同V。外部模型逐条构造常规命名句将原两patient描述与fixed名字明确关联；所有条件都保留同一命名句，不新加identity roster。名字/稳定de-re描述两种oldfact＋unused nearby×名字/描述两种target，cross4；另无inventory/原E47 name inventory two levels，first/last twoorder，总8×1152=9216raw。E40 their nephew/brother需在推断前改为原actor锚定的de-re描述，不许在新actor下重绑；all12主＋事前原NP非possessive10敏感。两个actor不变；event/target其余words冻结，命名句改变前提但matrix内同世界角色事实等价。构造来源CC-BY4、全部源只cache；自然GUM别名/role的现成标注并行外审，先核能用何种材料，不将UD obj自动当patient gold。
- **读数：** 全部M/Dactivity/Dneutral/J；主newother sameV两fact/readout forms×inventory/order原cell，形式匹配交互(match−cross)在old/new及different−same；同entity role信号的cross-form传递和inventory调节。主匹配交互定义[(Name→Name + Desc→Desc)−(Name→Desc + Desc→Name)]/2，先family两source均值paired10000 bootstrap seed20261005。all/eligible/grammar common/E31固定层与nonpossessive10全报，不按score选别名或名次。
- **阳性对照：** old explicit患者能通过两种fact表达读出canonical name；名字/description mapping短答可访问，当前384(base/scope)、独立两mapping问96，共480native。R8一句要求按passage命名关联与activity scope回答，全报。paired目标各两alternatives causal prefix token一致，实际input form匹配后target与neutral完全对应。
- **噪声地板 + MIE：** 固定FP32 seed0 batch4/8；semantic equivalence必须外审而非主agent认定，Name/Desc本身words长度/语篇自然性不同；D按角色世界配对而非比两string的绝对probability。E47已说明role/inventory body效应不等价world probability，native正确性不能证明内部状态。
- **混杂审计：** 每个description必须在given命名句中固定指向同Name，source/other distinct按普通读法、group成员不强排除；mother/boy/puppy等原属性保留，不暗加排他患者或可用性。names与descriptions的“was nearby”只能说明附近，不assert参加；所有actor labels/patient world清楚。original possessive两个family显式修复、不可用“their”自由切换，若不能高质量绑定就在该family标uncertain并全报，不另换好看词。不把alias mapping本身当首创。
- **决策表（跑之前写）：** old control与mapping有效、negative迁移cross form仍稳→entity-level role期待解释更强，下一自然原文角色/共指用途；negative只有fact/readout匹配且neutral近同→词汇/表达匹配解释，不能叫entity memory残留；role-minus-neutral与new−old仍有形式交互→具体关系使用依赖表达，保留pragmatic/reference-form竞争，不直接认定hidden binding；仅inventory有效→表述的语篇设置仍必要，自然出现频率/功能用途是下一证据；所有new效应失去或old无效→收窄原候选、分析命名前提影响，不扩模型追信号。这个卡检验同一role-reuse问题，不另开对象或写论文。
- **算力预算：** existing venv/Qwen3-8B frozen，按fact×target形式4shards各2304raw GPU0–3，nativeGPU6/7，预计≤.25GPU·h；**实际：** 待填。
- **命令：** referent_form_roles.py build/adopt/split；frozen likelihood/native；analyze_referent_forms.py。语料先Step/Luna独立作者和全文外审，任何推断前完成。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
