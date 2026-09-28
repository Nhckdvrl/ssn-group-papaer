# E001 Original-State Recoverability

**Verdict:** GO, with a narrower acquisition contract.

E001 takes 32 directly quoted old→new operations from the first T1 pool and checks the current linked PMC article. Matching is restricted to title/abstract/body; back-matter change notes are separately recorded so they cannot create false historical-state hits.

| Current PMC content state | Count |
|---|---:|
| old only | 7 |
| old and new | 7 |
| new only | 10 |
| neither exact selector | 7 |
| no PMC full text | 1 |

Thus 14/32 (43.75%) expose the old state somewhere in current article content; 14/31 (45.16%) among PMC-available originals. This is a convenience diagnostic, not a population estimate.

The result changes the data contract. A correction notice alone is insufficient: model items must verify that the supplied original excerpt contains the obsolete selector, and must exclude any excerpt that already leaks the corrected selector. Current PMC articles may be unmodified, fully updated, or hybrid.

Combining the E000 lower T1-yield bound with this diagnostic rate gives a conservative planning scale of roughly 3.6k screened notices for 150 old-state-recoverable items. This multiplication is only for acquisition planning because E001 is not a random sample.

Reproduce:

```bash
python3 scripts/audit_original_state.py \
  --config configs/e001_original_state.json \
  --annotations data/annotations/e001/old_new_selectors.json
```
