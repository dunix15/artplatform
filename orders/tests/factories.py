import factory

from orders.models import OrderDirection


class ArtworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "orders.Artwork"

    name = factory.Sequence(lambda n: f"Artwork {n}")


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "orders.Order"

    artwork = factory.SubFactory(ArtworkFactory)
    user_id = factory.Sequence(lambda n: n)
    price = 0
    direction = OrderDirection.sell


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "orders.Transaction"

    artwork = factory.SubFactory(ArtworkFactory)
    buy_order = factory.SubFactory(OrderFactory)
    sell_order = factory.SubFactory(OrderFactory)
    price = 0
