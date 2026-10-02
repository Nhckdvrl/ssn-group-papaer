# E30：E29两项跨batch超门槛的有界校对

- **状态：** DONE
- **对应：** P04；E29读数可比性，技术校对而非scientific claim
- **问题（一句话）：** 相同原knowledge输入的.0023/.00295概率差，来自源材料/编码变化，还是组成不同的FP32 batch？
- **设置：** OLMoE SFT/DPO原SHA，原784prompt与360knowledge子序列的batch8；源全360knowledge输入CPU逐token原echo-prefix/直接encode对照（已通过）。GPU只校对两已失败key，加固定首末knowledge key，各bare/common-chat；batch1重复、源原mix batch8、E29 knowledge-only batch8；保持同原prompt、FP32/noTF32，不调门槛、不挑新科学样本。两个独立GPU5/6。
- **读数：** 每key P(Yes)、support mass、各组成与batch1概率差，重复单例一致性及input SHA；两个失败case是POST-HOC触发的debug case，不用于总体科学效应估计。
- **阳性对照：** 重新读取原source与raw prediction；各组成内目标prefix字节/IDs相同；首末控制；重复batch1。
- **噪声地板 + MIE：** 原.001门槛保持；不以漂亮effect放宽。已有E29 SFT/DPO裸入口仍隔离。
- **决策表（跑之前写）：** A同IDs不同batch复现→数值敏感，E29 affected入口不可当精细效应；保留，必要时完整single-item另卡，不局部替换原坏行；B单例也不稳定→暂停该数值接口解释；C编码不同→实现bug，隔离原读数；D不复现→不确定，原超门槛仍保留。任何结果都不升级pragmatic finding。
- **算力预算：** 2卡≤10分钟、各4key×2入口×4组成，無下载/训练/API。其余槽让位E28等待完整权重。不能为占卡重复baseline。

## 结果
先写卡，未运行。

完成：CPU全360knowledge同字节/IDs，GPU固定debug case复现SFT .002338/DPO .002949的组成差，single-repeat一致；首末控制仍通过。结果results/E30-numerical-boundary-summary.json。确定batch数值敏感，尚未定位具体kernel/router机制；原两个E29裸入口继续隔离，不以新单例替换旧行，不升级科学主张。
