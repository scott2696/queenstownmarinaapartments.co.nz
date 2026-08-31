import re, pathlib
ROOT = pathlib.Path('.')
HOWWE = ' <a href="/review-methodology/">How we test &rarr;</a>'

INTROS = {
'index.html':
 "We funded an account at every site below, played it, and put a withdrawal through before "
 "ranking anything. What we score: how fast the money actually lands, whether NZD and Kiwi "
 "banking work properly, how deep the pokies range really goes, and whether the bonus terms "
 "still look fair once you read past the headline." + HOWWE,

'online-casinos/index.html':
 "These are the sites we keep going back to. Every one was funded with our own money, played "
 "properly and cashed out again &mdash; payout speed, NZD banking, pokies range, bonus honesty, "
 "licensing and support all scored the same way, so the order means something." + HOWWE,

'casino-apps/index.html':
 "We installed and played each of these on a real phone rather than judging the desktop site "
 "and assuming. What decided it: whether the cashier works properly on mobile, how the pokies "
 "handle a small screen, and whether getting back into your account is painless." + HOWWE,

'casino-bonuses/index.html':
 "We read every set of bonus terms end to end, then worked out what you could realistically "
 "walk away with. Headline size matters far less than the wagering multiplier, the game "
 "weighting and the cash-out cap &mdash; that is what sets this order." + HOWWE,

'crypto-casinos/index.html':
 "We deposited and withdrew in crypto at each of these and timed what came back. Spinjo cleared "
 "fastest of the group we checked. Coin support, provably fair games and how much verification "
 "you actually face decide the rest." + HOWWE,

'crypto-casinos/bitcoin/index.html':
 "We funded each of these in BTC and cashed out again, watching where network fees and "
 "confirmation waits really bite. Withdrawal speed, fairness and the value of the bonus set "
 "the order." + HOWWE,

'crypto-casinos/ethereum/index.html':
 "We ran ETH deposits and withdrawals through every site here, tracking gas costs and how long "
 "confirmations took at busy times. Payout speed, fees and fairness decide the ranking." + HOWWE,

'crypto-casinos/no-kyc/index.html':
 "We signed up at each of these to find out how far you actually get before documents are "
 "asked for &mdash; because 'no KYC' rarely means never. Sign-up friction, payout speed and "
 "licensing set the order." + HOWWE,

'fast-payout-casinos/index.html':
 "We timed real withdrawals, from hitting cash-out to money landing, with verification already "
 "done &mdash; that is the number that matters once you are actually playing. Method options "
 "and how consistently each site pays count for the rest." + HOWWE,

'free-spins-no-deposit/index.html':
 "We claimed every offer on this page and tried to withdraw what we won. Most no-deposit spins "
 "die on the wagering or a quiet cash-out cap, so the ranking reflects what genuinely reached "
 "an account." + HOWWE,

'no-deposit-casinos/index.html':
 "We claimed each of these and pushed it through to a withdrawal request rather than stopping "
 "at the sign-up. The wagering, the maximum cash-out and whether winnings pay as cash or as "
 "more bonus are what separate them." + HOWWE,

'no-wagering-free-spins/index.html':
 "We went looking for the catch in each of these. Genuinely cashable means 0&times; wagering "
 "and no quiet cap on what you keep &mdash; these are the offers that survived the check." + HOWWE,

'minimum-deposit-casinos/index.html':
 "We paid in the smallest amount each site allows and played from there. What ranks them is "
 "how little you can genuinely start with, whether the low-deposit offer is worth having at "
 "all, and whether they pay out afterwards." + HOWWE,

'minimum-deposit-casinos/1-dollar/index.html':
 "A single dollar buys less than it used to. We tested the low-deposit tier to see where a "
 "genuinely small stake still gets you a real shot, and where the minimum has quietly crept "
 "up &mdash; check each site's current minimum before you commit." + HOWWE,

'online-pokies/index.html':
 "We played the libraries ourselves rather than counting titles on a landing page. Depth, which "
 "studios are genuinely included, whether RTP is published honestly and how jackpots are "
 "reached decide the order." + HOWWE,

'sports-betting/index.html':
 "We put our own money through each of these books across rugby, league and racing. Market "
 "depth, how sharp the odds look once the margin is stripped out, and how quickly a winning "
 "bet actually pays are what set the order." + HOWWE,

'sports-betting/tab-review/index.html':
 "We bet across rugby, league and racing with each of these to see how they hold up next to "
 "the TAB in day-to-day use &mdash; odds, markets and how fast a win is paid." + HOWWE,
}

changed = 0
for f, new in INTROS.items():
    p = ROOT / f
    h = p.read_text(encoding='utf-8')
    m = re.search(r'<div class="toplist"', h)
    if not m:
        print('  no toplist:', f); continue
    pre = h[:m.start()]
    ps = list(re.finditer(r'<p>(.*?)</p>', pre, re.S))
    if not ps:
        print('  no intro <p>:', f); continue
    last = ps[-1]
    h = h[:last.start()] + f'<p class="toplist-intro">{new}</p>' + h[last.end():]
    p.write_text(h, encoding='utf-8')
    changed += 1
print('intros rewritten:', changed)
