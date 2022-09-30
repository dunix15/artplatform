from enumfields.drf import EnumSupportSerializerMixin
from rest_framework import serializers

from .models import Artwork, Order, Transaction


class ArtworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artwork
        fields = ("id", "name")


class OrderSerializer(EnumSupportSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user_id", "artwork", "price", "direction", "is_canceled")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "artwork", "price", "buy_order", "sell_order")
