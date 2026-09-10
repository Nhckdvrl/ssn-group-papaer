# Invalid runs — allenai/Olmo-3-7B-Instruct-DPO

Excluded from every analysis. Not a scientific result.

The harness uses raw few-shot text prompts, matching the parent's lm-eval-harness
setup. Olmo-3-7B-Instruct-DPO does not accept them: at **full** readout it emits zero
characters on `gsm8k_gen_cot` and `gsm8k_gen_direct` (`mean_out_chars = 0`, accuracy
0.0000), so the baseline itself is broken and no relative-performance ratio computed
from it means anything. `mmlu_gen_cot` at full readout is 0.1475 with a parse rate of
0.193, also degenerate.

This is a prompt-format failure of the harness on a chat-tuned checkpoint, not a
property of the model or of the intervention. The additional model families therefore
use checkpoints that accept raw few-shot prompting, which is also closer to the
parent's setup.

Retained for the audit trail only.
