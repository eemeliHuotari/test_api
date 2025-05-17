import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "burgir.settings")
django.setup()

from app.models import User, Table, MenuItem, Order, OrderItem, Reservation

# Support functions:

def get_next_available_user_number():
    """
    Finds the next available number for a username in the format 'UserX'.
    """
    existing_users = User.objects.filter(name__startswith="User").values_list("name", flat=True)
    
    used_numbers = set()
    for name in existing_users:
        if name.startswith("User") and name[4:].isdigit():
            used_numbers.add(int(name[4:]))
    
    new_number = 0
    while new_number in used_numbers:
        new_number += 1

    return new_number

def get_next_available_item_number(item_type):
    """
    Finds the next available number for a menu item with the given type.
    
    Args:
        item_type (str): The type of the menu item (e.g., "main course", "drink").
    
    Returns:
        int: The next available number for that item type.
    """
    existing_items = MenuItem.objects.filter(name__startswith=item_type).values_list("name", flat=True)
    
    used_numbers = set()
    for name in existing_items:
        parts = name.split()
        if len(parts) > 1 and parts[-1].isdigit():
            used_numbers.add(int(parts[-1]))

    new_number = 1
    while new_number in used_numbers:
        new_number += 1

    return new_number

def is_table_available(table, start_time, duration):
    """
    Checks if a table is available at a given time.

    Args:
        table (Table): The table to check availability for.
        start_time (datetime): The desired reservation start time.
        duration (timedelta): The duration of the reservation.

    Returns:
        bool: True if the table is available, False otherwise.
    """
    end_time = start_time + duration

    # Check if any existing reservation overlaps
    overlapping_reservations = Reservation.objects.filter(
        table=table,
        date_and_time__lt=end_time,  # Starts before this reservation ends
    ).filter(
        date_and_time__gt=start_time - timedelta(minutes=1)  # Ends after this reservation starts
    )

    return not overlapping_reservations.exists()  # True if no overlap

# Population functions:

def populate_users(n=10):
    """
    Populates the User model with random user data.

    Args:
        n (int): Number of users to create.
    """
    users_created = 0
    for i in range(n):
        new_number = get_next_available_user_number()
        name = f"User{new_number}"
        
        user = User.objects.create(name=name)
        users_created += 1
        print(f"Created User {user.id}: {name}")

    print(f"\nSuccessfully created {users_created} users.\n")

def populate_tables(n=10):
    """
    Populates the Table model with random table data.

    Args:
        n (int): Number of tables to create.
    """
    tables_created = 0

    for _ in range(n):
        min_people = random.randint(1, 4)  # Random minimum capacity
        max_people = random.randint(min_people + 1, min_people + 6)  # Ensure max > min
        
        table = Table.objects.create(min_people=min_people, max_people=max_people)
        tables_created += 1
        print(f"Created Table {table.id}: Min {min_people}, Max {max_people}")

    print(f"\nSuccessfully created {tables_created} tables.")

def populate_menuitem(n=10):
    """
    Populates the MenuItem model with random data.

    Args:
        n (int): Number of menu items to create.
    """
    item_types = ["main course", "drink", "appetizer", "snack", "dessert"]
    menuitems_created = 0

    for i in range(n):
        item_type = random.choice(item_types)
        new_number = get_next_available_item_number(item_type)
        name = f"{item_type} {new_number}"
        description = f"Description for {item_type} {i + 1}"
        price = round(random.uniform(5.0, 35.0), 2)
        
        menu_item = MenuItem.objects.create(name=name, description=description, type=item_type, price=price)
        menuitems_created += 1
        print(f"Created MenuItem {menu_item.id}: {name}")

    print(f"\nSuccessfully created {menuitems_created} menu items.\n")

def populate_orders_and_orderitems(n=10):
    """
    Populates the Order model with random data.

    Args:
        n (int): Number of orders to create.
    """
    new_orders_list = []

    status_types = ["pending", "registered", "preparing", "ready", "cancelled"]

    users = list(User.objects.all())  # Fetch all users once
    menu_items = list(MenuItem.objects.all())  # Fetch all menuitems once

    if not users:
        print("No users found. Please populate the User model first.")
        return
    
    if not menu_items:
        print("No menuitems found. Please populate the MenuItems model first.")
        return

    orders_created = 0
    order_items_created = 0

    for _ in range(n):

        status_type = random.choice(status_types)
        user = random.choice(users)
        
        new_order = Order.objects.create(status=status_type, user=user)
        orders_created += 1
        print(f"Created Order {new_order.id} for {user.name}")
        new_orders_list.append(new_order)

    print(f"\nSuccessfully created {orders_created} orders.\n")
    
    for _ in range(n):

        menuitem_type = random.choice(menu_items)
        quantity = random.randint(1,4)
        order = random.choice(new_orders_list)
        
        order_item = OrderItem.objects.create(item=menuitem_type, amount=quantity, order=order)
        order_items_created += 1
        print(f"Created Order Item {order_item.id} with {quantity} x {menuitem_type.name} for Order {order.id}")

    print(f"\nSuccessfully created {order_items_created} order items.\n")

def populate_reservations(n=10):
    """
    Populates the Reservation model with random reservations efficiently, ensuring no table overlap.

    Args:
        n (int): Number of reservations to create.
    """
    users = list(User.objects.all())
    tables = list(Table.objects.all())
    tables.sort(key=lambda t: t.min_people)

    if not users:
        print("No users found. Please populate the User model first.")
        return

    if not tables:
        print("No tables found. Please populate the Table model first.")
        return

    reservations_created = 0

    for _ in range(n):
        user = random.choice(users)

        number_of_people = random.randint(1, max(t.max_people for t in tables))

        days_ahead = random.randint(1, 90)
        start_time = timezone.now() + timedelta(days=days_ahead, hours=random.randint(8, 22))

        duration = timedelta(minutes=random.choice([30, 60, 90, 120, 150, 180]))

        suitable_table = next(
            (table for table in tables if table.min_people <= number_of_people <= table.max_people and is_table_available(table, start_time, duration)),
            None
        )

        if not suitable_table:
            print(f"No available table found for {number_of_people} people at {start_time}.")
            continue

        reservation = Reservation.objects.create(
            user=user,
            table=suitable_table,
            number_of_people=number_of_people,
            date_and_time=start_time,
            duration=duration
        )

        reservations_created += 1
        print(f"Created Reservation {reservation.id} for {number_of_people} people at Table {suitable_table.id} on {start_time}.")

    print(f"\nSuccessfully created {reservations_created} reservations without conflicts.\n")

# Run the script
if __name__ == "__main__":
    # Adjust the number as needed
    n = 20
    populate_users(n)
    populate_tables(n)
    populate_menuitem(n)
    populate_orders_and_orderitems(n)
    populate_reservations(n)
