# E20：同事实换对象顺序，区分否定对象最近提及与旧关系影响（2026-10-05）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01/P10；E19为什么明确role cue之后还有history差。
- **问题（一句话）：** 把原only-X/not-Y改成not-Y/but-only-X，使肯定对象最后出现，GP历史差会消失还是仍保留？
- **设置：** 原7episodic sources×2NP choice×GP/comma×2role事实×3targets=168新输入，仅continued-same（E19中7源这层明确）；复用E19 same168旧scores。pinned frozen Qwen3-8B FP32/SDPA、seed0/batch4、TF32=false、raw text无instruction/question/chat。全部/eligible/acceptable/facts-preserved∩clear-scope strata、两个NP选项和每source报告。
- **数据：** 独立Luna构作同事实对象顺序变换，另两Luna各96/72审rendered文本。仅exclusive role statement变化；S1、原same bridge、S2及三个target短语不变；actor/activity/进行时/episode范围/互斥关系不变。允许but与particle为语法调整，dry off粒子前置须明确记录；lexical tokens除but应保持同词袋。source22构作者uncertain保留，最终独立review事前标flags；不因结果改同义词/素材。cache/E20-material-preparation-v1，原数据版本/审计理由不进git。
- **读数：** R=bits(own NP)−bits(author ref)，M=bits(other NP)−bits(own NP)；两个format各报告GP/cue cells与D=GP−comma；主contrast order-history = D_not-Y-only-X−D_only-X-not-Y，分别reference-only/initial-only。role事实双向控制在两format/GP/cue分别报告。两NP先source内平均、paired bootstrap10000/seed20261005、95%CI，不以CI跨0证明完全恢复。
- **阳性对照：** 两format的reference-only/initial-only应能反向改变target preference；原E19 reference-only与initial-only控制GP+8.51 [5.15,12.32]bits、cue+10.60 [7.75,13.55]。三个targets pre-context tokens相同、HF/manual loss核对；旧E19/hash固定复用。若新format本身不被读数响应，只谈语言/测量局限。
- **噪声地板 + MIE：** 原FP32词级漂移≈1e−5bits；n7 CI与source模式完整报告，不设任意阈值gate。
- **混杂审计：** 改顺序同时改变信息焦点/协调结构，不能把order交互归成纯recency神经机制；但同事实控制能限制“必须是旧语义关系不可覆盖”。新增but/粒子位置统计保留，GP/cue相同变化、targets固定。same-only让scope明确，不用E19不确定的separate读数宣称semantic failure。raw likelihood不是准确率，也未证明query下模型先恢复了。
- **决策表（跑之前写）：** 肯定对象最后时GP差大幅减小/符号改变且role控制有效 → “negated-last重新喂入旧association”解释增加，下一对照不提及被排除NP、同时控制否定/焦点；差仍保留且双向控制有效 → nearest mention不足，追源句repair/explicit事件身份绑定，不扩大模型；控制无效或事实标注有差异 → 查格式语言与不确定性，不包装能力；不同source不同 → 找反应结构，不筛source赢家。
- **算力预算：** 一张空闲H20，168新输入，预计≤.03 GPU·h。**实际：** 待运行。
- **命令：** 在workbench内source env；`late_role_evidence.build(... anchors=('same',),experiment='E20')`、`fact_order.py adopt`；`$IIR_PYTHON scripts/event_identity_infer.py --experiment E20 --data $IIR_CACHE/E20-material-preparation-v1/audited-v1.jsonl --out $IIR_CACHE/runs/E20`；`scripts/fact_order.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E20 --out results/E20-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行；I01 PILOT，C01/C02仍L0。
