"""Views for managing users."""

import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    HttpResponseNotAllowed,
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt

from ..models import User


def user(request):
    """
    Handle requests for the users endpoint.

    This function routes requests to appropriate handlers based on the HTTP method:
    - GET: Returns all users (handled by get_all)
    - POST: Creates a new user (handled by create_user)

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    if request.method == "GET":
        return get_all(request)
    elif request.method == "POST":
        return create_user(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"], "Only GET and POST are allowed!")


def user_id(request, user_identifier):
    """
    Handle requests for a specific user based on the provided identifier.

    This function routes requests based on the HTTP method:
    - GET: Returns user by ID or name (handled by get_by_identifier)
    - DELETE: Deletes a user (handled by delete_user)

    Args:
        request (HttpRequest): Django HTTP request object
        user_identifier (str): User ID or name to identify the user

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    if user_identifier.isdigit() and request.method == "DELETE":
        return delete_user(request, int(user_identifier))
    if request.method == "GET":
        return get_by_identifier(request, user_identifier)
    else:
        return HttpResponseNotAllowed(
            ["GET", "DELETE"], "Only GET and DELETE are allowed!"
        )


def get_all(request):
    """
    Returns all users in the database.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing all users with a short representation and total count
    """

    users = {"user_count": 0, "users": []}
    for user in User.objects.all():
        users["users"].append(user.serialize(short=True))
        users["user_count"] += 1
    return JsonResponse(users)


def get_by_identifier(request, id):
    """
    Returns a specific user by their ID or name.

    Args:
        request (HttpRequest): Django HTTP request object
        id (str): User ID (numeric) or name to search for

    Returns:
        JsonResponse: JSON containing the requested user's detailed information
    """

    try:
        if id.isdigit():
            user = User.objects.get(id=int(id))
        else:
            user = User.objects.get(name=id)

    except ObjectDoesNotExist:
        return HttpResponseNotFound("User does not exist!")

    return JsonResponse(user.serialize())


@csrf_exempt
def create_user(request):
    """
    Creates a new user.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing the newly created user
    """

    try:
        data = json.loads(request.body)
        name = data.get("name")

        if not name:
            return HttpResponseBadRequest("Missing required field: 'name'.")

        if User.objects.filter(name=name).exists():
            return HttpResponseBadRequest("User with this name already exists.")

        newuser = User.objects.create(name=name)
        return JsonResponse(newuser.serialize(), status=201)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")


@csrf_exempt
def delete_user(request, id):
    """Deletes a user by their ID."""

    try:
        user = User.objects.get(id=id)
        user.delete()
        return HttpResponse(f"User {id} deleted successfully.", status=200)

    except User.DoesNotExist:
        return HttpResponseNotFound(f"User with ID {id} not found.")
