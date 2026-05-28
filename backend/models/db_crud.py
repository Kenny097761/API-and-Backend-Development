import sqlite3
from backend.models.db_connect import get_connection


_ALLOWED_TRANSITIONS = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["delivered"],
}


def is_valid_transition(current_status, new_status):
    return new_status in _ALLOWED_TRANSITIONS.get(current_status, [])


class ShipmentAlreadyExistsError(Exception):
    pass


def add_device(name, type, unit_price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO devices (name, type, unit_price, stock) VALUES (?, ?, ?, ?)""",
                   (name, type, unit_price, stock))
    conn.commit()
    conn.close()

def create_order(customer_id,total_price,status ='saved'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" INSERT INTO orders (customer_id,status,total_price,created_at) VALUES(?,?,?,datetime('now'))""",
    (customer_id, status, total_price))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def create_order_item(order_id,device_id,quantity,total_price):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""INSERT INTO order_items(order_id,device_id,quantity,total_price)VALUES (?,?,?,?)""",
    (order_id,device_id,quantity,total_price))
    conn.commit()
    conn.close()

def replace_order_items(order_id, items, new_total): 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT device_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
    old_items = cursor.fetchall()

    for old in old_items:
        cursor.execute(
            "UPDATE devices SET stock = stock + ? WHERE device_id = ?",
            (old["quantity"], old["device_id"])
        )
    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
    for item in items:
        cursor.execute("""INSERT INTO order_items (order_id, device_id, quantity, total_price) VALUES (?, ?, ?, ?)""",
            (order_id, item["device_id"], item["quantity"], item["total_price"])
        )

        cursor.execute(
            "UPDATE devices SET stock = stock - ? WHERE device_id = ?",
            (item["quantity"], item["device_id"])
        )
 
    cursor.execute(
        "UPDATE orders SET total_price = ? WHERE order_id = ?",
        (new_total, order_id)
    )
    conn.commit()
    conn.close()

def decrement_stock(device_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE devices SET stock = stock - ? WHERE device_id = ?", (quantity, device_id))
    conn.commit()
    conn.close()
 
def create_shipment(order_id, staff_id, address_dict):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO shipments
                    (order_id, staff_id, status,
                     street_number, street_name, suburb, postcode, created_at)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, datetime('now'))
                """,
                (
                    order_id,
                    staff_id,
                    address_dict["street_number"],
                    address_dict["street_name"],
                    address_dict["suburb"],
                    address_dict["postcode"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ShipmentAlreadyExistsError(
                f"Order {order_id} already has a shipment"
            ) from exc
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

# ------------- READ -------------

# login auth
def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM users WHERE email = ? AND password = ?""", (email, password))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        return None

    cursor.execute("""
        SELECT * FROM staff
        WHERE staff_id = ?
    """, (user["user_id"],))

    staff = cursor.fetchone()
    role = "customer"

    if staff is not None:
        role = "admin"

    result = {
        "user_id": user["user_id"],
        "email": user["email"],
        "status": user["status"],
        "role": role,
    }
    conn.close()
    return result

def get_user_details(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return None

    cursor.execute("SELECT name FROM staff WHERE staff_id = ?", (user_id,))
    staff = cursor.fetchone()
    role = "customer"
    name = None

    if staff is not None:
        role = "admin"
        name = staff["name"]
    else:
        cursor.execute(
            "SELECT first_name, last_name FROM customers WHERE customer_id = ?",
            (user_id,),
        )
        customer = cursor.fetchone()
        if customer is not None:
            name = f"{customer['first_name']} {customer['last_name']}"

    conn.close()
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "status": user["status"],
        "role": role,
        "name": name,
    }

# list all devices
def get_devices():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return devices

# search by name/type
def search_devices(name, type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM devices WHERE name LIKE ? AND type LIKE ?""", (f"%{name}%", f"%{type}%"))
    devices = cursor.fetchall()
    conn.close()
    return devices

# dublicate device check
def device_exists(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM devices WHERE name = ?""", (name,))
    device = cursor.fetchone()
    conn.close()
    return device is not None

def get_all_orders():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM orders""")
    data = cursor.fetchall()
    conn.close()
    return data

def get_order(order_id):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM orders WHERE order_id=?""",(order_id,))
    order=cursor.fetchone()
    conn.close()
    return order

def get_customer_orders(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE customer_id = ?",
        (customer_id,)
    )
    data = cursor.fetchall()
    conn.close()
    return data

def search_customer_orders(customer_id, order_id=None, date=None):
    conn = get_connection()
    cursor = conn.cursor()
    base = "SELECT * FROM orders WHERE customer_id = ?"
    values = [customer_id]
    if order_id is not None:
        base += " AND order_id = ?"
        values.append(order_id)
    if date is not None:
        base += " AND DATE(created_at) = ?"
        values.append(date)
    cursor.execute(base, values)
    data = cursor.fetchall()
    conn.close()
    return data
 
def get_order_items(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM order_items oi
        JOIN devices d ON oi.device_id = d.device_id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_shipment_by_id(shipment_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.shipment_id,
                s.order_id,
                s.staff_id,
                st.name        AS staff_name,
                s.status,
                s.street_number,
                s.street_name,
                s.suburb,
                s.postcode,
                s.created_at,
                o.customer_id
            FROM shipments s
            JOIN orders o     ON s.order_id = o.order_id
            LEFT JOIN staff st ON s.staff_id = st.staff_id
            WHERE s.shipment_id = ?
            """,
            (shipment_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_shipments_by_customer(customer_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.shipment_id,
                s.order_id,
                s.staff_id,
                st.name        AS staff_name,
                s.status,
                s.street_number,
                s.street_name,
                s.suburb,
                s.postcode,
                s.created_at
            FROM shipments s
            JOIN orders o     ON s.order_id = o.order_id
            LEFT JOIN staff st ON s.staff_id = st.staff_id
            WHERE o.customer_id = ?
            ORDER BY s.created_at DESC
            """,
            (customer_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_shipments():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.shipment_id,
                s.order_id,
                o.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                s.staff_id,
                st.name AS staff_name,
                s.status,
                s.street_number,
                s.street_name,
                s.suburb,
                s.postcode,
                s.created_at
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN staff st ON s.staff_id = st.staff_id
            ORDER BY s.shipment_id DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_paid_orders_without_shipment():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.order_id, o.customer_id, o.total_price,
                   c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.status = 'paid'
              AND o.order_id NOT IN (
                  SELECT order_id FROM shipments WHERE order_id IS NOT NULL
              )
            ORDER BY o.order_id
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_order_with_customer_address(order_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.order_id, o.customer_id, o.status,
                   c.street_number, c.street_name, c.suburb, c.postcode
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
            """,
            (order_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def is_staff(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM staff WHERE staff_id = ?", (user_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def get_customer_payment_methods(customer_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT payment_method_id, customer_id, method_type, provider,
                   account_name, card_last4, expiry_month, expiry_year,
                   is_default, created_at
            FROM payment_methods
            WHERE customer_id = ?
            ORDER BY is_default DESC, payment_method_id ASC
        """, (customer_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_payment_method_by_id(payment_method_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM payment_methods
            WHERE payment_method_id = ?
        """, (payment_method_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_payable_orders_by_customer(customer_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, customer_id, status, total_price, created_at
            FROM orders
            WHERE customer_id = ?
              AND status IN ('saved', 'pending', 'pending payment')
            ORDER BY created_at DESC
        """, (customer_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def create_payment(order_id, customer_id, payment_method_id, amount):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO payments (order_id, customer_id, payment_method_id, amount, status, paid_at)
            VALUES (?, ?, ?, ?, 'paid', datetime('now'))
        """, (order_id, customer_id, payment_method_id, amount))

        cursor.execute("""
            UPDATE orders
            SET status = 'paid'
            WHERE order_id = ?
        """, (order_id,))

        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_payment_by_order_id(order_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM payments
            WHERE order_id = ?
        """, (order_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_customer_payment_history(customer_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.payment_id,
                p.order_id,
                p.customer_id,
                p.payment_method_id,
                p.amount,
                p.status,
                p.paid_at,
                pm.method_type,
                pm.provider,
                pm.card_last4
            FROM payments p
            JOIN payment_methods pm ON p.payment_method_id = pm.payment_method_id
            WHERE p.customer_id = ?
            ORDER BY p.paid_at DESC
        """, (customer_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_payments():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.payment_id,
                p.order_id,
                p.customer_id,
                p.payment_method_id,
                p.amount,
                p.status,
                p.paid_at,
                u.email,
                c.first_name,
                c.last_name,
                pm.method_type,
                pm.provider,
                pm.card_last4
            FROM payments p
            JOIN users u ON p.customer_id = u.user_id
            LEFT JOIN customers c ON p.customer_id = c.customer_id
            JOIN payment_methods pm ON p.payment_method_id = pm.payment_method_id
            ORDER BY p.paid_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
# ------------- UPDATE -------------

def update_device(device_id, name, type, unit_price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE devices SET name = ?, type = ?, unit_price = ?, stock = ? WHERE device_id = ?""",
        (name, type, unit_price, stock, device_id))
    conn.commit()
    conn.close()

def update_order_total(order_id,total):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""UPDATE orders SET total_price=? WHERE order_id=?""",
    (total,order_id))
    conn.commit()
    conn.close()

def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        (status, order_id)
    )
    conn.commit()
    conn.close()

def update_shipment_status(shipment_id, new_status):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE shipments SET status = ? WHERE shipment_id = ?",
            (new_status, shipment_id),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()

# ------------- DELETE -------------

def delete_device(device_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
    conn.commit()
    conn.close()

def cancel_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT device_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute(
            "UPDATE devices SET stock = stock + ? WHERE device_id = ?",
            (item["quantity"], item["device_id"])
        )
    cursor.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()

def cancel_shipment(shipment_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE shipments SET status = 'cancelled' WHERE shipment_id = ?",
            (shipment_id,),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()
