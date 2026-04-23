from scripts.generate_data import generate_customers, generate_products, generate_orders, generate_clickstream


def test_data_generation_shapes():
    customers = generate_customers(20)
    products = generate_products(10)
    orders, payments, returns, inventory = generate_orders(customers, products, 50, 14)
    clickstream = generate_clickstream(customers, products, 200, 14)

    assert len(customers) == 20
    assert len(products) == 10
    assert len(orders) > 0
    assert len(payments) == 50
    assert "order_id" in orders.columns
    assert "event_type" in clickstream.columns
    assert len(inventory) > 0
    assert "refund_amount" in returns.columns or returns.empty
