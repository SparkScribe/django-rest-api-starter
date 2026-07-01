from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import OrderFilter
from .models import Customer, Order
from .serializers import (
    CustomerSerializer,
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)


class CustomerViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.select_related("customer").prefetch_related("items")
    filterset_class = OrderFilter
    ordering_fields = ["created_at", "total", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action in ("partial_update", "update"):
            return OrderStatusSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(instance).data)

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)
