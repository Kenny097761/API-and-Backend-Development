from flask import Blueprint, request, jsonify, session
from backend.models.orders import Order
from backend.models.db_crud import login_user, get_connection

orders_bp = Blueprint("orders", __name__)


def get_session_user():
    user_id = session.get("user_id")
    if not user_id:
        return None, None

    role = session.get("role")
    if not role:
        # main repo login didn't set role — look it up from the DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff WHERE staff_id = ?", (user_id,))
        is_staff = cursor.fetchone() is not None
        conn.close()
        role = "admin" if is_staff else "customer"
        session["role"] = role  # cache it so we don't query every request

    return user_id, role


@orders_bp.route("/orders/create", methods=["POST"])
def create():
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error": "Items are required"}), 400

    order = Order()
    result = order.create(user_id, data["items"])
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@orders_bp.route("/orders/customer")
def customer_orders():
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    order = Order()
    result = order.get_customer(user_id)
    return jsonify(result), 200


@orders_bp.route("/orders/search/<int:order_id>")
def search_by_id(order_id):
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    order = Order()
    result = order.search(user_id, order_id=order_id, date=None)
    return jsonify(result), 200


@orders_bp.route("/orders/search_by_date/<date>")
def search_by_date(date):
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    order = Order()
    result = order.search(user_id, order_id=None, date=date)
    return jsonify(result), 200


@orders_bp.route("/orders/all")
def all_orders():
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "admin":
        return jsonify({"error": "Staff only"}), 403

    order = Order()
    result = order.get_all()
    return jsonify(result), 200


@orders_bp.route("/orders/<int:id>")
def order_detail(id):
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role not in ("customer", "admin"):
        return jsonify({"error": "Access denied"}), 403

    order = Order()
    result = order.get_detail(id)
    if "error" in result:
        return jsonify(result), 404

    if role == "customer" and result["order"]["customer_id"] != user_id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify(result), 200


@orders_bp.route("/orders/update/<int:id>", methods=["PUT"])
def update(id):
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"error": "Items are required"}), 400

    order = Order()
    result = order.update(id, user_id, role, data["items"])
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 200


@orders_bp.route("/orders/cancel/<int:id>", methods=["PUT"])
def cancel(id):
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    if role != "customer":
        return jsonify({"error": "Customers only"}), 403

    data = request.get_json()
    if not data or not data.get("confirmed"):
        return jsonify({"error": "Cancellation must be confirmed"}), 400

    order = Order()
    result = order.cancel(id, user_id, role)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 200


@orders_bp.route("/api/devices")
def get_all_devices():
    from backend.models.db_crud import get_devices
    devices = get_devices()
    return jsonify([dict(d) for d in devices])


@orders_bp.route("/api/user/info")
def user_info():
    user_id, role = get_session_user()
    if not user_id:
        return jsonify({"error": "Login required"}), 401
    return jsonify({
        "user_id": user_id,
        "role": role
    })
