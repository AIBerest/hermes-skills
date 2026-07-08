# Paid subscription / autopay consent template

Use when the product charges recurring payments or converts a trial into paid access.

I agree that `[OPERATOR_LEGAL_NAME]` may initiate recurring charges for `[PRODUCT_NAME]` under these terms:

- trial price: `[TRIAL_PRICE_OR_NONE]`;
- trial period: `[TRIAL_PERIOD_OR_NONE]`;
- recurring amount: `[RECURRING_AMOUNT]`;
- billing period: `[BILLING_PERIOD]`;
- next charge date/time rule: `[NEXT_CHARGE_RULE]`;
- cancellation route: `[CANCEL_ROUTE]`;
- support contact: `[SUPPORT_EMAIL]`.

Recommended checkbox:

```text
I agree to recurring charges: [amount] every [period] after [trial/first date]. I can cancel future charges at [cancel route].
```

UI rule:

```json
{
  "required": true,
  "defaultChecked": false,
  "separateFromOffer": true
}
```
