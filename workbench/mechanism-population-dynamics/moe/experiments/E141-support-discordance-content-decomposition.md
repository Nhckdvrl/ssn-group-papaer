# E141：实际贡献变异来自支持差异还是共同调用时的计算（2026-10-26）

- **状态：** DONE；三组完整replay、独立NumPy审计通过；原预登记保持。
- **类型：** MEASUREMENT；无训练、无新匹配、无支持外expert查询。
- **对应：** P28/C09：E139实际分量同时含mask/门值/内容，2.32倍变异不能直接叫内容差；P27/E140检验选择与维持，二者不相互替代。
- **问题（一句话）：** 锁定原cal对应后，观察到的贡献变异有多少落在只调用一方的输入，有多少发生在双方实际共同调用时？

## 设置与锁定对应
- 只用原Dolma held262144位置/512序列/32文件，原native H cache与B16×512完整gate/selected子batch，沿E137 native_trace真实BF16乘积。此次不扩POS，原A不是新前置条件。
- 预定free R（E135/E139）、fixed F（E136/E138）、warmstart trainable T（E140）各三学生最终4096；全组全pair全64保留。R/F已完成，T尚训练中，不根据结果删/换组。
- 只用各组原training Hcal8192 final maps到seed1；R/F引用E139，T须等E140原final cal完整后按原规则引用，不在held重新匹配/改尺度/旋转。映射只是数据轴重标，不物理重排参数。
- 可先运行已具完整proof的R/F，再等T原终点补齐，明确partial直至三组完成；冻结同一源码/独立additive ledger，不为partial结果追加条件。新replay是旧raw未保存所需mask分区能量/f向量，不能仅由原cohort variance重建。

## 主读数：全held精确分账
- 对每个已匹配expert和学生对(s,t)，实际分量`c_s=actual BF16(w_s*f_s)`，未被选则0。将`||c_s-c_t||²`精确分为support XOR上的单边`||c_selected||²`，及both-on上的`||c_s-c_t||²`；both-off为0。
- 三对SSE之和/9重建等权三学生cohort variance；所有per-sequence×expert×pair count/energy/两项SSE及完整总项保留。与原E139/E140同群体原始pairSSE/variance逐项核对，是程序阳性参照，不是科学绩效门槛。
- 报全held每位置单位的两项与组差，及paired file-cluster 1000次seed141输入CI；非seed处理效应CI。`ΔV=ΔV_XOR+ΔV_both`中both项可为负，XOR组差可超过总组差，不强行解释成0–100%的知识比例。
- fixed final相同物理gate/identity映射下XOR=0是结构参照，不单独认领新发现。不同组both-on群体不同，覆盖/count必须并列，不把条件群体误差外推总体。

## 辅助：共同on的实际内容/门值
- 仅在两方当前实际共同on处，读取原生selected forward已算出的BF16 `f_s,f_t,w_s,w_t`，不查询任一未选expert。
- 在FP64中对同BF16值的理想乘积精确拆 `δ(wf)=δw*(f_s+f_t)/2 + (w_s+w_t)/2*δf`，报告gate项/content项平方范数、二者cross及恒等残差；另列actual BF16乘积delta与理想乘积delta的floor，不把平方项直接当内容占比。
- 保留共同on原f的能量/SSE/dot与明确的pooled cosine（zero energy记未定义，不删expert）。它只描述该共同调用人口的向量方向/尺度，不命名语义算法，不解决gate–content尺度耦合或支持外函数。
- 所有参数/源/输入/映射SHA与native full-row程序核对，不改E139/E140源、已有raw或旧分数。

## 阳性对照、噪声地板 + MIE、混杂审计、决策表（跑之前写）
- CPU手算：纯support不同且共享f→差异只落XOR；相同w不同f→共同on content项；相同f不同w→gate项；负cross/零覆盖/非自逆映射；pairSum/9双恒等式；copy差0。真实BF16 product floor与统计F64舍入单列，无人为MIE/拟合门槛。
- XOR归属不是替换mask的因果效应，锁定matcher不穷尽对应；不同both-on群体的选择效应保留。当前on不代表完整训练历史on，off不代表从未训练。
- 若额外变异主要落在XOR→主动收窄为本对应下的分配重现性差，不补off-query维护内容故事。
- 若共同on仍有内容向量差→只支持该人口中的输出内容差，结合gate项/尺度/覆盖/函数距离解释，不称严格同函数或语义分工任意。
- 若混合或方向相反→全报连续分账，不加匹配/中心化/指纹网格。C09原actual-component事实保持，解释可收窄；不自动开关线/升论文状态。
- **算力预算：** ≤900 GPU秒，独立E141 ledger分阶段加总；R/F可用fvcrc21空闲GPU3与E140三训练并行，总4卡/全探索≤8，T原终点及映射齐后再补。全部read-only/NVMe，充分统计而非完整巨量向量归档。

## 结果（运行后追加）
- 尚未新replay；这项是看到E139后提出的新前瞻构念测量，不回写E139主读数。

### 完整结果与独立审计
- source SHA `9aa007be4c1dbaa50967f74010adf4a16ad75b71b84890942d8dbf11e7eb48a2`冻结，R/F六CP/原cal/H/metadata CPU预检与独立源审通过；04:27:11UTC GPU3 PID890176先采R/F；T原E140全stage complete后，以真实完整readout/CP/maps descriptor于04:33:48UTC GPU3 PID892020补齐，未改源/重匹配。实际56.124250GPU秒，两成功作业，ledger独立。
- `results/e141/support_partition.json`全三组complete/errors空；同pairSum/9单位的total=XOR+both：free .072467196=.024964044+.047503152；fixed .031208956=0+.031208956；warm .032817626=.000539825+.032277800。
- free−fixed：total +.041258240 [paired输入file CI .040007464,.042968630]，XOR +.024964044 [.024007163,.026203285]，both +.016294197 [.015436917,.017557111]。差异同时分布于support-discordant与共同调用处，不仅是编号或调用位置；不是mask干预的因果份额。
- warm−fixed：total+.001608670 [.001326436,.001951853]、XOR+.000539825 [.000503402,.000585989]、both+.001068845 [.000810791,.001374134]；warm−free对应−.039649570/−.024424218/−.015225352，完整paired区间在summary。输入CI非seed总体，不能把比例叫知识百分比。
- 共同on raw f pooled-cosine三pair：free .605002/.591669/.610597，fixed .755460/.755131/.754437，warm .716241/.715877/.717233。每位置共同on slot数free4.7341/4.1337/4.8449，fixed8/8/8；不同条件人口与gate/内容尺度耦合完整保留，不外推所有expert函数或命名语言算法。ideal gate/content平方项cross与actual BF16 floor全保存，不把平方项当加法内容份额。
- `independent_audit.json` SHA32341995…9de36be，由非作者独立NumPy复算，不导入主统计/不用GPU；可复跑`e141_independent_audit.py`。全512×64×3 raw、105global/1000draw CI、每组192 expert-pair表、3paired contrasts、计数/分账/对称分解/floor均闭合，旧pairSSE最大差5.7e−14、cohortVar9.8e−15，pairedCI误差≤2.1e−17；固定XOR严格0。保留全64与未定义零能量，不筛列。
- C09仍为actual-component有限cohort事实，E141补充其变异同时包含支持差和共同调用向量差；不升级为严格同函数/所有输入的纯内容自由度。原E139/E140分数及源保持。
