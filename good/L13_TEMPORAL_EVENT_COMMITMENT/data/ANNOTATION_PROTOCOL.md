# L13 — Annotation protocol (stimuli_v1)

Three judgements per item, from the passage alone.

**Q1 strict commitment.** "Based only on the passage, is the statement true?"
- `YES` — the passage *guarantees* the statement is true.
- `NO` — the passage rules it out.
- `ND` — the passage leaves it open.

Decide by entailment, not by what probably happened in the world. If you can
imagine a continuation of this passage on which the statement is false, and
another on which it is true, the answer is `ND`.

**Q2 occurrence likelihood.** How likely is it that the statement is true?
1 very unlikely · 2 unlikely · 3 equally likely and unlikely · 4 likely · 5 very likely.
This is the pragmatic judgement Q1 excludes. Q1 and Q2 may disagree, and should.

**Q3 naturalness.** Would a native speaker write this? 1 very unnatural … 5 fully natural.

Items are presented shuffled, without condition or gold. Blinding is partial: the
construction is visible in the passage itself. Recorded as author annotation.
