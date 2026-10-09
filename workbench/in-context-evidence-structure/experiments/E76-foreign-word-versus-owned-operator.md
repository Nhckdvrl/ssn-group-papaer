# E76：答案词仅出现在其它来源，自己的熟悉运算能否决定答案？（2026-10-10）

- **状态：** PLANNED
- **类型：** PILOT，独立于E75任意函数空间gate；本卡先测行为基础，尚无word/relationship内部因果结论。
- **对应：** I04/C09/C15/P17；来源条件化与熟悉运算的组合。
- **为什么现在：** E74任意label函数在raw下未有效执行，不能据此定位来源组合。改用预训练熟悉的±1运算，仍由demo确定各source采用哪个运算；正确词仅在foreign demo标签中出现，给word来源/关系来源一个便宜的阳性基础。不是首次发现ICL加法（E19及大量近邻已有）。
- **设置：** Qwen3-8B float32/eager、conda verl-clean、GPU0；32contexts seed76001，sourceA offset±1×query q∈{3,4,5,6}各4contexts完整平衡。Alex/Sam/Chris/Dana对应A/B/C/D，offset为[b,−b,−b,b]，input为q−2/q+2，每source×input两records，共16随机混排。
  - query q在所有sources都未出现；SourceA/B正确输出q±1从未在自己的labels中出现，却在相反offset的foreign source真实label里出现。输入只含q±2，header只声明±1，所以正确词不在任何input、query或任务候选列表中，只在foreign labels出现。模型可以自行算出词，不因此预设必须copy。
  - 全12 source×input query；A/B的中点query为主读数，8已见input为正控，C/D中点另报。四候选数字q−3/q−1/q+1/q+3，精确continuation logprob；模型prompt不列候选，即时choices，不称自由生成能力。token校对见末节。
  - base、scope_swap（A/B换offset）、owned_a（A/C换）、owned_b（B/D换）、foreign_swap（C/D换），均为真实±1函数、全局label/token频率/位置相同。comp_a只换C、comp_b只换D用于补偿-only，频率变化有意保留、不可混称matched。
  - header声明每source独立固定±1规则；默认与加E74同一句Source scope指令（R8）。不提供source offset表/答案，保留所有contexts。
- **读数：** 候选margin/accuracy，8 seen controls与A/B、C/D novel分开；Ψ=[lp_A(tA)−lp_A(tB)]−[lp_B(tA)−lp_B(tB)]，同步response Ψ_base−Ψ_swap。正确source运算预测正号，固定非负source-matched label支持预测负号；该简化account不是所有label-anchor理论。owner-minus-comp同方向、untouched-source及foreign响应保留。4000context bootstrap seed760。
- **阳性对照：** exact整数oracle逐query、32格平衡；missing输入/owned正确word缺失及foreign实际出现；全局token频率/标签位置不变（comp例外）；seen≥.90；重复cache no-op≤.10nats；source/model/config/hash与完整32×7×2×12评分。
- **噪声地板 + MIE：** no-op≤.10；至少一个指令条件seen≥.90且A/B novel accuracy≥.80，signed response≥1.0nats、CI不跨0，才获得有效source-owned运算基础；反方向≤−1且CI不跨0只提供有界默认支持检索线索。独立确认需新名字/数字范围及未使用材料，不能把本pilot称已证计算规律。
- **混杂审计：** 算法来自预训练熟悉算术，参数由context选择；区别task retrieval与arbitrary-function learning，不能从比E74好说明唯一source机制。四候选选择不是端到端；位置/频率matched但owned/comp交互可非线性；高准确率不证明foreign word被实际copy。局部±1任务与source-based语义分类不同，不反推E46不存在干扰。
- **决策表（跑之前写）：**
  - 运算准确、source响应正确 → 熟悉运算可与来源组合；可设计word读出与关系使用的分离干预，仍不能以behavior证明copy路径。
  - seen好、novel差 → 新函数执行/Source组合未获得有效阳性；先看单源/熟悉运算对照，不能宣称“凡输出不在source就不能推断”。
  - Source一句恢复 → 策略/接口边界；不称能力缺失。
  - foreign关系变化显著影响正确Source → 优先关系混用解释；不继续将foreign contribution称合法词实现。
  - 无MIE或控制差 → 不铺后续patch，不用更多seed救故事；所有结果保留。
- **算力：** 本地GPU0空卡，E75在GPU1独立回答任意函数空间问题；8B已在NVMe，预计单卡3–8分钟、float32无需训练。只行为pilot，关键结果未回不并行下游。
- **产物：** scripts/e76_operator.py / scripts/analyze_e76.py，小run/analysis JSON入git，behavior/layout留本地；依卡复现。
- **定位：** 已有E19/global transform、Cho shortcut/denoising、Test-then-Route predicate/word分离、Mixing Mechanisms指针/词以及Competition of Mechanisms读取/采用区别。潜在增量仅为来源内新参数的操作与foreign word carriers的具体因果边界；当前未证明，不能泛称新组合瓶颈。

## 科学打分前tokenization校正
首次启动在数字token断言处失败，0条科学评分，保留`results/e76/qwen3_operator_invalid_candidate_tokenization/`与日志。Qwen数字本身1token，但带前导空格是[220,digit]两token；误假设与英文标签一样。修为精确p(space|prefix)+p(digit|prefix,space)，四候选共享space，所有主差分/margin/排序中的公共space项自然抵消；不换任务/seed/门槛。数字anchor位置改记space后的digit。原程序已终止后再改，E75及其依赖未修改；不是看科学结果后调整读数。
