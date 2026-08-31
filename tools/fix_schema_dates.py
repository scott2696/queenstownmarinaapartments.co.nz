#!/usr/bin/env python3
"""Ensure every page-level schema node carries datePublished and dateModified.

Walks nested structures including @graph wrappers. Idempotent - nodes that
already have both dates are left alone.
"""
import re, json, glob, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = {'WebPage', 'AboutPage', 'ContactPage', 'ProfilePage', 'CollectionPage'}
PUBLISHED = '2026-01-15'   # matches the convention on the other 22 pages
MODIFIED = '2026-08-31'


def stamp(node):
    """Add missing dates to any page-level node, at any depth."""
    changed = False
    if isinstance(node, list):
        for x in node:
            changed |= stamp(x)
        return changed
    if not isinstance(node, dict):
        return False
    if node.get('@type') in PAGE:
        if 'datePublished' not in node:
            node['datePublished'] = PUBLISHED
            changed = True
        if 'dateModified' not in node:
            node['dateModified'] = MODIFIED
            changed = True
    for v in node.values():
        changed |= stamp(v)
    return changed


def main():
    touched = 0
    for p in sorted(ROOT.glob('**/index.html')):
        h = p.read_text(encoding='utf-8')
        hit = False

        def repl(m):
            nonlocal hit
            try:
                d = json.loads(m.group(1))
            except ValueError:
                return m.group(0)
            if stamp(d):
                hit = True
                return ('<script type="application/ld+json">'
                        + json.dumps(d, ensure_ascii=False) + '</script>')
            return m.group(0)

        h2 = re.sub(r'<script type="application/ld\+json">(.*?)</script>',
                    repl, h, flags=re.S)
        if hit:
            p.write_text(h2, encoding='utf-8')
            print(f'  stamped: {p.relative_to(ROOT)}')
            touched += 1
    print(f'\npages updated: {touched}')


if __name__ == '__main__':
    main()
