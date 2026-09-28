# E000 — offline corpus and construct audit

Read [RESULTS.md](RESULTS.md) first. This is an exploratory data experiment, not a model run. The protocol was written after initial inspection exposed linked INIs, so it is not a preregistration.

Run from the repository root:

```sh
good/L02_REFERENTIAL_COMMITMENT/.venv/bin/python -B good/L02_REFERENTIAL_COMMITMENT/scripts/run_data_audit.py --run-id UNIQUE_ID
good/L02_REFERENTIAL_COMMITMENT/.venv/bin/python -B -m unittest discover -s good/L02_REFERENTIAL_COMMITMENT/tests -v
good/L02_REFERENTIAL_COMMITMENT/.venv/bin/python -B good/L02_REFERENTIAL_COMMITMENT/scripts/extract_training.py --verify-existing
```

New runs refuse to overwrite old runs. The original archive is a gzip/tar despite its retained download name train.zip. `extract_training.py` verifies existing bytes and the member manifest. Acquisition manifests and specifications are under `data/`; source admissibility decisions are in `data/SOURCE_ADJUDICATION.md`. An old acquisition field named valid only established successful transfer and is not a corpus-validity gate.

The local .venv uses CPython 3.12.3 and no third-party packages. Raw archives, extracted large source files, and paper PDFs/text are stored locally and excluded from Git. Small manifests, code, protocols, reports and processed observations remain versionable. No generated stimulus is empirical evidence; malformed graph test fixtures test only software.
