# What Attention Recalls and Recurrence Controls in Hybrid Language Models（2026预印本，会议状态未核对）[证据：正文§3–4、附录B/C/E核对]

原文：https://arxiv.org/html/2609.04434v1；代码：https://github.com/kirillTerra/split-prefill

1. **形态：** 两种原生记忆的功能分离＋cache-level干预。
2. **问题：** attention KV与recurrent状态是不是只有长/短记忆差别；作者从小型事实检索、语言/人格控制建立另一种分工。
3. **idea来源：** DOCUMENTED为把同时需retrieval/control的大benchmark拆成isolated任务；文章次序非真实发现时间线。
4. **方法所有权：** split-prefill保留一个通道，state-swap交叉两个真实context的KV与recurrent/conv状态；两个query完全相同。未来query仍正常处理。
5. **关键链：** dictionary/list经KV可回忆，language/persona经rec可保留；crossed dictionary+language使值取KV side、语言取rec side。Qwen3.5-27B亦有单seed扩展，不能说首次在此模型交换两记忆。
6. **技术学习：** cached multi-token query可能默默忽略恢复的recurrent状态。附录B要求进入initial_state或单token连续，conv必须一起保存。切口应在同user turn；render一次再按token boundary切，不分别套模板。
7. **证据边界：** 功能不是静态全部内容；KV也可能有response mode信息但此计算未有效使用。跨memory实际jointstate不保证自然分布；rec-only位置变0是作者明确选择，不应误用成完美条件控制。作者的persona Qwen2.5 judge“different family”措辞与Qwen被测家族关系需谨慎，非我们证据依据。
8. **可迁移动作：** 当两个解释在完整模型答案上相同时，让内部两记忆带互相矛盾的信息，再读一个回答中的两个独立属性。
9. **ICES：** E103借用state-swap；全部输出仍yes/no，从同样格式的demo推断c与私人p，不直接提供language/style指令。四函数profile能区分criterion/private polarity/整函数两memory依赖，但cache广泛携带多种信息，不能仅凭分工命名为独立abstract程序。若只是KV支持整个rule，符合已有retrieval框架，增量有限，应回到E91形成机制而非加层扫描。
