import json
from django.test import TestCase, Client
from django.urls import reverse
from ..models import MenuItem


class MenuViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.menu_item1 = MenuItem.objects.create(
            name="Burger", description="A tasty burger", type="main course", price=9.99
        )
        self.menu_item2 = MenuItem.objects.create(
            name="Coke", description="Refreshing beverage", type="drink", price=1.99
        )

    def test_get_menu(self):
        """Test that the get_menu view returns the correct menu."""
        response = self.client.get(reverse("Menu Items"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("main course", response.json())
        self.assertIn("drink", response.json())

    def test_get_items_by_type(self):
        """Test that the get_items_by_type view returns the correct items."""
        response = self.client.get(reverse("Get items by type", args=["drink"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["type"], "drink")
        self.assertEqual(len(response.json()["items"]), 1)

    def test_get_items_by_type_invalid_method(self):
        response = self.client.post(reverse("Get items by type", args=["drink"]))
        self.assertEqual(response.status_code, 405)

    def test_create_menu_item(self):
        """Test that a new menu item can be created."""
        new_item_data = {
            "name": "Fries",
            "description": "Crispy fries",
            "type": "snack",
            "price": 2.99,
        }
        response = self.client.post(
            reverse("Menu Items"),
            json.dumps(new_item_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "Fries")

    def test_create_menu_item_wrong_datatype(self):
        # Test that creating a menu item with a wrong datatype fails
        new_item_data = {
            "name": "Fries",
            "description": "Crispy fries",
            "type": "snack",
            "price": "dolla fiddy",
        }
        response = self.client.post(
            reverse("Menu Items"),
            json.dumps(new_item_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)

    def test_create_menu_item_missing_fields(self):
        """Test that creating a menu item with missing fields fails."""
        new_item_data = {
            "name": "Fries",
            "description": "Crispy fries",
            "type": "snack",
        }
        response = self.client.post(
            reverse("Menu Items"),
            json.dumps(new_item_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.content.decode())

    def test_create_menu_item_duplicate_name(self):
        """Test that creating a menu item with a duplicate name fails."""
        new_item_data = {
            "name": "Burger",
            "description": "Another tasty burger",
            "type": "main course",
            "price": 10.99,
        }
        response = self.client.post(
            reverse("Menu Items"),
            json.dumps(new_item_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Menu item with this name already exists", response.content.decode()
        )

    def test_create_menu_item_invalid_json(self):
        """Test that creating a menu item with invalid JSON fails."""
        invalid_json_data = "Invalid JSON"
        response = self.client.post(
            reverse("Menu Items"),
            invalid_json_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON format", response.content.decode())
