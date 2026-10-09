# CLAIMS — In-Context Evidence Structure

**2026-10-06 整理（agent）。** 主旨（I04）：In-context learners index evidence by output — they track drift that changes which outputs are used, not drift that reassigns outputs to inputs.

**等级说明：** 按 `workbench/EXECUTION.md` §3。升 L3 需独立校对（§5），本线尚未做——因此凡已满足 L3 泛化条件（≥2 个模型家族且 ≥2 个任务）的主张，标为 **L2** 并在“待补”中注明。

| ID | 主张（含适用范围） | 等级 | 证据（实验卡 / 结果文件） | 待补 / 升级条件 |
|---|---|---|---|---|
| C00 | 程序化 nonce 规则任务支持真实 in-context 任务学习（未饱和、换字典稳定） | L1 | E00；`results/e00_debug` | 用审计后的词库（`data/lexicon.json`）重跑确认版 |
| C01 | 测量工具有效：exact 层级 Bayes oracle（λ×ε，28 个单测；K 类置换版另有穷举单测）+ 成簇 / 前缀噪声方向 / A→B vs B→A 检验；阳性对照（标签流）13/13 模型测到规范方向 | L2 | E01、E05、E06、E16；`scripts/ices/oracle.py`、`oracle_perm.py` | 泛化条件已满足，待独立校对后升 L3 |
| C02 | **条件结构被可交换汇总**：类别→标签映射的变化（nonce 规则、SST、奇偶、大小、类别条件变换、K=4/6 置换、任务切换）下，成簇≈零散、前缀噪声方向与 oracle 相反、A→B≈B→A；指令、可见 CoT、thinking（2 万 token）、T=64、时间戳都不改变；13 模型 0.6B–32B、4 个家族 | L2 | E02a、E03、E07、E08、E09、E16、E23、E25、E27；`results/confirm_v1`、`results/night_core` | 泛化条件已满足，待独立校对后升 L3 |
| C03 | **输出侧变化被规范追踪**：标签流（含无关输入/独特 id/自然词）13/13 模型方向规范；全局变换（大小写↔反转、±1/±3/±10）多数模型规范、随规模增强（32B）；词汇/字符串函数多数只有近因 | L2 | E05、E06、E11、E16、E19、E20；`results/conf_rel` | 泛化条件已满足（标签流），待独立校对 |
| C04 | 隐式先验：标签流 λ≈0.02–0.05、ε≈0.05–0.1；分类 λ=0、ε=0.3 | L1 | E10b（Qwen3-8B） | 多模型拟合 |
| C05 | 看最近邻、不看最近期：预测跟随 query 像哪一半 demo，与新旧无关（两种顺序对称，到 32B） | L2 | E04、E21；`results/local_nat` | 待独立校对 |
| C06 | 为什么（训练统计）：任务同质的从零训练复现解离；易变分类数据（toy、LoRA）只带来近因，不产生条件层面的变化推断 | L1 | E12（toy v1–v3）、E18（2 种子 + 4× 剂量） | 更大训练预算；预训练语料统计 |
| C07 | **同一答案内的解离**：新 regime 用大写标在输出上时，格式通道规范（16/16 模型×任务），映射通道平坦或弱近因（8B）；32B 开始按大写分组（SST）；删除影响：格式通道旧 demo 支持度为负 8/8 且与输入内容无关，映射通道为正 16/16 且同类主导 | L2 | E22、E26；`results/marked`、`results/reset` | 待独立校对 |
| C08 | **时间结构只在“偏向新输出”的成分上**：不均衡翻转时，条件成分噪声方向错 12/12（6 模型、到 32B）；少数类 query 被拉向错误答案；关系型输出（±2）同样成立 | L2 | E28、E29；`results/imbal`、`results/imbal_ca` | 偏置成分的“规范性”在弱信号下部分来自注意力竞争（E37），措辞需与此一致 |
| C09 | **证据按输出身份分开**：分隔阶梯——不同输出词 0.00（10/10）≪ 输入领域 0.36–0.49 < 显式上下文标签 0.51–0.91 < 时间（完全合并）；上下文交互的溢出 > 主效应溢出（14/14，7 模型） | L2 | E24、E30、E31、E34、E35；`results/ctxeffect`、`results/vocabsep`、`results/domain` | 待独立校对 |
| C10 | **泄漏 ∝ 标签语义相似度**：14 套标签词，溢出比与 bge / 模型内部锚点相似度 ρ=0.75–0.96（5 模型 × 2 任务） | L2 | E33；`results/vocabgrad/summary.csv` | 待独立校对 |
| C11 | **建设性修复**：新 regime 换成新输出词后，concept drift 被规范追踪（映射通道噪声方向 11/12，含 1.7B/2B） | L2 | E32；`results/relabel` | 待独立校对 |
| C12 | **机制**：一族晚层读标签头按内容相似度（强）、上下文标签（弱）、不按位置读取 demo 标签锚点（逐头 DLA 重建 r=0.9997）；旧锚点因因果掩码不可改写，新锚点不携带变化信号；方向错误的噪声效应 = 晚层直接读取噪声锚点（因果修补，阳性对照精确） | L2 | E36、E37、E38；`results/mech/`（不进 git） | L4 需：读标签头消融按预测改变映射与泄漏；非 Qwen 模型复现 |

**混杂审计（C02 等升 L2 时完成）：** 1 噪声地板：bf16 batch 噪声 ~0.1 nats/条、无方向，200–300 base 平均后 ≈0.007 — 已控制。2 工具有效性：标签流阳性对照 13/13 — 已控制。3 选窗：配对设计，所有条件共享输入/名字/query — 无关。4 自校准：同一读数（exact 序列 log-odds），跨任务用归一化指数（CSIn/NDIn）— 已控制。5 提示词默认值：E03（指令）、E09（CoT/thinking）— 已控制（不能恢复）。6 输入一致性：同一 tokenizer/同一 prompt 字节 — 已控制。7 幸存种子：全部 base 报告 — 已控制。8 算力匹配：不适用。9 数据重叠：pilot 与确认版种子分离（≥500000）— 已控制。10 事后切片：多次修正如实记录（见下）；确认版与 E24 之后的实验预测均跑前写定 — 已控制。11 饱和：分类 accA 0.79–0.99；标签流 |logit| 大，用归一化指数 — 已注明。12 系统特有：13 模型 4 族 — 已控制。机制实验另有健全性检查（旧锚点逐位相同）与阳性对照（全位置修补精确复原）。

**作废 / 修正记录**
- 2026-10-10：E70首轮bf16 common key写回的fixed-Q组内logit spread max0.06986>预定0.02，32-context运行VOID，原始JSONL与control_failure.json保留；未读取科学条件结果。改float32同seed重跑，阈值不变；both直接取blind donor以精确实现数学同一性，不能把数值误差解释为地址变化。
- 2026-10-10：E66首轮bf16分段cache实验完成24contexts，但与整段native max差1.625nats>预定0.10；标VOID，保留`results/e66/qwen3_discovery_invalid_chunking_bf16/`。仅检查控制、不使用其它条件解释机制；同seed改float32复核，阈值保持。
- 2026-10-10：E63首轮SDPA消息分解的最大相对重建RMS=0.0723，超过跑前0.02阈值，synthetic/real两次运行标VOID（保留`results/e63/*_invalid_reconstruction/`）。no-op与all-attention冻结误差0不能替代组件数值校验。改为原生eager attention weights/V重跑同一种子，不使用首轮结果解释机制。
- 2026-10-10：E59首个real发现运行将E56的toxic=1误作label_index=1(safe)，demo/query同步反向而与E56预定极性不一致；完整汇总前停止，保留`results/e59/qwen3_real_discovery_polarity_mismatch/`，不纳入证据。同seed59002按1−toxic重跑，synthetic不受影响。
- 2026-10-10：E55的“同一标签”回归项实际是该demo的二元label identity，非与query的正确输出相同；系数0.92不能解释为gold-label匹配程度。其prototype probe在CV前全数据标准化；E58/E59改为固定训练集预处理。暂保留原数值与L1范围，不把probe可读出当作天然部署/原因定位。
- 2026-10-10：E56c跨数据集同时更换词表，只证明给定模块的迁移有限；撤回“证明不存在通用来源方向”及“只因词表”的确定措辞。E58/E59检出可跨标签迁移的来源差分，仍不等于全部来源表示可因子化。
- 2026-10-10：10-09复盘中“来源信息在，默认路由不用”与“绑定文献只研究单键”不是成立结论。E59直接测到native来源影响的name-key中介；ACL 2026 CBR已研究entity×relation绑定。旧结果保留，新定位见10-10复盘；C12/C13的有界现象证据不因此作废。
- 2026-10-06：E30 中“主效应能按上下文绑定 = 一条可条件化的独立先验通路”在机制层不成立（经 Sam 锚点的泄漏比与交互相同，差别来自 query 自己标注者锚点的反证，E37）。
- 2026-10-06：“两条通路 = 两组头”（E36）、“新锚点是运行滤波器”（E37）、“‘Label:’ 预测位置存放运行估计”（E38b）被否定；E37 初版数字因 1/rms 缩放作废。
- 2026-10-06：“主效应来自相邻 token 统计”被 E34 否定；“E10 游程头 = 边缘通道”被 E28b 否定。
- 2026-10-06：“任务识别是时间性的、任务学习是可交换的”被 E27 否定。
- 2026-10-06：C02–C07 原标 L3，因未做独立校对改为 L2（泛化条件已满足）。
- 2026-10-05 晚：“全局规则→时间敏感”修正为“输出标签流→结构推断；多数函数切换→仅近因”；“表层规律型 regime → 结构推断”被 E20 证伪。
- 2026-10-05：“表层 vs 潜在”被 E11b 证伪；“单条 demo 可识别 regime”被 E13 证伪；E12 toy v1 不可判读；E10 游程头不是通用时间整合电路。
| C13 | 多人带名字的样例混在同一上下文时，LLM 只保留每人标注倾向的 35–58%（两个真实数据集：Measuring Hate Speech、GoEmotions；8 个模型、4 个家族、7–32B，基础与指令）；交互型视角（谁对哪类内容严）保留 27–48%（E47）；明确指令的作用因模型而异（Qwen2.5-7B-Instruct 1.14、Qwen3-8B 在 GoEmotions 0.98，其余 0.37–0.86）；每人独立的输出标签词在同词表单人基线下恢复到 0.80–1.27（10 个模型 × 数据集中 9 个；gemma 0.52 / 0.70）；机制（Qwen3-8B、Qwen2.5-7B、Mistral-7B）：读标签头把另一人的标签锚点读入答案（= 自己贡献的 73–82%），换词后注意力仍在（81–88%）但贡献降到 3–12%（读出层面的分隔） | L2（待独立校对） | E46、E46b、E47、E48、E49；`results/e46*/analysis.json`、`results/e47/analysis.json`、`results/e48/Qwen3-8B_analysis.json`、`results/e49/analysis.json` | **实际代价未建立（E50、E51、E52）：E52 两套真实标注规范冲突（Davidson 推文）时，混合在边界样本上仍保留 0.59–0.98 的规范准确率，指令常能完全恢复；MovieLens 共享账号的交互情形中，8 个样例只带来 +3–6 点个人准确率，混合无可观察的大代价（Mistral 保留 ~0.8，其余不可判定）；在 GoEmotions 主效应情形下，同词混合仍保留 86–98% 的个人标签预测收益（区分损失发生在 logit 层面，决策远离边界）**；机制在 2 家族 3 模型；2026-10-09 修正了换词比例的词表偏移混杂（E46b） | 2026-10-09 | 未校对 |

## 2026-10-10 新测量（均待独立校对，不作L3/完整机制理论）

| ID | 主张（含适用范围） | 等级 | 证据（实验卡 / 结果文件） | 待补 / 升级条件 |
|---|---|---|---|---|
| C14 | 固定Alex/Sam、平衡二元来源×标签任务中，标签锚点存在可跨标签迁移的来源**双胞胎差分**：Qwen3/Mistral合成检索层残差约0.98–1.00；独立真实评论池Qwen残差0.992–1.000。pre-RoPE K/V跨标签更弱且方向不对称（real某K层0.724），因此只支持common source component，非完整独立编码/天然可用绑定 | L1 | E58、E59；`results/e58/{qwen3_discovery,qwen3_confirmation,mistral_discovery}/analysis.json`、`results/e59/qwen3_real_confirmation/probe_analysis.json` | 新名字与来源抽象角色、去掉双胞胎配对的native解码、相关检索子空间中的因果交换；不得用差分probe饱和声明部署能力 |
| C15 | 在此before-label格式中，native来源交换影响主要经来源名字K中介（Qwen synthetic0.92/0.94，real0.97/0.88，Mistral0.82）；同位置换label的作用很小，label-anchor KV主要承担mapping-flip。source-K与label-KV联合交换有明显非加性交互，纯label-V版本不足以恢复；支持分布于不同位置的协作，未定位精确串行电路 | L1 | E59、E61；`results/e59/*/mediation_analysis.json`、`results/e61/*/analysis.json`；真实与独立合成确认已完成 | 中介比例依赖反事实与hybrid操作；尚需消息/path干预及强模型边界，不能推出新计算构件或一般composition能力缺失 |
| C16 | 对来源名字K交换的native来源影响，**答案末位**label消息不是完整中介：Qwen独立合成确认冻结末位仍余0.471[0.438,0.508]，冻结整个query仅余0.061[0.027,0.094]；受控来源规则的独立真实评论池余0.527[0.476,0.581]→0.054[0.001,0.102]。Mistral同词表复现末位已仅余0.127[0.089,0.165]、全query余0.078[0.040,0.113]，显示时序有模型差异。两scope base/sourceK逐位相同、原生消息重建RMS/no-op误差0。支持query内部、答案前位置参与来源条件化的label消息传递，不支持“默认完全不用source”，也未证明这些计算已足以稳定完成任务 | L1 | E63、E64；`results/e64/qwen3_{synthetic,real}_confirmation_{final,all}/analysis.json` | 独立校对；按query字段的path定位；与Cho shortcut/FV/conditional-rule文献正面对照；前沿推理模型边界。比例是指定干预的平均logit效应比，不是互斥可加份额 |

### C16的E65扩展（L1，2026-10-10）
- sender-edge反事实验证query→末位接力：Qwen独立synthetic冻结Label marker剩余0.226[0.172,0.285]、all-relay0.021[0.004,0.042]；real确认marker0.065[-0.016,0.138]。Mistral同synthetic发现集marker0.947[0.930,0.963]，source字段0.051[0.033,0.068]，sender有模型边界。证据：E65，`results/e65/*/analysis.json`；原生重建/no-op/full冻结全0。
- direct-label删除**不构成稳定修复**：Qwen synthetic发现accuracy−0.086、确认+0.035，real确认−0.023（CI跨0）；Mistral−0.117且margin也下降。平均交互增强不足以推出更好source选择。POST-HOC四项分解还检出偏置与变异扩大，详见`factorial_posthoc.json`，非独立能力/校准验证。
- 继续区分metadata-selected function与input-dependent answer，不因模板token relay或瞬时task state而宣称novelty（Bai2401.11323、Li2509.04466、Cho已有强参照）。

### C16的E66压力测试（不升级，2026-10-10）
输入前source-clause全层KV未部署规则（确认full−null margin−0.109[-0.202,−0.010]nats，single也失败）；已见input的query缓存保留rule相关logit（+1.109[0.861,1.369]nats、rule donor1.919[1.521,2.287]），accuracy仅+0.039，低于预定MIE。证据：E66、`results/e66/qwen3_confirmation/analysis.json`。不能从single/mixed接口共同失败推出独有组合瓶颈，不能从after-input成功证明function transfer；有效推断float32，bf16 chunk首轮VOID。

## 2026-10-10：E67–E70（全部L1、尚非完整计算理论）

| ID | 主张与范围 | 等级 | 实验卡 / 结果 | 限制与升级条件 |
|---|---|---|---|---|
| C17 | 在平衡2-source分类与匹配token多重集下，将相同source code从Tag字段移至答案prefix、不改变最终class词，Qwen独立确认accuracy+0.074[0.047,0.105]、source排序+0.109[0.055,0.172]；label-only K/V不能充分移植收益 | L1 | E67；`results/e67/qwen3_confirmation/analysis.json` | 只限最终class词相同：完整输出语法/namespace仍不同；TF prefix不等同全词表端到端生成。Mistral matched+0.031 CI跨0，非普遍规律；仍需独立schema与强模型边界 |
| C18 | demo prefix K在指定native接口依赖历史上下文化，但不要求历史label内容：E68 isolated-K确认损害Source排序0.063；E69全label列禁读、非label KV逐位不随label-flip变化的K仍保留accuracy/排序，blind−isolated排序+0.102[0.031,0.172] | L1 | E68/E69；`results/e68/qwen3_confirmation/analysis.json`、`results/e69/qwen3_confirmation/analysis.json` | 其它native缓存/labels保留，不能说整模型无标签学习或所有V同等可部署；KV/V/joint的排序等效界更弱。历史必要≠先前task判决，需共偏移/角色/信息内容分解 |
| C19 | float32下，来自不同发现context的冻结label-blind公共prefix-key偏移，在新词库/标签词上恢复blind−isolated margin效应0.527[0.274,0.760]、accuracy+0.059[0.023,0.094]；固定Q组内相对logits近不变（spread<4e-6），支持group visibility/prior可介导预测恢复 | L1 | E70；`results/e70/qwen3_confirmation/analysis.json`、`frozen_frame/frame_metadata.json` | shared Source排序0.828，低于native0.938，预测恢复≠binding恢复。仅固定两名字/marker/布局、36层高容量偏移，保留原生其它缓存，非函数向量独立足够、非整个contextualization规律；进一步预测新schema/名字/模型与native路径 |

E70 common/centered/both的Source排序交互为事后分析（`interaction_posthoc.json`），需要新材料预定确认才升级为合作机制解释。所有新主张不改C09/C13旧有界结果，也不自动定义新head。与Cho shortcut、Few-Shot Examples Add Up（特别附录K）及TVS等强近邻的差异尚需预测与因果路径补足。
