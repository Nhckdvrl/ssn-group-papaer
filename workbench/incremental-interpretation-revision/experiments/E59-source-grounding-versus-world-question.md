# E59：源断言与世界补全是否在问答中混合？（2026-10-06）

- **状态：** DONE（完整三族评分、最终资格、全部分层与W3类别均衡已完成）
- **类型：** MEASUREMENT + CLAIM；§3 E59问题形式菜单。
- **对应：** I02 / C06–C09 / P13；先前误读由晚到语法证据排除时，回答是否按source断言还是可能的世界补全来判断？
- **问题（一句话）：** 明确“No=未被句子断言”，或者提供Not determined，是否会改变原GP问答差距及完整重读的收益？
- **来源与设计时点：** Amouyal与HANS已注明non-entailment约定；E52原题约定的interim显示部分control低、R1没有清楚的GP特异恢复。该interim的Gemma/Llama native有已修正重复BOS，不据其效果选择材料/模型；本卡区分scope账户，待D0完整后运行，三族仍沿用跑前固定8/12/8确认面板。
- **设置：** 只用E52全部needs_revision且YN的原句/原问句，不改字符；D0两遍或第三遍已裁T1，配对两侧两遍T3acceptable且无第三遍降级。保留所有不合格/不成对/分歧的缺失原因，不按错误题筛。三种任务O2原native Yes/No（原gold）、G2显式源断言“Yes iff entailed; No if unasserted or contradicted”、W3显式世界约束“Yes iff entailed; No iff contradicted; Not determined iff neither”。G2/W3 gold从已完成Step5 T1枚举按任务定义机械映射，原gold永不覆盖，不虚构新人工标注。WH不硬变为YN，留E53与后续角色问句。
- **模型与版本：** Qwen3-8B、Gemma3-12B-it、Llama3.1-8B-Instruct，固定E52同字节，FP32/SDPA、native模板一次special tokens、greedy候选联合LP。O2/G2两选项两顺序，W3三选项全部6顺序；R0/R1/R5各测两侧。O2可按完整prompt/input token/hash机械复用纠正E52 FP32同任务，不选更好run。G2/W3不改S/Q、仅明确回答规则与选项空间。
- **读数：** 主要O2→G2的GP/control各自收益、gap缩小、与R1/R5交互；主对比限定O2/G2 gold相同的配对，gold不同单列。W3按T1类别分开、类别均衡描述，不能用大比例NEITHER或不同chance底线冒充普遍能力恢复。GP/control需同问句、同T1类别及资格，CI用E52连接的lexical cluster10000次bootstrap。全部构式/模型/阅读/scope切片保留，空类别不填0。
- **阳性对照：** 原simple/final问题中T1 ENTAILED的Yes，CONTRADICTED的No（数量可能少、如实报告），NEITHER的Not determined；三类别正确率分别报。选项顺序稳定性、输入无重复BOS；只有No/unknown默认策略不算恢复。
- **噪声地板 + MIE：** 同三族FP32仪器与全部mapping波动；≥5pp选择性改变且CI分开作为追问heuristic，不自动科学判断。选项概率是任务条件概率，不称world belief。
- **混杂审计：** scope清晰度与新指令长度混杂不能单独当编码机制；G2作为R8的一句源约束恢复控制，generic修订指令仍由E52报告。W3多一个答案，故不直接比较其绝对概率/accuracy与O2；Step两call一致率不是语义真理。任务scope差是测量诊断，机制结论需后续干预。与E53逐题关系POST-HOC标明。
- **决策表（跑之前写）：** G2消除差且positive稳定→E3增加，检验E53真实角色表达；G2仍有差且R1特异改善→E54/E55；W3正确判NEITHER但O2/复述加旧角色→区分回答规则和角色生成用途，继续因果定位；所有任务control仍低→该模型只描述，检查读出协议、不从地板推能力；异质→保留四账户、不挑一模型局部链。
- **算力预算：** 三族各单卡，预计1–3 GPU·h（实际n待D0合格数据）；共享八个GPU锁，不结束既有服务。资产外置`/data1/xiangding/work/incremental-interpretation-revision/E59/`。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（2026-10-07，完整资格1014QA/507同题pairs）：明确G2源支持、words、initial NEITHER同gold的MVRR，Qwen/Gemma/Llama的GP−cue损失分别63.79pp [49.14,77.61] / 58.62 [43.10,74.14] / 37.07 [18.97,54.31]，各29连接lexical clusters。cue正确率86.21% / 91.38% / 81.90%，源理解缺陷没有被源规则澄清消掉。
- G2 R1的GP绝对收益分别−4.31pp [−13.79,6.03] / −4.31 [−11.21,1.72] / −13.79 [−24.14,−5.17]；cue+5.17 [0,13.79] / +3.45 [0,10.34] / +6.90 [.86,15.52]。不能把更大的gap只归为GP受损，也没有稳定选择性修复。letters、probability、ALL/final、R5和全部构式仍完整报告；NPS及部分NPZ/NPVP cue偏弱，不能由地板归因能力。
- 结果文件：`results/E59-source-scope-summary.json`；完整external `E59/source-scope-final-v1.json`、cluster-effects及`source-scope-class-balanced-v1.json`。W3各类/缺失/共享重采样保留，不与二选项绝对分数比较。C仅8QA且主要不是初始题，不能做宽范围世界矛盾能力判断。
- 按决策表执行：源规则并未消除全部差距，转向已预注册E54问句前干预。E54协议写于阅读E59效果之前，固定三族/全部读出，不据本表择胜模型或材料。P13原“约一半错误不是GP效应”撤回；原审计及结果不删除。
- 主张变化：C06–C09仍L0。
- POST-HOC：设计依据包含原题约定的interim诊断，不作为E52真实错误的最终结论；未更改E52预定读数。
- 生成器因菜单文字引用返回E64，跑前采用尚未占用的菜单编号E59。
- 算力：资格投影是CPU确定性处理，0新增GPU时；原blind超集63120任务/族、最终60840/族，原GPU时由各qualified config的blind_score_source引用，不把资格投影0写成总成本。Gemma等待资格进程曾143结束，原评分完整，未重复推理。

### 读出控制补充（运行前；由E52纠正输入后的字母偏置触发）
Llama8纠正native的R0仍2947/3464选择A（两mapping已保留），不能把接近50%的准确率直接推为理解能力。三族独立prefix-only forward（不输入任何候选答案）与候选序列评分对照，LP最大差<9e−5；2D/4D纯因果mask一致，未见候选未来泄漏或索引错误。这是读数/能力的限制，不能把符号偏置本身当本线finding。
E59跑前追加相同三scope×R0/R1/R5的letters与words两种响应；显示选项与顺序一样，只把答复指令从A/B(/C)改为Yes/No(/Unknown)。W3把Not determined标为Unknown并明确定义；三族各候选均为单token（在完整prefix中验证），避免多词长度偏置。所有组合保留（每YN句60任务），不据结果挑读出；原Q/S仍不改，gold仍机械来自已完成Step5。主O2→G2对比按两readout分别报，W3不直接对比绝对概率。借用已有MCQA symbol-bias工作的诊断控制，完整叙事需由修订内容与因果后果决定。

### 推理与语义资格解耦（新条件推理前登记）
原D0-v4已完成但literal反例复核仍进行；E52 R2/原句surprisal全14模型与三族FP32 R2已完成，空出GPU。先按原v4独立T3与精确S/Q配对形成输入超集，不以暂定T1类别筛；G2/W3 gold一律PENDING/None，不能提前分析。三族固定FP32、全部scope/readout/reading/option-order的候选LP原样保存，O2原gold保留。完整qualified-v3完成后，以本卡原定T1/T3/同类配对规则投影全部合格任务、确定性赋gold；若任一合格任务缺失则拒绝分析，不挑成功题或更好模型。旧资格及超集输出全留。该解耦只减少等待，不改变主读数、资格或假说决策表。
所有候选在完整prefix里都是单token，使用不含任何答案的prefix-only forward计算相同的候选联合LP。每模型首个固定输入×三scope×两readout共6任务，与独立完整候选序列LP数值核对，最大差<1e−3才继续；guard失败保留并修复，不能当能力差。保存检验、token/prompt/hash、原始gold-free scores，资格投影不产生新GPU时。
