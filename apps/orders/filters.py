import django_filters

from .models import Order


class OrderFilter(django_filters.FilterSet):
    customer_id = django_filters.NumberFilter(field_name="customer_id")

    class Meta:
        model = Order
        fields = ["status", "customer_id"]
