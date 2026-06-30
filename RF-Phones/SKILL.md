---
name: rf-phones
description: Build and maintain Russian smartphone e-commerce storefronts with popular RF-market models, verified real product images, consumer-ready Russian copy, required commerce/legal pages, local preview, and browser verification.
---

# RF Phones

Use this skill when creating or improving a Russian smartphone store, landing catalog, product gallery, or small e-commerce prototype for mobile phones in Russia.

## Workflow

1. Confirm the storefront goal and scope from the request.
2. Use current sources for model popularity and product facts when the user asks for real models, current demand, prices, specs, or market fit.
3. Prefer official brand pages for product images and specs:
   - Xiaomi / Redmi: `mi.com`
   - Samsung: `samsung.com`
   - realme: `realme.com`
   - Use reputable retailers only when official product media is unavailable.
4. Save product images locally in the project, usually under `assets/products/`.
5. Keep a source manifest such as `assets/products/sources.json` with the source URL for each image group.
6. Use buyer-facing Russian copy only. Avoid internal words such as "макет", "демонстрационный", "прототип", "товарная сетка", "основные страницы", or implementation notes.
7. Include the commerce pages buyers expect:
   - Главная
   - Каталог
   - Карточка товара
   - Корзина / оформление заказа
   - Помощь / доставка и оплата
   - Контакты
   - Политика конфиденциальности
   - Пользовательское соглашение / оферта
   - Возврат и гарантия
8. Start a local server when needed and verify in the browser.

## Product Imagery Rules

- Do not use placeholder phone drawings when the user asked for real products.
- Product cards, hero sections, galleries, and cart rows should all use real device images.
- For SKU variants that differ only by memory or RAM, reuse the same model image group.
- Validate that every referenced image loads locally:
  - no broken `<img>` elements
  - nonzero `naturalWidth`
  - images are committed or otherwise included with the project

## Copy Rules

Write as if the site is live for customers. Good examples:
- "Популярные смартфоны для работы, учебы и связи"
- "Цена фиксируется при подтверждении заказа"
- "Доставка по России, гарантия 12 месяцев"

Avoid:
- "Макет магазина"
- "Демонстрационный текст"
- "Все цены демонстрационные"
- "Блоки доверия"
- "Основной покупательский сценарий"

## Verification Checklist

Before reporting completion:

- Run syntax/build checks available for the project.
- Search the code for internal/prototype wording.
- Verify main routes in a browser.
- Verify product images are local and not broken.
- Keep the local preview open when the user asked to see it.
