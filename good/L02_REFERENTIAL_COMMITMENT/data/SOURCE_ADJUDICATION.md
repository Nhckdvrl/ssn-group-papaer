# Source identity adjudication — 2026-09-08

Early acquisition manifests contain a field `valid` that checked HTTP success (and PDF magic for PDFs). **It did not verify dataset identity.** Keep these records immutable; the decisions below supersede that field for research use. The current downloader separates transport, payload format, and research identity.

| Payload | Decision | Evidence |
|---|---|---|
| `raw/semeval2010/train.zip` | Accepted original training-package route | Preserved original Task 10 training page links to this URL; archived binary contains named Task10TrainingFN and Task10TrainingPB nested tar files. Original README matches accessible Saarland README bytes. NI, frame and sentence counts reproduced. Not a bitwise comparison to an unavailable live 2010 package. |
| `raw/semeval2010/test_candidate.zip` | Rejected: wrong task | Archive member names identify SemEval2010_task8_data_release. Similar timestamp did not establish identity. No observations extracted or used. |
| `raw/semeval2010/test_exact_response.bin` | Rejected: not data | 244-byte HTML resource-unavailable notice, despite HTTP 200. |
| `raw/dkpro_sample/semeval1010-en-sample.xml` | Parser reference only | Pinned DKPro commit and NOTICE; one sentence, not a corpus release. |
| `raw/official_docs/legacy_data_portal.html` | Access failure | HTTP 404 preserved. |
| `raw/semeval2010/extracted/.../tiger/*.xml` | Accepted for training-release descriptive audit | Named archive members and SHA-256 recorded. withHeads and companion agree on NI flags, targets and links. Some semantic links and published count definitions remain unresolved. |

The original annotation guide is the archive member `Semeval2010Task10TrainingFN/annotation_guidelines.pdf`. `train_members_manifest.json` pins its bytes. The extracted text is a convenience rendering; PDF is authoritative. Original annotations are not rewritten.

No test set, independently verified negative-support gold, or replication corpus has yet been admitted. No model weights were downloaded or modified.
