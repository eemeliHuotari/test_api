"""Views for table management."""

import json

from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseServerError,
)

from ..models import Table


def tables(request):
    """
    Handle requests for the tables endpoint.

    This function routes requests to appropriate handlers based on the HTTP method:
    - GET: Returns all tables (handled by get_all)
    - POST: Creates a new order (handled by create_table)

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    if request.method == "GET":
        return get_all(request)
    elif request.method == "POST":
        return create_table(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"], "Only GET and POST are allowed!")


def get_all(request):
    """
    Returns all tables and total number of tables.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing all the tables

    """

    tables = {"table_count": 0, "tables": []}
    for table in Table.objects.all():
        tables["table_count"] += 1
        tables["tables"].append(table.serialize())
    return JsonResponse(tables)


def create_table(request):
    """
    Creates a new table.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing the newly created table
    """

    try:
        data = json.loads(request.body)
        min_people = data.get("min_people")
        max_people = data.get("max_people")

        if min_people is None or max_people is None:
            return HttpResponseBadRequest(
                "Missing required fields: 'min_people' and 'max_people'."
            )

        new_table = Table.objects.create(min_people=min_people, max_people=max_people)
        return JsonResponse(new_table.serialize(), status=201)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except Exception as e:
        return HttpResponseServerError(f"Error creating table: {str(e)}")
