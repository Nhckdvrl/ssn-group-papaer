# E119 独立校对（2026-10-11启动；2026-10-12续审）

截至本版4/4批完整，96 contexts、29,184评分；primary数值逐项复算最大差4.66e-15、rotation observer最大差1.67e-16。E117/E118封版未动，本会话未独立GPU重跑。

确认范围：14B native形成/B shared作用3.05949[2.55728,3.57072]nats、关联KV绝对/ signed超额+.31805/+.24882均正；signed cache交互−.68563[−1.13304,−.23680]，不能把8B的方向原样泛化。Criterion native signed det=.56798[.40784,.75091]、rotation=.40978[.33043,.49261]且两task原生选择性均正。

形成接口不能概括为纯共同gain：native label det为负(−.02011[−.03735,−.00516])而平均normalized rotation CI跨0；label_gate normalized rotation为正(.12372[.01666,.24219])而raw det CI跨0。edge/edge_gate signed det小正、normalized rotation CI跨0。保留全部方向、尺度和实际label预测残差；这些反驳的是有限功能null，未识别正确、完整、独立criterion程序或input filtering。

## 范围与方法

对象为同一Qwen3-14B的两个独立任务块(native namespace/association、criterion×code)，不是两个14B模型。官方post-trained revision40c069…、40层/40 attention heads/8 KV heads；plain continuation不用chat/生成reasoning，不叫Base或完整reasoning压力测试。cached config逐项匹配、8 shard size和HF cache blob名字核过(total29,536,665,640 bytes)，本会话未重hash全部weight bytes或远端RAM副本。

先读卡与产生样本/干预脚本；用raw独立写出均值/context CI/居中Pearson/重建和矩阵det后才打开作者analysis/response_rotation。原seed910/10000 mean-bootstrap与109910/10000 reconstruction-bootstrap逐项匹配；另20000/seed1119重算observer det/rotation。脚本diff核过：native仅model默认路径/revision；criterion model/seed/revision和CPU全pool可行性guard，science/conditions/attention/primary不变。

## 完整运行计数

| 批 | seed | contexts | 条件×query | 评分 | GPU·时记录 | full/split最大误差 |
|---|---:|---:|---:|---:|---:|---:|
| criterion_confirmation | 119301 | 32 | 33×8 | 8448 | 0.27170 | 1.14e-05 |
| criterion_discovery | 119201 | 16 | 33×8 | 4224 | 0.11959 | 1.72e-05 |
| native_confirmation | 119101 | 32 | 43×8 | 11008 | 0.24064 | 1.72e-05 |
| native_discovery | 119001 | 16 | 43×8 | 5504 | 0.11417 | 1.72e-05 |

CPU重建token几何流720条，其中native每context额外的within+far组合为CPU几何校对，未新增GPU条件；raw world×layer过去同/异label availability计数15360项。所有A非B token、固定B标签/source/multiset、world/private truth、full-rank、query gold/unique/no-demo-overlap通过。所有40层每mode n次+self1、pristine source/self0/static layer0 KV0通过作者记录与源码消费核验。

## Native形成、关联与全部通道

| 批 | single A正/反 | A形成/B shared 幅度差 | signed交互 | 关联KV cross−within abs/signed |
|---|---|---|---|---|
| native_confirmation | 1.000/1.000 | 3.05949[2.55728,3.57072] | -0.68563[-1.13304,-0.23680] | 0.31805[0.22555,0.42141]/0.24882[0.11508,0.38985] |
| native_discovery | 1.000/1.000 | 2.26732[1.48121,3.10144] | -0.10634[-0.79191,0.48632] | 0.21557[0.05288,0.42726]/0.19011[0.00639,0.40988] |

| 批 | target/bg/channel | rule r | rule RMSE | zero RMSE | raw r/RMSE/zero |
|---|---|---:|---:|---:|---|
| native_confirmation | label_interface_B0_k | 0.8992 | 1.2689 | 2.6105 | 0.8190/0.9075/1.5677 |
| native_confirmation | label_interface_B0_kv | 0.9337 | 1.0473 | 2.6105 | 0.9050/0.6982/1.5677 |
| native_confirmation | label_interface_B0_v | 0.0256 | 2.7545 | 2.6105 | 0.1325/1.6212/1.5677 |
| native_confirmation | all_A_formation_B0_k | 0.8673 | 2.2494 | 3.6202 | 0.7752/1.3605/2.0464 |
| native_confirmation | all_A_formation_B0_kv | 0.9081 | 2.0075 | 3.6202 | 0.8646/1.1587/2.0464 |
| native_confirmation | all_A_formation_B0_v | -0.0017 | 3.7465 | 3.6202 | 0.0844/2.0982/2.0464 |
| native_confirmation | label_interface_B1_k | 0.8783 | 2.2624 | 3.9488 | 0.8408/1.3092/2.3011 |
| native_confirmation | label_interface_B1_kv | 0.9271 | 1.8182 | 3.9488 | 0.9048/1.0798/2.3011 |
| native_confirmation | label_interface_B1_v | 0.0836 | 4.0722 | 3.9488 | 0.1533/2.3671/2.3011 |
| native_confirmation | all_A_formation_B1_k | 0.8754 | 2.8587 | 4.5937 | 0.8163/1.5931/2.5724 |
| native_confirmation | all_A_formation_B1_kv | 0.9283 | 2.3787 | 4.5937 | 0.8919/1.3376/2.5724 |
| native_confirmation | all_A_formation_B1_v | 0.0774 | 4.6955 | 4.5937 | 0.1146/2.6545/2.5724 |
| native_discovery | label_interface_B0_k | 0.9007 | 1.2377 | 2.4278 | 0.8074/0.8909/1.4542 |
| native_discovery | label_interface_B0_kv | 0.9387 | 0.9476 | 2.4278 | 0.9048/0.6597/1.4542 |
| native_discovery | label_interface_B0_v | 0.0911 | 2.4605 | 2.4278 | 0.1847/1.4482/1.4542 |
| native_discovery | all_A_formation_B0_k | 0.9125 | 1.7073 | 2.9918 | 0.8223/1.0674/1.6914 |
| native_discovery | all_A_formation_B0_kv | 0.9499 | 1.3756 | 2.9918 | 0.9051/0.8418/1.6914 |
| native_discovery | all_A_formation_B0_v | 0.1346 | 2.9773 | 2.9918 | 0.1561/1.6851/1.6914 |
| native_discovery | label_interface_B1_k | 0.8948 | 1.9523 | 3.6328 | 0.8712/1.1189/2.1752 |
| native_discovery | label_interface_B1_kv | 0.9481 | 1.4378 | 3.6328 | 0.9395/0.8127/2.1752 |
| native_discovery | label_interface_B1_v | -0.0480 | 3.7886 | 3.6328 | 0.2537/2.1263/2.1752 |
| native_discovery | all_A_formation_B1_k | 0.8901 | 2.2728 | 3.9742 | 0.8466/1.3116/2.3317 |
| native_discovery | all_A_formation_B1_kv | 0.9515 | 1.7098 | 3.9742 | 0.9222/1.0008/2.3317 |
| native_discovery | all_A_formation_B1_v | -0.0400 | 4.1150 | 3.9742 | 0.2234/2.2965/2.3317 |

## Criterion：所有接口的J、方向和原始预测

| 批 | 接口 | J | food selectivity | service selectivity | det(nats²) | signed rotation | weak rows(context) |
|---|---|---|---|---|---|---|---:|
| criterion_confirmation | native | 0.34325[0.26487,0.43265] | 0.28231[0.19890,0.37106] | 0.40418[0.29420,0.52845] | 0.56798[0.40784,0.75091] | 0.40978[0.33043,0.49261] | 0 |
| criterion_confirmation | gate | 0.05849[0.02940,0.08900] | 0.07276[0.00052,0.14202] | 0.04422[-0.02689,0.12504] | 0.02894[0.00319,0.05525] | 0.18988[0.07345,0.30970] | 0 |
| criterion_confirmation | label | -0.02377[-0.04783,-0.00255] | -0.01128[-0.05036,0.02186] | -0.03626[-0.07790,0.00066] | -0.02011[-0.03735,-0.00516] | 0.00588[-0.12074,0.13998] | 0 |
| criterion_confirmation | label_gate | 0.03828[0.01192,0.06827] | 0.10880[0.04640,0.17800] | -0.03224[-0.08934,0.03061] | 0.00738[-0.01061,0.02707] | 0.12372[0.01666,0.24219] | 0 |
| criterion_confirmation | edge | 0.00602[0.00288,0.00935] | 0.00342[-0.00968,0.01411] | 0.00861[-0.00117,0.02197] | 0.00068[0.00012,0.00130] | 0.08480[-0.04191,0.21448] | 0 |
| criterion_confirmation | edge_gate | 0.01258[0.00757,0.01876] | 0.01774[0.00156,0.03473] | 0.00743[-0.01063,0.02649] | 0.00194[0.00031,0.00474] | 0.07201[-0.04020,0.18959] | 0 |
| criterion_confirmation | far_label | -0.01920[-0.03482,-0.00597] | -0.02279[-0.06551,0.01245] | -0.01562[-0.04421,0.01166] | 0.00192[-0.00123,0.00556] | 0.01090[-0.14504,0.16357] | 0 |
| criterion_discovery | native | 0.33986[0.22776,0.48842] | 0.27461[0.16019,0.39938] | 0.40512[0.21488,0.66182] | 0.48219[0.28343,0.79400] | 0.43016[0.29198,0.57684] | 0 |
| criterion_discovery | gate | 0.10403[0.04658,0.17126] | 0.10680[-0.02887,0.26459] | 0.10127[-0.02182,0.24719] | 0.03482[0.01123,0.06101] | 0.32254[0.17157,0.48647] | 0 |
| criterion_discovery | label | 0.00261[-0.02240,0.02794] | 0.08158[0.01806,0.15370] | -0.07636[-0.15132,-0.01352] | -0.00880[-0.02070,0.00154] | 0.04738[-0.08625,0.20277] | 0 |
| criterion_discovery | label_gate | 0.03931[-0.01483,0.10973] | 0.13277[0.02705,0.27227] | -0.05414[-0.15906,0.06183] | 0.00456[-0.02553,0.03770] | 0.14485[-0.09740,0.37392] | 0 |
| criterion_discovery | edge | 0.00229[-0.00504,0.00813] | -0.01315[-0.03780,0.00640] | 0.01772[0.00446,0.03256] | 0.00026[-0.00029,0.00087] | 0.11384[-0.08971,0.32453] | 0 |
| criterion_discovery | edge_gate | 0.00346[-0.00906,0.01492] | 0.00099[-0.03655,0.03427] | 0.00593[-0.01936,0.03021] | 0.00069[-0.00002,0.00158] | 0.11210[-0.15346,0.36212] | 0 |
| criterion_discovery | far_label | -0.00690[-0.02227,0.00911] | 0.06740[0.00861,0.13639] | -0.08120[-0.13867,-0.03348] | -0.00304[-0.00920,0.00191] | 0.00526[-0.30892,0.31898] | 0 |

每context M的两行是food/service标准的same−opposite代码半差，两列是Food/Service响应。det(M)逐context计算再bootstrap；signed rotation=det/(两row norm之积)，即signed sin夹角。任一row norm≤.001nats时rotation定义0，但context与det全部保留。nonzero可反驳受限共同功能方向＋任意row增益解释；平均0不能证明每context rank1，不识别隐藏程序或input filtering。Prospective observer commit be96cd03、SHA e453f4…在首E119评分前有卡/git记录；不把旧E118事后方向解释冒充prospective实验。

| 批 | single A正/反 | single B service+/service−/food+/food− | direct food | raw native label预测r/RMSE/zero | gated r/RMSE/zero | far−shared J |
|---|---|---|---|---|---|---|
| criterion_confirmation | 0.844/0.797 | 0.879/0.871/0.836/0.828 | 0.984 | 0.668/0.646/0.746 | 0.665/0.878/1.018 | 0.00457[-0.00930,0.01904] |
| criterion_discovery | 0.844/0.828 | 0.898/0.875/0.820/0.773 | 0.992 | 0.347/0.874/0.917 | 0.277/1.103/1.142 | -0.00951[-0.03299,0.01265] |

## 完整criterion响应

每一接口的两个任务、bias/F/S/FS均保留，Delta=.5(same−opposite)，含所有零/负。全部33条件accuracy/argmax、完整feature响应、所有per-context矩阵和20000-bootstrap也在JSON。

| 批 | 接口 | B criterion | bias | Food | Service | Food×Service |
|---|---|---|---|---|---|---|
| criterion_confirmation | native | food | -0.06939[-0.17270,0.03758] | 0.95419[0.84559,1.06578] | 0.67188[0.59183,0.75068] | 0.07698[-0.01339,0.17282] |
| criterion_confirmation | native | service | -0.07430[-0.15777,0.00864] | 0.57585[0.46612,0.68600] | 0.98003[0.87976,1.08499] | 0.15321[0.07523,0.23241] |
| criterion_confirmation | gate | food | -0.12739[-0.23927,-0.02808] | 0.46095[0.35826,0.55987] | 0.38818[0.29982,0.48201] | -0.00016[-0.10091,0.10066] |
| criterion_confirmation | gate | service | -0.13362[-0.23532,-0.05107] | 0.26679[0.16570,0.37202] | 0.31101[0.23630,0.38945] | 0.04658[-0.01905,0.11138] |
| criterion_confirmation | label | food | -0.05752[-0.11489,-0.00128] | 0.29082[0.23374,0.34872] | 0.30209[0.24449,0.36157] | -0.01533[-0.05867,0.02997] |
| criterion_confirmation | label | service | -0.05266[-0.10000,-0.00711] | 0.22982[0.16828,0.29349] | 0.19356[0.14435,0.24351] | -0.02401[-0.07281,0.02536] |
| criterion_confirmation | label_gate | food | -0.07900[-0.17216,0.00903] | 0.43902[0.34003,0.53955] | 0.33022[0.24886,0.41453] | -0.00946[-0.08264,0.06531] |
| criterion_confirmation | label_gate | service | -0.08203[-0.16105,-0.01513] | 0.27861[0.18420,0.37974] | 0.24636[0.17727,0.31885] | 0.00012[-0.05661,0.05814] |
| criterion_confirmation | edge | food | -0.02359[-0.03644,-0.01011] | 0.05129[0.03742,0.06515] | 0.04787[0.03234,0.06493] | -0.00051[-0.01540,0.01518] |
| criterion_confirmation | edge | service | -0.01305[-0.02456,-0.00140] | 0.03312[0.01974,0.04645] | 0.04173[0.02586,0.05983] | 0.00055[-0.01264,0.01443] |
| criterion_confirmation | edge_gate | food | -0.02262[-0.04092,-0.00455] | 0.07236[0.04837,0.09945] | 0.05462[0.03533,0.07641] | -0.00456[-0.02646,0.01794] |
| criterion_confirmation | edge_gate | service | -0.02188[-0.03707,-0.00656] | 0.04629[0.02384,0.07105] | 0.05372[0.03183,0.08055] | 0.00293[-0.01578,0.02077] |
| criterion_confirmation | far_label | food | 0.05783[0.01665,0.10033] | -0.01380[-0.06156,0.03538] | 0.00899[-0.02937,0.04820] | -0.01021[-0.05048,0.02801] |
| criterion_confirmation | far_label | service | 0.03171[-0.01051,0.07404] | -0.00152[-0.04028,0.04312] | -0.01714[-0.05335,0.01969] | -0.01485[-0.05006,0.02090] |
| criterion_discovery | native | food | -0.09956[-0.25892,0.05904] | 0.87608[0.76259,0.99400] | 0.60148[0.46711,0.73958] | -0.08640[-0.22677,0.06416] |
| criterion_discovery | native | service | -0.10040[-0.23724,0.03840] | 0.52379[0.37387,0.67161] | 0.92891[0.74662,1.15601] | -0.02911[-0.22691,0.16121] |
| criterion_discovery | gate | food | -0.14452[-0.29344,0.00979] | 0.40560[0.22452,0.60054] | 0.29880[0.21216,0.38861] | -0.00426[-0.13529,0.13452] |
| criterion_discovery | gate | service | -0.10346[-0.24721,0.03594] | 0.17887[0.01564,0.34222] | 0.28014[0.18611,0.37018] | 0.01453[-0.15610,0.21208] |
| criterion_discovery | label | food | -0.01986[-0.12371,0.10604] | 0.30644[0.22702,0.38920] | 0.22486[0.14848,0.31316] | -0.05468[-0.19845,0.06650] |
| criterion_discovery | label | service | 0.02476[-0.07640,0.15591] | 0.21924[0.12474,0.31751] | 0.14289[0.07852,0.21635] | -0.09591[-0.23072,0.01096] |
| criterion_discovery | label_gate | food | -0.10111[-0.22064,0.03390] | 0.40345[0.26628,0.55893] | 0.27068[0.20849,0.33792] | -0.02431[-0.16765,0.10683] |
| criterion_discovery | label_gate | service | -0.10536[-0.23104,0.02238] | 0.23643[0.09467,0.37758] | 0.18228[0.10547,0.25516] | -0.01685[-0.17782,0.15835] |
| criterion_discovery | edge | food | -0.00027[-0.02316,0.02559] | 0.02481[-0.00025,0.04564] | 0.03796[0.01916,0.05754] | -0.01871[-0.04471,0.00828] |
| criterion_discovery | edge | service | -0.00817[-0.02311,0.00942] | 0.01580[-0.00174,0.03336] | 0.03352[0.01576,0.05113] | -0.01067[-0.03553,0.01420] |
| criterion_discovery | edge_gate | food | -0.01289[-0.04857,0.02688] | 0.03420[-0.00146,0.06573] | 0.03321[0.00936,0.05679] | -0.00820[-0.03874,0.02197] |
| criterion_discovery | edge_gate | service | -0.03377[-0.05949,-0.00829] | 0.02458[0.00023,0.04913] | 0.03051[0.00750,0.05109] | 0.00276[-0.02172,0.02742] |
| criterion_discovery | far_label | food | 0.00353[-0.07406,0.08897] | 0.03341[-0.02970,0.09928] | -0.03399[-0.09912,0.03918] | -0.03022[-0.11148,0.04288] |
| criterion_discovery | far_label | service | 0.04253[-0.01415,0.09834] | 0.02709[-0.01887,0.07908] | -0.05411[-0.11148,0.01134] | -0.06583[-0.11936,-0.01463] |

## 局限

- 模板food总在service前，方面身份与词序/位置未正交；固定模板F/S功能响应有效，不外推为位置无关抽象标准。
- 所有native/label/edge响应矩阵都来自请求A且A raw固定的B code反事实，非B自己的任务正确率或正确Source隔离；single B按自身gold另报。
- 14B是同一Qwen3家族大小对照，不自动增加独立架构或证明每个任务能力更强；强弱由single/direct读数决定。8B/14B未控制训练配方/数据，计算差异不能仅归因于参数规模增加。
- plain continuation仅全Source计算图，不是native chat或完整thinking/reasoning压力测试。
- 所有GPU self/full-split/static layer0/cache指纹/全层消费阳性是作者run与源码核验，本会话没有独立GPU复跑。
- J是平均criterion×feature交互；每task增益差也可J>0，两个task各F/S/selectivity同时保留。
- prospective det/rotation只能检验每context同一功能方向＋任意row gain的受限null；不能排除非线性latent等价或识别完整独立criterion程序/input filtering。
- 平均signed det/rotation CI跨0不证明每context rank1，符号可抵消；保留全部per-context matrix与预定weak handling，不删弱行context。
- actual-donor系数1预测需连同target/zero/RMSE，不能由namespace高r外推criterion接口或完整无donor算法。
- F/R、gate/label/edge是上下文化位置缓存与功能接口，不是独立语义模块；query继续演化。
- 探索/确认新评论无字节重合但context间仍共享词模板，bootstrap单位context；全部接口CI未多重比较校正。
