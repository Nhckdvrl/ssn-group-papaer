# E58：来源表示跨标签迁移与锚点因果交换（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（高信息量机制判别，不训练主模型或 adapter）
- **对应：** I04、C12、C13；检验 E55/E56c 的“来源—标签合取”候选解释，未将其写成成立主张。
- **问题（一句话）：** 来源身份在标签锚点上是否有可跨标签迁移的表示，且只交换这些锚点的 key/value 是否足以改变来源条件化答案？
- **设置：** 冻结 Qwen3-8B，bf16 / SDPA。16 条样例，两个来源 Alex/Sam × 两个输出标签，各组合 4 条；输入为 animals / fruits 的简单语义分类，来源规则互为反转，每上下文随机决定规则方向。次序随机，标签/来源/语义类频率严格平衡。每个上下文构造双胞胎：只交换全部来源名字，输入/标签/次序不动；要求名字单 token，所有锚点位置逐位相同。查询用未出现在该上下文的词；两来源 × 两输入类，答案统一在相同标签空间。
  - discovery：seed 58001，64 train / 64 test，上下文为分组单位，词库 animals/fruits；标签 yes/no。
  - independent confirmation：seed 158001，96 train / 96 test，独立词库 occupations/vehicles；标签 toxic/safe（任意分类代码，不给定情感语义）。确认集在方法固定后运行，不筛上下文或种子。
  - 默认头说明 + 一句指令（“Use only examples from the requested source; each source may use a different mapping.”）。因果交换采用默认说明；指令是能力/default control。
  - 记录模型 revision、完整配置/脚本 SHA256、原始逐上下文结果。相同模型优先单次加载；Mistral-7B-v0.3 在 primary 测量有效后作有界复现，不视为本实验达到 L3。
- **读数：**
  1. **表示：** 每 4 层 residual；每层 pre-RoPE K、V。按完整上下文固定 train/test（双胞胎不可跨集合）。主读数使用双胞胎差分去掉内容/标签/位置共同成分；X 上训练无截距 ridge 来源解码，测试未见上下文 X（within）与 Y（cross），反向亦然。训练预处理只使用训练集；报告准确率、按上下文 bootstrap 95% CI、source-effect directions cosine。原始表示的 train-centered probe 作为辅读数。
  2. **因果：** 从名字交换双胞胎取 cached K、V，分别移植 base 提示中全部标签锚点的 K-only / V-only / KV（所有层），query 不变。读 source-correct label margin，准确率，及 (base margin − intervention margin)/(base margin − renamed margin)；分母弱时只报未归一化配对差。只修改缓存，不给模型新训练。分别衡量来源信息在“选择哪条”与“读出什么”中的参与。
  3. **跨词表：** discovery 的来源方向直接作用于 confirmation 表示，仅解码，不重新拟合（不同输入任务导致不能单独归因词表；内部 X→Y 迁移才是主要判别）。
- **阳性对照：** (a) 标签 identity 能解码；早层来源 within 可解码；(b) 全 prefix cache 移植必须复原 renamed 结果（max logit difference ≤0.10 nats）；(c) no-op cache 逐位相同；(d) base 与 renamed 源正确 margin 应反号/有差，否则该 causal 读数不可判；(e) query 单 token 标签健全性。
- **噪声地板 + MIE：** 固定 8 个 context 的重复前向，报告 bf16 误差；随机置换 train 来源标签的 probe 与 matched random-direction 作为解码地板。bootstrap 单位为 context，不把 16 anchors 当独立样本。within ≥0.80 且 cross 比 within 低 ≥0.15（CI 不跨 0）才推动合取解释；cross ≥0.80 且 gap≤0.10 支持可迁移来源成分（不等于完全因子化）。causal raw margin shift >0.20 nats 且 CI 不跨 0 才值得追进，阈值只为本 pilot 排序。
- **混杂审计：** 噪声：重复测量；工具：阳性对照；采样：全 factorial + paired identity swap；自校准：统一 logit margin，未用每条件增益；指令：一句恢复 control；输入一致性：token/anchor assert；种子：预定全部报告；算力：无 adapter，不涉及训练成本比较；集合重叠：上下文分组，确认输入词库不重叠；多重比较：完整层曲线报告，预定检索层 16–35 不挑峰值；饱和：准确率 + 连续 margin；系统范围：先单模型 L1。**未控制：** 语义类别任务与真实标注任务不同；名字差分包含对整段上下文的间接作用；K/V transplant 是 hybrid intervention，不能等同一个独立来源构件；RoPE 位置影响，因此主 probe 在 pre-RoPE K 上完成。
- **决策表（跑之前写）：**
  - within 高而 cross 稳定低 → 支持 label-dependent 来源表示；后续才检验联合编码的交换方向，不宣布充分解释。
  - within/cross 均高，且 K 交换影响答案 → 独立/可迁移来源成分参与检索，否定“只有合取来源表示”作为充分解释；转向默认权重/程序选择。
  - within/cross 高，但 K 交换无效、V 交换有效 → 来源主要通过 payload/后续读出参与；不能把表示可读出当作 retrieval 可用证据。
  - 两类交换都弱、全缓存交换有效 → 主要来源计算可能在其它位置或 query 表示，标签锚点并非充分中介。
  - 默认已近饱和或一句指令恢复 → 本任务是计算程序的阳性/边界对照，不能据此确认旧任务失败普遍性。
  - discovery 与 confirmation 分歧 → 报告边界，保留竞争解释，不能将否定结果吸收进 I04。
- **算力预算：** Qwen3-8B ≤2 GPU·时（预计 <1）；有效后 Mistral ≤1 GPU·时。**实际：** 0.050 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。Conda `verl-clean`；本地 NVMe staging 避免 NFS 重复加载。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 发现/独立确认/异家族复现全部完成。合成检索层source差分跨标签：Qwen残差0.984–1.000、Mistral1.000；真实评论独立池（E59同协议）残差0.992–1.000，但K最低0.724，V最低0.823，方向不对称。只能说存在common source component，不能说整个source编码独立。原始表示probe与双胞胎差分probe分开保存在JSON。
- 标签锚点KV仅传递完整source-swap效应的Qwen发现0.036[0.009,0.065]、确认0.016[−0.010,0.042]、Mistral0.045[0.019,0.072]。完整cache/no-op/repeat误差均0。
- 结果：`results/e58/*/analysis.json`；按表削弱“仅source×label合取”充分解释，将问题转向可读出与实际中介的区别；C14新增L1，未作普遍编码结论。
