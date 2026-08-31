#!/usr/bin/env python3
"""Regenerate the mobile (hamburger) nav on every page.

Covers all 37 pages. Idempotent - rewrites the <nav class="shell-mobile-nav">
block in place. Run from the repo root:  python3 tools/build_nav.py
"""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAV = [
    ("Casinos", [
        ("/online-casinos/",                  "Best Online Casinos"),
        ("/online-pokies/",                   "Online Pokies"),
        ("/highest-rtp-pokies/",              "Highest RTP Pokies"),
        ("/fast-payout-casinos/",             "Fast Payout Casinos"),
        ("/minimum-deposit-casinos/",         "Minimum Deposit Casinos"),
        ("/minimum-deposit-casinos/1-dollar/", "$1 Deposit Casinos"),
        ("/no-deposit-casinos/",              "No Deposit Casinos"),
        ("/casino-apps/",                     "Casino Apps"),
        ("/casino-reviews/",                  "Casino Reviews"),
    ]),
    ("Bonuses", [
        ("/casino-bonuses/",                  "Casino Bonuses"),
        ("/free-spins-no-deposit/",           "Free Spins No Deposit"),
        ("/no-wagering-free-spins/",          "No Wagering Free Spins"),
    ]),
    ("Crypto", [
        ("/crypto-casinos/",                  "Crypto Casinos"),
        ("/crypto-casinos/bitcoin/",          "Bitcoin Casinos"),
        ("/crypto-casinos/ethereum/",         "Ethereum Casinos"),
        ("/crypto-casinos/no-kyc/",           "No KYC Casinos"),
    ]),
    ("Alternatives", [
        ("/jackpot-city-alternatives/",       "Jackpot City Alternatives"),
        ("/zodiac-casino-alternatives/",      "Zodiac Alternatives"),
        ("/captain-cooks-alternatives/",      "Captain Cooks Alternatives"),
        ("/spin-casino-alternatives/",        "Spin Casino Alternatives"),
        ("/luxury-casino-alternatives/",      "Luxury Casino Alternatives"),
        ("/casino-rewards-casinos/",          "Casino Rewards Network"),
    ]),
    ("Sports", [
        ("/sports-betting/",                  "Sports Betting NZ"),
        ("/sports-betting/tab-review/",       "TAB NZ Review"),
    ]),
    ("Guides", [
        ("/guides/",                          "All Guides"),
        ("/guides/nz-online-casino-law/",     "NZ Online Casino Law"),
        ("/guides/nz-betting-law/",           "NZ Betting Law"),
        ("/pokies-winnings-tax-nz/",          "Gambling Winnings Tax"),
        ("/review-methodology/",              "How We Test"),
    ]),
    ("About", [
        ("/about/",                           "About Us"),
        ("/authors/",                         "Our Authors"),
        ("/contact/",                         "Contact"),
        ("/responsible-gambling/",            "Responsible Gambling"),
    ]),
    ("Legal", [
        ("/privacy/",                         "Privacy Policy"),
        ("/terms/",                           "Terms &amp; Conditions"),
        ("/cookies/",                         "Cookie Policy"),
    ]),
]


def build(current):
    """Render the nav, marking the current page with aria-current."""
    out = ['<nav class="shell-mobile-nav" id="shellMobileNav" aria-label="Mobile"><ul>']
    out.append('<li><a href="/"%s>Home</a></li>' %
               (' aria-current="page"' if current == '/' else ''))
    for group, items in NAV:
        open_attr = ' open' if any(u == current for u, _ in items) else ''
        out.append(f'<li><details{open_attr}><summary>{group}</summary><ul>')
        for url, label in items:
            cur = ' aria-current="page"' if url == current else ''
            out.append(f'<li><a href="{url}"{cur}>{label}</a></li>')
        out.append('</ul></details></li>')
    out.append('</ul></nav>')
    return ''.join(out)


def main():
    pages = sorted(ROOT.glob('**/index.html'))
    urls = {u for _, items in NAV for u, _ in items} | {'/'}
    changed = 0
    for p in pages:
        rel = '/' + str(p.relative_to(ROOT)).replace('index.html', '')
        html = p.read_text(encoding='utf-8')
        new, n = re.subn(r'<nav class="shell-mobile-nav".*?</nav>',
                         lambda m: build(rel), html, flags=re.S)
        if n:
            p.write_text(new, encoding='utf-8')
            changed += 1
        else:
            print(f'  no mobile nav found in {rel}')
    total = 1 + sum(len(i) for _, i in NAV)
    print(f'{changed} pages updated; nav lists {total} links')
    missing = {'/' + str(p.relative_to(ROOT)).replace('index.html', '')
               for p in pages} - urls
    print('pages NOT in nav:', missing or 'none')


if __name__ == '__main__':
    main()
