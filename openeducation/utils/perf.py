import time
from contextlib import contextmanager


@contextmanager
def timed(section: str):
    t0 = time.time()
    yield
    dt = time.time() - t0
    print(f"[perf] {section}: {dt:.3f}s")
