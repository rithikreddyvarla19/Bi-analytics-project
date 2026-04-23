# Quality Checks

Quality checks are executed by `scripts/run_quality_checks.py` using an equivalent dataframe validation layer (pandera-style checks).

## Implemented checks
- Non-null and uniqueness checks on core IDs (`order_id`, `order_line_id`, `payment_id`, `return_id`, `event_id`).
- Positive value constraints for `order_amount`, `item_quantity`, `refund_amount`.
- Non-negative inventory checks for `on_hand_qty`.
- Refund/return threshold guardrail (`return_rate <= 0.25`).
- Stage row count capture for warehouse tables.

## Artifacts
- `outputs/quality/data_quality_report.csv`
- `outputs/quality/quality_summary.json`
- `outputs/observability/stage_row_counts.csv`
