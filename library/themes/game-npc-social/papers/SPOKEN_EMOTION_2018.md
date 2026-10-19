# Spoken Conversational AI in Video Games – Emotional Dialogue Management Increases User Engagement（IVA 2018）`[证据级别：完整正文，作者上传HTML抽取]`

规范记录：`spoken_emotion_2018`。Jamie Fraser、Ioannis Papaioannou、Oliver Lemon；IVA 2018，179–184，DOI 10.1145/3267851.3267896。**实读：作者Ioannis Papaioannou于2018-10-11上传的6页会议稿完整正文§1–7、图文、两表和实例（ResearchGate公开全文抽取）；未取得可下载PDF，PDF请求403，正式排版未逐像素复核。** [作者全文](https://www.researchgate.net/publication/328215976_Spoken_Conversational_AI_in_Video_Games-Emotional_Dialogue_Management_Increases_User_Engagement) · [机构发表记录](https://researchportal.hw.ac.uk/en/publications/spoken-conversational-ai-in-video-games-emotional-dialogue-manage/)

## 1. 论文形态、背景与来源

游戏对话系统与初步玩家对照。**DOCUMENTED**：把2017 Alexa Challenge的Alana集成到Unity酒馆，通过语音中的礼貌/威吓改变NPC情绪和信息披露，探索自由表达怎样成为玩法。它早于LLM，不能在新研究中把“语言影响情绪再影响剧情信息”写成新能力。

## 2. 具体机制

Windows ASR、IBM Watson**转录文本**tone analysis与TTS、AIML persona和Alana响应选择。Hulda参考Skyrim人物/台词/wiki，但只是自建酒馆原型。ASR按轮、不可打断、有键盘备用。emotion是−1至1标量：anger −.1，joy +.1；sadness通常被解释为道歉而+.1，另有角色相关规则与反向调节。达到±.4才释放线索，正面状态给更多文字信息。正文“乘2把−.6变−.3”有算术表述错误，应保留而不冒充核过实现。

## 3. 数据、基线和真实结果

**16名参与者，两组各8人**，情绪开/关between-subject，同一个酒馆、收集三条线索后结束。情绪条件同时增加了信息门槛，因此平均9分43秒对5分05秒（作者p<.05，未报统计量/方差）不能单独解释为更好投入，也可能是达成任务需要更多对话。

享受项：开启组75% agree、25% strongly agree；关闭组12.5% disagree、50% agree、37.5% strongly agree。开启组更多人肯定享受，但更强烈同意比例反而较少；不宜写成全面增强。沉浸项开启6/8、关闭2/8为同意或非常同意，只有描述统计，未报显著性。没有长期依恋、更多人物或现代强LLM比较。

## 4. 与最近邻的距离

| 近邻 | 区别 |
|---|---|
| [情绪评价引擎](APPRAISAL_ENGINES_2016.md) | 本篇用简化情绪阈值构成实际谜题，未实现复杂OCC/应对推理。 |
| [Chain-of-Emotion](CHAIN_EMOTION_2024.md) | CoE可开放生成角色情绪语义；本篇演示普通标量+规则已能让情绪成为可利用交互。 |
| [礼貌语音玩法](ETIQUETTE2024.md) | 都把言语方式变成机制，提示“时间更长”同时可能包含投入和摩擦。 |
| [开放VR对话](DIALOGS_GENAI2026.md) | 后者研究生成NPC归因与修复劳动；本篇有开/关对照，但情绪与任务难度共同改变。 |

## 5. 证据评价与对我们

这补全了此前知识库标作“只有摘要”的原文欠账，但证据仍小。可迁移的是把角色反应落实到玩家能够理解的差异；新方法应对比同等剧情阻力/信息条件，拆开情绪表示、交互难度和语言自然性。仅把好感值包装成LLM并让玩家多说几轮，没有足够增量；复杂情绪也无需都变成开门密码。
