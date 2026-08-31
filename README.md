# queenstownmarinaapartments.co.nz

Static site migrated from `pokiesrealmoney.co.com`. Hand-written HTML/CSS, no build
step, no framework, no dependencies.

## Structure

    /                       homepage
    /<section>/index.html   one directory per URL slug (38 pages total)
    /css/                   smoked-home.css (primary), casino.css, style.css
    /assets/styles.css
    /images/                favicons + hero-nzd.svg
    sitemap.xml             38 URLs
    robots.txt              points at sitemap; blocks SEO crawlers
    CNAME                   queenstownmarinaapartments.co.nz
    .nojekyll               disables Jekyll processing on GitHub Pages

## Local preview

    python3 -m http.server 8000

Then open http://localhost:8000 — trailing-slash directory URLs resolve the same way
GitHub Pages resolves them.

## Deploy

Push to the repo's default branch with GitHub Pages configured to serve from it.
The `CNAME` file sets the custom domain; DNS must point at GitHub Pages:

    ALIAS/ANAME @    ->  meridianstack.github.io
    (or four A records for GitHub Pages' IPv4 addresses)
    CNAME     www    ->  meridianstack.github.io

Enable "Enforce HTTPS" in repo Settings > Pages once the certificate provisions.

## Migration notes

All 618 references to the old domain were rewritten: canonicals, hreflang, OG tags,
JSON-LD `@id` graph nodes, sitemap, and robots. See MIGRATION.md for the cutover
checklist and redirect setup.
