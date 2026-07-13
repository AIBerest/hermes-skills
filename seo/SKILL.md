---
name: seo
description: Use for SEO audits and implementation on commercial websites and landing pages, especially Russian/Yandex local SEO. Covers indexability, robots, sitemap, metadata, headings, image alt/title, Schema.org, text over-optimization, and verification before deploy.
---

# SEO

Use this skill when a user asks to analyze SEO remarks, improve search visibility, fix indexation issues, or prepare a landing page for Yandex/Google crawling.

## Workflow

1. **Extract the remarks**
   - If the user provides a DOCX/PDF/screenshot, extract the text first.
   - Separate actionable site changes from external actions such as submitting URLs in Yandex Webmaster.

2. **Inspect the current page**
   - Check `<title>`, description, canonical, `<meta name="robots">`, language, Open Graph/Twitter tags.
   - Check `robots.txt`, `sitemap.xml`, HTTP availability, and whether the page has accidental `noindex`, `nofollow`, or `Disallow: /`.
   - List H1/H2/H3 headings and detect duplicates.
   - List all `<img>` tags and verify non-empty `alt` and useful `title` where the project requires it.
   - Check Schema.org markup for the business type, address, phone, opening hours, URL, services, and FAQ where relevant.
   - Review visible copy for keyword stuffing. Keep core commercial terms, but replace repeated phrases with natural synonyms.

3. **Make narrow fixes**
   - Add `meta robots` as `index, follow` unless there is a clear reason not to index.
   - Keep canonical stable and absolute.
   - Make headings unique without weakening search intent.
   - Add descriptive `alt` and `title` to informative images; decorative images may use empty `alt` only if the audit requirement allows it.
   - Update `robots.txt` and `sitemap.xml` if crawling or URL discovery is incomplete.
   - Improve Schema.org with accurate local business data. Do not invent ratings, reviews, coordinates, legal names, or opening hours.
   - Reduce over-repetition by using natural alternatives such as “профильный сервис”, “автосервис”, “британские автомобили”, “проверка”, “техобслуживание”, and model-specific wording.

4. **Add regression checks**
   - If the repo has a verification script, add checks for the SEO issues fixed.
   - At minimum verify: robots meta, crawlable robots.txt, no duplicate H2/H3, image alt/title coverage, sitemap reference, Schema.org presence.

5. **Verify**
   - Run project tests and the site verification script.
   - For deployed sites, fetch the live HTML and confirm critical SEO tags are present.

## Yandex-specific notes

- If a page is not indexed, code changes alone may not be enough. Tell the user to add the site in Yandex Webmaster, verify ownership, run “Проверка URL”, and submit the URL for indexing.
- If hosted outside Russia, recommend setting the region in Yandex Webmaster before suggesting infrastructure migration.
- Do not claim Yandex has indexed the page unless verified from Yandex Webmaster or an up-to-date external check.

## Reporting

Report:
- What was fixed in code.
- What was verified locally/live.
- What remains an external webmaster action.
- Whether any recommendation was intentionally not implemented and why.
