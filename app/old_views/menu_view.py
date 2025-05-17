"""Views for managing the menu."""

import json

from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseServerError,
)

from ..models import MenuItem


def menu(request):
    """
    Handle requests for the menu endpoint.

    This function routes requests to appropriate handlers based on the HTTP method:
    - GET: Returns all menu (handled by get_menu)
    - POST: Creates a new order (handled by create_menu_item)

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    print(request.method == "GET")
    if request.method == "GET":
        return get_menu(request)
    elif request.method == "POST":
        return create_menu_item(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"], "Only GET and POST are allowed!")


def get_menu(request):
    """
    Returns the complete menu with items grouped by type.

    Args:
        request (HttpRequest): Django HTTP request object (unused)

    Returns:
        JsonResponse: JSON containing all menu items organized by their type
    """

    # get whole menu
    menu_items = MenuItem.objects.all()
    # Group items by type
    menu_by_type = {}
    for item in menu_items:
        if item.type not in menu_by_type:
            menu_by_type[item.type] = []  # Create a new list for this type
        menu_by_type[item.type].append(item.serialize())

    return JsonResponse(menu_by_type)


def get_items_by_type(request, menu_item_type: str):
    """
    Returns menu items filtered by their type.

    Args:
        request (HttpRequest): Django HTTP request object
        menu_item_type (str): The type of menu items to filter by (e.g., "drink", "main course")

    Returns:
        JsonResponse: JSON containing all menu items of the specified type
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"], "Only GET is allowed!")

    items = {"type": menu_item_type, "items": []}
    for item in MenuItem.objects.filter(type=menu_item_type).all():
        items["items"].append(item.serialize())

    return JsonResponse(items)


def create_menu_item(request):
    """
    Creates a new menu item.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing the newly created menu item
    """

    try:
        data = json.loads(request.body)
        name = data.get("name")
        description = data.get("description")
        item_type = data.get("type")
        price = data.get("price")

        if not (name and description and item_type and price):
            return HttpResponseBadRequest("Missing required fields")

        if MenuItem.objects.filter(name=name).exists():
            return HttpResponseBadRequest("Menu item with this name already exists.")

        new_item = MenuItem.objects.create(
            name=name, description=description, type=item_type, price=price
        )
        return JsonResponse(new_item.serialize(), status=201)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except Exception as e:
        return HttpResponseServerError(f"Error creating user: {str(e)}")
