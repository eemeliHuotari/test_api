"""Views for managing reservations."""

import json
from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import (
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotAllowed,
)
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..models import Reservation, Table, User


def reservations(request):
    """
    Handle requests for the reservations endpoint.

    This function routes requests to appropriate handlers based on the HTTP method:
    - GET: Returns all reservations (handled by get_all)
    - POST: Creates a new reservation (handled by create_reservation)

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    if request.method == "GET":
        return get_all(request)
    elif request.method == "POST":
        return create_reservation(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"], "Only GET and POST are allowed!")


def reservation_id(request, reservation_identifier):
    """
    Handle requests for specific reservations based on the provided identifier.

    This function routes requests based on the type of identifier and HTTP method:
    - If identifier is numeric:
      - GET: Returns reservation by ID (handled by get_by_id)
      - DELETE: Deletes a reservation (handled by delete_reservation)
      - PUT: Updates a reservation (handled by update_reservation)
    - If identifier is a valid time status string ("upcoming", "current", "past"):
      - Returns reservations with that time status (handled by get_by_time_status)
    - Otherwise:
      - Treats identifier as a username and returns user's reservations (handled by get_by_user)

    Args:
        request (HttpRequest): Django HTTP request object
        reservation_identifier (str): Reservation ID, time status, or username to filter by

    Returns:
        JsonResponse: Result from the appropriate handler function
    """
    if reservation_identifier.isdigit():
        reservation_identifier = int(reservation_identifier)
        if request.method == "GET":
            return get_by_id(request, reservation_identifier)

        elif request.method == "DELETE":
            return delete_reservation(request, reservation_identifier)

        elif request.method == "PUT":
            return update_reservation(request, reservation_identifier)

        else:
            return HttpResponseNotAllowed(
                ["GET", "DELETE", "PUT"], "Only GET, DELETE, PUT are allowed!"
            )
    else:
        if request.method == "GET":
            valid_time_status = ["upcoming", "current", "past"]
            if reservation_identifier in valid_time_status:
                return get_by_time_status(request, reservation_identifier)
            else:
                return get_by_user(request, reservation_identifier)
        else:
            return HttpResponseNotAllowed(["GET"], "Only GET is allowed!")


def get_all(request):
    """
    Returns all reservations in the database.

    Args:
        request (HttpRequest): Django HTTP request object (unused)

    Returns:
        JsonResponse: JSON containing all reservations with their count
    """

    reservations = {"reservation_count": 0, "reservations": []}

    for reservation in Reservation.objects.all():
        reservations["reservation_count"] += 1
        reservations["reservations"].append(reservation.serialize())

    return JsonResponse(reservations)


def get_by_time_status(request, time_status: str):
    """
    Returns reservations filtered by their time status (upcoming, current, or past).

    Args:
        request (HttpRequest): Django HTTP request object (unused)
        time_status (str): The time status - "upcoming", "current" or "past"

    Returns:
        JsonResponse: JSON containing all reservations with the specified time status
    """

    valid_time_status = ["upcoming", "current", "past"]
    if time_status not in valid_time_status:
        return HttpResponseBadRequest(f"Time must be one of: {valid_time_status}")

    reservations = {"reservation_count": 0, "reservations": []}
    all_reservations = Reservation.objects.all()

    current_time = timezone.now()

    if time_status == "upcoming":
        for reservation in Reservation.objects.filter(
            date_and_time__gt=current_time
        ).all():
            reservations["reservation_count"] += 1
            reservations["reservations"].append(reservation.serialize())

    elif time_status == "current":
        for reservation in all_reservations:
            if reservation.date_and_time > current_time:
                continue
            reservation_end = reservation.date_and_time + reservation.duration
            if reservation_end > current_time:
                reservations["reservation_count"] += 1
                reservations["reservations"].append(reservation.serialize())

    elif time_status == "past":
        for reservation in all_reservations:
            reservation_end = reservation.date_and_time + reservation.duration
            if reservation_end < current_time:
                reservations["reservation_count"] += 1
                reservations["reservations"].append(reservation.serialize())

    return JsonResponse(reservations)


def get_by_id(request, reservation_id: int):
    """
    Returns a specific reservation by its ID.

    Args:
        request (HttpRequest): Django HTTP request object (unused)
        reservation_id (int): The unique identifier of the reservation

    Returns:
        JsonResponse: JSON containing the requested reservation details
    """

    try:
        reservation = Reservation.objects.get(id=int(reservation_id))
    except ObjectDoesNotExist:
        return HttpResponseNotFound(
            f"Reservation with number {reservation_id} not found!"
        )

    return JsonResponse(reservation.serialize())


def get_by_user(request, user_name: str):
    """
    Returns all reservations for a specific user.

    Args:
        request (HttpRequest): Django HTTP request object (unused)
        user_name (str): Username to filter reservations by

    Returns:
        JsonResponse: JSON containing all reservations for the specified user
    """

    try:
        user = User.objects.get(name=user_name)
    except ObjectDoesNotExist:
        return HttpResponseNotFound(f"User {user_name} does not exist")

    reservations = {"user": user.name, "reservations": []}
    for reservation in Reservation.objects.filter(user=user).all():
        reservations["reservations"].append(reservation.serialize())

    return JsonResponse(reservations)


@csrf_exempt
def create_reservation(request):
    """
    Creates a new reservation.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing the newly created reservation
    """

    try:
        data = json.loads(request.body)
        user_name = data.get("reserver")
        table_id = data.get("table")
        number_of_people = data.get("number_of_people")
        date_and_time = data.get("date_and_time")
        duration = data.get("duration")

        if not (
            user_name and table_id and number_of_people and date_and_time and duration
        ):
            return HttpResponseBadRequest("Missing required fields.")
        try:
            user = User.objects.get(name=user_name)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found.")
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return HttpResponseNotFound("Table not found.")
        naive_datetime = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M:%S")
        aware_datetime = timezone.make_aware(
            naive_datetime, timezone.get_current_timezone()
        )
        hours, minutes, seconds = map(int, duration.split(":"))
        duration_timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        if aware_datetime < timezone.now():
            return HttpResponseBadRequest("Reservation can't be in the past!")

        if number_of_people < table.min_people:
            return HttpResponseBadRequest(
                f"Too few people for this table. Minimum required: {table.min_people}."
            )
        if number_of_people > table.max_people:
            return HttpResponseBadRequest(
                f"Too many people for this table. Maximum allowed: {table.max_people}."
            )

        end_time = aware_datetime + duration_timedelta
        overlapping = Reservation.objects.filter(
            date_and_time__lt=end_time,
            date_and_time__gte=(aware_datetime - models.F("duration")),
        )

        if overlapping.exists():
            return HttpResponseBadRequest(
                "Reservation overlaps with existing reservations"
            )

        new_reservation = Reservation.objects.create(
            user=user,
            table=table,
            number_of_people=number_of_people,
            date_and_time=aware_datetime,
            duration=duration_timedelta,
        )
        return JsonResponse(new_reservation.serialize(), status=201)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except ValueError:
        return HttpResponseBadRequest("Invalid date/time or duration format.")
    except Exception as e:
        return HttpResponseServerError(f"Error creating reservation: {str(e)}")


@csrf_exempt
def update_reservation(request, id):
    """
    Updates an existing reservation.

    Args:
        request (HttpRequest): Django HTTP request object
        id (int): ID of reservation to update

    Returns:
        JsonResponse: JSON containing the updated reservation
    """

    try:
        data = json.loads(request.body)
        number_of_people = data.get("number_of_people")
        date_and_time = data.get("date_and_time")
        duration = data.get("duration")

        try:
            reservation = Reservation.objects.get(id=id)
        except Reservation.DoesNotExist:
            return HttpResponseNotFound("Reservation not found.")

        if number_of_people:
            reservation.number_of_people = number_of_people

        if date_and_time:
            naive_datetime = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M:%S")
            aware_datetime = timezone.make_aware(
                naive_datetime, timezone.get_current_timezone()
            )
            reservation.date_and_time = aware_datetime

        if duration:
            hours, minutes, seconds = map(int, duration.split(":"))
            duration_timedelta = timedelta(
                hours=hours, minutes=minutes, seconds=seconds
            )
            reservation.duration = duration_timedelta

        if number_of_people < reservation.table.min_people:
            return HttpResponseBadRequest(
                f"Too few people for this table. Minimum required: {reservation.table.min_people}."
            )
        if number_of_people > reservation.table.max_people:
            return HttpResponseBadRequest(
                f"Too many people for this table. Maximum allowed: {reservation.table.max_people}."
            )

        if aware_datetime < timezone.now():
            return HttpResponseBadRequest("Reservation can't be in the past!")

        end_time = aware_datetime + duration_timedelta
        overlapping = Reservation.objects.filter(
            date_and_time__lt=end_time,
            date_and_time__gte=(aware_datetime - models.F("duration")),
        )

        if overlapping.exists():
            return HttpResponseBadRequest(
                "Reservation overlaps with existing reservations"
            )

        reservation.save()
        return JsonResponse(reservation.serialize(), status=200)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except ValueError:
        return HttpResponseBadRequest("Invalid date/time or duration format.")
    except Exception as e:
        return HttpResponseServerError(f"Error updating reservation: {str(e)}")


@csrf_exempt
def delete_reservation(request, id):
    """
    Deletes a reservation by its ID.

    Args:
        request (HttpRequest): Django HTTP request object
        id (int): ID of reservation to delete

    Returns:
        JsonResponse: JSON containing a success message
    """

    try:
        reservation = Reservation.objects.get(id=id)
        reservation.delete()
        return JsonResponse(
            {"message": f"Reservation {id} deleted successfully."}, status=204
        )

    except Reservation.DoesNotExist:
        return HttpResponseNotFound("Reservation not found.")
    except Exception as e:
        return HttpResponseServerError(f"Error deleting reservation: {str(e)}")
