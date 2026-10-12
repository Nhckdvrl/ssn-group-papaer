# E131 独立 raw 校对（滚动封存）

这是 EXECUTION §5 的 raw-first 数值/实际运行校对，不改主张等级、研究状态或冻结科学读数。
当前完整审计 8/18 stage，224 contexts、112000 评分；三个 stage 按完整批滚动纳入，后续待完整批再增加。

三个科学源见 JSON；dispatch `5abd14f91ac0cd56f40e714413d83d066ff4173af5a24e0de1cd4788a5f0beb9`；protocol `550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f`。
每批全部 raw 推导先写入独立 seal，再打开该批 author analysis。CPU/pre-score/精度修复审计保持原文件。

## llama_confirmation_mechanism

完整 32 contexts ×43接口×8 query = 11008 评分；32 层、1 实际 GPU；float32/eager、TF32=False，model revision `1f47e50cdbe801ad8a5174156ec3a0655108fb9f`。
CPU context 字节一致，实际 edge hook 全层 11 模式计数符合冻结条件；cached/full 最大误差 7.62939453e-06，self 0，layer0 sender K/V 固定为0。没有独立 GPU 重跑。
作者 analysis 比较 1041 个有限数值，最大误差 8.548717289613705e-15。

| 读数 | 均值 [95% context bootstrap CI] |
|---|---|
| A_formation_B_shared signed | 0.800534 [0.632796, 0.976782] |
| A_formation_B_shared absolute | 0.800534 [0.632796, 0.976782] |
| B_reading_A_shared signed | 3.05499 [2.7607, 3.34619] |
| B_reading_A_shared absolute | 2.8526 [2.58611, 3.12102] |
| stage_interaction signed | 0.528302 [0.329439, 0.733922] |
| stage_interaction absolute | 0.711856 [0.519407, 0.918167] |
| label_effect_B_shared signed | 0.56332 [0.415595, 0.71451] |
| label_effect_B_shared absolute | 0.56332 [0.415595, 0.71451] |
| edge_K_B_shared signed | 0.567104 [0.42794, 0.712849] |
| edge_K_B_shared absolute | 0.567104 [0.42794, 0.712849] |
| full_native relation signed | 3.26151 [3.04925, 3.47458] |
| full_native relation absolute | 3.13307 [2.91404, 3.35518] |
| label_native relation signed | -0.327631 [-0.46811, -0.185829] |
| label_native relation absolute | 0.311615 [0.211456, 0.421975] |
| answer_native relation signed | -0.0464131 [-0.11097, 0.0180449] |
| answer_native relation absolute | 0.10536 [0.0701587, 0.141924] |
| single_A private=False candidate | 0.976562 [0.953125, 1] |
| single_A private=False full argmax | 0.976562 [0.953125, 1] |
| single_A private=True candidate | 0.96875 [0.90625, 1] |
| single_A private=True full argmax | 0.96875 [0.90625, 1] |

| 重建目标 / 历史消息通道 | raw r / RMSE / zero RMSE |
|---|---|
| label_interface_B0_k | 0.713001 / 0.365137 / 0.487114 |
| label_interface_B0_kv | 0.823958 / 0.28136 / 0.487114 |
| label_interface_B0_v | 0.460699 / 0.437325 / 0.487114 |
| all_A_formation_B0_k | 0.742442 / 0.39522 / 0.579462 |
| all_A_formation_B0_kv | 0.843567 / 0.31728 / 0.579462 |
| all_A_formation_B0_v | 0.450106 / 0.520369 / 0.579462 |
| label_interface_B1_k | 0.926696 / 0.394607 / 1.01876 |
| label_interface_B1_kv | 0.950344 / 0.331852 / 1.01876 |
| label_interface_B1_v | 0.42398 / 0.966058 / 1.01876 |
| all_A_formation_B1_k | 0.917879 / 0.424305 / 1.03262 |
| all_A_formation_B1_kv | 0.942788 / 0.364257 / 1.03262 |
| all_A_formation_B1_v | 0.374489 / 1.01768 / 1.03262 |

JSON 保留全部43接口的均值/CI、full/candidate/label rate、双私人方向与 margin；12重建目标的 raw/rule双差、r/RMSE/zero及bootstrap、全部关系响应和逐层原生注意统计。完整性不由阳性方向筛选。

## qwen3_confirmation_mechanism

完整 32 contexts ×43接口×8 query = 11008 评分；36 层、1 实际 GPU；float32/eager、TF32=False，model revision `b968826d9c46dd6066d109eabc6255188de91218`。
CPU context 字节一致，实际 edge hook 全层 11 模式计数符合冻结条件；cached/full 最大误差 1.90734863e-05，self 0，layer0 sender K/V 固定为0。没有独立 GPU 重跑。
作者 analysis 比较 1041 个有限数值，最大误差 1.5543122344752192e-15。

| 读数 | 均值 [95% context bootstrap CI] |
|---|---|
| A_formation_B_shared signed | 2.35112 [1.85709, 2.83652] |
| A_formation_B_shared absolute | 2.19068 [1.70676, 2.68195] |
| B_reading_A_shared signed | 3.98709 [2.72755, 5.25424] |
| B_reading_A_shared absolute | 3.60369 [2.45289, 4.76843] |
| stage_interaction signed | 0.982599 [0.452274, 1.52764] |
| stage_interaction absolute | 1.1374 [0.550375, 1.74033] |
| label_effect_B_shared signed | 1.7087 [1.22835, 2.12674] |
| label_effect_B_shared absolute | 1.64482 [1.17994, 2.04934] |
| edge_K_B_shared signed | 1.94375 [1.52844, 2.34859] |
| edge_K_B_shared absolute | 1.94375 [1.52844, 2.34859] |
| full_native relation signed | 5.25918 [4.32535, 6.21284] |
| full_native relation absolute | 4.96618 [4.08646, 5.88344] |
| label_native relation signed | 0.269928 [0.074419, 0.482905] |
| label_native relation absolute | 0.292624 [0.1355, 0.469708] |
| answer_native relation signed | 0.221402 [0.0666906, 0.390779] |
| answer_native relation absolute | 0.333009 [0.21514, 0.467005] |
| single_A private=False candidate | 0.976562 [0.953125, 1] |
| single_A private=False full argmax | 0.976562 [0.953125, 1] |
| single_A private=True candidate | 0.929688 [0.859375, 0.976562] |
| single_A private=True full argmax | 0.929688 [0.859375, 0.976562] |

| 重建目标 / 历史消息通道 | raw r / RMSE / zero RMSE |
|---|---|
| label_interface_B0_k | 0.893341 / 1.17324 / 2.59441 |
| label_interface_B0_kv | 0.923224 / 1.02146 / 2.59441 |
| label_interface_B0_v | 0.809822 / 1.50229 / 2.59441 |
| all_A_formation_B0_k | 0.774938 / 1.77083 / 2.78722 |
| all_A_formation_B0_kv | 0.807524 / 1.65921 / 2.78722 |
| all_A_formation_B0_v | 0.688453 / 2.00708 / 2.78722 |
| label_interface_B1_k | 0.906088 / 1.05759 / 2.5252 |
| label_interface_B1_kv | 0.950655 / 0.789097 / 2.5252 |
| label_interface_B1_v | 0.726671 / 1.79773 / 2.5252 |
| all_A_formation_B1_k | 0.83071 / 1.44129 / 2.61527 |
| all_A_formation_B1_kv | 0.88855 / 1.1959 / 2.61527 |
| all_A_formation_B1_v | 0.624078 / 2.13144 / 2.61527 |

JSON 保留全部43接口的均值/CI、full/candidate/label rate、双私人方向与 margin；12重建目标的 raw/rule双差、r/RMSE/zero及bootstrap、全部关系响应和逐层原生注意统计。完整性不由阳性方向筛选。

## qwen32_discovery_mechanism

完整 16 contexts ×43接口×8 query = 5504 评分；64 层、2 实际 GPU；float32/eager、TF32=False，model revision `9216db5781bf21249d130ec9da846c4624c16137`。
CPU context 字节一致，实际 edge hook 全层 11 模式计数符合冻结条件；cached/full 最大误差 1.14440918e-05，self 0，layer0 sender K/V 固定为0。没有独立 GPU 重跑。
作者 analysis 比较 1041 个有限数值，最大误差 3.3306690738754696e-15。

| 读数 | 均值 [95% context bootstrap CI] |
|---|---|
| A_formation_B_shared signed | 2.80057 [2.01472, 3.62035] |
| A_formation_B_shared absolute | 2.80057 [2.01472, 3.62035] |
| B_reading_A_shared signed | 3.14041 [1.88286, 4.48167] |
| B_reading_A_shared absolute | 3.07415 [1.85594, 4.34551] |
| stage_interaction signed | -0.0318751 [-0.719077, 0.696474] |
| stage_interaction absolute | 0.722014 [-0.214394, 1.69076] |
| label_effect_B_shared signed | 1.77863 [1.07618, 2.52446] |
| label_effect_B_shared absolute | 1.77863 [1.07618, 2.52446] |
| edge_K_B_shared signed | 1.91474 [1.29994, 2.51529] |
| edge_K_B_shared absolute | 1.91474 [1.29994, 2.51529] |
| full_native relation signed | 6.0101 [5.23445, 6.71574] |
| full_native relation absolute | 5.54699 [4.74196, 6.31891] |
| label_native relation signed | 0.257399 [-0.389722, 0.887548] |
| label_native relation absolute | 0.57899 [0.110835, 1.09539] |
| answer_native relation signed | 0.227448 [0.032712, 0.450298] |
| answer_native relation absolute | 0.221145 [0.0429652, 0.440647] |
| single_A private=False candidate | 1 [1, 1] |
| single_A private=False full argmax | 1 [1, 1] |
| single_A private=True candidate | 1 [1, 1] |
| single_A private=True full argmax | 1 [1, 1] |

| 重建目标 / 历史消息通道 | raw r / RMSE / zero RMSE |
|---|---|
| label_interface_B0_k | 0.767897 / 1.17358 / 1.73944 |
| label_interface_B0_kv | 0.867504 / 0.900725 / 1.73944 |
| label_interface_B0_v | 0.486019 / 1.51718 / 1.73944 |
| all_A_formation_B0_k | 0.823518 / 1.20855 / 2.12805 |
| all_A_formation_B0_kv | 0.868195 / 1.09379 / 2.12805 |
| all_A_formation_B0_v | 0.448476 / 1.9083 / 2.12805 |
| label_interface_B1_k | 0.797187 / 1.27903 / 2.1181 |
| label_interface_B1_kv | 0.905607 / 0.918926 / 2.1181 |
| label_interface_B1_v | 0.285791 / 2.04177 / 2.1181 |
| all_A_formation_B1_k | 0.817802 / 1.47912 / 2.50833 |
| all_A_formation_B1_kv | 0.888484 / 1.24716 / 2.50833 |
| all_A_formation_B1_v | 0.215507 / 2.46413 / 2.50833 |

JSON 保留全部43接口的均值/CI、full/candidate/label rate、双私人方向与 margin；12重建目标的 raw/rule双差、r/RMSE/zero及bootstrap、全部关系响应和逐层原生注意统计。完整性不由阳性方向筛选。

## llama_confirmation_native

完整 32 contexts ×64接口×8 query = 16384 评分；32 层、1 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 1.33514404e-05、native self 0、graph-zero 0。
作者数值比较 1217 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/cross_answer_removal/rule_signed | 0.858995 [0.663328, 1.08461] |
| shared/native/cross_answer_removal/rule_absolute | 0.858995 [0.663328, 1.08461] |
| shared/native/within_answer_removal/rule_signed | -0.251548 [-0.417454, -0.0766109] |
| shared/native/within_answer_removal/rule_absolute | -0.251548 [-0.417454, -0.0766109] |
| shared/native/cross_vs_within_removal/rule_signed | 1.11054 [0.803049, 1.43359] |
| shared/native/cross_vs_within_removal/rule_absolute | 1.11054 [0.803049, 1.43359] |
| shared/native/all_cross_removal/rule_signed | -0.317654 [-0.546594, -0.103333] |
| shared/native/all_cross_removal/rule_absolute | -0.317654 [-0.546594, -0.103333] |
| shared/native/answer_path_restoration/rule_signed | -0.275431 [-0.393277, -0.155121] |
| shared/native/answer_path_restoration/rule_absolute | -0.275431 [-0.393277, -0.155121] |
| shared/native/restoration_residual/rule_signed | -0.0422237 [-0.220341, 0.124554] |
| shared/native/restoration_residual/rule_absolute | -0.0422237 [-0.220341, 0.124554] |
| shared/gate/cross_answer_removal/rule_signed | 1.03 [0.771829, 1.35236] |
| shared/gate/cross_answer_removal/rule_absolute | 0.941903 [0.724444, 1.18462] |
| shared/gate/within_answer_removal/rule_signed | -1.3526 [-1.56872, -1.13777] |
| shared/gate/within_answer_removal/rule_absolute | -1.3526 [-1.56872, -1.13777] |
| shared/gate/cross_vs_within_removal/rule_signed | 2.3826 [2.04414, 2.74847] |
| shared/gate/cross_vs_within_removal/rule_absolute | 2.2945 [1.9855, 2.60466] |
| shared/gate/all_cross_removal/rule_signed | 1.80676 [1.51649, 2.12497] |
| shared/gate/all_cross_removal/rule_absolute | 1.80676 [1.51649, 2.12497] |
| shared/gate/answer_path_restoration/rule_signed | 0.986672 [0.679213, 1.30297] |
| shared/gate/answer_path_restoration/rule_absolute | 1.04861 [0.769822, 1.34018] |
| shared/gate/restoration_residual/rule_signed | 0.82009 [0.553832, 1.07735] |
| shared/gate/restoration_residual/rule_absolute | 0.758149 [0.503737, 1.00924] |
| far/native/cross_answer_removal/rule_signed | 0.037679 [-0.0601642, 0.151653] |
| far/native/cross_answer_removal/rule_absolute | -0.00878786 [-0.121572, 0.0848005] |
| far/native/within_answer_removal/rule_signed | 0.10077 [-0.0814039, 0.285385] |
| far/native/within_answer_removal/rule_absolute | 0.360017 [0.230095, 0.486567] |
| far/native/cross_vs_within_removal/rule_signed | -0.0630914 [-0.244303, 0.123283] |
| far/native/cross_vs_within_removal/rule_absolute | -0.368805 [-0.501656, -0.233652] |
| far/native/all_cross_removal/rule_signed | 0.207275 [-0.0298272, 0.445073] |
| far/native/all_cross_removal/rule_absolute | 0.0873284 [-0.100548, 0.274004] |
| far/native/answer_path_restoration/rule_signed | 0.184983 [0.0932909, 0.282249] |
| far/native/answer_path_restoration/rule_absolute | 0.0964509 [-0.00554141, 0.20415] |
| far/native/restoration_residual/rule_signed | 0.0222917 [-0.24927, 0.280091] |
| far/native/restoration_residual/rule_absolute | -0.00912248 [-0.229106, 0.197911] |
| far/gate/cross_answer_removal/rule_signed | 0.026384 [-0.0545886, 0.124967] |
| far/gate/cross_answer_removal/rule_absolute | -0.0233254 [-0.118993, 0.0585024] |
| far/gate/within_answer_removal/rule_signed | 0.101275 [-0.0406974, 0.236653] |
| far/gate/within_answer_removal/rule_absolute | 0.171716 [0.062393, 0.282986] |
| far/gate/cross_vs_within_removal/rule_signed | -0.0748906 [-0.219005, 0.104772] |
| far/gate/cross_vs_within_removal/rule_absolute | -0.195041 [-0.34588, -0.0665455] |
| far/gate/all_cross_removal/rule_signed | 0.0235371 [-0.177234, 0.207553] |
| far/gate/all_cross_removal/rule_absolute | 0.444212 [0.333731, 0.561493] |
| far/gate/answer_path_restoration/rule_signed | 0.145791 [0.0812201, 0.217682] |
| far/gate/answer_path_restoration/rule_absolute | 0.176643 [0.123865, 0.239998] |
| far/gate/restoration_residual/rule_signed | -0.122254 [-0.344824, 0.0734616] |
| far/gate/restoration_residual/rule_absolute | 0.267569 [0.158099, 0.383377] |

恢复是在全部 B→A 形成阻断中开放 B答案→A-label 边；没有 donor。raw removed 计数是恢复前被删边数，net removed=removed−restored，与独立 CPU 最终图逐ctx一致。

## qwen3_confirmation_native

完整 32 contexts ×64接口×8 query = 16384 评分；36 层、1 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 6.67572021e-05、native self 0、graph-zero 0。
作者数值比较 1217 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/cross_answer_removal/rule_signed | 1.76178 [1.26387, 2.29437] |
| shared/native/cross_answer_removal/rule_absolute | 1.59096 [1.07659, 2.13228] |
| shared/native/within_answer_removal/rule_signed | 0.869533 [0.30571, 1.46344] |
| shared/native/within_answer_removal/rule_absolute | 0.869533 [0.30571, 1.46344] |
| shared/native/cross_vs_within_removal/rule_signed | 0.892252 [0.158955, 1.61436] |
| shared/native/cross_vs_within_removal/rule_absolute | 0.721431 [0.0634894, 1.35693] |
| shared/native/all_cross_removal/rule_signed | -1.51024 [-2.44466, -0.642686] |
| shared/native/all_cross_removal/rule_absolute | -1.51024 [-2.44466, -0.642686] |
| shared/native/answer_path_restoration/rule_signed | -0.64992 [-1.26947, -0.0802565] |
| shared/native/answer_path_restoration/rule_absolute | -0.64992 [-1.26947, -0.0802565] |
| shared/native/restoration_residual/rule_signed | -0.860322 [-1.53475, -0.21576] |
| shared/native/restoration_residual/rule_absolute | -0.860322 [-1.53475, -0.21576] |
| shared/gate/cross_answer_removal/rule_signed | 1.09715 [0.476778, 1.69414] |
| shared/gate/cross_answer_removal/rule_absolute | 1.07353 [0.58056, 1.58545] |
| shared/gate/within_answer_removal/rule_signed | -0.930463 [-1.50353, -0.428156] |
| shared/gate/within_answer_removal/rule_absolute | -0.631991 [-1.05759, -0.230018] |
| shared/gate/cross_vs_within_removal/rule_signed | 2.02761 [1.55429, 2.54555] |
| shared/gate/cross_vs_within_removal/rule_absolute | 1.70552 [1.22287, 2.23052] |
| shared/gate/all_cross_removal/rule_signed | 1.52715 [0.879919, 2.15398] |
| shared/gate/all_cross_removal/rule_absolute | 1.9496 [1.49265, 2.45411] |
| shared/gate/answer_path_restoration/rule_signed | 2.14334 [1.42586, 2.89258] |
| shared/gate/answer_path_restoration/rule_absolute | 2.43839 [1.85599, 3.07251] |
| shared/gate/restoration_residual/rule_signed | -0.616196 [-1.133, -0.100523] |
| shared/gate/restoration_residual/rule_absolute | -0.488786 [-0.872756, -0.086809] |
| far/native/cross_answer_removal/rule_signed | 0.249581 [0.0735407, 0.425907] |
| far/native/cross_answer_removal/rule_absolute | -0.0428854 [-0.225293, 0.157723] |
| far/native/within_answer_removal/rule_signed | 0.0794723 [-0.246178, 0.415777] |
| far/native/within_answer_removal/rule_absolute | 0.02903 [-0.227014, 0.290939] |
| far/native/cross_vs_within_removal/rule_signed | 0.170109 [-0.21745, 0.554843] |
| far/native/cross_vs_within_removal/rule_absolute | -0.0719154 [-0.396779, 0.254239] |
| far/native/all_cross_removal/rule_signed | 0.0514088 [-0.454463, 0.539436] |
| far/native/all_cross_removal/rule_absolute | -0.154897 [-0.637285, 0.31757] |
| far/native/answer_path_restoration/rule_signed | 0.110141 [-0.0676857, 0.304493] |
| far/native/answer_path_restoration/rule_absolute | 0.0571986 [-0.123275, 0.219202] |
| far/native/restoration_residual/rule_signed | -0.0587324 [-0.571676, 0.454684] |
| far/native/restoration_residual/rule_absolute | -0.212096 [-0.687519, 0.262044] |
| far/gate/cross_answer_removal/rule_signed | 0.277581 [0.0938867, 0.473108] |
| far/gate/cross_answer_removal/rule_absolute | -0.242499 [-0.384896, -0.100672] |
| far/gate/within_answer_removal/rule_signed | 0.235343 [-0.147933, 0.641208] |
| far/gate/within_answer_removal/rule_absolute | -0.309706 [-0.651924, -0.0123529] |
| far/gate/cross_vs_within_removal/rule_signed | 0.0422385 [-0.368522, 0.453352] |
| far/gate/cross_vs_within_removal/rule_absolute | 0.0672067 [-0.253788, 0.403869] |
| far/gate/all_cross_removal/rule_signed | 0.115037 [-0.183342, 0.409933] |
| far/gate/all_cross_removal/rule_absolute | 0.6801 [0.506986, 0.866439] |
| far/gate/answer_path_restoration/rule_signed | 0.34774 [0.0875325, 0.652563] |
| far/gate/answer_path_restoration/rule_absolute | 0.556103 [0.339079, 0.823691] |
| far/gate/restoration_residual/rule_signed | -0.232703 [-0.646158, 0.159462] |
| far/gate/restoration_residual/rule_absolute | 0.123997 [-0.17943, 0.393777] |

恢复是在全部 B→A 形成阻断中开放 B答案→A-label 边；没有 donor。raw removed 计数是恢复前被删边数，net removed=removed−restored，与独立 CPU 最终图逐ctx一致。

## qwen3_confirmation_function

完整 32 contexts ×85接口×8 query = 21760 评分；36 层、1 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 4.95910645e-05、native self 0、graph-zero 0。
作者数值比较 1893 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/answer_cross_off_minus_normal mean candidate gain | 0.0761719 [0.0517578, 0.0996094] |
| shared/native/all_cross_off_minus_normal mean candidate gain | -0.0957031 [-0.12207, -0.0683594] |
| shared/native/answer_minus_all mean candidate gain | 0.171875 [0.146484, 0.195312] |
| shared/native/normal full mean / joint | 0.844727 [0.819336, 0.870117] / 0.707031 [0.662109, 0.753906] |
| shared/native/answer_cross_off full mean / joint | 0.920898 [0.892578, 0.945312] / 0.863281 [0.818359, 0.904297] |
| shared/native/all_cross_off full mean / joint | 0.749023 [0.735352, 0.762695] / 0.521484 [0.5, 0.542969] |
| shared/gate/answer_cross_off_minus_normal mean candidate gain | 0.105469 [0.0800781, 0.130859] |
| shared/gate/all_cross_off_minus_normal mean candidate gain | 0.131836 [0.0996094, 0.166016] |
| shared/gate/answer_minus_all mean candidate gain | -0.0263672 [-0.0507812, -0.00292969] |
| shared/gate/normal full mean / joint | 0.819336 [0.786133, 0.851562] / 0.667969 [0.603516, 0.726562] |
| shared/gate/answer_cross_off full mean / joint | 0.924805 [0.901367, 0.946289] / 0.863281 [0.822266, 0.900391] |
| shared/gate/all_cross_off full mean / joint | 0.951172 [0.933594, 0.967773] / 0.914062 [0.884766, 0.941406] |
| far/native/answer_cross_off_minus_normal mean candidate gain | 0.00195312 [-0.00488281, 0.00878906] |
| far/native/all_cross_off_minus_normal mean candidate gain | -0.0146484 [-0.0302734, 0.000976562] |
| far/native/answer_minus_all mean candidate gain | 0.0166016 [0.00195312, 0.0322266] |
| far/native/normal full mean / joint | 0.948242 [0.924805, 0.96875] / 0.914062 [0.876953, 0.947266] |
| far/native/answer_cross_off full mean / joint | 0.951172 [0.930664, 0.969727] / 0.917969 [0.886719, 0.947266] |
| far/native/all_cross_off full mean / joint | 0.506836 [0.488281, 0.526367] / 0.0703125 [0.0449219, 0.101562] |
| far/gate/answer_cross_off_minus_normal mean candidate gain | -0.00390625 [-0.0126953, 0.00488281] |
| far/gate/all_cross_off_minus_normal mean candidate gain | 0 [-0.0234375, 0.0244141] |
| far/gate/answer_minus_all mean candidate gain | -0.00390625 [-0.0292969, 0.0195312] |
| far/gate/normal full mean / joint | 0.945312 [0.920898, 0.96582] / 0.904297 [0.863281, 0.939453] |
| far/gate/answer_cross_off full mean / joint | 0.941406 [0.916016, 0.963867] / 0.896484 [0.851562, 0.935547] |
| far/gate/all_cross_off full mean / joint | 0.945312 [0.925781, 0.962891] / 0.908203 [0.875, 0.9375] |

primary 中 both 是两 Actor accuracy 的均值，不是 joint；JSON 单列 joint 与完整输出/other-source word，并保留全部85接口/双私有方向。

## llama_confirmation_function

完整 32 contexts ×85接口×8 query = 21760 评分；32 层、1 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 1.71661377e-05、native self 0、graph-zero 0。
作者数值比较 1893 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/answer_cross_off_minus_normal mean candidate gain | 0.0888672 [0.0654297, 0.111328] |
| shared/native/all_cross_off_minus_normal mean candidate gain | -0.0449219 [-0.0634766, -0.0273438] |
| shared/native/answer_minus_all mean candidate gain | 0.133789 [0.109375, 0.158203] |
| shared/native/normal full mean / joint | 0.796875 [0.779297, 0.814453] / 0.601562 [0.570264, 0.636719] |
| shared/native/answer_cross_off full mean / joint | 0.885742 [0.860352, 0.90918] / 0.777344 [0.730469, 0.822266] |
| shared/native/all_cross_off full mean / joint | 0.751953 [0.742188, 0.760742] / 0.509766 [0.496094, 0.523438] |
| shared/gate/answer_cross_off_minus_normal mean candidate gain | 0.00488281 [-0.00585938, 0.0166016] |
| shared/gate/all_cross_off_minus_normal mean candidate gain | -0.0078125 [-0.0253906, 0.00683594] |
| shared/gate/answer_minus_all mean candidate gain | 0.0126953 [-0.000976562, 0.0292969] |
| shared/gate/normal full mean / joint | 0.978516 [0.963867, 0.991211] / 0.960938 [0.935547, 0.984375] |
| shared/gate/answer_cross_off full mean / joint | 0.983398 [0.97168, 0.993164] / 0.96875 [0.947266, 0.986328] |
| shared/gate/all_cross_off full mean / joint | 0.970703 [0.949219, 0.988281] / 0.945312 [0.904297, 0.976562] |
| far/native/answer_cross_off_minus_normal mean candidate gain | 0.00195312 [-0.00195312, 0.00585938] |
| far/native/all_cross_off_minus_normal mean candidate gain | -0.0263672 [-0.0400391, -0.0136719] |
| far/native/answer_minus_all mean candidate gain | 0.0283203 [0.015625, 0.0419922] |
| far/native/normal full mean / joint | 0.944336 [0.913086, 0.969727] / 0.896484 [0.835938, 0.945312] |
| far/native/answer_cross_off full mean / joint | 0.93457 [0.902344, 0.961914] / 0.875 [0.8125, 0.92583] |
| far/native/all_cross_off full mean / joint | 0.538086 [0.523438, 0.553711] / 0.0976562 [0.0703125, 0.126953] |
| far/gate/answer_cross_off_minus_normal mean candidate gain | 0.00292969 [-0.00390625, 0.0107422] |
| far/gate/all_cross_off_minus_normal mean candidate gain | -0.0205078 [-0.0429688, -0.00195312] |
| far/gate/answer_minus_all mean candidate gain | 0.0234375 [0.00585938, 0.0449219] |
| far/gate/normal full mean / joint | 0.964844 [0.949219, 0.978516] / 0.933594 [0.90625, 0.958984] |
| far/gate/answer_cross_off full mean / joint | 0.967773 [0.952148, 0.981445] / 0.939453 [0.912109, 0.964844] |
| far/gate/all_cross_off full mean / joint | 0.944336 [0.917969, 0.96582] / 0.896484 [0.845703, 0.9375] |

primary 中 both 是两 Actor accuracy 的均值，不是 joint；JSON 单列 joint 与完整输出/other-source word，并保留全部85接口/双私有方向。

## qwen32_discovery_native

完整 16 contexts ×64接口×8 query = 8192 评分；64 层、2 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 2.67028809e-05、native self 0、graph-zero 0。
作者数值比较 1217 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/cross_answer_removal/rule_signed | 1.8158 [1.2704, 2.40887] |
| shared/native/cross_answer_removal/rule_absolute | 1.8158 [1.2704, 2.40887] |
| shared/native/within_answer_removal/rule_signed | -0.275258 [-0.800424, 0.241267] |
| shared/native/within_answer_removal/rule_absolute | -0.275258 [-0.800424, 0.241267] |
| shared/native/cross_vs_within_removal/rule_signed | 2.09106 [1.43341, 2.77952] |
| shared/native/cross_vs_within_removal/rule_absolute | 2.09106 [1.43341, 2.77952] |
| shared/native/all_cross_removal/rule_signed | 0.658736 [0.094746, 1.25104] |
| shared/native/all_cross_removal/rule_absolute | 0.658736 [0.094746, 1.25104] |
| shared/native/answer_path_restoration/rule_signed | -0.822093 [-1.21092, -0.429981] |
| shared/native/answer_path_restoration/rule_absolute | -0.822093 [-1.21092, -0.429981] |
| shared/native/restoration_residual/rule_signed | 1.48083 [0.821612, 2.1825] |
| shared/native/restoration_residual/rule_absolute | 1.48083 [0.821612, 2.1825] |
| shared/gate/cross_answer_removal/rule_signed | 1.59975 [1.06622, 2.17243] |
| shared/gate/cross_answer_removal/rule_absolute | 1.5109 [0.968464, 2.09668] |
| shared/gate/within_answer_removal/rule_signed | -1.51349 [-2.10254, -1.00132] |
| shared/gate/within_answer_removal/rule_absolute | -1.51349 [-2.10254, -1.00132] |
| shared/gate/cross_vs_within_removal/rule_signed | 3.11324 [2.45646, 3.79018] |
| shared/gate/cross_vs_within_removal/rule_absolute | 3.02439 [2.39731, 3.67829] |
| shared/gate/all_cross_removal/rule_signed | 3.5194 [2.63839, 4.36693] |
| shared/gate/all_cross_removal/rule_absolute | 3.5194 [2.63839, 4.36693] |
| shared/gate/answer_path_restoration/rule_signed | 1.08521 [0.602189, 1.66002] |
| shared/gate/answer_path_restoration/rule_absolute | 1.11148 [0.643487, 1.67627] |
| shared/gate/restoration_residual/rule_signed | 2.43419 [1.46833, 3.39021] |
| shared/gate/restoration_residual/rule_absolute | 2.40792 [1.44505, 3.35903] |
| far/native/cross_answer_removal/rule_signed | -0.0147546 [-0.37583, 0.337647] |
| far/native/cross_answer_removal/rule_absolute | -0.23654 [-0.571148, 0.0842006] |
| far/native/within_answer_removal/rule_signed | -0.71512 [-2.0281, 0.578173] |
| far/native/within_answer_removal/rule_absolute | -2.04223 [-2.96484, -1.17904] |
| far/native/cross_vs_within_removal/rule_signed | 0.700366 [-0.561639, 1.94237] |
| far/native/cross_vs_within_removal/rule_absolute | 1.80569 [0.920668, 2.71237] |
| far/native/all_cross_removal/rule_signed | -0.168347 [-0.758475, 0.368178] |
| far/native/all_cross_removal/rule_absolute | -0.354636 [-0.799799, 0.0416877] |
| far/native/answer_path_restoration/rule_signed | -0.217483 [-0.489484, 0.0668952] |
| far/native/answer_path_restoration/rule_absolute | -0.108712 [-0.346144, 0.145854] |
| far/native/restoration_residual/rule_signed | 0.0491364 [-0.483259, 0.558557] |
| far/native/restoration_residual/rule_absolute | -0.245924 [-0.665634, 0.158765] |
| far/gate/cross_answer_removal/rule_signed | -0.142146 [-0.541998, 0.252117] |
| far/gate/cross_answer_removal/rule_absolute | -0.205538 [-0.516131, 0.109714] |
| far/gate/within_answer_removal/rule_signed | -0.290234 [-1.60194, 1.00009] |
| far/gate/within_answer_removal/rule_absolute | -1.82683 [-2.52322, -1.23346] |
| far/gate/cross_vs_within_removal/rule_signed | 0.148087 [-1.11872, 1.40419] |
| far/gate/cross_vs_within_removal/rule_absolute | 1.6213 [0.933276, 2.38017] |
| far/gate/all_cross_removal/rule_signed | -0.137769 [-0.573875, 0.301272] |
| far/gate/all_cross_removal/rule_absolute | 0.758327 [0.515749, 1.01342] |
| far/gate/answer_path_restoration/rule_signed | -0.112896 [-0.422939, 0.150314] |
| far/gate/answer_path_restoration/rule_absolute | 0.383334 [0.198596, 0.616317] |
| far/gate/restoration_residual/rule_signed | -0.0248725 [-0.583637, 0.542431] |
| far/gate/restoration_residual/rule_absolute | 0.374994 [0.0259555, 0.716374] |

恢复是在全部 B→A 形成阻断中开放 B答案→A-label 边；没有 donor。raw removed 计数是恢复前被删边数，net removed=removed−restored，与独立 CPU 最终图逐ctx一致。

## 首次32B探索与配对锚点的范围

Q32 n16 已在原冻结接口上得到 A形成与 B读取背景的正功能作用；signed/absolute interaction 的 CI 均跨0，保留该边界而不把形成效应作废。固定系数历史答案 KV 对实际 A-label 干预有预测改善和残差，不能改述为完整中介或全部必要性解释。
native 答案路径恢复与 query隔离恢复不同，全部负向/零向及 K/KV/V 通道保留。新小模型三阶段 n32 锚点已独立测本批私人功能；mean accuracy 与 joint 成功分列，不把 far 输出词空间错误误叫独立 latent/ID 模块。
驻留 device-hours 另核 worker 连续累计记录：每个worker最终值只计一次；运行中快照只覆盖记录时点，不能累加逐stage覆盖值。

## 范围

原生形成与当前 query 读取环境在实际接口上作交叉检验；历史答案边功能、A-label 交换和全部 A cache 干预是不同对象。重建系数固定为1，不拟合，不把相关性当必要性或完整解释比例。
候选词 accuracy 不能替代完整输出，单 Source 私人功能也不等同原子满分。注意 mass 为全部 heads 的和，跨模型不能直接比较绝对质量。
尚未完成的大模型确认与70B材料不作科学结论；保留前次 TF32 三个0科学 row实现失败及修复记录。

本次未运行 GPU、未改科学源/卡/claims/论文、未 commit/push。

## 当前作者 8/18 PARTIAL 报告独立复核

summary八批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。8完整表行、43统计单元、126数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前无真实大小confirmation pair，D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。建议自然功能表标题显式写shared/mean，数值无须修改。

报告script `f78bbd374be1f04397659d83b51a3ac4a32c716d3fd1321de909aaa74d2ec949`；summary `2279be7ff19be6de886aa105094a90198eecfb65e91ece196cc8a7809108f7cc`；report `b9e699cdcf055376198794babe3a392c0a771c707904981ab8aa2fad95918c42`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。

## 当前作者 8/18 PARTIAL 报告独立复核

summary八批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。8完整表行、43统计单元、126数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前无真实大小confirmation pair，D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。新版自然功能表标题已明确shared/两Actor平均，resource_scope已明确last_observed快照；数值未改。

报告script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `91d0a7d8c038eefa5c4c4044a1e7fbc1ece75be2f7fe4b361c16569ffb32d9e6`；report `2cf6dfe5cb03724a72a9eb2e9f332f570505722785050cb44fb36054563d33a3`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。
