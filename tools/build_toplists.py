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
SPORTS_PAGES = ['sports-betting', 'sports-betting/tab-review']

SPORTS_HEADING = 'Top Sports Betting Sites for NZ Players'
SPORTS_INTRO = ('<strong>We may earn a commission</strong> from the operators below; '
                'offer specifics are not yet confirmed, so verify current terms on each '
                'site. See our <a href="/review-methodology/">review methodology</a>.')

DEFAULT_OFFER = "Visit site for current offer"


def held(op, cat):
    h = op.get('hold') or {}
    return h.get('all') or h.get(cat)


def link_for(op, cat):
    """Preferred link for the category, falling back to the other.

    Most operators in this lineup use one URL for both casino and betting,
    so a missing column is filled from its counterpart rather than dropping
    the operator. See the per-operator 'note' fields in operators.json.
    """
    if cat == 'sports':
        return op['bettingLink'] or op['casinoLink']
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
    # brand mark: real logo where we have one, styled wordmark otherwise
    if op.get('logo'):
        mark = (f'<img src="/logos/{op["logo"]}" alt="{name} logo" loading="lazy" '
                f'decoding="async">')
    else:
        mark = (f'<span style="font-weight:800;color:#16233a;font-size:.8rem;'
                f'text-align:center;line-height:1.1">{name}</span>')

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
        f'{mark}</div>{stars}</div>'
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

    if not spans and cat == 'sports':
        # these pages have no toplist container; insert one after the answer box
        m = re.search(r'<div class="answer-box">', html)
        if m:
            sp = block_span(html, m.start())
            if sp:
                section = (f'\n<h2>{SPORTS_HEADING}</h2>\n<p>{SPORTS_INTRO}</p>\n'
                           f'<div class="toplist" id="toplist">{cards}</div>\n')
                html = html[:sp[1]] + section + html[sp[1]:]
                count = 1

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



PICK_LABEL = {'casino': 'Top Rated for NZ',
              'crypto': 'Top Crypto Pick for NZ',
              'sports': 'Top Sports Pick for NZ'}


def hero_card(op, url, cat):
    """The 'Editor's #1 Pick' hero card for a page's top operator."""
    name = op['name'].replace('&', '&amp;')
    href = url.replace('&', '&amp;')
    if op.get('logo'):
        # the mark tile is dark navy by default; our logos are dark artwork,
        # so the tile is overridden to white here or they would not read
        # tile is 48x48 by default, but most of these marks are wide wordmarks
        # (Spinjo is 3.2:1) which object-fit would shrink to a sliver, so the
        # tile is widened and the dark navy swapped for white
        mark = (f'<span class="hero-featured-mark" style="background:#fff;padding:6px;'
                f'width:96px;height:52px;border-radius:10px;flex-shrink:0">'
                f'<img src="/logos/{op["logo"]}" alt="{name} logo" loading="lazy" '
                f'style="width:100%;height:100%;object-fit:contain"></span>')
    else:
        mark = '<span class="hero-featured-mark">&#9733;</span>'
    return (
        '<div class="hero-featured">'
        '<div class="hero-featured-band">Editor\'s #1 Pick</div>'
        '<div class="hero-featured-body">'
        f'<div class="hero-featured-head">{mark}<div>'
        f'<p class="hero-featured-name">{name}</p>'
        f'<p class="hero-featured-pick">{PICK_LABEL[cat]}</p>'
        '</div></div>'
        '<p class="hero-featured-detail">Offer terms are not yet confirmed &mdash; '
        'check the current offer on site.</p>'
        f'<a href="{href}" class="btn-primary" style="display:block;text-align:center" '
        f'rel="nofollow sponsored noopener" target="_blank">Play at {name} &rarr;</a>'
        '<p class="hero-featured-fine">18+ &middot; T&amp;Cs apply &middot; '
        'verify current offer</p>'
        '</div></div>')


def rebuild_hero(page, cat):
    """Swap the hero card for the page's #1 operator.

    Only applied to pages that carry a toplist - the legal and utility pages
    (privacy, terms, cookies, responsible-gambling, ...) keep their
    'Kiwi Player Essentials' card deliberately.
    """
    path = ROOT / (page if page.endswith('.html') else f'{page}/index.html')
    if not path.exists():
        return 0
    html = path.read_text(encoding='utf-8')
    if '<div class="toplist"' not in html:
        return 0
    ops = lineup(cat)
    if not ops:
        return 0
    op, url = ops[0]
    m = re.search(r'<div class="hero-featured">', html)
    if not m:
        return 0
    sp = block_span(html, m.start())
    if not sp:
        return 0
    html = html[:sp[0]] + hero_card(op, url, cat) + html[sp[1]:]
    path.write_text(html, encoding='utf-8')
    return 1



RANK_BADGE = ["Editor's #1 Pick", '#2 Pick', '#3 Pick', '#4 Pick', '#5 Pick']


def review_card(op, url, rank):
    """Operator review card.

    Deliberately carries no welcome-offer, licence, min-deposit, games or
    pros/cons detail: none of that has been supplied for this lineup, and
    those are checkable factual claims a reader would act on financially.
    Restore review-highlights / review-pros-cons here once real data exists.
    """
    name = op['name'].replace('&', '&amp;')
    href = url.replace('&', '&amp;')
    if op.get('logo'):
        # header is a dark gradient; these logos are dark artwork, so the
        # mark sits on its own white tile
        logo = (f'<span style="display:inline-flex;align-items:center;'
                f'justify-content:center;background:#fff;border-radius:8px;'
                f'width:76px;height:44px;padding:5px;flex-shrink:0">'
                f'<img src="/logos/{op["logo"]}" alt="{name} logo" loading="lazy" '
                f'style="width:100%;height:100%;object-fit:contain"></span>')
    else:
        logo = ''
    badge = RANK_BADGE[rank - 1] if rank <= len(RANK_BADGE) else f'#{rank} Pick'
    return (
        '<div class="review-card">'
        '<div class="review-header"><div class="review-header-left">'
        f'{logo}<h3>{name} Review</h3>'
        f'<span class="review-badge">{badge}</span>'
        '</div>'
        f'<a href="{href}" class="btn-claim" rel="nofollow sponsored noopener" '
        f'target="_blank">Visit {name}</a>'
        '</div>'
        '<div class="review-body">'
        f'<p>{name} is part of our current New Zealand lineup. Our full '
        'assessment &mdash; welcome offer, licensing, banking and game range '
        '&mdash; is not published yet, so we make no claims about its terms '
        "here. Check the operator's site for current details before you "
        'deposit.</p>'
        '</div></div>')


def rebuild_reviews(page, cat):
    """Replace operator review cards with the lineup's top operators.

    Author bios on /authors/ reuse .review-card but have no .review-header,
    so they are skipped.
    """
    path = ROOT / (page if page.endswith('.html') else f'{page}/index.html')
    if not path.exists():
        return 0
    html = path.read_text(encoding='utf-8')

    spans = []
    for m in re.finditer(r'<div class="review-card">', html):
        sp = block_span(html, m.start())
        if sp and '<div class="review-header">' in html[sp[0]:sp[1]]:
            spans.append(sp)
    if not spans:
        return 0

    ops = lineup(cat)[:len(spans)]
    if len(ops) < len(spans):
        return 0
    cards = [review_card(op, u, i) for i, (op, u) in enumerate(ops, 1)]
    for (s, e), card in zip(reversed(spans), reversed(cards)):
        html = html[:s] + card + html[e:]
    path.write_text(html, encoding='utf-8')
    return len(spans)


def main():
    total = 0
    for pages, cat in ((CASINO_PAGES, 'casino'), (CRYPTO_PAGES, 'crypto'), (SPORTS_PAGES, 'sports')):
        n = len(lineup(cat))
        print(f'{cat}: {n} operators -> {len(pages)} pages')
        for p in pages:
            total += rewrite(p, cat)
    print(f'\nrebuilt {total} toplist blocks')
    print(f'ItemList structured data: {rebuild_itemlist()} items')
    heroes = 0
    for pages, cat in ((CASINO_PAGES, 'casino'), (CRYPTO_PAGES, 'crypto'),
                       (SPORTS_PAGES, 'sports')):
        for pg in pages:
            heroes += rebuild_hero(pg, cat)
    print(f'hero #1-pick cards: {heroes}')
    revs = 0
    for pages, cat in ((CASINO_PAGES, 'casino'), (CRYPTO_PAGES, 'crypto'),
                       (SPORTS_PAGES, 'sports')):
        for pg in pages:
            revs += rebuild_reviews(pg, cat)
    print(f'review cards rebuilt: {revs}')

    print('\nHELD BACK (needs your input):')
    for op in DATA:
        for cat in ('casino', 'sports', 'crypto'):
            if op[cat] and held(op, cat):
                print(f'  {op["name"]:20} [{cat}] {held(op, cat)}')
                break


if __name__ == '__main__':
    main()
