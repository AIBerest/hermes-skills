# chip-legal-web-rf

Public-clean Hermes skill and template pack for Russian website legal documents and consent checkboxes.

It helps an agent or operator prepare a generic legal surface for a paid website/web app:

- public offer / terms;
- privacy and personal-data policy;
- personal-data processing consent;
- advertising/newsletter consent;
- cookies/analytics consent;
- service/community rules;
- product-specific addendum;
- paid subscription/autopay consent;
- expert/content release;
- registration and payment checkbox matrix.

## Important boundary

This repository is not legal advice. It is a reusable checklist and template pack. Adapt it with a lawyer before production use.

The repo is intentionally public-clean: no customer names, no real operator requisites, no private domains, no emails, no secrets, no copied private contracts.

## Quick start

```bash
python3 scripts/validate_public_skill.py .
bash scripts/test.sh
```

Read first:

1. `SKILL.md`
2. `references/checkbox-consent-principles.md`
3. `references/document-pack-map.md`
4. `templates/legal/`
5. `templates/ui/consent-matrix.json`

## Install as a Hermes skill

Copy the repository folder into a Hermes skills directory, then reload/list skills in your agent environment.

```bash
mkdir -p ~/.hermes/skills
cp -R chip-legal-web-rf ~/.hermes/skills/chip-legal-web-rf
```
