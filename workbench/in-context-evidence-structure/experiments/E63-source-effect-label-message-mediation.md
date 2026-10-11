# E63：来源影响是否由重新读取标签传递（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（从位置效应追至计算链；不将“有旁路”本身作新颖性）
- **对应：** I04、C12/C13；E59source-name K中介；E61需label K+V才恢复；E55晚层attention弱来源偏好。
- **问题（一句话）：** 来源名字K改变答案，是因为改变了答案位置接收的label-anchor消息，还是主要通过其它消息/后续读出调节？
- **为什么现在做：** “source在name-key、mapping在label-KV”不说明计算的顺序，也不能证明source决定读哪组label。只有对信息消息而非token位置作干预，才能分开source-conditioned retrieval与post-retrieval modulation这两种解释。
- **设置：** Qwen3-8B frozen，E59的before模板与同词表；base与source-name K swapped（所有层）作比较。按head计算答案末位attention对label anchors的贡献，过o_proj得到label-message；source-name消息同法。记录base的每层末位消息，然后在source-K swapped计算中替换为base：
  - 全层label-message冻结；早半层label-message冻结；晚半层label-message冻结；全层source-name-message冻结；全层attention输出冻结（阳性）；base+label-message自身冻结（no-op）。只对query最后位置，不修改prefix或其它query token，明确保留绕过末位的可能路径。
  - discovery：64 synthetic animals/fruits yes/no seed63001 +48真实E56 train-pool seed63002。
  - confirmation：64 synthetic occupations/vehicles toxic/safe seed163001 +48真实test-pool seed163002。
  - synthetic/real head/pools/sign/token验证与前卡一致。label-message系原始attention×V的组件，不从答案正确与否挑head。记录所有层所有head的label attention source fraction作辅助。
- **读数：** base−source-K swapped的raw margin效应；冻结各消息后的剩余效应及相对完整效应fraction（分母≤0.2nats不归一化）；context bootstrap95%CI；准确率；末位label attention对base对应source的份额变化。no-op精度与重建att输出相对RMS误差，标明bf16分解近似。
- **阳性对照：** all-attention-output冻结应恢复base（≤0.10nats）；base自己的label-message冻结应≈base；source K swap effect须可测；完整sum attention×V×O与原模块输出RMS误差记录（应<0.02相对值，若超出停止解释组件结果）。
- **噪声地板 + MIE：** 前卡no-op=0；组件bf16分解有数值噪声，实测。全label冻结移除≥0.70效应并在确认材料复现才称强中介；仅移除≤0.30且source/freezing-all controls有效，则更支持非label消息或后续读出调制。阈值为pilot解释，不给head新命名。
- **混杂审计：** 配对源名字/标签/内容/位置；干预仅消息组件；无训练/无gold-dependent selection；全部预定层报告；真实train/test分离；未控制：末位冻结不阻断其它query位置传来的label信息；base组件替换是hybrid干预；分解bf16误差；需要path patching才能宣称具体串行电路。
- **决策表（跑之前写）：**
  - label消息冻结大幅移除source effect → 来源影响依赖末位label重新读取，继续检验source→query→label路径，不先宣布新结构。
  - label消息冻结保留大部分effect，source消息冻结显著移除 → source可能在另一通路调节任务/读出，“来源选择=按来源选label锚点”不充分。
  - 两种组件各不充分、all冻结充分 → 跨位置/多消息协作，保留开放解释。
  - 数值阳性不通过 → VOID/修harness，不解释机制。
- **算力预算：** ≤0.7GPU·时；**实际：** 0.053 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 原生eager重跑全部控制通过：完整attention×V×O重建RMS=0，no-op/all冻结logit误差0。初版SDPA分解两运行VOID。
- 只冻结答案末位label-message：source-K效应仍余synthetic发现0.692[0.655,0.726]、确认0.508[0.479,0.536]；real确认0.501[0.439,0.559]。末位name消息冻结基本不改变来源效应。
- 结果：`results/e63/*/analysis.json`。不能由末位阴性断言post-retrieval/不用label，因为其它query位置可能已读label；因此串行推进E64范围对照。

### 阳性失败与修复（2026-10-10，未解读机制结果）
首轮SDPA分解最大相对重建RMS=0.0723，超过跑前0.02阈值（平均0.00367；no-op与all冻结logit误差0仍不能替代组件验证）。两首轮目录`_invalid_reconstruction`标VOID、不作证据。修复为eager backend，直接用模块返回的原生attention weights与原生V分解，完整attention@V@O按相同维度重算，去掉独立QK/softmax近似；同原种子完整重跑。backend改变记录在run.json/脚本hash，不改读数/阈值。
