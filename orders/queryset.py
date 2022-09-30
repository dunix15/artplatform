from locallib.queryset import BaseQuerySet


class ArtworkQuerySet(BaseQuerySet):
    pass


class OrderQuerySet(BaseQuerySet):
    def artwork(self, arg):
        return self.id_field_filter("artwork", arg)

    def direction(self, arg):
        return self.field_filter("direction", arg)

    def buy(self):
        return self.direction(self.model.OrderDirection.buy.value)

    def sell(self):
        return self.direction(self.model.OrderDirection.sell.value)

    def active(self):
        return self.filter(is_canceled=False)

    def canceled(self):
        return self.filter(is_canceled=True)


class TransactionQuerySet(BaseQuerySet):
    pass
