# E21：点名排除、泛指排除与最简排他句（2026-10-05）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** I01/P10；E20最后对象变化仅部分消除history，继续追why。
- **问题（一句话）：** 同一排他事实中，把已否定的原患者再次点名，会比泛指排除或只说only正确对象更强地维持GP旧关联吗？
- **设置：** 原7episodic sources×2NP×GP/comma×2role事实×minimal/generic×3targets=336新输入；continued-same，复用E20 named168。同frozen pinned Qwen3-8B FP32/SDPA、seed0/batch4、TF32=false、raw text无question/chat/instruction。all/eligible/acceptable/facts-preserved∩clear-scope，option0/1/both，每source报告。两个new style使用同独立审核交集cohort，不能按各自更好结果筛source。
- **材料：** 仅late role句：minimal保留only X、去冗余Y；generic保留not generic-Y but only X，肯定对象最后，去具名Y；S1/same桥/S2目标完全保留。reference-only的原Y均2词，generic用2词anyone/anything else，精确同词数且同not/but/only框架；initial-only中himself→泛指2词会+1词，单独记录。minimal更短，仅作辅助不能隔离纯mention因素。field-v1 generic错误换成onlyX and nothing else，运行前v2保持原结构；v2构作中24条新增baboon/were语法错被独立review发现，v3仅were→was修复，312句原文一致、24句单独独立重审。旧版本/全部原因保留，任何E21模型之前完成。
- **独立审计：** 两Luna各192/144完整rendered审核，变换事实/only scope/原episode/grammaticality/selection；v3 changed24由原独立reviewer重审并合并，未变化312用原hash/标注。不由parent确定gold，全部semantic_gold=null；raw/licensed文字留cache/E21-material-preparation-v1，只hash/stat进git。
- **读数：** R=bits(own NP)−bits(ref)，M=bits(other NP)−bits(own NP)，每named/minimal/generic与role事实报告GP/cue、D=GP−comma。主generic-minus-named的D，尤其reference-only严格length/order matched；minimal-minus-named及generic-minus-minimal辅助，不能以缩短句子证明点名效应。双向role-evidence阳性控制每style/GP/cue全部报告。两个NP先source内平均，paired bootstrap10000/seed20261005/95%CI和每source。
- **阳性对照：** E20 named ref-only history R−3.40 [−4.28,−2.44]，双向role控制GP+9.56/cue+9.39bits；新两style也应能区分role事实，若不起作用只谈语言/读数不适用。3targets causal pre-token相同；HF/manual loss核对，原E20冻结/hash复用。
- **噪声地板 + MIE：** FP32词级漂移≈1e−5bits；n7/sample CI为主要噪声，无任意效果gate；整体已偏允许对象不能把任何非零D叫全体失败。
- **混杂审计：** reference-only generic与named只把2词具体NP换成2词泛指，仍改变指称/强调，这是要区分的语言动作；不是某神经机制的隔离。minimal省掉句词、initial-only generic长1词，报告长度/语义flag、不得用辅助alone证明因果。all输入都评分、faithful层事前独立定义；不看结果修数据/换synonyms。negated概念的可及性已有psycholinguistic近邻，novelty不能只命名为CIE。
- **决策表（跑之前写）：** 同长度generic使history明显变小且role控制有效 → 具名否定刷新association解释增加，检查原谓词重现/role dependence与独立现成source；minimal/generic都仍保留D → 点名刷新不足，转源句repair或具体事件身份绑定控制；只minimal变小 → 长度/删除框架仍竞争，不宣布named effect；control弱/事实有差异 → 限定instrument，不扫prompt/models；source反向 → 找结构，保留全source不挑赢家。
- **算力预算：** 单空闲H20，336新inputs，预计≤.03 GPU·h。**实际：** 待运行。
- **命令：** workbench内source env；`scripts/exclusion.py build/adopt`；`$IIR_PYTHON scripts/event_identity_infer.py --experiment E21 --data $IIR_CACHE/E21-material-preparation-v1/audited-v3.jsonl --out $IIR_CACHE/runs/E21`；`scripts/exclusion.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E21 --out results/E21-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行；I01 PILOT、C01/C02仍L0。
