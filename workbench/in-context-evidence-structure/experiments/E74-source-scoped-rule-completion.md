# E74：标签全局出现，正确来源组合未出现——正向支持还是约束推断？（2026-10-10）

- **状态：** PLANNED
- **类型：** PILOT（新问题观测，不锁定机制）
- **对应：** I04/C09/C15/P12；测试positive output-support解释的边界。
- **为什么现在：** E71与预算压力测试不能自动把label-anchor路径变成新机制理论。Cho unseen-label区分copy与过滤，但语义任务仍可借预训练先验；此处随机source-specific映射令目标不是预训练已知分类，并令目标词全局出现，拆开word availability与source-specific evidence。
- **问题：** 当某来源从未用过query的正确标签，但给定函数约束唯一确定它，模型能否条件化推断？同一标签赋给该来源的其它类别，能否变成对该输出的反证？
- **设置：** Qwen3-8B，float32/eager，conda verl-clean，本地单卡。36contexts seed74001；四来源Alex/Sam/Chris/Dana，三category north/south/east，三label Red/Blue/Green。类别身份显式，不需从cat/fruits推断潜在类。每source有3×3置换，A/B每cell2份；C/D用4/2/3与2/4/3的互补重复数，随机混排。
  - full：四source三category全覆盖，30records。held：A/B同时缺同一个category，各留2个已知类别；C/D全覆盖，26records。A/B的缺失标签始终不同：每个目标词至少在另一来源真实record中出现，同类别在C/D也出现。
  - A/B缺失类别的两个目标标签由6个有序label pair均衡，ordered label pair×缺失类别完整交叉，每格重复2contexts；缺失类别轮换，observed类别的common-label位置随机，C/D的class→label独立随机置换。既无预训练固定映射，也不能靠全局最少label独立解决两个source query。目标input label组合未见，但source/class/label的单独身份都见过。
  - **scope swap：** 同步交换A/B两种目标label identity在各自函数中的分配，C/D不变。held实际改的是A/B各一个非query类别label；query目标由bijection补全而互换，两个source更新方向相反。所有global label/token频率、record位置、input/source完全相同。
  - **owned A/B修改：** 分别只交换A或B的两种target label；held改变的是一个已见非query cell，推断query target随之改变。通过分别交换C或D对应labels补偿计数，保持整个prompt token频率与位置完全相同，另一目标source的mapping保持。Full中用C/D联合交换保证同一不变性。
  - **foreign swap / cycle：** 仅C/D联合交换target pair或联合循环三labels。两种都保持全局词频、A/B函数不变，检验distractor频率代理或foreign copy。C/D重复数与label相关，因此该对照不可省略。
  - comp_a/comp_b单独保留C/D补偿变化、A/B不改，拆开补偿与owned编辑。它们有意允许global频率变化，source-difference另控制公共bias；不能与完整frequency-matched干预混称。
  - **函数空间：** 同一records，分别明确每个source的函数为bijection，或各类别label独立采样/可重复。后者的A/B未见category不可识别，oracle为uniform colour posterior、决策Unknown；不能以随机隐藏gold算错误。所有条件允许Red/Blue/Green/Unknown，Unknown仅表示不能由records+所述规则推出。
  - 输出两种raw提示：默认声明任务规则，以及加一句“Use only the records from the requested source and the stated mapping constraint.”。两者不是独立能力证据；本卡先测即时next-token程序，必要时之后另做native生成。全部12个source×category query，主读数为A/B的held category；其它10个seen query为正控。
- **读数：** 精确4-candidate logprob、candidate accuracy（tie按strict正确margin>0定义）、Known/Unknown概率、held与seen正控分开。source colour对比Ψ=[lp_A(targetA)−lp_A(targetB)]−[lp_B(targetA)−lp_B(targetB)]；**signed scope response**=Ψ_base−Ψ_scope-swap。正确constraint补全预测正号；固定、非负、source-matched label-support模型预测负号；source-blind/global频率预测不能在A/B间区分。该简化account不等于所有label-anchor理论。
  - family×coverage对source response/Unknown行为，owned−comp-only的source对比（隔离自己的改变），owned修改的edited/untouched-source响应及foreign-swap/cycle−base的A/B目标margin/accuracy；context bootstrap4000，不择seed/layer。ratio与不适用accuracy不包装成新规律。
- **阳性对照：** 枚举6个bijections及27个独立函数，按records过滤后验，full/held oracle逐query核对；global计数/位置与scope/foreign反事实断言；seen queries与full正控；重复native cache打分no-op≤0.10nats。SourceA/B目标label不同、目标token全局真实出现、querycategory在C/D有真实record断言。
- **噪声地板 + MIE：** no-op≤0.10；full/seen正确率≥0.80且至少一句Source指令有有效读数才解释缺失组合。held bijection accuracy≥0.70、signed response≥0.30nats且CI不跨0，或明显相反signed response≤−0.30且CI不跨0，才确认72新contexts seed174001（Alice/Bob/Casey/Eli，oak/elm/pine，one/two/three）。缺失类别/ordered label pair全预定平衡。不因结果差换标签后算原确认。
- **混杂审计：** full/held长度与类别覆盖不同，不能把performance差单独定位source-binding；main scope swap在held内词频/位置完全匹配。family指令改变任务假设，是需要研究的变量，非唯一规范先验；不声称一般不理性。Unknown在instruction出现，可能有指令bias，用full事实正控检测。默认raw/强回复模型差异仍待native确认；全局label可读不证明缺失组合被推断。
- **决策表（跑之前写）：**
  - 正scope response、held准确、foreign不影响 → positive support不足以描述此程序；进入约束信息内容与source gate的因果拆解，仍可能是已知排除/信息过滤机制。
  - 负scope response、full/seen良好 → 默认近即时支持检索；不能说模型无constraint能力，先查native/明确程序。
  - family不改变输出、Unknown在full也泛滥 → task/接口没有被可靠理解，不做计算机制结论。
  - foreign严重影响、scope无效 → global/foreign规则替代解释优先，不宣称source-local completion。
  - controls差 → 改观测或接口，不扫更多模型强保；全部negative保留。
- **算力：** 本地GPU0（E72-8B已结束），模型NVMe复用；不与同卡队列相撞，预计3–8分钟。只先36contexts，关键读数回来才做确认/机制；余卡留给已运行问题。
- **产物：** scripts/e74_completion.py、scripts/analyze_e74.py；小run/analysis/oracle audit入git，contexts/behavior JSONL留NFS。
- **定位：** Cho ICLR2026 unseen-label/denoising已占“不能仅copy”的反例；Incomplete ICL已利用负类别证据，ICL Ciphers已用bijection与不可识别对照，broader-spectrum ICL已有排除想法。潜在增量只是source-scoped、全局词可用但联合支持缺失的matched signed-response与机制选择，不能称首次发现约束/排除/任务学习。文字与新词组都不是novelty依据。


## 跑前设计校正
在token/model科学打分之前，审计发现24contexts无法让6个ordered target pairs与3个缺失category完全交叉。改36发现（每格2次）/72确认（每格4次），避免category或source-name能够部分预测target。没有读取本实验科学结果；MIE、其它因素与seed保持。


## 跑前替代解释审计：同步修改不足以定位来源
A的未见label等于B的独有已见label，反之亦然。因此positive synchronized response也可能来自跨源复制，不足以说source-local completion。加owned单源修改与C/D计数补偿；再用foreign-only swap/cycle打破C/D high-frequency标签代理。C/D合计每个label各6次，所以base中A/B两个target同频，任何修改也保留全局计数。四种来源都须遵守同一函数空间，没有用违反bijection的假数据当对照。本校正在模型打分前写入，未查看本实验结果。


单源owned修改使A/B可以具有相同缺失label，不能继续强制两个target不同；其target仍在C/D实际记录中出现。C/D字面类别映射独立随机，但重复数按target pair设计，因此foreign-only swap/cycle和compensation-only必须报告，避免把C/D频率代理当source-local规则推断。Source-local解释须经过owned specificity；同步sign单独不够。

## 分析前符号校正
模型发现运行期间、尚未读取任何科学打分或运行分析器时，代数复核发现分析代码误给owned_b−comp_b加了负号。由于Ψ=LD_A−LD_B，A由targetA换为targetB会降低LD_A，B由targetB换为targetA会提高LD_B，两者都降低Ψ。因此两条owner响应均为Ψ_comp−Ψ_owned，无额外符号。只校正分析器实现，运行中的打分脚本未改；edited-source单独LD的方向仍A正、B负。原卡的来源条件化方向与判断门槛未变。
同阶段将分析器调用从导入函数的默认2000重采样显式改为本卡规定的4000次（bootstrap seed740）；没有读取科学结果。
