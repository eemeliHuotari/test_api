import json
from django.test import TestCase, Client
from django.urls import reverse
from ..models import Table


class TableViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.table1 = Table.objects.create(min_people=2, max_people=4)
        self.table2 = Table.objects.create(min_people=1, max_people=2)

    def test_get_all_tables(self):
        response = self.client.get(reverse("Tables"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("table_count", response.json())
        self.assertEqual(response.json()["table_count"], 2)

    def test_create_table(self):
        data = {"min_people": 3, "max_people": 6}
        response = self.client.post(
            reverse("Tables"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("min_people", response.json())
        self.assertEqual(response.json()["min_people"], 3)

    def test_create_table_wrong_data_type(self):
        data = {"min_people": "www", "max_people": "ggg"}
        response = self.client.post(
            reverse("Tables"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 500)

    def test_create_table_missing_fields(self):
        data = {"min_people": 3}
        response = self.client.post(
            reverse("Tables"), json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_create_table_invalid_json(self):
        response = self.client.post(
            reverse("Tables"), "invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
