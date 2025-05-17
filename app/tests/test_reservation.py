import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Reservation, Table, User


class ReservationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(name="testuser")
        self.table = Table.objects.create(min_people=2, max_people=4)
        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            number_of_people=3,
            date_and_time=timezone.now() + timedelta(days=1),
            duration=timedelta(hours=2),
        )
        self.current_reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            number_of_people=3,
            date_and_time=timezone.now(),
            duration=timedelta(hours=2),
        )
        self.past_reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            number_of_people=3,
            date_and_time=timezone.now() - timedelta(days=1),
            duration=timedelta(hours=2),
        )

    def test_get_all_reservations(self):
        response = self.client.get(reverse("Reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservation_count", response.json())
        self.assertEqual(response.json()["reservation_count"], 3)

    def test_get_by_time_status_upcoming(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=["upcoming"],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservation_count", response.json())
        self.assertEqual(response.json()["reservation_count"], 1)

    def test_get_by_time_status_current(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=["current"],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservation_count", response.json())
        self.assertEqual(response.json()["reservation_count"], 1)

    def test_get_by_time_status_past(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=["past"],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservation_count", response.json())
        self.assertEqual(response.json()["reservation_count"], 1)

    def test_post_by_time_status(self):
        response = self.client.post(
            reverse(
                "ReservationsID",
                args=["current"],
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_get_by_time_status_invalid(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=["invalid"],
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_by_id(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_get_by_id_not_found(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=[999],
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_post_get_by_id(self):
        response = self.client.post(
            reverse(
                "ReservationsID",
                args=[
                    self.reservation.id,
                ],
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_get_by_user(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=[self.user.name],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reservations", response.json())

    def test_post_by_user(self):
        response = self.client.post(
            reverse(
                "ReservationsID",
                args=[self.user.name],
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_get_by_user_not_found(self):
        response = self.client.get(
            reverse(
                "ReservationsID",
                args=["unknown"],
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_create_reservation(self):
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": 3,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_create_reservation_with_less_min_people(self):
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": 1,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_reservation_with_more_max_people(self):
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": 99,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_reservation_wrong_date_format(self):
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": 3,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "date here",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_overlapping(self):
        """Making an overlapping reservation should return 400."""
        # post the same reservation twice
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": 3,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400, "Made overlapping reservation!")

    def test_create_past_reservation(self):
        """Making a reservation in the past should return 400."""
        past_time = (timezone.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

        request_data = self.reservation.serialize()
        request_data["date_and_time"] = past_time

        response = self.client.post(
            reverse("Reservations"),
            json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400, "Made reservation in the past!")

    def test_create_reservation_missing_fields(self):
        data = {"reserver": self.user.name, "table": self.table.id}
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_reservation_invalid_json(self):
        response = self.client.post(
            reverse("Reservations"),
            "invalid json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_reservation_user_not_found(self):
        data = {
            "reserver": "89j45timg9jq45yj9",
            "table": self.table.id,
            "number_of_people": 3,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_create_reservation_table_not_found(self):
        data = {
            "reserver": self.user.name,
            "table": 999,
            "number_of_people": 3,
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_create_reservation_wrong_datatype(self):
        data = {
            "reserver": self.user.name,
            "table": self.table.id,
            "number_of_people": "many",
            "date_and_time": (timezone.now() + timedelta(days=2)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "02:00:00",
        }
        response = self.client.post(
            reverse("Reservations"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)

    def test_update_reservation(self):
        data = {
            "number_of_people": 4,
            "date_and_time": (timezone.now() + timedelta(days=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_update_reservation_to_past(self):
        data = {
            "number_of_people": 4,
            "date_and_time": (timezone.now() - timedelta(days=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_reservation_to_overlap(self):
        data = {
            "number_of_people": 4,
            "date_and_time": (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.past_reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_reservation_less_min_people(self):
        data = {
            "number_of_people": 1,
            "date_and_time": (timezone.now() + timedelta(days=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_reservation_more_max_people(self):
        data = {
            "number_of_people": 99,
            "date_and_time": (timezone.now() + timedelta(days=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_reservation_wrong_datatype(self):
        data = {
            "number_of_people": "my whole family",
            "date_and_time": (timezone.now() + timedelta(days=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "duration": "03:00:00",
        }
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)

    def test_update_reservation_not_found(self):
        data = {"number_of_people": 4}
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[999],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_reservation(self):
        response = self.client.delete(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            )
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_reservation_not_found(self):
        response = self.client.delete(
            reverse(
                "ReservationsID",
                args=[999],
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_update_reservation_invalid_json(self):
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            "invalid json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Invalid JSON format.")

    def test_update_reservation_invalid_date_format(self):
        data = {"date_and_time": "invalid date format"}
        response = self.client.put(
            reverse(
                "ReservationsID",
                args=[self.reservation.id],
            ),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content.decode(), "Invalid date/time or duration format."
        )
