import uuid

from django.db import models
from enum import Enum
from enumfields import EnumField

from locallib.models import BaseModel

from .queryset import ArtworkQuerySet, OrderQuerySet, TransactionQuerySet


class Artwork(BaseModel):
    objects = ArtworkQuerySet.as_manager()

    name = models.TextField()

    def __str__(self):
        return self.name


class OrderDirection(str, Enum):
    buy = "buy"
    sell = "sell"


class Order(BaseModel):
    objects = OrderQuerySet.as_manager()

    OrderDirection = OrderDirection

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.BigIntegerField()
    artwork = models.ForeignKey(
        Artwork, on_delete=models.PROTECT, related_name="orders"
    )
    price = models.FloatField()
    direction = EnumField(
        OrderDirection,
        max_length=4,
        help_text="Direction type, either buy or sell",
    )
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.artwork}, {self.direction}, price: {self.price}"


class Transaction(BaseModel):
    objects = TransactionQuerySet.as_manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artwork = models.ForeignKey(
        Artwork, on_delete=models.PROTECT, related_name="transactions"
    )
    price = models.FloatField()
    buy_order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="buy_transactions"
    )
    sell_order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name="sell_transactions"
    )

    def __str__(self):
        return f"{self.artwork}, price: {self.price}"
