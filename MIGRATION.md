# Migration: pokiesrealmoney.co.com -> queenstownmarinaapartments.co.nz

## Status

Done:
- 38 HTML pages copied, directory structure and slugs unchanged
- All 618 old-domain references rewritten (canonical, hreflang, og:url,
  JSON-LD `@id` graph nodes, sitemap.xml, robots.txt)
- 43 JSON-LD blocks re-validated after rewrite — all parse
- Zero missing local asset references
- `.nojekyll` added; `CNAME` verified

Outstanding:
- Brand wordmark still reads "PokiesRealMoney" (365 strings) — awaiting new name
- No `404.html` — will be added with the rebrand so it matches the template
- Old-domain 301s not yet configured (see below)
- Local git remote points at the OLD repo — must be corrected before pushing

## The redirect problem

A domain migration only preserves ranking equity if the old URLs return **HTTP 301**
to their new counterparts. GitHub Pages cannot do this — it serves static files and
has no redirect layer, no `.htaccess`, no config. If the old domain is currently on
GitHub Pages, it cannot issue real 301s as-is.

Slugs are identical between the two sites, so every redirect is a flat host swap:

    https://pokiesrealmoney.co.com/<path>  ->  https://queenstownmarinaapartments.co.nz/<path>

Pick one of these to serve the old domain:

**Cloudflare (recommended, free).** Move the old domain's nameservers to Cloudflare,
then add a Redirect Rule:

    When:  hostname equals pokiesrealmoney.co.com
    Then:  Dynamic redirect, 301
    URL:   concat("https://queenstownmarinaapartments.co.nz", http.request.uri.path)
    Preserve query string: on

One rule covers all 38 URLs. Free plan allows this.

**Netlify (free).** Point the old domain at a Netlify site containing only a
`_redirects` file:

    https://pokiesrealmoney.co.com/*  https://queenstownmarinaapartments.co.nz/:splat  301!

**Meta refresh — last resort.** If the old domain must stay on GitHub Pages, each old
page gets `<meta http-equiv="refresh" content="0;url=...">` plus
`<link rel="canonical">` to its new URL. Google treats this as a *soft* redirect: it
does consolidate signals, but more slowly and less reliably than a 301. Only use this
if neither option above is possible.

## Cutover order

1. Finish the rebrand pass; review the site locally
2. Point the target repo remote at the correct GitHub repo; push; enable Pages
3. Confirm DNS resolves and HTTPS certificate provisions for the new domain
4. Verify all 38 URLs return 200 on the new domain (script below)
5. **Only then** put the 301s on the old domain — never redirect before the
   destination is confirmed live, or you strand every URL at once
6. Verify a sample of old URLs return 301 to the right target
7. In Search Console: add and verify the new domain as a property, then run
   **Change of Address** on the old property. This requires the 301s to be live
   and is what tells Google the move is intentional
8. Submit the new sitemap; leave the old property in place for ~6 months so you can
   watch the transfer in the Change of Address report
9. Update backlinks you control, and affiliate program account URLs

Do not remove the 301s. They should stay in place permanently, or at minimum a year.

## Verify all URLs after deploy

    while read -r u; do
      printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' "$u")" "$u"
    done < <(grep -o '<loc>[^<]*</loc>' sitemap.xml | sed 's/<[^>]*>//g')

Anything not `200` needs fixing before step 5.
