# 痛点日志 — 2026-10-03

| ID | 复现条件与量级 | 实验 | 状态 / 下一动作 |
|---|---|---|---|
| P01 | 初始系统Python无torch；8×H20约96GB授权 | E01–E20 | env与依赖锁完成；独立GPU锁调度 |
| P02 | parent缺二值许可；25试标9许可/61choice分歧；partial access不能全当negative | E01/E05/E11/E19 | SDT gold不成立；明确候选q、QUD、规范，不强造标签 |
| P03 | 原生格式导致不解析；E06 3,600都可解析；E10同预算逐字一致 | E02/E06/E10 | 客观版本化解析；提示恢复不等于latent能力 |
| P04 | thinking初版漏关；BF16 batch差.85/4.62；Flan target-left-pad差2.22/1.05 | E03/E08/E15 | 初版隔离；FP32/right-pad及首末数值gate通过 |
| P05 | 原14B下载已完成；OLMoE三stage约56GB曾网络断流，Base/SFT完整，DPO2026-10-03下载完整；免费OpenCode403 | E02/E12 | 有界重试/断点不清除；其他完整模型并行运行；不使用半成品或绕过限制 |
| P06 | ALTPRAG URIAL/数据版本、PaCE表/文本/stage冲突；presupposition context方向、listener–speaker Table5/prose冲突 | D1/D5 | 阅读/页图核对保留，未取得原实现处注明不确定；不据此kill |
| P07 | E19 IR16item仅6有critical utterance；SI published q_posterior而src q_prior；human排除267与文中247不符 | E19 | 遵循发布prompt与原eligibility；缺数据不自行填造；结果界限透明 |
| P08 | GPT2双换行token边界及left-pad绝对position会改变atomic概率；Flan数字0非一token | E18/E19 | GPT2-r3 gate通过；Flan atomic协议不可用，不当能力证据 |
| P09 | 原下注生成max50/首newline下，部分模型输出说明/单选/无效整数 | E20 | 固定收全；无效与截断单列；不能悄悄归一化或用新prompt救排名 |
| P10 | Graded Expectations候选频数加权需count-only null；SALT原OSF401 | D5 | 尚无原资产，不宣称论文错误；语义理论保留用于许可分析 |
| P11 | E21 OLMoE chat实际输入不一致：Base bos=None，SFT bos50279；special映射0/50279 | E26/E27 | 固定完整SFT tokenizer与BOS0/50279配对，旧聊天stage归因隔离；裸输入parity通过 |
| P12 | ImplicatureX源BF16 pair sum偏离1最大.00293；自然Q3-4B recognition .78→.46重归一诊断，median order gap .99917 | E23–E25 | 技术问题保留原cache，不作paper finding；不能据小模型源阈值数字直接说human-like |

痛点是测量/驻留障碍，未升级为科学发现；次级方向可更换，territory状态只由人决定。


| ID | 复现条件与量级 | 实验 | 状态 / 下一动作 |
|---|---|---|---|
| P09 | IQAP无QA probable prior≈1；Q25Instruct bare full-vs-content强度差+.122→−.137 | E33 | 原full主/secondary content/null全报，不把prior当over-inference |
| P10 | Circa负强度4B源/逆序strong acc .808→.038；strict8B强+.577而弱−.500 | E34/E36/E37 | 有界指令控制完成，停止局部prompt救分；真正语境证据待研究 |
| P11 | Mistral数字两token、原尾空格retokenize，官方template追加assistant遗漏system | E35 | 全在CPU拦截；完整候选+冻结prefix、独立full teacher-forcing gate，第三family运行 |

| P13 | E38/E39五token非EOS数字截断；E42 5196中3677延长变prose | E42 | 原数字不覆写；相关stage解释隔离，固定32诊断结束，不救排名 |
| P14 | E43 MistralInstr chat数值完整覆盖2/1/11 of32；Q3-14 Mark初始理解不符human | E43 | 全bounds/失败保留，不筛材料；无两入口跨family能力结论 |
| P15 | BWIM public QA code与paper confidence实现、seed session不同，原闭源答案器 | E44/E45 | 五model有限confidence协议迁移；不拿dummy Yellow或本地judge冒充原QA |

| P16 | E45五模型无歧义control正确5/19/21/29/8 of64；Q3-14有11精确z反射、23其它错误 | E45 | 几何仅POST-HOC诊断；confidence/partner能力解释隔离，不增加恢复prompt |
| P17 | E49两Q25原生rep penalty使processed generate scores与raw teacherforce不同；首轮0预测 | E49 | 原四失败control/日志保留，独立r2用raw logits，保持生成与.001 gate；不改其余运行脚本 |
| P18 | Mayn源identity photo/practice不能被一行文字视作等价；weak-evidence processed727 vs final723缺原filter | E47/E49/E50 | 明确文本迁移/派生speaker读数；未配gold不伪造标注，free OpenCode403仍无可用标签 |

- P19（E53，POST-HOC）：strict parser拒绝完整JSON围栏/数字字符串，不能把schema失败叫语义错误。无损CPU审计恢复大量可用，但控制仍失败；原主读数不改、恢复不作能力提升、不追加prompt。
