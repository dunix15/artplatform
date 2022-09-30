from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet

from .models import Artwork, Order, Transaction
from .serializer import ArtworkSerializer, OrderSerializer, TransactionSerializer
from .tasks import match_order_task


class ArtworkViewSet(ModelViewSet):
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer


user_id_param = openapi.Parameter(
    "user_id", openapi.IN_QUERY, description="user id", type=openapi.TYPE_INTEGER
)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.active()
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return qs.filter(user_id=user_id)

        return qs

    @swagger_auto_schema(manual_parameters=[user_id_param])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.save()
        match_order_task.delay(order.id)


class TransactionViewSet(ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return qs.filter(
                Q(buy_order__user_id=user_id) | Q(sell_order__user_id=user_id)
            )

        return qs.none()

    @swagger_auto_schema(manual_parameters=[user_id_param])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CancelOrderView(APIView):
    def post(self, request, order_id, format=None):
        Order.objects.id(order_id).update(is_canceled=True)
        return Response(data={"is_canceled": True})
