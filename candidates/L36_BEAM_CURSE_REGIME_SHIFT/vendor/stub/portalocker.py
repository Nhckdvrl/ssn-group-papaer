class Lock:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): return False
def lock(*a, **k): pass
def unlock(*a, **k): pass
