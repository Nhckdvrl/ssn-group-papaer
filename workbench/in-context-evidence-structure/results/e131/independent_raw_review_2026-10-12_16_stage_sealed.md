# E131 独立 raw 校对（滚动封存）

这是 EXECUTION §5 的 raw-first 数值/实际运行校对，不改主张等级、研究状态或冻结科学读数。
当前完整审计 16/18 stage，416 contexts、207616 评分；三个 stage 按完整批滚动纳入，后续待完整批再增加。

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

## qwen32_discovery_function

完整 16 contexts ×85接口×8 query = 10880 评分；64 层、2 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 3.81469727e-05、native self 0、graph-zero 0。
作者数值比较 1893 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/answer_cross_off_minus_normal mean candidate gain | 0.0898438 [0.0585938, 0.125] |
| shared/native/all_cross_off_minus_normal mean candidate gain | -0.121094 [-0.158203, -0.0820312] |
| shared/native/answer_minus_all mean candidate gain | 0.210938 [0.193359, 0.226562] |
| shared/native/normal full mean / joint | 0.869141 [0.837891, 0.898438] / 0.738281 [0.675781, 0.796875] |
| shared/native/answer_cross_off full mean / joint | 0.958984 [0.935498, 0.980469] / 0.921875 [0.878906, 0.960938] |
| shared/native/all_cross_off full mean / joint | 0.748047 [0.724609, 0.767578] / 0.523438 [0.492188, 0.554688] |
| shared/gate/answer_cross_off_minus_normal mean candidate gain | -0.00585938 [-0.0292969, 0.0175781] |
| shared/gate/all_cross_off_minus_normal mean candidate gain | 0.0195312 [-0.00585938, 0.0429688] |
| shared/gate/answer_minus_all mean candidate gain | -0.0253906 [-0.0566406, 0.00390625] |
| shared/gate/normal full mean / joint | 0.957031 [0.939453, 0.974609] / 0.917969 [0.882812, 0.949219] |
| shared/gate/answer_cross_off full mean / joint | 0.951172 [0.925781, 0.974609] / 0.910156 [0.863281, 0.953125] |
| shared/gate/all_cross_off full mean / joint | 0.976562 [0.960938, 0.990234] / 0.953125 [0.921875, 0.980469] |
| far/native/answer_cross_off_minus_normal mean candidate gain | 0.0078125 [-0.00585938, 0.0214844] |
| far/native/all_cross_off_minus_normal mean candidate gain | -0.0117188 [-0.0410156, 0.015625] |
| far/native/answer_minus_all mean candidate gain | 0.0195312 [-0.0078125, 0.0527344] |
| far/native/normal full mean / joint | 0.947266 [0.929688, 0.962891] / 0.898438 [0.867188, 0.929688] |
| far/native/answer_cross_off full mean / joint | 0.945312 [0.917969, 0.96875] / 0.890625 [0.835938, 0.9375] |
| far/native/all_cross_off full mean / joint | 0.505859 [0.474609, 0.535156] / 0.078125 [0.0429688, 0.113281] |
| far/gate/answer_cross_off_minus_normal mean candidate gain | 0.0234375 [0.0078125, 0.0390625] |
| far/gate/all_cross_off_minus_normal mean candidate gain | 0.0429688 [0.0078125, 0.078125] |
| far/gate/answer_minus_all mean candidate gain | -0.0195312 [-0.0625, 0.0195312] |
| far/gate/normal full mean / joint | 0.886719 [0.863281, 0.910156] / 0.777344 [0.730469, 0.824219] |
| far/gate/answer_cross_off full mean / joint | 0.910156 [0.878906, 0.939453] / 0.824219 [0.761719, 0.878906] |
| far/gate/all_cross_off full mean / joint | 0.929688 [0.898438, 0.958984] / 0.863281 [0.804688, 0.917969] |

primary 中 both 是两 Actor accuracy 的均值，不是 joint；JSON 单列 joint 与完整输出/other-source word，并保留全部85接口/双私有方向。

## qwen32_confirmation_mechanism

完整 32 contexts ×43接口×8 query = 11008 评分；64 层、2 实际 GPU；float32/eager、TF32=False，model revision `9216db5781bf21249d130ec9da846c4624c16137`。
CPU context 字节一致，实际 edge hook 全层 11 模式计数符合冻结条件；cached/full 最大误差 2.86102295e-05，self 0，layer0 sender K/V 固定为0。没有独立 GPU 重跑。
作者 analysis 比较 1041 个有限数值，最大误差 1.887379141862766e-15。

| 读数 | 均值 [95% context bootstrap CI] |
|---|---|
| A_formation_B_shared signed | 2.67564 [2.26579, 3.09561] |
| A_formation_B_shared absolute | 2.67564 [2.26579, 3.09561] |
| B_reading_A_shared signed | 3.48458 [2.59559, 4.34803] |
| B_reading_A_shared absolute | 3.44877 [2.57556, 4.28449] |
| stage_interaction signed | -0.0366461 [-0.524953, 0.462008] |
| stage_interaction absolute | 0.953078 [0.162029, 1.74936] |
| label_effect_B_shared signed | 1.82901 [1.45682, 2.20981] |
| label_effect_B_shared absolute | 1.82901 [1.45682, 2.20981] |
| edge_K_B_shared signed | 1.72437 [1.30378, 2.14575] |
| edge_K_B_shared absolute | 1.72437 [1.30378, 2.14575] |
| full_native relation signed | 6.44775 [5.96564, 6.91385] |
| full_native relation absolute | 5.55102 [5.0034, 6.08222] |
| label_native relation signed | 0.0802578 [-0.328562, 0.462212] |
| label_native relation absolute | 0.427176 [0.18772, 0.690232] |
| answer_native relation signed | 0.115059 [-0.016557, 0.249384] |
| answer_native relation absolute | 0.183865 [0.0974458, 0.283014] |
| single_A private=False candidate | 1 [1, 1] |
| single_A private=False full argmax | 1 [1, 1] |
| single_A private=True candidate | 1 [1, 1] |
| single_A private=True full argmax | 1 [1, 1] |

| 重建目标 / 历史消息通道 | raw r / RMSE / zero RMSE |
|---|---|
| label_interface_B0_k | 0.770968 / 1.18922 / 1.85657 |
| label_interface_B0_kv | 0.882834 / 0.864484 / 1.85657 |
| label_interface_B0_v | 0.50517 / 1.59436 / 1.85657 |
| all_A_formation_B0_k | 0.765872 / 1.35054 / 2.10069 |
| all_A_formation_B0_kv | 0.852074 / 1.11474 / 2.10069 |
| all_A_formation_B0_v | 0.481149 / 1.84546 / 2.10069 |
| label_interface_B1_k | 0.783501 / 1.24793 / 1.99896 |
| label_interface_B1_kv | 0.876483 / 0.961205 / 1.99896 |
| label_interface_B1_v | 0.272753 / 1.94327 / 1.99896 |
| all_A_formation_B1_k | 0.733195 / 1.47417 / 2.16558 |
| all_A_formation_B1_kv | 0.828571 / 1.21255 / 2.16558 |
| all_A_formation_B1_v | 0.29324 / 2.07494 / 2.16558 |

JSON 保留全部43接口的均值/CI、full/candidate/label rate、双私人方向与 margin；12重建目标的 raw/rule双差、r/RMSE/zero及bootstrap、全部关系响应和逐层原生注意统计。完整性不由阳性方向筛选。

## qwen32_confirmation_native

完整 32 contexts ×64接口×8 query = 16384 评分；64 层、2 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 1.14440918e-05、native self 0、graph-zero 0。
作者数值比较 1217 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/cross_answer_removal/rule_signed | 1.97202 [1.46707, 2.4996] |
| shared/native/cross_answer_removal/rule_absolute | 1.97202 [1.46707, 2.4996] |
| shared/native/within_answer_removal/rule_signed | -0.387405 [-0.725429, -0.0637983] |
| shared/native/within_answer_removal/rule_absolute | -0.387405 [-0.725429, -0.0637983] |
| shared/native/cross_vs_within_removal/rule_signed | 2.35943 [1.89179, 2.81866] |
| shared/native/cross_vs_within_removal/rule_absolute | 2.35943 [1.89179, 2.81866] |
| shared/native/all_cross_removal/rule_signed | 0.16323 [-0.402849, 0.70094] |
| shared/native/all_cross_removal/rule_absolute | 0.16323 [-0.402849, 0.70094] |
| shared/native/answer_path_restoration/rule_signed | -0.544483 [-0.832696, -0.276054] |
| shared/native/answer_path_restoration/rule_absolute | -0.544483 [-0.832696, -0.276054] |
| shared/native/restoration_residual/rule_signed | 0.707713 [0.165118, 1.24932] |
| shared/native/restoration_residual/rule_absolute | 0.707713 [0.165118, 1.24932] |
| shared/gate/cross_answer_removal/rule_signed | 1.7718 [1.27392, 2.30858] |
| shared/gate/cross_answer_removal/rule_absolute | 1.6892 [1.22048, 2.20604] |
| shared/gate/within_answer_removal/rule_signed | -1.1613 [-1.70314, -0.605209] |
| shared/gate/within_answer_removal/rule_absolute | -1.0494 [-1.54812, -0.521671] |
| shared/gate/cross_vs_within_removal/rule_signed | 2.93309 [2.30546, 3.52867] |
| shared/gate/cross_vs_within_removal/rule_absolute | 2.7386 [2.12048, 3.30643] |
| shared/gate/all_cross_removal/rule_signed | 3.41163 [2.67696, 4.13863] |
| shared/gate/all_cross_removal/rule_absolute | 3.56159 [2.93932, 4.20878] |
| shared/gate/answer_path_restoration/rule_signed | 0.775127 [0.321263, 1.28387] |
| shared/gate/answer_path_restoration/rule_absolute | 1.03131 [0.64626, 1.4868] |
| shared/gate/restoration_residual/rule_signed | 2.6365 [2.01506, 3.24987] |
| shared/gate/restoration_residual/rule_absolute | 2.53028 [2.01983, 3.06513] |
| far/native/cross_answer_removal/rule_signed | 0.0924159 [-0.178395, 0.364986] |
| far/native/cross_answer_removal/rule_absolute | -0.149233 [-0.365384, 0.0467532] |
| far/native/within_answer_removal/rule_signed | -0.449371 [-1.58228, 0.651616] |
| far/native/within_answer_removal/rule_absolute | -2.14012 [-2.9556, -1.37036] |
| far/native/cross_vs_within_removal/rule_signed | 0.541787 [-0.554589, 1.66717] |
| far/native/cross_vs_within_removal/rule_absolute | 1.99089 [1.18537, 2.82689] |
| far/native/all_cross_removal/rule_signed | -0.646548 [-1.10179, -0.188389] |
| far/native/all_cross_removal/rule_absolute | -0.138818 [-0.543267, 0.248568] |
| far/native/answer_path_restoration/rule_signed | -0.131987 [-0.337453, 0.0918421] |
| far/native/answer_path_restoration/rule_absolute | -0.210694 [-0.406317, -0.00856851] |
| far/native/restoration_residual/rule_signed | -0.514562 [-0.90243, -0.138514] |
| far/native/restoration_residual/rule_absolute | 0.0718768 [-0.269555, 0.394289] |
| far/gate/cross_answer_removal/rule_signed | 0.127585 [-0.0978303, 0.36264] |
| far/gate/cross_answer_removal/rule_absolute | -0.0377642 [-0.254492, 0.180404] |
| far/gate/within_answer_removal/rule_signed | 0.696882 [-0.258625, 1.62981] |
| far/gate/within_answer_removal/rule_absolute | -1.5471 [-2.26952, -0.892491] |
| far/gate/cross_vs_within_removal/rule_signed | -0.569297 [-1.5703, 0.471813] |
| far/gate/cross_vs_within_removal/rule_absolute | 1.50934 [0.805345, 2.31632] |
| far/gate/all_cross_removal/rule_signed | 0.00399248 [-0.38235, 0.440554] |
| far/gate/all_cross_removal/rule_absolute | 0.911266 [0.672838, 1.20513] |
| far/gate/answer_path_restoration/rule_signed | 0.102983 [-0.0208952, 0.228098] |
| far/gate/answer_path_restoration/rule_absolute | 0.32042 [0.252254, 0.389494] |
| far/gate/restoration_residual/rule_signed | -0.0989907 [-0.496269, 0.337551] |
| far/gate/restoration_residual/rule_absolute | 0.590846 [0.345909, 0.883157] |

恢复是在全部 B→A 形成阻断中开放 B答案→A-label 边；没有 donor。raw removed 计数是恢复前被删边数，net removed=removed−restored，与独立 CPU 最终图逐ctx一致。

## qwen32_confirmation_function

完整 32 contexts ×85接口×8 query = 21760 评分；64 层、2 GPU，FP32/eager/TF32=False。CPU材料字节一致，全部实际层消费与几何边计数通过，cached/full 1.90734863e-05、native self 0、graph-zero 0。
作者数值比较 1893 项、最大误差 0。

| 固定读数 | 均值 [95% context bootstrap CI] |
|---|---|
| shared/native/answer_cross_off_minus_normal mean candidate gain | 0.0771484 [0.0576172, 0.0957031] |
| shared/native/all_cross_off_minus_normal mean candidate gain | -0.126953 [-0.147461, -0.107397] |
| shared/native/answer_minus_all mean candidate gain | 0.204102 [0.181641, 0.223633] |
| shared/native/normal full mean / joint | 0.879883 [0.862305, 0.897461] / 0.767578 [0.734375, 0.800781] |
| shared/native/answer_cross_off full mean / joint | 0.957031 [0.935547, 0.973633] / 0.921875 [0.888672, 0.951172] |
| shared/native/all_cross_off full mean / joint | 0.75293 [0.741211, 0.762695] / 0.529297 [0.515625, 0.542969] |
| shared/gate/answer_cross_off_minus_normal mean candidate gain | 0.0283203 [0.0146484, 0.0419922] |
| shared/gate/all_cross_off_minus_normal mean candidate gain | 0.0410156 [0.0244141, 0.0576172] |
| shared/gate/answer_minus_all mean candidate gain | -0.0126953 [-0.0302734, 0.00390625] |
| shared/gate/normal full mean / joint | 0.938477 [0.922852, 0.954102] / 0.884766 [0.857422, 0.912109] |
| shared/gate/answer_cross_off full mean / joint | 0.966797 [0.950195, 0.981445] / 0.939453 [0.910156, 0.964844] |
| shared/gate/all_cross_off full mean / joint | 0.979492 [0.96875, 0.989258] / 0.962891 [0.945312, 0.980469] |
| far/native/answer_cross_off_minus_normal mean candidate gain | 0.0205078 [0.00878906, 0.0322266] |
| far/native/all_cross_off_minus_normal mean candidate gain | 0.0205078 [-0.00292969, 0.0439453] |
| far/native/answer_minus_all mean candidate gain | 0 [-0.0234375, 0.0234375] |
| far/native/normal full mean / joint | 0.932617 [0.910156, 0.952148] / 0.869141 [0.828125, 0.90625] |
| far/native/answer_cross_off full mean / joint | 0.947266 [0.926758, 0.96582] / 0.898438 [0.859375, 0.933594] |
| far/native/all_cross_off full mean / joint | 0.526367 [0.504883, 0.550781] / 0.0996094 [0.0664062, 0.140625] |
| far/gate/answer_cross_off_minus_normal mean candidate gain | 0.0253906 [0.0107422, 0.0410156] |
| far/gate/all_cross_off_minus_normal mean candidate gain | 0.0693359 [0.0419678, 0.0966797] |
| far/gate/answer_minus_all mean candidate gain | -0.0439453 [-0.0693359, -0.0185547] |
| far/gate/normal full mean / joint | 0.871094 [0.850586, 0.891602] / 0.751953 [0.712891, 0.791016] |
| far/gate/answer_cross_off full mean / joint | 0.896484 [0.875, 0.916016] / 0.804688 [0.769531, 0.837891] |
| far/gate/all_cross_off full mean / joint | 0.94043 [0.922852, 0.957031] / 0.886719 [0.853516, 0.919922] |

primary 中 both 是两 Actor accuracy 的均值，不是 joint；JSON 单列 joint 与完整输出/other-source word，并保留全部85接口/双私有方向。

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

## 当前作者 9/18 PARTIAL 报告独立复核

summary9批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。9完整表行、48统计单元、147数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前无真实大小confirmation pair，D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。新版自然功能表标题已明确shared/两Actor平均，resource_scope已明确last_observed快照；数值未改。

报告script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `d93259aa09baebbea8d0bb5c9d4d45243e314e39cc5b351855608373e3beec1b`；report `3fb1534b6c6f360e6ab75595bcb0ac8f29ee96fc32c975113a198cce2299395c`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。

## 大小模型新32确认材料的独立配对

当前2个同family/stage的C32 pair已独立封存；实际运行contexts逐字一致。本次新native逐context large−small的vector与bootstrap910在打开该批author analysis前写入seal，发现n16不与C32配对。不同checkpoint recipe不是因果scaling law。

| Pair | 固定读数 | Large−small [95% paired CI] |
|---|---|---|
| qwen32_mechanism | A_formation_signed | 0.324514 [-0.149895, 0.810698] |
| qwen32_mechanism | A_formation_absolute | 0.484959 [0.0256545, 0.945314] |
| qwen32_mechanism | B_reading_signed | -0.502511 [-1.16083, 0.160483] |
| qwen32_mechanism | B_reading_absolute | -0.154925 [-0.751622, 0.455646] |
| qwen32_mechanism | label_interface_signed | 0.120315 [-0.470635, 0.732267] |
| qwen32_mechanism | label_interface_absolute | 0.184197 [-0.385392, 0.784987] |
| qwen32_mechanism | answer_K_signed | -0.219378 [-0.753467, 0.319236] |
| qwen32_mechanism | answer_K_absolute | -0.219378 [-0.753467, 0.319236] |
| qwen32_mechanism | answer_relation_signed | -0.106343 [-0.300782, 0.0673443] |
| qwen32_mechanism | answer_relation_absolute | -0.149144 [-0.311523, 0.0013804] |
| qwen32_native | native_answer_removal_signed | 0.210239 [-0.251162, 0.670078] |
| qwen32_native | native_answer_removal_absolute | 0.38106 [-0.163706, 0.950705] |
| qwen32_native | native_restricted_restore_signed | 0.105438 [-0.470388, 0.714444] |
| qwen32_native | native_restricted_restore_absolute | 0.105438 [-0.470388, 0.714444] |
| qwen32_native | gate_answer_removal_signed | 0.674644 [-0.0100294, 1.39626] |
| qwen32_native | gate_answer_removal_absolute | 0.615668 [-0.0625128, 1.30595] |
| qwen32_native | gate_restricted_restore_signed | -1.36822 [-2.29903, -0.47407] |
| qwen32_native | gate_restricted_restore_absolute | -1.40708 [-2.18184, -0.655059] |

双private差值同报为secondary，不筛模型；完整stage仍保留全部43/64/85接口、instruction和K/KV/V固定系数1重建。没有独立GPU重跑。
本次pre-author配对seal `79899f2586461ced44e438fc0b7abc5c46848151903810d088a112a25533d233` 已另存 independent_paired_raw_2026-10-12.json。

## 当前作者 10/18 PARTIAL 报告独立复核

summary10批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。10完整表行、66统计单元、196数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前1个实际大小confirmation pair、10个配对表行已核对；D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。新版自然功能表标题已明确shared/两Actor平均，resource_scope已明确last_observed快照；数值未改。

报告script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `8520b20ffb264e6476a49858ebbf9a7e0c769719dd3ea1b85ae65a47f40a61e4`；report `8eeef2e73dedc958e72c25e935a98eeee8c35da6caed2907053d835c2616c4cf`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。

## 当前作者 11/18 PARTIAL 报告独立复核

summary11批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。11完整表行、77统计单元、229数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前2个实际大小confirmation pair、18个配对表行已核对；D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。新版自然功能表标题已明确shared/两Actor平均，resource_scope已明确last_observed快照；数值未改。

报告script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `95d864ca21136ebb20a3e32a916fbad775e7f132b0e397cd36b922a53336fcef`；report `1662000dc2fae78b35b1538b8eae2d8ba946bd05ec0da71ccbbf3ca684b7b1fc`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。

## 三原核心读数图的展示校对

CSV/manifest与已封summary/raw逐项一致：8/12完整confirmation点，24个mean/CI数字误差0。Q32 function及L70三点为pending，CSV数字栏留空，图上只有灰文字，没有0位置的占位点。PNG已视检，模型行、点/误差条和nats/pp单位对应。

上下文只在同family、同stage内匹配；机制和自然function使用不同seed的SST材料，native使用controlled restaurant sentiment，不是所有panel/family共享一个dataset。function读数为shared、full vocabulary、两Actor及origin/cross等权平均gain，不是joint。建议在独立图caption/轴明确这些范围；这是展示说明，不改变指标或实验门槛。

plot script `2818a0e340c9f41dc97bfabb03458b11fb8cacfb836c3d063e24095fd76f9164`；CSV `8df221dff1dd949bf62f291e4344bcba072707e9b715a4e030d0413a7fc628e4`；manifest `9533b5852697452a40de4cc9bacad73b8bc2d1f0c14613e98362603f90cf821c`。不构建新scaling law或拟合，不运行GPU。

### 图范围说明修订后的再绑定

新版footnote已明确within each family and stage；manifest已明确mechanism/function分别采样SST、native为controlled restaurant，以及function为shared/full/two-Actor mean而非joint。PNG重新视检通过。CSV哈希不变，保留原24数字零误差校对，不重复raw。

script `273f8535e13927b62fc7639ea489e0a6ba193a3a3fe989f6a763a8c03cc876b2`；manifest `a2968abb56b5f6c724e500e6bdf7614f4d3a51ecbe86a9810d6a11759a169841`；PNG `ea38e5cce4c29051a3b8a37100c7056242100ac37d2c16d63d685eecadb7e967`。旧图snapshot与全部raw digest保留。

## 当前作者 12/18 PARTIAL 报告独立复核

summary12批嵌入的analysis/run/raw hash与已封独立结果一致；自然function的全部12 policy/18 contrast full-output字段按原origin/cross×A/B×8query权重独立重算。12完整表行、100统计单元、304数值呈现逐项一致。pairs函数逐context公式及stat回归原冻结读数；目前3个实际大小confirmation pair、36个配对表行已核对；D16不与小C32配对。

科学stage小时与worker驻留快照计数一致，每worker只计一次；运行中job的快照只覆盖last_observed_at，不代表报告生成时刻所有新增驻留。mean Actor accuracy不等同joint；shared表面other-source-word零不能识别provenance。新版自然功能表标题已明确shared/两Actor平均，resource_scope已明确last_observed快照；数值未改。

报告script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `7df5f43cd2e19d2c3894272541069a7ca5e4eff7dc952a1cbbbde5eecbebec7d`；report `9891e09a8128a032bacdb894a3b8ba38bd1d71ebe7739348d85b804352f03046`。继承bootstrap910/reconstruction109910的卡说明是澄清，不是科学CI变更；没有新理论资格或GPU重跑。

## 第12批完整确认的读序与实际范围

Qwen3-32B function confirmation 为32×85×8=21760评分；64层/2GPU、FP32/eager/TF32=False，CPU上下文字节一致。18套prefix图每层实际消费32次，共36864层调用；cache深复制ptr/seq-length保护沿用冻结实现。query图沿用同4D-mask接口并核graph-zero/numeric地板，没有把prefix hook计数冒称独立query-hook记录。cached/full1.9073486328125e−5，native cache self及graph-zero0；实际device map为层0–30在logical GPU0，31–63在logical GPU1，没有CPU/disk模型offload。

先保存新增raw及全部三组Qwen confirmation配对，再打开新author analysis；1893数值最大误差0。pre-author raw快照路径及SHA、第三配对文件SHA见JSON twelfth_stage_pre_author_snapshot及独立12_stage_pre_author_seal文件。旧两组配对seal保留在11_stages文件。

shared/full两Actor平均targeted−native +7.71484 [5.76172,9.57031]pp；targeted平均95.7031%，joint92.1875%。A+7.42188/B+8.00781pp、opposite+15.8203pp、same−.390625pp CI跨0。targeted−all +20.4102 [18.1641,22.3633]pp；query-only +5.85938 [4.19922,7.51953]pp。far/all-cross候选95.3125%但full52.6367%、joint9.96094%；全部接口/Actor/world/scope/private及other-word辅助保留。

Q8/Q32 function同32材料逐字配对，SHA8ba72167d5b80fec9aca38bd4b6ad17cd50923a5147414ac3820e944bed9566b。每context先large−small再bootstrap910；targeted gain差+.0976563 [−3.22266,3.32031]pp，不宣称gain随规模增大；query-only差+8.39844 [3.80859,13.08594]pp。18个function配对原向量及双private分组均保存。

当前Q32 discovery/confirmation三stage和两个8B新32锚点完整，12/18、336contexts、172032scores；剩余六stage为Llama70。以上是同链核心读数的扩规模实测，没有新资格、拟合或主张等级变化。

## 三原核心读数图的展示校对

CSV/manifest与已封summary/raw逐项一致：9/12完整confirmation点，27个mean/CI数字误差0。尚未完成的点为pending，CSV数字栏留空，图上只有灰文字，没有0位置的占位点。模型行、点/误差条和nats/pp单位随后视检核对。

上下文只在同family、同stage内匹配；机制和自然function使用不同seed的SST材料，native使用controlled restaurant sentiment，不是所有panel/family共享一个dataset。function读数为shared、full vocabulary、两Actor及origin/cross等权平均gain，不是joint。图footnote及manifest已明确这些范围；这是展示说明，不改变指标或实验门槛。

plot script `273f8535e13927b62fc7639ea489e0a6ba193a3a3fe989f6a763a8c03cc876b2`；CSV `2fbfafa1481cb0ea52f6acde74358ba5e797b8c163b5eb823cc64c6dd9f26c6a`；manifest `ed6dd09c2daed027237cd0466ca958614309cf86faec050d0505729def78f4ae`。不构建新scaling law或拟合，不运行GPU。

## 第13批：Llama-3.1-70B discovery mechanism 完整raw-first封存

16contexts ×43条件×8query =5504评分；80层、4GPU，FP32/eager/TF32=False；CPU上下文字节相同，冻结engine/parent/dispatch/protocol和model pin一致。实际edge全层调用12880；cached/full1.33514404e-05、self0、layer0 sender KV固定0。
原科学冻结commit 0a50bbb193a8ccada0a090b361fc29aad6bbe617，本批operational_launch标记058ea8f99c842d269d0dcf7496d323d3c833add3；与完成commit的四科学源逐字hash相同，双记资源launch与科学freeze，不把元数据指针差异当科学变更。
新增raw独立pre-author seal：40b36c6c5ff13ff744bd41bbffd558d7f7f197d6d5f7c96dc398776fee8101e9；原12stage JSON/MD字节封存另存。之后author analysis比较1041个数值，最大误差6.66133815e-15；本批独立会话没有先看stdout/authoranalysis。

作者读序另披露：root在tail进度时看到了最后三条relation summary；不能把本批写成所有参与者全盲。

| 冻结读数 | 均值 [95% context CI] |
|---|---|
| A_formation_B_shared/signed_rule_effect | 0.993142 [0.612124, 1.37253] |
| A_formation_B_shared/absolute_rule_effect | 0.993142 [0.612124, 1.37253] |
| A_formation_B_far/signed_rule_effect | 1.34484 [0.861377, 1.8677] |
| A_formation_B_far/absolute_rule_effect | 0.929003 [0.411527, 1.51058] |
| B_reading_A_shared/signed_rule_effect | 2.82914 [1.96758, 3.55419] |
| B_reading_A_shared/absolute_rule_effect | 2.62846 [1.7687, 3.36354] |
| B_reading_A_far/signed_rule_effect | 3.18084 [2.34473, 4.02891] |
| B_reading_A_far/absolute_rule_effect | 2.56432 [1.87561, 3.23753] |
| stage_interaction/signed_rule_effect | -0.351696 [-0.755948, 0.0359253] |
| stage_interaction/absolute_rule_effect | 0.0641391 [-0.334302, 0.516884] |
| label_effect_B_shared/signed_rule_effect | 0.260052 [-0.0630248, 0.613894] |
| label_effect_B_shared/absolute_rule_effect | 0.260052 [-0.0630248, 0.613894] |
| label_effect_B_far/signed_rule_effect | 1.0988 [0.668547, 1.54653] |
| label_effect_B_far/absolute_rule_effect | 0.886115 [0.457406, 1.35843] |
| edge_K_B_shared/signed_rule_effect | 0.664143 [0.468511, 0.878865] |
| edge_K_B_shared/absolute_rule_effect | 0.664143 [0.468511, 0.878865] |
| edge_K_B_far/signed_rule_effect | 0.312842 [0.026647, 0.617953] |
| edge_K_B_far/absolute_rule_effect | 0.28635 [-0.00722878, 0.599353] |
| relation/full_native/absolute_effect | 3.82987 [3.16001, 4.41451] |
| relation/full_native/signed_effect | 4.19896 [3.72713, 4.64954] |
| relation/label_native/absolute_effect | 1.48425 [0.984937, 1.97108] |
| relation/label_native/signed_effect | -1.50297 [-2.01073, -0.984342] |
| relation/answer_native/absolute_effect | 0.236624 [0.116472, 0.368284] |
| relation/answer_native/signed_effect | -0.22883 [-0.382258, -0.0850273] |
| relation/cross_KV_minus_K/absolute_effect | 0.183201 [0.0544286, 0.328373] |
| relation/cross_KV_minus_K/signed_effect | -0.210101 [-0.356627, -0.0752956] |
| relation/cross_KV_minus_V/absolute_effect | 0.129157 [0.0185824, 0.241746] |
| relation/cross_KV_minus_V/signed_effect | -0.22977 [-0.307847, -0.157769] |
| relation/relation_f0r1/absolute_effect | 2.67857 [2.17804, 3.10791] |
| relation/relation_f0r1/signed_effect | 2.67857 [2.17804, 3.10791] |
| relation/relation_f1r0/absolute_effect | 1.60298 [1.09072, 2.09753] |
| relation/relation_f1r0/signed_effect | -1.54889 [-2.08228, -0.988765] |
| relation/relation_label_cross_native/absolute_effect | 1.70341 [1.18302, 2.20047] |
| relation/relation_label_cross_native/signed_effect | -1.66387 [-2.1909, -1.1039] |
| relation/relation_answer_cross_kv_native/absolute_effect | 0.31453 [0.179138, 0.471297] |
| relation/relation_answer_cross_kv_native/signed_effect | -0.2601 [-0.436103, -0.0974009] |
| relation/relation_answer_cross_k_native/absolute_effect | 0.131328 [0.0742107, 0.198673] |
| relation/relation_answer_cross_k_native/signed_effect | -0.0499996 [-0.139009, 0.0325798] |
| relation/relation_answer_cross_v_native/absolute_effect | 0.185373 [0.123973, 0.260211] |
| relation/relation_answer_cross_v_native/signed_effect | -0.0303308 [-0.144766, 0.0806641] |

| 重建目标/通道 | raw r / RMSE / zero RMSE | rule双差 r / RMSE / zero |
|---|---|---|
| label_interface_B0_k | 0.448317 / 0.70924 / 0.704812 | 0.588066 / 0.882893 / 1.05084 |
| label_interface_B0_kv | 0.542122 / 0.632326 / 0.704812 | 0.64207 / 0.82772 / 1.05084 |
| label_interface_B0_v | 0.503417 / 0.615035 / 0.704812 | 0.619948 / 0.863859 / 1.05084 |
| all_A_formation_B0_k | 0.720458 / 0.63726 / 0.91485 | 0.824758 / 0.897194 / 1.48525 |
| all_A_formation_B0_kv | 0.78028 / 0.589749 / 0.91485 | 0.86153 / 0.855114 / 1.48525 |
| all_A_formation_B0_v | 0.634532 / 0.771246 / 0.91485 | 0.722885 / 1.24443 / 1.48525 |
| label_interface_B1_k | 0.765518 / 0.983846 / 1.47212 | 0.721291 / 1.14583 / 1.58362 |
| label_interface_B1_kv | 0.85433 / 0.824622 / 1.47212 | 0.743919 / 1.07539 / 1.58362 |
| label_interface_B1_v | 0.705219 / 1.05943 / 1.47212 | 0.520165 / 1.38228 / 1.58362 |
| all_A_formation_B1_k | 0.7275 / 1.11917 / 1.57854 | 0.711897 / 1.369 / 1.84306 |
| all_A_formation_B1_kv | 0.81383 / 0.976341 / 1.57854 | 0.717072 / 1.33557 / 1.84306 |
| all_A_formation_B1_v | 0.627248 / 1.23424 / 1.57854 | 0.480668 / 1.64304 / 1.84306 |

| 本批single_A/private | candidate / full / label rate |
|---|---|
| False | 1 [1, 1] / 1 [1, 1] / 1 [1, 1] |
| True | 1 [1, 1] / 1 [1, 1] / 1 [1, 1] |

完整43接口、12个固定系数重建、full/output/private双方、固定word关联、native attention全80层均在JSON，保留负向/零向和所有通道。没有新GPU评分、旧12批重算、配置筛选或claim等级改变。本批是固定n16探索；L70 confirmation未完整，不与L8 n32配对。

当前13/18、352contexts、177536scores；科学stage device-hours合计11.9440974，worker驻留另按最后快照记录，不能将运行中快照当最终总资源。

## 作者13-stage报告的新增行展示核对

只核新增L70 discovery mechanism行及metadata：8统计单元、19展示数字、1041嵌入analysis数值与独立seal一致，最大误差6.66133815e-15。旧12批不重算，其raw digest保持原seal；现有3组Qwen n32配对未变，没有L70新pair。总13/18、352contexts、177536scores及science/device-residency快照一致。root stdout读序例外保留，独立会话仍raw-first。

report script fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5；summary 66aeae626722594c7eb3ee78d7bf14237b8efa385b512bb6f4927e2bf8bde409；report f52207579cd3310ed9f66bd255a8fd0120e7258cd6aa2dad45f6517095dae79f。

## 13 批摘要来源重绑定（图仍为 9/12 确认点）

新增 70B n16 是 discovery，不进入确认图。已封的 9 点/27 个均值及 CI 数字与当前 summary、CSV 逐项相等，CSV 和脚本 SHA 不变；三个尚未完成的 70B confirmation 点仍为空值 pending。此次没有重算原 stage 或 CI，未把 pending 当零。当前 manifest `eebe1e21421bac46d3d5f6e193b4837388c5754b8aa9ccc8a921491f64382193` 绑定摘要 `66aeae626722594c7eb3ee78d7bf14237b8efa385b512bb6f4927e2bf8bde409`；旧 manifest 对应审计仍保留在 JSON 历史。

## 第14批：Llama-3.1-70B discovery native 完整raw-first封存

16 contexts ×64条件×8 query =8192评分；80层、4GPU，FP32/eager/TF32=False，沿用同模型驻留。CPU上下文字节/非args预检字段一致，model pin与冻结engine/parent/dispatch/protocol逐字hash一致。实际prefix mask全80层/30组合共38400次消费；cached/full 9.53674316e-06、native mask self 0、独立graph-zero 0。
原科学freeze 0a50bbb193a8ccada0a090b361fc29aad6bbe617，operational launch 058ea8f99c842d269d0dcf7496d323d3c833add3，completion ea3284790912c54b74bb5836080f447f3d09ac7b。这些commit中的四相关科学文件SHA相同；不将disjoint Git同步当实现变化。
新增独立pre-author seal fd86ecfb66ff608c6498af60c0234fb09ab60e7e06e39c69afee34618d157096；13批JSON/MD字节保存另存。之后比较author analysis 1217个有限数值，最大误差0。本会话没有在seal前读本批stdout或authoranalysis；root亦报告本批仅看行数/run是否存在，前第13批stdout例外仍保留。

全部query gold从class/private direction独立复算；名字与实际owner相符，B跨类/类内map均为无固定点双射，输入多重集/标签stream/A不变。shared/far是B词表背景，native/gate另为reading可达图。恢复是在全部B→A形成阻断下仅开放历史B answer→A label严格past边，没有donor。within control同样strict past、self保留；native removal/restore不是恒等重建。

| 固定 contrast | signed [95% context CI] | abs [95% context CI] | excess over within [95% CI] |
|---|---|---|---|
| shared_native_cross_answer_removal | 1.54209 [1.09627, 1.97003] | 1.54209 [1.09627, 1.97003] | 1.48946 [0.877992, 2.06935] |
| shared_native_within_answer_removal | -1.01778 [-1.446, -0.598672] | -1.01778 [-1.446, -0.598672] | -1.27516 [-1.86975, -0.726078] |
| shared_native_cross_vs_within_removal | 2.55987 [2.06511, 3.05854] | 2.55987 [2.06511, 3.05854] | 2.76461 [2.16054, 3.31364] |
| shared_native_all_cross_removal | -1.25335 [-1.81593, -0.746432] | -1.25335 [-1.81593, -0.746432] | -1.27507 [-1.90276, -0.726672] |
| shared_native_answer_path_restoration | -0.439691 [-0.653495, -0.20772] | -0.439691 [-0.653495, -0.20772] | -0.271201 [-0.481207, -0.0657611] |
| shared_native_restoration_residual | -0.813657 [-1.29101, -0.364698] | -0.813657 [-1.29101, -0.364698] | -1.00386 [-1.63493, -0.442601] |
| shared_gate_cross_answer_removal | 0.766491 [0.489261, 1.08167] | 0.708095 [0.395207, 1.05545] | 0.515634 [0.134803, 0.934864] |
| shared_gate_within_answer_removal | -1.24537 [-1.81001, -0.713042] | -1.22086 [-1.78898, -0.691925] | -1.29456 [-1.89891, -0.716646] |
| shared_gate_cross_vs_within_removal | 2.01186 [1.41604, 2.59499] | 1.92896 [1.30087, 2.55539] | 1.81019 [1.15993, 2.45507] |
| shared_gate_all_cross_removal | 1.6781 [1.13572, 2.25014] | 1.70261 [1.18851, 2.26164] | 1.21487 [0.657576, 1.81125] |
| shared_gate_answer_path_restoration | 1.01095 [0.637201, 1.40072] | 1.01525 [0.645488, 1.40289] | 0.772003 [0.41015, 1.15797] |
| shared_gate_restoration_residual | 0.66715 [0.110249, 1.2468] | 0.687363 [0.141097, 1.25869] | 0.442866 [-0.200949, 1.06668] |
| far_native_cross_answer_removal | -0.0255831 [-0.1232, 0.0667364] | 0.0448902 [-0.0448825, 0.140615] | 0.0795805 [-0.0539946, 0.212933] |
| far_native_within_answer_removal | 0.0794373 [-0.248604, 0.405373] | -0.329077 [-0.609102, -0.067357] | 0.0112374 [-0.278536, 0.276627] |
| far_native_cross_vs_within_removal | -0.10502 [-0.419581, 0.228777] | 0.373967 [0.120255, 0.63957] | 0.0683431 [-0.188988, 0.336226] |
| far_native_all_cross_removal | 0.00287708 [-0.428217, 0.444824] | -0.492481 [-0.838865, -0.170879] | -0.463434 [-0.807824, -0.145595] |
| far_native_answer_path_restoration | 0.0372653 [-0.140481, 0.237609] | -0.139106 [-0.301645, 0.0500409] | -0.113251 [-0.280662, 0.0690401] |
| far_native_restoration_residual | -0.0343882 [-0.430831, 0.3514] | -0.353376 [-0.695461, -0.0362503] | -0.350183 [-0.695958, -0.0336465] |
| far_gate_cross_answer_removal | -0.0555224 [-0.151132, 0.0327841] | 0.00333276 [-0.0807507, 0.0876137] | 0.0415713 [-0.0516119, 0.140568] |
| far_gate_within_answer_removal | 0.112615 [-0.209081, 0.435969] | -0.456223 [-0.672815, -0.246781] | -0.220159 [-0.449301, 0.0028121] |
| far_gate_cross_vs_within_removal | -0.168137 [-0.4911, 0.157555] | 0.459556 [0.242621, 0.680115] | 0.26173 [0.054695, 0.48617] |
| far_gate_all_cross_removal | 0.0526787 [-0.175273, 0.284778] | 0.384463 [0.255477, 0.520359] | 0.256076 [0.115523, 0.408916] |
| far_gate_answer_path_restoration | -0.0631117 [-0.146629, 0.0133317] | 0.115468 [0.0591835, 0.186602] | 0.02633 [-0.0274733, 0.0819868] |
| far_gate_restoration_residual | 0.11579 [-0.13659, 0.372315] | 0.268995 [0.115144, 0.428911] | 0.229746 [0.080799, 0.392296] |
| namespace_rule_native_native | 3.73253 [3.11872, 4.36001] | 3.73253 [3.11872, 4.36001] | — |
| namespace_rule_native_cross_answer_off | 2.16486 [1.71976, 2.6569] | 2.16486 [1.71976, 2.6569] | — |
| namespace_rule_native_within_answer_off | 4.82974 [4.19911, 5.43782] | 4.82974 [4.19911, 5.43782] | — |
| namespace_rule_native_all_B_off | 4.98876 [4.20935, 5.85064] | 4.98876 [4.20935, 5.85064] | — |
| namespace_rule_native_answer_only_restore | 4.5118 [3.81074, 5.27786] | 4.5118 [3.81074, 5.27786] | — |
| namespace_rule_gate_native | 1.62542 [1.161, 2.13035] | 1.62542 [1.161, 2.13035] | — |
| namespace_rule_gate_cross_answer_off | 0.803411 [0.517065, 1.14315] | 0.803411 [0.517065, 1.14315] | — |
| namespace_rule_gate_within_answer_off | 2.98341 [2.30059, 3.65236] | 3.02089 [2.39615, 3.65851] | — |
| namespace_rule_gate_all_B_off | 0 [0, 0] | 0 [0, 0] | — |
| namespace_rule_gate_answer_only_restore | 1.07406 [0.682957, 1.47419] | 1.08459 [0.701207, 1.47954] | — |

| 全部 rule response | signed [95% CI] | abs [95% CI] | within signed [95% CI] | within abs [95% CI] |
|---|---|---|---|---|
| shared_native_native | 3.81819 [3.28744, 4.30128] | 3.81819 [3.28744, 4.30128] | 0.0261054 [-0.293715, 0.319349] | 0.513552 [0.347942, 0.701102] |
| shared_native_cross_answer_off | 2.2761 [1.82551, 2.75901] | 2.2761 [1.82551, 2.75901] | -0.221604 [-0.546291, 0.064537] | 0.460916 [0.246773, 0.712769] |
| shared_native_within_answer_off | 4.83597 [4.59418, 5.07511] | 4.83597 [4.59418, 5.07511] | 0.0404397 [-0.117617, 0.214059] | 0.256169 [0.154619, 0.372674] |
| shared_native_all_B_off | 5.07154 [4.77228, 5.39404] | 5.07154 [4.77228, 5.39404] | 0.0606241 [-0.220644, 0.339704] | 0.491834 [0.338229, 0.648681] |
| shared_native_answer_only_restore | 4.63185 [4.4085, 4.88166] | 4.63185 [4.4085, 4.88166] | 0.11568 [-0.0593113, 0.293852] | 0.323344 [0.221959, 0.433329] |
| shared_gate_native | 1.6781 [1.13572, 2.25014] | 1.70261 [1.18851, 2.26164] | -0.279569 [-0.561975, 0.0504545] | 0.48774 [0.271825, 0.731762] |
| shared_gate_cross_answer_off | 0.911612 [0.498944, 1.39568] | 0.994515 [0.640488, 1.44248] | -0.0690094 [-0.235307, 0.143858] | 0.295279 [0.180633, 0.441567] |
| shared_gate_within_answer_off | 2.92347 [2.22109, 3.61265] | 2.92347 [2.22109, 3.61265] | 0.076244 [-0.192378, 0.393686] | 0.414045 [0.206125, 0.650235] |
| shared_gate_all_B_off | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| shared_gate_answer_only_restore | 1.01095 [0.637201, 1.40072] | 1.01525 [0.645488, 1.40289] | -0.071569 [-0.223291, 0.0720963] | 0.243244 [0.158556, 0.341607] |
| far_native_native | 0.0856623 [-0.265134, 0.434024] | 0.62692 [0.453415, 0.801082] | 0.0703152 [-0.0554029, 0.198347] | 0.213123 [0.133105, 0.297168] |
| far_native_cross_answer_off | 0.111245 [-0.245634, 0.46415] | 0.58203 [0.371726, 0.800252] | 0.0093056 [-0.143422, 0.169905] | 0.247813 [0.14879, 0.354613] |
| far_native_within_answer_off | 0.00622505 [-0.566285, 0.59924] | 0.955997 [0.629912, 1.30985] | 0.337796 [0.0816181, 0.584477] | 0.553437 [0.421546, 0.681964] |
| far_native_all_B_off | 0.0827852 [-0.590094, 0.689668] | 1.1194 [0.790012, 1.46096] | -0.0245925 [-0.203171, 0.147701] | 0.24217 [0.124826, 0.382346] |
| far_native_answer_only_restore | 0.120051 [-0.482065, 0.681125] | 0.980296 [0.659841, 1.31861] | 0.0906049 [-0.0608799, 0.237133] | 0.216315 [0.11372, 0.337654] |
| far_gate_native | 0.0526787 [-0.175273, 0.284778] | 0.384463 [0.255477, 0.520359] | 0.0286428 [-0.043672, 0.100162] | 0.128387 [0.0931875, 0.16637] |
| far_gate_cross_answer_off | 0.108201 [-0.110967, 0.330953] | 0.38113 [0.251907, 0.523174] | -0.0240239 [-0.125868, 0.0745411] | 0.166625 [0.107524, 0.227354] |
| far_gate_within_answer_off | -0.0599362 [-0.569614, 0.451806] | 0.840686 [0.547686, 1.16405] | 0.184349 [-0.0477218, 0.418655] | 0.364452 [0.202999, 0.546482] |
| far_gate_all_B_off | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| far_gate_answer_only_restore | -0.0631117 [-0.146629, 0.0133317] | 0.115468 [0.0591835, 0.186602] | 0.0432288 [-0.00457653, 0.0904222] | 0.0891378 [0.0629995, 0.118376] |

| A private/control (每方向8 context) | polarity | candidate [95% CI] | full [95% CI] | signed gold margin [95% CI] |
|---|---|---|---|---|
| single_A | False | 1 [1, 1] | 1 [1, 1] | 4.00926 [3.86374, 4.15213] |
| single_A | True | 1 [1, 1] | 1 [1, 1] | 4.08706 [3.69043, 4.44095] |
| single_A_within_answer_off | False | 1 [1, 1] | 0.921875 [0.8125, 1] | 5.83511 [5.50232, 6.19436] |
| single_A_within_answer_off | True | 1 [1, 1] | 1 [1, 1] | 5.44639 [4.78151, 6.12809] |
| origin_instruction | False | 0.984375 [0.953125, 1] | 0.984375 [0.953125, 1] | 2.94802 [2.41587, 3.42561] |
| origin_instruction | True | 1 [1, 1] | 1 [1, 1] | 3.11185 [2.72781, 3.51582] |
| cross_instruction | False | 1 [1, 1] | 1 [1, 1] | 4.60468 [4.27459, 4.91868] |
| cross_instruction | True | 1 [1, 1] | 1 [1, 1] | 4.88754 [4.65894, 5.08696] |

全部64接口的candidate/full/label率与gold margin、两个private方向，以及原20k独立bootstrap均保留在JSON。prefix mask实际消费来自全层hook assert；query可达图与缓存消费由冻结源、pristine data_ptr/length assert和数值/graph-zero核对，本批没有独立query hook计数，也没有第二次GPU运行。

当前14/18、368 contexts、185728 scores，stage device-hours合计14.9773816。新增批为固定n16 discovery，70B function与全部confirmation仍待完整；没有新增配对或确认图点，也未重算旧13批。

## 作者14-stage报告的新增行展示核对

仅核新增L70 discovery native行及metadata：3统计单元、9展示数字、1217个嵌入analysis数值与独立seal完全一致，最大误差0。旧13批不重算：其summary run对象逐项相同、原53行展示逐字保留、raw digests不变；三个Qwen n32配对对象相同，没有新增L70 pair或确认图点。总14/18、368contexts、185728scores及科学stage/驻留快照一致；已封图仍为原9/12确认点，不据发现批新增点。

report script `fd55a52ba4ee42717ba4d385276369227eeae9d87fcef28ef373ee0564263df5`；summary `d706568667acbcf715e51a63b623971bc8c4057b185886e2928d68f63a8bd8cd`；report `22a945a69c4d4a2269142e242b777474767c7b502e979c038b481743239e3976`。

## 14 批摘要来源重绑定（图仍为 9/12 确认点）

新增 70B n16 是 discovery，不进入确认图。已封的 9 点/27 个均值及 CI 数字与当前 summary、CSV 逐项相等，CSV 和脚本 SHA 不变；三个尚未完成的 70B confirmation 点仍为空值 pending。此次没有重算原 stage 或 CI，未把 pending 当零。当前 manifest `a62fe953d5cdfe69bf22eca7997834820f7a52f3723f918dc31a2b77806846cb` 绑定摘要 `d706568667acbcf715e51a63b623971bc8c4057b185886e2928d68f63a8bd8cd`；旧 manifest 对应审计仍保留在 JSON 历史。

## 第15批：Llama-3.1-70B discovery function 完整raw-first封存

16 contexts ×85条件×8 queries=10880评分；80层、4GPU、FP32/eager/TF32=False，model reused。冻结engine/parent/dispatch/protocol与model pin一致，CPU contexts/预检字段逐字一致；18个prefix/80层共23040实际mask消费。cached/full 2.28881836e-05，native mask self/graph-zero均0，pristine cache data_ptr/sequence length核对保持。
原科学freeze 0a50bbb193a8ccada0a090b361fc29aad6bbe617；launch 058ea8f99c842d269d0dcf7496d323d3c833add3；completion 3d0c6c3bbd65c6455aa730f164dbe3103e466c0a，相关四科学源SHA逐字一致。新增pre-author raw seal 84dca94bed62dc88d3ee436e980c39d40b4720c145fe5704d85f557eda70171f；原14stage JSON/MD另存，旧raw digests/配对/确认图不重算。之后比author analysis 1893个数值，最大误差0。

原始gold从q sentiment class/private convention重算；两namespace4个独立word IDs、两个private方向各8contexts。B跨/类内是无固定点双射、labelstream/Source/multiset/A固定；两个Actor在同一完整cache上query。官方SST split/Arrow gold/实际token布局由前评分CPU审计与本批字节匹配核对；无模型结果筛选。

| namespace/policy/scope | candidate mean [CI] | full mean [CI] | full joint both-correct [CI] | full A / B |
|---|---|---|---|---|
| shared_normal_native | 0.867188 [0.832031, 0.902344] | 0.867188 [0.832031, 0.902344] | 0.738281 [0.667969, 0.808594] | 0.921875 [0.875, 0.964844] / 0.8125 [0.742188, 0.875] |
| shared_normal_gate | 0.972656 [0.949219, 0.992188] | 0.972656 [0.949219, 0.992188] | 0.945312 [0.898438, 0.984375] | 0.972656 [0.9375, 1] / 0.972656 [0.9375, 0.996094] |
| shared_answer_cross_off_native | 0.984375 [0.964844, 1] | 0.984375 [0.964844, 1] | 0.972656 [0.941406, 1] | 0.980469 [0.957031, 1] / 0.988281 [0.96875, 1] |
| shared_answer_cross_off_gate | 0.986328 [0.96875, 1] | 0.986328 [0.96875, 1] | 0.972656 [0.9375, 1] | 0.992188 [0.976562, 1] / 0.980469 [0.953125, 1] |
| shared_all_cross_off_native | 0.75 [0.736328, 0.763672] | 0.75 [0.736328, 0.763672] | 0.511719 [0.492188, 0.535156] | 0.820312 [0.753906, 0.882812] / 0.679688 [0.609375, 0.753906] |
| shared_all_cross_off_gate | 0.996094 [0.988281, 1] | 0.996094 [0.988281, 1] | 0.992188 [0.976562, 1] | 0.992188 [0.976562, 1] / 1 [1, 1] |
| far_normal_native | 0.984375 [0.966797, 0.996094] | 0.970703 [0.947266, 0.990234] | 0.949219 [0.910156, 0.980469] | 0.984375 [0.960938, 1] / 0.957031 [0.921875, 0.984375] |
| far_normal_gate | 0.96875 [0.949219, 0.984375] | 0.96875 [0.949219, 0.984375] | 0.941406 [0.910156, 0.972656] | 0.984375 [0.960938, 1] / 0.953125 [0.925781, 0.980469] |
| far_answer_cross_off_native | 0.986328 [0.96875, 0.998047] | 0.980469 [0.960938, 0.996094] | 0.96875 [0.941406, 0.992188] | 0.988281 [0.96875, 1] / 0.972656 [0.949219, 0.992188] |
| far_answer_cross_off_gate | 0.974609 [0.951172, 0.992188] | 0.974609 [0.951172, 0.992188] | 0.953125 [0.914062, 0.984375] | 0.992188 [0.976562, 1] / 0.957031 [0.921875, 0.984375] |
| far_all_cross_off_native | 0.990234 [0.976562, 1] | 0.511719 [0.494141, 0.535156] | 0.0390625 [0.0078125, 0.0820312] | 0.707031 [0.550781, 0.847656] / 0.316406 [0.167969, 0.480469] |
| far_all_cross_off_gate | 0.988281 [0.974609, 0.998047] | 0.988281 [0.974609, 0.998047] | 0.980469 [0.960938, 0.996094] | 0.992188 [0.976562, 1] / 0.984375 [0.96875, 0.996094] |

| full-output contrast | mean [95% CI] | A [95% CI] | B [95% CI] | opposite [95% CI] | same [95% CI] |
|---|---|---|---|---|---|
| shared_answer_cross_off_minus_normal_native | 0.117188 [0.0800781, 0.154297] | 0.0585938 [0.0234375, 0.0976562] | 0.175781 [0.105469, 0.253906] | 0.234375 [0.160156, 0.308594] | 0 [0, 0] |
| shared_all_cross_off_minus_normal_native | -0.117188 [-0.154297, -0.0800781] | -0.101562 [-0.183594, -0.0273438] | -0.132812 [-0.230469, -0.0273438] | -0.234375 [-0.308594, -0.160156] | 0 [0, 0] |
| shared_answer_minus_all_native | 0.234375 [0.21875, 0.25] | 0.160156 [0.0898438, 0.234473] | 0.308594 [0.238281, 0.375] | 0.46875 [0.4375, 0.5] | 0 [0, 0] |
| shared_answer_cross_off_minus_normal_gate | 0.0136719 [0.00195312, 0.03125] | 0.0195312 [0, 0.0546875] | 0.0078125 [0, 0.0195312] | 0.0273438 [0.00390625, 0.0625] | 0 [0, 0] |
| shared_all_cross_off_minus_normal_gate | 0.0234375 [0.00585938, 0.0449219] | 0.0195312 [0, 0.0546875] | 0.0273438 [0.00390625, 0.0625] | 0.0429688 [0.0078125, 0.0859375] | 0.00390625 [0, 0.0117188] |
| shared_answer_minus_all_gate | -0.00976562 [-0.0234375, 0] | 0 [0, 0] | -0.0195312 [-0.046875, 0] | -0.015625 [-0.0429688, 0] | -0.00390625 [-0.0117188, 0] |
| shared_query_isolation_normal | 0.105469 [0.0566406, 0.150391] | 0.0507812 [-0.0078125, 0.101562] | 0.160156 [0.0742188, 0.246094] | 0.210938 [0.109375, 0.304688] | 0 [-0.0117188, 0.0117188] |
| shared_query_isolation_answer_cross_off | 0.00195312 [-0.0136719, 0.015625] | 0.0117188 [0, 0.03125] | -0.0078125 [-0.0351562, 0.0117188] | 0.00390625 [-0.0273438, 0.03125] | 0 [-0.0117188, 0.0117188] |
| shared_query_isolation_all_cross_off | 0.246094 [0.234375, 0.255859] | 0.171875 [0.105469, 0.242188] | 0.320312 [0.246094, 0.390625] | 0.488281 [0.464844, 0.507812] | 0.00390625 [0, 0.0117188] |
| shared_answer_by_query_interaction | -0.103516 [-0.146484, -0.0585938] | -0.0390625 [-0.0898438, 0.0195312] | -0.167969 [-0.246094, -0.09375] | -0.207031 [-0.292969, -0.117188] | 0 [0, 0] |
| far_answer_cross_off_minus_normal_native | 0.00976562 [0.00195312, 0.0195312] | 0.00390625 [0, 0.0117188] | 0.015625 [0, 0.0351562] | 0.0117188 [0, 0.0234375] | 0.0078125 [0, 0.0234375] |
| far_all_cross_off_minus_normal_native | -0.458984 [-0.480469, -0.433594] | -0.277344 [-0.433594, -0.140625] | -0.640625 [-0.785156, -0.480469] | -0.449219 [-0.472656, -0.425781] | -0.46875 [-0.5, -0.425781] |
| far_answer_minus_all_native | 0.46875 [0.445312, 0.486328] | 0.28125 [0.140625, 0.441406] | 0.65625 [0.492188, 0.804688] | 0.460938 [0.4375, 0.484375] | 0.476562 [0.445312, 0.5] |
| far_answer_cross_off_minus_normal_gate | 0.00585938 [-0.00390625, 0.015625] | 0.0078125 [0, 0.0234375] | 0.00390625 [-0.0078125, 0.015625] | 0.0078125 [0, 0.0195312] | 0.00390625 [-0.0078125, 0.015625] |
| far_all_cross_off_minus_normal_gate | 0.0195312 [0.0078125, 0.03125] | 0.0078125 [0, 0.0234375] | 0.03125 [0.0117188, 0.0546875] | 0.03125 [0.0078125, 0.0585938] | 0.0078125 [-0.0078125, 0.0234375] |
| far_answer_minus_all_gate | -0.0136719 [-0.0273438, -0.00390625] | 0 [0, 0] | -0.0273438 [-0.0546875, -0.0078125] | -0.0234375 [-0.0546875, 0] | -0.00390625 [-0.015625, 0.0078125] |
| far_query_isolation_normal | -0.00195312 [-0.0253906, 0.0234375] | 0 [-0.0234375, 0.0234375] | -0.00390625 [-0.0429688, 0.0429688] | -0.0117188 [-0.0430664, 0.015625] | 0.0078125 [-0.0195312, 0.046875] |
| far_query_isolation_answer_cross_off | -0.00585938 [-0.0234375, 0.0117188] | 0.00390625 [0, 0.0117188] | -0.015625 [-0.0507812, 0.015625] | -0.015625 [-0.046875, 0.0078125] | 0.00390625 [-0.015625, 0.0273438] |
| far_query_isolation_all_cross_off | 0.476562 [0.455078, 0.494141] | 0.285156 [0.140625, 0.445312] | 0.667969 [0.5, 0.820312] | 0.46875 [0.445312, 0.488281] | 0.484375 [0.457031, 0.5] |
| far_answer_by_query_interaction | -0.00390625 [-0.015625, 0.0078125] | 0.00390625 [-0.0117188, 0.0234375] | -0.0117188 [-0.03125, 0] | -0.00390625 [-0.015625, 0.0078125] | -0.00390625 [-0.0234375, 0.015625] |
| targeted_gain_shared_minus_far_native | 0.107422 [0.0703125, 0.146484] | 0.0546875 [0.0195312, 0.09375] | 0.160156 [0.0898438, 0.234375] | 0.222656 [0.152344, 0.296875] | -0.0078125 [-0.0234375, 0] |
| targeted_gain_shared_minus_far_gate | 0.0078125 [-0.0078125, 0.0273438] | 0.0117188 [-0.0195312, 0.0507812] | 0.00390625 [-0.0078125, 0.015625] | 0.0195312 [-0.0078125, 0.0546875] | -0.00390625 [-0.015625, 0.0078125] |

| 本批private函数（每方向8contexts） | direction | candidate [CI] | full [CI] | signed gold margin [CI] |
|---|---|---|---|---|
| single_A | False | 0.984375 [0.953125, 1] | 0.984375 [0.953125, 1] | 3.96597 [3.66442, 4.20365] |
| single_A | True | 1 [1, 1] | 1 [1, 1] | 3.17488 [2.51421, 3.82071] |
| single_B_origin_shared | False | 0.984375 [0.953125, 1] | 0.984375 [0.953125, 1] | 2.97807 [2.45717, 3.4678] |
| single_B_origin_shared | True | 1 [1, 1] | 1 [1, 1] | 4.12014 [3.94274, 4.31682] |
| single_B_cross_shared | False | 0.96875 [0.921875, 1] | 0.96875 [0.921875, 1] | 3.8997 [3.52723, 4.18022] |
| single_B_cross_shared | True | 1 [1, 1] | 1 [1, 1] | 3.51358 [3.12537, 3.89415] |
| single_B_origin_far | False | 0.984375 [0.953125, 1] | 0.984375 [0.953125, 1] | 3.2526 [2.69505, 3.74998] |
| single_B_origin_far | True | 0.984375 [0.953125, 1] | 0.984375 [0.953125, 1] | 1.80996 [1.38516, 2.26421] |
| single_B_cross_far | False | 0.953125 [0.90625, 0.984375] | 0.953125 [0.90625, 0.984375] | 1.46493 [1.10609, 1.88768] |
| single_B_cross_far | True | 1 [1, 1] | 1 [1, 1] | 3.57633 [3.25551, 3.91099] |

| B-convention响应 | signed [CI] | abs [CI] | within signed [CI] | within abs [CI] |
|---|---|---|---|---|
| shared_normal_native | 2.00089 [1.78968, 2.20884] | 2.00089 [1.78968, 2.20884] | -0.0610492 [-0.208547, 0.0782728] | 0.243915 [0.167847, 0.335449] |
| shared_normal_gate | 0.857243 [0.591632, 1.13048] | 0.857243 [0.591632, 1.13048] | -0.155128 [-0.343057, 0.00189145] | 0.250219 [0.120478, 0.408768] |
| shared_answer_cross_off_native | 0.951928 [0.714894, 1.22318] | 0.951928 [0.714894, 1.22318] | 0.0426882 [-0.276274, 0.366711] | 0.446007 [0.230563, 0.691219] |
| shared_answer_cross_off_gate | 0.300363 [0.166263, 0.442076] | 0.319909 [0.198312, 0.453789] | 0.0443783 [-0.12699, 0.200868] | 0.261505 [0.168707, 0.364485] |
| shared_all_cross_off_native | 1.85571 [1.56921, 2.14033] | 1.85571 [1.56921, 2.14033] | -0.119847 [-0.461976, 0.180602] | 0.434631 [0.22581, 0.705104] |
| shared_all_cross_off_gate | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |
| far_normal_native | 0.0532591 [-0.11725, 0.226695] | 0.302853 [0.209214, 0.399931] | 0.0686417 [-0.121269, 0.257323] | 0.302925 [0.187952, 0.42772] |
| far_normal_gate | -0.0133818 [-0.11123, 0.0822035] | 0.151528 [0.0895958, 0.219529] | 0.0810721 [-0.0329395, 0.219961] | 0.180761 [0.103343, 0.29255] |
| far_answer_cross_off_native | 0.0293685 [-0.142639, 0.204376] | 0.303203 [0.206406, 0.400002] | 0.001752 [-0.221268, 0.222952] | 0.338961 [0.201832, 0.491064] |
| far_answer_cross_off_gate | -0.00646703 [-0.102785, 0.0857703] | 0.146501 [0.0861883, 0.214243] | 0.0760505 [-0.0367394, 0.196577] | 0.17611 [0.101952, 0.268918] |
| far_all_cross_off_native | 0.0291333 [-0.0925231, 0.140372] | 0.199054 [0.13359, 0.269631] | 0.00941967 [-0.11439, 0.128574] | 0.184412 [0.107932, 0.268395] |
| far_all_cross_off_gate | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] | 0 [0, 0] |

全部85接口、两private方向、每world/Actor/namespace/policy、8个instruction接口、candidate/full/label rate、margin、other-source词A/B及20k独立重采样保留在JSON。shared词不可按表面词识别Source；far other-space不是自动可分latent模块。mean Actor accuracy不等于joint success，本批n16 discovery不代替固定n32确认或大小配对。

现在15/18、384contexts、196608scores；科学stage累计23.2591511 device-hours，worker驻留按各最后快照另记。没有修改五源、论文、claims或运行GPU，未读未完整确认批科学数据。

## 作者15-stage collector新增展示核对

新L70Dfunction行5统计单元/21个展示数、analysis1893数值、full-output960数值全部一致，最大误差均0。全部12policy/source/ns/scope的full与other-space，以及18配对full/foreign contrasts按原primary权重复核；已有full-accuracy/CI使用stage15已封推导，仅缺的other-word辅助contrast CI另从本批raw封存后才打开authorfullsummary。原14 run summary对象逐项一致、原54表行（含表头）逐字保留、三Qwen paired对象不变，旧science未重算。

本审计功能表的accuracy与accuracy差以0–1比例计，乘100得到%或pp；margin/code-response为nats。shared表面词不能分类Source，所记other-word0不是provenance成功。确认图仍9/12点，无L70新32结果。

summary `a4900acc76f6044c18696e0455fec30ad7885d000288e0c3fec0826ce74a93b3`；report `0cfcf1b01fed5df8e1347ea3d01084accd7fcf73454127a66de7a7ec29d9790e`；auxiliary seal `1fd3845ced0ef00eb9ecd05580869be09d3203c2e84a088200a982f4a132f339`。

## 第16批：Llama-3.1-70B confirmation mechanism 完整 raw-first 封存

32contexts×43条件×8query=11008评分；80层、4GPU、FP32/eager/TF32=False。实际全层edge调用25680；cached/full 7.62939453e-06、self 0；layer0 sender K/V固定0。CPU context/科学预检字节、model pin、冻结五源均一致。
新增 raw pre-author seal b55d3e98a6c465ff39a06b0a6a73f59c11bc5096d3ed11fa32687edcbf174668；配对seal 0d2b53ef83821b5760aeb5a217cfc259fffd6f4681267323f8e84d8dc47d5c7b。此前15stage JSON/MD另存；旧raw与三Qwen配对不重算。之后author analysis比较1041项，最大误差6.99440506e-15。

| 冻结读数 | 均值 [95% context CI] |
|---|---|
| A_formation_B_shared/signed_rule_effect | 0.95679 [0.678857, 1.26065] |
| A_formation_B_shared/absolute_rule_effect | 0.95679 [0.678857, 1.26065] |
| A_formation_B_far/signed_rule_effect | 0.998436 [0.64745, 1.37196] |
| A_formation_B_far/absolute_rule_effect | 0.75099 [0.44924, 1.07422] |
| B_reading_A_shared/signed_rule_effect | 3.35864 [2.88179, 3.824] |
| B_reading_A_shared/absolute_rule_effect | 3.15636 [2.70289, 3.59771] |
| B_reading_A_far/signed_rule_effect | 3.40028 [2.87362, 3.92429] |
| B_reading_A_far/absolute_rule_effect | 2.95056 [2.46764, 3.41045] |
| stage_interaction/signed_rule_effect | -0.0416462 [-0.445303, 0.354745] |
| stage_interaction/absolute_rule_effect | 0.205799 [-0.128187, 0.543286] |
| label_effect_B_shared/signed_rule_effect | 0.195665 [-0.0926982, 0.509779] |
| label_effect_B_shared/absolute_rule_effect | 0.195665 [-0.0926982, 0.509779] |
| label_effect_B_far/signed_rule_effect | 0.87307 [0.531079, 1.23488] |
| label_effect_B_far/absolute_rule_effect | 0.740783 [0.433099, 1.0665] |
| edge_K_B_shared/signed_rule_effect | 0.732268 [0.506241, 0.995972] |
| edge_K_B_shared/absolute_rule_effect | 0.732268 [0.506241, 0.995972] |
| edge_K_B_far/signed_rule_effect | 0.253707 [-0.0236873, 0.529311] |
| edge_K_B_far/absolute_rule_effect | 0.258578 [-0.00955343, 0.526564] |
| relation/full_native/absolute_effect | 4.08442 [3.74978, 4.40302] |
| relation/full_native/signed_effect | 4.29173 [3.94217, 4.62279] |
| relation/label_native/absolute_effect | 1.13775 [0.880427, 1.40465] |
| relation/label_native/signed_effect | -1.32009 [-1.60206, -1.0483] |
| relation/answer_native/absolute_effect | 0.14422 [0.0879849, 0.206493] |
| relation/answer_native/signed_effect | -0.168707 [-0.300255, -0.0525966] |
| relation/cross_KV_minus_K/absolute_effect | 0.185961 [0.124882, 0.254509] |
| relation/cross_KV_minus_K/signed_effect | -0.103139 [-0.194879, -0.00757961] |
| relation/cross_KV_minus_V/absolute_effect | 0.043001 [-0.023925, 0.112059] |
| relation/cross_KV_minus_V/signed_effect | -0.217855 [-0.277961, -0.163475] |
| relation/relation_f0r1/absolute_effect | 3.12999 [2.71302, 3.52059] |
| relation/relation_f0r1/signed_effect | 3.12999 [2.71302, 3.52059] |
| relation/relation_f1r0/absolute_effect | 1.2213 [1.00796, 1.44552] |
| relation/relation_f1r0/signed_effect | -1.15863 [-1.41241, -0.900419] |
| relation/relation_label_cross_native/absolute_effect | 1.35003 [1.11231, 1.60227] |
| relation/relation_label_cross_native/signed_effect | -1.28367 [-1.56679, -0.997828] |
| relation/relation_answer_cross_kv_native/absolute_effect | 0.263074 [0.200499, 0.333091] |
| relation/relation_answer_cross_kv_native/signed_effect | -0.134652 [-0.234314, -0.0294164] |
| relation/relation_answer_cross_k_native/absolute_effect | 0.0771133 [0.0575109, 0.0988314] |
| relation/relation_answer_cross_k_native/signed_effect | -0.0315132 [-0.0629769, -0.000210372] |
| relation/relation_answer_cross_v_native/absolute_effect | 0.220073 [0.158965, 0.294062] |
| relation/relation_answer_cross_v_native/signed_effect | 0.0832031 [-0.0109778, 0.185349] |

| 重建目标/通道 | raw r / RMSE / zero | rule双差 r / RMSE / zero |
|---|---|---|
| label_interface_B0_k | 0.466018 / 0.838151 / 0.751048 | 0.648182 / 0.910586 / 1.05903 |
| label_interface_B0_kv | 0.618571 / 0.644387 / 0.751048 | 0.718736 / 0.764572 / 1.05903 |
| label_interface_B0_v | 0.425496 / 0.677622 / 0.751048 | 0.466932 / 0.94189 / 1.05903 |
| all_A_formation_B0_k | 0.747292 / 0.633774 / 0.916751 | 0.862343 / 0.745037 / 1.45087 |
| all_A_formation_B0_kv | 0.838335 / 0.501861 / 0.916751 | 0.900553 / 0.723002 / 1.45087 |
| all_A_formation_B0_v | 0.463318 / 0.81767 / 0.916751 | 0.507194 / 1.29529 / 1.45087 |
| label_interface_B1_k | 0.858812 / 0.679205 / 1.32324 | 0.782449 / 0.972547 / 1.53147 |
| label_interface_B1_kv | 0.908573 / 0.564066 / 1.32324 | 0.837396 / 0.875973 / 1.53147 |
| label_interface_B1_v | 0.740565 / 0.90337 / 1.32324 | 0.555111 / 1.29121 / 1.53147 |
| all_A_formation_B1_k | 0.792019 / 0.826528 / 1.34293 | 0.718104 / 1.16187 / 1.65138 |
| all_A_formation_B1_kv | 0.845966 / 0.730166 / 1.34293 | 0.781105 / 1.06441 / 1.65138 |
| all_A_formation_B1_v | 0.656977 / 1.01388 / 1.34293 | 0.510559 / 1.42972 / 1.65138 |

| single_A/private | candidate / full / label rate |
|---|---|
| False | 0.992188 [0.976562, 1] / 0.992188 [0.976562, 1] / 1 [1, 1] |
| True | 0.992188 [0.976562, 1] / 0.992188 [0.976562, 1] / 1 [1, 1] |

| 新材料L70−L8配对（n32） | 均值 [95% paired context CI] |
|---|---|
| A_formation_signed | 0.156256 [-0.0873952, 0.402337] |
| A_formation_absolute | 0.156256 [-0.0873952, 0.402337] |
| B_reading_signed | 0.30365 [-0.0839259, 0.678152] |
| B_reading_absolute | 0.303765 [-0.114989, 0.692656] |
| label_interface_signed | -0.367655 [-0.632643, -0.0974534] |
| label_interface_absolute | -0.367655 [-0.632643, -0.0974534] |
| answer_K_signed | 0.165164 [-0.0213887, 0.354792] |
| answer_K_absolute | 0.165164 [-0.0213887, 0.354792] |
| answer_relation_signed | -0.122294 [-0.243531, -0.00741275] |
| answer_relation_absolute | 0.0388599 [-0.0386905, 0.120213] |

全部43接口、12重建、所有通道、fixed-word关系、双private/全文输出、实际80层注意与单方向控制均保留于JSON。signed/absolute与零/负同报；不把相关预测当完整中介、不作因果容量律。没有独立GPU重跑、科学源修改或主张等级变化。
当前16/18、416contexts、207616scores，科学stage device-hours=38.1835912；两个未完成确认不提前取结果。

## 第16批新增展示核对

仅核新增L70confirmation mechanism32和首次同材料L70−L8配对；analysis 1041项、max error 6.99440506e-15；配对全部统计项与独立raw seal一致。新表8cell/各CI与重建r/RMSE一致，10条原冻结配对读数逐行通过。旧15run、55行展示与三Qwen配对保留，不重算旧science、不给discoveryn16错误大小配对。当前16/18、416ctx/207616scores；驻留仍是last-observed累计快照。summary `6c346e99b76cdeea232d3ce2b737b7bf1054158ed33836540f226a147ca3d865`；report `2294563c85760e4da1dd36b7ed16ded5da316dfe2c96d2c63988ca9f605b7692`。

## 第16批确认图：10/12点

新增L70confirmation mechanism使用已先封raw与同新32材料配对；10点/30均值及CI端点与当前summary、sealedraw和CSV逐项相等。旧9点原值不变，两个L70native/function仍空值pending，不是零。没有重算stage或bootstrapCI；SST机制/function分别采样，native为controlledrestaurant，配对限定同family/stage。manifest `d40c8d05afad9bb3f8cade81a725bbebed5c8df082a88e9e17bcb9a1c62bab90`，摘要 `6c346e99b76cdeea232d3ce2b737b7bf1054158ed33836540f226a147ca3d865`。
