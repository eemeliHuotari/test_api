import json
from django.test import TestCase, Client
from django.urls import reverse
from ..models import User, Order, OrderItem, MenuItem


class OrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(name="Test User")
        self.menu_item = MenuItem.objects.create(
            name="Test Item", description="Test Description", price=10.0
        )
        self.order = Order.objects.create(user=self.user, status="pending")
        self.order_item = OrderItem.objects.create(
            order=self.order, item=self.menu_item, amount=2
        )

    # Tests for GET requests
    def test_get_all_orders(self):
        # Test that the get_all view returns the correct number of orders
        response = self.client.get(reverse("Orders"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("order_count", response.json())

    def test_get_orders_by_status(self):
        # Test that the get_by_status view returns the correct number of orders
        response = self.client.get(reverse("OrdersID", args=["pending"]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("order_count", response.json())

    def test_get_order_by_id(self):
        # Test that the get_by_id view returns the correct order
        response = self.client.get(reverse("OrdersID", args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["order_num"], self.order.id)

    def test_get_orders_by_user(self):
        # Test that the get_by_user view returns the correct number of orders
        response = self.client.get(reverse("OrdersID", args=[self.user.name]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("orders", response.json())

    # Tests for POST, UPDATE and DELETE requests

    def test_create_order(self):
        # Test that a new order can be created
        data = {
            "user": self.user.name,
            "order_items": [{"item_id": self.menu_item.id, "amount": 1}],
            "status": "pending",
        }
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("order_num", response.json())

    def test_create_order_with_incorrect_status(self):
        # Test that creating an order with an incorrect status type is not allowed
        data = {
            "user": self.user.name,
            "order_items": [{"item_id": self.menu_item.id, "amount": 1}],
            "status": "invalid",
        }
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertNotEqual(
            response.status_code,
            201,
            "Creating an order with an incorrect status type is not allowed!",
        )

    def test_create_order_invalid_json(self):
        """Test that creating an order with invalid JSON fails."""
        invalid_json_data = "Invalid JSON"
        response = self.client.post(
            reverse("Orders"), invalid_json_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format", response.content.decode())

    def test_update_order(self):
        # Test that an order can be updated
        data = {
            "status": "ready",
            "order_items": [{"item_id": self.menu_item.id, "amount": 3}],
        }
        response = self.client.put(
            reverse("OrdersID", args=[self.order.id]),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ready")

    def test_update_order_invalid_json(self):
        # Test that updating an order with invalid JSON fails
        response = self.client.put(
            reverse("OrdersID", args=[self.order.id]),
            "invalid json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid JSON format.")

    def test_delete_order(self):
        # Test that an order can be deleted
        response = self.client.delete(reverse("OrdersID", args=[self.order.id]))
        self.assertEqual(response.status_code, 204)

    # Tests for invalid requests

    def test_get_orders_by_incorrect_status(self):
        # Test that the get_by_status view returns 404 for an incorrect status (user)
        response = self.client.get(reverse("OrdersID", args=["not pending"]))
        self.assertEqual(response.status_code, 404)

    def test_get_order_by_invalid_id(self):
        # Test that the get_by_id view returns 404 for an invalid order id
        response = self.client.get(reverse("OrdersID", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_get_orders_by_invalid_user(self):
        # Test that the get_by_user view returns 404 for an invalid user
        response = self.client.get(reverse("OrdersID", args=["Invalid User"]))
        self.assertEqual(response.status_code, 404)

    def test_create_order_with_invalid_user(self):
        # Test that creating an order with an invalid user returns 404
        data = {
            "user": "Invalid User",
            "order_items": [{"item_id": self.menu_item.id, "amount": 1}],
            "status": "pending",
        }
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    def test_create_order_with_no_user_or_orderitem(self):
        # Test that creating an order with no user or order_items returns 400
        data = {"user": None, "order_items": None, "status": "pending"}
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_order_with_nonexistant_menuitem(self):
        # Test that creating an order with an invalid user returns 404
        data = {
            "user": self.user.name,
            "order_items": [{"item_id": 999999999999, "amount": 1}],
            "status": "pending",
        }
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_order_with_wrong_datatype(self):
        # Test that creating an order with an invalid datatype returns 500
        data = {
            "user": self.user.name,
            "order_items": "like a fifty",
            "status": "pending",
        }
        response = self.client.post(
            reverse("Orders"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)

    def test_update_order_with_invalid_id(self):
        # Test that updating an order with an invalid id returns 404
        data = {
            "status": "ready",
            "order_items": [{"item_id": self.menu_item.id, "amount": 3}],
        }
        response = self.client.put(
            reverse("OrdersID", args=[9999]),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_order_with_nonexistant_menuitem(self):
        # Test that an order can be updated
        data = {
            "status": "ready",
            "order_items": [{"item_id": 999999999999, "amount": 3}],
        }
        response = self.client.put(
            reverse("OrdersID", args=[self.order.id]),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_order_with_wrong_datatype(self):
        # Test that an order can be updated
        data = {"status": "ready", "order_items": "four numba fives"}
        response = self.client.put(
            reverse("OrdersID", args=[self.order.id]),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)

    def test_delete_order_with_invalid_id(self):
        # Test that deleting an order with an invalid id returns 404
        response = self.client.delete(reverse("OrdersID", args=[9999]))
        self.assertEqual(response.status_code, 404)
