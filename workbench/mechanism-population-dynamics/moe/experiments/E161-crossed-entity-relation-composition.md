# E161：国家×所问属性同时改变的计算组合（2026-10-28）

- **状态：** PLANNED；已登记，尚无本卡干预结果。
- **类型 / 对应：** PILOT；C14，实际信息分工与可组合计算。
- **问题：** R流传递的是完整donor答案，还是可与recipient实体结合的所问关系/答案类别信息？

## 从已有结果提出的竞争解释

E158完整末位置R流在同国家换属性时，donor答案首token命中为P/A/B=.750/.938/.875；只换国家时仅.042/.125/.104，attention流则两种都很强。单因素交换不能区分R“复制完整事实”与“偏向选择所问属性、其余上下文保留实体”。属性内排名的主读数接近0也不能当无中介：POST-HOC诊断显示，干预前另一属性的正确答案已经在该属性集合内接近排名天花板，native mean win约.99。原主指标/全部结果保留，不重定义旧阳性。

新实验同时改变donor国家与属性，直接观察是否出现两输入的组合答案。例如recipient=法国首都，donor=德国语言：完整donor答案为German；保留recipient国家但换属性的组合为French；只换国家保留原属性为Berlin；原答案为Paris。四者都在已有数据中，由输入标签确定，不看新输出选标签。

## 固定设置与标签

- 完全复用E158的96条原始查询、相同24国家、两关系、四模板、tokenizer、P/A/B成熟pins，0新训练/新模型/新提示词。
- 对canonical target(r,c)，h=(c+11)%24；四个原生查询为q00=(r,c)、q10=(r,h)、q01=(1−r,c)、q11=(1−r,h)。实际source取q11，两个输入因素同时变化。
- 四个canonical首答案token必须全部不同；该条件对全部48target在CPU、读新模型前检查，不按模型/结果筛国家。
- 同E158在全部16层末输入位置交换R、S、联合RS或attention A；保持此前位置的原生decoder状态，另一组件在当前H下内生计算，不固定成旧target值。
- R/S/H/final residual复用E158 v3真实组件缓存；attention和native baseline参照E158 v4完成数据。新原生重放逐层H/组件和/final状态、所选LP/top10及attention位一致，原HF参数/buffer/cal必须同一。
- 新干预576次（3model×4path×2relation×24country），源完整residual正控144次。旧576匹配移除可直接追溯E158，不重测或冒充新结果。

## 读数与统计

主读数为真实全词表argmax落入五类的比例：original(q00)、entity-hybrid(q10)、relation-hybrid(q01)、full-donor(q11)、other。不在四个候选子集中重新argmax；五类互斥且和为1。原生recipient的同类比例及变化同行。

关键对比是每条路径的relation-hybrid率减full-donor率，以及R与attention在该偏好上的差；entity-hybrid偏好同时完整报告，不预设attention只传国家。另报四个答案token的全词表LP变化、KL和A−P/B−P历史差。所有路径/国家/两关系/other结果保留，不能仅挑R的有利例子。

全部24国家簇为主，paired country bootstrap1000、seed161001，等权两关系；只是固定source映射下的输入CI，非训练seed或世界事实总体。次分析预定为四个canonical查询在P/A/B全都native top1正确的target，不用干预结果；保存国家mask、计数与点值，无CI。四查询共同top10至少8/24每关系作为既有可检出性门槛，弱基线只封存可行性，不换模型或挑source追阳性。

## 阳性对照

- CPU真实旧数据映射，四标签不同、source同时改变两因素、五类分割及全词表top1分类、统计轴/符号/配对重采样已知答案。
- 真正GPU三原生参数/buffer及旧BF16 cal相等；全部96query对照旧native selected LP/top10、R+S/H/最终状态和attention缓存位一致。
- 全query R+S/A同source身份、两个固定query额外R/S身份，共588；新q11 final residual替换应精确恢复source整词表分布，144正控，构造身份不当新机制。
- 所有参数/模块/临时forward/hooks事后恢复；raw有限、source原始文件SHA不变。

## 噪声地板 + MIE

保留E158完整前缀执行与原生last-only读出（无KV），继承实际full-head/last-only floor6.12e−5 KL、argmax0变化，并原生精确回放；不从结果线性扣地板。组合率10个百分点或LP .1 nat作为解释量级，完整CI/基线同行，不自动判方向生死。首token答案、别名/同义语言限制仍在，不称完整自由生成准确率。

## 混杂审计与决策表（跑之前写）

三个公开成熟谱系状态不是独立初始化。R整体包括native路由选择的加权输出，不把结果单归给某个expert权重或唯一算法模块。多个流和后续计算可以共同携带同一因素；hybrid偏好是该窗口中的相对信息控制，不等于纯因子、知识存储位置或天然联盟。

| 观察 | 科学判断 |
|---|---|
| R更偏relation-hybrid，attention更偏完整donor或entity-hybrid | 支持路径对输入因素有不同的实际控制，组合答案超出完整donor词覆盖 |
| R主要给full-donor | 更支持完整事实/答案内容传递，削弱简单“R只传所问关系” |
| other多或gold source本身不被预测 | 如实报告动态范围/混合干预品质，不能按少量成功国家命名角色 |
| P/A/B定性模式一致而依赖程度不同 | 连接较可重复的信息控制与历史可塑的合作关系，不宣布任务唯一规定所有职责 |
| 身份或来源回放失败 | 修工程保留成本，不作机制阴性 |

## 算力与当前结果

单卡三BF16模型预计82–83GB；cap2 GPU·时含装载/预检/失败。使用已核验NFS端点的本机临时NVMe副本降低重复I/O，原始资产保留且新模型参数/cal须相等，0新下载。与E160并发至多2卡≤8；先完整代码/CPU/plan/Git冻结再读新条件。raw ~/mechpop_cache/e161_crossed_entity_relation/。C14维持L2，当前只有设计与实现准备。
