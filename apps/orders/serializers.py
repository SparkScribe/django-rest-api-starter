from django.db import transaction
from rest_framework import serializers

from .models import Customer, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "email", "created_at"]
        read_only_fields = ["id", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "sku", "quantity", "unit_price", "line_total"]
        read_only_fields = ["id", "line_total"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["line_total"] = str(instance.line_total)
        return data


class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["sku", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "status",
            "total",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "total", "created_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True)

    class Meta:
        model = Order
        fields = ["customer", "status", "items"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one line item is required.")
        return value

    def validate_status(self, value):
        if value != Order.Status.DRAFT:
            raise serializers.ValidationError("New orders must start as draft.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        order.recalculate_total()
        return order


class OrderStatusSerializer(serializers.ModelSerializer):
    ALLOWED_TRANSITIONS = {
        Order.Status.DRAFT: {Order.Status.PAID, Order.Status.CANCELLED},
        Order.Status.PAID: {Order.Status.SHIPPED, Order.Status.CANCELLED},
        Order.Status.SHIPPED: set(),
        Order.Status.CANCELLED: set(),
    }

    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        current = self.instance.status
        allowed = self.ALLOWED_TRANSITIONS.get(current, set())
        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot move from '{current}' to '{value}'."
            )
        return value
