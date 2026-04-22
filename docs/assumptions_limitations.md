# Assumptions and Limitations

## Assumptions

- Data is generated to represent a mid-sized US e-commerce business with realistic variation by category, region, and monthly seasonality.
- `fact_sales` excludes cancelled orders from recognized revenue calculations.
- Returns are modeled as partial or full line-level refunds using `returned_qty`.
- Revenue KPI uses `recognized_revenue` (after discounts and refunds), not gross sales.
- Profit proxy uses accounting-light margin logic:
  - `profit_amount = recognized_revenue - cogs_amount`

## Data Quality Rules Applied

- Duplicate natural keys are removed (`customer_id`, `order_id`, `order_item_id`, etc.).
- Missing customer region is mapped to an explicit `Unknown` region record.
- Missing customer email is imputed with deterministic placeholders.
- Missing product brand is filled as `Unknown`.
- Negative or zero quantities are clipped to at least 1.
- Discount rates are clipped to the range 0.00 to 0.40.

## Limitations

- Data is synthetic and not linked to external market events.
- Marketing spend, shipment costs, and acquisition channels are not modeled.
- Returns are simplified to line-item quantity reductions and refund amounts.
- CLV is a proxy based on observed revenue, not a predictive lifetime model.
