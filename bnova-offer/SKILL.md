---
name: bnova-offer
description: Use when the user invokes /bnova-offer, $bnova-offer, or asks to create a B NOVA Studio branded PDF working document, offer, access handover, proposal, brief, or client-facing document on the B NOVA letterhead.
---

# BNOVA Offer

Create polished B NOVA Studio PDF documents on the saved letterhead.

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

## Visual Contract

Match the B NOVA Studio letterhead:

- A4 portrait, white background, generous margins.
- Header: exact saved B NOVA logo on the left, small uppercase document label on the right.
- Typography: use Noto Sans or a close geometric sans for body/title, bold sans for emphasis, and mono/small uppercase only for labels.
- Accent: electric blue `#0037FF`; body text near black `#111318`; muted gray `#7D8490`.
- Layout: large first-page title, sparse sections, lots of air, blue dash list markers, and light-gray blocks for key notes/results.
- Do not use heavy blue outline boxes as the default. Prefer flat light-gray blocks and clean label/value rows.
- Use short en dash `–` only. Never use the long em dash character `U+2014`.
- Copy must be concrete and operational. Avoid generic AI-sounding text, filler, and vague promises.
- If the document is client-facing, include a final dark B NOVA feedback block like the example:
  - left: `Обсудим детали?` plus a short direct sentence
  - right: `B NOVA STUDIO` plus contacts
  - `+7 913 004-61-62 · WhatsApp · Telegram`
  - `@E_Berest`
  - `berestenkoea@gmail.com`
  - `bnova.site`

## Security Rule

Never put passwords, API tokens, SSH private keys, backup codes, or 2FA codes into the generated document.

For access-transfer documents, list where access lives and which login/email is used. Say that passwords and codes are transferred separately through a protected channel.

## Workflow

1. Clarify only missing business facts; do not ask for passwords.
2. Copy `scripts/create_bnova_offer_pdf.py` or adapt it in a temp/workspace output folder.
3. Use `assets/bnova-header-logo.png` for the header logo; do not redraw it from memory.
4. Generate the final PDF into a user-accessible output path, usually `output/pdf/<descriptive-name>.pdf`.
5. Render the PDF pages to PNG using `pdfplumber` or Poppler.
6. Visually inspect every rendered page:
   - no clipped text
   - no horizontal overflow
   - contact block fits
   - links and labels are readable
   - B NOVA header and final feedback block present
7. Rebuild until clean, then report the final PDF path.

## Implementation Notes

The bundled script is a known-good starting point from the LR NSK access handover document. It includes:

- embedded B NOVA header image
- Noto Sans / DejaVu-compatible PDF fonts
- manual word wrapping
- light-gray accent blocks
- blue dash list markers
- clickable links
- final dark B NOVA feedback block

When adapting it, keep helper functions for `header`, `soft_note`, `info_rows`, `dash_list`, `feedback_block`, and `draw_wrap`.

Run it with a Python environment that has `reportlab`; in Codex, prefer the bundled workspace Python when available:

```bash
PYTHONPATH="$CODEX_PYTHON_PACKAGES" "$CODEX_PYTHON" scripts/create_bnova_offer_pdf.py --output output/pdf/example.pdf
```

If those variables are not defined, call `codex_app.load_workspace_dependencies` and use the returned Python executable and package path.

## Acceptance Criteria

- PDF opens and renders cleanly.
- B NOVA logo/header matches the saved asset.
- Final dark B NOVA feedback block is present when client-facing.
- No password/token/secret values are present.
- No long em dash character `U+2014` is present.
- The content answers the user's requested document purpose.
