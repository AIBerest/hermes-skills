---
name: chip-legal-web-rf
description: Public-clean Russian website legal-pack skill: draft and review generic public offers, privacy/personal-data policies, consent checkboxes for registration/payment, cookies, advertising consent, subscriptions/autopay, and product addenda without private data.
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [legal, russia, website, offer, privacy, personal-data, checkout, consent]
---

# chip-legal-web-rf

Public-clean skill for drafting and reviewing a standard Russian-language legal pack for a website, web app, Telegram/WebApp flow, or paid digital product.

This is a practical operator checklist and template pack, not legal advice. Before production use, a qualified lawyer should adapt the templates to the exact business model, tax status, payment provider, product mechanics, and current law.

## Trigger

Use this skill when a user asks to:

- prepare a site legal pack for the Russian Federation;
- draft or review a public offer, privacy policy, personal-data consent, cookies consent, advertising consent, rules, paid subscription/autopay consent, or service addendum;
- decide which checkboxes must appear during registration, checkout, payment, subscription, or newsletter signup;
- check whether consent is bundled, pre-ticked, missing a link, or mismatched with the documents;
- sanitize a private legal pack into reusable generic templates.

## Output Contract

Return:

1. **verdict** — `ok`, `ok_after_fixes`, or `blocked`;
2. **document inventory** — what exists, what is missing, what is stale;
3. **checkbox matrix** — required/optional, default state, screen, linked document, evidence to store;
4. **hard blockers** — placeholders, wrong entity fields, missing active consent, broken links, bundled ads consent, unavailable refund/cancel mechanics;
5. **draft text or patch notes** — exact replacement wording when possible;
6. **residual legal risk** — what needs lawyer/accountant/product-owner confirmation;
7. **verification evidence** — commands, scans, route/link checks, or reviewed files.

## Workflow

1. **Inventory the product flow**
   - registration/login;
   - checkout/payment;
   - subscription/autopay/trial;
   - newsletter/ads messages;
   - cookies/analytics/WebApp tracking;
   - user-generated content, community, recordings, experts, or downloadable materials.

2. **Inventory documents**
   - public offer / terms;
   - privacy and personal-data policy;
   - personal-data processing consent;
   - advertising/newsletter consent;
   - cookie/analytics consent or notice;
   - service/community rules;
   - product-specific addendum;
   - paid subscription/autopay consent when recurring charges exist;
   - expert/content release when recordings or guest materials are used.

3. **Build the checkbox matrix**
   - required contractual documents can block continuation;
   - advertising consent must be separate, optional, active opt-in, and not pre-ticked;
   - cookie/analytics consent depends on actual tracking and banner mechanics;
   - autopay/recurring charge consent must be explicit and separate from the general offer;
   - store consent evidence: user id/contact, document version, timestamp, IP/user-agent when available, screen/source, consent text/version.

4. **Review blockers**
   - placeholders like `[OPERATOR]`, `[EMAIL]`, `[DOMAIN]` left in production docs;
   - product claims not matching the real service;
   - no refund/cancel route despite refund/cancel text;
   - advertising consent bundled into offer/privacy acceptance;
   - pre-ticked optional consent;
   - payment provider/card claims that do not match actual provider behavior;
   - missing route links or 404 legal documents.

5. **Return exact next steps**
   - If safe: provide copy-ready checkbox labels and document links.
   - If blocked: list the minimum fixes before publishing.
   - If legal interpretation is material: mark as `needs lawyer review` rather than pretending certainty.

## Quick Test Checklist

- [ ] `bash scripts/test.sh` passes.
- [ ] `python3 scripts/validate_public_skill.py .` reports zero private markers and required files exist.
- [ ] Registration and payment examples keep contractual consents separate from advertising consent.
- [ ] Optional marketing/cookie consents are not pre-ticked.
- [ ] Templates contain placeholders only, not real names, emails, domains, addresses, INNs, or project data.

## Done Criteria

- Documents and checkbox matrix cover the actual user flow.
- Every checkbox has `required`, `defaultChecked`, `document`, `href`, `version`, and `evidenceToStore` semantics.
- Legal text is generic or clearly placeholder-based.
- No private data or project-specific names leak into public output.
- Residual legal/accounting/product-owner review needs are explicit.
