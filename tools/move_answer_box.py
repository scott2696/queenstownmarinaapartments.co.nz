#!/usr/bin/env python3
"""Move the 'Quick answer' box to sit below the operator table.

Six pages already had this layout; this brings the rest into line.
Idempotent - pages where the box already follows the toplist are skipped.
Run from the repo root:  python3 tools/move_answer_box.py
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def block_span(html, start):
    depth = 0
    for m in re.finditer(r'<div\b|</div>', html[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return start, start + m.end()
    return None


def move(path):
    html = path.read_text(encoding='utf-8')
    ab = html.find('<div class="answer-box">')
    tl = re.search(r'<div class="toplist"[^>]*>', html)
    if ab < 0 or not tl:
        return 'no answer-box or no toplist'
    if ab > tl.start():
        return 'already below'

    ab_span = block_span(html, ab)
    if not ab_span:
        return 'unbalanced answer-box'
    block = html[ab_span[0]:ab_span[1]]

    # strip trailing whitespace left behind so we don't accumulate blank lines
    rest = html[:ab_span[0]] + html[ab_span[1]:].lstrip('\n')

    tl2 = re.search(r'<div class="toplist"[^>]*>', rest)
    tl_span = block_span(rest, tl2.start())
    if not tl_span:
        return 'unbalanced toplist'

    out = rest[:tl_span[1]] + '\n' + block + rest[tl_span[1]:]
    path.write_text(out, encoding='utf-8')
    return 'moved'


def main():
    counts = {}
    for p in sorted(ROOT.glob('**/index.html')):
        r = move(p)
        counts[r] = counts.get(r, 0) + 1
        if r == 'moved':
            print(f'  moved: {p.relative_to(ROOT)}')
    print()
    for k, v in sorted(counts.items()):
        print(f'  {v:3}  {k}')


if __name__ == '__main__':
    main()
