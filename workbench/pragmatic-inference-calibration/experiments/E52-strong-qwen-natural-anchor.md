# E52：strong-qwen-natural-anchor（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2；E51的独立较强family anchor
- **对应：** C02/P02
- **问题（一句话）：** E51的自然含义区分是否只是OLMo dense谱系的局部行为；Qwen2.5-14B的匹配Base/Instruct如何改变相同原人类规范和原回答pair？
- **设置：** 已下载原Q25-14 Base/Instr pinned revision，完整Instr共同tokenizer。IQAP/Circa完全复用E51的源及E33/E34的原prompt/候选，两stage×两source四独立单卡，FP32/eager/noTF32、single sequence，4064 distributions；没有新增source或annotation，不筛模型正确项。写卡前未见本pair在两source的结果；E41/E46其它task结果已知，不冒充完全独立发现。
- **读数：** E51相同主/secondary、完整绝对candidate质量、IQAP null词汇prior、human分布及polarity；Circa原八选项全概率和正逆序、同问题原回答pair，不混成speaker certainty或因果单变量操纵。两模型差以原item/question paired bootstrap2000 seed0，另IQAP source-cluster；两endpoint非training seeds。
- **阳性对照：** 两native完整tokenizer backend、vocab/special maps逐项完全相同，原source/hash/human字段及完整candidate prefix全量检查；首末/每入口/每order独立完整model logits教师强制，LP<.001/prob<.001/argmax一致，repeat<1e-6；全部context长度低于本model limit、无截断。继承原一句格式要求，不给恢复能力的新指令。
- **噪声地板 + MIE：** 数值gate与task metrics分开；完整source估计/CI/候选mass/order/terminal都报，不用低概率候选的归一化高分解释知识。两个family的可用source相同条件关系才可讨论跨family；单个漂亮入口不追加救分。
- **混杂审计：** native Base套chat只是匹配入口；Base/Instr算法/data联动不能纯RLHF归因。原human选项非唯一真实intent、Circa共问题两回答改变语义与难度，不能作FPR gold。四作业全报告；不选幸存seed、readout或材料。暂无novelty claim，generic post-training/calibration变化已有ownership。
- **决策表（跑之前写）：** A与E51同一条件关系且质量可用→保留边界待独立交际条件预测；B与OLMo不同→family边界，不剪掉失败family；C只有mass/位置/terminal改善→elicitation，不升能力；D全部接近human或无稳定结构→报告成功/null、回territory。无自动关线/升状态。
- **算力预算：** 已缓存权重无新下载，四独立GPU锁，预计≤3GPU·时，0training/API/judge/子agent。E51仍等固定权重，锁协调不杀任一作业。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

尚无实验结果；先完整CPU预检，再数值gate，输出raw/config本地且不覆盖。

2026-10-03开GPU前CPU修正：首次gate发现Qwen Base与Instr完整backend/vocab相同，但native EOS角色不同（endoftext与im_end）。0GPU预测，原失败SHA保留data/E52-first-preflight-failure.json；不冒称special-map全相同。所有入口明确使用共同Instr实际IDs与terminal，以保证controlled matched input，native角色分别保存；Base的非native terminal可带来低candidate质量，必须独立报告、不能因归一分数归因能力。仅修正错误的asset等价假设，source/prompt/readout/numeric gate不变。

CPU全量prefix/source preflight已通过；完整source结果不按方向改readout。Circa全部单token content时作精确共享prefix分解以减少重复forward，再与独立完整model logits比对，不用首token代替多token。运行脚本冻结，所有原失败/raw保留。

四作业已实际GPU0–3计算，所有首末/各入口/order独立完整LP数值gate通过；IQAP300/model、Circa1732/model，结果尚未全完成。

完成4064，四作业全部原source/input/backend/fullcandidate/numeric gates通过，结果results/E52-strong-qwen-natural-summary.json。IQAP chat/full polarity .6133→.8467，paired+.2333 CI[.1467,.3133]；四类Brier .32078→.52921（越低越好），paired+.20843[.13429,.28723]；human definite .56333，Base/Instr对应phrase probability .46588/.25656。这是固定forced interpretation读数，不是speaker certainty或模型内在confidence。

必须同时报告：Base chat/full candidate mass8.04e−13、Instr .99703；Instr无QA null已将probable-yes置.99697，绝不能把Brier差单独解释为语用能力/校准变化。Circa原序chat条件弱回答correct .796875→.9765625、相对条件变化+.42729 CI[.37916,.47401]，但负强度原序弱correct .1154、逆序.8462；顺序依然强混杂。原全部order/source保留，不追加strict或换metric救故事。按决策B/C记录质量/elicitation与边界；C01/C02仍L0、0成熟贡献。
