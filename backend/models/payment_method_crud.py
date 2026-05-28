from backend.models.db_connect import get_connection
from backend.models.payment_method import PaymentMethod


PAYMENT_METHOD_COLUMNS = """
    payment_method_id,
    user_id,
    type,
    nickname,
    created_at,
    updated_at,
    cardholder_name,
    card_brand,
    card_last_four,
    expiry_date,
    account_name,
    bsb_last_three,
    account_last_four,
    paypal_email_masked
"""


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE lower(email) = lower(?)", (email,))
    row = cursor.fetchone()
    conn.close()
    return row["user_id"] if row else None


def create_user_for_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, password, status) VALUES (?, ?, ?)",
        (email, "", "active"),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_or_create_user_by_email(email):
    user_id = get_user_by_email(email)
    if user_id is not None:
        return user_id

    return create_user_for_email(email)


def is_customer(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if user is None:
        conn.close()
        return False

    cursor.execute("SELECT 1 FROM staff WHERE staff_id = ?", (user_id,))
    staff = cursor.fetchone()
    role = "customer"

    if staff is not None:
        role = "admin"

    conn.close()
    return role == "customer"


def row_to_payment_method(row):
    return PaymentMethod(*row) if row else None


def list_payment_methods(user_id, method_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    if method_type:
        cursor.execute(
            """
            SELECT """ + PAYMENT_METHOD_COLUMNS + """ FROM payment_methods
            WHERE user_id = ? AND type = ?
            ORDER BY created_at DESC, payment_method_id DESC
            """,
            (user_id, method_type),
        )
    else:
        cursor.execute(
            """
            SELECT """ + PAYMENT_METHOD_COLUMNS + """ FROM payment_methods
            WHERE user_id = ?
            ORDER BY created_at DESC, payment_method_id DESC
            """,
            (user_id,),
        )

    methods = [row_to_payment_method(row) for row in cursor.fetchall()]
    conn.close()
    return methods


def get_payment_method(user_id, payment_method_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT " + PAYMENT_METHOD_COLUMNS + " FROM payment_methods WHERE user_id = ? AND payment_method_id = ?",
        (user_id, payment_method_id),
    )
    method = row_to_payment_method(cursor.fetchone())
    conn.close()
    return method


def create_payment_method(user_id, method_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO payment_methods (
            user_id, type, nickname, cardholder_name, card_brand,
            card_last_four, expiry_date, account_name, bsb_last_three,
            account_last_four, paypal_email_masked, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            user_id,
            method_data.get("type"),
            method_data.get("nickname"),
            method_data.get("cardholder_name"),
            method_data.get("card_brand"),
            method_data.get("card_last_four"),
            method_data.get("expiry_date"),
            method_data.get("account_name"),
            method_data.get("bsb_last_three"),
            method_data.get("account_last_four"),
            method_data.get("paypal_email_masked"),
        ),
    )
    payment_method_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_payment_method(user_id, payment_method_id)


def update_payment_method(user_id, payment_method_id, method_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE payment_methods
        SET type = ?,
            nickname = ?,
            cardholder_name = ?,
            card_brand = ?,
            card_last_four = ?,
            expiry_date = ?,
            account_name = ?,
            bsb_last_three = ?,
            account_last_four = ?,
            paypal_email_masked = ?,
            updated_at = datetime('now')
        WHERE user_id = ? AND payment_method_id = ?
        """,
        (
            method_data.get("type"),
            method_data.get("nickname"),
            method_data.get("cardholder_name"),
            method_data.get("card_brand"),
            method_data.get("card_last_four"),
            method_data.get("expiry_date"),
            method_data.get("account_name"),
            method_data.get("bsb_last_three"),
            method_data.get("account_last_four"),
            method_data.get("paypal_email_masked"),
            user_id,
            payment_method_id,
        ),
    )
    changed = cursor.rowcount
    conn.commit()
    conn.close()

    if changed == 0:
        return None

    return get_payment_method(user_id, payment_method_id)


def delete_payment_method(user_id, payment_method_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM payment_methods WHERE user_id = ? AND payment_method_id = ?",
        (user_id, payment_method_id),
    )
    changed = cursor.rowcount
    conn.commit()
    conn.close()
    return changed > 0
