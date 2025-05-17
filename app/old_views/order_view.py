"""Views for managing orders."""

import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import (
    HttpResponseNotAllowed,
    JsonResponse,
    HttpResponseNotFound,
    HttpResponseBadRequest,
    HttpResponseServerError,
)
from django.views.decorators.csrf import csrf_exempt

from ..models import Order, User, OrderItem, MenuItem


def orders(request):
    """
    Handle requests for the orders endpoint.

    This function routes requests to appropriate handlers based on the HTTP method:
    - GET: Returns all orders (handled by get_all)
    - POST: Creates a new order (handled by create_order)

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: Result from the appropriate handler function
        HttpResponseNotAllowed: If the request method is not supported
    """
    if request.method == "GET":
        return get_all(request)
    elif request.method == "POST":
        return create_order(request)
    else:
        return HttpResponseNotAllowed(["GET", "POST"], "Only GET and POST are allowed!")


def orders_id(request, order_identifier):
    """
    Handle requests for specific orders based on the provided identifier.

    This function routes requests based on the type of identifier and HTTP method:
    - If identifier is numeric:
      - GET: Returns order by ID (handled by get_by_id)
      - PUT: Updates an order (handled by update_order)
      - DELETE: Deletes an order (handled by delete_order)
    - If identifier is a valid status string:
      - Returns orders with that status (handled by get_by_status)
    - Otherwise:
      - Treats identifier as a username and returns user's orders (handled by get_by_user)

    Args:
        request (HttpRequest): Django HTTP request object
        order_identifier (str): Order ID, status, or username to filter by

    Returns:
        JsonResponse: Result from the appropriate handler function
    """
    if order_identifier.isdigit():
        order_identifier = int(order_identifier)
        if request.method == "GET":
            return get_by_id(request, order_identifier)
        elif request.method == "PUT":
            return update_order(request, order_identifier)
        elif request.method == "DELETE":
            return delete_order(request, order_identifier)
        else:
            return HttpResponseNotAllowed(
                ["GET", "DELETE", "PUT"], "Only GET, DELETE, PUT are allowed!"
            )
    else:
        if request.method == "GET":
            valid_statuses = ["ready", "preparing", "pending", "registered"]
            if order_identifier.lower() in valid_statuses:
                return get_by_status(request, order_identifier)
            else:
                return get_by_user(request, order_identifier)
        else:
            return HttpResponseNotAllowed(["GET"], "Only GET is allowed!")


def get_all(request):
    """
    Returns all orders in the database grouped by status.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing all orders organized by their status
    """

    all_orders = Order.objects.all()
    order_by_status = {}
    orders = {"order_count": 0}
    for order in all_orders:
        if order.status not in order_by_status:
            order_by_status[order.status] = []  # Create a new list for this type
        order_by_status[order.status].append(order.serialize(short=True))
        orders["order_count"] += 1

    orders["orders"] = order_by_status

    return JsonResponse(orders)


def get_by_status(request, status):
    """
    Returns the order with a specific status.

    Args:
        request (HttpRequest): Django HTTP request object
        status (str): Expects order status, valid status are
        "ready", "preparing", "pending", "registered".

    Returns:
        JsonResponse: JSON containing all the orders with the specified status
    """

    orders = {"order_count": 0, "orders": []}
    for order in Order.objects.filter(status=status.lower()):
        orders["order_count"] += 1
        orders["orders"].append(order.serialize())
    return JsonResponse(orders)


def get_by_id(request, order_id: int):
    """
    Returns the order with a specific id.

    Args:
        request (HttpRequest): Django HTTP request object
        order_id (int): Order id to find.

    Returns:
        JsonResponse: JSON representation of the order with specified id.
    """

    try:
        order = Order.objects.get(id=int(order_id))
    except ObjectDoesNotExist:
        return HttpResponseNotFound(f"No order found for order number {order_id}!")

    return JsonResponse(order.serialize())


def get_by_user(request, user_name: str):
    """
    Returns the orders made by the specified user.

    Args:
        request (HttpRequest): Django HTTP request object
        user_name (str): The name of the user, who's orders to find.

    Returns:
        JsonResponse: JSON containing all the orders made by this user.
    """

    try:
        user = User.objects.get(name=user_name)
    except ObjectDoesNotExist:
        return HttpResponseNotFound(f"User {user_name} not found!")

    orders = {"user": user.name, "orders": []}
    for order in Order.objects.filter(user=user).all():
        orders["orders"].append(order.serialize())

    return JsonResponse(orders)


@csrf_exempt
def create_order(request):
    """
    Creates a new order.

    Args:
        request (HttpRequest): Django HTTP request object

    Returns:
        JsonResponse: JSON containing the newly created order
    """

    try:
        data = json.loads(request.body)
        user_name = data.get("user")
        order_items = data.get("order_items")
        status = data.get("status", "pending")

        if not user_name or not order_items:
            return HttpResponseBadRequest(
                "Missing required fields: user and order_items."
            )

        valid_statuses = ["ready", "preparing", "pending", "registered"]
        if status.lower() not in valid_statuses:
            return HttpResponseBadRequest(f"Valid status are: {valid_statuses}")

        try:
            user = User.objects.get(name=user_name)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found.")

        new_order = Order.objects.create(
            user=user,
            status=status,
        )

        for item in order_items:
            item_id = item.get("item_id")
            amount = item.get("amount")

            try:
                menu_item = MenuItem.objects.get(id=item_id)
            except MenuItem.DoesNotExist:
                return HttpResponseBadRequest(f"Menu item with id {item_id} not found.")

            OrderItem.objects.create(
                order=new_order,
                item=menu_item,
                amount=amount,
            )

        return JsonResponse(new_order.serialize(), status=201)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except Exception as e:
        return HttpResponseServerError(f"Error creating order: {str(e)}")


@csrf_exempt
def update_order(request, id):
    """
    Updates an existing order.

    Args:
        request (HttpRequest): Django HTTP request object
        id (int): ID of order to update

    Returns:
        JsonResponse: JSON containing the updated order
    """

    try:
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return HttpResponseNotFound("Order not found.")

        data = json.loads(request.body)
        status = data.get("status")
        order_items = data.get("order_items")

        if status:
            order.status = status

        if order_items:
            for item in order_items:
                item_id = item.get("item_id")
                amount = item.get("amount")
                try:
                    menu_item = MenuItem.objects.get(id=item_id)
                except MenuItem.DoesNotExist:
                    return HttpResponseBadRequest(
                        f"Menu item with id {item_id} not found."
                    )
                try:
                    order_item = OrderItem.objects.get(order=order, item=menu_item)
                    order_item.amount = amount
                    order_item.save()
                except OrderItem.DoesNotExist:
                    OrderItem.objects.create(
                        order=order,
                        item=menu_item,
                        amount=amount,
                    )
        order.save()
        return JsonResponse(order.serialize(), status=200)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")
    except Exception as e:
        return HttpResponseServerError(f"Error updating order: {str(e)}")


@csrf_exempt
def delete_order(request, id):
    """
    Deletes an order by its ID.

    Args:
        request (HttpRequest): Django HTTP request object
        id (int): ID of order to delete

    Returns:
        JsonResponse: JSON containing a success message
    """

    try:
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return HttpResponseNotFound("Order not found.")
        order.order_items.all().delete()
        order.delete()
        return JsonResponse({"message": "Order deleted successfully."}, status=204)

    except Exception as e:
        return HttpResponseServerError(f"Error deleting order: {str(e)}")
