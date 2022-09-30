from django.test import TestCase

from orders.models import Transaction, Order, OrderDirection
from orders.tasks import match_order
from .factories import ArtworkFactory, OrderFactory


class TransactionTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.artwork = ArtworkFactory()

    def test_no_match(self):
        """
        Simple test for situation when there isn't any match
        """
        OrderFactory(artwork=self.artwork, direction=OrderDirection.sell, price=2)
        buy_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.buy, price=1
        )
        with self.assertNumQueries(4):
            transaction = match_order(buy_order.id)
            self.assertIsNone(transaction)

    def test_basic_match(self):
        """
        Basic match with the same price.
        Ensure there is transaction object and orders are canceled.
        """
        sell_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.sell, price=1
        )
        buy_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.buy, price=1
        )
        with self.assertNumQueries(6):
            transaction = match_order(buy_order.id)
            self.assertEqual(transaction.price, 1)
            self.assertEqual(transaction.sell_order_id, sell_order.id)
            self.assertEqual(transaction.buy_order_id, buy_order.id)

        self.assertEqual(Transaction.objects.count(), 1)
        self.assertTrue(Order.objects.id(sell_order).get().is_canceled)
        self.assertTrue(Order.objects.id(buy_order).get().is_canceled)

    def test_first_sell(self):
        """
        If the first order to arrive was a buy order, next sell order
        for this item with a price lower or equal to the buy order's price
        will produce a transaction with the price of the buy order
        """
        sell_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.sell, price=1
        )
        buy_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.buy, price=2
        )
        with self.assertNumQueries(6):
            transaction = match_order(buy_order.id)
            self.assertEqual(transaction.price, sell_order.price)

    def test_first_buy(self):
        """
        If the first order to arrive was a sell order, next buy order
        for this item with a price greater or equal to the sell order's price
        will produce a transaction with the price of the sell order.
        """
        buy_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.buy, price=2
        )
        sell_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.sell, price=1
        )
        with self.assertNumQueries(6):
            transaction = match_order(sell_order.id)
            self.assertEqual(transaction.price, buy_order.price)

    def test_multiple_sell(self):
        """
        For multiple orders outstanding in the same direction
        they be executed from best to worst price with ties broken by order of arrival.
        """
        sell_orders = [
            OrderFactory(
                artwork=self.artwork, direction=OrderDirection.sell, price=price
            )
            for price in [1, 1, 2, 4]
        ]
        expected_sell_order = sell_orders[0]

        buy_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.buy, price=3
        )
        with self.assertNumQueries(6):
            transaction = match_order(buy_order.id)
            self.assertEqual(transaction.price, expected_sell_order.price)
            self.assertEqual(transaction.sell_order_id, expected_sell_order.id)

    def test_multiple_buy(self):
        """
        For multiple orders outstanding in the same direction
        they be executed from best to worst price with ties broken by order of arrival.
        """
        buy_orders = [
            OrderFactory(
                artwork=self.artwork, direction=OrderDirection.buy, price=price
            )
            for price in [1, 3, 3, 4]
        ]
        expected_buy_order = buy_orders[1]

        sell_order = OrderFactory(
            artwork=self.artwork, direction=OrderDirection.sell, price=2
        )
        with self.assertNumQueries(6):
            transaction = match_order(sell_order.id)
            self.assertEqual(transaction.price, expected_buy_order.price)
            self.assertEqual(transaction.buy_order_id, expected_buy_order.id)
