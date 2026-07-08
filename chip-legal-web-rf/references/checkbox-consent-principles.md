# Checkbox and consent principles

## Core rules

1. A user must be able to open each linked document before accepting it.
2. Required contractual/legal checkboxes may block registration/payment.
3. Marketing consent must be separate, optional, active opt-in, and not pre-ticked.
4. Autopay/recurring-payment consent must be separate from the general offer acceptance.
5. Cookie/analytics consent should match the actual banner/tracking mechanics.
6. The UI text must match the document title and URL exactly enough to be auditable.
7. Store consent evidence with document version and timestamp.

## Registration matrix

| Consent | Required | Default | Why |
|---|---:|---:|---|
| Privacy/personal-data policy acknowledgement | yes | false | User must know data-processing terms. |
| Personal-data processing consent | yes when consent is legal basis | false | Separate evidence of consent. |
| Service/community rules | yes when access depends on rules | false | Contractual conduct/access condition. |
| Advertising/newsletter consent | no | false | Must be separate voluntary opt-in. |
| Cookies/analytics | depends on banner mechanics | false | Must match actual tracking. |

## Payment matrix

| Consent | Required | Default | Why |
|---|---:|---:|---|
| Public offer / terms | yes | false | Contract acceptance. |
| Privacy/personal-data policy | yes | false | Payment/access processing involves personal data. |
| Personal-data consent | yes when consent is legal basis | false | Payment/access data processing. |
| Product-specific addendum | yes for special product terms | false | Special terms override or supplement general offer. |
| Autopay/recurring consent | yes for recurring charges | false | User must actively accept recurring charges. |
| Advertising/newsletter consent | no | false | Optional marketing, never bundled. |

## Evidence to store

- user id or contact;
- consent type;
- document title;
- URL;
- version/date;
- exact label text or text hash;
- timestamp;
- source screen/action;
- IP/user-agent when appropriate and available;
- payment/order id when consent is tied to checkout.
