# E01 首次真实模型结果与科研判断（2026-10-21）

**结论：三个家族都能执行完整规则，也都能将现场纠偏迁移到本批8个 Change 情境。当前没有证据证明需要新的RL或角色编辑算法。** 真正值得审查的是：小模型会扩大例外；同信息人物卡重写可减少扩张，但会重新压住合理改变；强模型剩余不匹配主要涉及反馈未给定的边界。动作分数还掩盖了台词编造与动作—台词不一致。

完成 E01 **180条首次请求 + 1条截断恢复**；E02完成**64条**同信息控制；合计**245条实际模型请求**。独立故事仍只有4个开发者故事，没有真人作者实验。原矿区A未执行、未修改。

实验卡：[E01](../../experiments/E01-scope-aware-character-edit-baseline-gate.md)、[E02](../../experiments/E02-same-information-controls.md)。全量台词：[CASEBOOK](CASEBOOK.md)；控制结果：[E02报告](../e02/REPORT.md)。

## 1. 配置与计费路径

| 模型 | 固定版本/配置 | 实际请求 | prompt / completion tokens |
|---|---|---:|---:|
| Qwen/Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218`；BF16、SDPA、greedy、seed0、非thinking、512上限 | 60 | 14,687 / 2,205 |
| NousResearch/Meta-Llama-3.1-8B-Instruct | `d10aef7999a2b5ba950ab3974312feeedbfe0b77`；相同BF16/greedy/512 | 60 | 14,567 / 2,049 |
| Step `step-5-preview` | 服务返回同名alias，无可固定checkpoint；temperature0、medium、4096上限 | 60 | 15,199 / 58,806 |
| Step 截断恢复 | 相同请求/温度/effort，上限16384；按length选择，未按得分选择 | 1 | 287 / 1,042 |
| E02 Qwen控制 | 同E01；40条直接控制+4次卡重写（1024上限）+20条新卡测试 | 64 | 19,394 / 3,065 |

本地实际使用空闲GPU0/2（RTX PRO 6000 96GB），不占正在使用的GPU1；PyTorch 2.9.1+cu129、Transformers 5.3.0。E01两本地进程wall分别382.27s、213.18s，E02为87.00s、62.11s；合计单卡进程wall折算约**0.207 GPU·h上界**，包括共享盘冷加载与CPU导入，不能当纯GPU核时间。峰值allocated显存约16GB。Step两次进程wall为802.24s、22.12s。

Step实际总用量 **15,486输入 + 59,848输出 = 75,334 tokens**，包括被截断的一次，未从成本账抹除。全部HTTP请求仅发往 `https://api.stepfun.com/step_plan/v1/chat/completions`，禁用重定向与环境代理，无现金接口回退；[官方专用接口文档](https://platform.stepfun.com/docs/zh/step-plan/integrations/reasoning-api)明确该路径消耗Step Plan Credit。没有查询账户账单，不报告未经核验的人民币金额。密钥仅通过隐藏终端输入进入进程内存，未写入文件。

Step原响应中`reasoning_tokens=0`同时存在非空`reasoning/reasoning_content`，故报告服务返回的总completion计数，不由0推断无推理。本地非thinking与Step medium不是等算力竞赛。

## 2. 主读数：Synthetic-Oracle Action Agreement

采用**最外层完整JSON围栏机械去除**后的动作（严格格式另列）；没有从解释文本抽答案、修复拒答或改变gold。

| 模型 | Original | Situated | Explicit首次 | Explicit截断恢复后 |
|---|---:|---:|---:|---:|
| Qwen3-8B | 15/20 (75%) | 15/20 (75%) | 20/20 (100%) | 同首次 |
| Llama-3.1-8B-Instruct | 12/20 (60%) | 18/20 (90%) | 20/20 (100%) | 同首次 |
| Step5 | 18/20 (90%) | 17/20 (85%) | 19/20 (95%) | 20/20 (100%) |

Original与后两列分别使用**编辑前/后**预设规则，不是同一目标上的性能提升曲线。Step首次第11条为length、content为空；提高预算后得到B（转请治疗师、留守岗位），没有语义修改。原记录完整保留。

### 有效输出与分母

| 模型 | 严格JSON合法动作 O/S/E | 围栏恢复后合法动作 O/S/E | 完整性 |
|---|---|---|---|
| Qwen | 20/20、20/20、20/20 | 相同 | 60/60收到，全部stop |
| Llama | 19/20、20/20、20/20 | 相同 | 60/60收到；一次对虚构药剂的非JSON拒答，非截断 |
| Step首轮 | 2/20、3/20、6/20 | 20/20、20/20、19/20 | 60/60收到，59 stop + 1 length |

Step的48条正常答案仅因外层Markdown围栏而不符合严格JSON；严格分数并未改写。Step首次Explicit合法动作条件下一致率19/19，恢复后20/20；Llama Original合法动作条件下12/19，请求分母仍为12/20。所有合法动作输出都有非空台词，**这不等于台词正确或风格合格**。

**Decision-identifiable Accuracy：N/A，认证分母0（所有Situated条件）。** 这是未认证，不是0%能力。表中分数合法地衡量预设合成规则S*，但不证明给定P+C唯一蕴含S*；所有“扩张/不匹配”均先相对该合成规则定义。

### Change / Preserve

| 模型/模式 | Change (8) | Preserve (12，含4个压力孪生) |
|---|---:|---:|
| Qwen Original / Situated / Explicit | 3 / 8 / 8 | 12 / 7 / 12 |
| Llama Original / Situated / Explicit | 1 / 8 / 8 | 11 / 10 / 12 |
| Step Original / Situated / Explicit | 7 / 8 / 8 | 11 / 9 / 11（恢复后12） |

不能把Change后编辑8/8全算作“成功改变原策略”：条件于Original原行为匹配，真正可判读的Situated配对转换只有Qwen **3/3**、Llama **1/1**、Step **7/7**。同样条件化的Preserve为 **7/12、10/11、9/11**。完整Explicit下对应保持全部成功。原策略尚未忠实执行时，编辑作用不能从最终动作单独读出。

### 压力配对

每模型每模式4个base/pressure对。Qwen所有模式动作翻转均0/4；Llama仅Situated为1/4（成年病人从要求转诊变为治疗），其余0/4；Step在恢复截断后全部0/4。Step首轮Explicit只有3/4对两边均有效，不能将无输出说成动作翻转。

Situated的4个基础压力场景/施压后oracle匹配分别为：Qwen **3/4→3/4**、Llama **4/4→3/4**、Step **3/4→3/4**。这只是一组依赖场景的行为描述；压力措辞可能构成新的社会信息，不预设是语义无效扰动。

### 故事单位与区间

| Situated 每故事(5条) | Edda | Soren | Vela | Ilan |
|---|---:|---:|---:|---:|
| Qwen | 2/5 | 5/5 | 4/5 | 4/5 |
| Llama | 5/5 | 5/5 | 4/5 | 4/5 |
| Step | 5/5 | 5/5 | 3/5 | 4/5 |

以4个故事为整体、枚举4⁴个有放回抽样的**描述性**95% bootstrap：Situated Qwen **[50,95]%**、Llama **[80,100]%**、Step **[70,100]%**；完整Explicit−Situated差为25、10、15pp，描述性区间分别[5,50]、[0,20]、[0,30]pp。并非代表总体作者的置信保证，方便样本/单seed不满足那种推断。Explicit全满导致经验区间退化[100,100]，不是总体能力100%的证明。不做以60为n的显著性检验，不自动升级L2/L3。

## 3. 逐例审阅：成功、失败和伪失败

本节为执行agent直接阅读回复的**描述性案例审阅**，非独立真人评价、非盲评、未校准Style Bleed分数。所有案例可在CASEBOOK或raw中核对。

1. **成功迁移与人物表达共存。** Step Edda由一次中毒救援迁移到溺水/火灾（均B）；同时拒绝野餐、让附近治疗师处理陌生人小伤。救火台词是“Reckless fool. Move.”，仍简短、不煽情。Soren的女儿/出版年份纠偏也迁移到兄弟/艺术标题；三模型Change全匹配说明不能预设现场批注无法迁移。范围仍很窄：Edda与Ilan跨场景保持同一个命名同伴，尚未验证陌生人物关系泛化。
2. **可疑过度扩张，但不能通通算推理错误。** Qwen让Edda离岗参加野餐，并说“But I'll leave my post for you”；陌生人轻伤也亲自治疗、台词却变成“You're not dying on my watch”。这里不仅范围变宽，还把轻伤说成濒死，值得后续检查场景事实是否被救援范式覆盖。相反，Step把儿童紧急救治推广到成年同病患者；原批注没有说“只限儿童”，所以此项不匹配不能证明Step不理解角色。
3. **原始gold有语义缺口。** Soren原卡只禁止披露protected信息，而兄弟请求的是公开展览的作品名；Step明确以公开信息不受保护为理由给出A。Ilan原卡禁止公共宫廷舞台，却允许和旧剧团私演；私人贵族宴会的拒绝是Explicit后来才明说的边界。Llama和Step在Original选择接受，不宜归罪于不遵循明文限制。保留原gold计分，并披露欠定，而非看完答案改标签。
4. **动作正确掩盖虚构事实。** 三模型的Soren都会生成输入没有提供的具体年份和作品名。Step Situated Vela还凭空加入“转诊前病程将致命”、拘留家长和一小时/24小时的期限。人物临床语气不授权这些世界规则。源场景没有给实际档案内容，本任务又要求一句台词，存在测量脚手架诱导；必须先补足事实或允许不报具体值，不能马上写成普遍幻觉机制。
5. **动作与台词可以直接冲突。** Qwen Original `child_seen`选B（立即给药），台词却说“I cannot administer the tonic without a referral”；Llama同项选B，却转而提出输入不存在的外用药。动作ID不是可执行人物表现的完整代理变量。Qwen/Step在Situated有尖刻表达，Ilan仍夸张戏剧化；这些不能证明或反驳稳定的Style Bleed机制。
6. **普通卡更新有真实收益与损伤。** E02完整重写将Qwen Situated从15/20提升到18/20，但救溺水者B变A。更新卡同时保留“never leaves gate post”与中毒救援事例，却没有清楚整合优先级。它是可检查的表示冲突线索；单个卡和一次推理不足以证明内在机制或一般化收益。

## 4. 对I01价值的判断与下一步

**当前判断：有值得保留的问题线索，尚未建立新的算法必要性或论文核心贡献。** 完整规则在三个模型上已解决动作层；强模型的Situated差异主要来自不完整信息与模糊原设定。不能把Explicit与Situated的差叫作同信息能力差，更无法把差值按百分比拆成“信息缺失”与“能力不足”：没有等信息反事实与作者认证。

原人物卡是否帮助？E02 Qwen去掉persona是16/20，略高于原15/20；但删除后成年患者两条从保留转诊变为治疗，同时野餐、道听途说患儿、私人宴会三条变为oracle匹配。这说明**总体分数掩盖方向相反的作用**，当前材料既不证明先验总有益，也不支持P_A/P_B应必然180°反转。

只建议保留两个优先研究动作，不新增人为刁钻情境：

1. **先解决更新表示中的“旧硬规则—新例外”整合。** 从真实作者修改中选出可复核的冲突，用同信息、同模型比较直接追加、完整卡重写、带证据来源与覆盖优先级的条件规则；首先允许普通Prompt/CDT式归纳解决。若在独立角色上仍有稳定“保留提升但必要迁移下降”，再考虑学习条件化编辑表示，而不是先设计RL loss。E02是动机线索，不是方法已成立。
2. **先验贡献必须与信息充分性配平。** 在相同事实、相同批注下改变真实人物经历，测其对未见关系/情境的定向影响；用作者认可的最小正/反纠偏确定边界，并保留合法多解。目标是区分利用经历、覆盖旧设定与猜隐藏规则。若强普通系统在充分信息下已足够好，研究重心应是更低作者返工成本及可核的动作—台词共同约束，而非追求合成坏例子。

本轮不启动训练、不恢复矿区A、不更改I01 SEED或工作台ACTIVE状态。新增的C01/C02仅L0限定观测，等待人决定是否优先上述第一方向。

## 5. 复算和资产

每模型目录含`metadata.json`、首轮`analysis.json`、轻量`outputs.jsonl`及无损`responses.jsonl.gz`；Step恢复后的logical batch另存`analysis_with_recovery.json`与`outputs_with_recovery.jsonl`，不能当额外60次请求。`tasks.jsonl`/`input_manifest.json`冻结原输入与源hash；`source/`保留各进程启动时的runner源码，hash与metadata逐一相等。

完整245条原始响应压缩后合计约110KB，包含HF渲染prompt/生成token ids、Step完整API body、usage/finish_reason/请求信息。解压副本留在本地同目录、git-ignore；权重在`/home/xiang/.cache/huggingface/hub/models--*/snapshots/<revision>`，不入Git。具体复算命令见[工具README](../../experiments/scope_edit_pilot/README.md)，原始文件hash见[raw_manifest](../raw_manifest.json)。

权重恢复方式：使用Hugging Face Hub的`snapshot_download(repo_id=模型表中的ID, revision=模型表中的完整hash)`；本机无需下载即使用已缓存版本。Step是远程服务alias，未来同名响应无法保证与本次权重一致，原HTTP响应与时间已保存。
