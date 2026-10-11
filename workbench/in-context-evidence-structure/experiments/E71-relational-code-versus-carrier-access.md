# E71：答案前缀的收益需要来源关系，还是只需要一套扩展语法？（2026-10-10）

- **状态：** DONE
- **类型：** PILOT
- **对应：** I04/C17/C18/C19/P12；本次主张不升级。
- **为什么现在：** E67同时改变了来源码的结构位置与答案namespace；E70只在Alex/Sam码词上冻结迁移。最强近邻已提出非任务特定QK alignment，不能再把label-blind状态当新规则表示。必须拆开关系信息、载体可读性和特定词先验。
- **问题：** 相同答案语法、码词频率、来源和最终标签下，code与source的关系是否决定prefix收益？旧冻结frame对未见code词是否有效？common与centered合作是否能在新预定材料上确认？
- **设置：** Qwen3-8B，conda verl-clean，float32/eager，全36层/8 KV heads，单卡；不训练、不择层、不拟合偏移尺度。32contexts seed71001发现（animals/fruits、yes/no、source Alex/Sam、code Red/Blue）；有读数跨MIE再64contexts seed171001确认（occupations/vehicles、toxic/safe、source Alice/Bob、code Left/Right）。确认同时换多种材料，只能检验联合泛化；如失败，不自动归因为名字或码词中的某一个。
  - 16demo，source×kind每cell4条，规则相反，rule方向、顺序固定随机；所有query输入未在demo出现。
  - linked：code=source xor独立随机permutation。orthogonal：source×kind每cell分别2条code0/2条code1，随机分配；code与source/kind/final-label的经验互信息均0。两种上下文总code各8次、class各8次，所有其它token、位置完全相同。
  - D0Q0：Tag放code，Label前缀为Mark；D1Q1：Tag为Mark，Label前缀放code。每个relation内交换位置的token多重集、序列长度、label位置严格一致；relation之间token多重集、位置也相同。保持Source字段真实/充分，所以两个relation中oracle均能用source×input求final label。
  - 主要评测4个source×kind query，query code相同（linked的正常code）；没有提供gold class。追加4个仅翻code的query为预定**冲突诊断**：linked中Source与code冲突，没有唯一合理默认解读，不能将其计入能力准确率或失败率；orthogonal中两code都合法，额外query仅作稳健性读数。
  - 两种关系/布局均含“一句只看Source”的指令和single-source对照。teacher-forced prefix是外部给定，不等于native端到端prefix生成；尤其orthogonal前缀不能由source唯一推出，不作端到端优劣结论。
  - D1的native recipient保留label及其它缓存、全部V；仅patch demo prefix K：isolated / label-blind / own-common / centered / norm / negative-common / frozen-shared。isolated与label-blind masks完全沿E70，前者只见header及自身demo，后者非label禁止直接/间接读取任何实际label列；非label对flip labels逐位不变。
  - 旧shared偏移直接取E70 seed70001无query提取结果，hash固定bcec93a6282d781665716699083885caad6c636414beb65ec5da7b19f8b0f3d9。不得新code重提取frame、重调尺度或筛context后称迁移。
- **读数：** 主要自然query的correct margin、final-label accuracy、同input source排序；两个relation各自D1−D0及其relation×layout交互；各patch−isolated，若blind−isolated gap>0.2nats则报告转移比例。预定common×centered交互=blind−common−centered+isolated（同E70 POST-HOC，现在用fresh样本先写定）。source ranking与accuracy分开。
  - 冲突诊断：正常与翻code的gold-aligned margin差，仅表示哪个cue影响计算；不以默认答案正确性归因。全部query/per-layer prefix组mass、label组mass及source/code比例保存；attention相关性不升因果主张。
- **阳性对照：** full4D=no-op、prefix K self-patch=no-op、label-blind非label K/V对label flip差0、forbidden mass0；两relation的token counts与cell计数断言；common及frozen共享shift的fixed-native-Q组内相对logit spread≤0.02nats。prefix donor K全部V之外缓存bytewise保留。
- **噪声地板 + MIE：** no-op≤0.10nats，盲化feature/mass精确0。relation×layout若accuracy或source排序≥0.05且CI不跨0（或margin≥0.3nats且CI不跨0），则确认；shared恢复≥0.50blind−isolated且CI不跨0.25，同时accuracy/source排序≥0.05且CI不跨0，也触发确认。合作交互若source排序≥0.05且CI不跨0，则确认。正向/反向同报；ratio分母不足0.2不解释。context bootstrap4000，未做多重比较校正，L1。
- **混杂审计：** code relation的删除不是信息等价操纵（Source仍充分），旨在分离冗余关系与namespace，不推完全等价行为。码词可能有语义/角色先验；新词只能收窄词依赖，不证明普遍。query code冲突有解释歧义；hybrid cache存在非自然接口，common固定Q不变性不约束后续Q。native其它labels仍保留，不称frame包含整个算法。
- **决策表（跑之前写）：**
  - linked prefix收益明显、orthogonal无收益 → 收窄到关系码参与选择，单纯namespace解释不足；仍需实际路由因果证据，不能称新binding机制。
  - 两者prefix收益相近 → 来源码关系不是必要，优先格式/输出先验/通用carrier解释，不强保source绑定故事。
  - 新code全无prefix收益 → E67是有词/格式边界结果，公共可读性解释不自动普遍；不无条件扩模型。
  - frozen共享shift转移、centered单独弱而合作强 → group access与matching的协作有独立线索；恢复accuracy/来源排序必须分别报告。
  - own-common有效而frozen无效 → 当前frame含context/词身份特性，撤回新code通用frame候选；不得事后改frame后仍称同一次确认。
  - control失败 → VOID留存、同seed修复后重跑；所有negative保留。confirm落回噪声/MIE以下 → 不升级发现效果。
- **算力：** 本地GPU0先32contexts，预计单卡3–6分钟（包括模型加载），峰值<80GB；关键发现回来后才启动确认。fvcrc20留给独立问题，不盲目占满。记录进程墙时而非利用率积分。
- **产物：** scripts/e71_relational.py、scripts/analyze_e71.py；results/e71/*/{run,analysis}.json入git，contexts/behavior JSONL及layout留NFS。
- **定位：** Cho ICLR2025已有forerunner/shortcut与prediction bias；Few-Shot Examples Add Up §6/附录K已有alignment不需原任务identity；Wang anchor/QK已有。该卡只测试明确的relation×format预测与此前公共偏移的边界，不宣称这些概念首次发现。

## 发现记录（确认运行之前写）
- 32contexts全部控制通过：no-op/feature/mass/untouched=0，fixed-Q spread2.86e-6。
- linked D0→D1 accuracy0.734→0.914；orthogonal0.578→0.578。relation×layout accuracy+0.180[0.078,0.281]、margin+0.526[0.422,0.614]，满足预定确认MIE。
- frozen共享frame linked margin效应恢复0.720[0.570,0.871]，accuracy+0.125[0.063,0.188]、source排序+0.109[0.031,0.188]，满足预定确认MIE；orthogonal full gap0.045不足0.2，不解释ratio。
- 预定cooperation的source排序交互为0[-0.047,0.047]，未复现E70的事后线索；不能写成已确认合作理论。发现阶段原生linked排序饱和到1.00，CI不代表跨任务确定性。
- 按原卡启动64context seed171001（Alice/Bob、Left/Right、新词库、toxic/safe），不修改frame、读数或阈值。结果文件 results/e71/qwen3_discovery/analysis.json。

## 独立确认：哪些预测成立，哪些失败
- 64contexts全保留，no-op/feature/forbidden/未修改cache均0，fixed-Q spread2.86e-6。science wall time发现196.582s、确认388.433s。
- relation×layout accuracy0.109[0.070,0.152]、margin0.514[0.427,0.597]；source排序0.063[-0.039,0.164]不确定。linked D0→D1 accuracy0.520→0.645、排序0.898→0.938；orthogonal0.500→0.516、排序0.664→0.641。相同扩展语法不充分解释收益，关系码是有界的关键条件；不是新binding电路证明。
- **冻结frame泛化未过预设MIE：** 恢复35.0%[23.1,47.7]平均margin效应（低于50%），accuracy+3.1点[0.8,5.5]（低于5点），source排序−0.8点[-6.3,4.7]。不复现发现72%/12.5点规模；不能称跨名字/码词的通用frame。因确认同时换名字、码词、词库、标签，不能单独归因为哪个因素。
- own common恢复69.5%[55.0,85.8]margin、accuracy+6.3点[2.7,9.8]，但source排序+2.3点CI跨0；说明该context的共享成分仍有用，固定跨context方向并不自动替代它。
- 预定common×centered来源排序交互+0.086[0.023,0.156]；accuracy交互−0.016[-0.063,0.027]、margin+0.030[-0.088,0.137]。E70事后线索得到新材料有界支持，但发现集交互0、有排序饱和；只支持这个排序统计/接口的非加性，非完整普遍合作理论。
- linked D1正常−翻code margin+1.021[0.892,1.165]；为冲突cue诊断，不报为Source准确率。只有一句Source指令的raw恢复很小，不能推广到native chat/reasoning；E72独立压力测试处理该边界。
- 结果 results/e71/qwen3_confirmation/analysis.json；C17/C19仍L1，原E70的固定身份范围保留，通用frame候选收窄；不改ACTIVE状态。
