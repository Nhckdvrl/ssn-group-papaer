# E166：增益匹配能否解释跨历史性质迁移与伙伴作用（2026-10-29）

- **状态：** DONE；两谱系18格×440题、独立复算、来源终态及恢复监督exit0全部完成。
- **类型 / 对应：** CLAIM；C14/P33。用户持续授权高信息量研究，总并发最多4卡。
- **重要问题：** E164/E165的专家函数包带走低预算概率质量、且未改共享函数的作用改变，是否主要由简单的逐层输出增益校准实现，而不是需要函数响应中的其余结构？

## 设计选择与主线价值

E165给出新反向结果：native P16损伤+.105，专家单独移入共同P反而改善.223 NLL（固定实际P路由），D来源干预可抵消其改善。旧E163 native几何POST-HOC亦见早层R/S幅度显著重新分配，但没有位置或同输入函数证据，不能直接命名outlier机制。全文Super Experts、Massive Activations、ME Layer有真实全局条件信号/预测干预；一般outlier重要性不是本研究新点。

原未运行的“按header/body删除S”骨架只能定位依赖发生在哪段输入，不能区分函数方向变化与简单R增益的统一解释。本卡在任何新读数前替换为跨两个谱系的闭式增益对照，并把S-zero扩到原P32运行条件，直接检验性质与伙伴依赖之间的因果联系。不拟合新adapter、不扫增益或mask；这是可能改变整篇解释的竞争模型，不是挽救OLMoE P16性能。

## 固定资产、输入和校准

- EMO：沿E164的共同D_P/G_P/S_P，R来源P/B。OLMoE：沿E165的共同D_P/G_P，专家来源P/A；无S不制造伪共享组。权重/pin/原生dtype与算术严格继承原记录。
- 两谱系复用同55学科440题及各8条validation cal，token各沿原E164/E165输入和原P选择器（EMO31R+S；OLMoE16/64）。模型间只比较本谱系对比，不跨tokenizer相减NLL。所有题/学科保留。
- **只在native P full实际cal轨迹上**，对每层同一个输入h、同G_P路由，原生程序计算父专家输出r_P与donor输出r_D。EMO仅取routed部分，S_P不并入；OLMoE取全部MoE输出。
- 一层一个、对所有专家/任务/政策相同的正增益：a_l=sqrt(sum_cal ||r_D||² / sum_cal ||r_P||²)。BF16向量先转FP32作乘积，再FP64归约。存完整能量/点积/计数与16个系数，不依赖held预测；不拟合标签损失。沿既有cal文本（含固定dev5及原正确续接），不声称输入完全不含标签。
- GainP在每个routed expert输出后施加同层a_l（FP32乘法后回原BF16），后续gate乘积/求和按原生程序；不改参数。EMO共享输出不缩放。这是16标量、input-independent的透明竞争模型，不是已排除所有可能gain或输入条件映射的oracle。

## 预定条件：固定实际路由，比较完整性质与合作

每题/每policy先用原生P、S完整时捕获mask前实际gate logits；所有条件回放相同轨迹，固定支持与门值，原mask在其后施加。其余输入/响应仍内生，效应不是孤立expert直接效应或唯一中介比例。

- EMO：R模式P/B/GainP ×full/P32 ×S完整/全零，共12格。
- OLMoE：E模式P/A/GainP ×full/P16，共6格。
- 旧E164/E165对应P/donor完整条件、EMO全S-zero full逐题精确guard；新EMO P32 S-zero对原始零化helper另作真实身份。Gain=1在真实原生端点逐位重现，Gain=0对原routed-zero helper；校准observer必须逐位保留native P前向。来源参数/buffer/hooks终态只读。

读数为真实答案token NLL、choice CE、raw/per-char准确率；首答案完整词表KL单列，继承FP32乘积后FP64求和。每谱系完整矩阵、full→mask损伤、GainP−P、donor−P、GainP−donor全报。EMO同时报各R下两policy的S移除效应、源R×S交互与GainP对该角色变化的逼近；不再从不同运行条件的共存直接推断因果支撑。

同55学科配对簇bootstrap2000，seed166002；两个谱系共用draw但不合成跨模型NLL分数。区间条件于固定模型/cal/输入，不是训练seed总体。增益误差与cal余弦仅说明函数近似，不替代预测检验。

## 阳性对照、噪声地板 + MIE、决策表

CPU原生FP32/BF16已知比例函数必须恢复已知增益；全1/全0增益对应真实identity/原zero，S保持未缩放；真实mask/route顺序、候选重排/多token/因果前缀和源只读都先通过。统计由独立系数向量/归约程序复算。精确旧guard失败先修实现并记费用，不放宽。

NLL .1 nat/准确率5pp沿既有解释量级，仅是参考而非自动科学判决。CI含0不当等价证明；比较GainP与donor的直接配对区间、残余量和完整质量，不能只挑一个改善格。

| 观察 | 解释改变 |
|---|---|
| GainP逼近donor预算收益及EMO S角色变化，直接差的CI较窄 | 支持简单增益为这组表型的建设性解释；不再把迁移签名本身当新的独立语义函数 |
| 校准能量匹配而held预测/角色仍显著不同 | 削弱这项预锁的逐层统一gain解释，支持其余函数响应结构；不宣称所有标量/对齐都失败 |
| OLMoE能由gain解释，EMO不能，或反之 | 相似操作签名可以由不同计算实现；论文需写清形成/使用条件，不硬凑统一机制 |
| R_B P32优势在移除S后明显减弱/反转 | 同运行条件直接支持S参与性质实现；仍不叫shared独立容量或唯一中介比例 |
| R_B优势在S-zero仍保留 | 性质与较强S依赖可共存，但前者不要求该在线shared通道；保留原正结果并拆开因果叙事 |
| 接口/数值失败 | 无科学结论，留失败/费用并修程序；不换模型、样本或增益规则 |

## 资源与停点

全部成熟权重/输入已在耐久缓存，0新权重训练，32个闭式cal系数（每谱系16），无梯度优化。两谱系顺序单卡运行，先CPU装载/指纹、需要时节点NVMe并核SHA；不占卡等I/O。预计合计1–2 GPU时，cap4含预检/失败，总并发≤4。耐久监督/心跳/退出码/完整成本；原source、数据、mask、统计与代码在新条件前冻结。E165及本项完成后先整合主张、论文和复现，不自动E167或gain/位置扫描。

## 冻结与执行

数值源码ef8f58c8，27个文件SHA，plan `ae9d5cc6983f8d2dcc9575f893ca011200cbe90990d414fd1627c3f3f60102fc`；[plan](../results/e166/plan.json)绑定E164/E165原始输入、mask、完整旧分数和来源指纹。FP32/BF16两原生族的已知2P、unit/zero增益、observer identity、来源只读均通过；独立统计fixture合计16356数值/16938元数据，最大差8.88e−16。[CPU凭证](../results/e166/CPU_tests.json)，装载前默认GPU编号冲突及修复另记CPU失败文件，不含科学结果。

fvcrc21物理1，外层监督PID2100137，先OLMoE再EMO；4GPU时累计cap含失败。GPU0已有他人作业，未使用。CPU准备和占用等待不占卡；实际参数/缓冲核对后才取得GPU。完成由两个worker exit0、完整矩阵、来源终态与独立复算共同确认。

### 装载恢复（条件和数值27文件不变）

OLMoE6格×440题完成并exit0，原生旧LL/KL及终态只读通过，GPU计时1056.54秒。随后EMO在canonical NFS的FP32→BF16按页读中阻塞，10:46:05 UTC确认PID2126323/PGID、无EMO GPU ledger/校准/预测后定向SIGTERM；原worker -15、原chain1完整保留，不追认为成功。该CPU尝试监督648.2秒，GPU0秒。

`e166_stage_emo.py`对既有两份公开FP32源做节点NVMe实文件复制及全文件SHA；256MiB有界顺读probe为3.083秒，最多2个复制worker。`e166_emo_local.py`仅改`e156_loading._classes`返回的checkpoint目录，原生类、from_pretrained kwargs、CPU转换、参数/buffer指纹和旧预测精确guard不变。`e166_resume.py`只恢复未得到新读数的EMO并保留完整OLMoE，完成后调用冻结分析/校验。三份适配源码和新监督单列SHA；失败和CPU成本进入封存，不重跑已完成OLMoE。

## 结果与解释（全部已取得）

| 预定读数 | 估计 [95%配对55学科簇CI] |
|---|---|
| EMO P32：真实donor−P / GainP−P | −.293673 [−.384908,−.204286] / +.394301 [.237482,.594057] |
| EMO P32：GainP−donor直接差 | +.687974 [.520068,.897586] |
| EMO full：S角色变化donor−P / GainP−P | +.289102 [.210344,.370695] / +.862787 [.759625,.969648] |
| EMO P32 S-zero：donor−P | −.355742 [−.553136,−.147963] |
| EMO P32的S角色变化donor−P | −.062069 [−.256914,.134638]；不作角色等价/符号反转结论 |
| EMO full：donor−P / GainP−P完整NLL | +.211679 [.148799,.270843] / +.153257 [.117038,.190261] |
| OLMoE P16：donor−P / GainP−P | −.223023 [−.308090,−.139628] / −.275951 [−.314664,−.240695] |
| OLMoE P16：GainP−donor直接差 | −.052928 [−.132099,.026407]；不当等价检验 |
| OLMoE gain full：NLL变化 / 首答案KL | +.004246 [.000569,.007447] / .003706 |

EMO P32 choice CE donor−P=−.725434 [−1.024036,−.419082]，GainP−P=+.918719 [.519563,1.356419]；S-zero donor的CE区间跨0，NLL优势保留。OLMoE P16 GainP的CE改善.696603 [.467075,.915067]，donor改善.487595 [.068763,.920151]。所有raw/per-char准确率、输出KL及逐学科数据在完整summary；未将NLL改善称准确率提升。

**科学推进：** 统一RMS增益能在OLMoE产生预算性质，却在EMO增强full共享依赖、同时让P32变差；这将伙伴重要性与选择性质分开干预。真实R_B的P32 NLL优势在固定P路由、关闭在线S输出后仍保留，共享本身仍有明显预测作用。这排开“预算优势只是shared在线补位”解释，并支持函数来源、响应接口与合作使用是需要分别识别的组织变量。不扫描更好的gain来挽救该竞争模型。

cal同输入响应：OLMoE gain=.9303–.9997、cos=.9774–.9997；EMO gain=.2048–.9618、cos=.6882–.9698，均为预定规则的观测，未据held调整。POST-HOC完整学科描述：OLMoE gain/donor改善54/45科NLL；这是描述计数，无额外CI或训练seed结论。

## 完成与复算

总GPU工作计时3866.130493秒=1.073925137 GPU时；OLMoE1056.54秒，EMO余量，最多1卡，峰值31.920098/55.024348GB。原CPU-only中断648.2秒、stage636.891秒/0GPU、新CPU准备121.235秒分列。原链失败保持原事实；有效完成入口为[execution_complete](../results/e166/execution_complete.json)中列出的OLMoE及EMO恢复worker和恢复chain，均exit0。

[EMO完整summary](../results/e166/emo_summary.json)、[OLMoE完整summary](../results/e166/olmoe_summary.json)、[独立审计](../results/e166/independent_audit.json)、[主图](../paper/figures/05_gain_and_partner_interventions.png)。16356数值/16938元数据独立复算最大差1.0658e−14。raw在`~/mechpop_cache/e166_gain_transport/{emo,olmoe}/scores.npz`，198730/121042 B，SHA分别e50c24cd…da86a1 /66b1d82f…78477a。manifest逐项绑定完整SHA；source ef8f58c8 /plan ae9d5cc6…102fc、27数值文件未变。CPU统一入口`reproduce.py E166 all`已完整通过，0模型前向。

C14维持L2。该批后集中形成论文、复现和封存；自动GPU队列为空，无E167。
