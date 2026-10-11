# E81：保持读取总量时，来源码内部的分配能否改变规则选择？（2026-10-10）

- **状态：** DONE（32-context pilot与64新context确认完成）
- **类型：** PILOT；本次只做一个机制问题，不追加函数/词典能力关卡。
- **对应：** I04/C16/C17/C19/P12/P13。研究对象是多规则ICL的证据选择；Tag/prefix只是区分解释的操作变量。
- **为什么现在：** 人审计要求正面对齐Cho、CoSToM、contextualize/aggregate及QK/V近邻。E59–E71已有实质证据，但不能将output source-ranking等同于内部选择。旧E71只存固定prefix位置（D0为Mark，不是Tag来源码）；POST-HOC初读显示公共偏移可能减少而非增加载体mass。要分开权重总量、组内分配与完整结果，不能再追52.7%涨到80%。
- **问题（一句话）：** 在相同多来源分类任务中，用另一布局的原生读取总量或组内权重替换来源码的读取，哪种改变能转移Tag/prefix收益；保持总量和输入类别分配时翻转来源权重，答案是否跟随？
- **设置：** Qwen3-8B固定revision b968826d9c46dd6066d109eabc6255188de91218，float32/eager，conda verl-clean，本地空GPU0。沿E71 linked关系、16demo/2Source/2kind、每cell4条，名字Alice/Bob、码Left/Right、标签toxic/safe、occupations/vehicles。新32contexts seed81001（非E71的发现/确认seed），仅4个无冲突自然query。Source字段始终充分，demo/query交换Tag与prefix的相同码，token多重集/长度/sites不变。全部contexts/错误donor保留，不以正确性筛选。
  - 两原生布局D0/D1；实际carrier G分别为Tag码token与答案prefix码token，按同一demo顺序对应，不比较D0的Mark与D1的码。
  - 收集原生每层/head/有效query位置的attention。分解为载体总量m、组内pi、组外条件分布r。全36层及**整个query所有有效位置**执行干预，不只末位。
  - 对每recipient做固定2×2：m取recipient/另一布局的原生值；pi取recipient/另一布局原生值。组外条件分布r按当前recipient活的Q/K计算，按(1−m)缩放；组内为m*pi。因m/pi都钳制到预先收集值，早层干预后它们仍在逐层可比；组外权重及V/MLP可随下游状态变化，不声称全网其它计算不变。
  - self=(own m,own pi)应重建native；mass=(donor m,own pi)；within=(own m,donor pi)；both=(donor m,donor pi)。不拟合尺度、不挑层/头、不用gold输出构造权重。
  - **source_flip：** m保持own。对每kind，固定该kind的pi总量及每个source×kind cell内部相对权重，仅交换两个Source的cell总量。用已知合成kind/source元数据定义反事实，不是可部署的方法。可以改变按来源的分配而不改变类别边缘，不假定天然就是“正确证据选择”。
  - **full_attention donor：** 整个query attention替换为另一布局原生矩阵，demo的码/Mark列按角色交换对齐（都在query以前，不改变因果可达性），query列按物理位置保留；recipient V/cache/残差保留。诊断carrier之外的读取路径是否重要，不以它未恢复作为experiment整体失败。
  - 两布局都测一句Source指令；不延展新的自由生成/推理能力结论。
- **读数：** correct logit margin、strict二候选accuracy、同Input的Source输出排序分别保存（后者非内部source selection）。actual carrier与label的m、requested-source份额、按query字段与层段的读数；四条件的对称Shapley m/pi贡献及交互；D1−D0在相同m/pi后的剩余差。source_flip−self的margin/accuracy/排序、组内Source份额变化；total mass和kind边缘不变误差。所有读数按context聚合，bootstrap4000 seed810，不选幸存种子/最佳层。
- **阳性对照：** CPU exact group分解/重建与kind-preserving来源交换；相同token/layout检查；native self重建；前4contexts两布局整段前向与prefix-cache query评分核对；全attention self恢复；逐干预m/pi目标、行和、masked mass、kind边缘误差。另一布局完整attention的效果不是预设正分，是诊断结果。
- **噪声地板 + MIE：** float32 self/full-forward margin误差≤.01nats、attention行和及m/pi/kind误差≤2e−5、masked probability≤1e−7。组内及cell条件分布用相应原生logits的softmax稳定计算，避免近零mass除法，不静默换uniform。主差值margin≥.15nats或accuracy/输出排序≥.05且CI不跨0，视为值得独立确认的pilot；不是整线资格门槛。原生layout gap不足.15时报告实际效应，不据此做不稳ratio或换seed追显著。
- **混杂审计：** 缓存/概率移植是非自然干预；不同角色的V内容、其上下文化和其它原生路径保留，所以共同m/pi后的差不能独归Value/readout。source_flip固定kind但cell内具体词不同；cell频率严格平衡、顺序/词/方向全保留，不说脱离任务的一般Source模块。活组外反馈可改变label读取，这是作用的下游而非被固定的量。全部head平均描述不直接证明因果位置；本实验因果范围限实际码carrier与全query，不代表所有多规则场景。只检验此具体解释，非重新论证弱模型永远失败。
- **决策表（跑之前写）：**
  - mass主要转移收益、within/source_flip弱 → carrier预算配置足以解释部分位置收益；不称修复绑定，不预设mass增加。
  - within或source_flip在固定mass下有清楚效应 → 组内来源分配有独立作用；联合m/pi与行为读数检验，不拿output排序替代选择证据。
  - both弱而full_attention明显 → 重要读取发生在该carrier之外；当前载体解释不足，回已有query路径，不开新任务。
  - 同m/pi后布局差仍在 → 当前分解不足，允许payload/历史/其它路径；不直接命名新Value机制。
  - 全部操作效应小/不确定 → 此接口没有决定性区分，保留有界结果，不铺十种变体追同故事。
  - 数值/映射控制失败 → 该运行VOID，修具体操作，同seed重跑，原失败留存；不升级科学主张。
- **算力预算：** 单卡≤.2GPU·时，必要的独立确认另≤.3；关键pilot回来前不并行下游分支。**实际：** 待填。
- **产物：** scripts/e81_carrier_allocation.py、analyze_e81.py；results/e81/*小run/control/analysis入git，raw JSONL/NFS本地；旧E70/E71注意力再分析单独标POST-HOC。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e81_carrier_allocation.py --model /tmp/ices_models/Qwen3-8B --out results/e81/qwen3_confirmation --n 64 --seed 181001`；pilot同命令改out为qwen3_discovery、n32、seed81001。
- **定位：** Cho shortcut/forerunner已解释提前计算，Bakalova与Wang2026已有上下文化/QK−V区分；单softmax的m/pi数学不新。潜在增量是自然的多规则Source条件下，具体读数与反事实可否支持可预测的证据选择解释。CoSToM是读出→有监督构造→对话验证，非原生电路完整逆向；不硬仿训练涨分。

## 结果（跑完后填写；不改上方读数）
E80没有科学运行；自动编号工具因历史文字中出现E80而分配E81，不将编号跳跃计成实验进展。

### 32-context pilot与确认前预测（2026-10-10）
新seed81001全部32contexts/18条件/4query完成，75.960s=.0211GPU·时。self max2.10e−5、整段/cache max1.66e−4nats，m误差3.58e−7、kind边缘2.38e−7、forbidden mass0。
Tag/prefix native accuracy .5234/.6250，差+.1016[.0469,.1563]；output source ranking .9688/.9531，绝非accuracy与选择同一指标。

- Tag接收prefix carrier的m/pi：both−native margin−.2177[−.3429,−.0917]，accuracy−1.6点CI跨0；mass-only亦损害margin。prefix接收Tag的m/pi更差，both margin−1.1073[−1.2941,−.9298]，accuracy−11.7[−17.2,−6.3]点。不能把码载体的两种概率统计当成可直接互换的完整程序。
- 角色对齐的whole-query full-attention donor到Tag：margin+.8618[.6820,1.0681]、accuracy+13.3[7.0,19.5]点；到prefix方向margin−.3001[−.4506,−.1566]、accuracy−6.3[−10.9,−1.6]点。V/cache/输入未换，支持更广的读取分布参与位置收益，但attention donor可能已经含答案相关选择，**不证明抽象来源算法已移植**。
- 在固定码carrier m与kind边缘下flip source pi：Tag margin−.3178[−.3996,−.2401]；prefix−.8961[−1.0863,−.7140]、accuracy−7.8[−14.1,−2.3]点。来源分配有指定接口的独立因果作用，不是从output排序间接推出来。

**下一次运行预定：** 同源码、同条件/词库/名字/标签，64新context seed181001，不重调偏移、不改层/指标。确认预测为：native prefix收益为正；码carrier both不能把收益转给Tag（margin方向不正）；whole-query角色对齐attention到Tag有正margin/accuracy效应；固定m/kind的Source flip在两布局有负margin，prefix准确率亦下降。全部context/error donor保留。确认只是新context级别复现，不声称新模型/新词表泛化。若未成立按事实收窄，不增加配置追同故事。

### POST-HOC输出读数解释（源于pilot，确认未读之前写）
对于同Input的A/B query，设z为safe−toxic分数，b=(z_A+z_B)/2，s=gold_sign_A*(z_A−z_B)/2。输出source ranking只检验s>0；两Source都答对需s>|b|。这个代数本身不新，也不等于内部选择机制。pilot Tag/Prefix的s均值.637/1.227、|b|均值2.189/1.963；Tag全attention移植s1.499、|b|2.196。因此accuracy与ranking分离可以来自已有正确方向的来源对比增强，而非两个独立模块是否修复。用独立标POST-HOC的脚本保存几何与exact accuracy重建；不改主读数/阈值，不把同公式重述当新贡献。没有看确认数据挑此签名。

### 64-context确认：carrier分配有作用，却不是位置收益的充分接口
seed181001全部64contexts/18条件/4query保留；140.785s，两个科学运行合计216.745s=.0602GPU·时。source hashes逐项一致；self max2.10e−5、整段/cache max2.86e−5nats，行和≤6.56e−7、m误差≤2.38e−7、kind≤2.98e−7、masked mass0。

| 条件 | accuracy | correct margin | output Source排序 |
|---|---|---|---|
| Tag native | .5234[.5078,.5430] | .5833[.5161,.6523] | .8750 |
| Prefix native | .6445[.6055,.6797] | 1.1094[.9507,1.2828] | .9219 |
| Tag + Prefix carrier m/pi | .5234[.5039,.5469] | .4532[.3807,.5279] | .6328 |
| Tag + Prefix whole-query attention | .6563[.6172,.6953] | 1.3714[1.1839,1.5774] | .9141 |
| Prefix固定m/kind、翻Source pi | .5313[.5078,.5586] | .2605[.2003,.3222] | .6406 |

native位置收益+12.1[8.2,16.0]点。Tag carrier both−native margin−.1301[−.2012,−.0590]、accuracy0[−2.3,2.3]点；没有转移收益。**Tag full-attention与carrier both按构造使用相同码载体m/pi，改变的是其它token的读取条件分布；前者比后者accuracy+13.3[9.4,17.2]点、margin+.9181[.7352,1.1107]。** V没有从donor移植；demo cache/V保留，但query内的V/残差随干预继续演化，不宣称全网Value完全固定。

固定m/kind翻Source分配：Tag margin−.3056[−.3644,−.2513]；Prefix−.8489[−1.0027,−.7122]、accuracy−11.3[−15.2,−7.8]点，符合确认前预测。Prefix码carrier全query source份额.600→.400，m仍.02101；操作的是概率分配，有直接因果效果，不由输出排序推内部选择。另一方面，Tag的native carrier总mass .02191与source份额.609都略高于Prefix的.02101/.600，预测却更弱；全头均值不是完整机制，不能用“码更显眼/更按Source读”概括收益。

POST-HOC几何确认：Tag native s=.5833、|b|=2.0196；full-attention s=1.3714、|b|=2.0927。|b|差+.0731[−.1011,.2550]，不作等效零结论；观察到的主要变化为Source contrast增强，而非平均共同bias下降。Source排序只记录contrast符号，不能将它与accuracy的分离当双模块已经成立。一般bias/读出认识已有Cho Hidden Calibration等近邻。

**实际更新：** 此格式中，码载体的Source分配有独立作用，而位置收益不能仅靠该carrier读取统计转移；更广的query读取程序能转移收益。C20新增L1，不升L2/完整原生算法；多层权重donor可能已携带答案相关选择，未证明抽象策略可迁移到新任务。当前不追加后续配置，先把此因果区别纳入现有query路径解释。

结果`results/e81/qwen3_{discovery,confirmation}/{analysis,run,preflight,output_geometry_posthoc}.json`，图`results/figs/e81_carrier_and_query.{png,pdf}`；raw本地。full-minus-both是跑前决策表的比较，分析器追加显式差值不改评分/原指标；POST-HOC输出几何独立标注。
