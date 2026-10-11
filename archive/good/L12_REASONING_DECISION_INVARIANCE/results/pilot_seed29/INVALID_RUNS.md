# Excluded Runs

- `instruct_sft_common_raw/`: 237/240 invalid under a raw prompt. The released SFT checkpoint requires its native chat template.
- `think_sft_len512_invalid_parser/`: only 110/240 continuations closed `</think>`; a loose parser read A/B tokens inside truncated reasoning. Replaced by the strict 1,024-token run.
- `think_sft_no_think_len32_invalid_parser/`: 0/240 strict direct answers after an injected `</think>`; the model continued explanatory generation and hit the cap. Excluded from behavior and mechanism claims.
