from django_webtest import WebTest

from .factories import ArtworkFactory, OrderFactory, TransactionFactory
from orders.models import Artwork, Order, Transaction
from orders.serializer import OrderSerializer, TransactionSerializer


class ArtworkTests(WebTest):
    url = "/v1/artworks/"
    detail_url = "/v1/artworks/{id}/"

    def test_get_artworks(self):
        response = self.app.get(self.url)

        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 0)

        ArtworkFactory()
        response = self.app.get(self.url)
        self.assertEqual(len(response.json), 1)

    def test_get_artwork(self):
        artwork = ArtworkFactory()
        response = self.app.get(self.detail_url.format(id=artwork.id))
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json["name"], artwork.name)

    def test_create_artwork(self):
        self.app.post_json(
            self.url,
            params={"name": "Mona Lisa"},
            status=201,
        )
        self.assertEqual(Artwork.objects.count(), 1)


class OrderTests(WebTest):
    url = "/v1/orders/"

    def setUp(self):
        super().setUp()
        self.artwork = ArtworkFactory()

    def test_view_all_orders(self):
        OrderFactory.create_batch(10, artwork=self.artwork)
        response = self.app.get(self.url)
        self.assertEqual(len(response.json), 10)

    def test_view_user_orders(self):
        user_id = 1
        order = OrderFactory(artwork=self.artwork, user_id=user_id)
        OrderFactory(artwork=self.artwork, user_id=2)
        response = self.app.get(
            self.url,
            params={"user_id": user_id},
            status=200,
        )
        self.assertEqual(len(response.json), 1)
        expected = OrderSerializer(order).data
        self.assertEqual(response.json[0], expected)

    def test_create_order(self):
        self.app.post_json(
            self.url,
            params={
                "user_id": 1,
                "artwork": self.artwork.id,
                "price": 10,
                "direction": "sell",
            },
            status=201,
        )
        self.assertEqual(Order.objects.count(), 1)
        self.assertFalse(Transaction.objects.exists())

    def test_cancel_order(self):
        order = OrderFactory(artwork=self.artwork)
        response = self.app.post_json(
            f"/v1/orders/{order.id}/cancel",
            params={},
            status=200,
        )
        self.assertTrue(response.json["is_canceled"])
        self.assertFalse(Order.objects.active().exists())

    def test_match_order(self):
        """
        Simple matching test. More complicated ones are defined in `test_transactions.py`
        """
        sell_order = self.app.post_json(
            self.url,
            params={
                "user_id": 1,
                "artwork": self.artwork.id,
                "price": 10,
                "direction": "sell",
            },
            status=201,
        )
        self.assertFalse(Transaction.objects.exists())
        buy_order = self.app.post_json(
            self.url,
            params={
                "user_id": 2,
                "artwork": self.artwork.id,
                "price": 10,
                "direction": "buy",
            },
            status=201,
        )
        transaction = Transaction.objects.select_related(
            "sell_order", "buy_order"
        ).first()
        self.assertEqual(str(transaction.sell_order.id), sell_order.json["id"])
        self.assertEqual(str(transaction.buy_order.id), buy_order.json["id"])
        self.assertTrue(transaction.sell_order.is_canceled)
        self.assertTrue(transaction.buy_order.is_canceled)


class TransactionTests(WebTest):
    url = "/v1/transactions/"

    def setUp(self):
        super().setUp()
        self.user_id = 42
        self.transaction = TransactionFactory(sell_order__user_id=self.user_id)
        TransactionFactory.create_batch(10, sell_order__user_id=1, buy_order__user_id=2)

    def test_view_all_transactions(self):
        response = self.app.get(self.url)
        self.assertEqual(len(response.json), 0)

    def test_view_user_transactions(self):
        response = self.app.get(
            self.url,
            params={"user_id": self.user_id},
            status=200,
        )
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["id"], str(self.transaction.id))
