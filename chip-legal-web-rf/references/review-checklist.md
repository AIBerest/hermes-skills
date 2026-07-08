# Review checklist

## Hard blockers

- [ ] Real operator fields are missing or still placeholders in production.
- [ ] Public URLs in checkbox labels return 404.
- [ ] Marketing consent is bundled into required offer/privacy acceptance.
- [ ] Optional consent is pre-ticked.
- [ ] Autopay is charged without a separate active consent.
- [ ] Offer promises product mechanics that do not exist.
- [ ] Refund/cancel text does not match actual support/product flow.
- [ ] Privacy policy lists data categories/processors that do not match reality.
- [ ] Cookie text says cookies/analytics exist when no banner or analytics exists, or vice versa.
- [ ] Payment document claims the operator stores full card numbers when the payment provider actually handles card data.

## Useful mechanical scans

Search for placeholders:

```bash
rg '\[(OPERATOR|EMAIL|DOMAIN|INN|ADDRESS|PRODUCT|PRICE)\]|_____|TODO|FIXME' .
```

Search for risky consent mistakes:

```bash
rg 'pre.?tick|checked: true|defaultChecked: true|advertising.*required|ads.*required' .
```
