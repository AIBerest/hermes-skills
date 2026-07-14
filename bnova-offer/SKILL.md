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
- Typography: clean sans for body, bold sans for large title, mono/small uppercase for labels.
- Accent: electric blue `#0037FF`; body text near black `#111318`; muted gray `#7D8490`.
- Layout: large first-page title, blue outlined information boxes, sparse sections, lots of air.
- Footer on every page: `B NOVA STUDIO · РАБОЧИЙ ДОКУМЕНТ · БЕЗ ПАРОЛЕЙ` and page number.
- If the document is client-facing, include a final B NOVA contact block with:
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
   - B NOVA header/footer present
7. Rebuild until clean, then report the final PDF path.

## Implementation Notes

The bundled script is a known-good starting point from the LR NSK access handover document. It includes:

- embedded B NOVA header image
- DejaVu/Noto-compatible PDF fonts
- manual word wrapping
- blue outline boxes
- clickable links
- final B NOVA contact block

When adapting it, keep helper functions for `header`, `footer`, `box`, `note_box`, `contact_block`, and `draw_wrap`.

Run it with a Python environment that has `reportlab`; in Codex, prefer the bundled workspace Python when available:

```bash
PYTHONPATH="$CODEX_PYTHON_PACKAGES" "$CODEX_PYTHON" scripts/create_bnova_offer_pdf.py --output output/pdf/example.pdf
```

If those variables are not defined, call `codex_app.load_workspace_dependencies` and use the returned Python executable and package path.

## Acceptance Criteria

- PDF opens and renders cleanly.
- B NOVA logo/header matches the saved asset.
- Footer and B NOVA contact block are present when client-facing.
- No password/token/secret values are present.
- The content answers the user's requested document purpose.
