from flask import Blueprint, jsonify, request, session
from backend.models.db_crud import (
    get_payable_orders_by_customer,
    get_customer_payment_methods,
    get_payment_method_by_id,
    get_order,
    get_payment_by_order_id,
    create_payment,
    get_customer_payment_history,
    get_all_payments,
    is_staff,
)

payments_bp = Blueprint("payments_bp", __name__)


def current_user():
    user_id = session.get("user_id")
    role = session.get("role")
    return user_id, role


@payments_bp.route("/api/orders/payable", methods=["GET"])
def get_payable_orders():
    user_id, role = current_user()
    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401
    if role != "customer":
        return jsonify({"error": "Only customers can view payable orders"}), 403

    orders = get_payable_orders_by_customer(user_id)
    return jsonify(orders), 200


@payments_bp.route("/api/payment-methods/me", methods=["GET"])
def my_payment_methods():
    user_id, role = current_user()
    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401
    if role != "customer":
        return jsonify({"error": "Only customers can view payment methods"}), 403

    methods = get_customer_payment_methods(user_id)
    return jsonify(methods), 200


@payments_bp.route("/api/payments", methods=["POST"])
def make_payment():
    user_id, role = current_user()
    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401
    if role != "customer":
        return jsonify({"error": "Only customers can make payments"}), 403

    data = request.get_json() or {}
    order_id = data.get("order_id")
    payment_method_id = data.get("payment_method_id")

    if not order_id or not payment_method_id:
        return jsonify({"error": "order_id and payment_method_id are required"}), 400

    order = get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order["customer_id"] != user_id:
        return jsonify({"error": "You can only pay your own orders"}), 403

    if order["status"] not in ("saved", "pending", "pending payment"):
        return jsonify({"error": "This order is not eligible for payment"}), 400

    method = get_payment_method_by_id(payment_method_id)
    if not method:
        return jsonify({"error": "Payment method not found"}), 404

    if method["customer_id"] != user_id:
        return jsonify({"error": "Payment method does not belong to this customer"}), 403

    existing_payment = get_payment_by_order_id(order_id)
    if existing_payment:
        return jsonify({"error": "This order has already been paid"}), 400

    payment_id = create_payment(
        order_id=order_id,
        customer_id=user_id,
        payment_method_id=payment_method_id,
        amount=order["total_price"],
    )

    return jsonify({
        "message": "Payment completed successfully",
        "payment_id": payment_id,
        "order_id": order_id,
        "amount": order["total_price"],
        "status": "paid"
    }), 201


@payments_bp.route("/api/payments/me", methods=["GET"])
def my_payment_history():
    user_id, role = current_user()
    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401
    if role != "customer":
        return jsonify({"error": "Only customers can view their payment history"}), 403

    payments = get_customer_payment_history(user_id)
    return jsonify(payments), 200


@payments_bp.route("/api/payments", methods=["GET"])
def all_payments():
    user_id, role = current_user()
    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Only staff can view all payments"}), 403

    payments = get_all_payments()
    return jsonify(payments), 200