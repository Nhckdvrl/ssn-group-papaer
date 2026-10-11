class _C:
    def __getattr__(self, k): return ""
Fore = Back = Style = _C()
def init(*a, **k): pass
