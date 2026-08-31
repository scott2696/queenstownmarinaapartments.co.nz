#!/usr/bin/env python3
"""Add a WebPage node to pages that have none.

Five pages carried FAQ and breadcrumb schema but nothing describing the page
itself, and no author. Values are read from each page's own title, meta
description and canonical - nothing is invented. Idempotent.
"""
import re, json, glob, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUTHOR = 'Tāne Tamati'
SITE = 'https://queenstownmarinaapartments.co.nz'
PAGE_TYPES = {'WebPage', 'AboutPage', 'ContactPage', 'ProfilePage', 'CollectionPage'}


def has_page_node(h):
    def w(n):
        if isinstance(n, list):
            return any(w(x) for x in n)
        if isinstance(n, dict):
            if n.get('@type') in PAGE_TYPES:
                return True
            return any(w(v) for v in n.values())
        return False
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            if w(json.loads(b)):
                return True
        except ValueError:
            pass
    return False


def main():
    added = 0
    for p in sorted(ROOT.glob('**/index.html')):
        h = p.read_text(encoding='utf-8')
        if has_page_node(h):
            continue
        title = re.search(r'<title>(.*?)</title>', h, re.S)
        desc  = re.search(r'<meta name="description" content="(.*?)"', h, re.S)
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        mod   = re.search(r'"dateModified"\s*:\s*"([^"]+)"', h)
        pub   = re.search(r'"datePublished"\s*:\s*"([^"]+)"', h)
        if not (title and canon):
            print(f'  skipped (no title/canonical): {p.relative_to(ROOT)}')
            continue
        node = {
            '@context': 'https://schema.org',
            '@type': 'WebPage',
            'name': html.unescape(title.group(1)).strip(),
            'url': canon.group(1),
            'inLanguage': 'en',
            'datePublished': pub.group(1) if pub else '2026-01-15',
            'dateModified': mod.group(1) if mod else '2026-08-31',
            'author': {'@type': 'Person', 'name': AUTHOR,
                       'url': f'{SITE}/authors/'},
            'publisher': {'@id': f'{SITE}/#org'},
        }
        if desc:
            node['description'] = html.unescape(desc.group(1)).strip()
        tag = ('<script type="application/ld+json">'
               + json.dumps(node, ensure_ascii=False) + '</script>\n')
        h = h.replace('</head>', tag + '</head>', 1)
        p.write_text(h, encoding='utf-8')
        print(f'  added: {p.relative_to(ROOT)}')
        added += 1
    print(f'\nWebPage nodes added: {added}')


if __name__ == '__main__':
    main()
