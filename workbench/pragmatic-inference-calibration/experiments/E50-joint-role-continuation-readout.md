# E50：joint-role-continuation-readout（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2，E49同源readout边界
- **对应：** C02/P02
- **问题（一句话）：** E49的source选择预测与listener关系能在不要求填写概率的续接似然读数下保留，还是主要来自显式概率任务？
- **设置：** 完全同24源场景、三身份、三对象循环位置/三个speaker目标对象；不新增source、规范或人类标签。源四可用词固定；speaker补全“The speaker says: red.”等四完整表达；listener补全“The speaker was referring to Object 1.”等三句。bare含native BOS若存在/chat含native完整template与固定assistant prefill，Q3 no-thinking，OL共用SFT tokenizer。每入口432×bare/chat=864/model、同八endpoint6912 distributions。不是MCQ gold，不给probability list或CoT指令。
- **读数：** 主读数完整句尾period候选conditional likelihood（无EOS），secondary去period的词/数字content likelihood，完整多token非只首token。两读数均保存fullcandidate IDs/LP、绝对candidate mass与归一概率。原角色映回后复用E49 all-item group/identity/joint Bayes诊断，同source human norm；fullword模型概率并非透明knowledge，prefill是条件，不声称无prompt测量。主读数不按结果切换。
- **阳性对照：** E49源/actualtoken/human hash不变；prefix每candidate全量逐token精确相等，两OL实际输入完全一致。tiny候选microbatch右padding4与独立single全teacher forcing首末/两task/两入口：fullLP<.001、prob<.001、argmax相同，重复<1e-6。失败0科学预测并保存。无歧义12source各入口/身份≥.95 argmax floor，全部原item/位置保留。单token与多token按各自完整span，不靠默认rep penalty。
- **噪声地板 + MIE：** item bootstrap2000 seed0、rotation/候选非独立item；完整raw本地。独立teacherforcegate是仪器，不训练population CI；candidate mass弱时不归因能力。与E49只在映射后的同source分布比较，不用两种输出point score排行造故事。
- **混杂审计：** E49照片/练习缺失与派生speaker任务限制继承；native lexical/length/period prior均可能影响，content仅既定secondary诊断。固定prefill可能与native语境不适配，bare/chat全部报告；原candidate归一化不保证候选外无信息。Bayes诊断uniform prior是计算假设，不判LLM机制错。SFT/DPO不是isolated RLHF。这里是跨readout检验而非不断加指令救分，之后不能据某一个漂亮入口重复局部优化。
- **决策表（跑之前写）：** A两role控制成功且joint/身份条件结构跨两读数保留→候选关系仍须独立自然来源/nearest定位；B显式分配与续接不同或candidate mass极弱→readout解释、不升级；C无歧义失败→仪器/任务floor、不当能力negative；D所有端点结构符合parent或无新边界→保留成功/null，回到territory，不造机制。任何结果不自动关线。
- **算力预算：** 八独立GPU锁、FP32/noTF32、候选batch≤4，预计≤4 GPU·时；已下载模型、0training/API/judge/subagent。优先空卡，正在跑E49的OL锁后接入，不终止完整作业。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。已看到E49六endpoint完成、两个OL运行；未查看其source任务分数。E50动机来自跑前的metalinguistic局限与Hu/Levy/NMI读数压力，不伪装未知结果为预注册独立发现。C01/C02仍L0。

2026-10-03执行：八endpoint全864原prefix/两种候选span CPU逐token gate通过，OL SFT/DPO相同输入，suffix长度2–3token，不用首token代替。八作业进入GPU锁队列，已有E49作业不终止。数值gate先执行，尚无完成结果；各raw/run/config后续逐个核对。

2026-10-03完成：八endpoint各864、6912 distributions；全部原source/input/两span/独立完整model teacherforce/概率质量gate通过，匹配完整E49结果。common-chat full下六Qwen/Mistral端点各身份listener控制均36/36；OL SFT34/33/30、DPO32/31/29，不能共同能力归因。Q3-8 bare full adult−child−.01803 CI[−.03156,−.00344]，既定content+.00480[.00122,.00933]；Q3-4 bare/full+.02852[.01306,.04697]，chat/full−.06852[−.10856,−.02762]。这类方向反转先属于readout边界，不挑一个当科学故事。

更多限制：adult critical Q3-8 bare/full listener/speaker candidate mass .0322/.0091，bare/content .9974/.5166；chat/full speaker极低，不能用归一化posterior宣布模型内部Bayes不一致。full为主content不替换；全部24source/三rotation保留，不过滤能力正确材料。结果：results/E50-joint-role-continuation-summary.json。按决策B记录instrument/readout解释，不继续局部加prompt。C01/C02仍L0，没有成熟paper claim。
