# E131：大小模型上的同一形成、操作和Source功能链

PARTIAL：13/18个预定stage完成。发现n16与新确认n32分别展示；大小配对只用逐字相同的新32材料。未完成的stage不作结论。所有继承分析、条件与三通道保留，报告不拟合模型。

## 形成与固定系数反事实

| Model / phase / n | A形成signed nats | A形成absolute nats | B读取signed nats | stage signed交互 | label B0 KV raw r | RMSE / zero | rule双差r | 固定word答案关联absolute |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3_confirmation_mechanism / 32 | 2.3511 [1.8571,2.8365] | 2.1907 [1.7068,2.6819] | 3.9871 [2.7275,5.2542] | 0.9826 [0.4523,1.5276] | 0.92322 | 1.02146 / 2.59441 | 0.91999 | 0.3330 [0.2151,0.4670] |
| qwen32_discovery_mechanism / 16 | 2.8006 [2.0147,3.6204] | 2.8006 [2.0147,3.6204] | 3.1404 [1.8829,4.4817] | -0.0319 [-0.7191,0.6965] | 0.86750 | 0.90072 / 1.73944 | 0.93875 | 0.2211 [0.0430,0.4406] |
| qwen32_confirmation_mechanism / 32 | 2.6756 [2.2658,3.0956] | 2.6756 [2.2658,3.0956] | 3.4846 [2.5956,4.3480] | -0.0366 [-0.5250,0.4620] | 0.88283 | 0.86448 / 1.85657 | 0.92213 | 0.1839 [0.0974,0.2830] |
| llama_confirmation_mechanism / 32 | 0.8005 [0.6328,0.9768] | 0.8005 [0.6328,0.9768] | 3.0550 [2.7607,3.3462] | 0.5283 [0.3294,0.7339] | 0.82396 | 0.28136 / 0.48711 | 0.93973 | 0.1054 [0.0702,0.1419] |
| llama70_discovery_mechanism / 16 | 0.9931 [0.6121,1.3725] | 0.9931 [0.6121,1.3725] | 2.8291 [1.9676,3.5542] | -0.3517 [-0.7559,0.0359] | 0.54212 | 0.63233 / 0.70481 | 0.64207 | 0.2366 [0.1165,0.3683] |

## 原生操作：相同路径在不同读取环境

| Model / phase / n | Full-source答案移除signed | Full-source受限恢复signed | A-only受限恢复signed |
|---|---:|---:|---:|
| qwen3_confirmation_native / 32 | 1.7618 [1.2639,2.2944] | -0.6499 [-1.2695,-0.0803] | 2.1433 [1.4259,2.8926] |
| qwen32_discovery_native / 16 | 1.8158 [1.2704,2.4089] | -0.8221 [-1.2109,-0.4300] | 1.0852 [0.6022,1.6600] |
| qwen32_confirmation_native / 32 | 1.9720 [1.4671,2.4996] | -0.5445 [-0.8327,-0.2761] | 0.7751 [0.3213,1.2839] |
| llama_confirmation_native / 32 | 0.8590 [0.6633,1.0846] | -0.2754 [-0.3933,-0.1551] | 0.9867 [0.6792,1.3030] |

## 真实文本两Source函数：shared词表、两Actor平均candidate/full

| Model / phase / n | Native candidate/full % | Targeted candidate/full % | targeted−native full pp | targeted−all full pp | query-only−native full pp |
|---|---:|---:|---:|---:|---:|
| qwen3_confirmation_function / 32 | 84.4727 [81.9336,87.0117] / 84.4727 [81.9336,87.0117] | 92.0898 [89.2578,94.5312] / 92.0898 [89.2578,94.5312] | 7.6172 [5.1758,9.9609] | 17.1875 [14.6484,19.5312] | -2.5391 [-6.5430,1.4648] |
| qwen32_discovery_function / 16 | 86.9141 [83.7891,89.8438] / 86.9141 [83.7891,89.8438] | 95.8984 [93.5498,98.0469] / 95.8984 [93.5498,98.0469] | 8.9844 [5.8594,12.5000] | 21.0938 [19.3359,22.6562] | 8.7891 [5.4688,12.1094] |
| qwen32_confirmation_function / 32 | 87.9883 [86.2305,89.7461] / 87.9883 [86.2305,89.7461] | 95.7031 [93.5547,97.3633] / 95.7031 [93.5547,97.3633] | 7.7148 [5.7617,9.5703] | 20.4102 [18.1641,22.3633] | 5.8594 [4.1992,7.5195] |
| llama_confirmation_function / 32 | 79.6875 [77.9297,81.4453] / 79.6875 [77.9297,81.4453] | 88.5742 [86.0352,90.9180] / 88.5742 [86.0352,90.9180] | 8.8867 [6.5430,11.1328] | 13.3789 [10.9375,15.8203] | 18.1641 [16.2109,20.0195] |

## 新32材料的大小配对差

| Family / stage | Fixed readout | Large−small [95% paired context CI] |
|---|---|---:|
| qwen32_mechanism | A_formation_signed | 0.3245 [-0.1499,0.8107] |
| qwen32_mechanism | A_formation_absolute | 0.4850 [0.0257,0.9453] |
| qwen32_mechanism | B_reading_signed | -0.5025 [-1.1608,0.1605] |
| qwen32_mechanism | B_reading_absolute | -0.1549 [-0.7516,0.4556] |
| qwen32_mechanism | label_interface_signed | 0.1203 [-0.4706,0.7323] |
| qwen32_mechanism | label_interface_absolute | 0.1842 [-0.3854,0.7850] |
| qwen32_mechanism | answer_K_signed | -0.2194 [-0.7535,0.3192] |
| qwen32_mechanism | answer_K_absolute | -0.2194 [-0.7535,0.3192] |
| qwen32_mechanism | answer_relation_signed | -0.1063 [-0.3008,0.0673] |
| qwen32_mechanism | answer_relation_absolute | -0.1491 [-0.3115,0.0014] |
| qwen32_native | native_answer_removal_signed | 0.2102 [-0.2512,0.6701] |
| qwen32_native | native_answer_removal_absolute | 0.3811 [-0.1637,0.9507] |
| qwen32_native | native_restricted_restore_signed | 0.1054 [-0.4704,0.7144] |
| qwen32_native | native_restricted_restore_absolute | 0.1054 [-0.4704,0.7144] |
| qwen32_native | gate_answer_removal_signed | 0.6746 [-0.0100,1.3963] |
| qwen32_native | gate_answer_removal_absolute | 0.6157 [-0.0625,1.3060] |
| qwen32_native | gate_restricted_restore_signed | -1.3682 [-2.2990,-0.4741] |
| qwen32_native | gate_restricted_restore_absolute | -1.4071 [-2.1818,-0.6551] |
| qwen32_function | candidate_normal_native_both | 3.5156 [0.9766,6.0547] |
| qwen32_function | candidate_normal_gate_both | 11.9141 [8.6914,15.5273] |
| qwen32_function | candidate_answer_cross_off_native_both | 3.6133 [0.6836,6.6406] |
| qwen32_function | candidate_answer_cross_off_gate_both | 4.1992 [1.9531,6.6406] |
| qwen32_function | candidate_all_cross_off_native_both | 0.3906 [-1.1719,2.0508] |
| qwen32_function | candidate_all_cross_off_gate_both | 2.8320 [1.2695,4.4922] |
| qwen32_function | candidate_targeted_gain | 0.0977 [-3.2227,3.3203] |
| qwen32_function | candidate_targeted_minus_all | 3.2227 [0.0000,6.3477] |
| qwen32_function | candidate_query_isolation | 8.3984 [3.8086,13.0859] |
| qwen32_function | full_normal_native_both | 3.5156 [0.9766,6.0547] |
| qwen32_function | full_normal_gate_both | 11.9141 [8.6914,15.5273] |
| qwen32_function | full_answer_cross_off_native_both | 3.6133 [0.6836,6.6406] |
| qwen32_function | full_answer_cross_off_gate_both | 4.1992 [1.9531,6.6406] |
| qwen32_function | full_all_cross_off_native_both | 0.3906 [-1.1719,2.0508] |
| qwen32_function | full_all_cross_off_gate_both | 2.8320 [1.2695,4.4922] |
| qwen32_function | full_targeted_gain | 0.0977 [-3.2227,3.3203] |
| qwen32_function | full_targeted_minus_all | 3.2227 [0.0000,6.3477] |
| qwen32_function | full_query_isolation | 8.3984 [3.8086,13.0859] |

## 完整性与解释对象

上述表显示同一计算操作的核心读数；每stage完整43/64/85条件、全部K/KV/V及两重建目标、读数背景、私人方向和单函数/一句指令控制，保留在各analysis.json与独立raw审计。没有根据效果换模型、头、层、系数或材料。
相同解释可以有不同的幅度、通道权重和层位置；形成与读取应分别看。准确率接近满分不意味着形成关系消失，某个交互CI跨零也不等于其他已测操作失效。尚未完成的确认与70B不提前结论。
