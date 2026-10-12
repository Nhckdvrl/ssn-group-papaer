"""Run an experiment engine on Gemma-2, which needs its BOS token at the start of the prompt.

Every engine encodes text with add_special_tokens=False. For Gemma-2 this wrapper prepends the BOS token to
any encoding of text that starts with the shared prompt header, so the processed prompt begins with BOS while
demonstration blocks, label words and queries are encoded exactly as for the other models.

Usage: python scripts/run_gemma.py scripts/<engine>.py <engine args>
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e56_query_adapter import HEAD
import transformers

_orig = transformers.AutoTokenizer.from_pretrained


def _patched_from_pretrained(*args, **kwargs):
    tok = _orig(*args, **kwargs)
    base = type(tok)
    bos = tok.bos_token_id
    assert bos is not None

    class GemmaBOS(base):
        def encode(self, text, *a, **kw):
            ids = base.encode(self, text, *a, **kw)
            if isinstance(text, str) and text.startswith(HEAD) and (not ids or ids[0] != bos):
                ids = [bos] + list(ids)
            return ids

        def __call__(self, text, *a, **kw):
            out = base.__call__(self, text, *a, **kw)
            if isinstance(text, str) and text.startswith(HEAD) and out['input_ids'][:1] != [bos]:
                out['input_ids'] = [bos] + list(out['input_ids'])
                if 'attention_mask' in out:
                    out['attention_mask'] = [1] + list(out['attention_mask'])
                if 'offset_mapping' in out:
                    out['offset_mapping'] = [(0, 0)] + list(out['offset_mapping'])
            return out

    tok.__class__ = GemmaBOS
    return tok


transformers.AutoTokenizer.from_pretrained = _patched_from_pretrained
engine = sys.argv[1]
sys.argv = sys.argv[1:]
sys.path.insert(0, str(Path(engine).resolve().parent))
runpy.run_path(engine, run_name='__main__')
