"""Write a {pid: cell} assignment file."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from generator import generate

def main():
    pool, n, cells, offset, out = sys.argv[1], int(sys.argv[2]), sys.argv[3].split(","), int(sys.argv[4]), sys.argv[5]
    props = generate(pool, n)
    a = {p["pid"]: cells[(i + offset) % len(cells)] for i, p in enumerate(props)}
    json.dump(a, open(out, "w"), indent=0)
    from collections import Counter
    print(out, Counter(a.values()))

main()
