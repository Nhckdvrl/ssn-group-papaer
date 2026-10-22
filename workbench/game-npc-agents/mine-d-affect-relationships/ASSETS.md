# 矿区D资产与复现入口（2026-10-22）

导航：[Baseline与复现范围](BASELINES.md) · [脚本职责与离线命令](scripts/README.md) · [结果状态](results/README.md)。本页是来源、环境与仓库外资产的唯一登记入口，不把下载缓存复制进研究仓库。

**2026-10-22源纠正：** D-E03 Monte Summary的14原生单元被本轮适配器误换成117文学章号；原归档保持完整历史，六作品S相关比较暂撤回。正确来源与新结果见[纠正记录](results/D-SOURCE-CORRECTION-2026-10-22.md)。新冻结输入在`data/arcane_D-E07_v2/`，完整旧28编译中断记录也保留；D-E06连续轨迹另在`data/closed_D-E06/`和`runs/D-E06/`。

完整第三方数据、权重、原文和大raw位于本机NVMe：`/var/tmp/ssn-game-npc-d/`。Git仅保留源hash/样本ID、轻量读数、代码和中文报告。父workbench保持一个ACTIVE-MAIN；B/I01暂停，矿区A不执行。

| 资产 | 固定版本 | 位置与本轮状态 |
|---|---|---|
| ArcANE代码 | `46ee34a73c7bd006ba52a7a262586f02301cdb6f` | `vendor/ArcANE`；原生Trial/context/prompt及judge模板用于D-E01/D-E03 |
| ArcANE正式公开benchmark | 随该Git revision | 实际18作品、80个有probe人物、494轴、4282 probes、13438 phase单元；9个空轴文件单列。论文Harry Potter部分未公开，不补造。详见[清单](results/assets_inventory.json) |
| ArcANE-Data训练配置 | `6076de00429ca293b6738f571196ad1264e9a433` | `data/ArcANE-Data`；完整SFT/DPO/RL parquet。与正式benchmark分开；公开10小说子集与发布权重历史12小说训练池分开 |
| ArcANE-8B-DPO | `67b9bea604bea65a5245928ed87103545814b4f7` | `models/ArcANE-8B-DPO`；完整merged权重已下载并实际推理 |
| PHASE-Tree代码 | `0be378fd23c49915255406d881f2389b46b608b8` | `vendor/PHASE-Tree`；四种文本输入使用原生prompt，状态/门控源码已核查 |
| LongEvoRoleBench | `ce09fb68439963c71c3035ee2918c21ae02a3cbc` | `data/LongEvoRoleBench`；四长程语料全部processed资产约7.14GB，含六文本变体、原始时间元数据、中间状态及演化档案；无短程全量跑分 |
| PHASE参数模型资产 | `db2aa3b516a1d78650ffd3f01ef14dcb8f6ea8b4` | `models/phase_tree_models`；两套hypermod约1.8GB已下载；本轮文本路径不依赖，不声称已跑参数适配 |
| Qwen3-8B | `b968826d9c46dd6066d109eabc6255188de91218` | 复用本机HF缓存；D-E01/D-E03角色生成 |
| Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` | 复用本机HF缓存；D-E02原生backbone |
| Qwen3-32B | `9216db5781bf21249d130ec9da846c4624c16137` | 已从本机固定缓存复制到`models/Qwen3-32B`；普通章节摘要、统一本地评委与容量参照；D-E04直接状态更新普通模型 |

目录关系：`data/arcane_D-E01/`存205个phase的原生任务/独立参考；`data/phase_D-E02/`存64问题四变体与独立评委参考；`data/arcane_D-E03/`存固定嵌套25probe/81phase及242章摘要教师任务。实际prompt/raw/token IDs在`runs/D-E0*/`，运行stdout在`logs/`。metadata/source快照保存每次调用配置，章节摘要与原文不入本仓库Git。

公开ArcANE存量判分的四作品主表与两部lowpop表已由官方脚本离线复算，放`logs/official_*_reaggregated.{json,txt,tex}`；这是历史输出重聚合，不是新模型实测。Step5 low因实际共享并发9/8限制停止，340正式尝试321合法分数单列，未转现金；D-E01/03正式比较统一用本地Qwen3-32B完整评分，不拼接评委。它与论文原DeepSeek须分开；PHASE同一本地judge与原GPT-4.1须分开。没有未授权OpenAI/DeepSeek/embedding调用。

## 获取与许可身份

- 代码来源：[ArcANE](https://github.com/holi-lab/ArcANE)、[PHASE-Tree](https://github.com/MemTensor/PHASE-Tree)。用`git clone`后checkout表中完整revision。
- 数据/权重：使用Hugging Face `snapshot_download(repo_id, revision=完整hash, repo_type='dataset'或省略, local_dir=资产目录)`。LongEvo本轮仅选`processed/{Friends,TheOffice,HPD,StarTrek_TNG}/**`；其余数据未下载不假称全量完成。
- ArcANE小说：官方`arc_construction.download_novels`的Gutenberg edition ID；镜像延迟时使用同eBook编号的官方www.gutenberg.org/cache/epub文本，核验eBook ID与起止标记。`data/novels/`及`results/arc_extraction/*/chapters/`均仅在vendor缓存中。
- 许可按资产分别记录：ArcANE代码MIT，repo benchmark `LICENSE-DATA`为CC BY 4.0；HF训练卡标MIT；ArcANE模型Apache-2.0；PHASE代码MIT、LongEvo卡CC-BY-NC-4.0，原语料出处仍单独存在。没有把代码许可当全部影视/小说数据许可。

## 环境与运行

现有推理解释器：`/home/xiang/miniconda3/envs/openslime/bin/python`（PyTorch 2.9.1+cu129、Transformers 5.3.0，依赖见各run metadata）。系统`python3`仅用于stdlib脚本与Step HTTP transport；导入官方ArcANE需要该现有环境的dotenv/openai等依赖。

D-E01角色生成以原生prompt为准，由`scripts/run_local_arcane.py`写官方兼容记录；D-E02/Summary教师与本地judge由`scripts/run_local_text.py`保存完整raw和token IDs。`queue_summary_actors.py`只按依赖完成状态推进；`queue_judges.py`的Step队列已因实际限流退出；本地评分使用`queue_local_judges.py`。密钥只在进程内存/子进程环境，不写文件。

离线复算：`scripts/summarize_results.py --asset-root /var/tmp/ssn-game-npc-d --experiment D-E01|D-E02|D-E03 --out 输出.json`。它取每个judge_id的首个合法分数，保留全部失败尝试计数；D-E03明确复用同一嵌套样本上的D-E01参照，不重复计为新调用。

## 直接状态形成参照：EvolvingWorld

官方代码固定`1de26550ccfff105f3ffe9f4b386716446291341`，HF数据固定`ae7d82d38909783805979a8055d5ae913cb982f7`。本轮大文件只下载训练混合文件和character_update单任务文件（约4.55GB），同时保存固定版本dataset card，不称完整世界模拟复现或已取得专用权重。单任务文件删除details，完整文件可恢复作品/角色/场景；两者24,977条conversation hash完全匹配。51部作品、2,671角色，22,306次相邻出场的输入profile/tracker与上次输出逐字相接；6条tracker为dict，按原生f-string存入下一输入。清单见`results/update_provenance_inventory.json`。

D-E04直接使用原生角色更新system/human；完整监督与输出留在`data/update_D-E04/`、`runs/D-E04/`，只将样本ID/hash与轻量结果入Git。这是公开训练资产上的通用模型诊断，非官方held-out rollout。该代码revision未见LICENSE文件，HF数据卡未给标准license标识；卡片正文明确说明非商用学术研究/复现，并列出训练评估用途，再分发细节未另展开。当前仅本地研究运行/读取，无vendor代码或原文再发布。原著出处仍分别核对。

## 本轮完整原始输出的持久归档

主机`fvcrc20`；独立于NVMe临时目录的持久文件：

`/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-first-residency/raw-runs-and-frozen-inputs.tar.gz`

实际归档157文件，压缩20.12 MiB、原始105.32 MiB，全部成员逐字节SHA256核验完成，归档对应研究commit为`39e7c575`。校验和、每个成员的路径/字节/hash及归档对应研究commit见[RAW-MANIFEST](results/D-RAW-MANIFEST.json)；[运行总账](results/D-RUN-LEDGER.json)把角色、状态、教师、评委、前向与API分开。[输入与评分来源核验](results/D-INTEGRITY.json)确认同题/仅一句指令、API输入与本地相同、首个完整结果选择、PUF候选与raw hash对应、四文本NLL目标一致。归档不含权重、完整第三方corpus或vendor仓库，不因此改变原资产许可；文件仅限本地研究者访问。

已配置该研究机SSH别名时可下载（亦可替换为实际登录地址）：

```sh
scp fvcrc20:/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-first-residency/raw-runs-and-frozen-inputs.tar.gz .
sha256sum raw-runs-and-frozen-inputs.tar.gz
mkdir -p restored-d
tar -xzf raw-runs-and-frozen-inputs.tar.gz -C restored-d
```

`environment.json`保存Python/torch/transformers/CUDA/GPU信息；各run metadata、runner_source、frozen tasks包含实际配置、模型revision、输入与完整输出。HF缓存中的Qwen3-8B/Qwen2.5-7B可按表中revision重新下载。环境恢复后可重播冻结任务，不需要重新抽样/生成故事。Step API没有可固定权重hash，原回包/usage/response_id保留；生成token IDs供应方不提供则明确null，不伪造。

Step5用于D-E01评价的部分/预试与D-E05状态actor分开：前者资源中断、不拼入本地主表；后者65请求/64完整状态、394,805已记录tokens。所有已记录Plan用量及早期最多2个在途未知调用见总账；绝不把未知计为0，也不把API壁钟加到GPU小时。

## 不调用模型的完整复算

下面命令在仓库根目录执行，`/var/tmp/ssn-game-npc-d`可换成解压后的完整资产根；如使用官方后处理，按上表恢复相应固定vendor revision。解释器推荐现有openslime环境。

实际脚本目录为`workbench/game-npc-agents/mine-d-affect-relationships/scripts/`：

- `recompute_arcane.py --asset-root <资产根> --project <仓库根>`：D-E01/D-E03主表、严格轨、跨评委与图，无新模型请求。
- `summarize_results.py --asset-root <资产根> --experiment D-E02 --out <输出>`：LongEvo原生文本内容表；加`--strict-native-json`为严格轨。
- `summarize_likelihood.py --asset-root <资产根> --out <输出>`：原句NLL，256次已保存前向分数复算，无新生成。
- `summarize_updates.py --asset-root <资产根> --out <输出>`：D-E04原生flag主表；加`--condition identity_line`为控制；另加`--plan-run <资产根>/runs/D-E05/step5`为强普通参照。
- `summarize_state_quality.py --asset-root <资产根> --out <输出>`：D-E04原生PUF准则单角色适配；加`--include-plan`给D-E04＋D-E05共同表与同题有效配对。
- `summarize_runs.py --asset-root <资产根> --out <输出>`和`verify_measurement.py --asset-root <资产根> --out <输出>`：总账与来源检查。所有算术从保留raw重建，不以人工改分覆盖原结果。

原生阅读范围、样本来源与许可说明见正文报告及四张权威论文卡；本轮没有跑PHASE参数适配、ArcANE-32B专用权重、EvolvingWorld专用checkpoint或完整多智能体rollout，也没有声称它们已被这些普通单步基线替代。

## 持续实验资产（D-E06–D-E09）

同一NVMe根下，`data/closed_D-E06`保存29轨迹/87后续问题、原句、三更新路径与强消费者冻结输入；`data/arcane_D-E07_v2`保存正确Monte源分片、完整81摘要与人物整理输入；旧`arcane_D-E07`及中断raw保留。`data/arcane_D-E08`复用同81输入，Step5实际82次Plan调用得到81卡，新增317,848记录tokens。`data/prefix_D-E09`为六人物的完整来源前缀、301固定窗口、15 probe/47 phase与查询边界证明。权重沿用上表revision，无新训练。

对应完整原始运行分别在`runs/D-E06`至`runs/D-E09`。D-E06–08推理和离线表已全部完成，D-E09两个前缀worker已按预算停止，完整cohort未齐，演员/评分未启动；各自metadata区分完成状态，不能将目录存在等同完成。首夜持久归档未覆盖；持续实验的完整与明确停止记录已另行归档，见末节。

- `recompute_continuation.py --asset-root <根> --project <仓库>`：按依赖完成D-E06三消费者、D-E07修正来源全表及D-E08强教师表与图，仅离线分析。
- `recompute_prefix_results.py --asset-root <根> --project <仓库>`：D-E09全47phase主表，与共同20phase的近期上下文嵌套表分开。
- `collect_continuation_costs.py --asset-root <根> --out <账本> --include-prefix --require-complete`：D-E06–09独立调用账，含Step新增用量；不把API壁钟加入GPU小时，不重复首夜账。
- `archive_runs.py --asset-root <根> --destination <新的持久目录> --manifest <清单> --include-continuation`：所有运行结束且资格检查通过后归档。完整模型输入含实际使用的来源前缀文本，限本地研究保存；原文与权重不进Git。

另外只读取得EvolvingWorld官方六部OOD作品的`extracted_data/scenes`与`character_dynamic`，hash与规模见[D-HELDOUT-SOURCE-INVENTORY](results/D-HELDOUT-SOURCE-INVENTORY.json)；尚未据此声称新实测或所有模型都未见作品。


## 可复用连续经历索引

**来源资格：** 该索引定义的是固定训练文件内按发布`scene_index`排列的后继，不认证原著时序，也不保证不同发布文件同号场景相同。后续新增[EW来源资格说明](results/D-EW-SOURCE-QUALIFICATION-2026-10-22.md)及[对照清单](results/D-EW-SOURCE-BINDINGS.json)，既有原始文件和索引不重排。

`data/EvolvingWorld/experience_index.sqlite`是固定4.18GB混合训练文件的只读索引，约28.66MiB，不复制正文。已将138,596条任务的精确UTF-8字节区间、SHA256与作品/角色/场景/任务元数据全部回读核验；51作品、2,671角色条目、22,306相邻出场链接。24,977更新出场均有同出场动机任务，其中19,937有互动生成任务。这是来源可用性，不是新增独立科研样本或已标好的成长真值。

[轻量索引清单](results/D-EXPERIENCE-INDEX.json)记录固定HF revision、原文件hash、索引hash/大小、任务数及核验覆盖；SQLite留在资产目录，不进Git。`experience_store.py`将同一出场的原生任务和同人物下次出场连接；保留未说话角色、无更新样本及原始源划分，不按模型表现挑选。返回的原生conversation包含监督目标，调用方必须把目标和未来记录与当前推理输入分开。

重建与使用：

```sh
python3 workbench/game-npc-agents/mine-d-affect-relationships/scripts/experience_store.py --build --source /var/tmp/ssn-game-npc-d/data/EvolvingWorld/train/all_tasks_with_details.json --index /var/tmp/ssn-game-npc-d/data/EvolvingWorld/experience_index.sqlite --revision ae7d82d38909783805979a8055d5ae913cb982f7 --expected-sha256 2f9dd6b90c7ed6870916cce91fc5d8ec6ac218f3c0ec6a225736c095bf751e07 --verify --out /var/tmp/experience-index-inventory.json
```

已有索引时去掉`--build`，用`--verify`全量核验；重建须选新目标路径，不覆盖已有来源记录。`ExperienceStore.get(row_id)`精确回读一条原任务并校验hash；`appearance(update_id)`返回同出场各任务ID及同人物下次出场ID，不自动构造新训练prompt。此入口供之后不同baseline与学习方案共享，原D-E01–09冻结输入不受影响。


## 补充互动资产：MiniMax Role-play Benchmark

官方[MiniMaxAI/role-play-bench](https://huggingface.co/datasets/MiniMaxAI/role-play-bench)，固定revision `3c1be2a56afbcaab19ae6b40b8a24429eae792f5`，数据卡声明Apache-2.0。本地`data/MiniMaxRolePlay`取得README及六个parquet，共79,570,650字节数据文件：英语45种子/1,485轨迹，中文50/1,650；另有相同键的3,135评分。11模型/推理档位、每种子各3run，均为作者发布的模拟互动，不是我们的推理或真人玩家记录。

[库存](results/D-MINIMAX-ASSET-INVENTORY.json)逐文件固定hash、记录schema和join覆盖。全部dialogue可按JSON解析且长度与num_turns一致，每条102项（与数据卡100生成turn及初始消息需区分）。中文一条round编号非连续，异常键/hash保留；不改原值、不按此当模型行为失败。轨迹/评分无重复键，种子引用全部存在。六项评分是已发布记录，未重新调用裁判。

获取：`snapshot_download('MiniMaxAI/role-play-bench', repo_type='dataset', revision=上述hash, allow_patterns=['README.md','data/*/*.parquet'], local_dir=资产根+'/data/MiniMaxRolePlay')`。复核使用`scripts/inspect_interaction_release.py --root <本地目录> --revision <固定hash> --out <库存>`，需现有openslime环境的pyarrow。

数据卡明确这是偏聊天的合成公开子集，英语统一用户侧字段、中文按场景变化；评价将有铺垫的人物变化与OOC区分，并关注不替用户说话、叙事推进和回应性。它没有阶段人物弧或可执行游戏世界，六表也未提供完整用户模拟器/细粒度judge运行代码；因此作为互动证据资产，不冒称已复现其生成/评分协议。角色原设定、原始轨迹及未改评分只留仓库外。


## 持续驻留的最终持久归档（含明确未完成记录）

`/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-continuation/raw-runs-and-frozen-inputs.tar.gz`

实际372文件、58,688,960压缩字节，所有成员逐项SHA256核验；对应研究commit `86c90ad633937c520247caeec54e9c66842b5fe5`。归档SHA256：

`6de6db7ee89cbc431cc3bc09b622784d38e4289494a2f88687dc326fc7aec974`

[逐成员清单与停止状态](results/D-CONTINUATION-RAW-MANIFEST.json)保存完整/停止run资格。该包累积保留首夜及续测raw、冻结计划输入、配置、runner源码、token IDs与日志；D-E07源中断、Step部分校准、D-E09预算停止仍明确为部分记录，不因归档而成为完成实验。D-E09冻结计划含未处理窗口，实际覆盖以[覆盖表](results/D-E09-COVERAGE.json)为准。没有权重、vendor或完整未使用的第三方corpus；文件仅限本地研究访问，下载方式同前述SSH/scp示例，替换为本节路径。

[全部调用/成本记录](results/D-RESIDENCY-TOTALS.json)与[完成结果](results/D-CONTINUATION-REPORT-2026-10-22.md)分开：7,080本地生成记录、495 Plan请求，不包含公开MiniMax旧轨迹；D-E09无角色评分。旧首夜归档继续保留原hash。

## 人物适应学习准备：原生视图与SFT导出

固定来源仍为上述EvolvingWorld revision与4.18GB混合训练文件。[数据契约及重建命令](data/README.md)、[固定作品政策](data/adaptation_view_policy.json)、[全量清单](results/D-ADAPTATION-VIEWS.json)共同登记：51作品24,977更新，所有22,306同人物后继的profile/tracker接续匹配；18,144连接有后续互动。它们是发布顺序资格，不是原著时序证明。

仓库外工作路径：`/var/tmp/ssn-game-npc-d/data/adaptation_views_v1/`。`episodes.jsonl`为19,029,259字节指针，SHA256 `3d0ce18d3a99c3dd14ae36a9a606ac0cba197ecba22583b3f425aa3752af3371`；`native_update_train.jsonl`实际14,079条、202,960,875字节，SHA256 `bec24aa18aeb0816dc59494a13bfa7dde5a95bec34566ec96dc323280837feb0`。原生prompt与completion分字段，全文不进Git。已观察的9作品不进入新训练或新测试，完整划分见清单；不认证基础模型或既有专用模型未见这些作品。

持久本地归档：`/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-22-adaptation-preparation/native-learning-views.tar.gz`，含视图、原生训练导出、政策与必要脚本快照；逐成员校验与完整hash见[准备归档清单](results/D-ADAPTATION-PREPARATION-MANIFEST.json)。仅限本地研究访问，不公开再分发原始文本。该资料准备没有模型调用、训练或新的心理标签，不能加入实验调用总数。

## D-E10正在运行的学习与后续互动

- 隔离解释器：`/var/tmp/ssn-game-npc-d/venvs/adaptation/bin/python`，使用openslime系统包，局部安装`peft==0.21.2`、`torchao==0.16.0`。torch2.9.1+cu129、transformers5.3.0未变；torchao可选量化C++扩展未加载，普通BF16/LoRA不依赖它。
- 训练缓存：`data/training_D-E10/{tokens.bin,entries.jsonl,manifest.json}`；int32精确tokens、完整样本边界、来源row/hash及作品划分。14,079更新＋14,079动机＋23,088互动＋128验证，无截断/超长排除。[逐文件hash](results/D-E10-training-data.json)。早期单进程准备目录保留中断原因；其3,819条完整输出与并行缓存前缀逐字相同，没有不同数据版本。
- 评测：`data/evaluation_D-E10/`内episodes/references分离；6作品47经历87后续context，来源与资格见[selection](results/D-E10-selection.json)。不是同场景行为重放或真人交互。
- 实际训练：`runs/D-E10/train_update_v2/`与`train_multitask_v2/`，保存初始/半程/最终验证、每步loss/梯度/样本与tokens、LoRA/优化器/RNG、源码与元数据。首轮`train_update`/`train_multitask`均在适配器装配失败、0优化步，原记录不删除。base权重revision沿用Qwen3-8B；只有最终完整训练checkpoint进入主评测。
- 七系统：`runs/D-E10/system_<name>/`保存update/motivation/actor与统一recovery所有尝试，实际messages、生成IDs、模型/adapter hash；states/motivations/outputs给出确定性选择与失败承接。`judges/<name>`保留盲评及事前12组重复；`likelihood/`使用共同未适配8B评分。
- 运行编排：`runs/D-E10/{training_jobs,evaluation_jobs,analysis_jobs}.json`；stdout在`logs/D-E10-*`。评分等strong32完整释放GPU后才装模型，SFT路径等对应最终完整checkpoint。`finish_status.json`明确汇总/推送失败或完成；不会改用中途checkpoint或幸存系统。
- 当前权重和raw仍在运行中，不打包搬动；结束后再按实际完整性归档。所有大文件不入Git，代码和轻量读数同步原main。D-E10全部本地，无新API和现金fallback；旧D-E01–09总账保持原数字，另计本轮。

### D-E10本地I/O与启动修复（2026-10-23，非新实验条件）

共享家目录的权重/依赖读取拖慢阶段切换，已按原文件逐字复制到NVMe。`models/local_snapshots/<revision>/LOCAL_MIRROR.json`登记完整校验；8B为16,397,461,266字节、32B为65,540,298,478字节，只有完成且来源匹配的镜像会被推理/NLL选用。配置、tokenizer与LFS内容hash一并核验，不改变模型版本。简明路径/hash见[D-E10-local-cache](results/D-E10-local-cache.json)。

`runtime/site-packages-v2/RUNTIME_MIRROR.json`含19,970文件、7,940,962,509字节逐项hash；隔离venv的`game_npc_local_runtime.pth`启用相同依赖字节，PEFT/TorchAO局部版本保持不变。已实测导入Torch2.9.1、Transformers5.3.0、PEFT0.21.2、NumPy1.26.4。训练进程未中断或换运行环境；启动条件不同，不把旧/新阶段壁钟差当方法效率增益。首轮离线预扫描中断目录和日志保留。

为避免shell profile等待，从本地目录以`/bin/bash`非login启动。四个模型入口的Git provenance改为脚本定位仓库，消除cwd依赖。首次盲评因此失败时尚无metadata/模型输出、0评分调用；`judges/base_setup_failed_workdir`、`queue_before_cwd_fix.json`及`finish_before_judge_cwd_fix.json`保留。新队列已启动，不覆盖首次失败记录；作业表记录全部PIDs/原因。

首次实际评分前固定judge batch为2，并明确动机生成于场景入口、回复发生于后续可见互动处；不得要求入口动机预知后来对话。五维量表与样本未改。该澄清早于任何评分生成；不是根据分数改读数。七系统主表仍只在全部注册路径结束后生成。

## D-E11：官方模拟器下的连续生成

固定HF revision的`data/EvolvingWorld/test/test_snapshots_ood.json`保存106官方起点，33,921,259字节；下载方式为HF snapshot_download指定本文件及既有revision。源hash与6个固定索引见[D-E11-selection](results/D-E11-selection.json)。`data/native_D-E11/snapshots.json`只有模拟所需初始字段，无ground_truth_scenes/tag；回顾性初始资料的资格不因此变成严格时间证据。

`runs/D-E11/{base,update_sft,multitask_sft}/`保留每次物理调用raw、精确输入/生成tokens、采样设置、adapter路由和metadata；每个`snapshot_<index>`有实时result/trace/meta、官方all_scenes/character_dynamic/world_dynamic视图和日志。官方vendor实现不修改、不入Git，本地runner保存原始源码及vendor逐文件hash。世界调用禁用LoRA；U-SFT仅角色更新启用；MT三个角色任务启用。快照输入先冻结，生成过程中不插入未来参考对白。

`runs/D-E11/jobs.json`登记GPU2实际生成队列，后续评分等D-E10与三条互动路径完整结束。该项是多角色原生短轨迹参照，用于人物变化的交互后果，不是新多智能体社会研究线或真人玩家试验；最多3场景不能称长期人物成长已验证。

首次资源中断的`base_interrupted_gpu_contention`含21完整生成记录及0完整轨迹。OOM/中断时原client未返回的调用没有完整输出，INTERRUPTION与实验卡明确其缺失，不将21称全部启动数。后续client先记录requests，失败写error及未知completion tokens。新队列等GPU2空闲，已消耗231.201秒仍计累计预算；不隐藏原失败或终止别的作业。

生成队列优先GPU2；D-E10全部完成后，也可使用它释放的空闲GPU0/1/3，实际选择写入status与模型metadata。不会在D-E10训练/评价期间夺用其卡，也不依赖其他项目必须停机。

### 完成后持久归档队列（尚未完成）

`archive_adaptation_study.py`分别等待D-E10正式结果/D-E11正式评分完整完成，将原始记录、失败尝试、冻结评测输入和最终LoRA/优化器状态保存到`/home/xiang/research-assets/game-npc-agents/mine-d/2026-10-23-adaptation/{D-E10,D-E11}/raw-and-final-adapters.tar.gz`。只保留最终训练权重，基础/中途权重不复制入包；训练token缓存可按源revision及manifest重建。逐成员SHA复读通过后才产生Git轻量`D-E10-RAW-MANIFEST.json`或`D-E11-RAW-MANIFEST.json`。当前是已启动的等待任务，路径预登记不代表归档已存在；失败不会发布完成清单。
