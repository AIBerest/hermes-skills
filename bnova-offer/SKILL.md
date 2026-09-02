---
name: bnova-offer
description: Use when the user invokes /bnova-offer, $bnova-offer, or asks to create a B NOVA branded PDF working document, offer, access handover, proposal, brief, or client-facing document on the B NOVA letterhead.
---

# BNOVA Offer

Create polished B NOVA PDF documents on the saved letterhead. Default client-facing proposals to the approved «Пансионат Вера» B NOVA editorial style unless the user supplies a different reference.

## Trigger

Use this skill for `/bnova-offer` and for requests such as:

- commercial proposal / КП on B NOVA letterhead
- access handover document
- client working document
- branded PDF with B NOVA contacts
- "сделай на таком же бланке B NOVA"

## Required Assets

- Header logo: `assets/bnova-header-logo.png`
- Example PDF: `examples/akt-peredachi-dostupov-lr-nsk.pdf`
- Generator template: `scripts/create_bnova_offer_pdf.py`

## Default Proposal Style – Pension Vera Reference

Use this as the default visual system for B NOVA proposals:

- Build the document as print HTML/CSS and render it with a browser (Playwright/Chromium). Do not use ReportLab for a client-facing proposal unless browser rendering is unavailable.
- Use **Carlito Regular** for body and **Carlito Bold** for headings, prices and emphasis. Never use a monospaced font or artificial letter spacing in body copy.
- Use A4 portrait, a 14 mm horizontal grid, wide white space, a compact logo at the upper left, small muted metadata at the upper right, and a light footer with `B NOVA` plus page number.
- Use large, dense, left-aligned headings with one bold phrase; body copy must be compact, natural and comfortably readable.
- Use electric blue `#2853F4`, near-black `#171922`, muted gray `#8D95A4`, pale blue `#EEF1FF`, and thin light-gray rules.
- Use round blue bullet markers, pale-blue `РЕЗУЛЬТАТ` callouts with a solid blue left rule, thin blue outlined callouts, and two-column option/price cards. Use dashed pale-blue notes sparingly.
- Finish with a white contact section separated by a thin rule: `Обсудим детали?`, a muted one-line invitation, then B NOVA contact links. Do not use a dark contact block in this default style.
- Match the hierarchy and spacing of the supplied Pension Vera reference before adding decorative elements. Keep pages quiet; no gradients, shadows, framed-everything layout, or generic PDF styling.

## Visual Contract

When the user explicitly asks for a different brand/reference, match that reference instead. Otherwise, match the default B NOVA Pension Vera style:

- A4 portrait, white background, generous margins.
- Header: exact saved B NOVA logo on the left, small uppercase document label on the right.
- Typography: use Carlito Regular/Bold; uppercase labels may have modest tracking, but body copy must never be tracked.
- Accent: electric blue `#2853F4`; body text near black `#171922`; muted gray `#8D95A4`.
- Layout: large first-page title, sparse sections, lots of air, blue round markers, pale-blue result blocks, thin blue frames, and option/price cards.
- Use the design patterns intentionally:
  - Thin blue frame: one primary working/action block, usually on page 1 for the main link, demo, or key artifact.
  - Light-gray block: result, warning, note, or short explanation that should feel separate from body text.
  - Blue bold text: important links, numbers, option labels, and 1-3 key words inside a heading.
  - Line-table rows: access maps, prices, account lists, or comparisons.
  - Blue left rule: compact final note or "simple math" style takeaway.
  - White contact section: final B NOVA feedback/contact area separated by a thin rule.
- Do not make every important item a blue frame. The document should alternate quiet text, lists, gray blocks, tables, and one framed working block.
- Use short en dash `–` only. Never use the long em dash character `U+2014`.
- Copy must be concrete and operational. Avoid generic AI-sounding text, filler, vague promises, and long abstract introductions.
- If the document is client-facing, include the final white B NOVA contact section: `Обсудим детали?`, a short direct sentence, `B NOVA`, `bnova.site`, `8-983-009-35-32`, `info@bnova.site`, and `Telegram @E_Berest`.

## Formal SEO Contract Variant

For an SEO-договор, смету, ТЗ или ежемесячный акт, use a formal B NOVA document variant rather than proposal cards:

- Build an editable `.docx`, then render and inspect every page before delivery.
- Use A4 portrait, Arial 10.5 pt body, blue `#2456D6` section headings, restrained pale-blue price bands, and thin light-gray tables. Add a small `B NOVA` header and muted page footer.
- Keep the cover/title area clean: contract number and date, no decorative hero block. Put requisites in a two-column signature table.
- Put the detailed schedule in an annex: month heading, a price band, then compact numbered work items. Add a monthly act and a practical source-data questionnaire when useful.
- Show the first-month price and the recurring monthly price. Do not show a cumulative project total unless the user explicitly requests it.
- Use short en dash `–` only. Never use the long em dash character `U+2014` in text, headings, metadata, tables, or document properties.

## Security Rule

Never put passwords, API tokens, SSH private keys, backup codes, or 2FA codes into the generated document.

For access-transfer documents, list where access lives and which login/email is used. Say that passwords and codes are transferred separately through a protected channel.

## Workflow

1. Clarify only missing business facts; do not ask for passwords.
2. Build a print HTML/CSS document using the Default Proposal Style. Use `assets/bnova-header-logo.png` for the header logo; do not redraw it from memory.
3. Render the HTML with Chromium/Playwright into a user-accessible PDF, usually `output/pdf/<descriptive-name>.pdf`. Use ReportLab only as a documented fallback.
4. Render the PDF pages to PNG using `pdfplumber` or Poppler.
5. Visually inspect every rendered page:
   - no clipped text
   - no horizontal overflow
   - headings and body use Carlito with no body letter spacing
   - contact section fits and does not overlap the next-step block
   - option cards, price rows and labels are readable
   - B NOVA header and footer are present
6. Rebuild until clean, then report the final PDF path.

## Implementation Notes

The bundled ReportLab script is a legacy fallback for access handovers. For the default client-facing proposal style, prefer browser HTML/CSS. It includes:

- embedded B NOVA header image
- Noto Sans / DejaVu-compatible PDF fonts for fallback documents only
- manual word wrapping
- thin blue framed working block
- light-gray result/note blocks
- line-table rows
- blue left-rule note
- blue dash list markers
- clickable links
- final dark B NOVA feedback block for legacy documents only

When adapting it, keep helper functions for `header`, `framed_callout`, `soft_note`, `line_rows`, `info_rows`, `blue_side_note`, `dash_list`, `feedback_block`, and `draw_wrap`.

Run it only when a Python/ReportLab fallback is required; in Codex, prefer the bundled workspace Python when available:

```bash
PYTHONPATH="$CODEX_PYTHON_PACKAGES" "$CODEX_PYTHON" scripts/create_bnova_offer_pdf.py --output output/pdf/example.pdf
```

If those variables are not defined, call `codex_app.load_workspace_dependencies` and use the returned Python executable and package path.

## Acceptance Criteria

- PDF opens and renders cleanly.
- B NOVA logo/header matches the saved asset.
- Client-facing proposals use the white Pension Vera-style contact section unless the user requests a different reference.
- No password/token/secret values are present.
- No long em dash character `U+2014` is present.
- The content answers the user's requested document purpose.
