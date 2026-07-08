# Agent handoff

This is a public-clean skill repo for Russian website legal documents and consent checkboxes.

## What to do with it

1. Load `SKILL.md` when asked to draft or review legal docs for a Russian-facing website/payment flow.
2. Use `references/checkbox-consent-principles.md` before writing checkbox labels.
3. Use `templates/legal/*.md` as placeholders, not as final legal advice.
4. Run validation before publishing or re-exporting:

```bash
bash scripts/test.sh
```

## What not to do

- Do not insert real operator data into this public repo.
- Do not bundle advertising consent into the offer/privacy checkbox.
- Do not pre-tick optional consents.
- Do not claim lawyer approval unless a lawyer actually reviewed the adapted pack.
