from django.contrib import admin
from enumfields.admin import EnumFieldListFilter

from .models import Artwork, Order, Transaction


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("created_on",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("artwork", "user_id", "direction", "price", "created_on")
    ordering = ("created_on",)
    list_filter = (
        "artwork",
        ("direction", EnumFieldListFilter),
        "created_on",
    )
    list_select_related = ("artwork",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("artwork", "price", "created_on")
    ordering = ("created_on",)
    list_filter = (
        "artwork",
        "created_on",
    )
    list_select_related = ("artwork", "sell_order", "buy_order")
