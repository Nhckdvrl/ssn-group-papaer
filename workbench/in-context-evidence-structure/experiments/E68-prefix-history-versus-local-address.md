# E68：答案前缀收益来自局部地址，还是先前样例计算的复用？（2026-10-10）

- **状态：** DONE
- **类型：** PILOT（承接E67，非找到prefix就宣称novelty）
- **对应：** C09/C15/C16，P12/I04；E67同最终标签的编码效应。
- **问题：** 保留demo当前input/source/code、位置及原生label KV，只移除生成前缀状态时对之前demonstrations的访问，会否使来源条件化收益消失？
- **为什么现在：** E67独立确认matched accuracy+0.074、source排序+0.109，但label-only KV只移植约0.083的固定Q格式gap；K-only接近0。不能把收益解释成label-key修复。Cho shortcut提供更强解释：后续demo的forerunner已复用先前判断。与“只是局部prefix address/induction”需要正面竞争。
- **设置：** Qwen3-8B冻结bf16/eager，同revision/conda，无训练。32-context发现seed68001 animals/fruits yes/no，64-context独立确认seed168001 occupations/vehicles toxic/safe仅在pilot对照有效且主要effect≥MIE时跑；E67的metadata/answer code相同token多重集设计，随机code permutation独立于orientation。
  - 两layout native prefixes D0/D1。label-flip donor仅翻转各demo最终label，不改input/source/code/query；全prefix flip为rule响应阳性。
  - **历史隔离donor：** 对每个demo的所有receiver token，只允许读取header和该demo自身因果前缀，禁止任何以前demo。全4D causal mask保留原位置/RoPE/文本/频率；header本身普通causal，不含demo信息。不是删除tokens或压缩位置。
  - 原生D1 recipient中只移植isolated donor的`answer prefix` K/V/KV，所有label-anchor KV仍是native；比较Tag、source位置及label-anchor KV。另以D0为recipient移植nativeD1的prefix K/V/KV、Tag KV、prefix＋Tag KV、prefix＋Tag＋label KV、全prefix，Q0/Q1均跑。保留所有组合，不能挑最有效site。
  - **历史内容反事实：** D1 label-flip donor的prefix K/V/KV移植至nativeD1，query恒定；own label在prefix之后，不能影响它。first-demo prefix在native/label-flip donor之间逐位相同作因果检查；isolated donor前缀在label-flip前后**全部**逐位相同作历史隔离检查（不见此前/自身label）。
  - full explicit 4D causal donor与native内置mask完全匹配；all-cache swap输出恢复donor。捕获原生attention检查isolated每个demo对其它demo的质量=0。
  - native一句指令、single-source参照在E67已建立；本卡保留这两对matched参照，以新seed复核任务可识别性。全部query和seed保留，不按正确性挑选。
- **读数：** correct margin、accuracy、同input source排序；isolated-prefix替换相对D1 native的差、相对D1−D0 matched gap的损失比例（gap>0.2nats才用）；label-flip prefix响应相对自然全prefix flip，及site/donor transfer的绝对读数。context bootstrap4000，始终同时报告margin/accuracy/ranking。
- **阳性对照：** 4D full causal=no-op≤0.10nats；first prefix flip差=0、isolated所有prefix flip差=0、跨demo attention质量=0；full donor恢复；label-flip自然响应>0.2nats；matched token多重集/位置/labels空间不变。一句指令single不是上界。
- **噪声地板 + MIE：** E67完整swap/self误差0；本卡重新核对。isolated-prefix移除≥0.5的margin格式gap、并使accuracy或source排序下降≥0.05且CI不跨0，才进入历史依赖确认；prefix label-flip转移≥0.3自然响应、CI不跨0为历史内容载体线索；不能用一项大margin声称能力消失。
- **混杂审计：** isolated patch保持native label evidence/currentdemo raw input/source，切断此前labels与其它此前demo共同变化，未仅隔离label历史；prefix-state变化可能是context normalization/分布移位，不唯一等于task-state消失。native label-flip donor可分别约束label-history。全层high容量KV，不称独立单向量；prefixK改变查询相似度不等于新head；比例非可加。信息等价是任务三元组和token多重集，语法角色操纵正是变量。
- **决策表（跑之前写）：**
  - isolated-prefix损害matched收益、label-flip prefix有强响应 → 历史计算在非label载体中有具体线索，与Cho shortcut比较source分区及新布局预测，不称“首次发现”递归。
  - isolated-prefix不损害收益、label-flip prefix弱 → 主要局部address/当前语义；不追可复用task state，考察literal-prefix匹配边界。
  - 原生D1 prefix移植可转移、isolation令转移/表现变弱 → 非label carrier参与，但先区分local address与history。
  - nativeprefix移植不足或Tag主导 → 改变定位；不能强保answer-prefix解释，检查query语法/通用格式一致性。
  - 只有margin/attention变化、accuracy/ranking不变或数值控制失败 → 不升级科学主张，修harness/保留bounded结果。
- **算力预算：** pilot≤0.4GPU·时，确认≤0.6；实际待填。关键结果串行，非blind Cartesian扫配置。

## 结果
待运行。

### 结果（2026-10-10）
- 发现32/独立确认64完成；所有no-op/full-mask/full-swap差0，native first-prefix flip差0，isolated所有prefix flip差0，禁止跨demo attention质量0。
- 确认matched gap margin0.576[0.480,0.668]、accuracy+0.094[0.059,0.137]、source排序+0.078[0.016,0.141]。仅把D1原生prefix K/V/KV换成isolated，分别移除68.1%[56.2,79.9]／74.7%[54.6,92.5]／70.1%[51.8,85.6]的格式margin gap；KV accuracy−0.078[-0.113,-0.047]、source排序−0.133[-0.195,-0.070]，支持history-dependent上下文化的必要性，未证明其内容。
- **替代解释约束：** label-flip donor的prefix KV只转移原生full-rule-flip效应0.013[-0.007,0.034]；V0.017[0.000,0.033]，远低于预定0.30。因此不支持前缀已存先前完整标签判断的当前版本。
- 原生D1 prefix单独移植至D0Q1只转移0.033[-0.053,0.112]固定Q格式gap；prefix＋Tag KV0.675[0.554,0.815]，再加label KV0.808[0.729,0.895]。联合carrier有作用，不能把prefix单个位置当充分状态；确认accuracy恢复幅度较小，ratio不是可加份额。
- **决策：** 存在历史依赖，但label-history解释不足。进入E69保留unlabeled结构的对照，避免把必要性等同task-state内容；再用E70检验公共context offset/状态失配。C18候选仍L1，没有命名新shortcut机制。
- 资产`results/e68/qwen3_{discovery,confirmation}/{run,analysis}.json`；实际164.96秒=0.046GPU·时。
