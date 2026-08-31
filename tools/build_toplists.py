#!/usr/bin/env python3
"""Regenerate operator toplists from data/operators.json.

Idempotent: rewrites the contents of every <div class="toplist"> on the mapped
pages. Commission terms live outside this repo and are never rendered.
Run from the repo root:  python3 tools/build_toplists.py
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT/'data/operators.json').read_text())['operators']

CASINO_PAGES = """index.html online-casinos online-pokies casino-apps casino-bonuses
casino-rewards-casinos fast-payout-casinos free-spins-no-deposit highest-rtp-pokies
minimum-deposit-casinos minimum-deposit-casinos/1-dollar no-deposit-casinos
no-wagering-free-spins casino-reviews jackpot-city-alternatives
captain-cooks-alternatives luxury-casino-alternatives spin-casino-alternatives
zodiac-casino-alternatives""".split()
CRYPTO_PAGES = """crypto-casinos crypto-casinos/bitcoin crypto-casinos/ethereum
crypto-casinos/no-kyc""".split()
# Sports intentionally unmapped - see MIGRATION.md.
SPORTS_PAGES = []

DEFAULT_OFFER = "Visit site for current offer"


def held(op, cat):
    h = op.get('hold') or {}
    return h.get('all') or h.get(cat)


def link_for(op, cat):
    if cat == 'casino':
        return op['casinoLink']
    if cat == 'sports':
        return op['bettingLink']
    return op['casinoLink'] or op['bettingLink']


def lineup(cat):
    out = []
    for op in DATA:
        if not op[cat]:
            continue
        if held(op, cat):
            continue
        url = link_for(op, cat)
        if not url:
            continue
        out.append((op, url))
    return out


def card(op, url, rank):
    name = op['name'].replace('&', '&amp;')
    href = url.replace('&', '&amp;')
    offer = (op['offer'] or DEFAULT_OFFER).replace('&', '&amp;')
    stars = ''
    if op.get('rating'):
        full = int(op['rating'])
        stars = ('<div class="toplist-stars">'
                 + '<span class="star">&#9733;</span>' * full
                 + '</div>')
    return (
        f'<div class="toplist-item" id="{op["slug"]}">'
        f'<div class="toplist-rank">{rank}</div>'
        f'<div class="toplist-logo-wrap"><div class="toplist-logo">'
        f'<span style="font-weight:800;color:#16233a;font-size:.8rem;'
        f'text-align:center;line-height:1.1">{name}</span></div>{stars}</div>'
        f'<div class="toplist-info"><div class="toplist-name">{name}</div>'
        f'<div class="toplist-bonus">{offer}</div></div>'
        f'<div class="toplist-cta"><a href="{href}" class="btn-play" '
        f'rel="nofollow sponsored noopener" target="_blank">Play Now</a></div>'
        f'</div>'
    )


def block_span(html, start):
    """Return (start, end) of the balanced div beginning at `start`."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', html[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return start, start + m.end()
    return None


def rewrite(page, cat):
    path = ROOT / (page if page.endswith('.html') else f'{page}/index.html')
    if not path.exists():
        print(f'  MISSING {page}'); return 0
    html = path.read_text(encoding='utf-8')
    cards = ''.join(card(op, u, i) for i, (op, u) in enumerate(lineup(cat), 1))

    # match the container with any attributes (some carry id="toplist") and
    # reuse the original opening tag so ids survive a rebuild
    spans = []
    for m in re.finditer(r'<div class="toplist"[^>]*>', html):
        sp = block_span(html, m.start())
        if sp:
            spans.append((sp[0], sp[1], m.group(0)))
    count = len(spans)
    for s, e, open_tag in reversed(spans):   # back-to-front keeps indices valid
        html = html[:s] + open_tag + cards + '</div>' + html[e:]

    # the placeholder disclaimer is no longer true once real links ship
    html = re.sub(
        r'<strong>Offers and links (?:below )?are placeholders</strong>[^<]*',
        '<strong>We may earn a commission</strong> from the operators below. '
        'This never affects our rankings, which follow our '
        '<a href="/review-methodology/">review methodology</a>. '
        'Verify current terms on each site. ',
        html)
    path.write_text(html, encoding='utf-8')
    return count


SITE = 'https://queenstownmarinaapartments.co.nz'


def rebuild_itemlist(page='index.html', cat='casino'):
    """Keep the ItemList structured data in sync with the visible toplist."""
    path = ROOT / page
    html = path.read_text(encoding='utf-8')
    ops = lineup(cat)
    items = [{"@type": "ListItem", "position": i, "name": op['name'],
              "url": f"{SITE}/#{op['slug']}"}
             for i, (op, _) in enumerate(ops, 1)]

    def repl(m):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        if d.get('@type') != 'ItemList':
            return m.group(0)
        d['numberOfItems'] = len(items)
        d['itemListElement'] = items
        return ('<script type="application/ld+json">'
                + json.dumps(d, ensure_ascii=False) + '</script>')

    html, n = re.subn(r'<script type="application/ld\+json">(.*?)</script>',
                      repl, html, flags=re.S)
    path.write_text(html, encoding='utf-8')
    return len(items)


def main():
    total = 0
    for pages, cat in ((CASINO_PAGES, 'casino'), (CRYPTO_PAGES, 'crypto'), (SPORTS_PAGES, 'sports')):
        n = len(lineup(cat))
        print(f'{cat}: {n} operators -> {len(pages)} pages')
        for p in pages:
            total += rewrite(p, cat)
    print(f'\nrebuilt {total} toplist blocks')
    print(f'ItemList structured data: {rebuild_itemlist()} items')

    print('\nHELD BACK (needs your input):')
    for op in DATA:
        for cat in ('casino', 'sports', 'crypto'):
            if op[cat] and held(op, cat):
                print(f'  {op["name"]:20} [{cat}] {held(op, cat)}')
                break


if __name__ == '__main__':
    main()
