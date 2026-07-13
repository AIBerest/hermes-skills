---
name: bnova
description: Use when the user invokes BNOVA, $bnova, or asks to add the B NOVA Studio website development credit to a site's footer. Adds the text "Разработка сайта - B NOVA Studio" linking to https://bnova.site/ while preserving the existing footer design and project conventions.
---

# BNOVA

## Goal

Add a website development credit to the site's footer:

```html
Разработка сайта - <a href="https://bnova.site/" target="_blank" rel="noopener noreferrer">B NOVA Studio</a>
```

Use the exact public text `Разработка сайта - B NOVA Studio`; make `B NOVA Studio` the clickable link to `https://bnova.site/`.

## Workflow

1. Inspect the project to find the primary footer component or footer markup.
2. Add the BNOVA credit once, near existing legal/copyright/footer metadata.
3. Match the site's existing footer typography, spacing, color, and responsive behavior.
4. Use `target="_blank"` and `rel="noopener noreferrer"` for the BNOVA external link.
5. If the project has verification tests or static checks, add/update a focused check so the credit text and link are not accidentally removed.
6. Run the project's relevant verification command before reporting completion.

## Placement Guidance

- Prefer the main site footer over per-page content sections.
- If legal links exist, place the credit after or near them.
- If there is already an agency/developer credit, update it instead of adding a duplicate.
- Do not alter unrelated legal text, tracking scripts, forms, or navigation.

## Acceptance Criteria

- The footer visibly contains `Разработка сайта - B NOVA Studio`.
- The `B NOVA Studio` text links to `https://bnova.site/`.
- The link opens in a new tab with `rel="noopener noreferrer"`.
- The implementation follows the existing code style and passes available checks.
