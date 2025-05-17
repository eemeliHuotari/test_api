from django.test import TestCase, Client
from django.urls import reverse

class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "../templates/home.html")