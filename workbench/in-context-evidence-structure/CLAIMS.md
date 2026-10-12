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


### E71对C17/C19的预定压力测试（2026-10-10，仍L1）
- C17：保持扩展namespace、token频率/位置相同，code与source一一对应时prefix收益大、与source/class正交时小。独立新材料relation×layout accuracy+0.109[0.070,0.152]、margin+0.514[0.427,0.597]；来源排序交互CI跨0。Source字段仍真实/充分，故单纯答案空间扩展不足以解释该有界收益；尚非新binding电路。证据 E71、results/e71/qwen3_confirmation/analysis.json。
- C19：**旧冻结frame的新身份/新码迁移未达到预设MIE**：fraction0.350[0.231,0.477]、accuracy+0.031[0.008,0.055]、来源排序−0.008[-0.063,0.047]。发现的0.720/accuracy+0.125幅度不复现。原C19的固定Alex/Sam范围保留；不升级“通用frame”，不按seed或词表重估旧frame后算确认。
- 同context的own common仍恢复0.695[0.550,0.858]margin、accuracy+0.063[0.027,0.098]；完整blind与common/centered的来源排序交互+0.086[0.023,0.156]，是E70 POST-HOC之后新预定材料的有界支持。发现交互0、确认accuracy/margin交互CI跨0，不能升为普遍合作理论。
- 新名字/码词/词库/label同时更换，只能说明联合泛化有边界，不能单独定位哪种身份导致。native chat/reasoning尚待E72，raw一句Source指令边界不得替代该测试。

### E72/E73对能力叙事的限制（2026-10-10，无升级）
- 证据：E72、E73，`results/e72/*/analysis.json`、`results/e73/qwen3_discovery/analysis.json`、`prefix_audit.json`。direct96的single/entity也截断；48次实际短/长采样前缀完全一致，orthogonal thinking同轨迹2048→4096 accuracy .1875→.8125。不能拿未完成回复当来源绑定失败。
- Qwen3.8-27B 8context thinking2048：source_only/linked/entity/single accuracy1.00，orthogonal .4375但56.25%截断。前四项只支持有有效行为程序，orthogonal低分不能证明程序不存在；不从同开发者模型推广frontier边界。
- E73严格direct单来源.750，未过跑前.80控制，因此不触发原能力确认。观察Markdown遗漏后的装饰parser为POST-HOC：8B默认chat长预算source_only .8125、single .9375；不替换strict结果、不把事后阳性当原门槛通过。Source指令下真实错误仍存在，但只有4contexts、未确认。
- 所有这些结果收窄“默认不使用来源”“reasoning无法恢复”的适用范围，未否定原E02/E46的指定任务现象；也未建立稳定新计算规律。C17/C19仍L1，完整因果算法与贡献门槛仍未跨过。

### E74尚未鉴别正向支持与约束补全（不新增主张）
E74、`results/e74/qwen3_discovery/{analysis,run}.json`：36contexts full/seen近100%，held bijection目标accuracy .319–.361；Source指令同步signed响应−.516[−1.178,.105]、owner响应也CI跨0。held independent Unknown决策accuracy0，说明即时输出未可靠执行声明函数空间，不能把微弱负号称已识别positive-support算法。原门槛均未达到，不跑72-context确认；先E75 native有效性。word读取来源≠rule证据来源仍是候选问题，不据此降级E48真实贡献测量或提升新机制主张。

### E75–E77：函数解释边界与进一步降级（不升级）
- E75、`results/e75/qwen3_native_gate/analysis.json`：18新seed contexts full/held bijection均1.00，independent .6667并有.3333截断；所有闭合Unknown正确，不筛闭合后宣称全可靠。允许有效native推理可以补全Source约束，raw低分不是Source能力缺失；完整三条件gate尚未过。

- E76、`results/e76/qwen3_operator_confirmation/analysis.json`：Source方向响应3.648[3.403,3.883]确认，但accuracy .7344[.6719,.7969]未过.80。**query恒为demo中点，Source均值即gold；x+b又是加性，不证明真正Input×Source函数**。撤回阳性的完整组合解释，保留实际数字与方向。两位数whole label值未见不等于每个子token在own source未见。pair分解为POST-HOC，Source排序1.00也不能证明函数完整。
- E77、`results/e77/qwen3_function/analysis.json`：相同Source label边缘下，direct-rule全0..9 query1.00；single complement插值1.00/外推.8828，而single identity .5625/.6719也未过.80，mixed更弱。不能从Single−Mixed差称独有Source组合缺陷。错误多是另一合法function，接下来function识别/应用、指令先后与信息位置仍是竞争解释，不提前宣称“表示在却不用”。

### E78：函数偏好依赖定义顺序，识别→部署主张未建立（不升级）
E78、`results/e78/qwen3_bridge/analysis.json`：32新context/四Source独立规则，mixed direct插值subtract在两定义顺序下.9609→.2500，copy .7734→.9609；word/频率不变。copy-minus-subtract偏好变化+.8984[.7284,1.0821]，single同样+.3672[.2812,.4467]。因此E77的identity劣势不是已经证明的稳定函数或Source组合结构。两order mixed Rule-ID .8516，copy/subtract .8750/.8281，未过两函数.90；single gold-copy外推.8945亦未过执行阳性。auto−empty插值+.1895[.1016,.2637]、外推+.2441[.1680,.3125]是真差值，但一般self-inferred instruction交回执行已有Liu/Neubig/Andreas2024强近邻，不能当新机制。所有材料保留，无C##升级；physical label来源→rule evidence来源仍待有界检验，而非已有新结论。

### E79：共享词典的执行阳性不足，不作规则来源归因（不升级）
[E79](experiments/E79-parameter-evidence-versus-codebook-evidence.md)、`results/e79/qwen3_codebook/{analysis,run,preflight,error_signature_posthoc}.json`：16新context、两定义顺序全部保留。词典lookup .9531–.9875、seen .9844–1.00，但提供真实规则的direct subtract插值 .2188[.0625,.3889]、外推 .1563[.0667,.2639]，未通过复合执行阳性；同context numeric原子未测，不能声称原子均可靠而组合失败。Mixed own-source signed响应约1.5–2.1nats且CI为正，仍不等于完整函数执行；lexical及foreign_D读数CI宽，不能当已区分机制或等效零影响。事后direct subtract错误中151/256输出g(x)、48正确、57其它，是行为签名而非内部计算时序证据。分析bool相减修正不改评分引擎/读数/样本，无新C##。

### 本次综合：保持证据等级，收束投入与措辞
见[`RESEARCH_SYNTHESIS_2026-10-10.md`](RESEARCH_SYNTHESIS_2026-10-10.md)。E59–E71的来源因果路径、whole-query范围、关系×位置与公共载体偏移为优先解释链条；E74–E79不作为其成立的额外门槛。E71冻结frame新身份恢复.350[.231,.477]、accuracy+.031[.008,.055]是正的部分迁移，未达到原MIE不等于无迁移。公共key偏移作用于**整个demo prefix-code载体组**，不是两个Source各自的组偏移；固定Q组内相对logits不变只支持该局部不变性。保留所有原阈值与解释降级，不提升L1或改变I04/ACTIVE，不宣称已有统一ICL理论。

## E81：来源码分配与更广的query读取（L1，有界因果解释）

| ID | 主张（含适用范围） | 等级 | 证据 | 边界 |
|---|---|---|---|---|
| C20 | Qwen3-8B float32、E71 linked分类schema中，固定actual code-carrier每层/head/query的m及kind边缘、翻Source分配，独立64contexts的Prefix margin−.8489[−1.0027,−.7122]、accuracy−11.3[−15.2,−7.8]点；其分配有因果作用。但只移植该carrier的m/pi不能转移位置收益；同recipient Tag与相同码carrier m/pi下，角色对齐whole-query读取比carrier-only accuracy+13.3[9.4,17.2]点、margin+.9181[.7352,1.1107]，指向carrier之外读取的参与 | L1 | [E81](experiments/E81-carrier-mass-versus-source-allocation.md)、`results/e81/qwen3_confirmation/{analysis,run}.json`；32新context pilot→64新seed确认，源码冻结 | native demo缓存/V保留，query内V/状态活反馈；概率donor可能已有答案相关信息，不证明抽象策略或完整电路。单模型/同schema、未经独立科研校对；不能将head平均或output排名当整个证据选择 |

**测量解释修正：** `output_geometry_posthoc.json`证明ranking仅测s>0，accuracy还依赖s与共享bias b的大小。Tag full-attention的Source contrast .583→1.371，|b|均值2.020→2.093；不能把prediction/ranking分离直接升级为“access与binding两个模块修复不同”。E70/71旧数值不作废；C19只保留指定key预算变化与输出效果的有界因果事实。一般校准/label prior已有强近邻，非新的ICES理论。

### C20的E82扩展：Label读取收益与原生Source-effect不是同一反事实

[E82](experiments/E82-label-reading-versus-query-relay.md)、`results/e82/qwen3_confirmation/{analysis,run}.json`：固定码carrier分布、原生Tag组外读取重放baseline下，替换Label列条件log权重使accuracy+7.8[3.9,11.7]点、margin+.4610[.3813,.5438]；只替换query内部列accuracy+.8[−.8,2.3]点、margin+.0472[.0261,.0679]。Label全query相对只在末位替换，margin差+.0140[.0069,.0229]，无大的额外收益。32-context pilot→64新seed确认，源码冻结，数值控制通过。

这是指定布局收益的转移，不是原生Source-effect纯中介；与C16整query原生中介不矛盾。组外log权重拼接会重新归一化其它组，native/活反馈的baseline也不同；不报组件贡献百分比、不命名新独立模块。C20仍L1，同模型/schema，abstract Source策略尚未证明。后续E83用不含query gold的固定关系模型预测Label变化，避免以完整donor取代解释。

### C20的E83预测原型（仍L1）

[E83](experiments/E83-predictive-label-reader.md)、`results/e83/qwen3_prediction/{analysis,run}.json`：只拟合E82 discovery native Label权重变化、不拟合gold输出的冻结关系reader，在64全新contexts将Tag correct margin提高+.3760[.3583,.3933]；预算/位置reader无增益（−.0285[−.0344,−.0226]）。Source/input交互项再+.0667[.0645,.0690]；Label身份项改善统计拟合但无额外margin收益（−.0050[−.0095,−.0005]）。Source匹配翻号损害margin .6320[.5978,.6660]。

这是多个层/head的固定显式关系模型（最大单模型9216系数、kind使用合成语义元数据），不是部署方法或原生模块定位。R与实际Label donor重放作用的逐context相关仅.252/RMSE .273nats，完整预测不足；native条件下Source-match与code-match共线，不能说已证明抽象Source寻址。最大模型不选winner、不重拟合新context，C20不升L2。下一步E84冻结同系数检验该具体共线解释。

### E84对C20预测器的身份解释（仍L1）

[E84](experiments/E84-source-field-versus-code-prediction.md)、`results/e84/qwen3_confirmation/{analysis,run}.json`：Source字段与query code交叉时，冻结同系数的code-match预测比Source-field-match的加权allocation MSE低1.5386[1.5041,1.5714]、输出作用MSE低.1651[.0711,.2750]；原自然query的两预测严格相同。native field/code两输出分量均为正（Prefix .594/.583），不能说code取代Source字段。

code predictor平均field/code分量接近指定Label donor重放，但逐query效果RMSE .620、相关.116，简单B预算模型RMSE .527更低；不升级完整机制模型。cue冲突及TF prefix改变条件语义，结果只诊断身份影响、不作能力负结论。当前候选解释是布局改变涉及code关系驱动的Label读取，同时NameK来源路径仍存在；E85回native路径检验二者依赖，未经该实验不宣布两个独立Source模块。

### E85：cue-specific原生依赖与有限组合预测（C20仍L1）

[E85](experiments/E85-cue-specific-source-paths.md)、`results/e85/qwen3_confirmation/{analysis,run,gate_validation}.json`：64新contexts，Prefix field/code原生分量.566/.496；NameK交换后−.337/.321；LabelKV交换后−.497/−.460；joint +.319/−.309，各分量CI均不跨0。Tag符号同样重现。NameK使code减弱但未反转，不作无影响或独立模块结论。

pilot之后明确POST-HOC提出、commit decabf63冻结的均值组合模型`n*m/b`，未用确认数据重拟合；四项joint均值绝对残差.007–.036nats，固定预测MSE .0232 [.0190,.0280]nats²，优于additive的1.2189。Tag code残差+.022 [.002,.041]仍存在。它只支持此身份/映射接口下的平均作用组合，不是新乘法原理、完整逐query算法或两个Source ID的证明。泛用多机制/绑定与QK/V耦合已有所有权；具体来源cue依赖及预测是这里的候选增量。Source-name K与LabelKV含上下文化信息，hybrid不等于full NM；仍同模型/schema、未经独立科研校对。

### E86：冻结外推失败，保留E85自身的证据范围

[E86](experiments/E86-source-equivalent-code-aliases.md)、`results/e86/qwen3_discovery/{analysis,run}.json`：16新contexts，明确同Source两码可互换；segregated−balanced的未知Item matched/crossed margin gap，Tag14.463 [13.055,15.826]、Prefix15.892 [14.548,17.156]nats；冻结E85均值外推仅.395/.928。两预测模型均严重失准，不因cue相对MSE较小称预测成功。规则输出响应仍为正；这不证明来源信息消失或唯一按码分组的native算法。C20仍L1，E85联合干预的独立确认不撤回。64-context确认未启动，当前不将alias局部控制扩展为主问题。

### E88：来源字段状态的功能范围（C16/C20仍L1）

[E88](experiments/E88-preinput-criterion-transfer.md)、`results/e88/qwen3_confirmation/{analysis,availability_comparison,run}.json`：24 pilot→32新措辞contexts；保留recipient示例，在input前query来源字段上换同姓名donor K/V。隐式criterion T=−.00084[−.01307,.01154]nats；另一姓名T=.17472[.02833,.32209]；显式criterion T=.18225[.14904,.21662]。显式−隐式=.18309[.15328,.21541]，相对native均值比的差也为正。源码冻结、数值误差≤1.34e−5，不筛contexts。

这项分离限制了该Source-field状态的功能解释，不证明pure address、完整criterion不存在或新独立模块。raw默认discordant accuracy约50.8%，不能先假定完整标准已经可靠学会。JIT/Local Task Vectors已提供时间/分布式表示的强解释；显式标准阳性不替代从多Source demo推断规则的中心。E85有效均值预测保留；独立科研校对未完成，不升L2/3。

### E89初版的能力解释作废／接口校对

[E89](experiments/E89-native-criterion-recognition-and-use.md)、`results/e89/qwen3_discovery/wrong_answer_type_posthoc.json`：共享system列两种回答类型，评论请求只用Label:结尾。explicit条件256条评论请求中181个首token为food/service变体。第一token/合法标签域的低准确率不能支持“标准应用失败”；初版只保留为请求歧义诊断，没有主张据此升级。修订明确每次问题，并完整生成，原始数据/源码revision保留。这个校对不自动作废E88的preregistered logit反事实。

### E89完整解码后的解释边界（仍不升级）

`results/e89/qwen3_completed_answers/{run,final_answer_audit_posthoc}.json`：所有178截断样本延长，原前缀178/178保持；最后两条仍未完成。最终内容parser的138项修正已逐项核对末行，标POST-HOC并保留原统计。相反情绪评论base56.25%[52.34,60.94]，explicit52.34%[48.44,56.25]；标准识别在明确请求中分别50.0%和53.12%，初版explicit96.9%没有跨请求保持。没有形成“标准已可靠学会但无法使用”的证据，不据此给C16/C20或能力缺失升级。

**E56代码核对（不是新结果）：** `scripts/e56_query_adapter.py`的qhook只在最后位置加delta，且prefill时state.on=False；示例缓存确实来自未修改模型。不能为了减弱E56而假设该adapter重编码了示例。其成功仍支持baseline表示加额外训练计算的构造性可用性；不等于原生程序或一个八维独立开关已存在。

E88功能校对：explicit patch后的recipient向selectivity仍+.04938[−.01601,.11380]；正的donor向T可以来自Source效应减弱。双向T排除常数label bias，没有排除一般Source-cue扰动，故不将+.182nats直接称为执行donor criterion。用原已注册读数保留这个解释，不开新控制矩阵。

### E90：来源位置选择与rule信息依赖（C16/C20仍L1）

[E90](experiments/E90-source-isolation-before-and-after.md)、`results/e90/qwen3_{discovery,confirmation,heterogeneity}/{analysis,run,rule_sensitivity}.json`：24→48原signed正方向没有确认；POST-HOC发现异质性后，在第三批32新contexts运行前冻结rule contrast幅度。query所有位置只允许读A、其原始证据不变时，B改rule仍使A答案改变17.58%[12.11,23.83]，幅度.73394[.47362,1.08336]nats，16正/16负；两阶段隔离为数值零。不是用绝对值替换原预测，也不称平均性能损失。

`results/e90/qwen3_single_adapter_confirmation/{analysis,run}.json`：现有E56模块在完全没有另一Source的48新contexts仍使61.72%→89.32%，+27.60[21.35,33.85]点；native复测完全一致。这明确排除“收益仅仅来自排除另一Source”的充分解释；模块仍是额外监督计算，不能据此定位完整原生criterion。

Source正确位置读取不蕴含Source信息的功能独立，准确率高也不蕴含独立。宽泛上下文化/attention归因限制已有文献；具体关系信息的计算模型和novelty仍待建立，不自动升级或关闭I04。保留E48/E56/E85，C16/C20仍L1。

### E91：输出namespace对来源内形成/检索的作用（C16/C20仍L1）

[E91](experiments/E91-label-namespace-and-inherited-rule.md)、`results/e91/qwen3_{discovery,confirmation}/{analysis,run,preflight}.json`：24→48新contexts，同脚本SHA45d2f946…；A全部raw token与输出词表固定，只改B编码。query所有位置禁止读取B时，rule影响幅度shared .68334→far .19266，配对下降.49068[.34106,.64469]nats；只改A缓存K、固定全部cached V，下降.22772[.09473,.36098]；V-only下降.24758[.10033,.40605]。两单项均不能复现far；K/V全换精确复现far是数值对照，max误差1.72e−5。A-only B-rule翻转改变答案率22.4%→7.3%，accuracy差CI跨0。

支持B的标签编码影响A历史K/V与后续读取；纯直接foreign词的Value投影不是完整充分解释。保留E48直接DLA、E85冻结预测。一般上下文化/QK-V区分已有文献，未定位完整criterion或唯一子空间；Key作用含access与活query状态，跨Source影响不自动视为不合理。当前一个family/受控rule/原test池，执行者自查不算独立科研校对；无L2/L3升级或开关线。

### E95–E97：共享标准的功能链（探索，不升级C16/C20）

[E95](experiments/E95-source-grouping-and-common-criterion.md)、[E96](experiments/E96-criterion-scope-and-functional-mediation.md)、[E97](experiments/E97-criterion-inference-input-and-answer-code.md)，对应results/e95、e96、e97的analysis/completeness_audit：原2ctxthinking标准16/16、A mixed19/32；仅传自推criterion，删除B/C后Own mixed87.5%且concordant私人偏好100%；新160个标准Goal全部正确，p_A/p_B影响0、c翻转100%。支持标准信息可在不同功能请求中推断、通过文字约束新私人判断；不支持默认私人过程已有同一latent或已识别独立原生criterion模块。

n2仅探索；E96 Own+self/inverse各64行只有32 unique prompts，Own+none只有16，bootstrap单位为context而非重复行。E95材料A块均在foreign之后；E97 review字段与私人Goal不同，不声称token相同的query机制比较。独立agent审计核对数字与边界；仍未做独立新材料的机制确认。

### E98–E99：内部接口未成立，功能链在新材料确认（C16/C20仍L1）

[E98](experiments/E98-criterion-trajectory-without-teacher-cache.md)的112项阳性中，文字mixed14/16、相反私人偏好轨迹8/16，c翻转0；后384未运行。它不支持任何关于prepared donor有无criterion的结论。

[E99](experiments/E99-independent-factor-interface-confirmation.md)、`results/e99/merged/{analysis,completeness_audit}.json`：8新context、criterion64/64，Own256/256但128 unique，native mixed107/128＝83.59%[68.75,96.09]、concordant128/128；39续写、0未知，独立审计通过。标准推断和文字组合链确认；原生本身较强，旧n2普遍弱表现未确认。不能从不同流程的分差证明默认已形成同一latent。全成功经验CI退化、位置与模板关联均保留；无L2升级。

### E101：局部规则断言不是已验证的可迁移状态（无主张升级）

[E101](experiments/E101-native-criterion-commitment-interchange.md)、`results/e101/merged/{analysis,completeness_audit,word_effect_posthoc}.json`：512/512、0未知，511/512最终判断不变。L63 residual首token64/64跟随donor，POST-HOC 20/64 aspect类别改变，但最终仅一例新错误。操作确实生效；此首次局部断言接口没有产生criterion/函数/属性/答案的完整运输profile。不能从已有78.125% event匹配声称运输，不能推广为标准不存在。条件性词语clamp不执行，C16/C20不升降，原结果保留。

### E102：来源字段私人函数切换主要重定位recipient证据（有界探索）

[E102](experiments/E102-source-pointer-versus-program.md)、`results/e102/qwen35_discovery/{analysis,run,completeness_audit}.json`：448/448、0未解析；主分叉recipient B63/64、15/16完整profile，donor函数0/16完整；四donor c/p世界在64receiver上0答案flip，微小margin变化保留。数值self-copy/字段外/matched-prefix差0；失败数值运行保留。限制是layer16、输入前整个字段、4原开发context；支持地址型功能作用，不证明全网络无规则表示。无C16/C20升级，旧E94结果澄清而非撤回。

### E103：示例私人函数主要依赖KV，未发现预设的C/P跨memory分工

[E103](experiments/E103-inferred-rule-memory-crossing.md)、`results/e103/qwen35_discovery/{analysis,run,numeric_audit,carry_audit,completeness_audit}.json`：256/128unique，native98.44%，KV whole-function模型95.31%[90.63,100]，C/P模型无完整四query profile。all-donor/self-copy数值0，48linear真实消费恢复state；split/unsplit微差完整保存。限定direct B完全可识别任务与这个hybrid模型，不称KV存独立抽象程序、不称Rec零作用，无C16/C20升级。

### E104：criterion的部分内部控制，不是已确认原生程序

[E104](experiments/E104-criterion-policy-state-interface.md)、`results/e104/qwen35_positive/{analysis,paired_contrasts,run,completeness_audit}.json`：352、0未知；cross-Actor仅Rec从显式cue搬运，opposite mixed65.63% vs50%，+15.63[6.25,25]pp，concordantOwner p32/32保持、完整profile6/16。存在部分criterion信息作用，actor地址/整teacher函数不够解释；但未达到稳健接口，标准推断Goal矩阵未运行，不能叫native shared criterion program。正式主张不升级。

### E105 / E106：有限标准信息与已确认的历史label证据作用（C16/C20仍L1）

[E105](experiments/E105-inferred-criterion-memory-use.md)、results/e105/qwen35_discovery/{analysis,profile_audit,completeness_audit}.json：608/608，标准16/16；opposite mixed37.5→56.25%、+18.75[3.125,40.625]pp，criterion margin+.442[.402,.482]。after13/128、explicit25/128 EOS，不能称稳定criterion程序。E107同材料/同交换的原生自由续写正在运行，原读数不改。

[E106](experiments/E106-inherited-rule-input-mediation.md)、results/e106/qwen3_confirmation/{analysis,run,completeness_audit}.json：32未选择新context、4608评分。label KV替换使B-rule幅度减少.429[.250,.632]nats，评论内容中介仅.0059[−.0251,.0447]，mirror−.0020[−.0127,.0089]；完整A缓存重建精确，36层干预消费与self路径校对通过。限定评论内容而非所有pre-label位置，不宣称无输入端路由或已有完整prototype算法。正式主张暂不升级，没有独立L3校对。

### E107：私人KV因果参与，标准运输仍不稳定（不升级）

[E107](experiments/E107-criterion-memory-native-continuation.md)、results/e107/merged/{analysis,completeness_audit}.json：480＋extra controls4、0未知；192固定teacher tensor pairs精确同且Own KV不同，同向私人映射全保持。mixed51.56→56.25%，+4.69[0,9.375]pp；explicit60.94%，before/after没有可靠控制转换。自然续写修正EOS测量限制，BF16 full/split微差.787–1.289nats报告，匹配cached/self路径0。结束此Rec/consumer扩展，不推出全模型无criterion；C16/C20 L1不改。

## C21：输出命名通过历史答案消息改变本Source的证据形成（L3，有界）

| ID | 主张 | 等级 | 证据 | 威胁/校对 |
|---|---|---|---|---|
| C21 | Qwen3-8B与Mistral-7B-v0.3 FP32、MHS受控私人规则中，A raw/label固定、整个query禁读B时，B输出namespace对A label证据的作用可通过**先前B答案K→A label形成**近似重建。各32独立context：Qwen完整label接口减少B-rule幅度.553[.353,.761]nats、答案K .561[.360,.772]，Mistral相应为.0619[.0333,.0947]/.0611[.0284,.0986]。冻结系数1逐query rule双差分K重建r=.969/.966、RMSE.810/.265（零预测3.267/.865）；同一冻结namespace预测在Qwen新情绪材料亦保持K r=.907、KV r=.958 | L3 | [E109](experiments/E109-foreign-messages-at-label-formation.md)、[E111](experiments/E111-polarity-relation-versus-namespace.md)、[E112](experiments/E112-formation-mechanism-mistral-family.md)；results/e109/qwen3_confirmation、results/e111/qwen3_validation、results/e112/mistral_confirmation中的analysis/reconstruction/run/completeness审计；12项混杂审计与[独立校对](results/e109/independent_review_2026-10-11.md) | 实际验证3个model/task组合，并非完整2×2；MHS为新context而非disjoint评论。actual donor激活的充分近似子图重建，不是唯一/必要路径或无donor行为算法。K-only仅该边不直接替换V，后继状态自然演化；不称固定全部内容。E110限制与E111关系残差保留。独立318项复算通过；C16/C20和I04正式状态不跟随升级 |

### E110限制C21的功能内容解释（不撤回C21）

[E110](experiments/E110-learned-relation-fixed-label-stream.md)、results/e110/qwen3_discovery/{analysis,run,completeness_audit}.json：16contexts，固定Source/label/位置，B答案第0层KV精确0差；跨类与同类文本置换效应差.0458[−.1358,.2108]nats，答案形成边差.0234[−.0207,.0682]；同类置换已大。该载体对固定label关系改变的完整A label重建r=.323，不能以namespace成功推断通用规则运输。当前需要更清楚的语义关系反事实，E111同任务同时检验namespace/关系；C16/C20 L1仍不改。

## C22：固定输出身份时，历史答案区域消息传递学到的关联（L3，有界、三家族/两材料benchmark）

| ID | 主张 | 等级 | 证据 | 威胁/校对 |
|---|---|---|---|---|
| C22 | 在明确餐厅情绪与独立官方SST5真实Movie情绪两材料benchmark的私人yes-no约定中，Qwen3-8B/Mistral-7B-v0.3等家族，B标签词/Source/位置不变，跨情绪配对相对同类置换的超额作用可经历史B答案区域消息在A label形成时部分传入。各32新词/句式确认，A-only query：答案KV差Qwen .618[.446,.813]、Mistral .404[.313,.499]nats；V版本较K明显更强。正常全Source读取时该超额作用也保持：Qwen .241[.149,.348]、Mistral .263[.198,.329]；E121 SST32 KV绝对超额Qwen.493[.280,.764]/Mistral.128[.056,.213]、Llama.183[.135,.239]、14B.211[.120,.311] | L3 | [E111](experiments/E111-polarity-relation-versus-namespace.md)、[E113](experiments/E113-relation-content-mistral.md)、[E114](experiments/E114-native-formation-reading-crossing.md)；results/e111/qwen3_validation、results/e113/mistral_confirmation、results/e114/{qwen3_confirmation,mistral_confirmation}的analysis/run/completeness审计；[新增独立校对](results/e114/independent_review_2026-10-11.md)，559项数值与两家族token几何通过；[E121](experiments/E121-natural-sentiment-mechanism.md)、results/e121/*_confirmation/{analysis,run,preflight,completeness_audit}.json、[自然数据/机制独立校对](results/e121/independent_review_2026-10-12.md)、[覆盖判断](results/e122/manuscript_claim_audit_2026-10-12.md) | E121后已有明确餐馆与官方SST独立Movie benchmark直接实测、独立校对，支持有界L3；不称跨任务完整程序。传递部分关联，KV/V不等价；native存在通道差异、其它路径大。答案区域包含实际分隔token（Mistral32/Qwen16个B sender），非只word。Mistral实际分块token流含额外空格、非字面整串编码；条件内配对仍严格相同。CTA/QK-V宽所有权保留 |

C21的L3登记依据E109/E111/E112的三个已验证组合与独立校对，§4/5通过；不能当成全部ICL统一理论或论文已就绪。E111完成时C22为单模型范围；不要求残差完美覆盖才承认有界增量，也不因跨模型namespace确认把关联V一并泛化。

**2026-10-11 E113/E114更新：** C22关联内容的家族范围由Qwen扩至Mistral，并接回native全Source读取；该更新依据独立的关联实验而非由C21推断。等级不机械升级，任务范围仍为明确情绪。此前“单模型”是E111完成时记录。C21形成路径获得native支持，范围与精度见C23，不能直接将旧gated精度外推到完整模型。

## C23：原生判断同时依赖形成后的本来源证据与其它来源的读取环境（L3，有界）

| ID | 主张 | 等级 | 证据 | 威胁/校对 |
|---|---|---|---|---|
| C23 | Qwen3-8B/Mistral-7B-v0.3等家族，在受控餐馆情绪与独立官方SST5真实Movie私有yes-no任务中，query允许读取全部来源，固定B位置缓存时改变A位置缓存的namespace形成历史，仍改变对B配对的rule响应：B shared环境下幅度减弱2.098[1.344,2.892]/1.238[1.037,1.464]nats；B far时为.759[.269,1.269]/.684[.461,.896]。A/B缓存交叉的signed rule交互.775[.113,1.440]/.321[.187,.454]。历史答案区域K/KV形成反事实仍可预测原生A label接口的部分namespace作用，两个读取背景均保持（KV r：Qwen .899/.930、Mistral .959/.968）；SST32 formed-A/B-shared幅度Qwen2.151[1.487,2.895]/Mistral1.091[.925,1.258]，signed交互.767[.283,1.244]/.524[.378,.673] | L3 | [E114](experiments/E114-native-formation-reading-crossing.md)；results/e114/{qwen3_confirmation,mistral_confirmation}/{analysis,run,preflight,completeness_audit}.json；[独立校对](results/e114/independent_review_2026-10-11.md)、independent_recalculation_2026-10-11.json；完整§4审计见卡；[E121](experiments/E121-natural-sentiment-mechanism.md)对应自然形成/读取完整analysis/run、[SST独立raw](results/e121/independent_review_2026-10-12.md)、[L3覆盖核对](results/e122/manuscript_claim_audit_2026-10-12.md) | E121后已有两家族/controlled餐馆与官方SST5真实Movie benchmark，MHS另有局部native验证；只在实际接口/语义范围记L3。F/R是位置缓存因子；B缓存也已上下文化且可含A信息，query/attention继续演化，不是固定reader/两个纯Source模块。混合corner为诊断，完整native两端阳性另核；actual donor的近似/部分重建，非唯一必要路径或无donor行为模型。signed交互直接支持本设计的非加性，不以absolute交互单独推断。Mistral分块序列化范围明确；raw比值不作中介份额 |

C23把Source-gated形成接口接回原生多来源判断，补齐当前叙事的功能联系；不要求解释全部ICL或完美覆盖关系残差才记成果。C16/C20、I04及ACTIVE状态不变，没有自动进入candidate或新增实验关卡。

### 2026-10-11：E115–E117扩大已测范围并区分新的功能问题

- [E115](experiments/E115-llama-frozen-native-mechanism.md)：Llama-3.1-8B base，32新词句single两私人方向100%。C22固定label关联KV绝对超额.157[.103,.215]nats，signed −.081[−.172,.011]；C23形成条件作用(B shared/far).947[.740,1.158]/.337[.088,.592]，signed交互.221[.026,.417]。冻结KV原生label效果r .838/.881、RMSE .559/.720（zero1.015/1.411）。C22/C23的明确情绪范围扩至第三家族，仍L2；grade不机械随模型数上调。证据results/e115/llama_confirmation/{analysis,run,completeness_audit}.json，权重身份results/e115/model_identity_audit.json。
- [E116](experiments/E116-native-mhs-formation-reading.md)：三家族真实MHS文本的局部native形成效应已确认，Qwen/Mistral/Llama B shared幅度.344[.179,.525]/.0645[.0357,.0928]/.112[.075,.155]；完整数值见卡与results/e116/*_confirmation。single规则能力仍弱，因此扩的是C21/C23的因果margin任务范围，不写成可靠人类私人规则部署或应用修复。MHS探索与确认评论交集124，保留新context表述。
- [E117](experiments/E117-criterion-feature-formation.md)：固定A与B输出stream的paired criterion反事实，经A-label缓存改变新输入的Food/Service功能响应；三家族确认两方面同增。当前历史答案KV的Service作用没有跨三家族一致保持（Llama部分作用确认，Qwen/MistralCI跨0），不能由C21 namespace路径或C22情绪关联推断完整criterion运输。原阳性机制不撤回，新的功能分叉由E118检验；未新增L3/摘要标准程序主张。

三实验原始复算、实际token流、all-layer消费与取样校对：[第三轮独立审计](results/e117/independent_review_2026-10-11.md)。C16/C20、I04/ACTIVE状态不变；新增完整四点observer的探索POST-HOC-DESIGN与确认冻结已分开记录。

### 2026-10-12：E118/E119功能校对与已有主张的能力范围

E11914B正常全Source确认：namespace形成幅度3.059[2.557,3.571]nats，固定答案KV关联abs .318[.226,.421]/signed .249[.115,.390]；冻结KV对label rule反事实r .934/.927、RMSE1.047/1.818（zero2.610/3.949）。C21形成解释与C22/C23在更大同族模型上有直接支持，不以参数数自动升级。**C23 signed交互14B为−.686[−1.133,−.237]，8B级家族正方向不能写成普遍规律。** 14B plain continuation不是完整reasoning压力测试。

E118三家族与E11914B的criterion×private-code响应显示，关联幅度/两task平均J与具体功能方向必须分别解释。far形成同时降低两方面代码响应，即使J差近零；native label负det、gated label正normalized rotation、edge小正det都保留。不能从CI跨0宣称形成端rank1，也不能从namespace高r推广完整criterion程序。Food始终先Service，固定模板范围明示。

## C24：关联形成与标准相关功能响应需要不同的反事实测量（L2，有界）

| ID | 主张 | 等级 | 证据 | 边界 |
|---|---|---|---|---|
| C24 | 固定方面顺序的双方面评论任务、请求A且A raw/B输出stream固定时，B criterion×私人约定反事实在不同缓存干预接口产生不同A功能响应。Qwen3-14B32新材料native下，B代码反转对匹配方面相对另一面更强：Food选择性.282[.199,.371]、Service .404[.294,.528]nats；signed rotation .410[.330,.493]。query全程禁读B位置、A仍由完整历史形成的gated条件rotation .190[.073,.310]。A-label交换J为−.0238[−.0478,−.0025]，历史答案KV对actual label干预只部分重建（r .668/RMSE .646 vszero .746）。因此关联消息传入的证据不能直接替代整个criterion相关功能的验证 | L2 | [E118](experiments/E118-criterion-code-feature-crossing.md)、[E119](experiments/E119-stronger-model-formation-criterion.md)；results/e118/*_confirmation、results/e119/criterion_{discovery,confirmation}/{analysis,response_rotation,run,completeness_audit}.json；[E118独立校对](results/e118/independent_review_2026-10-11.md)、[E119独立校对](results/e119/independent_review_2026-10-11.md)及独立主张措辞核对 | n16→n32独立材料，方向observer首E119评分前冻结；各CI未多重比较校正。native改变完整历史、label/edge保留recipient其它缓存，故不能由接口差异推断独立隐藏模块/算法。B code影响A不是成功Source隔离或B自己的任务正确率；固定方面词序尚未排除位置选择。label负det、gated label小正rotation、edge小正det和残差保留，未称label完全共同gain、无criterion信息或独立完整程序。actual donor重建非无donor算法 |

C24把C22“关联可进入本来源证据”与其具体功能尺度分开，补充而不撤回C21–C23。由人判断最终论文意义与形态；C16/C20等级与I04/ACTIVE排程未改。E115–E119完整24批、576contexts/181632评分，三份独立审计36750项数值核过（max1.13e−14）；独立token几何/消费校验完成，未独立GPU重跑。


### 2026-10-12：E120/E121把形成预测接到原生操作与自然功能

C21–C23新增直接证据，不把旧重建冒称独占必要路径。| 模型，确认n32 | full-source阻断 | A-only阻断 | full-source有限图恢复 | A-only有限图恢复 |
|---|---:|---:|---:|---:|
| Qwen3-8B | 1.649 [1.108, 2.250] | 1.104 [0.543, 1.770] | -0.806 [-1.365, -0.266] | 1.455 [0.999, 1.945] |
| Mistral-7B-v0.3 | 1.054 [0.886, 1.227] | 1.039 [0.804, 1.289] | 0.140 [0.053, 0.231] | 0.647 [0.463, 0.835] |
| Llama-3.1-8B | 0.808 [0.517, 1.109] | 1.108 [0.834, 1.386] | -0.233 [-0.336, -0.122] | 0.958 [0.635, 1.276] |
| Qwen3-14B | 1.329 [0.967, 1.717] | 1.126 [0.669, 1.637] | 0.039 [-0.217, 0.287] | 1.120 [0.673, 1.646] |

- **C21：** E120四模型原生操作阻断支持历史答案访问的条件贡献；只恢复答案→label在A-only读取为正，在native可为负。output-namespace重建L3范围保留；native操作不是纯原始message数值贡献或唯一电路，不自动升级L4。
- **C22：** E121固定output/multiset的自然情绪配对内容作用确认，四checkpoint KV绝对超额依次.493/.128/.183/0.211nats，signed逐项保留，Llama为−.109。仍是部分关联，不由absolute效应推断正确标准隔离。
- **C23：** E121真实文本private能力有效，同一native形成×读取与namespace预测在新query成立；不同缓存背景仍活演化，signed方向按模型/材料核。功能自然范围从MHS弱任务拓展到SST明确私人约定，不把这称真实人标准部署。
- **C24：** E120/E121为单方面，不能自动扩展双方面criterion结论。整体双Actor/criterion×code使用预测在E122跑前冻结，目前未完成，不作结果升级。

| 模型，确认n32 | single正约定（n16） | single反约定（n16） | native形成幅度nats | KV label rule r / RMSE / zero | 固定词关联KV abs超额nats |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | 98.4% [96.1, 100.0] | 88.3% [80.5, 95.3] | 2.151 [1.487, 2.895] | 0.931 / 1.363 / 3.658 | 0.493 [0.280, 0.764] |
| Mistral-7B-v0.3 | 99.2% [97.7, 100.0] | 96.9% [93.0, 100.0] | 1.091 [0.925, 1.258] | 0.948 / 0.336 / 1.048 | 0.128 [0.056, 0.213] |
| Llama-3.1-8B | 97.7% [95.3, 100.0] | 99.2% [97.7, 100.0] | 0.689 [0.488, 0.901] | 0.930 / 0.309 / 0.840 | 0.183 [0.135, 0.239] |
| Qwen3-14B | 99.2% [97.7, 100.0] | 93.8% [87.5, 99.2] | 1.678 [1.340, 2.052] | 0.966 / 0.519 / 1.949 | 0.211 [0.120, 0.311] |

实验卡[E120](experiments/E120-operation-necessity.md)/[E121](experiments/E121-natural-sentiment-mechanism.md)与results/e120、e121每批analysis/run/behavior可复核。E120独立9736项/完整token和图校验通过，E121完整8328项审计已封版；不将复算称独立GPU复跑。single within-answer-off的Mistral损伤/Qwencross-within CI跨零均保留，范围不夸成来源专用构件。未改变I04与ACTIVE正式状态。


### 2026-10-12：E122构造性功能预测与C22/C23证据升级

| 模型，确认n32 | targeted−native平均pp | A | B | 两gold一致 | 两gold冲突 | targeted−all-cross pp |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | 2.93 [1.42, 4.35] | 1.37 [-0.68, 3.32] | 4.49 [2.15, 6.84] | -2.34 [-4.00, -0.78] | 8.20 [5.86, 10.45] | 11.91 [10.25, 13.53] |
| Mistral-7B-v0.3 | 3.42 [1.17, 5.76] | 5.66 [2.54, 9.08] | 1.17 [-1.27, 3.52] | -1.95 [-4.98, 0.88] | 8.79 [6.15, 11.62] | 9.81 [6.74, 13.04] |
| Llama-3.1-8B | 7.37 [5.37, 9.43] | 8.01 [4.79, 11.33] | 6.74 [4.49, 8.89] | -1.86 [-4.30, 0.39] | 16.60 [13.87, 19.43] | 12.65 [10.40, 15.04] |
| Qwen3-14B | 2.78 [0.49, 4.79] | 2.83 [0.00, 5.47] | 2.73 [0.10, 5.37] | -3.61 [-5.86, -1.56] | 9.18 [6.15, 12.30] | 13.33 [11.33, 15.38] |

C23新增[选择性形成/读取功能证据E122](experiments/E122-source-preserving-formation.md)：8批16→32、三家族＋更大同族在同prefix请求两个Actor，primary平均收益确认；一致gold成本/每Actor区间/模型query-only差异完整。它不是同一query joint正确率，也不是独立source-selection head或固定其它latent信息的纯操作。E123真实文本/namespace功能预测在91374879首评分前冻结，正在执行；E122结论不以E123阳性作资格条件。

**登记升级：C22 L2→有界L3、C23 L2→有界L3。** 依据不是模型数增加，而是controlled restaurant与独立公认SST5 Movie benchmark的实际n32 paired确认、至少Qwen/Mistral两家族、§4审计及§5独立raw校对。C22 SST固定word内容KV abs .493/.128，两方向/private与signed全部核；C23 SST形成条件作用和signed交互在两家族确认，不将14B其它材料的负交互抹掉。主行范围同步，旧“仍L2”均为当时历史登记。C21有界L3保留，C24固定双方面单任务仍L2，不把其它主张自动上调。

证据追加[E121](experiments/E121-natural-sentiment-mechanism.md)与`results/e121/{qwen3,mistral,llama,qwen14}_confirmation/{analysis,run,preflight,completeness_audit}.json`；[独立自然数据/机制审计](results/e121/independent_review_2026-10-12.md)8328项max5e−15，[E122原始审计](results/e122/independent_review_2026-10-12.md)9960项max0和[独立整篇/覆盖判断](results/e122/manuscript_claim_audit_2026-10-12.md)。Source函数正确性、priors、图归一化、多重比较、实际token构造范围明列；无独立GPU复跑。未改I04/ACTIVE、未自动转candidate或使用H判决。


### 2026-10-12：E122/E123整体功能预测与三项主文认识

C21形成解释、C22部分关联内容、C23形成/读取共同作用不仅保留原界面预测，还产生整体功能政策的独立确认。E122双方面targeted平均+2.93/+3.42/+7.37/+2.78pp；[E123](experiments/E123-natural-source-function-policy.md)真实SST四checkpointshared平均+7.32[5.37,9.28]/+5.37[2.93,7.71]/+9.47[7.52,11.52]/+7.42[5.57,9.38]pp，两Actor收益CI均正，candidate/full primary逐query一致。四模型16→32、所有85条件完整，证据`results/e123/*_confirmation/{analysis,run,preflight,full_output_summary}.json`与[独立22824项复算](results/e123/independent_review_2026-10-12.md)。C21–23有界L3/C24单任务L2保留，不凑新C25。

query-only与targeted优劣依模型/任务而变；same约定不保证受益。far native headroom/词先验不同，namespace gain差不能单独证明纯identity特异性。far/all-cross own-space正确率仍94–97%但full51–54%，other-word44.6–46.9%且Actor不对称，表明完整wordspace使用与candidate函数需要分开。Mistral far targeted full−1.27[−2.44,−.20]pp、candidate0，14B full+1.27[.29,2.25]；不得改写为普遍无损repair、Source识别新组件或bindingID独占解释。政策删除不等边数、状态活演化，结论是固定政策的整体功能后果。


### 2026-10-12：E124身份共同上下文的形成/读取功能

[C23补充E124](experiments/E124-source-identity-coordination.md)：私有监督完全互不可达、公共无标签名单F/R交叉。Qwen完整输出形成身份特异+4.59[2.73,6.64]pp，A/B与私人方向均正，candidate差+.10CI0；Mistral−1.07[−2.05,−.20]，Llama−.68[−1.95,.49]。提供不交换私人监督的部分形成期身份作用及家族边界，不推广统一修复或识别新binding ID。完整6批144ctx/54144scores，独立11742项max0/实际消费与可达图审计，证据results/e124/*_confirmation/{analysis,run,preflight}.json、[audit](results/e124/independent_review_2026-10-12.md)。C21–23有界L3、C24L2与formal状态不变；E125只检验共享Source词空间的更明确关系，不以它成功为原主张新资格。


### E125公共关系的形成作用，C23构造性补充

E125公共Source–输出词关系三模型16→32已完成：形成期特异+26.66/+7.71/+8.30pp，直接query期三项未定；错误对应表也有益，不能以字面表路由解释。私人监督历史形成隔离、joint query仍读两缓存，Qwen候选功能代价与M/L来源非对称保留。下一项E126以信息完全等价的表行顺序做私人缓存组合，检验共同上下文兼容性；不是新头/层或prompt优化。 95%CI Q[23.05,30.47]/M[5.08,10.45]/L[6.05,10.84]；正确比交换形成+11.72/+4.39/+5.47pp，但交换表自身全家族收益，不证明照表选择。三家族/all-seed/all-direction与single/instruction/floor/inert/actual层mask保留；[E125](experiments/E125-public-output-schema-coordination.md)、[raw audit](results/e125/independent_review_2026-10-12.md)、各确认analysis/run.json。6批.735239 GPU·时，独立18126数值max0、100800prefix/302400query层调用，9216完整argmax零确认；无独立GPU rerun。


### E126：相同事实下的联合缓存兼容依赖（C23补充）

E126在public事实/private监督/词集/global位置全部相同时，共同order形成的Source缓存联合使用优于混合：Q/M/L +23.49[20.80,26.07]/+10.40[7.96,13.04]/+5.42[4.00,6.79]pp，private source-only仍强；主要词空间使用，candidate效应小。它补充公共关系形成如何支持独立规则部署，但不识别ID或latent非加性。Q/M两个coherent order有差、margin点负CI0、M A joint低全部保留。 [E126](experiments/E126-equivalent-schema-cache-composition.md)/[完整raw审计](results/e126/independent_review_2026-10-12.md)；6批.627887GPU时、12462数值max0、actual每层图/gold全部过。C21–23 L3/C24L2与formal状态不变。


E126 **POST-HOC辅助解释**（不改冻结primary/正式等级）：只在两private约定相反的origin，逐argmax另一Source词与其gold核对；coherent−mixed另一规则相容输出Q/M/L −23.73[−27.44,−20.02]/−10.06[−12.79,−7.42]/−4.88[−6.64,−3.22]pp，符合requested code换词的变化远小。Q/L own-space错误code同时增加2.54[.68,4.88]/.68[.10,1.27]pp，非所有错误一起减少，也非both-world primary的中介份额。此读数只测输出与规则相容，单纯词空间竞争仍可能选中另一已学函数，不识别called rule/ID。来源[实验卡](experiments/E126-equivalent-schema-cache-composition.md)、[独立POST-HOC校对](results/e126/posthoc_independent_review_2026-10-12.md)、[诊断](results/e126/posthoc_selected_code.json)。

### E127：共享输出下共同形成背景约束规则使用（C23补充）

四固定checkpoint16→32全部完成；shared/opposite primary共同背景收益Q8/M7/L8/Q14 +8.89[6.64,11.13]/+5.86[4.10,7.71]/+.78[.10,1.56]/+9.38[7.32,11.52]pp，Source特异margin均CI正。与E126一起排除仅选择不同词集作为完整解释，补充同词私人映射在联合使用时的背景依赖；S是已有gold margin投影，不是额外独立机制证据，不推断新ID。L individual/private不普遍正、own0设计恒等、coherent冲突joint仅53–65%全部保留。依据[卡E127](experiments/E127-shared-output-rule-cache-composition.md)、results/e127/*_confirmation/{analysis,run,preflight}.json、[独立35528项复算](results/e127/independent_raw_review_2026-10-12.md)。C21–23有界L3/C24L2和人负责的formal状态不改，不另凑C25。E128会检验food/service输入标准，不把新资格附加到旧形成主张。

**辅助条件说明更正：** E124–127存储instruction同时阻断跨Source私人形成，不能冒称相对native的纯prompt效果；数值与primary维持，附录B披露。E128首评分前修正，E122/123纯prompt控制不受影响。


## 2026-10-12：E128完整后回到规则选择计算

E128四checkpoint16→32全部完成；同no/yes同private code而Food/Service标准不同，冲突query的coherence收益Q8/M7/L8/Q14 +1.56[−.59,3.52]/+.98[−1.37,3.32]/+.78[0,1.76]/+2.93[.59,5.47]pp。四家T小正，但joint约50–53%，原生与单函数能力按同冲突query范围核；不把code协调泛化为完整标准选择，也不撤回已封形成阳性。192ctx/130560评分、1.237902GPU时、38760独立raw数值max0。

依据[卡E128](experiments/E128-criterion-frame-cache-composition.md)、[全矩阵报告](results/e128/report.md)、[38760项raw独立核](results/e128/independent_raw_review_2026-10-12.md)。C23形成兼容与C24功能分辨率获得有界补充，不将每个实验新增claim，不自动升降级。原C21–23三认识与最强近邻所有权保留。主文§6.5一段、附录K完整两phase及primary匹配primitive；函数弱/固定方面位置/公共关系与私人规则不等于新ID保留。下一项E129检验input-independent来源选择状态在同recipient图上的criterion×code功能，两co-primary为CueB本身与CueB−CueA的signed det；Hendel/JIT/Dong的一般task-state范围必须正面承认。


## 2026-10-12：E129来源状态功能的完整结果

E129两checkpoint固定16→32完成，pre-input Source Cue来自完全隔离私人历史、保留recipient全部示例时，两模型两个co-primary功能det的确认CI均跨0；不是数值失败。Q14仍有小标准相关响应，不能称Cue没有任务信息。单函数冲突能力L约69–74%、14B约77–80%，故这项运输接口不足不能由任务全不会解释；也不外推模型没有criterion表示或默认原生Cue无效。96ctx/49152评分、.413184完整run GPU时、20580独立raw数值max3.33e−16。

证据[卡E129](experiments/E129-source-cue-task-information.md)、[完整报告](results/e129/report.md)、[独立raw](results/e129/independent_raw_review_2026-10-12.md)，主文Discussion两句/附录L完整范围。未确认两个标准方向不等于信息完全不存在；native与F0形成图不混同，Q14纯指令实际输出代价保留。旧三认识/最强近邻所有权保留，不新凑claim/自动升级或缩掉已封阳性。当前候选问题是不同历史共享政策如何形成Source条件信号，与C23形成/部署链连接；独立高层审阅和论文核对后再写新卡，未运行。


## 2026-10-12：E130完整结果与跨尺度核心检验

E130固定Llama8B/Qwen14B各16→32、native/targeted/independent三历史policy与同F0 receiver，96ctx/104448scores完整。两个native确认co-primary的95%CI均含0：L CueB−.00001751[−.00004604,.00000357]、Source差+.00000294[−.00002280,.00003356]nats²；Q14相应−.00018214[−.00060371,.00024593]/−.00036502[−.00099327,.00021095]。Q14Food selectivity+.02144[.00972,.03348]nats而Service−.01465[−.02661,−.00353]，部分criterion响应保留。这个Source前输入接口的三政策没有建立完整两个方向，不能据此收缩C21–23的原生历史形成/关系/功能解释。

依据[卡E130](experiments/E130-formation-to-source-cue.md)、[完整136接口与全部政策/函数报告](results/e130/report.md)、[独立raw/report校对](results/e130/independent_raw_review_2026-10-12.md)。81188 raw数值max4.44e−16，28728展示数字全一致；.805577完整科学run GPUh，数值floor2.48e−5。读序例外公开，未独立GPU rerun。主文三认识/等级/formal状态保持，附录L补该follow-up。

阅读ACL/EMNLP/NAACL实际跨模型证据后，E131直接检验同一核心链：Q32/L70形成反事实、原生操作、真实SST两来源功能，加同family8B新材料配对，18CPU完整首评分前451238d5冻结。初试TF32的三worker未通过原.001误差、0科学row，失败全部保留；0a50bbb1恢复原full-FP32并重启同种子/材料，8B已通过数值检查，32加载完成，70权重下载并依资产/空卡接入。既不缩主张，也不要求强模型持续犯错；待完整结果判断形成与读取怎样共同改变Source使用。

E131首轮9/18独立校对完整：Q32三环节已支持同一形成/原生操作/Source函数解释，SST shared平均full86.9141→95.8984%，配对收益8.9844[5.8594,12.5000]pp；单规则两方向本批100%而形成仍有作用。原C21–23三级和C24二级不变；新32确认与70未完成，不借局部Cue结果撤销形成认识，不用D与不同材料的8B作配对scale。见E131卡与results/e131独立raw/report。


### E131：相同三环解释的32B确认（C21–C23补充）

同family/stage新32材料配对：Qwen3-32B A形成signed2.676[2.266,3.096]nats，系数1 KV label raw r=.883、rule双差r=.922；原生答案路径移除1.972[1.467,2.500]、受限恢复A-only+.775[.321,1.284]/full-source−.544[−.833,−.276]。真实SST shared/full两Actor平均87.99→95.70%、gain7.71[5.76,9.57]pp，相对all-cross+20.41[18.16,22.36]；与Q8 gain差CI0、query-only差+8.40[3.81,13.09]，不把区间跨0当统计等价。说明同形成操作/原生贡献在32B仍成立，读取贡献可以变化；单函数强不能替代关系形成与使用的机制解释。

依据[E131卡](experiments/E131-large-model-mechanism-chain.md)、results/e131/qwen32_confirmation_{mechanism,native,function}/{analysis,run}.json、function/full_output_summary.json与[12批raw-first审计](results/e131/independent_raw_review_2026-10-12.md)。12/18完整stage，全部43/64/85条件、私人方向、负结果与36大小配对保留；没有独立GPU rerun。C21–23 L3/C24 L2及formal状态不变，未额外新增claim。L70当前仅加载/执行未完整批，不先算70证据，不以Cue接口限制收缩已确认形成链。

### 2026-10-12：E131 70B形成发现（不升级等级）

E131第13完整批Llama3.1-70B n16独立raw-first审计：A形成+.993[.612,1.373]nats，A单源两private方向100%；固定词answer关系excess abs+.237[.116,.368]而signed−.229[−.382,−.085]。12个固定重建都保留，shared/far B-cache背景下KV rawr.542/.854，均full-source query reading，残差/通道顺序不同；不声称规模使重建一律增强。支持C21/22现有形成与关系内容的跨当前容量补充，完整70B三环确认尚在执行，C21–23 L3/C24 L2及正式状态不变。证据[E131](experiments/E131-large-model-mechanism-chain.md)、[完整报告](results/e131/report.md)、[独立raw](results/e131/independent_raw_review_2026-10-12.md)、本批run/analysis；root stdout阅读例外如实记录，独立会话仍先raw封后作者比对。

### 2026-10-12：E131 70B原生发现（不升级等级）

第14完整批n16原生操作独立复算1217数值差0。full-source路径移除signed+1.542[1.096,1.970]nats；受限恢复A-only+1.011[.637,1.401]、full-source−.440[−.653,−.208]，cross-vswithin+2.560[2.065,3.059]。A单源两方向100%。支持既有形成操作在此大容量checkpoint参与native计算及其阅读环境依赖；确认与函数尚执行，不从发现批升级或新增claim。证据[E131](experiments/E131-large-model-mechanism-chain.md)、[完整报告](results/e131/report.md)、[独立raw](results/e131/independent_raw_review_2026-10-12.md)与本批run/analysis。C21–23 L3/C24 L2不变。


### 2026-10-12：E131 70B三环发现已接成链

第15批n16函数独立raw-first复算1893数值误差0：shared/full两Source平均86.72→98.44%，selective gain11.72[8.01,15.43]pp，targeted−all23.44[21.88,25]；A/B各5.86/17.58点、opposite23.44/same0。query-only10.55[5.66,15.04]；far all-cross candidate99.02/full51.17/joint3.91%，全部85条件与来源非对称保留。single A98.44/100%、B各方向95.31–100%，不是任务不可用条件下的机制归因。支持原C21–23形成/使用解释的当前大容量补充，未从n16发现提升等级或新增claim；剩原三批新32确认，C21–23 L3/C24 L2及formal状态不变。证据[E131](experiments/E131-large-model-mechanism-chain.md)、[完整报告](results/e131/report.md)、[独立raw](results/e131/independent_raw_review_2026-10-12.md)与llama70_discovery_function/{run,analysis,full_output_summary}.json。
