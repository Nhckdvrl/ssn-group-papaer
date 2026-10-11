# E65：query接力与直接标签复制是协作还是干扰（2026-10-10）

- **状态：** DONE
- **类型：** PILOT（C16/P13的下一环，未把“多阶段”当novelty）
- **对应：** C16、P13、I04；E64 whole-query与final-token差异。
- **问题（一句话）：** 来源条件化是否经query中间位置接力到答案，答案直接读取demo标签是增强还是削弱这个判断？
- **为什么现在做：** E64只说明整个query的label消息重要，尚未证明query→answer接力；把whole-query冻结读成完整source binding属于越界。本卡检验具体边，并用native删消息区分有用/有害读取，而非只看where。
- **设置：** frozen Qwen3-8B、bf16/eager，无训练。沿用E64的16-demo平衡2×2任务、固定(x,source,label)、default query布局Input→Source→Label冒号。
  - discovery：64 synthetic animals/fruits yes/no seed65001，48真实评论E56 train-pool受控反转规则seed65002。
  - confirmation：64独立synthetic occupations/vehicles toxic/safe seed165001，48独立real test-pool seed165002。不得选择正确答复/seed。
  - 模型revision/conda与E64相同，primary有效后在Mistral同synthetic发现材料做有界复现，不展开模型清单。
  - 用fast-tokenizer offsets把query非末位token固定分成input field、source field、label marker；与padding分开，三组严格覆盖所有有效非末位query token。字段是跑前定义，不选峰值。
  - source perturbation：只换prefix source-name K（E59/E64操作）。记录base全层原生attention head消息。在干预运行里，将答案末位从query_input/source/label_marker/all_nonfinal_query收到的消息替回base；比较prefix label→末位、prefix source→末位；联合替回prefix-label＋all-query-relay。all-attention-output冻结与base自冻结作阳性/no-op。
  - **native 2×2删除：** prefix label→末位消息、all_nonfinal_query→末位消息分别开/关，四条件同context；不删除prefix或query token、候选词、不训练新模块。sourceK扰动下亦做相同2×2，避免“关闭所有ICL所以来源差异消失”的伪解释。
  - 消息在head-space用原生attention概率、V定义，delta后仅经一次native O_proj；记录精确重建/no-op，避免对after-O_proj组件的bf16重复舍入。
  - 一句指令baseline及single-source参照作为能力/可识别性control；因果判断以未加指令的native程序为对象。
- **读数：** base−sourceK的paired source-correct margin变化及各边替回后的剩余量；完整效应≤0.2nats不归一化。删除2×2的accuracy、correct margin、sourceK效应、interaction，并同时报告single/instruction。
- **阳性对照：** 原生P@V@O重建相对RMS<0.02；base自冻结/full-attention冻结≤0.10nats；query字段覆盖/无padding/因果索引assert；保持模型native baseline与干预模板逐位一致；源码hash、config/tokenizer origin固定。
- **噪声地板 + MIE：** E64精确控制=0；本卡重新核对。relay替回与prefix-label替回各部分、联合剩余≤0.20且CI不跨0.5，作为两路径协作线索；仅query_source field移除≥0.50为来源字段接力线索。删除direct-label能提升≥0.05accuracy或≥0.20nats且CI不跨0并独立复现，才考虑“有害复制”解释；否则撤回/收窄稀释假说。
- **混杂审计：** 控制输入/频率/位置/labels；全层全head，无gold选择；recipient末位/sender字段明确定义；联合边可有交互，比例不相加；real是受控来源规则非自然个人groundtruth；删除使激活分布变化，不等于自然模型简单减一项；native零消息与counterfactual替回不同因果量，不混合解释。
- **决策表（跑之前写）：**
  - query relay替回移除大量source效应，prefix-label＋relay近完整 → 支持source-conditioned计算经query内部再输出，但尚不证明新电路。
  - source field不是主要relay、label marker/其它组主导 → 更换“source token已完成绑定”的候选定位，不强保。
  - 删除direct-label提高条件化，关闭relay损害，确认复现 → late-copy稀释有具体因果线索，继续和Cho bypass/过滤比较。
  - 删除direct-label损害margin/accuracy，或仅同比缩小source效应 → 两路径主要协作，拒绝“后续复制破坏早期正确规则”的当前版本。
  - relay弱而whole-query冻结强 → 接力可能经last residual/self-loop或其它prefix位置；最后sender-group冻结仍不充分。
  - 数值控制失败 → 修harness/VOID，不解释机制。
- **算力预算：** ≤1GPU·时（独立单卡任务）；**实际：** 待填。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 待运行。

### primary有效后的有界复现（2026-10-10，跑前）
发现集source/input字段的直接sender作用小、Label marker relay作用大，native direct-label删除的margin/accuracy不一致。按原计划在Mistral-7B-v0.3同synthetic发现材料seed65001,n64复现，区分计算程序而不将Qwen位置结果外推。

### 完成结果（2026-10-10）
- 5个预定运行完成（4×Qwen discovery/confirmation＋Mistral同synthetic发现复现）；native重建相对RMS/self/all冻结误差**全0**。实际0.178单GPU进程墙时折算GPU·时（非利用率积分）；SSH默认agent认证曾阻塞，未启动实验，改显式RSA/IdentityAgent=none成功，未丢弃科学读数。
- **独立合成确认：** 原始sourceK效应2.419[2.108,2.753]nats；冻结query_source→末位余0.818[0.773,0.863]，Label marker→末位余0.226[0.172,0.285]，全部query relay余0.021[0.004,0.042]，direct＋relay余0.004[-0.005,0.014]。prefix-label→末位余0.483[0.451,0.516]。
- **独立真实评论确认：** sourceK效应0.524[0.399,0.665]nats；query_source余0.905[0.839,0.979]，marker余0.065[-0.016,0.138]，全部relay余-0.013[-0.040,0.012]。是E56受控来源规则，不是自然个体标注。
- **Mistral模型边界：** 同synthetic发现材料，query_source余0.051[0.033,0.068]，marker余0.947[0.930,0.963]，全部relay余0.001[-0.015,0.017]；prefix-label余0.118[0.073,0.159]。与Qwen的主要sender相反。并非所有模型都在Label标记先得到答案。
- **直接demo标签读取是否有害：** Qwen synthetic discovery删direct后的accuracy差-0.086（CI见JSON），margin +0.598；independent confirmation accuracy +0.035[0.004,0.070]、margin +1.240[0.971,1.512]；real confirmation accuracy -0.023[-0.052,0.007]、margin +0.188[0.080,0.298]。Mistral删direct同时损害accuracy -0.117[-0.160,-0.074]与margin -0.193[-0.246,-0.148]。**没有稳定accuracy修复，拒绝普遍“late-copy破坏正确绑定”。** 增强logit交互不等于答案正确率，需拆偏置/变异。
- 删全部query→末位relay使所有材料的sourceK效应近0，且损害native表现；两类边有交互，效应比不能相加。
- native准确率（确认）synthetic0.551、real0.553；single-source0.797/0.620，一句指令0.551/0.547。不把明显机制效应写成完整任务能力。
- **决策更新：** 支持query→答案relay；定位从source field候选改为Qwen marker／Mistral source field，保留模型边界。并非新token类型或新shortcut；文献Bai2401.11323v4、Li2509.04466v3已有template汇聚/瞬时任务状态。E66进一步拆尚未见input的source-selected task state与已见input的answer state。
- C16扩展L1，不升L2/L3；结果`results/e65/*/analysis.json`、`run.json`，原始逐条JSONL本地保留。

### POST-HOC读出分解（2026-10-10，主要分析完成后）
为理解margin↑/accuracy不稳，按平衡source×input对逐context logits作正交四项分解（常数、source主效应、input主效应、gold-aligned交互），真实评论另保留item残差。`scripts/analyze_e65_factorial.py`、`factorial_posthoc.json`。这是描述性分析；居中accuracy使用评测query均值，不是可部署校准或独立能力证据。
- Qwen synthetic确认，删direct的gold交互+1.240，但绝对常数偏置+2.754[2.231,3.275]、source主效应+0.566[0.392,0.750]、input主效应+1.233[0.825,1.679]。同input的source排序正确率反而-0.039[-0.070,-0.008]；不能仅靠平均交互增强宣称来源选择改善。
- real确认交互+0.188，source主效应+0.291、input主效应+0.577，item残差RMS+1.708；同input source排序无明确改善（+0.008[-0.036,0.052]）。
- 因此“只消除了标签干扰”不是完整解释；删除同时改变偏置、个体变异与关系强度。未把此事后分解升级为新主张或验证过的理论。
