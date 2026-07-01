import pytest

from apps.orders.models import Customer, Order


@pytest.mark.django_db
def test_list_orders_requires_auth(api_client):
    response = api_client.get("/api/v1/orders/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_create_customer_and_order(auth_client):
    customer_response = auth_client.post(
        "/api/v1/customers/",
        {"name": "Acme Ltd", "email": "billing@acme.example"},
        format="json",
    )
    assert customer_response.status_code == 201
    customer_id = customer_response.data["id"]

    order_response = auth_client.post(
        "/api/v1/orders/",
        {
            "customer": customer_id,
            "status": "draft",
            "items": [
                {"sku": "WIDGET-01", "quantity": 2, "unit_price": "19.99"},
                {"sku": "WIDGET-02", "quantity": 1, "unit_price": "5.00"},
            ],
        },
        format="json",
    )
    assert order_response.status_code == 201
    assert order_response.data["status"] == "draft"
    assert len(order_response.data["items"]) == 2
    assert order_response.data["total"] == "44.98"


@pytest.mark.django_db
def test_order_list_pagination(auth_client):
    customer = Customer.objects.create(name="Beta Co", email="beta@example.com")
    for _ in range(25):
        order = Order.objects.create(customer=customer)
        order.items.create(sku="SKU", quantity=1, unit_price="10.00")
        order.recalculate_total()

    response = auth_client.get("/api/v1/orders/")
    assert response.status_code == 200
    assert response.data["count"] == 25
    assert len(response.data["results"]) == 20
    assert response.data["next"] is not None


@pytest.mark.django_db
def test_filter_orders_by_status(auth_client):
    customer = Customer.objects.create(name="Gamma Inc", email="gamma@example.com")
    Order.objects.create(customer=customer, status=Order.Status.DRAFT)
    Order.objects.create(customer=customer, status=Order.Status.PAID)
    Order.objects.create(customer=customer, status=Order.Status.PAID)

    response = auth_client.get("/api/v1/orders/", {"status": "paid"})
    assert response.status_code == 200
    assert response.data["count"] == 2
    assert all(o["status"] == "paid" for o in response.data["results"])


@pytest.mark.django_db
def test_order_status_transition(auth_client):
    customer = Customer.objects.create(name="Delta LLC", email="delta@example.com")
    create_response = auth_client.post(
        "/api/v1/orders/",
        {
            "customer": customer.id,
            "status": "draft",
            "items": [{"sku": "X", "quantity": 1, "unit_price": "10.00"}],
        },
        format="json",
    )
    order_id = create_response.data["id"]

    patch_response = auth_client.patch(
        f"/api/v1/orders/{order_id}/",
        {"status": "paid"},
        format="json",
    )
    assert patch_response.status_code == 200
    assert patch_response.data["status"] == "paid"

    bad_transition = auth_client.patch(
        f"/api/v1/orders/{order_id}/",
        {"status": "draft"},
        format="json",
    )
    assert bad_transition.status_code == 400


@pytest.mark.django_db
def test_health_endpoint(api_client):
    response = api_client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.data == {"status": "ok"}
