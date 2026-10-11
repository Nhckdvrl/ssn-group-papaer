"""Import-only shim for a missing, unused VLMEvalKit submission helper.

The pinned Curation-Bench vendor's run.py imports result_transfer at module
load time, but the file is absent. E12 does not evaluate MMMU_TEST or
MMT-Bench_ALL, the only two branches that call these functions. Fail closed
if either branch is ever reached.
"""

from __future__ import annotations

import sys
from types import ModuleType


def _unsupported_result_transfer(*args, **kwargs):
    raise RuntimeError("E12 compatibility shim cannot run submission transfer")


module = ModuleType("vlmeval.utils.result_transfer")
module.MMMU_result_transfer = _unsupported_result_transfer
module.MMTBench_result_transfer = _unsupported_result_transfer
sys.modules[module.__name__] = module
