---
name: bnova-contract
description: Use when preparing or revising B NOVA development contracts, website/CRM/SEO appendices, estimates, acts, acceptance criteria, requisites blocks, and client intake questions.
---

# B NOVA Contract

Prepare concrete, editable B NOVA contract documents for website development, catalog sites, CRM/lead systems, SEO-ready site builds, support work, estimates and acts. Keep the document practical: what is being made, what is excluded, how acceptance works, how payment works, and what happens when external technical access changes.

## Required Reference

Before drafting or revising a contract, read:

- `references/requisites.md` - B NOVA requisites, standard tax wording, signature block and reusable legal clauses.

## Contract Defaults

- Executor brand in contracts: `B NOVA`.
- Do not add extra brand suffixes unless the user explicitly asks for them.
- Standard executor tax wording: `НДС не облагается в связи с применением Исполнителем специального налогового режима.`
- Use the executor requisites from `references/requisites.md` unless the user provides newer details.
- If the customer provides their requisites, insert them fully in the two-column requisites/signature block.
- If customer requisites are incomplete, leave clean fill-in fields and list what is missing.
- For Russian contracts, use `Договор`, `Приложение`, `Акт сдачи-приемки работ`, `Исполнитель`, `Заказчик`, `Стороны`.

## Document Structure

For a website or CRM development contract, include:

1. Cover or opening block: number, date, city, project, price, approximate term.
2. Parties and subject.
3. Result of work.
4. Stages and timing.
5. Price and payment schedule.
6. Materials, accesses and personal-data handling.
7. Acceptance procedure.
8. Limitation of guarantees.
9. Technological restrictions clause.
10. Final terms.
11. Appendix 1: detailed scope, acceptance criteria, exclusions and launch questions.
12. Appendix 2: act template.
13. Two-column requisites and signature block.

## Scope Rules

- State what the client pays for in concrete deliverables and actions.
- Do not promise search positions, traffic, leads, revenue, approvals by third parties, uninterrupted third-party services or supplier actions.
- Separate base CRM connection from advanced CRM lead-system work.
- For base amoCRM connection, describe a simple website-origin lead: the form creates a request with a note that the appeal came from the site.
- For advanced amoCRM work, describe specific transmitted fields: form, page, source, UTM tags, category, brand, scenario, date/time, status and responsible person when technically possible.
- Exclude ad budgets, paid placements, paid services, licenses, hosting, domains, stock media, production costs, legal review, 1C/warehouse/supplier integrations and work beyond the agreed scope unless explicitly included.
- For personal data, include checkboxes and policy/consent drafting as project text, but do not present it as a legal opinion unless legal review is included.
- Telegram/WhatsApp should not be used to transmit personal data from forms. Only anonymized notifications are acceptable unless the user explicitly commissions a compliant alternative.

## Technological Restrictions Clause

Use this clause, adapting grammar to the document:

```text
Если программное обеспечение, облачные сервисы, API, коммуникационные каналы, хостинговая, платежная, аналитическая или иная технологическая инфраструктура, используемая Исполнителем для выполнения работ, будет ограничена, заблокирована, отозвана, запрещена к использованию, перестанет поддерживаться либо существенно изменит условия доступа, сроки выполнения работ подлежат соразмерному переносу на период, необходимый для подбора, настройки и внедрения альтернативного технического решения.

Если такие обстоятельства делают выполнение работ в первоначально согласованном объеме технически невозможным либо существенно меняют трудоемкость или стоимость проекта, Стороны согласуют изменение состава работ, сроков и стоимости дополнительным соглашением.

Если Стороны не согласуют альтернативное решение, любая из Сторон вправе инициировать расторжение договора. В этом случае расчет производится исходя из фактически выполненного объема работ на дату расторжения, понесенных Исполнителем расходов и стоимости результатов, переданных Заказчику.

Исполнитель уведомляет Заказчика о таких обстоятельствах в разумный срок после того, как Исполнителю стало известно об их влиянии на выполнение работ, и предлагает возможный вариант продолжения проекта.
```

Do not name specific platforms, AI tools, code hosts, clouds or SaaS vendors in this clause unless the user explicitly asks.

## B NOVA Layout

- Create an editable `.docx` when the user asks for a contract deliverable.
- Use A4 portrait.
- Use Arial 10.5 pt body text.
- Use `#2456D6` headings.
- Use a small B NOVA header.
- Use a muted footer with page number.
- Use pale-blue price/summary bands.
- Use light-gray table rules.
- Use a two-column requisites/signature block.
- Keep tables readable with explicit widths, cell padding and no clipped text.

## Acceptance Check

Before delivery:

- Verify the contract number, date, parties, price, payment schedule and term.
- Verify `НДС не облагается...` appears where tax wording is needed.
- Verify B NOVA requisites are complete.
- Verify the appendix matches the selected offer or ТЗ.
- Verify exclusions do not contradict included work.
- Verify no specific hidden tool/platform dependency is disclosed unless requested.
- Verify no guarantees of positions, traffic, leads or revenue appear.
- Verify no long em dash `U+2014` appears.
- Render every DOCX page and visually check for clipping, orphaned headings, split payment tables and broken signature blocks.
