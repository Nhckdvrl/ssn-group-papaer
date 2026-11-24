"""Check ARR author-response drafts: character count (limit 5,000 per response) and forbidden links.
usage: python3 count_chars.py responses/*.md"""
import re, sys

LIMIT = 5000
URL = re.compile(r"(https?://|www\.|\]\()", re.I)

for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    # drafting notes inside HTML comments are not part of the response
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    n = len(body)
    links = URL.findall(body)
    flag = "OK" if n <= LIMIT and not links else "CHECK"
    print(f"{flag:5s} {path}: {n} chars ({LIMIT - n:+d} left){'; links found: ' + str(len(links)) if links else ''}")
