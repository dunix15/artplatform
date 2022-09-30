from typing import Optional

from artplatform import celery_app
from django.db import transaction

from orders.models import Order, Transaction, OrderDirection


@transaction.atomic
def match_order(order_id: str) -> Optional[Transaction]:
    """
    Transaction happens when two orders for the same item are received
    with opposing interest and a matching price.
    We define a matching price as the following:
    - If the first order to arrive was a buy order, next sell order
    for this item with a price lower or equal to the buy order's price
    will produce a transaction with the price of the buy order.
    - If the first order to arrive was a sell order, next buy order
    for this item with a price greater or equal to the sell order's price
    will produce a transaction with the price of the sell order.
    """
    order = Order.objects.active().id(order_id).first()
    if not order:
        return None

    # match opposite direction
    if order.direction == OrderDirection.sell:
        kwargs = {
            "direction": OrderDirection.buy,
            "price__gte": order.price,
        }
    else:
        kwargs = {
            "direction": OrderDirection.sell,
            "price__lte": order.price,
        }

    match = (
        Order.objects.active().filter(**kwargs).order_by("price", "created_on").first()
    )
    if match:
        # completed orders are marked as canceled
        Order.objects.id([order, match]).update(is_canceled=True)

        transaction_obj = Transaction(artwork_id=order.artwork_id, price=match.price)
        for _order in [order, match]:
            if _order.direction == OrderDirection.sell:
                transaction_obj.sell_order = _order
            else:
                transaction_obj.buy_order = _order

        transaction_obj.save()
        return transaction_obj

    return None


@celery_app.app.task()
def match_order_task(order_id: str) -> Optional[int]:
    transaction_obj = match_order(order_id)
    return transaction_obj and transaction_obj.id
