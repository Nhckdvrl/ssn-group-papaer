# E02：训练端四条件发现pilot

**结论：conditioning杠杆有效，但没有形成值得升级的终点迁移主张。**
同起点MWB、同任务recipe、seed17，仅一联合CPT/适配seed；不是预训练重复或论文idea。
实验卡 `experiments/E02-reusable-bridge-task-learning.md`；完整数字、输入hash、paired-item与promptID cluster CI见 `e02_learning_analysis_seed17.json`。

| 条件 | CPT后DE conditional NLL | EN/DE@2048 | EN/DE@8192 | EN/DE@32768 |
|---|---:|---:|---:|---:|
| new_paired | 1.589 | 58.80/56.05 | 78.50/71.96 | 82.85/77.74 |
| new_split | 2.245 | 60.80/55.21 | 77.68/72.67 | 82.69/78.40 |
| reused_paired | 1.556 | 50.82/45.95 | 78.40/71.04 | 82.91/77.72 |
| reused_split | 2.162 | 44.45/36.79 | 75.41/70.68 | 82.85/77.45 |

NLL初始均3.43979；同文本mask阳性控制通过，四CPT loss均下降。NLL是双语条件预测诊断，不是reasoning证据。

终点DE contrasts，pp，paired-item95%CI：

- new paired−split：−0.66 [−1.40,0.12]。
- reused paired−split：+0.28 [−0.40,0.98]。
- new−reused paired：+0.02 [−0.60,0.64]。
- new−reused split：+0.96 [0.18,1.76]。
- coverage×conditioning：−0.94 [−1.96,0.04]。

CI条件于当前单seed，不代表训练分布；不把某项跨零当等价，也不把一项区间不跨零当新发现。
终点EN contrasts均很小（−0.16至+0.16pp）；DE split覆盖差尚不足以单独承接母问题。
早期new−reused split的DE+18.42pp伴随EN+16.35pp，paired差DE+10.10伴随EN+7.98；
coverage×conditioning早期EN/DE约−8.36/−8.32pp。这首先是内容暴露影响源语学习的读数，
不能挑早期快照包装为跨语言机制；完整曲线和初始随机头读数保留。

后果：不优先扩展同一NLI四格寻找小显著差异。保留四个完整LM CPT资产，
继续E03真实生成式学习；若第二任务出现有实践后果的瓶颈，再为独立训练干预注册，
不因本pilot关闭领域，也不预写桥接复用成功/失败故事。

边界：new是已选监督实例的无标签EN/DE文本，不是新预训练知识；reuse是同源MT、同领域但内容不重叠。
语言loss token差<0.1%，未固定独立信息量或有效attention FLOPs。split是固定输入/位置的文档隔离，
不是所有ordinary unpaired corpus组织。只有一base checkpoint；后续task dev继承已披露的premise重叠。
零CPT MWB17只作锚点，不是等预算方法。

资产：`artifacts/bridge_learning/{condition}_seed17/checkpoint/`是完整CPT LM；
后续 `artifacts/nli_learning/train_e02_{condition}_seed17/`仅分类backbone/head，不拿它评翻译遗忘。
